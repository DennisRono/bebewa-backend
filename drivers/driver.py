from models import Driver
from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity

driver_bp = Blueprint("driver", __name__)
api = Api(driver_bp)

#resource that returns driver related data once they are logged in
class Get_Driver_Data(Resource):
    @jwt_required()
    def get(self):
        try:
            driver=Driver.query.filter_by(id=get_jwt_identity()).first()
            if not driver:
                return make_response({"msg":"Driver not found"},400)
            return make_response(driver.to_dict(),200)
        except Exception as e:
            return make_response({"msg":"Internal server error"},500)
api.add_resource(Get_Driver_Data,'/data',endpoint="driver-data")

#resource that allows a driver to bid their price for an order
