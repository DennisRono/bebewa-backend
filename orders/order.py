from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from models import Order, db, Commodity, Commodity_Image, Recipient, Merchant, Order_Status_Enum
from sqlalchemy.exc import DatabaseError
import cloudinary
import cloudinary.uploader
from config import Config
from flask_jwt_extended import jwt_required, get_jwt_identity

order_bp = Blueprint("order", __name__)
api = Api(order_bp)

cloudinary.config(
    cloud_name=Config.cloudinary_cloud_name,
    api_key=Config.cloudinary_api_key,
    api_secret=Config.cloudinary_api_secret
)

# Creating an Orders Resource
class Orders(Resource):
    # a get method to get all orders
    def get(self):
        try:
            # querying the database to get all the orders
            orders = Order.query.all()
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
    @jwt_required()
    def post(self):
        try:
            data = request.get_json()

            # Ensuring that the required fields are not missing 
            if not data.get("name") or data.get("weight_kgs"):
                # creating and returning a response based on the response_body
                response_body = {"message":"The name or the wight in kgs is Required"}
                return make_response(response_body, 400)

            #  creating a commodity based on the users request
            new_commodity = Commodity(
                name = data["name"],
                weight_kgs = data["weight_kgs"],
                length_cm = data["length_cm"],
                width_cm = data["width_cm"],
                height_cm = data["height_cm"]
            )

            #  adding and commiting the new_commodity to the database 
            db.session.add(new_commodity)
            db.session.commit()

            # Handling image uploads
            images = request.files.getlist("images")

            # List to store Cloudinary image URLs
            image_urls = []

            if images and len(images)> 0:
                # Upload each image to Cloudinary and store the URLs
                for file in images:
                    if file.filename!="" and file.filename in ["jpg","png","jpeg"]:
                        result = cloudinary.uploader.upload(file)
                        image_urls.append(result.get("url"))
                    else:
                        return make_response({"message": "Only jpg, jpeg, and png files are allowed"}, 400)

                # Create and associate commodity images with the newly created commodity
                for url in image_urls:
                    new_commodity_image = Commodity_Image(
                        image_url=url,
                        commodity_id=new_commodity.id,
                    )
                    db.session.add(new_commodity_image)
            db.session.commit()

            # getting the merchant id based on the merchant who is logged in
            merchant_data = Merchant.query.filter_by(id = get_jwt_identity()).first()
            if not merchant_data:
                return make_response({"message":"merchant data is required"})
            
            # getting the recepient details
            recipient_data = data.get("recipient")
            if not recipient_data:
                return make_response({"message":"recipient data is required"},400)
            
            # Ensuring that the required fields are not missing 
            if not data.get("full_name") or data.get("phone_number"):
                # creating and returning a response based on the response_body
                response_body = {"message":"The full name or the phone number is Required"}
                return make_response(response_body, 400)
            
            new_recipient = Recipient(
                full_name = data["full_name"],
                phone_number = data["phone_number"],
                email = data["email"]
            )

            # adding and commiting the new_recepient to the database
            db.session.add(new_recipient)
            db.session.commit()

            # creating a new order
            new_order = Order(
                status=Order_Status_Enum("Pending_dispatch").value,
                commodity_id = new_commodity.id,
                merchant_id = merchant_data.id,
                recipient_id = new_recipient.id
            )
            # adding and commiting the new_recepient to the database
            db.session.add(new_order)
            db.session.commit()

            # Convert the new entities to dictionaries
            new_commodity_dict = new_commodity.to_dict()
            new_recipient_dict = new_recipient.to_dict()
            new_order_dict = new_order.to_dict()


            # Create the response body with the newly created objects
            response_body = {
                "order": new_order_dict,
                "commodity": new_commodity_dict,
                "recipient": new_recipient_dict,
                "message": "Order created successfully"
            }

            # Return the response with status 201 (Created)
            return make_response(response_body, 201)

        except DatabaseError as e:
            # creating and returning a database error message
            db.session.rollback()
            error_message = f"Database error : {str(e)}"
            return make_response({"error":error_message},500)
        except Exception as e:
            # creating and returning an unexpected error message 
            db.session.rollback()
            error_message = f"An unexpected error occured: {str(e)}"
            return make_response({"error":error_message},500)

        pass


api.add_resource(Orders, "/orders", endpoint="orders")
