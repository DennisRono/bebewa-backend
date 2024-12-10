from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource

review_bp = Blueprint("review", __name__)
api = Api(review_bp)


class reviewResource(Resource):
    def get(self):
        return {"message": "hello"}

    def post(self):
        pass


api.add_resource(reviewResource, "/review", endpoint="review")
