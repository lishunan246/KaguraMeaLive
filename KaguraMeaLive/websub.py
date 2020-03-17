# coding:utf-8

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime

from flask import request
from sqlalchemy import update

from KaguraMeaLive import app, db
from .LiveStreamDetails import LiveStreamingDetails
from .schema import Channel, Notification, Video
from .utils import rfc3339_to_datetime


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


@dataclass
class NotificationData:
    video_id: str
    video_url: str
    channel_name: str
    channel_id: str
    channel_url: str
    title: str = ""
    action: str = ""
    publish_time: datetime = None
    delete_time: datetime = None
    update_time: datetime = None
    livestreaming_details: LiveStreamingDetails = None

    def __str__(self):
        if self.action == "delete":
            return f"{self.channel_name} deleted a video: https://www.youtube.com/watch?v={self.video_id} @{self.delete_time}"
        elif self.action == "update":
            return f"{self.channel_name} updated a video '{self.title}': https://www.youtube.com/watch?v={self.video_id} publish @{self.publish_time}, update @{self.update_time}"
        else:
            return super().__str__()


def handle_notification(n: str) -> NotificationData:
    tree = ET.fromstring(n)
    if (len(tree)) == 1:
        # delete?
        entry = tree[-1]
        by = entry[-1]
        # noinspection PyTypeChecker
        video_id: str = entry.attrib['ref'].split(':')[-1],

        e = NotificationData(
            video_id=video_id,
            video_url=f"https://www.youtube.com/watch?v={video_id}",
            channel_name=by[0].text,
            channel_url=by[1].text,
            channel_id=by[1].text.split("/")[-1],
            action="delete",
            delete_time=rfc3339_to_datetime(entry.attrib['when'])
        )

    else:
        # update
        entry = tree[-1]
        author = entry[5]
        e = NotificationData(
            video_id=entry[1].text,
            video_url=entry[4].attrib["href"],
            channel_id=entry[2].text,
            channel_name=author[0].text,
            channel_url=author[1].text,
            action="update",
            publish_time=rfc3339_to_datetime(entry[6].text),
            update_time=rfc3339_to_datetime(entry[7].text),
            title=entry[3].text,
        )

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
        return ""

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
        d = LiveStreamingDetails(video_id=e.video_id)
        d.get(app.config['YOUTUBE_API_KEY'])

        # 视频，非直播
        if not d.isLiveStream:
            app.logger.info(f'video {e.video_id} is not a livestream')
            db.session.merge(c)
            db.session.merge(v)
            db.session.commit()
            return ""

        else:
            e.livestreaming_details = d
            v.is_livestream = True
            v.actual_start_time = d.actualStartTime
            v.active_livechat_id = d.activeLiveChatId
            v.concurrent_viewers = d.concurrentViewers
            v.scheduled_start_time = d.scheduledStartTime

            l = db.session.query(Video).filter_by(video_id=e.video_id).all()
            # 直播信息更新
            if l:
                app.logger.info('update previous livestreaming')
                db.session.merge(c)
                db.session.merge(v)
                db.session.commit()
                # todo: alert(e)
                return ""
            else:
                lt = db.session.query(Video).filter_by(title=e.title).all()
                # 还没改title， 先不管
                if lt:
                    app.logger.info('title seen before, ignored')
                    return ""
                # 改了title，需要alert
                else:
                    app.logger.info('add new livestreaming')
                    db.session.merge(c)
                    db.session.merge(v)
                    db.session.commit()
                    # todo: alert(e)
                    return ""
    else:
        app.logger.error(f'unknown event: {e}')
        return ""
