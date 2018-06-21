from flask_restful import Resource

from hxprezi import __version__


class HealthResource(Resource):
    """Single object resource """

    def get(self):
        return {"package_version": __version__}

