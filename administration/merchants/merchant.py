from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import Address, User_profile, db, Merchant, Driver_status_enum
import uuid
import re
from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash

def validate_email(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email)


def validate_phone_number(phone):
    return isinstance(phone, int) and len(str(phone)) in range(9, 13)

merchant_parser = reqparse.RequestParser(bundle_errors=True)
merchant_parser.add_argument("full_name", type=str, required=True, help="Full Name is required")
merchant_parser.add_argument("email", type=str, required=True, help="Email is required")
merchant_parser.add_argument("kra_pin", type=str, required=False, help="KRA PIN is required")
merchant_parser.add_argument("national_id", type=int, required=True, help="ID number is required")
merchant_parser.add_argument("phone_number", type=int, required=True, help="Phone number is required")
merchant_parser.add_argument("password", type=str, required=True, help="Password is required")
merchant_parser.add_argument("county", type=str, required=True, help="County is required")
merchant_parser.add_argument("town", type=str, required=True, help="Town is required")
merchant_parser.add_argument("street", type=str, required=True, help="Street is required")
merchant_parser.add_argument("status", type=str, choices=[e.value for e in Driver_status_enum], required=True,  help="Status is required")

class MerchantResource(Resource):
    def get(self):
        try:
            merchants = Merchant.query.filter_by(mark_deleted=False).all()
            return jsonify([merchant.to_dict() for merchant in merchants])
        except Exception as e:
            return make_response({"message": str(e)}, 500)

    def post(self):
        args = request.get_json()
        full_name = args.get("full_name")
        email = args.get("email")
        password = args.get("password")
        kra_pin = args.get("kra_pin")
        national_id = args.get("national_id")
        phone_number = args.get("phone_number")
        county = args.get("county")
        town = args.get("town")
        street = args.get("street")
        status = args.get("status")

        if not validate_email(email):
            return make_response({"message": "Invalid email format"}, 400)
        
        new_profile = User_profile(
            id=str(uuid.uuid4()),
            full_name=full_name,
            phone_number=phone_number,
            email=email,
            kra_pin=kra_pin,
            national_id=national_id,
        )
        new_address = Address(
            id=str(uuid.uuid4()),
            county=county,
            town=town,
            street=street
        )
        new_merchant = Merchant(
            id=str(uuid.uuid4()),
            phone_number=phone_number,
            status=status,
            password=generate_password_hash(password),
            user_profile_id=new_profile.id,
            address_id=new_address.id
        )

        try:
            db.session.add(new_profile)
            db.session.add(new_address)
            db.session.add(new_merchant)
            db.session.commit()
            return make_response(jsonify({"message": "Merchant created successfully!", "user": new_merchant.to_dict()}), 201)
        except BadRequest as e:
            return jsonify({
                "message": str(e),
                "status": "fail"
            }), 400
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
            profile = User_profile.query.filter_by(
                id=merchant.user_profile_id, mark_deleted=False
            ).first()
            address = Address.query.filter_by(
                id=merchant.address_id
            ).first()

            args = request.get_json()
            if "status" in args:
                merchant.status = args["status"]
            if "phone_number" in args:
                merchant.phone_number = args["phone_number"]
            if "password" in args:
                merchant.password = generate_password_hash(args["password"])
            if "county" in args:
                address.county = args["county"]
            if "town" in args:
                address.town = args["town"]
            if "street" in args:
                address.street = args["street"]
            if "full_name" in args:
                profile.full_name = args["full_name"]
            if "phone_number" in args:
                profile.phone_number = args["phone_number"]
            if "email" in args:
                profile.email = args["email"]
            if "kra_pin" in args:
                profile.kra_pin = args["kra_pin"]
            if "national_id" in args:
                profile.national_id = args["national_id"]

            db.session.commit()
            return make_response(jsonify({"message": "Merchant updated successfully!", "user": merchant.to_dict()}), 200)
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