
import httpretty
import json
import pytest
from unittest import mock

from hxprezi.api.resources import ManifestResource
from hxprezi.extensions import cache
from hxprezi.settings import TestConfig




def test_manifest_in_cache(app):
    # put something in cache
    manifest_id = 'chx:scroll'
    manifest_obj = {'fake': 'object'}
    cache.set(manifest_id, manifest_obj)

    # get the fake manifest
    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is not None
    assert m == manifest_obj


def test_invalid_manifest_id(app):
    manifest_id = 'too:many:colon:'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is not None
    assert 'error_message' in m
    assert 'invalid manifest_id' in  m['error_message']
    assert code == 400

def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://iiif.lib.harvard.edu/manifests/drs:blah':
        return MockResponse({'@id':
                             'https://iiif.lib.harvard.edu/manifests/drs:blah'},
                           200)
    return MockResponse(None, 404)


@httpretty.activate
@mock.patch('hxprezi.api.resources.manifest.requests.get',
           side_effect=mocked_requests_get)
def test_manifest_from_proxy(app):
    source = 'drs'
    mid = 'blah'
    manifest_id = '{0}:{1}'.format(source, mid)
    # using real object, not a mock from app!
    tstconfig = TestConfig()

    mresource = ManifestResource()
    proxy_url = mresource.make_url_for_service(
        mid, tstconfig.PROXIES[source])
    drs_sample_manifest = { '@id': proxy_url }

    httpretty.register_uri(
        httpretty.GET,
        proxy_url,
        body=drs_sample_manifest,
        content_type='application/json')

    m, code = mresource.fetch_from_service_as_string(proxy_url)

    assert m is not None
    assert code == 200
    assert 'error_message' in m
    assert proxy_url in json.dumps(m['error_message'])


def test_local_manifest_file_doesnt_exist(app):
    manifest_id = 'chx:scroll'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is not None
    assert code == 404
    assert 'not found' in m['error_message']


def test_local_manifest_path_not_file(app):
    app.config['LOCAL_MANIFESTS_DIR'] = app.config['PROJECT_ROOT']
    manifest_id = 'chx:scroll'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is not None
    assert code == 404
    assert 'not found' in m['error_message']


def test_local_manifest_ok(app):
    manifest_id = 'sample:m123'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is not None

    # test replace placeholders
    assert code == 200
    assert app.config['HX_SERVERS']['manifests']['hostname'] in m['@id']

    # test that it is in cache now
    m_from_cache = cache.get(manifest_id)
    assert m_from_cache == m


