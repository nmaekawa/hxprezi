
import os

from flask import current_app
from flask import json
from flask_restful import Resource

from hxprezi.extensions import cache


class ManifestResource(Resource):
    """Single object manifest."""

    def get(self, manifest_id):
        # search in cache
        manif = cache.get(manifest_id)

        # if in cache, return manifest
        if manif is not None:
            return manif

        # not in cache
        (source, doc_id) = ManifestResource.parse_id(manifest_id)
        if source is None:
            return ManifestResource.error_response(
                'invalid manifest_id; format <data_source>:<id>'), 400

        # source from proxy? pull from 3rd party (libraries)
        if source in current_app.config['MANIFESTS_PROXIES']:
            # not implemented yet
            return ManifestResource.error_response(
                'not able to fetch from source({0}) yet'.format(source)), 400

        # it's local, then look in filesys
        manif_string = ManifestResource.get_as_json_string(manifest_id)
        if manif_string is None:
            return None, 404
            #return ManifestResource.error_response(
            #    'manifest_id ({0}) not found'), 404

        # if found, fill in the gaps, adjust other stuff
        fixed_manif_string = ManifestResource.fix_placeholders(manif_string)
        manifest_object = json.loads(fixed_manif_string)

        # stash in cache
        cache.set(manifest_id, manifest_object)

        # return manifest
        return manifest_object


    @classmethod
    def parse_id(cls, manifest_id):
        try:
            source, doc_id = manifest_id.split(':')
        except Exception:
            return (None, None)
        else:
            return (source, doc_id)

    @classmethod
    def error_response(cls, msg):
        return {'error_message': msg}

    @classmethod
    def get_as_json_string(cls, manifest_id):

        manifest_path = os.path.join(
            current_app.config['LOCAL_MANIFESTS_DIR'],
            manifest_id.replace(':', '/') + '.json')

        manifest_as_json_string = None
        if os.path.exists(manifest_path) \
                and os.path.isfile(manifest_path) \
                and os.access(manifest_path, os.R_OK):
            with open(manifest_path, 'r') as fd:
                manifest_as_json_string = fd.read()

        return manifest_as_json_string

    @classmethod
    def get_as_json_object(cls, manifest_id):
        json_string = cls.get_as_json_string(manifest_id)
        return json.loads(json_string) if json_string is not None else None

    @classmethod
    def fix_placeholders(cls, json_string):
        # replace placeholders that point to hostnames that we are proxying!
        response_string = json_string.replace(
            current_app.config['HOSTNAME_PLACEHOLDERS']['manifests'],
            current_app.config['MANIFESTS_PROXIES']['local']['hostname'])
        response_string = response_string.replace(
            current_app.config['HOSTNAME_PLACEHOLDERS']['images'],
            current_app.config['IMAGES_PROXIES']['local']['hostname'])
        return response_string


def manifest(doc_id):
    manifest_path = '/Users/nmaekawa/Documents/devo/mirador-backend/hxprezi/data'
    prezi_dns = 'prezi.vm'
    image_dns = 'image.vm'

    logger = logging.getLogger(__name__)
    logger.error('--------------------------------- doc_id is ({0})'.format(doc_id))
    doc_id = doc_id.replace(':', '/')
    logger.error('--------------------------------- doc_id is ({0})'.format(doc_id))
    doc_path = os.path.join(manifest_path, doc_id + '.json')

    with open(doc_path, 'r') as f:
        template = f.read()

    template = template.replace('images.harvardx.harvard.edu', image_dns)
    template = template.replace('oculus.harvardx.harvard.edu', prezi_dns)

    doc = json.loads(template)
    doc['sequences'][0]['canvases'][0]['images'][0]['resource']['service']['@context'] = \
            'http://iiif.io/api/image/1/context.json'

    return json.jsonify(doc)

