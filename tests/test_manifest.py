
import pytest

from hxprezi.api.resources import ManifestResource
from hxprezi.extensions import cache




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


def test_manifest_from_proxy(app):
    manifest_id = 'drs:1234567'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is not None
    assert 'error_message' in m
    assert 'not able to fetch from source(drs) yet' in m['error_message']
    assert code == 400


def test_local_manifest_file_doesnt_exist(app):
    manifest_id = 'chx:scroll'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is None
    assert code == 404


def test_local_manifest_path_not_file(app):
    app.config['LOCAL_MANIFESTS_DIR'] = app.config['PROJECT_ROOT']
    manifest_id = 'chx:scroll'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is None
    assert code == 404


def test_local_manifest_ok(app):
    manifest_id = 'sample:m123'

    mresource = ManifestResource()
    m, code = mresource.get(manifest_id)

    assert m is not None

    # test replace placeholders
    assert app.config['HX_SERVERS']['manifests']['hostname'] in m['@id']

    # test that it is in cache now
    m_from_cache = cache.get(manifest_id)
    assert m_from_cache == m


