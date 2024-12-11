from models import Driver,Vehicle,db
from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime



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
api.add_resource(Get_Driver_Data,'/driver-data',endpoint="driver-data")

#resource that enables the driver to register their vehicle
class Register_Vehicle(Resource):
    @jwt_required()
    def post(self):
        #data passed in is a form data which contains json data and files 
        #gets files labelled under the key "images"
        images=request.files.getlist("images") #points to an array of images
        vehicle_data=request.form.get("vehicle_data") #points to a dict "vehicle_data" that contains json data about the vehicle
        if not vehicle_data:
            return make_response({"msg":"Required data is missing"},400)
        if len(images)==0:
            return make_response({"msg":"Upload atleast one image"},400)
        data=json.loads(vehicle_data) #parse form data into json format
        if not all(attr in data for attr in [
            "number_plate","model_name","make_name","tonnage","color"
        ]):
            return make_response({"msg":"Required data is missing"},400)
        number_plate=data.get("number_plate")
        try:
            vehicle=Vehicle.query.filter_by(number_plate=number_plate).first()
            if vehicle:
                return make_response({"msg":"Vehicle already exists"},400)
            new_vehicle=Vehicle(
                number_plate=number_plate,
                model_name=data.get("model_name"),
                make_name=data.get("make_name"),
                tonnage=data.get("tonnage"),
                color=data.get("color"),
                created_at=datetime.now(),
                mark_deleted=False
            )
            db.session.add(new_vehicle)
            db.session.flush() #assigns an id to the newly added vehicle
            #post images associated with a vehicle
            pass

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(e)
            return make_response({"msg":"Internal server error"},500)
api.add_resource(Register_Vehicle,'/add-vehicle', endpoint="add-vehicle")

#Update,Get,Delete vehicle details
class Vehicle_By_Number_Plate(Resource):
    def get(self,plate):
        try:
            vehicle=Vehicle.query.filter_by(number_plate=plate).first()
            if vehicle:
                return make_response(vehicle.to_dict(),200)
            return make_response({"msg":"Vehicle doesnt exist"})
        except Exception as e:
            print(e)
            return make_response({"msg":"Server error"},500)
    def patch(self,plate):
        # this method only updates delete status and adds images 
        # no other data is allowed to be updated 
        data=request.get_json()
        try:
            vehicle=Vehicle.query.filter_by(number_plate=plate).first()
            if not vehicle:
                return make_response({"msg":f"Vehicle plate number{plate} is not registered"},400)
            if "mark_deleted" in data:
                setattr(vehicle,"mark_deleted",data.get("mark_deleted"))
            #add update image logic


            db.session.commit()
            return make_response(vehicle.to_dict(),200)
        except Exception as e:
            db.session.rollback()
            print(e)
            return make_response({"msg":"Server error"},500)


#resource that allows a driver to bid their price for an order
