import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("POSTGRES_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 1800
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=59)
    JWT_ACCESS_REFRESH_EXPIRES = timedelta(days=30)
    SECRET_KEY = os.getenv("SECRET_KEY", "46ergsgwet5w5fewfweffhdgh")

    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
    MPESA_BUSINESS_SHORTCODE = os.getenv("MPESA_BUSINESS_SHORTCODE")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")

    #cloudinary configurations
    cloudinary_cloud_name=os.getenv("cloudinary_cloud_name")
    cloudinary_api_key=os.getenv("cloudinary_api_key")
    cloudinary_api_secret=os.getenv("cloudinary_api_secret")