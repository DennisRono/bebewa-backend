from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")
api = Api(admin_bp)


class AdminResource(Resource):
    def post(self):
        pass


api.add_resource(AdminResource, "/admin", endpoint="admin")
