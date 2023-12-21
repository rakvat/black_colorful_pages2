import dependencies # sets sys path for packages (has to be the first line)

import json
from functools import wraps
import bcrypt

from flask import Flask,render_template, request, Response, url_for, redirect
from flask_mysqldb import MySQL

from persistence import DBContact
from model import Filter, ContactForOrganize
from constants import LANGUAGES
from l10n.l import L

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
mysql = MySQL(app)

def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == app.config['ORGANIZE_LOGIN']:
            hashed = app.config['ORGANIZE_PASSWORD'].encode('utf-8')
            entered = auth.password.encode('utf-8')
            if bcrypt.checkpw(entered, hashed):
                return f(*args, **kwargs)

        return Response(
                'Could not verify your access level for that URL.\n'
                'You have to login with proper credentials',
                401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'},
            )

    return decorated

def _get_lang():
    lang_pararameter = request.args.get('lang') or app.config['DEFAULT_LANG']
    return lang_pararameter if lang_pararameter in LANGUAGES else app.config['DEFAULT_LANG']

@app.route("/")
def index():
    lang = _get_lang()
    return render_template(f'index_{lang}.html', lang=lang, L=L[lang])

@app.route("/list")
def list():
    filter = Filter.from_request(request)
    lang = _get_lang()
    contacts = DBContact(mysql=mysql).contacts(filter=filter, lang=lang)

    return render_template('list.html', contacts=contacts, lang=lang, L=L[lang])

@app.route("/imprint")
def imprint():
    lang = _get_lang()
    return render_template('imprint.html', lang=lang, L=L[lang])

@app.route("/organize", methods=['GET', 'POST'])
@auth_required
def organize():
    if request.method == 'POST':
        DBContact(mysql=mysql).create(ContactForOrganize.from_form_data(request.form))

    filter = Filter.from_request(request)
    contacts = DBContact(mysql=mysql).contacts_for_organize(filter=filter)
    return render_template('organize.html', contacts=contacts, languages=LANGUAGES, L=L['en'])

@app.route("/organize/new", methods=['GET'])
@auth_required
def organize_new():
    contact = ContactForOrganize.empty()
    return render_template('organize_new.html', contact=contact, languages=LANGUAGES, L=L['en'])

@app.route("/organize/<int:id>/edit", methods=['GET'])
@auth_required
def organize_edit(id: int):
    filter = Filter.for_id(id)
    contacts = DBContact(mysql=mysql).contacts_for_organize(filter=filter)
    return render_template('organize_edit.html', contact=contacts[0], languages=LANGUAGES, L=L['en'])

@app.route("/organize/<int:id>", methods=['DELETE', 'POST'])
@auth_required
def organize_contact(id: int):
    if request.method == 'POST':  # REST PUT semantics, but restricted to form method options
        DBContact(mysql=mysql).update(id, ContactForOrganize.from_form_data(request.form))
    return redirect(url_for('organize'))

@app.route("/organize/<int:id>/delete", methods=['POST'])
@auth_required
def organize_contact_delete(id: int):
    if request.method == 'POST':  # REST DELETE semantics, but restricted to form method options
        DBContact(mysql=mysql).delete(id)
    return redirect(url_for('organize'))

@app.route("/cache-events", methods=['GET'])
def cache_events():
    return "ok"
