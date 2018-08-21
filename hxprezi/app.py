import logging
import logging.config

from flask import Flask

from hxprezi import auth, api
from hxprezi.extensions import cors
from hxprezi.extensions import db, jwt, migrate
from hxprezi.settings import ProdConfig


def create_app(config_object=ProdConfig):
    """Application factory,"""
    app = Flask(__name__.split('.')[0])
    app.config.from_object(config_object)
    logging.config.dictConfig(app.config['LOGGING'])

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    """Register flask extensions."""
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # allow cors for all domains
    cors.init_app(
        app,
        max_age=86400,  # one day, matches django-cors-headers default
        methods=['OPTIONS', 'GET', 'HEAD'],
        vary_header=False,
    )

    return None


def register_blueprints(app):
    """Register flask blueprints."""
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api.views.blueprint)
    return None


def print_config(app):
    logger = logging.getLogger(__name__)
    logger.info('{0} CONFIGURATION SETTINGS:'.format(__name__))
    for key in app.config:
        logger.info('{0}: {1}'.format(key, app.config[key]))
