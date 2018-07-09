
import httpretty
import json
import os
import pytest
from unittest import mock

from hxprezi.api.resources import ManifestResource
from hxprezi.settings import TestConfig


def test_manifest_in_filecache(app):
    manifest_from_file = {
        'error_message': '{"fake": "object"}',
        'status_code': 200
    }

    mresource = ManifestResource()
    mresource.fetch_from_file_as_string = mock.MagicMock(
        return_value=(manifest_from_file, 200))

    # get the fake manifest
    m, code = mresource.get('blah')

    assert code == 200
    assert m is not None
    assert m == json.loads(manifest_from_file['error_message'])


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


def test_local_manifest_source_doesnt_exist(app):
    manifest_id = 'chx:painting'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is not None
    assert code == 404
    assert 'not found' in m['error_message']

def test_local_manifest_ok(app):
    manifest_id = 'sample:m123'
    # forcing my hand to pass test in python3.5
    m_content = '{\n"attribution": "Provided by Harvard University",\n"description": "Prosperous Suzhou Scroll",\n"label": "Gusu fan hua tu",\n"sequences": [\n{\n"canvases": [\n{\n"label": "Prosperous Suzhou Scroll",\n"width": 114981,\n"images": [\n{\n"resource": {\n"service": {\n"@context": "http://iiif.io/api/image/1/context.json",\n"profile": "http://library.stanford.edu/iiif/image-api/1.1/conformance.html#level1",\n"@id": "https://images.vm/ids/iiif/400098039"\n},\n"format": "image/jpeg",\n"height": 3466,\n"width": 114981,\n"@id": "https://images.vm/ids/iiif/400098039/full/full/0/native",\n"@type": "dcterms:Image"\n},\n"on": "https://manifests.vm/manifests/sample:m123/canvas/canvas-400098039.json",\n"motivation": "sc:painting",\n"@id": "https://manifests.vm/manifests/sample:m123/annotation/anno-400098039.json",\n"@type": "oa:Annotation"\n}\n],\n"height": 3466,\n"@id": "https://manifests.vm/manifests/sample:m123/canvas/canvas-400098039.json",\n"@type": "sc:Canvas"\n}\n],\n"viewingHint": "individuals",\n"@id": "https://manifests.vm/manifests/sample:m123/sequence/normal.json",\n"@type": "sc:Sequence"\n}\n],\n"@context": "http://www.shared-canvas.org/ns/context.json",\n"@id": "https://manifests.vm/manifests/sample:m123",\n"@type": "sc:Manifest",\n"logo": "https://images.vm/iiif/harvard_logo.jpg/full/full/0/default.jpg"\n}\n'

    mresource = ManifestResource()
    mresource.save_to_filecache_as_string = mock.MagicMock(return_value=None)

    m, code = mresource.get(manifest_id)

    assert m is not None

    # test replace placeholders
    assert code == 200
    assert app.config['HX_SERVERS']['manifests']['hostname'] in m['@id']

    # test that it is in cache now
    mresource.save_to_filecache_as_string.assert_called_with(manifest_id, m_content)


