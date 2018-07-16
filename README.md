# hxprezi

Simplest rest api to serve iiif manifests.


# quickstart

To stand a local vagrant hxprezi instance, follow these quick steps:

    # clone this repo
    $> git clone https://github.com/nmaekawa/hxprezi.git
    $> cd hxprezi
    
    # create and activate a virtualenv
    $> cd hxprezi
    $hxprezi> virtualenv -p python3 venv
    $hxprezi> source venv/bin/activate
    $(venv) hxprezi>
    
    # install pip requirements
    $(venv) hxprezi> pip install -r requirements/dev.txt
    
    # install hxprezi
    $(venv) hxprezi> pip install -e .
    
    # edit the sample.env file if you want to point to an image server or if
    # you have a sample manifests directory you want to use
    $(venv) hxprezi> vi sample.env
    ...
    HXPREZI_IMAGES_HOSTNAME='my.image.server.edu'
    HXPREZI_LOCAL_MANIFESTS_DIR='/Volumes/sample/manifests/mount'
    ...
    
    # run hxprezi
    $(venv) hxprezi> (FLASK_DEBUG=1 HXPREZI_DOTENV_PATH=sample.env hxprezi run)

If all goes well, you should be able to have manifests served from the
test/data/hx/sample:m123.json file in your browser by hitting the url for hx
manifests server:

    http://localhost:5000/api/v1/manifests/sample:m123



hxprezi is part of [hximg][https://github.com/nmaekawa/hximg-provision] (hx
backend for mirador), please refer to its readme for details in how to stand a
vagrant instance.


### unit tests

Use tox to create a virtualenv for tests, install all dependencies and run pytest


    $(venv) hxprezi> tox


Or run pytest manually

    $(venv) hxprezi> pytest tests



# about configuration

hxprezi serves iiif manifests from local filesys, or depending on
configuration, it fetches the requested manifest from a 3rd party server. Once
fetched, the manifest is cached and then served from this cache (it won't be
fetched again).

This cached version has all references to the 3rd party images and manifests
servers replaced by the 'local' hx images and manifests servers. hxprezi acts as a
proxy for fetched manifests from then on.

Settings configurable via env vars, defined in the dotenv file (ex:
sample.env), are:

    # 'local' hx manifests dir
    HXPREZI_LOCAL_MANIFESTS_SOURCE_DIR
    ex: HXPREZI_LOCAL_MANIFESTS_SOURCE_DIR='/opt/data/hx'
    
    # manifests cache dir
    HXPREZI_LOCAL_MANIFESTS_CACHE_DIR
    ex: HXPREZI_LOCAL_MANIFESTS_CACHE_DIR='/opt/data/cache'
    
    # hostname that will replace references to 3rd party images servers
    HXPREZI_IMAGES_HOSTNAME
    ex: HXPREZI_IMAGES_HOSTNAME='images-dev.site.com'
    
    # hostname that will replace references to 3rd party manifests servers
    ex: HXPREZI_MANIFESTS_HOSTNAME='manifests-dev.site.com'

The expected manifest directory is flat, for example, the path for the manifest
for cellx with id `12345678` should be:

    <HXPREZI_LOCAL_MANIFESTS_DIR>/hx/cellx:12345678.json


For more details on configuration for 3rd party servers, check
hxprezi/hxprezi/settings.py property `PROXIES` of class `Config`.


---eop


