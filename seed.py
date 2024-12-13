from datetime import date, datetime
from random import choice as rc
import random
import string
from faker import Faker
from werkzeug.security import generate_password_hash
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


fake = Faker()

def seed_admins(app, db):
    admins = []
    try:
        with app.app_context():
            from models import Admin, Admin_status_enum

            for _ in range(5):
                admin = Admin(
                    email=fake.email(),
                    password=generate_password_hash(fake.password()),
                    mark_deleted=fake.boolean(),
                    status=random.choice([status for status in Admin_status_enum]),
                )
                db.session.add(admin)
                admins.append(admin)
            db.session.commit()
        logger.info("Admin table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Admin table: {e}")
    return admins


def seed_drivers(app, db):
        with app.app_context():
            from models import Driver, Driver_status_enum, User_profile

            profiles = User_profile.query.all()

            for _ in range(10):
                try:
                    profile = rc(profiles)
                    driver = Driver(
                        phone_number=fake.random_number(digits=9),
                        password=generate_password_hash(fake.password()),
                        mark_deleted=fake.boolean(),
                        status=random.choice([status for status in Driver_status_enum]),
                        user_profile_id=profile.id,
                    )
                    db.session.add(driver)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Driver table: {e}")
        logger.info("Driver table seeded successfully.")


def seed_addresses(app, db):
    try:
        with app.app_context():
            from models import Address

            for _ in range(10):
                address = Address(
                    county=fake.state(),
                    town=fake.city(),
                    street=fake.street_address(),
                )
                db.session.add(address)
            db.session.commit()
        logger.info("Address table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Address table: {e}")


def seed_merchants(app, db):
        with app.app_context():
            from models import Merchant, Driver_status_enum, Address, User_profile

            addresses = Address.query.all()
            profiles = User_profile.query.all()

            for _ in range(10):
                try:
                    merchant = Merchant(
                        phone_number=fake.random_number(digits=9),
                        password=generate_password_hash(fake.password()),
                        mark_deleted=fake.boolean(),
                        status=rc([status for status in Driver_status_enum]),
                        user_profile_id=rc(profiles).id,
                        address_id=rc(addresses).id,
                    )
                    db.session.add(merchant)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Merchant table: {e}")
        logger.info("Merchant table seeded successfully.")



def seed_recipients(app, db):
    try:
        with app.app_context():
            from models import Recipient

            for _ in range(10):
                recipient = Recipient(
                    full_name=fake.name(),
                    phone_number=fake.random_number(digits=9),
                    email=fake.email(),
                )
                db.session.add(recipient)
            db.session.commit()
        logger.info("Recipient table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Recipient table: {e}")


def seed_user_profile(app, db):
    try:
        with app.app_context():
            from models import User_profile

            for _ in range(10):
                profile = User_profile(
                    full_name=fake.name(),
                    phone_number=fake.random_number(digits=9),
                    email=fake.email(),
                    kra_pin="".join(
                        random.choices(string.ascii_uppercase + string.digits, k=10)
                    ),
                    national_id=fake.random_number(digits=8),
                    mark_deleted=fake.boolean(),
                )
                db.session.add(profile)
            db.session.commit()
        logger.info("User Profile table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding User Profile table: {e}")


def seed_commodities(app, db):
    commodities = []
    try:
        with app.app_context():
            from models import Commodity

            for _ in range(10):
                commodity = Commodity(
                    name=fake.word(),
                    weight_kgs=fake.random_number(digits=2),
                    length_cm=fake.random_number(digits=2),
                    width_cm=fake.random_number(digits=2),
                    height_cm=fake.random_number(digits=2),
                )
                db.session.add(commodity)
                commodities.append(commodity)
            db.session.commit()
        logger.info("Commodity table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Commodity table: {e}")
    return commodities

def seed_commodity_images(app, db):
        with app.app_context():
            from models import Commodity,Commodity_Image
            commodities = Commodity.query.all()

            for _ in range(10):
                try:
                    commodity = Commodity_Image(
                        image_url=fake.image_url(),
                        commodity_id=rc(commodities).id
                    )
                    db.session.add(commodity)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Commodity Images table: {e}")
        logger.info("Commodity Images table seeded successfully.")


def seed_orders(app, db):
        with app.app_context():
            from models import (
                Order,
                Order_Status_Enum,
                Merchant,
                Recipient,
                Commodity,
                Address,
            )

            merchants = Merchant.query.all()
            recipients = Recipient.query.all()
            commodities = Commodity.query.all()
            addresses = Address.query.all()

            for _ in range(10):
                try:
                    order = Order(
                        status=rc([status for status in Order_Status_Enum]),
                        commodity_id=rc(commodities).id,
                        dispatch_time=fake.date_this_year(),
                        arrival_time=fake.date_this_year(),
                        created_at=fake.date_this_year(),
                        price=fake.random_int(min=10, max=1000),
                        merchant_id=rc(merchants).id,
                        address_id=rc(addresses).id,
                        recipient_id=rc(recipients).id,
                    )
                    db.session.add(order)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Order table: {e}")
        logger.info("Order table seeded successfully.")


def seed_reviews(app, db):
        with app.app_context():
            from models import Review, Order

            orders = Order.query.all()

            for _ in range(10):
                try:
                    review = Review(
                        rating=fake.random_int(min=0, max=5),
                        comment=fake.text(max_nb_chars=20),
                        order_id=rc(orders).id,
                    )
                    db.session.add(review)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Review table: {e}")
        logger.info("Review table seeded successfully.")

def seed_subscription_payment(app, db):
        with app.app_context():
            from models import Subscription_Payment, Subscription_status_enum, Driver, Transactions

            drivers = Driver.query.all()
            transactions = Transactions.query.all()

            for _ in range(10):
                try:
                    subscription_payment = Subscription_Payment(
                        price=fake.random_int(min=0, max=2000),
                        recurring_payment_date = fake.date_between_dates(date_start=datetime.now(), date_end=datetime(datetime.now().year + 1, 12, 31)),
                        status=random.choice([status for status in Subscription_status_enum]),
                        driver_id=rc(drivers).id,
                        transaction_id=rc(transactions).id
                    )
                    db.session.add(subscription_payment)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Subscription Payment table: {e}")
        logger.info("Subscription Payment table seeded successfully.")

def seed_transactions(app, db):
    try:
        with app.app_context():
            from models import Transactions

            for _ in range(10):
                transaction = Transactions(
                    amount=fake.random_int(min=0, max=2000),
                    phone_number=fake.random_number(digits=9),
                    transaction_code="".join(
                        random.choices(string.ascii_uppercase + string.digits, k=10)
                    ),
                    status=random.choice(['Completed', 'Pending', 'Cancelled']),
                )
                db.session.add(transaction)
            db.session.commit()
        logger.info("Transactions table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Transactions table: {e}")

def seed_bids(app, db):
        with app.app_context():
            from models import Bid, Driver, Order

            drivers = Driver.query.all()
            orders = Order.query.all()
            for _ in range(10):
                try:
                    bid = Bid(
                        status=random.choice(['Successful', 'Rejected']),
                        price=fake.random_int(min=0, max=2000),
                        driver_id=rc(drivers).id,
                        order_id=rc(orders).id
                    )
                    db.session.add(bid)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Bid table: {e}")
        logger.info("Bid table seeded successfully.")

def seed_models(app, db):
    try:
        with app.app_context():
            from models import Models

            for _ in range(10):
                order = Models(
                    name= fake.name(),
                )
                db.session.add(order)
            db.session.commit()
        logger.info("Models table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Models table: {e}")

def seed_makes(app, db):
        with app.app_context():
            from models import Make, Models
            models = Models.query.all()

            for _ in range(10):
                try:
                    order = Make(
                        name= fake.name(),
                        model_id=rc(models).id
                    )
                    db.session.add(order)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Make table: {e}")
        logger.info("Make table seeded successfully.")

def seed_vehicles(app, db):
        with app.app_context():
            from models import Make, Models, Vehicle, Driver
            models = Models.query.all()
            makes = Make.query.all()
            drivers = Driver.query.all()

            for _ in range(10):
                try:
                    order = Vehicle(
                        number_plate=fake.license_plate(),
                        make_name=rc(makes).id,
                        model_name=rc(models).id,
                        color=fake.color_name(),
                        driver_id=rc(drivers).id,
                        tonnage=random.uniform(1.0, 10.0),
                        mark_deleted=fake.boolean()
                    )
                    db.session.add(order)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Vehicles table: {e}")
        logger.info("Vehicles table seeded successfully.")

def seed_vehicle_images(app, db):
        with app.app_context():
            from models import Vehicle, Vehicle_Image
            vehicles = Vehicle.query.all()

            for _ in range(10):
                try:
                    order = Vehicle_Image(
                        image_url=fake.image_url(),
                        vehicle_id=rc(vehicles).id
                    )
                    db.session.add(order)
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Error while seeding Vehicles Images table: {e}")
        logger.info("Vehicles Images table seeded successfully.")

def seed_data():
    try:
        from app import app

        with app.app_context():
            from models import db
            db.drop_all()
            db.create_all()
            seed_admins(app, db)
            seed_user_profile(app, db)
            seed_drivers(app, db)
            seed_addresses(app, db)
            seed_merchants(app, db)
            seed_recipients(app, db)
            seed_commodities(app, db)
            seed_commodity_images(app, db)
            seed_orders(app, db)
            seed_reviews(app, db)
            seed_transactions(app, db)
            seed_subscription_payment(app, db)
            seed_bids(app, db)
            seed_models(app, db)
            seed_makes(app, db)
            seed_vehicles(app, db)
            seed_vehicle_images(app, db)
            logger.info("Seeding complete.")
    except Exception as e:
        logger.error(f"Error during seeding process: {e}")


if __name__ == "__main__":
    seed_data()
