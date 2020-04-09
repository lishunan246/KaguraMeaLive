# coding: utf-8

import requests

from KaguraMeaLive import db, app
from .schema import Channel


def subscribe(channel: Channel) -> None:
    r = requests.post(
        url='https://pubsubhubbub.appspot.com/subscribe',
        data={
            "hub.callback": f'{app.config["BASE_URL"]}/websub/{app.config["WEBSUB_TOKEN"]}',
            "hub.topic": channel.topic_url,
            "hub.verify": "async",
            "hub.mode": "subscribe"
        },
        timeout=5
    )
    if r.status_code == 202:
        app.logger.info(f"{channel.name} subscribed.")
    else:
        app.logger.error(f"{r.status_code} when subscribing {channel.name}, {r.content}")


def subscribe_job():
    """subscribe via pubsubhubbub"""

    for c in db.session.query(Channel).filter_by(subscribe=True).all():
        subscribe(c)
    app.logger.info('Subscribed.')
