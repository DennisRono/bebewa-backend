from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from models import Commodity, Commodity_Image,db
from sqlalchemy.exc import DatabaseError


commodity_bp = Blueprint("commodity", __name__)
api = Api(commodity_bp)


#  creating a Commodities Resource
class Commodities(Resource):
    # a method to get all commodities
    def get(self):
        try:
            # querying the database and getting all the commodities
            commodities = Commodity.query.all()

            #  Looping through the commodities to get one commodity and making it to a dictionary
            commodity_dict = [commodity.to_dict() for commodity in commodities]
            # creating and returning a response based on the commodity dict
            response = make_response(commodity_dict, 200)
            return response
        except DatabaseError as e:
            #  creating and returning an error message 
            error_message = f"Database error: {str(e)}"
            return make_response({"error":error_message},500)
        except Exception as e:
            # creating and returning an unexpected error message
            error_message= f"An uexpected error occured:{str(e)}"
            return make_response({"error": error_message},500)
    pass

api.add_resource(Commodities, "/commodities", endpoint="commodities")