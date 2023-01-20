import dependencies # sets sys path for packages
import json

from flask import Flask,render_template, request
from flask_mysqldb import MySQL

from persistence import DBContact
from model import Filter

app = Flask(__name__)
app.config.from_file("config.json", load=json.load)
mysql = MySQL(app)

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/list")
def list():
    filter = Filter.from_request(request)
    contacts = DBContact(mysql=mysql, lang_code="en").all_contacts(filter=filter)

    return render_template('list.html', contacts=contacts)
