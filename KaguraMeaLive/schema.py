# coding: utf-8

import click
from flask.cli import with_appcontext

from KaguraMeaLive import db

default_collation = 'utf8mb4_unicode_ci'


class Channel(db.Model):
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': default_collation}
    id = db.Column(db.String(50, collation=default_collation), primary_key=True)
    name = db.Column(db.String(50, collation=default_collation), nullable=False, index=True)
    subscribe = db.Column(db.Boolean, nullable=False, default=True)
    last_subscribe = db.Column(db.TIMESTAMP(timezone=True))
    topic_url = db.Column(db.String(150, collation=default_collation), nullable=False, index=True)
    channel_url = db.Column(db.String(150, collation=default_collation), nullable=False)


class Video(db.Model):
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': default_collation}

    id = db.Column(db.String(50, collation=default_collation), primary_key=True)
    channel_id = db.Column(db.String(50, collation=default_collation), index=True, nullable=False)
    title = db.Column(db.String(100, collation=default_collation), index=True)
    title_zh = db.Column(db.String(100, collation=default_collation))
    publish_time = db.Column(db.TIMESTAMP(timezone=True))
    last_update = db.Column(db.TIMESTAMP(timezone=True))
    deleted = db.Column(db.Boolean, nullable=False, default=False)
    video_url = db.Column(db.String(150, collation=default_collation), nullable=False)

    is_livestream = db.Column(db.Boolean, nullable=True, default=False)
    actual_start_time = db.Column(db.TIMESTAMP(timezone=True))
    scheduled_start_time = db.Column(db.TIMESTAMP(timezone=True))
    concurrent_viewers = db.Column(db.Integer)
    active_livechat_id = db.Column(db.String(50, collation=default_collation), index=True)


class Notification(db.Model):
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': default_collation}

    id = db.Column(db.Integer, primary_key=True)  # Auto-increment should be default
    content = db.Column(db.Text(collation=default_collation), nullable=False)
    last_update = db.Column(db.TIMESTAMP(timezone=True), nullable=False)


def init_db():
    db.create_all()

    channel_id = 'UCWCc8tO-uUl_7SJXIKJACMw'
    topic = f"https://www.youtube.com/xml/feeds/videos.xml?channel_id={channel_id}",

    a = Channel(
        id=channel_id,
        name="神楽めあ / KaguraMea",
        topic_url=topic,
        channel_url="https://www.youtube.com/channel/UCWCc8tO-uUl_7SJXIKJACMw"
    )

    db.session.merge(a)
    db.session.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
