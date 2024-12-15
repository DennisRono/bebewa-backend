from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from models import Order, db, Commodity, Commodity_Image, Recipient, Merchant, Order_Status_Enum
from sqlalchemy.exc import DatabaseError
import cloudinary
import cloudinary.uploader
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import json
from flask_socketio import emit,join_room

order_bp = Blueprint("order", __name__)
api = Api(order_bp)


cloudinary.config(
    cloud_name=Config.cloudinary_cloud_name,
    api_key=Config.cloudinary_api_key,
    api_secret=Config.cloudinary_api_secret
)
    
# Creating an Orders Resource
class Orders(Resource):
    # from app import socketio

    # a get method to get all orders specific to a merchant
    @jwt_required()
    def get(self):
        try:
            # querying the database to get all the orders
            orders = Order.query.filter_by(merchant_id=get_jwt_identity()).all()
            # Looping through the orders to get one order to a dictionary
            order_dict = [order.to_dict() for order in orders]
            #  creating and returning a response 
            response = make_response(order_dict, 200)
            return response
        except DatabaseError as e:
            #  creating and returning an error message 
            error_message = f"Database error: {str(e)}"
            return make_response({"error":error_message},500)
        except Exception as e:
            # creating and returning an unexpected error message
            error_message= f"An uexpected error occured:{str(e)}"
            return make_response({"error": error_message},500)

    #  a method to post an order
    # @socketio.on('order_posted')
    @jwt_required()
    def post(self):
        try:
            order_data = request.form.get("order_data") #get non-file data under the key order_data
            images = request.files.getlist("images") #get files data under the key images
            if not order_data:
                return make_response({"msg":"Order data is required"},400)
            data=json.loads(order_data) #convert non-file data into accepatble json format
            # data is a dict which includes keys to other dicts: commodity_data, recipient_data
            #ascertain that the keys pointing to this dicts are present
            if not all(attr in data for attr in ["commodity_data","recipient_data"]):
                return make_response({"msg":"Required commodity and recipient data is missing"},400)
            commodity_data=data.get("commodity_data")
            recipient_data=data.get("recipient_data")
            #validate commodity data
            if not all(attr in commodity_data for attr in ["name","weight_kgs"]):
                return make_response({"msg":"Name and commodity weight required"},400)
            # validate recipients data
            if not all(attr in recipient_data for attr in ["full_name","phone_number"]):
                return make_response({"msg":"Recipient name and phone number are required"},400)
            phone_number=recipient_data.get("phone_number")
            if not str(phone_number).isdigit() or len(str(phone_number))!=9:
                return make_response({"msg":"Invalid phone number format"},400)
            #  creating a commodity based on the users request
            new_commodity = Commodity(
                name = commodity_data.get("name"),
                weight_kgs = commodity_data["weight_kgs"],
                length_cm = commodity_data.get("length_cm",0),
                width_cm = commodity_data.get("width_cm",0),
                height_cm = commodity_data.get("height_cm",0)
            )
            #  adding and commiting the new_commodity to the database 
            db.session.add(new_commodity)
            db.session.flush()

            # Upload images related to the newly added commodity if the images exist
            image_urls = []  # List to store Cloudinary image URLs
            if images and len(images)> 0:
                # Upload each image to Cloudinary and store the URLs
                for file in images:
                    if file.filename!="" and file.filename in ["jpg","png","jpeg"]:
                        result = cloudinary.uploader.upload(file)
                        image_urls.append(result.get("url"))
                # Create and associate commodity images with the newly created commodity
                for url in image_urls:
                    new_commodity_image = Commodity_Image(
                        image_url=url,
                        commodity_id=new_commodity.id,
                    )
                    db.session.add(new_commodity_image)
                db.session.flush()

            # create a recipient to whom the order will be delivered
            new_recipient = Recipient(
                full_name = recipient_data["full_name"],
                phone_number = recipient_data["phone_number"]
                # email = recipient_data["email"]
            )
            db.session.add(new_recipient)
            db.session.flush()

            # getting the merchant data based on the merchant who is logged in
            merchant_data = Merchant.query.filter_by(id = get_jwt_identity()).first()
           
            # creating a new order
            new_order = Order(
                status=Order_Status_Enum("Pending_dispatch").value,
                commodity_id = new_commodity.id,
                merchant_id = merchant_data.id,
                recipient_id = new_recipient.id,
                created_at=datetime.now(),
                address_id=merchant_data.address_id
            )
            # adding and commiting the new_recepient to the database
            db.session.add(new_order)
            db.session.flush()

            #broadcast the newly created order
            from app import socketio
            join_room(new_order.id)
            socketio.emit("order_posted", new_order.to_dict(),to=new_order.id)
            # Return the response with status 201 (Created)
            db.session.commit()
            return make_response(new_order.to_dict(), 201)

        except DatabaseError as e:
            print(e)
            # creating and returning a database error message
            db.session.rollback()
            error_message = f"Database error : {str(e)}"
            return make_response({"error":error_message},500)
        except Exception as e:
            print(e)
            # creating and returning an unexpected error message 
            db.session.rollback()
            error_message = f"An unexpected error occured: {str(e)}"
            return make_response({"error":error_message},500)
api.add_resource(Orders, "/orders", endpoint="orders")

#update the status of an order
class Order_By_Id(Resource):
    @jwt_required()
    def get(self,id): #returns an order specific to a merchant
        try:
            order=Order.query.filter_by(id=id,merchant_id=get_jwt_identity()).first()
            if not order:
                return make_response({"msg":"Order does not exist"},400)
            return make_response(order.to_dict(),200)
        except Exception:
            return make_response({"msg":"Server error"},500)
    @jwt_required()
    def patch(self,id):
        order=Order.query.filter_by(id=id,merchant_id=get_jwt_identity()).first()
        if not order:
            return make_response({"msg":"Order does not exist"},400)
        data=request.get_json()
        try:
            if "driver_id" in data and data.get("driver_id"):
                setattr(order,"driver_id",data.get("driver_id"))
                from app import socketio
                socketio.emit("order_awarded", order.to_dict(),to=order.id)
            if "recipient_data" in data:
                recipient_data=data.get("recipient_data")
                recipient=Recipient.query.filter_by(id=order.recipient_id).first()
                for attr in recipient_data:
                    if recipient_data.get(attr) and recipient_data.get(attr)!="":
                        setattr(recipient,attr,recipient_data.get(attr))
            if "status" in data and Order_Status_Enum(data.get("status")).value:
                setattr(order,"status",Order_Status_Enum(data.get("status")).value)
            db.session.commit()
            return make_response(order.to_dict(),200)
        except Exception as e:
            db.session.rollback()
            return make_response({"msg":"Error updating order details"},500)

    @jwt_required()
    def delete(self,id):
        try:
            order=Order.query.filter_by(id=id,merchant_id=get_jwt_identity()).first()
            if order and order.status=="Pending Dispatch":
                db.session.delete(order)
                db.session.commit()
                return make_response({"msg":"Order deleted successfully"},204)
            return make_response({"msg":"Delete failed"},400)
        except Exception as e:
            return make_response({"msg":"Server error"},500)
api.add_resource(Order_By_Id,'/order/<string:id>')