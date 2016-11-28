# -*- coding: utf-8 -*-

import os, sqlite3
import pandas as pd
from flask import Flask, request, g, render_template
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, \
SelectField, IntegerField
from wtforms.validators import DataRequired
from crawlers_beta import PapCrawler, SeLogerCrawler

## APP

# create application
app = Flask(__name__)
app.config.from_object(__name__)

# load default config
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'rentapp.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))

# override config from an environment variable
app.config.from_envvar('RENTAPP_SETTINGS', silent=True)

def connect_db():
    '''Connect to the db
    '''
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    '''If no existing connexion, create one
    '''
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    '''If no db, create one
    '''
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    '''Commandline to initialize the db
    '''
    init_db()
    print ('Initialized the database.')

## FORMS

# read data for multiselect menu
file_path = os.path.dirname(os.path.abspath(__file__))
data_path = os.path.join(file_path, 'utils/quarters.csv')
choices = pd.read_csv(data_path)['quarter'].tolist()
choices = [(i, j) for i, j in enumerate(choices)]

# create forms

class UrlForm(FlaskForm):
    input_url = StringField('input_url', validators=[DataRequired()])

class ValidationForm(FlaskForm):
    price = DecimalField('price')
    subarea = SelectField('subarea', coerce=str)
    surface = DecimalField('surface')
    year = IntegerField('year')
    rooms = IntegerField('rooms')

## BEHAVIOUR

@app.route('/')
def index():
    form = UrlForm()
    return render_template('base.html', form=form)

@app.route('/', methods=['POST'])
def show_query_results():
    url = request.form.get('input_url')
    
    if 'pap' in url:
        crawler = PapCrawler(url)
        status = True
    elif 'seloger' in url:
        crawler = SeLogerCrawler(url)
        status = True
    else:
        status = False
    
    item = crawler.__dict__
    validation = ValidationForm()
    validation.price.default = item['price']
    validation.subarea.default = item['subarea']
    validation.subarea.choices = choices
    validation.surface.default = item['surface']
    validation.rooms.default = item['rooms']
    validation.year.default = item['year']
    form = UrlForm()
    return render_template('base.html', 
                           form=form,
                           validation=validation)

@app.route('/results', methods=['POST'])
def show_actual_price():
    result = 100
    return render_template('index.html', item=app.item, result=result)


if __name__ == '__main__':
    app.run(debug=True)