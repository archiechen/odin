from flask import Flask

from flask_bootstrap import Bootstrap
# flask-peewee bindings
from flask_peewee.db import Database
from flask.ext.moment import Moment

app = Flask(__name__)
app.config.from_object('config.Configuration')

moment = Moment(app)
db = Database(app)
Bootstrap(app)

import logging
from logging.handlers import RotatingFileHandler
from logging import Formatter
file_handler = RotatingFileHandler('./logs/server.log',maxBytes=102400000,encoding='utf-8')
file_handler.setFormatter(Formatter(
    '%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'
))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

import math

@app.template_filter('labeled')
def label_filter(score):
    return  "label-%d" % int(math.floor(score)) if score else "label-default"