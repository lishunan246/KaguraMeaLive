# coding:utf-8

import click
import requests
from flask.cli import with_appcontext

from KaguraMeaLive import db,app
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
        click.echo(f"{channel.name} subscribed.")
    else:
        click.echo(f"{r.status_code} when subscribing {channel.name}, {r.content}")


@click.command('subscribe')
@with_appcontext
def subscribe_command():
    """subscribe via pubsubhubbub"""

    for c in db.session.query(Channel).filter_by(subscribe=True).all():
        subscribe(c)
    click.echo('Subscribed.')
