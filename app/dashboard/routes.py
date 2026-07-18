"""
Route du tableau de bord principal : indicateurs clés de l'activité de la clinique.
"""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func

from app.extensions import db, cache
from app.models.consultation import Consultation, PaymentStatus
from app.models.patient import Patient
from app.models.payment import Payment
from app.models.inventory import Product
from app.models.notification import Notification
from app.utils.decorators import permission_required

dashboard_bp = Blueprint("dashboard", __name__, template_folder="../templates/dashboard")


@dashboard_bp.route("/")
@login_required
@permission_required("view_dashboard")
def index():
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    revenue_today = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.payment_date >= today_start)
        .scalar()
    )
    revenue_month = (
        db.session.query(func.coalesce(func.sum(Payment.amount), 0))
        .filter(Payment.payment_date >= month_start)
        .scalar()
    )

    patients_count = Patient.query.filter_by(is_deleted=False).count()
    appointments_today = Consultation.query.filter(
        Consultation.visit_date >= today_start, Consultation.is_deleted.is_(False)
    ).count()

    recent_patients = (
        Patient.query.filter_by(is_deleted=False)
        .order_by(Patient.created_at.desc())
        .limit(5)
        .all()
    )

    low_stock_products = (
        Product.query.filter(
            Product.is_deleted.is_(False),
            Product.quantity_in_stock <= Product.minimum_stock_threshold,
        )
        .order_by(Product.quantity_in_stock.asc())
        .limit(8)
        .all()
    )

    unpaid_consultations = Consultation.query.filter(
        Consultation.payment_status != PaymentStatus.PAID,
        Consultation.is_deleted.is_(False),
    ).count()

    # ---- Revenus des 7 derniers jours pour le graphique ----
    daily_revenue = []
    for i in range(6, -1, -1):
        day = (now - timedelta(days=i)).replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day + timedelta(days=1)
        total = (
            db.session.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.payment_date >= day, Payment.payment_date < day_end)
            .scalar()
        )
        daily_revenue.append({"label": day.strftime("%d/%m"), "total": float(total)})

    notifications = (
        Notification.query.filter_by(user_id=current_user.id, is_read=False)
        .order_by(Notification.created_at.desc())
        .limit(10)
        .all()
    )

    return render_template(
        "dashboard/index.html",
        revenue_today=revenue_today,
        revenue_month=revenue_month,
        patients_count=patients_count,
        appointments_today=appointments_today,
        recent_patients=recent_patients,
        low_stock_products=low_stock_products,
        unpaid_consultations=unpaid_consultations,
        daily_revenue=daily_revenue,
        notifications=notifications,
    )
