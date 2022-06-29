from flask_sqlalchemy import SQLAlchemy
import click

from flask import current_app, g
from flask.cli import with_appcontext

db = SQLAlchemy()

def get_db():
    """Get database connection
    """
    if "db" not in g:
        g.db = db#SQLAlchemy(current_app)
    return g.db

def close_db(e=None):
    """Close the database connection, does not seem to work
    """
    db = g.pop("db", None)

def init_db():
    """Initialize the database
    """
    db = get_db()
    db.create_all()

@click.command("init-db")
@with_appcontext
def init_db_command():
    """Create new tables
    """
    init_db()
    click.echo("Initialized the database.")

@click.command("clear-db")
@with_appcontext
def clear_db_command():
    """Drop all tables
    """
    get_db().drop_all()
    click.echo("Dropped all tables.")


def init_app(app):
    db.init_app(app)
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(clear_db_command)
