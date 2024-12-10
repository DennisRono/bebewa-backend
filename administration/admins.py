from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource

# login
# An Admin can Add another  [Roles]
# All CRUD operations on the driver/Merchant (Soft Delete a Driver)
# Analytics in the Dashboard [Bar Graph, Line Graph, Metrics]
# Warnings Before Deletions


admin_bp = Blueprint("admin", __name__)
api = Api(admin_bp)


class AdminResource(Resource):
    def get(self):
        return {"message": "hello"}

    def post(self):
        pass


api.add_resource(AdminResource, "/", endpoint="admin")
