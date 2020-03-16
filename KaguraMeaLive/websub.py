# coding:utf-8
from datetime import datetime

from flask import request
from sqlalchemy import update

from KaguraMeaLive import app, db
from .schema import Channel


@app.route(f'/WebSub/{app.config["WEBSUB_TOKEN"]}', methods=['GET'])
def handle_challenge():
    mode = request.args.get('hub.mode', "")
    challenge = request.args.get('hub.challenge', "")
    topic = request.args.get('hub.topic', "")
    # lease_seconds = request.args.get('hub.lease_seconds', "")

    if mode == 'subscribe':
        update(Channel).where(Channel.topic_url == topic).values(last_subscribe=datetime.utcnow, subcribe=True)
    elif mode == 'unsubscribe':
        update(Channel).where(Channel.topic_url == topic).values(subcribe=False)
    else:
        app.logger.error(f'Invalid mode: {mode}')

    return challenge


@app.route(f'/WebSub/{app.config["WEBSUB_TOKEN"]}', methods=['POST'])
def handle_message():
    a = Channel(name="sdf", id="sdfd")
    db.session.add(a)
    db.session.commit()
    return 's'
