from flask import Blueprint, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from sqlalchemy.exc import IntegrityError
from administration.drivers.driver import DriverResource
from administration.makes.make import MakeResource
from administration.merchants.merchant import MerchantResource
from administration.models.model import MakeAndModel, ModelResource
from administration.orders.orders import AdminOrderById, Order_List
from administration.vehicles.vehicle import VehicleResource
from models import db, Admin, Admin_status_enum
import uuid
from werkzeug.security import generate_password_hash
import re


admin_bp = Blueprint("admin", __name__)
api = Api(admin_bp)

def validate_email(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email)


def validate_phone_number(phone):
    return isinstance(phone, int) and len(str(phone)) in range(9, 13)


admin_parser = reqparse.RequestParser(bundle_errors=True)
admin_parser.add_argument("email", type=str, required=True, help="Email is required")
admin_parser.add_argument(
    "password", type=str, required=True, help="Password is required"
)
admin_parser.add_argument(
    "status",
    type=str,
    required=True,
    help="Status is required",
    choices=[status.value for status in Admin_status_enum],
)


class AdminResource(Resource):
    def get(self):
        try:
            admins = Admin.query.filter_by(mark_deleted=False).all()
            return jsonify([admin.to_dict() for admin in admins])
        except Exception as e:
            return make_response({"message": str(e)}, 500)

    def post(self):
        args = admin_parser.parse_args()
        email = args["email"]
        password = args["password"]
        status = args["status"]

        if not validate_email(email):
            return make_response({"message": "Invalid email format"}, 400)

        new_admin = Admin(
            id=str(uuid.uuid4()),
            email=email,
            password=generate_password_hash(password),
            mark_deleted=False,
            status=Admin_status_enum(status),
        )
        try:
            db.session.add(new_admin)
            db.session.commit()
            return make_response(new_admin.to_dict(), 201)
        except IntegrityError:
            db.session.rollback()
            return make_response({"message": "Email already exists"}, 409)
        except Exception as e:
            print(e)
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

class AdminDetailResource(Resource):
    def get(self, admin_id):
        try:
            admin = Admin.query.filter_by(id=admin_id, mark_deleted=False).first()
            if not admin:
                return make_response({"message": "Admin not found"}, 404)
            return jsonify(admin.to_dict())
        except Exception as e:
            return make_response({"message": str(e)}, 500)

    def patch(self, admin_id):
        try:
            admin = Admin.query.filter_by(id=admin_id, mark_deleted=False).first()
            if not admin:
                return make_response({"message": "Admin not found"}, 404)

            args = admin_parser.parse_args()
            if args["email"] and validate_email(args["email"]):
                admin.email = args["email"]
            if args["password"]:
                admin.password = generate_password_hash(args["password"])
            if args["status"]:
                admin.status = Admin_status_enum(args["status"])

            db.session.commit()
            return make_response(admin.to_dict(), 200)
        except IntegrityError:
            db.session.rollback()
            return make_response({"message": "Email already exists"}, 409)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

    def delete(self, admin_id):
        try:
            admin = Admin.query.filter_by(id=admin_id, mark_deleted=False).first()
            if not admin:
                return make_response({"message": "Admin not found"}, 404)

            admin.mark_deleted = True
            db.session.commit()
            return make_response({"message": "Admin deleted successfully"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)


api.add_resource(AdminResource, "/", endpoint="admins")
api.add_resource(AdminDetailResource, "/<string:admin_id>", endpoint="admin_detail")
api.add_resource(DriverResource, "/driver", endpoint="drivers")
api.add_resource(DriverResource, "/driver/<string:driver_id>", endpoint="driver_detail")
api.add_resource(MerchantResource, "/merchant", endpoint="merchants")
api.add_resource(
    MerchantResource,
    "/merchant/<string:merchant_id>",
    endpoint="merchant_detail",
)
api.add_resource(ModelResource, "/models", endpoint="models")
api.add_resource(ModelResource, "/models/<string:model_id>", endpoint="models_detail")
api.add_resource(MakeResource, "/make", endpoint="make")
api.add_resource(MakeResource, "/make/<string:make_id>", endpoint="make_detail")
api.add_resource(VehicleResource, "/vehicle", endpoint="vehicle")
api.add_resource(VehicleResource, "/vehicle/<string:vehicle_id>", endpoint="vehicle_detail")
api.add_resource(MakeAndModel, "/make-and-model", endpoint="make_and_model")
api.add_resource(Order_List,"/order-list", endpoint="order-list")
api.add_resource(AdminOrderById,'/admin-order/<string:id>', endpoint ="/admin-order/<string:id>")