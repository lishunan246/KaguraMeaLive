# coding: utf-8


import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
app.config.from_mapping(
    SECRET_KEY='dev',
    SQLALCHEMY_TRACK_MODIFICATIONS=False
)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("ENGINE_URL")

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
from .websub import handle_challenge, handle_message

app.teardown_appcontext(tear_down)
app.cli.add_command(init_db_command)
