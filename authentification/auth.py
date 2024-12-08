from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource


auth = Blueprint("auth", __name__, url_prefix="/auth")
api = Api(auth)


class Login(Resource):
    def post(self):
        pass


class Register(Resource):
    def post(self):
        pass


class Logout(Resource):
    def get(self):
        pass


api.add_resource(Login, "/login", endpoint="login")
api.add_resource(Register, "/register", endpoint="register")
api.add_resource(Logout, "/logout", endpoint="logout")
