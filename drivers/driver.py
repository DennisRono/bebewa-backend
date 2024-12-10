from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource

driver_bp = Blueprint("driver", __name__)
api = Api(driver_bp)


class DriverResource(Resource):
    def get(self):
        return {"message": "hello"}

    def post(self):
        pass


api.add_resource(DriverResource, "/driver", endpoint="driver")
