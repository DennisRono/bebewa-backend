from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource

merchant_bp = Blueprint("merchant", __name__)
api = Api(merchant_bp)


class MerchantResource(Resource):
    def get(self):
        return {"message": "hello"}

    def post(self):
        pass


api.add_resource(MerchantResource, "/merchant", endpoint="merchant")
