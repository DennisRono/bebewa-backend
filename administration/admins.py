from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import db, Admin, Driver, Merchant, Admin_status_enum, Driver_status_enum
import uuid
from werkzeug.security import generate_password_hash

admin_bp = Blueprint("admin", __name__)
api = Api(admin_bp)


def validate_email(email):
    import re

    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email)


def validate_phone_number(phone):
    return isinstance(phone, int) and len(str(phone)) in range(9, 13)


admin_parser = reqparse.RequestParser()
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

driver_parser = reqparse.RequestParser()
driver_parser.add_argument(
    "phone_number", type=int, required=True, help="Phone number is required"
)
driver_parser.add_argument(
    "password", type=str, required=True, help="Password is required"
)
driver_parser.add_argument(
    "status",
    type=str,
    choices=[e.value for e in Driver_status_enum],
    required=True,
    help="Status is required",
)


class AdminResource(Resource):
    def get(self):
        try:
            admins = Admin.query.filter_by(mark_as_deleted=False).all()
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
            mark_as_deleted=False,
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
            admin = Admin.query.filter_by(id=admin_id, mark_as_deleted=False).first()
            if not admin:
                return make_response({"message": "Admin not found"}, 404)
            return jsonify(admin.to_dict())
        except Exception as e:
            return make_response({"message": str(e)}, 500)

    def patch(self, admin_id):
        try:
            admin = Admin.query.filter_by(id=admin_id, mark_as_deleted=False).first()
            if not admin:
                return make_response({"message": "Admin not found"}, 404)

            args = admin_parser.parse_args()
            if args["email"] and validate_email(args["email"]):
                admin.email = args["email"]
            if args["password"]:
                admin.password = args["password"]
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
            admin = Admin.query.filter_by(id=admin_id, mark_as_deleted=False).first()
            if not admin:
                return make_response({"message": "Admin not found"}, 404)

            admin.mark_as_deleted = True
            db.session.commit()
            return make_response({"message": "Admin deleted successfully"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)


class DriverResource(Resource):
    def get(self):
        try:
            drivers = Driver.query.filter_by(mark_deleted=False).all()
            return jsonify([driver.to_dict() for driver in drivers])
        except Exception as e:
            return make_response({"message": str(e)}, 500)

    def post(self):
        args = driver_parser.parse_args()
        phone_number = args["phone_number"]
        password = args["password"]
        status = args["status"]

        if not validate_phone_number(phone_number):
            return make_response({"message": "Invalid phone number"}, 400)

        new_driver = Driver(
            id=str(uuid.uuid4()),
            phone_number=phone_number,
            password=generate_password_hash(password),
            mark_deleted=False,
            status=Driver_status_enum(status),
        )

        try:
            db.session.add(new_driver)
            db.session.commit()
            return make_response(new_driver.to_dict(), 201)
        except IntegrityError:
            db.session.rollback()
            return make_response({"message": "Phone number already exists"}, 409)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

    def patch(self, driver_id):
        try:
            driver = Driver.query.filter_by(id=driver_id, mark_deleted=False).first()
            if not driver:
                return make_response({"message": "Driver not found"}, 404)

            args = driver_parser.parse_args()
            if args["phone_number"] and validate_phone_number(args["phone_number"]):
                driver.phone_number = args["phone_number"]
            if args["password"]:
                driver.password = args["password"]
            if args["status"]:
                driver.status = Driver_status_enum(args["status"])

            db.session.commit()
            return make_response(driver.to_dict(), 200)
        except IntegrityError:
            db.session.rollback()
            return make_response({"message": "Phone number already exists"}, 409)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

    def delete(self, driver_id):
        try:
            driver = Driver.query.filter_by(id=driver_id, mark_deleted=False).first()
            if not driver:
                return make_response({"message": "Driver not found"}, 404)

            driver.mark_deleted = True
            db.session.commit()
            return make_response({"message": "Driver deleted successfully"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)


class MerchantResource(Resource):
    def get(self):
        try:
            merchants = Merchant.query.filter_by(mark_deleted=False).all()
            return jsonify([merchant.to_dict() for merchant in merchants])
        except Exception as e:
            return make_response({"message": str(e)}, 500)

    def post(self):
        args = request.get_json()
        name = args.get("name")
        email = args.get("email")
        password = args.get("password")

        if not validate_email(email):
            return make_response({"message": "Invalid email format"}, 400)

        new_merchant = Merchant(
            id=str(uuid.uuid4()),
            name=name,
            email=email,
            password=password,
            mark_deleted=False,
        )

        try:
            db.session.add(new_merchant)
            db.session.commit()
            return make_response(new_merchant.to_dict(), 201)
        except IntegrityError:
            db.session.rollback()
            return make_response({"message": "Email already exists"}, 409)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

    def patch(self, merchant_id):
        try:
            merchant = Merchant.query.filter_by(
                id=merchant_id, mark_deleted=False
            ).first()
            if not merchant:
                return make_response({"message": "Merchant not found"}, 404)

            args = request.get_json()
            if "name" in args:
                merchant.name = args["name"]
            if "email" in args and validate_email(args["email"]):
                merchant.email = args["email"]
            if "password" in args:
                merchant.password = args["password"]

            db.session.commit()
            return make_response(merchant.to_dict(), 200)
        except IntegrityError:
            db.session.rollback()
            return make_response({"message": "Email already exists"}, 409)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

    def delete(self, merchant_id):
        try:
            merchant = Merchant.query.filter_by(
                id=merchant_id, mark_deleted=False
            ).first()
            if not merchant:
                return make_response({"message": "Merchant not found"}, 404)

            merchant.mark_deleted = True
            db.session.commit()
            return make_response({"message": "Merchant deleted successfully"}, 200)
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
