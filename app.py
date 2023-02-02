import dependencies # sets sys path for packages (has to be the first line)

import json
from functools import wraps
import bcrypt

from flask import Flask,render_template, request, Response
from flask_mysqldb import MySQL

from persistence import DBContact
from model import Filter

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

@app.route("/organize", methods=['GET', 'POST'])
@auth_required
def organize():
    return render_template('organize.html', L=L['en'])

@app.route("/organize/new", methods=['GET'])
@auth_required
def organize_new():
    return render_template('organize_new.html')

@app.route("/organize/<int:id>", methods=['DELETE', 'PUT'])
@auth_required
def organize_contact():
    pass
