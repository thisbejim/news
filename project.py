import sys
import os
from flask import Flask, render_template, g, request, redirect, url_for, flash, jsonify, session, Response
import logging
from operator import itemgetter
from collections import OrderedDict
import requests
import pyrebase
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
db = pyrebase.Firebase('https://newstestapp.firebaseio.com', 'WQJUSvWmnpraVQROTBrKQaubyCqx9UQCrWZmv2ul')

# List all assets
@app.route('/')
def index():

    # get new articles
    results = db.sort_by_last('articles', 'timeOfApproval', 0, 20, None)

    # add time difference and urlsafe tag_line
    results = prep(results)
    
    # get popular articles
    popular_articles = db.sort_by_last('articles', 'clicks', 0, 5, None)
    popular_articles = prep(popular_articles)
    # get featured article
    featured_article_one = popular_articles[0]
    featured_article_two = popular_articles[1]

    # remove featured article from popular articles
    del popular_articles[0]
    del popular_articles[0]

    return render_template('index.html', articles=results, popular_articles=popular_articles,
                           featured_article_one=featured_article_one, featured_article_two=featured_article_two)


@app.route('/article/<article_id>/<article_tag_line>')
def article(article_id, article_tag_line):

    # get article
    one_article = db.one('articles', article_id, None)
    one_article = prep(one_article)
    # count and add clicks
    clicks = None
    for i in one_article:
        clicks = int(i['clicks']) + 1
    clicks = '{"clicks": %s }' % clicks

    # patch clicks
    db.patch('articles', article_id, clicks, None)

    return render_template('article.html', article=one_article)


@app.route('/news/<page_number>/<last_article_date>')
def pagination(page_number, last_article_date):

    results = db.sort_by_last('articles', 'timeOfApproval', last_article_date, 10, None)

    # add time differences
    results = prep(results)

    # get popular articles
    popular_articles = db.sort_by_last('articles', 'clicks', 0, 4, None)

    # get featured article
    featured_article = popular_articles[0]

    # remove featured article from popular articles
    del popular_articles[0]

    return render_template('index.html', articles=results, popular_articles=popular_articles,
                           featured_article=featured_article)


@app.template_filter('debug')
def debug(text):
    print(text)
    return ''


def prep(results):
    time_now = time.time() * 1000
    time_now = int(time_now)
    for i in results:

        # add url safe tag_line
        url_safe = i['tag_line']
        url_safe = ''.join(e for e in url_safe if e.isalnum())
        i['url_safe'] = url_safe

        # add time difference
        time_dif = time_now - i['timeOfApproval']
        if time_dif < 60000:
            seconds = int(time_dif / 1000)
            i['timeDif'] = str(seconds)+" seconds ago"
        elif time_dif < 3600000 > 60000:
            minutes = int(time_dif / 60000)
            i['timeDif'] = str(minutes)+" minutes ago"
        elif time_dif < 7200000 > 3600000:
            i['timeDif'] = "1 hour ago"
        elif time_dif < 86400000 > 7200000:
            hours = time_dif / 3600000
            hours = int(hours)
            i['timeDif'] = str(hours)+" hours ago"
        elif time_dif < 604800000 > 86400000:
            days = time_dif / 86400000
            days = int(days)
            i['timeDif'] = str(days)+" days ago"
        elif time_dif < 31449600000 > 604800000:
            weeks = time_dif / 604800000
            weeks = int(weeks)
            i['timeDif'] = str(weeks)+" weeks ago"
        elif time_dif > 31449600000:
            years = time_dif / 31449600000
            years = int(years)
            i['timeDif'] = str(years)+" years ago"
    return results


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)