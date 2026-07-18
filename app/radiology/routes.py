"""
Routes et formulaires de gestion des demandes d'examens radiologiques.
"""
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, send_file
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, Length

from app.extensions import db
from app.models.consultation import Consultation
from app.models.radiology import RadiologyRequest, RadiologyRequestStatus
from app.utils.decorators import permission_required
from app.utils.audit import log_action
from app.utils.pdf import render_pdf_from_template

radiology_bp = Blueprint("radiology", __name__, template_folder="../templates/radiology")


class RadiologyRequestForm(FlaskForm):
    exam_type = StringField(
        "Type d'examen", validators=[DataRequired(message="Le type d'examen est obligatoire."), Length(max=200)]
    )
    body_area = StringField("Région anatomique", validators=[Optional(), Length(max=150)])
    clinical_notes = TextAreaField("Renseignements cliniques", validators=[Optional()])
    submit = SubmitField("Créer la demande")


class RadiologyResultForm(FlaskForm):
    result_summary = TextAreaField("Compte rendu", validators=[DataRequired()])
    status = SelectField(
        "Statut",
        choices=[(s.value, s.value) for s in RadiologyRequestStatus],
        validators=[DataRequired()],
    )
    submit = SubmitField("Enregistrer le compte rendu")


@radiology_bp.route("/consultation/<int:consultation_id>/nouvelle", methods=["GET", "POST"])
@login_required
@permission_required("manage_lab_radiology")
def create_radiology_request(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id, is_deleted=False).first_or_404()
    form = RadiologyRequestForm()

    if form.validate_on_submit():
        radiology_request = RadiologyRequest(
            consultation_id=consultation.id,
            requested_by_id=current_user.id,
            exam_type=form.exam_type.data,
            body_area=form.body_area.data,
            clinical_notes=form.clinical_notes.data,
        )
        db.session.add(radiology_request)
        db.session.flush()
        log_action("creation_demande_radiologie", entity_type="RadiologyRequest", entity_id=radiology_request.id)
        db.session.commit()
        flash("Demande de radiologie créée avec succès.", "success")
        return redirect(url_for("consultations.view_consultation", consultation_id=consultation.id))

    return render_template("radiology/form.html", form=form, consultation=consultation)


@radiology_bp.route("/<int:request_id>/resultats", methods=["GET", "POST"])
@login_required
@permission_required("manage_lab_radiology")
def update_results(request_id):
    radiology_request = RadiologyRequest.query.filter_by(id=request_id, is_deleted=False).first_or_404()
    form = RadiologyResultForm(obj=radiology_request)

    if form.validate_on_submit():
        radiology_request.result_summary = form.result_summary.data
        radiology_request.status = form.status.data
        radiology_request.result_received_at = datetime.now(timezone.utc)
        log_action("mise_a_jour_resultats_radiologie", entity_type="RadiologyRequest", entity_id=radiology_request.id)
        db.session.commit()
        flash("Compte rendu enregistré avec succès.", "success")
        return redirect(url_for("consultations.view_consultation", consultation_id=radiology_request.consultation_id))

    return render_template("radiology/results.html", form=form, radiology_request=radiology_request)


@radiology_bp.route("/<int:request_id>/imprimer")
@login_required
@permission_required("manage_lab_radiology")
def print_request(request_id):
    radiology_request = RadiologyRequest.query.filter_by(id=request_id, is_deleted=False).first_or_404()
    from flask import current_app
    pdf_buffer = render_pdf_from_template(
        "radiology/pdf.html", radiology_request=radiology_request, clinic_name=current_app.config.get("CLINIC_NAME")
    )
    filename = f"radiologie_{radiology_request.consultation.patient.file_number}_{radiology_request.id}.pdf"
    return send_file(pdf_buffer, mimetype="application/pdf", download_name=filename)
