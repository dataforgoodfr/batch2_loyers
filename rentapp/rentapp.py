# -*- coding: utf-8 -*-

import os, sqlite3

# crawlers
from crawlers_beta import PapCrawler
from utils.tools import get_options, get_choice, get_refs
from utils.graphs import make_graph
from utils.charges import make_prediction

# flask
from flask import Flask, request, g, render_template, redirect, url_for, session
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired
from wtforms import StringField, DecimalField, \
SelectField, IntegerField, RadioField

## APP

# create application
app = Flask(__name__)
app.config.from_object(__name__)

# load default config
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'rentapp.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default',
))

# override config from an environment variable
app.config.from_envvar('RENTAPP_SETTINGS', silent=True)

'''
def connect_db():
    # Connect to the db
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv

def get_db():
    # If no existing connexion, create one
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db

def init_db():
    # If no db, create one
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('initdb')
def initdb_command():
    # Commandline to initialize the db
    init_db()
    print ('Initialized the database.')
'''

## FORMS

class UrlForm(FlaskForm):
    url = StringField('url', validators=[DataRequired()])

class AttrForm(FlaskForm):
    price = IntegerField('price', validators=[DataRequired()])
    charges = IntegerField('charges', default=0)
    subarea = SelectField('subarea', coerce=int)
    surface = IntegerField('surface', validators=[DataRequired()])
    year = IntegerField('year', validators=[DataRequired()])
    rooms = IntegerField('rooms', validators=[DataRequired()])


## BEHAVIOUR

@app.route('/', methods=['GET', 'POST'])
def index():
    urlform = UrlForm()
    display = 'url'
    return render_template('index.html', 
                           display=display, 
                           urlform=urlform)

@app.route('/scraping', methods=['POST'])
def scraping():
    # get url
    url = request.form['url']

    # scraping
    try:
        if 'pap' in url:
            crawler = PapCrawler(url)
        else:
            raise Exception()
    except:
        return redirect(url_for('index'))

    # crawler = PapCrawler(url)
    # get data from crawl
    session['item'] = crawler.__dict__
    return redirect(url_for('validation'))

@app.route('/validation', methods=['GET', 'POST'])
def validation():
    # initiate form
    item = session.get('item', None)
    form = AttrForm(request.form)

    # pre-fill validation
    form.price.data = item['price']
    form.surface.data = item['surface']
    form.rooms.data = item['rooms']
    form.year.data = item['year']

    # get area options and pre-fill
    options = get_options()
    form.subarea.choices = options
    form.subarea.data = get_choice(options, item['subarea'])

    # catch errors
    if not form.validate_on_submit():
        display = 'fill'
        return render_template('index.html', 
                               display=display, 
                               attr_form=form)

    # id to area
    id_quartier = int(request.form['subarea'])
    item['subarea'] = options[id_quartier][1]

    # set new values
    item['price'] = int(request.form['price'])
    item['charges'] = int(request.form['charges'])
    item['surface'] = int(request.form['surface'])
    item['rooms'] = int(request.form['rooms'])
    item['year'] = int(request.form['year'])

    # charges

    if item['charges']:
        item['price'] = item['price'] - item['charges']
    else:
        prediction = make_prediction(item)
        item['price'] = item['price'] - prediction

    # max rooms == 4
    if item['rooms'] > 4:
        item['rooms'] = 4

    session['item'] = item
    return redirect(url_for('results'))

@app.route('/results', methods=['GET', 'POST'])
def results():
    # get item references
    item = session.get('item', None)
    refs = get_refs(item)
    for key, value in refs.items():
        refs[key] = int(float(item['surface']) * value)
    refs['price'] = int(float(item['price']))
    # build graph
    graph = make_graph(refs)
    display = 'valid'
    return render_template('index.html', 
                           display=display, 
                           refs=refs, 
                           graph=graph)


if __name__ == '__main__':
    # port = int(os.environ.get("PORT", 5000))
    # app.run(host='0.0.0.0', port=port)
    app.run(debug=True)