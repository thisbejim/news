import sys
import os
from flask import Flask, render_template, g, request, redirect, url_for, flash, jsonify, session, Response
import logging
from operator import itemgetter
from collections import OrderedDict
import requests
import json
import datetime
import time
import oauthlib

# App Config
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = 'static/uploads/'


# Set allowable MIME Types for upload
ALLOWED_EXTENSIONS = ['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip']
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'super secret key'
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

app.config['SITE'] = "http://0.0.0.0:5000/"
app.config['DEBUG'] = True

# firebase db reference
db = 'https://newstestapp.firebaseio.com'

# List all assets
@app.route('/')
def index():

    # Get articles
    ref = db+'/articles.json?orderBy="time"&limitToFirst=10'

    # Jsonify response object
    articles = requests.get(ref).json()

    # set up list
    this_list = []

    # put dictionary in list for sorting
    for i in articles:
        # add ID key and assign id
        articles[i]["id"] = i
        this_list.append(articles[i])

    # sort list by time (datetime)
    this_list = sorted(this_list, key=itemgetter("time"))

    return render_template('index.html', articles=this_list)

@app.route('/article/<article_id>/<article_tag_line>')
def article(article_id, article_tag_line):

        article_ref = db+'/articles/'+article_id+'.json'

        article = requests.get(article_ref).json()

        this_list = []

        article["id"] = article_id
        this_list.append(article)

        return render_template('article.html', article=this_list)

@app.route('/news/<page_number>/<last_article_date>')
def pagination(page_number, last_article_date):

    ref = db+'/articles.json?orderBy="time"&startAt='+last_article_date+'&limitToFirst=10'

    articles = requests.get(ref).json()

    this_list = []
    for i in articles:
        articles[i]["id"] = i
        this_list.append(articles[i])

    this_list = sorted(this_list, key=itemgetter("time"))

    return render_template('index.html', articles=this_list)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)