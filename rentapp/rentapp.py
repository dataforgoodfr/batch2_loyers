# -*- coding: utf-8 -*-

import os, sqlite3
from flask import Flask, request, g, render_template
from crawlers import PapCrawler, LogCrawler

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

@app.route('/')
def index():
    '''Index Page
    '''
    return render_template('index.html', url=None)

@app.route('/', methods=['POST'])
def show_query_results():
    '''Index + scraper data
    '''
    url = request.form['input_url']
    assert type(url) == str
    attributes = run_crawler(url)
    return render_template('index.html', attr=attributes)

def run_crawler(url):
    '''Parse site from url and run the corresponding
    spider
    '''
    if 'pap' in url:
        crawler = PapCrawler(url)
    elif 'seloger' in url:
        crawler = LogCrawler(url)
    elif 'leboncoin' in url:
        crawler = LbcCrawler(url)
    else:
        parser.error('url cannot be parsed')
        sys.exit(-1)

    crawler.run()
    return crawler.item

if __name__ == '__main__':
    app.run()