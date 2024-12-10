from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource

metrics_bp = Blueprint("metrics", __name__)
api = Api(metrics_bp)


class MetricsResource(Resource):
    def get(self):
        return {"message": "hello"}

    def post(self):
        pass


api.add_resource(MetricsResource, "/metrics", endpoint="metrics")
