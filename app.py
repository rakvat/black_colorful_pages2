import dependencies # sets sys path for packages
import json

from flask import Flask,render_template, request
from flask_mysqldb import MySQL

from persistence import DBContact
from model import Filter

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
mysql = MySQL(app)

with open('l10n/structure.json', 'r', encoding='utf-8') as f:
    L = json.load(f)

def _get_lang():
    return request.args.get('lang') or app.config['DEFAULT_LANG']

@app.route("/")
def index():
    lang = _get_lang()
    return render_template('index.html', lang=lang, L=L[lang])

@app.route("/list")
def list():
    filter = Filter.from_request(request)
    lang = _get_lang()
    contacts = DBContact(mysql=mysql, lang=lang).all_contacts(filter=filter)

    return render_template('list.html', contacts=contacts, lang=lang, L=L[lang])

@app.route("/imprint")
def imprint():
    lang = _get_lang()
    return render_template('imprint.html', lang=lang, L=L[lang])
