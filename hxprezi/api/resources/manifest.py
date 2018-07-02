
import logging
import os
import requests
from urllib.parse import urljoin

from flask import current_app as app
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
            status_code = 400
            return ManifestResource.error_response(
                status_code,
                'invalid manifest_id; format <data_source>:<id>'), status_code

        # init service_info as local
        service_info = ManifestResource.get_service_info(source)

        if service_info is None:
            # it's hx, then look in filesys
            service_info = app.config['HX_SERVERS']
            m_object, status_code = \
                    ManifestResource.fetch_from_file_as_string(
                        doc_id)
        else:
            # source from proxy? fetch from service
            service_url = ManifestResource.make_url_for_service(
                doc_id, service_info)
            m_object, status_code = \
                ManifestResource.fetch_from_service_as_string(
                    service_url)

        if status_code != 200:
            return m_object, status_code

        # status_code 200 has manifest_string as error_message...
        manifest_string = m_object['error_message']

        # found it! replace hostname, adjust other stuff
        fixed_manif_string = ManifestResource.fix_placeholders(
            manifest_string,
            service_info,
        )
        # decode into json object, again!
        manifest_object = json.loads(fixed_manif_string)

        # stash in cache
        cache.set(manifest_id, manifest_object)

        # return manifest
        return manifest_object, 200


    @classmethod
    def parse_id(cls, manifest_id):
        try:
            source, doc_id = manifest_id.split(':')
        except Exception:
            return (None, None)
        else:
            if source in app.config['PROXIES']:
                return (source, doc_id)
            else:
                return ('hx', manifest_id)


    @classmethod
    def error_response(cls, code, msg):
        return {
            'error_code': code,
            'error_message': msg,
        }


    @classmethod
    def get_service_info(cls, source):
        if source in app.config['PROXIES']:
            return app.config['PROXIES'][source]
        else:
            return None


    @classmethod
    def make_url_for_service(cls, doc_id, service_info):
        service_url = 'https://{0}/{1}/{2}{3}'.format(
            service_info['manifests']['hostname'],
            service_info['manifests']['path'],
            service_info['manifests']['id_prefix'],
            doc_id,
        )
        return service_url


    @classmethod
    def fetch_from_service_as_object(cls, service_url):
        """ http request the manifest from 3rd party service (proxy)."""

        try:
            r = requests.get(service_url, timeout=REQUEST_TIMEOUT_IN_SEC)
        except requests.exceptions.RequestException as e:
            status_code = 503
            return ManifestResource.error_response(
                status_code,
                'unable to fetch manifest from ({0}) - {1}'.format(
                    service_url, e)), status_code

        if r.status_code != 200:
            return ManifestResource.error_response(
                r.status_code,
                'error fetching manifest from ({0}) - {1}'.format(
                    service_url, r.status_code)), r.status_code
        try:
            response = r.json()
        except ValueError as e:
            status_code = 502
            return ManifestResource.error_response(
                status_code,
                'error decoding json response from ({0}) - {1}'.format(
                    service_url, e)), status_code

        return response, 200


    @classmethod
    def fetch_from_service_as_string(cls, service_url):
        """ http request the manifest from 3rd party service (proxy)."""

        response, status_code = ManifestResource.fetch_from_service_as_object(
            service_url)
        if status_code == 200:
            return ManifestResource.error_response(
                status_code, json.dumps(response)), status_code
        else:
            return response, status_code


    @classmethod
    def fetch_from_file_as_string(cls, doc_id):
        """ load the manifest from local filesys; implies an hx manifest."""

        source = 'hx'
        manifest_path = os.path.join(
            app.config['LOCAL_MANIFESTS_DIR'],
            source,
            '{0}.json'.format(doc_id))

        manifest_as_json_string = None
        if os.path.exists(manifest_path) \
                and os.path.isfile(manifest_path) \
                and os.access(manifest_path, os.R_OK):
            with open(manifest_path, 'r') as fd:
                manifest_as_json_string = fd.read()

        if manifest_as_json_string is None:
            status_code = 404
            response = 'manifest ({0}/{1}) not found'.format(source, doc_id)
        else:
            status_code = 200
            response = manifest_as_json_string

        return ManifestResource.error_response(
            status_code, response), status_code


    @classmethod
    def fix_placeholders(
        cls, json_string, service_info):
        # replace placeholders that point to hostnames that we are proxying!
        response_string = json_string.replace(
            service_info['manifests']['placeholder'],
            app.config['HX_SERVERS']['manifests']['hostname'],
        )
        response_string = response_string.replace(
            service_info['images']['placeholder'],
            app.config['HX_SERVERS']['images']['hostname'],
        )
        return response_string


