from dotenv import load_dotenv
import os

# if dotenv file, load it now
dotenv_path = os.environ.get('HXPREZI_DOTENV_PATH', None)
if dotenv_path:
    load_dotenv(dotenv_path)

import click

from flask.cli import FlaskGroup
from flask.helpers import get_debug_flag

from hxprezi.app import create_app
from hxprezi.settings import DevConfig, ProdConfig


def create_hxprezi(info):
    config = DevConfig if get_debug_flag() else ProdConfig
    return create_app(config)


@click.group(cls=FlaskGroup, create_app=create_hxprezi)
def cli():
    """Main entry point"""


@cli.command("init")
def init():
    """Init application, create database tables
    and create a new user named admin with password admin
    """
    from hxprezi.extensions import db
    from hxprezi.models import User
    click.echo("create database")
    db.create_all()
    click.echo("done")

    click.echo("create user")
    user = User(
        username='admin',
        email='admin@mail.com',
        password='admin',
        active=True
    )
    db.session.add(user)
    db.session.commit()
    click.echo("created user admin")


if __name__ == "__main__":
    cli()
