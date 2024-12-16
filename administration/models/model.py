from flask import  jsonify, make_response, request
from flask_restful import  Resource, reqparse
from sqlalchemy.exc import IntegrityError
from models import  Models, db   
import uuid

model_parser = reqparse.RequestParser(bundle_errors=True)
model_parser.add_argument("name", type=str, required=True, help="Name is required")

make_and_model_parser = reqparse.RequestParser(bundle_errors=True)
make_and_model_parser.add_argument("make_name", type=str, required=True, help="Make Name is required")
make_and_model_parser.add_argument("model_name", type=str, required=True, help="Model Name is required")


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
        

class MakeAndModel(Resource):
    def post(self):
        try:
            args = make_and_model_parser.parse_args()
            make_name = args["make_name"]
            model_name = args["model_name"]
            model = Models(
                    id=str(uuid.uuid4()),
                    name= model_name,
                )

            make = Make(
                    id=str(uuid.uuid4()),
                    name= make_name,
                    model_id=model.id
                )
            db.session.add(model)
            db.session.add(make)
            db.session.commit()
            return make_response({
                "message": "Make and Model created successfully.",
                "make": make.to_dict(),
                "model": model.to_dict()
            }, 201)
        except IntegrityError:
            db.session.rollback()
            return make_response(
                {"message": "Invalid data. Ensure foreign keys are correct and all fields are valid."}, 400
            )
        except Exception as e:
            return make_response({"message": str(e)}, 500)