# coding: utf-8


import logging
import os
from logging.config import dictConfig
from logging.handlers import SMTPHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


def emit(self, record):
    """
    Overwrite the logging.handlers.SMTPHandler.emit function with SMTP_SSL.
    Emit a record.
    Format the record and send it to the specified addressees.
    """
    try:
        import smtplib
        from email.utils import formatdate
        port = self.mailport
        if not port:
            port = smtplib.SMTP_PORT
        smtp = smtplib.SMTP_SSL(self.mailhost, port, 3)
        msg = self.format(record)
        msg = "From: %s\r\nTo: %s\r\nSubject: %s\r\nDate: %s\r\n\r\n%s" % (
            self.fromaddr, ", ".join(self.toaddrs), self.getSubject(record), formatdate(), msg)
        if self.username:
            smtp.ehlo()
            smtp.login(self.username, self.password)
        smtp.sendmail(self.fromaddr, self.toaddrs, msg)
        smtp.quit()
    except (KeyboardInterrupt, SystemExit):
        raise
    except:
        self.handleError(record)


logging.handlers.SMTPHandler.emit = emit

mail_handler = SMTPHandler(
    mailhost=(os.environ.get("SMTP_HOST"), int(os.environ.get("SMTP_PORT"))),
    credentials=(os.environ.get("SMTP_USERNAME"), os.environ.get("SMTP_PASSWORD")),
    fromaddr=os.environ.get("FROM_ADDR"),
    toaddrs=[os.environ.get("TO_ADDR")],
    subject='KaguraMeaLive bot Error'
)
mail_handler.setLevel(logging.ERROR)
mail_handler.setFormatter(logging.Formatter(
    '[%(asctime)s][%(levelname)s][%(module)s]%(message)s'
))

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
app.config['TRANSLATE_APPID'] = os.environ.get("TRANSLATE_APPID")
app.config['TRANSLATE_SECRET'] = os.environ.get("TRANSLATE_SECRET")
app.config['DEFAULT_CHAT'] = os.environ.get("DEFAULT_CHAT")


app.config.from_pyfile(os.path.join(app.instance_path, 'config.py'), silent=True)

if not app.debug:
    app.logger.addHandler(mail_handler)

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
from .telegram_bot_webhook import answer_telegram, answer_telegram_get

app.teardown_appcontext(tear_down)
app.logger.info("service start")
