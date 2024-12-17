from models import Driver,Vehicle,db,Vehicle_Image,Bid
from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from datetime import datetime
from config import Config
# from cloudinary import clo
import cloudinary
import cloudinary.uploader
import cloudinary.api

driver_bp = Blueprint("driver", __name__)
api = Api(driver_bp)

cloudinary.config(
    cloud_name=Config.cloudinary_cloud_name,
    api_key=Config.cloudinary_api_key,
    api_secret=Config.cloudinary_api_secret
)


#resource that returns driver related data once they are logged in
class Get_Driver_Data(Resource):
    @jwt_required()
    def get(self):
        try:
            driver=Driver.query.filter_by(id=get_jwt_identity()).first()
            if not driver or driver.mark_deleted==True:
                return make_response({"message":"Driver not found"},400)
            return make_response(driver.to_dict(),200)
        except Exception as e:
            return make_response({"message":"Internal server error"},500)
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
            return make_response({"message":"Vehicle data is missing"},400)
        if not images or len(images)==0:
            return make_response({"message":"Upload atleast one image"},400)
        data=json.loads(vehicle_data) #parse form data into json format
        if not all(attr in data for attr in [
            "number_plate","model_name","make_name","tonnage","color"
        ]):
            return make_response({"message":"Required data is missing"},400)
        number_plate=data.get("number_plate")
        try:
            vehicle=Vehicle.query.filter_by(number_plate=number_plate).first()
            if vehicle and vehicle.mark_deleted==False:
                return make_response({"message":"Vehicle already exists"},400)
            #post images associated with a vehicle
            images_url=[] #initialize an empty array to store the generated urls
            for file in images:
                if file.filename!="" and file.filename in ["jpg","png","jpeg"]:
                    result=cloudinary.uploader.upload(file)
                    images_url.append(result.get("url"))
            #create a new vehicle record
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
            #post image urls and associate them with the newly created vehicle entry
            for url in images_url:
                new_url=Vehicle_Image(
                    image_url=url,
                    created_at=datetime.now(),
                    vehicle_id=new_vehicle.id
                )
                db.session.add(new_url)
            db.session.commit()
            return make_response(new_vehicle.to_dict(),201)
        except Exception as e:
            db.session.rollback()
            print(e)
            return make_response({"message":"Internal server error"},500)
api.add_resource(Register_Vehicle,'/add-vehicle', endpoint="add-vehicle")

#Update,Get,Delete vehicle details
class Vehicle_By_Number_Plate(Resource):
    def get(self,plate):
        try:
            vehicle=Vehicle.query.filter_by(number_plate=plate).first()
            if vehicle and vehicle.mark_deleted==False:
                return make_response(vehicle.to_dict(),200)
            return make_response({"message":"Vehicle doesnt exist"},400)
        except Exception as e:
            print(e)
            return make_response({"message":"Server error"},500)
        
    @jwt_required()
    def patch(self,plate):
        # this method only updates delete status and adds images 
        # no other data is allowed to be updated 
        images=request.files.getlist("images")
        vehicle_data=request.form.get("vehicle_data")
        try:
            vehicle=Vehicle.query.filter_by(number_plate=plate).first()
            if not vehicle or vehicle.mark_deleted==True:
                return make_response({"message":f"Vehicle plate number{plate} is not registered"},400)
            if vehicle_data:
                data=json.loads(vehicle_data)
                if "mark_deleted" not in data:
                    setattr(vehicle,"mark_deleted",data.get("mark_deleted"))
            #add update image logic
            if images and len(images)>0:
                image_urls=[]
                for image in images:
                    if image.filename!="" and image.filename in ["jpg","jpeg","png"]:
                        result=cloudinary.uploader.upload(image)
                        image_urls.append(result.get("url"))
                if len(image_urls)>0:
                    for image_url in image_urls:
                        new_image_url=Vehicle_Image(
                            image_url=image_url,
                            created_at=datetime.now(),
                            vehicle_id=vehicle.id
                        )
                        db.session.add(new_image_url)
            db.session.commit()
            return make_response(vehicle.to_dict(),200)
        except Exception as e:
            db.session.rollback()
            print(e)
            return make_response({"message":"Server error"},500)
api.add_resource(Vehicle_By_Number_Plate,"/vehicle/<string:plate>")

#resource that allows a driver to bid their price for an order
class Place_Get_All_Bid(Resource):
    @jwt_required()
    def get(self): #returns all bids by logged in driver
        try:
            my_bids=Bid.query.filter_by(driver_id=get_jwt_identity()).all()
            return make_response([bid.to_dict() for bid in my_bids],200)
        except Exception as e:
            print(e)
            return make_response({"message":"Server error"},500)
    @jwt_required()
    def post(self):
        data=request.get_json()
        if not all(attr in data for attr in ["order_id","price"]):
            return make_response({"message":"Required data is missing"},400)
        try:
            new_bid=Bid(
                status="Pending",
                price=data.get("price"),
                driver_id=get_jwt_identity(),
                order_id=data.get("order_id"),
                created_at=datetime.now()
            )
            db.session.add(new_bid)
            db.session.flush()
            from app import socketio
            socketio.emit("bid_placed",new_bid.to_dict(),to=data.get("order_id"))
            db.session.commit()
            return make_response(new_bid.to_dict(),201)
        except Exception as e:
            db.session.rollback()
            print(e)
            return make_response({"message":"Server error"},500)
api.add_resource(Place_Get_All_Bid,"/bids")

#resource that updates bid price details by a driver,deletes a bid
class Bid_By_Id(Resource):
    @jwt_required()
    def patch(self,id):
        data=request.get_json()
        try:
            bid=Bid.query.filter_by(id=id,driver_id=get_jwt_identity()).first()
            if not bid:
                return make_response({"message":"Bid doesnt exist"},400)
            if "price" in data:
                setattr(bid,"price",data.get("price"))
                db.session.commit()
            return make_response(bid.to_dict(),200)
        except Exception as e:
            return make_response({"message":"Server error"},500)
    
    @jwt_required()
    def delete(self,id):
        try:
            bid=Bid.query.filter_by(id=id,driver_id=get_jwt_identity()).first()
            if not bid:
                return make_response({"message":"Bid not found"},400)
            db.session.delete(bid)
            db.session.commit()
            return make_response({"message":"Deleted successfully"},204)
        except Exception:
            db.session.rollback()
            return make_response({"message":"Delete failed. Server error"},500)
api.add_resource(Bid_By_Id,'/bid/<string:id>')