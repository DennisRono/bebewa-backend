import uuid
from flask import Blueprint, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from models import db, Review

review_bp = Blueprint("review", __name__)
api = Api(review_bp)

review_parser = reqparse.RequestParser()
review_parser.add_argument(
    "rating", type=int, help="Rating must be an integer between 1 and 5"
)
review_parser.add_argument(
    "comment", type=str, help="Comment must be a non-empty string"
)


class ReviewResource(Resource):

    def get(self, order_id):
        try:
            review = Review.query.filter_by(order_id=order_id).first()
            if not review:
                return make_response({"message": "Review not found"}, 404)
            return jsonify(review.to_dict())
        except Exception as e:
            return make_response({"message": str(e)}, 500)

    def post(self, order_id):
        args = review_parser.parse_args()
        if args["rating"] is None or args["comment"] is None:
            return make_response({"message": "Rating and comment are required."}, 400)

        rating = args["rating"]
        comment = args["comment"]

        if not (1 <= rating <= 5):
            return make_response({"message": "Rating must be between 1 and 5."}, 400)

        try:
            review = Review(
                id=str(uuid.uuid4()),
                rating=rating,
                comment=comment,
                order_id=order_id,
            )

            db.session.add(review)
            db.session.commit()

            return make_response(
                {"message": "Review created successfully.", "review_id": review.id}, 201
            )

        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)


class ReviewPatchResource(Resource):
    def patch(self, review_id):
        args = review_parser.parse_args()
        try:
            review = Review.query.filter_by(id=review_id).first()
            if not review:
                return make_response({"message": "Review not found"}, 404)

            if args["rating"] is not None:
                if not (1 <= args["rating"] <= 5):
                    return make_response(
                        {"message": "Rating must be between 1 and 5."}, 400
                    )
                review.rating = args["rating"]

            if args["comment"] is not None:
                if not args["comment"]:
                    return make_response({"message": "Comment cannot be empty."}, 400)
                review.comment = args["comment"]

            db.session.commit()

            return make_response(
                {"message": "Review updated successfully.", "review_id": review.id}, 200
            )

        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)

    def delete(self, review_id):
        try:
            review = Review.query.filter_by(id=review_id).first()
            if not review:
                return make_response({"message": "Review not found"}, 404)

            db.session.delete(review)
            db.session.commit()

            return make_response({"message": "Review deleted successfully."}, 200)

        except Exception as e:
            db.session.rollback()
            return make_response({"message": str(e)}, 500)


api.add_resource(ReviewResource, "/<string:order_id>", endpoint="order_reviews")
api.add_resource(
    ReviewPatchResource, "/<string:review_id>", endpoint="order_reviews_patch"
)
