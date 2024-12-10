from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource

order_bp = Blueprint("order", __name__)
api = Api(order_bp)


class OrderResource(Resource):
    def get(self):
        return {"message": "hello"}

    def post(self):
        pass


api.add_resource(OrderResource, "/order", endpoint="order")
