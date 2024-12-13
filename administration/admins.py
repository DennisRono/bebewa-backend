from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import Make, Models, Vehicle, db, Admin, Driver, Merchant, Admin_status_enum, Driver_status_enum
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

model_parser = reqparse.RequestParser()
model_parser.add_argument("name", type=str, required=True, help="Name is required")

make_parser = reqparse.RequestParser()
make_parser.add_argument("name", type=str, required=True, help="Name is required")
make_parser.add_argument("model_id", type=str, required=True, help="Model ID is required")

vehicle_parser = reqparse.RequestParser()
vehicle_parser.add_argument("number_plate", type=str, required=True, help="number plate is required")
vehicle_parser.add_argument("color", type=str, required=True, help="Vehicle Color is required")
vehicle_parser.add_argument("tonnage", type=int, required=True, help="tonnage is required")
vehicle_parser.add_argument("driver_id", type=str, required=True, help="driver id is required")
vehicle_parser.add_argument("make_name", type=str, required=True, help="Make ID is required")
vehicle_parser.add_argument("model_name", type=str, required=True, help="Model ID is required")

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
            admin = Admin.query.filter_by(id=admin_id, mark_deleted=False).first()
            if not admin:
                return make_response({"message": "Admin not found"}, 404)

            admin.mark_deleted = True
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


class ModelResource(Resource):
    def get(self):
        try:
            merchants = Models.query.all()
            return jsonify([merchant.to_dict() for merchant in merchants])
        except Exception as e:
            return make_response({"message": str(e)}, 500)
        
    def post(self):
        try:
            args = model_parser.parse_args()
            name = args["name"]
            order = Models(
                    id=str(uuid.uuid4()),
                    name= name,
                )
            db.session.add(order)
            db.session.commit()
            return make_response(order.to_dict(), 201)
        except IntegrityError:
            db.session.rollback()
            return make_response(
                {"message": "Invalid data. Ensure foreign keys are correct and all fields are valid."}, 400
            )
        except Exception as e:
            return make_response({"message": str(e)}, 500)
    
    def patch(self, model_id):
        try:
            model = Models.query.filter_by(
                id=model_id, mark_deleted=False
            ).first()
            if not model:
                return make_response({"message": "Model not found"}, 404)

            args = request.get_json()
            if "name" in args:
                model.name = args["name"]
            db.session.commit()
            return make_response(model.to_dict(), 200)
        except IntegrityError:
            db.session.rollback()
            return make_response(
                {"message": "Invalid data. Ensure foreign keys are correct and all fields are valid."}, 400
            )
        except IntegrityError:
            db.session.rollback()
            return make_response(
                {"message": "Invalid data. Ensure foreign keys are correct and all fields are valid."}, 400
            )
        except Exception as e:
            return make_response({"message": str(e)}, 500)
        
    def delete(self, model_id):
        try:
            models = Models.query.filter_by(
                id=model_id, mark_deleted=False
            ).first()
            if not models:
                return make_response({"message": "Model not found"}, 404)

            models.mark_deleted = True
            db.session.commit()
            return make_response({"message": "Model deleted successfully"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

class MakeResource(Resource):
    def get(self):
        try:
            makes = Make.query.all()
            return jsonify([make.to_dict() for make in makes])
        except Exception as e:
            return make_response({"message": str(e)}, 500)
        
    def post(self):
        try:
            args = make_parser.parse_args()
            name = args["name"]
            model_id = args["model_id"]
            make = Make(
                    id=str(uuid.uuid4()),
                    name= name,
                    model_id=model_id
                )
            db.session.add(make)
            db.session.commit()
            return make_response(make.to_dict(), 201)
        except IntegrityError:
            db.session.rollback()
            return make_response(
                {"message": "Invalid data. Ensure foreign keys are correct and all fields are valid."}, 400
            )
        except Exception as e:
            return make_response({"message": str(e)}, 500)
    
    def patch(self, make_id):
        try:
            make = Make.query.filter_by(
                id=make_id
            ).first()
            if not make:
                return make_response({"message": "Make not found"}, 404)

            args = request.get_json()
            if "name" in args:
                make.name = args["name"]
            if "model_id" in args:
                make.model_id = args["model_id"]
            db.session.commit()
            return make_response(make.to_dict(), 200)
        except IntegrityError:
            db.session.rollback()
            return make_response(
                {"message": "Invalid data. Ensure foreign keys are correct and all fields are valid."}, 400
            )
        except Exception as e:
            return make_response({"message": str(e)}, 500)
        
    def delete(self, make_id):
        try:
            make = Make.query.filter_by(
                id=make_id
            ).first()
            if not make:
                return make_response({"message": "Make not found"}, 404)

            make.mark_deleted = True
            db.session.commit()
            return make_response({"message": "Make deleted successfully"}, 200)
        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

class VehicleResource(Resource):
    def get(self):
        try:
            vehicles = Vehicle.query.all()
            return jsonify([vehicle.to_dict() for vehicle in vehicles])
        except Exception as e:
            return make_response({"message": str(e)}, 500)
        
    def post(self):
        try:
            args = vehicle_parser.parse_args()
            number_plate = args["number_plate"]
            make_name = args["make_name"]
            model_name = args["model_name"]
            color = args["color"]
            driver_id = args["driver_id"]
            tonnage = args["tonnage"]
            order = Vehicle(
                    number_plate=number_plate,
                    make_name=make_name,
                    model_name=model_name,
                    color=color,
                    driver_id=driver_id,
                    tonnage=tonnage
                )
            db.session.add(order)
            db.session.commit()
            return make_response(order.to_dict(), 201)
        except IntegrityError:
            db.session.rollback()
            return make_response(
                {"message": "Invalid data. Ensure foreign keys are correct and all fields are valid."}, 400
            )
        except Exception as e:
            return make_response({"message": str(e)}, 500)
    
    def patch(self, vehicle_id):
        try:
            vehicle = Vehicle.query.filter_by(id=vehicle_id, mark_deleted=False).first()
            if not vehicle:
                return make_response({"message": "Vehicle not found."}, 404)

            args = request.get_json()
            if "number_plate" in args:
                vehicle.number_plate = args["number_plate"]
            if "make_name" in args:
                vehicle.make_name = args["make_name"]
            if "model_name" in args:
                vehicle.model_name = args["model_name"]
            if "color" in args:
                vehicle.color = args["color"]
            if "driver_id" in args:
                vehicle.driver_id = args["driver_id"]
            if "tonnage" in args:
                vehicle.tonnage = args["tonnage"]

            db.session.commit()
            return make_response(vehicle.to_dict(), 200)
        
        except IntegrityError:
            db.session.rollback()
            return make_response(
                {"message": "Invalid data. Ensure foreign keys are correct and all fields are valid."}, 400
            )
        except Exception:
            return make_response({"message": "An unexpected error occurred."}, 500)
        
    def delete(self, vehicle_id):
        try:
            vehicle = Vehicle.query.filter_by(id=vehicle_id, mark_deleted=False).first()
            if not vehicle:
                return make_response({"message": "Vehicle not found."}, 404)

            vehicle.mark_deleted = True
            db.session.commit()
            return make_response({"message": "Vehicle deleted successfully."}, 200)
        
        except Exception:
            db.session.rollback()
            return make_response({"message": "An unexpected error occurred."}, 500)

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
