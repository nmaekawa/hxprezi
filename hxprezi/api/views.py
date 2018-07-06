from flask import Blueprint
from flask_restful import Api

from hxprezi.api.resources import UserResource, UserList
from hxprezi.api.resources import HealthResource
from hxprezi.api.resources import ManifestResource


blueprint = Blueprint('api', __name__, url_prefix='/api/v1')
api = Api(blueprint)


api.add_resource(UserResource, '/users/<int:user_id>')
api.add_resource(UserList, '/users')
api.add_resource(HealthResource, '/health')
api.add_resource(ManifestResource, '/manifests/<string:manifest_id>',
                 endpoint='api_manifest')
