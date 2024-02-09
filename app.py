import dependencies # sets sys path for packages (has to be the first line)

import bcrypt
from datetime import datetime, timedelta
from flask import abort, Flask, render_template, request, Response, url_for, redirect
from flask_mysqldb import MySQL
from functools import wraps
import json

from constants import LANGUAGES
from l10n.l import L
from model import Filter, ContactForOrganize
from persistence import DBContact
from radar import Radar
from osm import get_raw_osm_json, parse_osm_json

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
mysql = MySQL(app)
NUM_RADAR_IDS_TO_CACHE_PER_REQUEST = 8
NUM_OSM_IDS_TO_CACHE_PER_REQUEST = 10

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == app.config["ORGANIZE_LOGIN"]:
            hashed = app.config["ORGANIZE_PASSWORD"].encode("utf-8")
            entered = auth.password.encode("utf-8")
            if bcrypt.checkpw(entered, hashed):
                return f(*args, **kwargs)

        return Response(
                "Could not verify your access level for that URL.\n"
                "You have to login with proper credentials",
                401,
                {"WWW-Authenticate": "Basic realm='Login Required'"},
            )

    return decorated

def _get_lang():
    lang_pararameter = request.args.get("lang") or app.config["DEFAULT_LANG"]
    return lang_pararameter if lang_pararameter in LANGUAGES else app.config["DEFAULT_LANG"]

@app.route("/")
def index():
    lang = _get_lang()
    return render_template(f"index_{lang}.html", lang=lang, L=L[lang])

@app.route("/list")
def list():
    filter = Filter.from_request(request)
    lang = _get_lang()
    contacts = DBContact(mysql=mysql).contacts(filter=filter, lang=lang)

    return render_template("list.html", contacts=contacts, lang=lang, L=L[lang])

@app.route("/print_list")
def print_list():
    lang = _get_lang()
    contacts = DBContact(mysql=mysql).contacts(filter=Filter(), lang=lang)

    return render_template("print_list.html", contacts=contacts, lang=lang, L=L[lang])

@app.route("/print_event_list")
def print_event_list():
    lang = _get_lang()
    contacts = DBContact(mysql=mysql).contacts(filter=Filter(only_with_events=True), lang=lang)

    return render_template("print_event_list.html", contacts=contacts, lang=lang, L=L[lang])

@app.route("/imprint")
def imprint():
    lang = _get_lang()
    return render_template("imprint.html", lang=lang, L=L[lang])

@app.route("/organize", methods=["GET", "POST"])
@auth_required
def organize():
    if request.method == "POST":
        DBContact(mysql=mysql).create(ContactForOrganize.from_form_data(request.form))

    filter = Filter.from_request(request)
    contacts = DBContact(mysql=mysql).contacts_for_organize(filter=filter)
    return render_template("organize.html", contacts=contacts, languages=LANGUAGES, L=L["en"])

@app.route("/organize/new", methods=["GET"])
@auth_required
def organize_new():
    contact = ContactForOrganize.empty()
    return render_template("organize_new.html", contact=contact, languages=LANGUAGES, L=L["en"])

@app.route("/organize/<int:id>/edit", methods=["GET"])
@auth_required
def organize_edit(id: int):
    filter = Filter.for_id(id)
    contacts = DBContact(mysql=mysql).contacts_for_organize(filter=filter)
    return render_template("organize_edit.html", contact=contacts[0], languages=LANGUAGES, L=L["en"])

@app.route("/organize/<int:id>", methods=["DELETE", "POST"])
@auth_required
def organize_contact(id: int):
    if request.method == "POST":  # REST PUT semantics, but restricted to form method options
        DBContact(mysql=mysql).update(id, ContactForOrganize.from_form_data(request.form))
    return redirect(url_for("organize"))

@app.route("/organize/<int:id>/delete", methods=["POST"])
@auth_required
def organize_contact_delete(id: int):
    if request.method == "POST":  # REST DELETE semantics, but restricted to form method options
        DBContact(mysql=mysql).delete(id)
    return redirect(url_for("organize"))

@app.route("/update-events", methods=["GET"])
def update_events():
    lang = _get_lang()
    id = int(request.args.get("id", 0))
    contacts = DBContact(mysql=mysql).contacts_for_organize(filter=Filter.for_id(id))
    if len(contacts) == 0 or contacts[0].radar_group_id is None:
        abort(404)
    one_hour_ago = datetime.now() - timedelta(hours=1)
    if contacts[0].events_cached_at and contacts[0].events_cached_at > one_hour_ago:
        return {"status": 304}  # not modified
    events_map = Radar(contacts[0].radar_group_id).get_events()
    DBContact(mysql=mysql).update_events_cache(id, events_map)
    return {"events": events_map[lang], "status": 200}

@app.route("/cache-events", methods=["GET"])
def cache_events():
    contact_and_radar_ids = DBContact(mysql=mysql).contact_to_event_cache(count=NUM_RADAR_IDS_TO_CACHE_PER_REQUEST)
    if not len(contact_and_radar_ids):
        return "nothing to cache"
    for contact_id, radar_group_id in contact_and_radar_ids:
        events_map = Radar(radar_group_id).get_events()
        DBContact(mysql=mysql).update_events_cache(contact_id, events_map)
    return f"cached {[contact_id for (contact_id, _) in contact_and_radar_ids]}"

@app.route("/cache-osm-data", methods=["GET"])
def cache_osm_data():
    contact_and_osm_node_ids = DBContact(mysql=mysql).contact_to_osm_cache(count=NUM_OSM_IDS_TO_CACHE_PER_REQUEST)
    if not len(contact_and_osm_node_ids):
        return "nothing to cache"
    for contact_id, osm_node_id in contact_and_osm_node_ids:
        osm_json = get_raw_osm_json(osm_node_id)
        DBContact(mysql=mysql).update_osm_json(contact_id, osm_json)
    return f"cached {[contact_id for (contact_id, _) in contact_and_osm_node_ids]}"

@app.route("/parse-osm-data", methods=["GET"])
def parse_osm_data():
    contacts_with_osm = DBContact(mysql=mysql).contacts_with_osm()
    failed = []
    for contact in contacts_with_osm:
        try:
            osm_info_map = parse_osm_json(contact.osm_cached_json)
            DBContact(mysql=mysql).update_osm_info(contact, osm_info_map)
        except Exception as err:
            failed.append(contact.id)

    return f"parsed {len(contacts_with_osm)} contacts with OSM. Failed: {failed}"
