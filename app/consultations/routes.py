"""
Routes de gestion des consultations (visites médicales).
"""
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.patient import Patient
from app.models.consultation import Consultation, ConsultationStatus, PaymentStatus
from app.models.payment import Payment
from app.consultations.forms import ConsultationForm, QuickPaymentForm
from app.utils.decorators import permission_required
from app.utils.audit import log_action

consultations_bp = Blueprint("consultations", __name__, template_folder="../templates/consultations")


@consultations_bp.route("/patient/<int:patient_id>/nouvelle", methods=["GET", "POST"])
@login_required
@permission_required("manage_consultations")
def create_consultation(patient_id):
    patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first_or_404()
    form = ConsultationForm()
    if request.method == "GET":
        form.visit_date.data = datetime.now()
        form.status.data = ConsultationStatus.COMPLETED.value

    if form.validate_on_submit():
        consultation = Consultation(
            patient_id=patient.id,
            doctor_id=current_user.id,
            visit_date=form.visit_date.data,
            reason=form.reason.data,
            diagnosis=form.diagnosis.data,
            treatment=form.treatment.data,
            notes=form.notes.data,
            status=form.status.data,
            consultation_price=form.consultation_price.data,
        )
        db.session.add(consultation)
        db.session.flush()
        log_action("creation_consultation", entity_type="Consultation", entity_id=consultation.id,
                    description=f"Nouvelle consultation pour {patient.full_name}")
        db.session.commit()
        flash("Consultation enregistrée avec succès.", "success")
        return redirect(url_for("patients.view_patient", patient_id=patient.id))

    return render_template("consultations/form.html", form=form, patient=patient, is_edit=False)


@consultations_bp.route("/<int:consultation_id>")
@login_required
@permission_required("manage_consultations")
def view_consultation(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id, is_deleted=False).first_or_404()
    payment_form = QuickPaymentForm()
    return render_template("consultations/detail.html", consultation=consultation, payment_form=payment_form)


@consultations_bp.route("/<int:consultation_id>/modifier", methods=["GET", "POST"])
@login_required
@permission_required("manage_consultations")
def edit_consultation(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id, is_deleted=False).first_or_404()
    form = ConsultationForm(obj=consultation)

    if form.validate_on_submit():
        form.populate_obj(consultation)
        consultation.refresh_payment_status()
        log_action("modification_consultation", entity_type="Consultation", entity_id=consultation.id)
        db.session.commit()
        flash("Consultation mise à jour avec succès.", "success")
        return redirect(url_for("consultations.view_consultation", consultation_id=consultation.id))

    return render_template(
        "consultations/form.html", form=form, patient=consultation.patient, is_edit=True, consultation=consultation
    )


@consultations_bp.route("/<int:consultation_id>/absent", methods=["POST"])
@login_required
@permission_required("manage_consultations")
def mark_no_show(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id, is_deleted=False).first_or_404()
    consultation.status = ConsultationStatus.NO_SHOW
    log_action("patient_absent", entity_type="Consultation", entity_id=consultation.id)
    db.session.commit()
    flash("Le patient a été marqué comme absent.", "info")
    return redirect(url_for("patients.view_patient", patient_id=consultation.patient_id))


@consultations_bp.route("/<int:consultation_id>/finaliser", methods=["POST"])
@login_required
@permission_required("manage_consultations")
def finalize_visit(consultation_id):
    """Termine la visite et enregistre un paiement final en une seule action."""
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
        consultation.status = ConsultationStatus.COMPLETED
        log_action("finalisation_visite", entity_type="Consultation", entity_id=consultation.id,
                    description=f"Paiement de {form.amount.data} DA enregistré")
        db.session.commit()
        flash("Visite finalisée et paiement enregistré avec succès.", "success")
    else:
        flash("Montant de paiement invalide.", "danger")

    return redirect(url_for("patients.view_patient", patient_id=consultation.patient_id))
