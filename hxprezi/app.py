import logging
import logging.config

from flask import Flask

from hxprezi import auth, api
from hxprezi.extensions import cache, db, jwt, migrate
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
    cache.init_app(app)
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    return None


def register_blueprints(app):
    """Register flask blueprints."""
    app.register_blueprint(auth.views.blueprint)
    app.register_blueprint(api.views.blueprint)
    return None
