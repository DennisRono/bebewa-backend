from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from models import Merchant,db, User_profile, Address, Driver_status_enum
from sqlalchemy.exc import DatabaseError
from werkzeug.security import generate_password_hash
from flask_jwt_extended import jwt_required, get_jwt_identity

merchant_bp = Blueprint("merchant", __name__)
api = Api(merchant_bp)

# creating a home resource 
class Home(Resource):
    # a get method that returns a message
    def get(self):
        # creating and returning a response based on the response body
        response_body = {"message": "welcome to bebewa app"}
        response = make_response(response_body, 200)
        return response


#  Creating a Merchants Resource
class Merchants(Resource):
    # a method to get all merchants
    def get(self):
        try:
            # querying the merchants database to get all merchants
            merchants = Merchant.query.all()
            # Looping through all merchants to get one merchant and converting the merchant to a dictionary
            merchant_dict = [merchant.to_dict(only = ("profile.full_name",
            "profile.id", 
            "profile.email", 
            "profile.phone_number",
            "profile.kra_pin",
            "profile.national_id",
            "address","phone_number",
            "status", 
            "orders.id",
            "orders.status",
            "orders.commodity_id",
            "orders.dispatch_time",
            "orders.arrival_time",
            "orders.price",
            "orders.merchant_id",
            "orders.address_id",
            "orders.recipient",
            "orders.driver_id")
            ) for merchant in merchants]
            # creating and returning a response 
            response = make_response(merchant_dict,200)
            return response
        except DatabaseError as e:
            #  creating and returning an error message 
            error_message = f"Database error: {str(e)}"
            return make_response({"error":error_message},500)
        except Exception as e:
            # creating and returning an unexpected error message
            error_message= f"An uexpected error occured:{str(e)}"
            return make_response({"error": error_message},500)
        
    #  validating the phone_number to be exactly 10 digits
    def is_valid_phone_number(self, phone_number):
        return phone_number.isdigit() and len(phone_number) == 9
    
    
    # validating the id_number to be exactly 8 digits
    def is_valid_national_id(self, national_id):
        return national_id.isdigit() and len(national_id) == 8
    
    # validating the id_number to be exactly 8 digits
    def is_valid_email(self, email):
        return "@" in email
    
    #  a method to post a merchant
    def post(self):
        try:
            # creating a user based on users request
            data = request.get_json()
            # getting the phone number and returning a response if the phone number is invalid
            phone_number = data.get("phone_number")

            if not phone_number or not self.is_valid_phone_number(phone_number):
                print(self.is_valid_phone_number(phone_number))
                # creating and returning a response 
                response_body = {"message": "Phone number must be exactly 9 digits."}
                response = make_response(response_body,400)
                return response
            
            # getting the national id and returning a response is the national_id is invalid
            national_id = data.get("national_id")

            if national_id and not self.is_valid_national_id(national_id):
                # creating and returning a response
                response_body = {"message":"National Id must be exactly 8 digits"}
                response = make_response(response_body, 400)
                return response
            
            # getting the kra pin and email based on the users request
            kra_pin = data.get("kra_pin")
            email = data.get("email")
            if email and not self.is_valid_email(email):
                # creating and returning a response
                response_body = {"message":"Email must contain @"}
                response = make_response(response_body, 400)
                return response
            
            # checking if the email, phone_number,kra_pin and the national_id
            if User_profile.query.filter_by(phone_number=phone_number).first():
                # creating and returning a response
                response_body = {"message":"The phone number already exists"}
                response = make_response(response_body, 400)
                return response
            
            if national_id and User_profile.query.filter_by(national_id=national_id).first():
                # creating and returning a response
                response_body = {"message":"The national id already exists"}
                response = make_response(response_body, 400)
                return response
            
            if kra_pin and User_profile.query.filter_by(kra_pin=kra_pin).first():
                # creating and returning a response
                response_body = {"message":"The kra pin already exists"}
                response = make_response(response_body, 400)
                return response
            
            if email and User_profile.query.filter_by(email=email).first():
                # creating and returning a response
                response_body = {"message":"The email already exists"}
                response = make_response(response_body, 400)
                return response

            new_user = User_profile(
                full_name = data["full_name"],
                phone_number = phone_number,
                email = email,
                kra_pin = kra_pin,
                national_id = national_id,
                mark_deleted = False
            )

            # adding and commiting the user to the database
            db.session.add(new_user)
            db.session.commit()

            # Get the address data and create a new address
            address_data = data.get("address")
            if not address_data:
                return make_response({"message": "Address is required."}, 400)

            new_address = Address(
                county=address_data["county"],
                town=address_data["town"],
                street=address_data["street"]
            )

            # Add and commit the new address to the database
            db.session.add(new_address)
            db.session.commit()

            # Create the merchant and associate it with the user and address
            # creating a password based on the users input
            password = generate_password_hash(data["password"])
            new_merchant = Merchant(
                # id = new_user.id,
                phone_number=phone_number,
                password=password, 
                mark_deleted=False,
                status=Driver_status_enum("Active").value, 
                user_profile_id=new_user.id,
                address_id=new_address.id
            )

            # Add and commit the new merchant to the database
            db.session.add(new_merchant)
            db.session.commit()

            # Convert the new user and merchant to a dictionary
            new_user_dict = new_user.to_dict()
            new_user_dict["address"] = new_address.to_dict()
            new_user_dict["merchant"] = new_merchant.to_dict()

            # Return the response
            response = make_response(new_user_dict, 201)
            return response
        except DatabaseError as e:
            # creating and returning a database error message
            db.session.rollback()
            error_message = f"Database error: {str(e)}"
            return make_response({"error":error_message},500)
        except Exception as e:
            db.session.rollback()
            # creating and returning an unexpected error message
            error_message = f"An unexpected error occured:{str(e)}"
            return make_response({"error": error_message}, 500)
        
#  creating a MerchantsById Resource
class MerchantsById(Resource):
    # a method to get a single merchant
    @jwt_required()
    def get(self):
        try:
            # querying and filtering the database using the id
            merchant = Merchant.query.filter_by(id = get_jwt_identity()).first()

            if merchant:
                # making the merchant to a dictionary
                merchant_dict = merchant.to_dict(only = ("profile.full_name",
            "profile.id", 
            "profile.email", 
            "profile.phone_number",
            "profile.kra_pin",
            "profile.national_id",
            "address","phone_number",
            "status", 
            "orders.id",
            "orders.status",
            "orders.commodity_id",
            "orders.dispatch_time",
            "orders.arrival_time",
            "orders.price",
            "orders.merchant_id",
            "orders.address_id",
            "orders.recipient",
            "orders.driver_id"))
                # creating and returning a response based on the merchants dict
                response = make_response(merchant_dict, 200)
                return response
            else:
                # creating and returning a response based on the response body
                response_body = {"message":f"Merchant with the id of {id} is not found"}
                response = make_response(response_body, 400)
                return response
        except DatabaseError as e:
            # creating and returning a Database error message
            error_message = f"Database error: {str(e)}"
            return make_response({"error": error_message},500)
        except Exception as e:
            # creating and returning an unexpected error message
            error_message = f"An Unexpected error occured: {str(e)}"
            return make_response({"error":error_message},500)
    
    #  a method to patch a merchant
    @jwt_required()
    def patch(self):
        try:
            # querying and filtering the database using the id
            merchant = Merchant.query.filter_by(id = get_jwt_identity()).first()
            if merchant:
                #  getting the data out of the users request
                data = request.get_json()
                # setting attributes based on the data gathered
                
                if "password" in data:
                    setattr(merchant, "password",generate_password_hash(data["password"]) )

                # updating the address based on the users request
                if "address" in data:
                    address_data = data["address"]
                    # using the relationship to set attributes
                    address = Merchant.query.filter_by(id = merchant.address_id).first()
                    if address:
                        for attr in address_data:
                            if address_data[attr] != "":
                                setattr(address, attr, address_data[attr])

                
                # commiting the changes to the database
                db.session.commit()

                # creating the merchant to a dictionary format
                merchant_dict = merchant.to_dict()
                # creating and returning a response based on the merchants dict
                response = make_response(merchant_dict, 200)
                return response
            else:
                # creating and returning a response based on the response body
                response_body = {"message":f"The merchant with the id of {id} is not found"}
                response = make_response(response_body, 400)
                return response
        except DatabaseError as e:
            # creating and returning a Database error message
            db.session.rollback()
            error_message = f"Database error: {str(e)}"
            return make_response({"error": error_message}, 500)
        except Exception as e:
            # creating and returning an uexpected error message
            db.session.rollback()
            error_message = f"An Unexpected error occured: {str(e)}"
            return make_response({"error": error_message}, 500)
        
    #  a method to delete the merchant from the database
    def delete(self, id):
        try:
            # querying and filtering the database using the id
            merchant = Merchant.query.filter_by(id = id).first()

            if merchant:
                # deleting the merchant from the database and commiting the changes
                db.session.delete(merchant)
                db.session.commit()

                # creating and returning a response based on the response body
                response_body = {"message":f"The merchant with the id of {id} has been deleted successfully"}
                response = make_response(response_body, 204)
                return response
            else:
                # creating and returning a response based on the response body
                response_body = {"message":f"The Merchant with the id of {id} is not found"}
                response = make_response(response_body, 400)
                return response
        except DatabaseError as e:
            # creating and returning a Database error message
            db.session.rollback()
            error_message = f"Database error: {str(e)}"
            return make_response({"error": error_message}, 500)
        except Exception as e:
            # creating and returning an unexpected error message
            db.session.rollback()
            error_message = f"An unexpected error occured: {str(e)}"
            return make_response({"error": error_message}, 500)
    pass



api.add_resource(Home, "/", endpoint="home")
api.add_resource(Merchants, "/merchants", endpoint="merchants")
api.add_resource(MerchantsById, "/merchant", endpoint="merchants_by_id")