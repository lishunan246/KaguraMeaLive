# coding: utf-8

import click
from flask.cli import with_appcontext

from KaguraMeaLive import db

default_collation = 'utf8mb4_unicode_ci'


class Channel(db.Model):
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': default_collation}
    id = db.Column(db.String(50, collation=default_collation), primary_key=True)
    name = db.Column(db.String(50, collation=default_collation), nullable=False)


def init_db():
    db.create_all()


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')
