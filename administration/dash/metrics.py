from flask import Blueprint, jsonify, make_response, request
from flask_restful import Api, Resource
from sqlalchemy import func
from datetime import datetime, timedelta

from models import (
    db,
    Merchant,
    Admin,
    Driver,
    Driver_status_enum,
    Admin_status_enum,
    Order,
    Order_Status_Enum,
    Commodity,
    Vehicle,
)

metrics_bp = Blueprint("metrics", __name__)
api = Api(metrics_bp)


class MetricsResource(Resource):
    def get(self):
        try:
            total_admins = Admin.query.filter_by(mark_deleted=False).count()
            total_drivers = Driver.query.filter_by(mark_deleted=False).count()
            total_merchants = Merchant.query.filter_by(mark_deleted=False).count()

            active_admins = Admin.query.filter_by(
                mark_deleted=False, status=Admin_status_enum.Active
            ).count()
            suspended_admins = Admin.query.filter_by(
                mark_deleted=False, status=Admin_status_enum.Suspended
            ).count()

            active_drivers = Driver.query.filter_by(
                mark_deleted=False, status=Driver_status_enum.Active
            ).count()
            suspended_drivers = Driver.query.filter_by(
                mark_deleted=False, status=Driver_status_enum.Suspended
            ).count()

            active_merchants = Merchant.query.filter_by(
                mark_deleted=False, status=Driver_status_enum.Active
            ).count()
            suspended_merchants = Merchant.query.filter_by(
                mark_deleted=False, status=Driver_status_enum.Suspended
            ).count()

            total_orders = Order.query.filter_by(
                status=Order_Status_Enum.Delivered
            ).count()
            orders_by_status = {
                "Pending_dispatch": Order.query.filter_by(
                    status=Order_Status_Enum.Pending_dispatch
                ).count(),
                "On_transit": Order.query.filter_by(
                    status=Order_Status_Enum.On_transit
                ).count(),
                "Delivered": Order.query.filter_by(
                    status=Order_Status_Enum.Delivered
                ).count(),
                "Cancelled": Order.query.filter_by(
                    status=Order_Status_Enum.Cancelled
                ).count(),
            }

            average_order_price = db.session.query(func.avg(Order.price)).scalar()

            orders_count_subquery = (
                db.session.query(Driver.id, func.count(Order.id).label("order_count"))
                .join(Order, Driver.id == Order.driver_id)
                .group_by(Driver.id)
                .subquery()
            )

            orders_per_driver = db.session.query(
                func.avg(orders_count_subquery.c.order_count)
            ).scalar()

            most_active_merchant = (
                db.session.query(Merchant.id, func.count(Order.id))
                .join(Order)
                .group_by(Merchant.id)
                .order_by(func.count(Order.id).desc())
                .first()
            )
            most_active_merchant = (
                {
                    "merchant_id": most_active_merchant[0],
                    "order_count": most_active_merchant[1],
                }
                if most_active_merchant
                else None
            )

            total_commodities_delivered = (
                db.session.query(func.sum(Commodity.weight_kgs)).join(Order).scalar()
            )

            active_vehicles = Vehicle.query.filter_by(mark_deleted=False).count()

            revenue_by_merchant = [
                {"merchant_id": merchant_id, "revenue": revenue}
                for merchant_id, revenue in db.session.query(
                    Merchant.id, func.sum(Order.price)
                )
                .join(Order)
                .group_by(Merchant.id)
                .all()
            ]

            data = {
                "total_admins": total_admins,
                "total_drivers": total_drivers,
                "total_merchants": total_merchants,
                "active_admins": active_admins,
                "suspended_admins": suspended_admins,
                "active_drivers": active_drivers,
                "suspended_drivers": suspended_drivers,
                "active_merchants": active_merchants,
                "suspended_merchants": suspended_merchants,
                "total_orders": total_orders,
                "orders_by_status": orders_by_status,
                "average_order_price": average_order_price,
                "orders_per_driver": orders_per_driver,
                "most_active_merchant": most_active_merchant,
                "total_commodities_delivered": total_commodities_delivered,
                "active_vehicles": active_vehicles,
                "revenue_by_merchant": revenue_by_merchant,
            }

            start_date = datetime.now() - timedelta(days=30)
            user_creation_stats = {
                "admins": [
                    {"date": str(row[0]), "count": row[1]}
                    for row in db.session.query(
                        func.date(Admin.created_at), func.count(Admin.id)
                    )
                    .filter(Admin.created_at >= start_date)
                    .group_by(func.date(Admin.created_at))
                    .all()
                ],
                "drivers": [
                    {"date": str(row[0]), "count": row[1]}
                    for row in db.session.query(
                        func.date(Driver.created_at), func.count(Driver.id)
                    )
                    .filter(Driver.created_at >= start_date)
                    .group_by(func.date(Driver.created_at))
                    .all()
                ],
                "merchants": [
                    {"date": str(row[0]), "count": row[1]}
                    for row in db.session.query(
                        func.date(Merchant.created_at), func.count(Merchant.id)
                    )
                    .filter(Merchant.created_at >= start_date)
                    .group_by(func.date(Merchant.created_at))
                    .all()
                ],
            }

            order_status_distribution = {
                "Pending": orders_by_status["Pending_dispatch"],
                "On Transit": orders_by_status["On_transit"],
                "Delivered": orders_by_status["Delivered"],
                "Cancelled": orders_by_status["Cancelled"],
            }

            revenue_trends = [
                {"date": str(row[0]), "revenue": row[1]}
                for row in db.session.query(
                    func.date(Order.created_at), func.sum(Order.price)
                )
                .filter(Order.created_at >= start_date)
                .group_by(func.date(Order.created_at))
                .all()
            ]

            graph_data = {
                "user_creation_stats": user_creation_stats,
                "order_status_distribution": order_status_distribution,
                "revenue_trends": revenue_trends,
            }

            return jsonify(
                {
                    "metrics": data,
                    "graph_data": graph_data,
                }
            )

        except Exception as e:
            return make_response({"message": str(e)}, 500)


api.add_resource(MetricsResource, "/metrics", endpoint="metrics")
