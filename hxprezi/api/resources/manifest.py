
import os
import requests
from urllib.parse import urljoin

from flask import current_app
from flask import json
from flask_restful import Resource

from hxprezi.extensions import cache

REQUEST_TIMEOUT_IN_SEC = 5

class ManifestResource(Resource):
    """Single object manifest."""

    def get(self, manifest_id):
        # search in cache
        manif = cache.get(manifest_id)

        # if in cache, return manifest
        if manif is not None:
            return manif, 200

        # find if source is hx or proxied
        source, doc_id = ManifestResource.parse_id(manifest_id)
        if source is None:
            return ManifestResource.error_response(
                'invalid manifest_id; format <data_source>:<id>'), 400

        # source from proxy? fetch from service
        if source in current_app.config['MANIFESTS_PROXIES']:
            manifests_service_info = current_app.config['MANIFESTS_PROXIES'][source]
            m_object, status_code = \
                ManifestResource.fetch_from_service_as_object(
                    source, doc_id, manifests_service_info)

            if status_code != 200:
                return m_object, status_code

            # hum... this was already decoded from the response body...
            manifest_string = json.dumps(m_object)
        else:
            # it's hx, then look in filesys
            manifest_string = ManifestResource.fetch_from_file_as_string( source, doc_id)
            if manifest_string is None:
                return None, 404

        # found it! replace hostname, adjust other stuff
        fixed_manif_string = ManifestResource.fix_placeholders(
            manifest_string,
            manifests_service_info,
            current_app.config['IMAGES_PROXIES'][source]
        )
        # decode into json object, again!
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
    def fetch_from_service_as_object(cls, source, doc_id, service_info):
        """ http request the manifest from service."""

        service_url = urljoin(
            'https://{0}'.format(service_info['hostname']),
            service_info['path'],
            '{0}{1}'.format(service_info['id_prefix'], doc_id))

        try:
            r = requests.get(service_url, timeout=REQUEST_TIMEOUT_IN_SEC)
        except RequestsException as e:
            return ManifestsResource.error_response(
                'unable to fetch manifest from ({0}) - {1}'.format(
                    service_url, e)), 503
        if r.status_code != 200:
            return ManifestResource.error_response(
                'error fetching manifest from ({0}) - {1}'.format(
                    service_url, e)), r.status_code
        try:
            response = r.json()
        except ValueError as e:
            return ManifestResource.error_response(
                'error decoding json response from ({0}) - {1}'.format(
                    service_url, e)), 502

        return response, 200


    @classmethod
    def fetch_from_file_as_string(cls, source, doc_id):

        manifest_path = os.path.join(
            current_app.config['HX_MANIFESTS_DIR'],
            source, '{0}.json'.format(doc_id))

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
    def fix_placeholders(
        cls, json_string, manifests_service_info, images_service_info):
        # replace placeholders that point to hostnames that we are proxying!
        response_string = json_string.replace(
            current_app.config['HX_SERVERS']['manifests']['placeholder'],
            manifests_service_info['hostname']
        )
        response_string = response_string.replace(
            current_app.config['HX_SERVERS']['images']['placeholder'],
            images_service_info['hostname']
        )
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

