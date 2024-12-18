from flask import jsonify, make_response, request
from flask_restful import Resource
from models import Order, db, Admin, Driver, Merchant, Commodity, Order_Status_Enum, Recipient, Commodity_Image
from sqlalchemy.exc import DatabaseError
from flask_jwt_extended import jwt_required, get_jwt_identity
import cloudinary
import cloudinary.uploader
from datetime import datetime
import json


class Order_List(Resource):
    def get(self):
        try:
    
            orders = Order.query.all()
            
            for order in orders:
                merchant = Merchant.query.filter_by(id = order.merchant_id).first()
                if merchant:
                    order.merchant_full_name = merchant.profile.full_name
                    order.merchant_address_street = merchant.address.street
                    order.merchant_address_town = merchant.address.town
                
                commodity = Commodity.query.filter_by(id = order.commodity_id).first()
                if commodity:
                    order.commodity_name = commodity.name
                    order.commodity_dimensions = commodity.weight_kgs
                    order.commodity_image= [image.to_dict() for image in commodity.images]
                driver = Driver.query.filter_by(id = order.driver_id).first()
                if driver:
                    order.driver_full_name = driver.profile.full_name
            
            order_dict = [
                {
                    "id": order.id,
                    "status":order.status.value,
                    "price": order.price,
                    "merchant_full_name": order.merchant_full_name,  
                    "merchant_address_street": order.merchant_address_street, 
                    "merchant_address_town": order.merchant_address_town, 
                    "commodity_name": order.commodity_name,
                    "commodity_dimensions":order.commodity_dimensions,
                    "commodity_image": order.commodity_image,
                    "dispatch_time": order.dispatch_time,
                    "arrival_time": order.arrival_time,
                    "recipient": {
                        "full_name": order.recipient.full_name,
                        "email": order.recipient.email,
                        "phone_number": order.recipient.phone_number
                    },
                    "driver_name":order.driver_full_name
                }
                for order in orders
            ]

            
            response = make_response(jsonify(order_dict), 200)
            return response
        except DatabaseError as e:
            
            error_message = f"Database error: {str(e)}"
            return make_response({"message":error_message},500)
        except Exception as e:
            
            error_message= f"An uexpected error occured:{str(e)}"
            return make_response({"message": error_message},500)
    
    
    @jwt_required()
    def post(self):
        try:
            order_data = request.form.get("order_data") #get non-file data under the key order_data
            images = request.files.getlist("images") #get files data under the key images
            if not order_data:
                return make_response({"message":"Order data is required"},400)
            data=json.loads(order_data) #convert non-file data into accepatble json format
            
            #ascertain that the keys pointing to this dicts are present
            if not all(attr in data for attr in ["commodity_data","recipient_data"]):
                return make_response({"message":"Required commodity and recipient data is missing"},400)
            commodity_data=data.get("commodity_data")
            recipient_data=data.get("recipient_data")
            #validate commodity data
            if not all(attr in commodity_data for attr in ["name","weight_kgs"]):
                return make_response({"message":"Name and commodity weight required"},400)
            
            if not all(attr in recipient_data for attr in ["full_name","phone_number"]):
                return make_response({"message":"Recipient name and phone number are required"},400)
            phone_number=recipient_data.get("phone_number")
            if not str(phone_number).isdigit() or len(str(phone_number))!=9:
                return make_response({"message":"Invalid phone number format"},400)
            
            new_commodity = Commodity(
                name = commodity_data.get("name"),
                weight_kgs = commodity_data["weight_kgs"],
                length_cm = commodity_data.get("length_cm",0),
                width_cm = commodity_data.get("width_cm",0),
                height_cm = commodity_data.get("height_cm",0)
            )
            
            db.session.add(new_commodity)
            db.session.flush()
            
            image_urls = []  
            if images and len(images)> 0:
                
                for file in images:
                    if file.filename!="" and file.filename in ["jpg","png","jpeg"]:
                        result = cloudinary.uploader.upload(file)
                        image_urls.append(result.get("url"))
                
                for url in image_urls:
                    new_commodity_image = Commodity_Image(
                        image_url=url,
                        commodity_id=new_commodity.id,
                    )
                    db.session.add(new_commodity_image)
                db.session.flush()
            
            new_recipient = Recipient(
                full_name = recipient_data["full_name"],
                phone_number = recipient_data["phone_number"]
                
            )
            db.session.add(new_recipient)
            db.session.flush()
            
            admin_data = Admin.query.filter_by(id = get_jwt_identity()).first()
            if admin_data:
                merchant_data = Merchant.query.all()
                for merchant in merchant_data:
                    return merchant.to_dict(only=("profile.full_name", "profile.phone_number","id",))
            
            new_order = Order(
                status=Order_Status_Enum("Pending_dispatch").value,
                commodity_id = new_commodity.id,
                merchant_id = admin_data.merchant.id,
                recipient_id = new_recipient.id,
                created_at=datetime.now(),
                address_id=admin_data.merchant.address_id
            )
            
            db.session.add(new_order)
            db.session.commit()
            
            return make_response(new_order.to_dict(), 201)
        except DatabaseError as e:
            print(e)
            
            db.session.rollback()
            error_message = f"Database error : {str(e)}"
            return make_response({"message":error_message},500)
        except Exception as e:
            print(e)
            
            db.session.rollback()
            error_message = f"An unexpected error occured: {str(e)}"
            return make_response({"message":error_message},500)

#update the status of an order
class AdminOrderById(Resource):
    @jwt_required()
    def get(self,id): #returns an order specific to a admin
        try:
            order=Order.query.filter_by(id=id,admin_id=get_jwt_identity()).first()
            if not order:
                return make_response({"message":"Order does not exist"},400)
            return make_response(order.to_dict(),200)
        except Exception:
            return make_response({"message":"Server error"},500)
    @jwt_required()
    def patch(self,id):
        order=Order.query.filter_by(id=id,admin_id=get_jwt_identity()).first()
        if not order:
            return make_response({"message":"Order does not exist"},400)
        data=request.get_json()
        try:
            if "driver_id" in data and data.get("driver_id"):
                setattr(order,"driver_id",data.get("driver_id"))
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
            return make_response({"message":"Error updating order details"},500)
    @jwt_required()
    def delete(self,id):
        try:
            order=Order.query.filter_by(id=id,admin_id=get_jwt_identity()).first()
            if order and order.status=="Pending Dispatch":
                db.session.delete(order)
                db.session.commit()
                return make_response({"message":"Order deleted successfully"},204)
            return make_response({"message":"Delete failed"},400)
        except Exception as e:
            return make_response({"message":"Server error"},500)