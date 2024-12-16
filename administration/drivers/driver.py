from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import User_profile, db, Driver, Driver_status_enum
import uuid
import re
from werkzeug.security import generate_password_hash
from werkzeug.exceptions import BadRequest

def validate_email(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email)


def validate_phone_number(phone):
    return isinstance(phone, int) and len(str(phone)) in range(9, 13)

driver_parser = reqparse.RequestParser(bundle_errors=True)
driver_parser.add_argument("full_name", type=str, required=True, help="Full Name is required")
driver_parser.add_argument("email", type=str, required=True, help="Email is required")
driver_parser.add_argument("kra_pin", type=str, required=True, help="KRA PIN is required")
driver_parser.add_argument("national_id", type=int, required=True, help="ID number is required")
driver_parser.add_argument("phone_number", type=int, required=True, help="Phone number is required")
driver_parser.add_argument("password", type=str, required=True, help="Password is required")
driver_parser.add_argument("status", type=str, choices=[e.value for e in Driver_status_enum], required=True,  help="Status is required")


class DriverResource(Resource):
    def get(self):
        try:
            drivers = Driver.query.filter_by(mark_deleted=False).all()            
            return jsonify([driver.to_dict() for driver in drivers])
        except Exception as e:
            print(e)
            return make_response({"message": str(e)}, 500)

    def post(self):
        try:
            args = driver_parser.parse_args()
            full_name = args["full_name"]
            email = args["email"]
            kra_pin = args["kra_pin"]
            national_id = args["national_id"]
            phone_number = args["phone_number"]
            password = args["password"]
            status = args["status"]

            if not validate_phone_number(phone_number):
                return make_response({"message": "Invalid phone number"}, 400)
            
            new_profile = User_profile(
                id=str(uuid.uuid4()),
                full_name=full_name,
                phone_number=phone_number,
                email=email,
                kra_pin=kra_pin,
                national_id=national_id,
                mark_deleted=False,
            )

            new_driver = Driver(
                id=str(uuid.uuid4()),
                phone_number=phone_number,
                password=generate_password_hash(password),
                mark_deleted=False,
                status=Driver_status_enum(status),
                user_profile_id=new_profile.id
            )

            db.session.add(new_profile)
            db.session.add(new_driver)
            db.session.commit()
            return make_response(new_driver.to_dict(), 201)
        except BadRequest as e:
            return jsonify({
                "message": str(e),
                "status": "fail"
            }), 400
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
            
            profile = User_profile.query.filter_by(id=driver.user_profile_id, mark_deleted=False).first()
            if not profile:
                return make_response({"message": "Failed to update Profile as Profile was not found"}, 404)

            args = driver_parser.parse_args()
            if args["phone_number"] and validate_phone_number(args["phone_number"]):
                driver.phone_number = args["phone_number"]
                profile.phone_number = args["phone_number"]
            if args["password"]:
                driver.password = args["password"]
            if args["status"]:
                driver.status = Driver_status_enum(args["status"])
            if args["full_name"]:
                profile.full_name = args["full_name"]
            if args["email"]:
                profile.email = args["email"]
            if args["kra_pin"]:
                profile.kra_pin = args["kra_pin"]
            if args["national_id"]:
                profile.national_id = args["national_id"]

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

