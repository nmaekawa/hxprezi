import logging
import os
import requests
from urllib.parse import urljoin

from flask import current_app as app
from flask import json
from flask import request
from flask import url_for
from flask_restful import Api
from flask_restful import Resource


REQUEST_TIMEOUT_IN_SEC = 5


class ManifestResourceResponse(object):
    """response object for manifest resource.

    depending on status_code, it can provide:
    status_code == 200
        manifest_as_json_string
        manifest_as_json_object
    status_code != 200
        error_message (as string)
    """
    def __init__(self,
                 status_code,
                 json_as_object=None, json_as_string='',
                 error_message=''):
        self._status_code = status_code
        self._json = None
        self._error_message = ''
        if status_code == 200:
            if json_as_object is not None:
                self._json = json_as_object
                # this ignores arg json_as_string
            elif json_as_string:
                # might raise JsonException if string not parsable json
                self._json = json.loads(json_as_string)
            else:
                raise AttributeError((
                    'cannot create ManifestResourceResponse with '
                    'status_code(200) and empty json object'))
        else:  # need an error_message
            if error_message:
                self._error_message = error_message
            else:
                # don't blame the messenger!
                self._error_message = (
                    'the developer failed to describe the error that just '
                    'ocurred, thus this lame message')
    @property
    def status_code(self):
        return self._status_code

    @property
    def manifest_obj(self):
        return self._json
    @manifest_obj.setter
    def manifest_obj(self, value):
        if self._status_code != 200:
            raise ValueError(
                'cannot modify manifest object when status_code({0})'.format(
                    self._status_code))
        self._json = value

    @property
    def manifest_str(self):
        return json.dumps(self._json)
    @manifest_str.setter
    def manifest_str(self, value):
        if self._status_code != 200:
            raise ValueError(
                'cannot modify manifest string when status_code({0})'.format(
                    self._status_code))
        self._json = json.loads(value)  # raise exc if not parsable

    @property
    def error_message(self):
        return self._error_message



class ManifestResource(Resource):
    """Single object manifest."""

    def get(self, manifest_id):

        # is it in filecache?
        resp = self.fetch_from_file(manifest_id, from_cache=True)

        if resp.status_code == 200:
            return resp.manifest_obj, 200

        # not in cache, is it local?
        resp = self.fetch_from_file(manifest_id, from_cache=False)

        if resp.status_code == 200:
            service_info = app.config['HX_SERVERS']

            # fix service context and profile for local manifests
            fixed_manif_obj = self.fix_local_service_context(resp.manifest_obj)

        # not local; find if we know how to proxy this source
        else:
            source, doc_id = self.parse_id(manifest_id)

            logging.getLogger(__name__).debug(
                'in get manifestResource({0}) SOURCE({1}) DOC({2})'.format(
                    manifest_id, source, doc_id))

            if source is None:
                e_message = ('invalid manifest_id({}); '
                             'format <data_source>:<id>').format(manifest_id)
                return ManifestResource.error_response(
                    400, e_message), 400

            elif source == 'hx':
                return ManifestResource.error_response(
                    404, 'not found ({})'.format(manifest_id)), 404

            # init service_info
            service_info = self.get_service_info(source)
            if service_info is None:
                error_message = 'unknown source for manifest_id({0})'.format(manifest_id)
                return ManifestResource.error_response(404, error_message)

            # fetch from service
            service_url = self.make_url_for_service(
                doc_id, service_info)
            resp = self.fetch_from_service(service_url)

            # return error while fetching
            if resp.status_code != 200:
                return ManifestResource.error_response(
                    resp.status_code, resp.error_message)

        # found it! replace hostname, adjust other stuff
        fixed_manif_string = self.fix_placeholders(
            resp.manifest_str,
            service_info,
        )

        # save it back to resp obj to jsonify
        resp.manifest_str = fixed_manif_string

        # save in filesys cache
        self.save_to_filecache_as_string(manifest_id, resp.manifest_str)

        # return manifest
        return resp.manifest_obj, 200


    def parse_id(self, manifest_id):
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


    def get_service_info(self, source):
        if source in app.config['PROXIES']:
            return app.config['PROXIES'][source]
        else:
            return None


    def make_url_for_service(self, doc_id, service_info):
        service_url = 'https://{0}/{1}/{2}{3}'.format(
            service_info['manifests']['hostname'],
            service_info['manifests']['path'],
            service_info['manifests']['id_prefix'],
            doc_id,
        )
        return service_url


    def fetch_from_service(self, service_url):
        """ http request the manifest from 3rd party service (proxy)."""

        try:
            r = requests.get(service_url, timeout=REQUEST_TIMEOUT_IN_SEC)
        except requests.exceptions.RequestException as e:
            status_code = 503
            emsg = 'unable to fetch manifest from ({0}) - {1}'.format(
                service_url, e)
            return ManifestResourceResponse(503, error_message=emsg)

        if r.status_code != 200:
            emsg = 'error fetching manifest from ({0}) - {1}'.format(
                service_url, r.status_code)
            return ManifestResourceResponse(r.status_code, error_messag=emsg)

        try:
            response = r.json()
        except ValueError as e:
            emsg = 'error decoding json response from ({0}) - {1}'.format(
                    service_url, e)
            status_code = 502
            return ManifestResource.error_response(502, emsg)

        return ManifestResourceResponse(200, json_as_object=response)


    def fetch_from_file(self, doc_id, from_cache=False):
        """ load the manifest from local filesys; implies an hx manifest."""

        if from_cache:
            basedir = app.config['LOCAL_MANIFESTS_CACHE_DIR']
        else:
            basedir = app.config['LOCAL_MANIFESTS_SOURCE_DIR']

        manifest_as_json_string = None
        manifest_path = os.path.join(basedir, '{0}.json'.format(doc_id))
        if os.path.exists(manifest_path) \
           and os.path.isfile(manifest_path) \
           and os.access(manifest_path, os.R_OK):
            with open(manifest_path, 'r') as fd:
                manifest_as_json_string = fd.read()

        if manifest_as_json_string is None:
            response = ManifestResourceResponse(
                404,  # not found
                error_message='local manifest ({0}) not found'.format(doc_id))
        else:
            response = ManifestResourceResponse(
                200, json_as_string=manifest_as_json_string)

        return response


    def save_to_filecache_as_string(self, doc_id, manifest_string):
        """ save manifest string to filesys as hx source.

        once saved, we don't fetch it from 3rd party anymore.
        """
        manifest_path = os.path.join(
            app.config['LOCAL_MANIFESTS_CACHE_DIR'],
            '{0}.json'.format(doc_id))

        with open(manifest_path, 'w') as fd:
            fd.write(manifest_string)


    def fix_placeholders(
        self, json_string, service_info):
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


    def fix_local_service_context(self, manifest_obj):
        # set service context and profile to iiif image api 2.0
        for sequence in manifest_obj['sequences']:
            for canvases in sequence['canvases']:
                for image in canvases['images']:
                    image['resource']['service']['profile'] = \
                            app.config['HX_SERVICE_PROFILE']
                    image['resource']['service']['@context'] = \
                            app.config['HX_SERVICE_CONTEXT']

        return manifest_obj






