from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_restful import Api, Resource
from config import Config


app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

api = Api(app)


@app.before_request
def handle_options_request():
    if request.method == "OPTIONS":
        response = make_response("", 200)
        response.headers["Allow"] = ("GET, POST, PUT, DELETE, OPTIONS", "PATCH")
        return response


class Wake(Resource):
    def get(self):
        return make_response(jsonify({"message": "server is awake"}), 200)


api.add_resource(Wake, "/wake", endpoint="wake")

if __name__ == "__main__":
    app.run(port=5555, debug=True)
