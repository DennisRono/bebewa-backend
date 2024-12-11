from random import choice as rc
import random
import string
from faker import Faker
from werkzeug.security import generate_password_hash
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Faker
fake = Faker()


def empty_tables(app, db):
    try:
        with app.app_context():
            from models import (
                Admin,
                Driver,
                Merchant,
                Recipient,
                Order,
                Address,
                Models,
                Make,
                Vehicle,
                Vehicle_Image,
                Commodity,
                Commodity_Image,
            )

            db.session.query(Admin).delete()
            db.session.query(Driver).delete()
            db.session.query(Merchant).delete()
            db.session.query(Recipient).delete()
            db.session.query(Order).delete()
            db.session.query(Address).delete()
            db.session.query(Models).delete()
            db.session.query(Make).delete()
            db.session.query(Vehicle).delete()
            db.session.query(Vehicle_Image).delete()
            db.session.query(Commodity).delete()
            db.session.query(Commodity_Image).delete()
            db.session.commit()
        logger.info("Tables emptied successfully.")
    except Exception as e:
        logger.error(f"Error while emptying tables: {e}")


def seed_admins(app, db):
    admins = []
    try:
        with app.app_context():
            from models import Admin, Admin_status_enum

            for _ in range(5):
                admin = Admin(
                    email=fake.email(),
                    password=generate_password_hash(fake.password()),
                    mark_as_deleted=fake.boolean(),
                    status=random.choice([status for status in Admin_status_enum]),
                )
                db.session.add(admin)
                admins.append(admin)
            db.session.commit()
        logger.info("Admin table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Admin table: {e}")
    return admins


def seed_drivers(app, db, profiles):
    drivers = []
    try:
        with app.app_context():
            from models import Driver, Driver_status_enum

            for _ in range(10):
                profile = rc(profiles)
                driver = Driver(
                    phone_number=fake.random_number(digits=9),
                    password=generate_password_hash(fake.password()),
                    mark_deleted=fake.boolean(),
                    status=random.choice([status for status in Driver_status_enum]),
                    user_profile_id=profile.id,
                )
                db.session.add(driver)
                drivers.append(driver)
            db.session.commit()
        logger.info("Driver table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Driver table: {e}")
    return drivers


def seed_addresses(app, db):
    addresses = []
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
                addresses.append(address)
            db.session.commit()
        logger.info("Address table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Address table: {e}")
    return addresses


def seed_merchants(app, db, addresses):
    merchants = []
    try:
        with app.app_context():
            from models import Merchant, Driver_status_enum

            for _ in range(10):
                address = rc(addresses)
                merchant = Merchant(
                    phone_number=fake.random_number(digits=9),
                    password=generate_password_hash(fake.password()),
                    mark_deleted=fake.boolean(),
                    status=rc([status for status in Driver_status_enum]),
                    address_id=address.id,
                )
                db.session.add(merchant)
                merchants.append(merchant)
            db.session.commit()
        logger.info("Merchant table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Merchant table: {e}")
    return merchants


def seed_recipients(app, db):
    recipients = []
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
                recipients.append(recipient)
            db.session.commit()
        logger.info("Recipient table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Recipient table: {e}")
    return recipients


def seed_user_profile(app, db):
    profiles = []
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
                profiles.append(profile)
            db.session.commit()
        logger.info("User Profile table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding User Profile table: {e}")
    return profiles


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


def seed_orders(app, db, merchants, recipients, commodities, addresses):
    try:
        with app.app_context():
            from models import Order, Order_Status_Enum

            for _ in range(10):
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
        logger.info("Order table seeded successfully.")
    except Exception as e:
        logger.error(f"Error while seeding Order table: {e}")


def seed_data():
    try:
        from app import app
        from models import db

        empty_tables(app, db)
        seed_admins(app, db)
        profiles = seed_user_profile(app, db)
        seed_drivers(app, db, profiles)
        addresses = seed_addresses(app, db)
        merchants = seed_merchants(app, db, addresses)
        recipients = seed_recipients(app, db)
        commodities = seed_commodities(app, db)
        seed_orders(app, db, merchants, recipients, commodities, addresses)
        logger.info("Seeding complete.")
    except Exception as e:
        logger.error(f"Error during seeding process: {e}")


if __name__ == "__main__":
    seed_data()
