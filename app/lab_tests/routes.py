"""
Routes et formulaires de gestion des demandes d'analyses (laboratoire).
"""
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional

from app.extensions import db
from app.models.consultation import Consultation
from app.models.lab import LabTestRequest, LabRequestStatus
from app.utils.decorators import permission_required
from app.utils.audit import log_action
from app.utils.pdf import render_pdf_from_template

lab_tests_bp = Blueprint("lab_tests", __name__, template_folder="../templates/lab_tests")


class LabTestRequestForm(FlaskForm):
    tests_requested = TextAreaField(
        "Analyses demandées", validators=[DataRequired(message="Veuillez préciser les analyses demandées.")]
    )
    clinical_notes = TextAreaField("Renseignements cliniques", validators=[Optional()])
    submit = SubmitField("Créer la demande")


class LabTestResultForm(FlaskForm):
    result_summary = TextAreaField("Résumé des résultats", validators=[DataRequired()])
    status = SelectField(
        "Statut",
        choices=[(s.value, s.value) for s in LabRequestStatus],
        validators=[DataRequired()],
    )
    submit = SubmitField("Enregistrer les résultats")


@lab_tests_bp.route("/consultation/<int:consultation_id>/nouvelle", methods=["GET", "POST"])
@login_required
@permission_required("manage_lab_radiology")
def create_lab_request(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id, is_deleted=False).first_or_404()
    form = LabTestRequestForm()

    if form.validate_on_submit():
        lab_request = LabTestRequest(
            consultation_id=consultation.id,
            requested_by_id=current_user.id,
            tests_requested=form.tests_requested.data,
            clinical_notes=form.clinical_notes.data,
        )
        db.session.add(lab_request)
        db.session.flush()
        log_action("creation_demande_analyse", entity_type="LabTestRequest", entity_id=lab_request.id)
        db.session.commit()
        flash("Demande d'analyses créée avec succès.", "success")
        return redirect(url_for("consultations.view_consultation", consultation_id=consultation.id))

    return render_template("lab_tests/form.html", form=form, consultation=consultation)


@lab_tests_bp.route("/<int:request_id>/resultats", methods=["GET", "POST"])
@login_required
@permission_required("manage_lab_radiology")
def update_results(request_id):
    lab_request = LabTestRequest.query.filter_by(id=request_id, is_deleted=False).first_or_404()
    form = LabTestResultForm(obj=lab_request)

    if form.validate_on_submit():
        lab_request.result_summary = form.result_summary.data
        lab_request.status = form.status.data
        lab_request.result_received_at = datetime.now(timezone.utc)
        log_action("mise_a_jour_resultats_analyse", entity_type="LabTestRequest", entity_id=lab_request.id)
        db.session.commit()
        flash("Résultats enregistrés avec succès.", "success")
        return redirect(url_for("consultations.view_consultation", consultation_id=lab_request.consultation_id))

    return render_template("lab_tests/results.html", form=form, lab_request=lab_request)


@lab_tests_bp.route("/<int:request_id>/imprimer")
@login_required
@permission_required("manage_lab_radiology")
def print_request(request_id):
    lab_request = LabTestRequest.query.filter_by(id=request_id, is_deleted=False).first_or_404()
    from flask import current_app
    pdf_buffer = render_pdf_from_template(
        "lab_tests/pdf.html", lab_request=lab_request, clinic_name=current_app.config.get("CLINIC_NAME")
    )
    filename = f"analyses_{lab_request.consultation.patient.file_number}_{lab_request.id}.pdf"
    return send_file(pdf_buffer, mimetype="application/pdf", download_name=filename)
