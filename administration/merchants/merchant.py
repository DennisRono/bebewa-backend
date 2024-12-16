from flask import jsonify, make_response, request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models import db, Merchant
import uuid
import re

def validate_email(email):
    email_regex = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(email_regex, email)


def validate_phone_number(phone):
    return isinstance(phone, int) and len(str(phone)) in range(9, 13)

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