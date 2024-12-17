from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from flask_restful import Api, Resource
from config import Config
from models import db, Driver_status_enum
from flask_migrate import Migrate
from authentification.auth import auth
from administration.admins import admin_bp
from administration.dash.metrics import metrics_bp
from drivers.driver import driver_bp
from merchants.merchant import merchant_bp
from orders.order import order_bp
from reviews.review import review_bp
from merchants.commodity import commodity_bp
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

app = Flask(__name__)
CORS(app)
JWTManager(app=app)
app.config.from_object(Config)
socketio=SocketIO(app=app,cors_allowed_origins="*")



app.register_blueprint(auth)
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(metrics_bp, url_prefix="/admin/dash")
app.register_blueprint(driver_bp, url_prefix='/driver')
app.register_blueprint(merchant_bp)
app.register_blueprint(order_bp)
app.register_blueprint(review_bp, url_prefix="/reviews")
app.register_blueprint(commodity_bp)

api = Api(app)
migrate = Migrate(app=app, db=db)
db.init_app(app=app)
JWTManager(app=app)


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
# print(Driver_status_enum("Active").value)

if __name__ == "__main__":
    socketio.run(port=5555, debug=True)
