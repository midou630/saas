"""
Routes de gestion des ordonnances : création, modification, suppression, impression PDF.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user

from app.extensions import db
from app.models.consultation import Consultation
from app.models.prescription import Prescription, PrescriptionItem, PrescriptionTemplate
from app.prescriptions.forms import PrescriptionForm
from app.utils.decorators import permission_required
from app.utils.audit import log_action
from app.utils.pdf import render_pdf_from_template

prescriptions_bp = Blueprint("prescriptions", __name__, template_folder="../templates/prescriptions")


@prescriptions_bp.route("/consultation/<int:consultation_id>/nouvelle", methods=["GET", "POST"])
@login_required
@permission_required("manage_prescriptions")
def create_prescription(consultation_id):
    consultation = Consultation.query.filter_by(id=consultation_id, is_deleted=False).first_or_404()
    form = PrescriptionForm()
    templates = PrescriptionTemplate.query.order_by(PrescriptionTemplate.name).all()

    if form.validate_on_submit():
        prescription = Prescription(
            consultation_id=consultation.id,
            issued_by_id=current_user.id,
            additional_instructions=form.additional_instructions.data,
        )
        db.session.add(prescription)
        db.session.flush()

        for index, item_form in enumerate(form.items):
            if item_form.medication_name.data:
                db.session.add(
                    PrescriptionItem(
                        prescription_id=prescription.id,
                        position=index,
                        medication_name=item_form.medication_name.data,
                        dosage=item_form.dosage.data,
                        frequency=item_form.frequency.data,
                        duration=item_form.duration.data,
                        instructions=item_form.instructions.data,
                    )
                )

        log_action("creation_ordonnance", entity_type="Prescription", entity_id=prescription.id,
                    description=f"Nouvelle ordonnance pour {consultation.patient.full_name}")
        db.session.commit()
        flash("Ordonnance créée avec succès.", "success")
        return redirect(url_for("prescriptions.view_prescription", prescription_id=prescription.id))

    return render_template(
        "prescriptions/form.html", form=form, consultation=consultation, templates=templates, is_edit=False
    )


@prescriptions_bp.route("/<int:prescription_id>")
@login_required
@permission_required("manage_prescriptions")
def view_prescription(prescription_id):
    prescription = Prescription.query.filter_by(id=prescription_id, is_deleted=False).first_or_404()
    return render_template("prescriptions/detail.html", prescription=prescription)


@prescriptions_bp.route("/<int:prescription_id>/modifier", methods=["GET", "POST"])
@login_required
@permission_required("manage_prescriptions")
def edit_prescription(prescription_id):
    prescription = Prescription.query.filter_by(id=prescription_id, is_deleted=False).first_or_404()
    form = PrescriptionForm(obj=prescription)

    if request.method == "GET":
        form.items.entries = []
        for item in prescription.items:
            form.items.append_entry(item)

    if form.validate_on_submit():
        prescription.additional_instructions = form.additional_instructions.data
        PrescriptionItem.query.filter_by(prescription_id=prescription.id).delete()

        for index, item_form in enumerate(form.items):
            if item_form.medication_name.data:
                db.session.add(
                    PrescriptionItem(
                        prescription_id=prescription.id,
                        position=index,
                        medication_name=item_form.medication_name.data,
                        dosage=item_form.dosage.data,
                        frequency=item_form.frequency.data,
                        duration=item_form.duration.data,
                        instructions=item_form.instructions.data,
                    )
                )

        log_action("modification_ordonnance", entity_type="Prescription", entity_id=prescription.id)
        db.session.commit()
        flash("Ordonnance mise à jour avec succès.", "success")
        return redirect(url_for("prescriptions.view_prescription", prescription_id=prescription.id))

    return render_template(
        "prescriptions/form.html", form=form, consultation=prescription.consultation, templates=[], is_edit=True,
        prescription=prescription,
    )


@prescriptions_bp.route("/<int:prescription_id>/supprimer", methods=["POST"])
@login_required
@permission_required("manage_prescriptions")
def delete_prescription(prescription_id):
    prescription = Prescription.query.filter_by(id=prescription_id, is_deleted=False).first_or_404()
    consultation_id = prescription.consultation_id
    prescription.soft_delete()
    log_action("suppression_ordonnance", entity_type="Prescription", entity_id=prescription.id)
    db.session.commit()
    flash("Ordonnance supprimée avec succès.", "success")
    return redirect(url_for("consultations.view_consultation", consultation_id=consultation_id))


@prescriptions_bp.route("/<int:prescription_id>/imprimer")
@login_required
@permission_required("manage_prescriptions")
def print_prescription(prescription_id):
    prescription = Prescription.query.filter_by(id=prescription_id, is_deleted=False).first_or_404()
    pdf_buffer = render_pdf_from_template(
        "prescriptions/pdf.html", prescription=prescription, clinic_name=current_app_clinic_name()
    )
    filename = f"ordonnance_{prescription.consultation.patient.file_number}_{prescription.id}.pdf"
    return send_file(pdf_buffer, mimetype="application/pdf", as_attachment=False, download_name=filename)


def current_app_clinic_name():
    from flask import current_app
    return current_app.config.get("CLINIC_NAME", "Cabinet Médical")
