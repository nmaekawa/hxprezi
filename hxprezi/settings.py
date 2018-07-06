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

    # not using flask-caching for now
    CACHE_TYPE = 'null'  # Can be "memcached", "redis", etc.

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

    LOCAL_MANIFESTS_SOURCE_DIR = os.environ.get(
        'HXPREZI_LOCAL_MANIFESTS_SOURCE_DIR',
        os.path.join(PROJECT_ROOT, 'tests/data/hx'))
    LOCAL_MANIFESTS_CACHE_DIR = os.environ.get(
        'HXPREZI_LOCAL_MANIFESTS_CACHE_DIR',
        os.path.join(PROJECT_ROOT, 'tests/data/cache'))

    # ignores cache and considers filesys the only source
    LOCAL_ONLY = os.environ.get('HXPREZI_LOCAL_ONLY', 'true').lower() == 'true'

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
    }

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


class DevConfig(Config):
    """Development configuration."""

    ENV = 'dev'
    DEBUG = True

    DB_NAME = 'dev.db'
    # Put the db file in project root
    DB_PATH = os.path.join(Config.PROJECT_ROOT, DB_NAME)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}'.format(DB_PATH)


class TestConfig(Config):
    """Test configuration."""

    ENV = 'test'
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


