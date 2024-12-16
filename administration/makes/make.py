from flask import jsonify, make_response, request
from flask_restful import Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import Make, db
import uuid

make_parser = reqparse.RequestParser(bundle_errors=True)
make_parser.add_argument("name", type=str, required=True, help="Name is required")
make_parser.add_argument("model_id", type=str, required=True, help="Model ID is required")


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
