from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import Vehicle, Vehicle_Image, db
import cloudinary
import cloudinary.uploader

vehicle_parser = reqparse.RequestParser(bundle_errors=True)
vehicle_parser.add_argument("number_plate", type=str, required=True, help="number plate is required")
vehicle_parser.add_argument("color", type=str, required=True, help="Vehicle Color is required")
vehicle_parser.add_argument("tonnage", type=int, required=True, help="tonnage is required")
vehicle_parser.add_argument("driver_id", type=str, required=True, help="driver id is required")
vehicle_parser.add_argument("make_id", type=str, required=True, help="Make ID is required")
vehicle_parser.add_argument("model_id", type=str, required=True, help="Model ID is required")

class VehicleResource(Resource):
    def get(self):
        try:
            vehicles = Vehicle.query.filter_by(mark_deleted=False).all()
            return jsonify([vehicle.to_dict() for vehicle in vehicles])
        except Exception as e:
            return make_response({"message": str(e)}, 500)
        
    def post(self):
        try:
            content_type = request.content_type
            if content_type.startswith('application/json'):
                args = vehicle_parser.parse_args()
            elif content_type.startswith('multipart/form-data'):
                args = {}
                for arg in ["number_plate", "color", "tonnage", "driver_id", "make_id", "model_id"]:
                    value = request.form.get(arg)
                    if value is None:
                        return {"error": f"Missing required form field: {arg}"}, 400
                    args[arg] = value if arg != "tonnage" else int(value)
            else:
                return {"error": "Unsupported media type"}, 415

            
            if Vehicle.query.filter_by(number_plate=args["number_plate"]).first():
                return make_response(
                    {"message": f"Vehicle with number plate '{args['number_plate']}' already exists."}, 400
                )

            vehicle = Vehicle(
                number_plate=args["number_plate"],
                make_name=args["make_id"],
                model_name=args["model_id"],
                color=args["color"],
                driver_id=args["driver_id"],
                tonnage=args["tonnage"],
            )
            db.session.add(vehicle)
            db.session.flush()  

            images = request.files.getlist("files")
            allowed_extensions = {"jpg", "jpeg", "png"}
            image_urls = []

            for file in images:
                if file and file.filename.split(".")[-1].lower() in allowed_extensions:
                    result = cloudinary.uploader.upload(file)
                    image_urls.append(result.get("url"))
                else:
                    return make_response(
                        {"message": "Only jpg, jpeg, and png files are allowed"}, 400
                    )

            for url in image_urls:
                new_vehicle_image = Vehicle_Image(image_url=url, vehicle_id=vehicle.id)
                db.session.add(new_vehicle_image)

            db.session.commit()
            return make_response(vehicle.to_dict(), 201)

        except IntegrityError as e:
            db.session.rollback()
            error_message = str(e.orig).lower() if hasattr(e, "orig") else str(e).lower()
            constraint_mapping = {
                "number_plate": "The 'number_plate' provided is already in use or invalid.",
                "driver_id": "The 'driver_id' provided does not exist or is invalid.",
                "make_id": "The 'make_id' provided does not exist or is invalid.",
                "model_id": "The 'model_id' provided does not exist or is invalid.",
            }
            for field, user_message in constraint_mapping.items():
                if field in error_message:
                    return make_response({"message": user_message}, 400)
            return make_response(
                {"message": "Database integrity error. Ensure all foreign keys and constraints are valid."}, 400
            )
        except ValueError as ve:
            return make_response({"message": f"Invalid data: {str(ve)}"}, 400)
        except Exception as e:
            return make_response({"message": "Internal server error: " + str(e)}, 500)
        

    def patch(self, vehicle_id):
        try:
            vehicle = Vehicle.query.filter_by(id=vehicle_id, mark_deleted=False).first()
            if not vehicle:
                return make_response({"message": "Vehicle not found."}, 404)

            args = request.get_json()
            if "number_plate" in args:
                vehicle.number_plate = args["number_plate"]
            if "make_name" in args:
                vehicle.make_name = args["make_id"]
            if "model_name" in args:
                vehicle.model_name = args["model_id"]
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