from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData, DateTime, func
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
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    mark_deleted = db.Column(db.Boolean, nullable=False, default=False)

    # relationships
    driver = db.relationship("Driver", back_populates="profile")
    merchant = db.relationship("Merchant", back_populates="profile")
    # serialize rules
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
    mark_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    status = db.Column(db.Enum(Admin_status_enum), nullable=False)

    # serialize rules
    serialize_rules = ("-password",)


class Driver_status_enum(Enum):
    Active = "Active"
    Inactive = "Inactive"
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
    current_balance = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    mark_deleted = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.Enum(Driver_status_enum), nullable=False, default="Active")
    user_profile_id = db.Column(db.String, db.ForeignKey("user_profiles.id"))
    # relationships
    profile = db.relationship("User_profile", back_populates="driver")
    deliveries = db.relationship("Order", back_populates="driver")
    subscription = db.relationship("Subscription_Payment", back_populates="driver")
    bid = db.relationship("Bid", back_populates="driver")
    # serialize rules
    serialize_rules = ("-profile.driver", "-password", "-deliveries.driver", "-subscription.driver", '-bid.driver',)


class Address(db.Model, SerializerMixin):
    __tablename__ = "addresses"

    id = db.Column(
        db.String, default=lambda: str(uuid.uuid4()), unique=True, primary_key=True
    )
    county = db.Column(db.String, nullable=False)
    town = db.Column(db.String, nullable=False)
    street = db.Column(db.String, nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    #  a one to one relationship between the merchant and the address
    merchant = db.relationship("Merchant", back_populates="address")

    # serialization rules
    serialize_rules = ("-merchant.address", )


class Merchant(db.Model, SerializerMixin):
    __tablename__ = "merchants"

    id = db.Column(
        db.String, default=lambda: str(uuid.uuid4()), unique=True, primary_key=True
    )
    phone_number = db.Column(db.Integer, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    mark_deleted = db.Column(db.Boolean, nullable=False, default=False)
    status = db.Column(db.Enum(Driver_status_enum), nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    user_profile_id = db.Column(db.String, db.ForeignKey("user_profiles.id"))
    address_id = db.Column(db.String, db.ForeignKey("addresses.id"))
    # relationships
    profile = db.relationship("User_profile", back_populates="merchant")
    orders = db.relationship("Order", back_populates="merchant")
    #  a one to one relationship between the merchant and the address
    address = db.relationship("Address",uselist = False, back_populates="merchant")
    # serialize rules
    serialize_rules = ("-profile.merchant", "-password", "-orders.merchant", "-address.merchant", )


class Recipient(db.Model, SerializerMixin):
    __tablename__ = "recipients"

    id = db.Column(
        db.String, primary_key=True, default=lambda: str(uuid.uuid4()), unique=True
    )
    full_name = db.Column(db.String, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False, unique=True)
    email = db.Column(db.String, unique=True)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    # relationships
    deliveries = db.relationship("Order", back_populates="recipient")
    # serialize rules
    serialize_rules = ("-deliveries.recipient",)


class Models(db.Model, SerializerMixin):
    __tablename__ = "models"

    id = db.Column(
        db.String, unique=True, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String, unique=True, nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )


class Make(db.Model, SerializerMixin):
    __tablename__ = "makes"

    id = db.Column(
        db.String, unique=True, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
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
    mark_deleted = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # relationships
    images = db.relationship("Vehicle_Image", back_populates="vehicle")
    # serialize rules
    serialize_rules = ("-images.vehicle",)


class Vehicle_Image(db.Model, SerializerMixin):
    __tablename__ = "vehicle_images"

    id = db.Column(
        db.String, primary_key=True, unique=True, default=lambda: str(uuid.uuid4())
    )
    image_url = db.Column(db.String, nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    vehicle_id = db.Column(db.String, db.ForeignKey("vehicles.id"), nullable=False)

    # relationships
    vehicle = db.relationship("Vehicle", back_populates="images")
    # serialize rules
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
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    # relationships
    images = db.relationship("Commodity_Image", back_populates="commodity")
    # serialize rules
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
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    # relationships
    commodity = db.relationship("Commodity", back_populates="images")
    # serialize rules
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
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    # relationships
    merchant = db.relationship("Merchant", back_populates="orders")
    driver = db.relationship("Driver", back_populates="deliveries")
    recipient = db.relationship("Recipient", back_populates="deliveries")
    review = db.relationship("Review", back_populates="order")
    bid = db.relationship("Bid", back_populates="order")

    # serialize rules
    serialize_rules = (
        "-merchant.orders",
        "-merchant.profile.driver",
        "-driver.profile.merchant",
        "-driver.deliveries",
        "-driver.bid.driver",
        "-driver.bid.order",
        "-recipient.deliveries",
        "-review",
        "-bid.order",
        "-bid.driver",
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
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )

    order_id = db.Column(db.String, db.ForeignKey("orders.id"), nullable=False)

    # relationships
    order = db.relationship("Order", back_populates="review")

    serialize_rules = ("-order.review",)

class Subscription_status_enum(Enum):
    Paid = "Paid"
    Unpaid = "Unpaid"
    Cancelled = "Cancelled"


# Subscriptions Table for Drivers
class Subscription_Payment(db.Model, SerializerMixin):
    __tablename__ = "subscription_payment"

    id = db.Column(
        db.String,
        unique=True,
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    price = db.Column(db.Integer, nullable=False, default=0)
    recurring_payment_date = db.Column(DateTime, nullable=False, default=func.now())
    status = db.Column(db.Enum(Subscription_status_enum), nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    driver_id = db.Column(db.String, db.ForeignKey("drivers.id"), nullable=False)
    transaction_id = db.Column(db.String, db.ForeignKey("transactions.id"), nullable=False)

    driver = db.relationship("Driver", back_populates="subscription")
    transaction = db.relationship("Transactions", back_populates="subscription")

    serialize_rules = ('-driver.subscription', '-transaction.subscription',)

class Transactions(db.Model, SerializerMixin):
    __tablename__ = "transactions"

    id = db.Column(
        db.String,
        unique=True,
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    amount = db.Column(db.Integer, nullable=False)
    phone_number = db.Column(db.Integer, nullable=False)
    transaction_code = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    subscription = db.relationship("Subscription_Payment", back_populates="transaction")

    serialize_rules = ('-subscription.transaction',)

# Bidding Table
class Bid(db.Model, SerializerMixin):
    __tablename__ = "bids"

    id = db.Column(
        db.String,
        unique=True,
        nullable=False,
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    status = db.Column(db.String, nullable=False)
    created_at = db.Column(DateTime, nullable=False, default=func.now())
    updated_at = db.Column(
        DateTime, nullable=False, default=func.now(), onupdate=func.now()
    )
    price = db.Column(db.Integer, nullable=False)

    driver_id = db.Column(db.String, db.ForeignKey("drivers.id"), nullable=False)
    order_id = db.Column(db.String, db.ForeignKey("orders.id"), nullable=False)

    driver = db.relationship("Driver", back_populates="bid")
    order = db.relationship("Order", back_populates="bid")

    serialize_rules = ('-driver.bid', '-order.bid',)
