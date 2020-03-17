# coding:utf-8

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime

import pytz
from dateutil.parser import parse
from flask import request
from sqlalchemy import update

from KaguraMeaLive import app, db
from .schema import Channel, Notification, Video


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


def rfc3339_to_datetime(rfc3999: str) -> datetime:
    shanghai = pytz.timezone('Asia/Shanghai')

    return parse(rfc3999).astimezone(shanghai)


@dataclass
class NotificationData:
    def __init__(self):
        channel_name: str
        channel_id: str
        video_id: str
        video_url: str
        action: str
        publish_time: datetime
        delete_time: datetime
        update_time: datetime
        title: str

    def __str__(self):
        if self.action == "delete":
            return f"{self.channel_name} deleted a video: https://www.youtube.com/watch?v={self.video_id} @{self.delete_time}"
        elif self.action == "update":
            return f"{self.channel_name} updated a video '{self.title}': https://www.youtube.com/watch?v={self.video_id} publish @{self.publish_time}, update @{self.update_time}"
        else:
            return super().__str__()


def handle_notification(n: str) -> NotificationData:
    tree = ET.fromstring(n)
    e = NotificationData()
    if (len(tree)) == 1:
        # delete?
        e.action = "delete"
        entry = tree[-1]
        e.video_id = entry.attrib['ref'].split(':')[-1]
        e.video_url = f"https://www.youtube.com/watch?v={e.video_id}"
        ts = entry.attrib['when']
        e.delete_time = rfc3339_to_datetime(ts)
        by = entry[-1]
        e.channel_name = by[0].text
        e.channel_url = by[1].text
        e.channel_id = e.channel_url.split("/")[-1]
    else:
        # update
        e.action = "update"

        entry = tree[-1]
        e.video_id = entry[1].text
        e.channel_id = entry[2].text
        e.title = entry[3].text
        e.video_url = entry[4].attrib["href"]
        author = entry[5]
        e.channel_name = author[0].text
        e.channel_url = author[1].text
        e.publish_time = rfc3339_to_datetime(entry[6].text)
        e.update_time = rfc3339_to_datetime(entry[7].text)
    return e


@app.route(f'/WebSub/{app.config["WEBSUB_TOKEN"]}', methods=['POST'])
def handle_message():
    data = request.get_data().decode("utf-8")
    app.logger.debug(f'{data}')

    n = Notification(content=data, last_update=datetime.now())
    db.session.add(n)
    db.session.commit()

    e = handle_notification(data)
    app.logger.info(e)
    if e.action == "delete":
        c = Channel(
            id=e.channel_id,
            name=e.channel_name,
            channel_url=e.channel_url,
        )
        v = Video(
            id=e.video_id,
            channel_id=e.channel_id,
            deleted=True,
            last_update=e.delete_time,
            video_url=e.video_url,
        )
        db.session.merge(c)
        db.session.merge(v)
        db.session.commit()
    elif e.action == "update":
        c = Channel(
            id=e.channel_id,
            name=e.channel_name,
            channel_url=e.channel_url,
        )
        v = Video(
            id=e.video_id,
            channel_id=e.channel_id,
            deleted=False,
            video_url=e.video_url,
            title=e.title,
            publish_time=e.publish_time,
            last_update=e.update_time,
        )
        db.session.merge(c)
        db.session.merge(v)
        db.session.commit()
    else:
        app.logger.error(f'unknown event: {e}')
    return ""
