# hxprezi

Simplest rest api to serve iiif manifests.


# disclaimer

For demo purposes only! provided to show how to setup a hxprezi vagrant
installation and support to this repo is OUT-OF-SCOPE at this time.


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


Or run pytest manually:o

    $(venv) hxprezi> pytest tests


# about configuration

hxprezi serves manifests from the filesys, in the configured
`HXPREZI_LOCAL_MANIFESTS_DIR` env vars set in dotenv file (in examples below
`sample.env`).

Once hxprezi finds the manifest file and replace the references to images and
manifests servers to the ones configured in `HXPREZI_IMAGES_HOSTNAME` and
`HXPREZI_MANIFESTS_HOSTNAME` env vars, it caches these edited versions in the
filesys cache dir (`HXPREZI_LOCAL_MANIFESTS_CACHE_DIR` env var) and never looks
back - a refresh endpoint is to be implemented in the future.

The expected manifest directory is flat, for example, the path for the manifest
for cellx with id `12345678` should be:

    <HXPREZI_LOCAL_MANIFESTS_DIR>/hx/cellx:12345678.json

Say you don't want to serve manifests from Harvard Museums yet, you can drop
them in the manifests dir, and hxprezi won't try to fetch from the musemus
servers. For example:

    <HXPREZI_LOCAL_MANIFESTS_DIR>/hx/huam:98765432.json

---eop


