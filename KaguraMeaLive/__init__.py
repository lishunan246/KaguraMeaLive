# coding: utf-8


import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s][%(levelname)s][%(module)s]%(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("SQLALCHEMY_DATABASE_URI")
app.config['BASE_URL'] = os.environ.get("BASE_URL")
app.config['WEBSUB_TOKEN'] = os.environ.get("WEBSUB_TOKEN")
app.config['YOUTUBE_API_KEY'] = os.environ.get("YOUTUBE_API_KEY")
app.config['TELEGRAM_BOT_TOKEN'] = os.environ.get("TELEGRAM_BOT_TOKEN")

app.config.from_pyfile(os.path.join(app.instance_path, 'config.py'), silent=True)

db = SQLAlchemy(app)
# ensure the instance folder exists
try:
    os.makedirs(app.instance_path)
except OSError:
    pass


# a simple page that says hello
@app.route('/')
def hello():
    return 'Hello, World!'


def tear_down(e=None):
    pass


from .schema import init_db_command
from .subscribe import subscribe_command

app.cli.add_command(init_db_command)
app.cli.add_command(subscribe_command)

from .websub import handle_challenge, handle_message

app.teardown_appcontext(tear_down)
