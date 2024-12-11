from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy_serializer import SerializerMixin
import uuid
from enum import Enum


metadata = MetaData()
db = SQLAlchemy(metadata=metadata)


class User_profile(db.Model, SerializerMixin):
    __tablename__ = "user_profiles"

    id = db.Column(
        db.String,
        unique=True,
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    full_name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    email = db.Column(db.String, unique=True)
    kra_pin = db.Column(db.String, unique=True)
    national_id = db.Column(db.Integer, unique=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime)
    mark_deleted = db.Column(db.Boolean, nullable=False)

    # relationships
    # admin = db.relationship("Admin", back_populates="profile")
    driver = db.relationship("Driver", back_populates="profile")
    merchant = db.relationship("Merchant", back_populates="profile")
    # serialise rules
    # serialize_rules = ("-admin.profile", "-driver.profile", "-merchant.profile")
    serialize_rules = ("-driver.profile", "-merchant.profile")


class Admin_status_enum(Enum):
    Active = "Active"
    Suspended = "Suspended"


class Admin(db.Model, SerializerMixin):
    __tablename__ = "admins"

    id = db.Column(
        db.String,
        unique=True,
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    mark_as_deleted = db.Column(db.Boolean, nullable=False)
    # user_profile_id = db.Column(db.String, db.ForeignKey("user_profiles.id"))
    status = db.Column(db.Enum(Admin_status_enum), nullable=False)
    # relationships
    # profile = db.relationship("User_profile", back_populates="admin")

    # serialise rules
    # serialize_rules = ("-profile", "-password")
    serialize_rules = ("-password",)


class Driver_status_enum(Enum):
    Active = "Active"
    Suspended = "Suspended"


class Driver(db.Model, SerializerMixin):
    __tablename__ = "drivers"

    id = db.Column(
        db.String,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
        primary_key=True,
    )
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    mark_deleted = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.Enum(Driver_status_enum), nullable=False, default="Active")
    user_profile_id = db.Column(db.String, db.ForeignKey("user_profiles.id"))
    # relationships
    profile = db.relationship("User_profile", back_populates="driver")
    deliveries = db.relationship("Order", back_populates="driver")
    # serialise rules
    serialize_rules = ("-profile.driver", "-password", "-deliveries.driver")


class Address(db.Model, SerializerMixin):
    __tablename__ = "addresses"

    id = db.Column(
        db.String, default=lambda: str(uuid.uuid4()), unique=True, primary_key=True
    )
    county = db.Column(db.String, nullable=False)
    town = db.Column(db.String, nullable=False)
    street = db.Column(db.String, nullable=False)


class Merchant(db.Model, SerializerMixin):
    __tablename__ = "merchants"

    id = db.Column(
        db.String, default=lambda: str(uuid.uuid4()), unique=True, primary_key=True
    )
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    mark_deleted = db.Column(db.Boolean, nullable=False)
    status = db.Column(db.Enum(Driver_status_enum), nullable=False)
    user_profile_id = db.Column(db.String, db.ForeignKey("user_profiles.id"))
    address_id = db.Column(db.String, db.ForeignKey("addresses.id"))
    # relationships
    profile = db.relationship("User_profile", back_populates="merchant")
    orders = db.relationship("Order", back_populates="merchant")
    # serialise rules
    serialize_rules = ("-profile.merchant", "-password", "-orders.merchant")


class Recipient(db.Model, SerializerMixin):
    __tablename__ = "recipients"

    id = db.Column(
        db.String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True
    )
    full_name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False, unique=True)
    email = db.Column(db.String, unique=True)
    # relationships
    deliveries = db.relationship("Order", back_populates="recipient")
    # serialise rules
    serialize_rules = ("-deliveries.recipient",)


class Models(db.Model, SerializerMixin):
    __tablename__ = "models"

    id = db.Column(
        db.String, unique=True, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String, unique=True, nullable=False)


class Make(db.Model, SerializerMixin):
    __tablename__ = "makes"

    id = db.Column(
        db.String, unique=True, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String, nullable=False)
    model_id = db.Column(db.String, db.ForeignKey("models.id"))


class Vehicle(db.Model, SerializerMixin):
    __tablename__ = "vehicles"

    id = db.Column(
        db.String,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        unique=True,
        nullable=False,
    )
    number_plate = db.Column(db.String, nullable=False, unique=True)
    make_name = db.Column(db.String, db.ForeignKey("makes.id"), nullable=False)
    model_name = db.Column(db.String, db.ForeignKey("models.id"))
    color = db.Column(db.String, nullable=False)
    driver_id = db.Column(db.String, db.ForeignKey("drivers.id"))
    tonnage = db.Column(db.Integer, nullable=False)
    mark_deleted = db.Column(db.Boolean, nullable=False)

    # relationships
    images = db.relationship("Vehicle_Image", back_populates="vehicle")
    # serialise rules
    serialize_rules = ("-images.vehicle",)


class Vehicle_Image(db.Model, SerializerMixin):
    __tablename__ = "vehicle_images"

    id = db.Column(
        db.String, primary_key=True, unique=True, default=lambda: str(uuid.uuid4())
    )
    image_url = db.Column(db.String, nullable=False)
    vehicle_id = db.Column(db.String, db.ForeignKey("vehicles.id"), nullable=False)

    # relationships
    vehicle = db.relationship("Vehicle", back_populates="images")
    # serialise rules
    serialize_rules = ("-vehicle",)


class Commodity(db.Model, SerializerMixin):
    __tablename__ = "commodities"

    id = db.Column(
        db.String,
        primary_key=True,
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    name = db.Column(db.String, nullable=False)
    weight_kgs = db.Column(db.Float, nullable=False)
    length_cm = db.Column(db.Float)
    width_cm = db.Column(db.Float)
    height_cm = db.Column(db.Float)
    # relationships
    images = db.relationship("Commodity_Image", back_populates="commodity")
    # serialise rules
    serialize_rules = ("-images.commodity",)


class Commodity_Image(db.Model, SerializerMixin):
    __tablename__ = "commodity_images"

    id = db.Column(
        db.String,
        primary_key=True,
        unique=True,
        nullable=False,
        default=lambda: str(uuid.uuid4()),
    )
    image_url = db.Column(db.String, nullable=False)
    commodity_id = db.Column(db.String, db.ForeignKey("commodities.id"))
    # relationships
    commodity = db.relationship("Commodity", back_populates="images")
    # serialise rules
    serialize_rules = ("-commodity",)


class Order_Status_Enum(Enum):
    Pending_dispatch = "Pending_dispatch"
    On_transit = "On_transit"
    Delivered = "Delivered"
    Cancelled = "Cancelled"


class Order(db.Model, SerializerMixin):
    __tablename__ = "orders"

    id = db.Column(
        db.String,
        primary_key=True,
        nullable=False,
        unique=True,
        default=lambda: str(uuid.uuid4()),
    )
    status = db.Column(db.Enum(Order_Status_Enum), nullable=False)
    commodity_id = db.Column(db.String, db.ForeignKey("commodities.id"))
    dispatch_time = db.Column(db.DateTime)
    arrival_time = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False)
    price = db.Column(db.Integer, nullable=False, default=0)
    merchant_id = db.Column(db.String, db.ForeignKey("merchants.id"))
    address_id = db.Column(db.String, db.ForeignKey("addresses.id"), nullable=False)
    recipient_id = db.Column(db.String, db.ForeignKey("recipients.id"), nullable=False)
    driver_id = db.Column(db.String, db.ForeignKey("drivers.id"))

    # relationships
    merchant = db.relationship("Merchant", back_populates="orders")
    driver = db.relationship("Driver", back_populates="deliveries")
    recipient = db.relationship("Recipient", back_populates="deliveries")

    # serialise rules
    serialize_rules = (
        "-merchant.orders",
        "-driver.deliveries",
        "-recipient.deliveries",
    )


class Review(db.Model, SerializerMixin):
    __tablename__ = "reviews"

    id = db.Column(
        db.String,
        unique=True,
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False)
    edited_at = db.Column(db.DateTime)


# Subscriptions Table for Drivers
