"""
Routes de gestion des paiements et du suivi financier.
"""
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models.payment import Payment
from app.models.consultation import Consultation
from app.consultations.forms import QuickPaymentForm
from app.utils.decorators import permission_required
from app.utils.audit import log_action

payments_bp = Blueprint("payments", __name__, template_folder="../templates/payments")


@payments_bp.route("/")
@login_required
@permission_required("manage_payments")
def list_payments():
    page = request.args.get("page", 1, type=int)
    status_filter = request.args.get("status", "")

    query = Consultation.query.filter_by(is_deleted=False)
    if status_filter:
        query = query.filter(Consultation.payment_status == status_filter)

    pagination = query.order_by(Consultation.visit_date.desc()).paginate(
        page=page, per_page=current_app.config["PAYMENTS_PER_PAGE"], error_out=False
    )
    return render_template(
        "payments/list.html", consultations=pagination.items, pagination=pagination, status_filter=status_filter
    )


@payments_bp.route("/consultation/<int:consultation_id>/ajouter", methods=["POST"])
@login_required
@permission_required("manage_payments")
def add_payment(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id, is_deleted=False).first_or_404()
    form = QuickPaymentForm()

    if form.validate_on_submit():
        payment = Payment(
            consultation_id=consultation.id,
            amount=form.amount.data,
            method=form.method.data,
            payment_date=datetime.now(timezone.utc),
            note=form.note.data,
            received_by_id=current_user.id,
        )
        db.session.add(payment)
        consultation.amount_paid = (consultation.amount_paid or 0) + form.amount.data
        consultation.refresh_payment_status()
        log_action("ajout_paiement", entity_type="Payment", entity_id=consultation.id,
                    description=f"Paiement de {form.amount.data} DA")
        db.session.commit()
        flash("Paiement enregistré avec succès.", "success")
    else:
        flash("Données de paiement invalides.", "danger")

    return redirect(url_for("consultations.view_consultation", consultation_id=consultation.id))
