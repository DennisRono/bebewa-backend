from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from flask_jwt_extended import jwt_required,get_jwt_identity,create_access_token,create_refresh_token
from werkzeug.security import check_password_hash
from models import Driver, Merchant

auth = Blueprint("auth", __name__, url_prefix="/auth")
api = Api(auth)

#Resource that checks the validity of an access token
class Is_Token_Valid(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id=get_jwt_identity()
            if user_id:
                return make_response({"msg":True},200)
            return make_response({"msg":False},422)
        except Exception as e:
            print(e)
            return make_response({"msg":"Internal server error"},500)
api.add_resource(Is_Token_Valid,"/access-token", endpoint="access-token")

#Resource that generates a new access token if a refresh token is valid
class New_Access_Token(Resource):
    @jwt_required(refresh=True)
    def get(self):
        try:
            user_id=get_jwt_identity()
            if not user_id:
                return make_response({"msg":"Invalid request"},400)
            access_token=create_access_token(id=user_id)
            return make_response({"access_token":access_token},200)
        except Exception as e:
            print(e)
            return make_response({"msg":"Internal server error"},500)
api.add_resource(New_Access_Token,'/new-token',endpoint="new-token")

# Driver login resource
class Driver_Login(Resource):
    def post(self):
        data=request.get_json()
        if not all(attr in data for attr in ["phone_number", "password"]):
            return make_response({"msg":"Required data is missing"},400)
        phone_number=data.get("phone_number")
        password=data.get("password")
        try:
            driver=Driver.query.filter_by(phone_number=phone_number).first()
            if not driver:
                return make_response({"msg":f"{phone_number} not registered"},400)
            if not check_password_hash(driver.password, password):
                return make_response({"msg":"Wrong password"},400)
            return make_response({
                "access_token":create_access_token(identity=driver.id),
                "refresh_token":create_refresh_token(identity=driver.id),
            },201)
        except Exception as e:
            return make_response({"msg":"Internal server error"},500)
api.add_resource(Driver_Login,"/driver-login", endpoint="driver-login")

#merchant login resource
class Merchant_Login(Resource):
    def post(self):
        data=request.get_json()
        if not all(attr in data for attr in ["phone_number", "password"]):
            return make_response({"msg":"Required data is missing"},400)
        phone_number=data.get("phone_number")
        password=data.get("password")
        try:
            merchant=Merchant.query.filter_by(phone_number=phone_number).first()
            if not merchant:
                return make_response({"msg":f"{phone_number} not registered"},400)
            if not check_password_hash(merchant.password, password):
                return make_response({"msg":"Wrong password"},400)
            return make_response({
                "access_token":create_access_token(identity=merchant.id),
                "refresh_token":create_refresh_token(identity=merchant.id),
            },201)
        except Exception as e:
            return make_response({"msg":"Internal server error"},500)
api.add_resource(Merchant_Login,"/merchant-login", endpoint="merchant-login")

#admin login
class Admin_Login(Resource):
    def post(self):
        data=request.get_json()
        if not all(attr in data for attr in ["email", "password"]):
            return make_response({"msg":"Required data is missing"},400)
        email=data.get("email")
        password=data.get("password")
        try:
            admin=admin.query.filter_by(email=email).first()
            if not admin:
                return make_response({"msg":f"{email} not registered"},400)
            if not check_password_hash(admin.password, password):
                return make_response({"msg":"Wrong password"},400)
            return make_response({
                "access_token":create_access_token(identity=admin.id),
                "refresh_token":create_refresh_token(identity=admin.id),
            },201)
        except Exception as e:
            return make_response({"msg":"Internal server error"},500)
api.add_resource(Admin_Login,"/admin-login", endpoint="admin-login")

