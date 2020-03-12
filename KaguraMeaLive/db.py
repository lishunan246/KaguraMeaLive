# coding: utf-8

import click
import sqlalchemy.engine
from flask import g
from flask.cli import with_appcontext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

def get_engine() -> sqlalchemy.engine.Engine:
    if 'db' not in g:
        url = os.environ.get("ENGINE_URL")
        g.engine = create_engine(url, echo=True)

    return g.engine


def get_conn() -> sqlalchemy.engine.Connection:
    if 'conn' not in g:
        g.conn = get_engine().connect()

    return g.conn


def close_conn() -> None:
    conn = g.pop('conn', None)
    if conn:
        conn.close()


def get_session():
    if 'session' not in g:
        Session = sessionmaker(bind=get_engine())
        g.session = Session()

    return g.session


def close_session(e=None) -> None:
    session = g.pop('session', None)
    if session:
        session.close()


def init_db() -> None:
    engine = get_engine()

    from sqlalchemy import Table, Column, Integer, String, MetaData
    meta = MetaData()

    students = Table(
        'students', meta,
        Column('id', Integer, primary_key=True),
        Column('name', String(50)),
        Column('lastname', String(50)),
    )

    meta.create_all(engine)
    # with current_app.open_resource('schema.sql') as f:
    #     db.executescript(f.read().decode('utf8'))


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_session)
    app.cli.add_command(init_db_command)
