# -*- coding: utf-8 -*-
"""Application configuration."""
import os


class Config(object):
    """Base configuration."""

    SECRET_KEY = os.environ.get('HXPREZI_SECRET', 'secret-key')
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir))
    PROJECT_NAME = __name__.split('.')[0]
    PROJECT_NAME_UPPER = PROJECT_NAME.upper()

    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    HX_SERVERS = {
        'manifests': {
            'hostname': os.environ.get('HXPREZI_MANIFESTS_HOSTNAME', 'manifests.vm'),
            'path': 'manifests',
            'id_prefix': '',
            'placeholder': 'oculus.harvardx.harvard.edu',
        },
        'images': {
            'hostname': os.environ.get('HXPREZI_IMAGES_HOSTNAME', 'images.vm'),
            'path': 'iiif',
            'id_prefix': '',
            'placeholder': 'images.harvardx.harvard.edu',
        },
    }

    PROXIES = {
        'drs': {
            'manifests': {
                'hostname': 'iiif.lib.harvard.edu',
                'path': 'manifests',
                'id_prefix': 'drs:',
                'placeholder': 'iiif.lib.harvard.edu',
            },
            'images': {
                'hostname': 'ids.lib.harvard.edu',
                'path': 'ids/iiif',
                'id_prefix': '',
                'placeholder': 'ids.lib.harvard.edu',
            },
        },
        'huam': {
            'manifests': {
                'hostname': 'iiif.harvardartmuseums.org',
                'path': 'manifests/object',
                'id_prefix': '',
                'placeholder': 'iiif.harvardartmuseums.org',
            },
            'images': {
                'hostname': 'ids.lib.harvard.edu',
                'path': 'ids/iiif',
                'id_prefix': '',
                'placeholder': 'ids.lib.harvard.edu',
            },
        },
        'HX': HX_SERVERS,
    }

    LOCAL_MANIFESTS_DIR = os.environ.get(
        'HXPREZI_LOCAL_MANIFESTS_DIR', '/tmp/manifests')

    # Logging config
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'simple': {
                'format': ('%(asctime)s|%(levelname)s [%(filename)s:%(funcName)s]'
                        ' %(message)s')
            },
        },
        'handlers': {
            'console': {
                'level': 'DEBUG',
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'stream': 'ext://sys.stdout',
            },
            'errorfile_handler': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'formatter': 'simple',
                'filename': 'hxprezi_errors.log',
                'maxBytes': 10485760,  # 10MB
                'backupCount': 7,
                'encoding': 'utf8',
            },
        },
        'loggers': {
            'hxprezi': {
                'level': 'DEBUG',
                'handlers': ['console'],
                'propagate': True
            },
            'root': {
                'level': 'DEBUG',
                'handlers': ['console'],
            },
        }
    }


class ProdConfig(Config):
    """Production configuration."""

    ENV = 'prod'
    DEBUG = False

    DB_PATH = os.environ.get(
        'HXPREZI_DB_PATH',
        os.path.join(Config.PROJECT_ROOT, 'database.db'))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)

    CACHE_TYPE = 'redis'
    # TODO: add redis config!


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True

    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)

    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.


class TestConfig(Config):
    """Test configuration."""

    ENV = 'test'
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

    CACHE_TYPE = 'simple'  # Can be "memcached", "redis", etc.

    LOCAL_MANIFESTS_DIR = os.path.join(Config.PROJECT_ROOT, 'tests/data')




