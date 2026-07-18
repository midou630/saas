"""
Routes de gestion des patients : liste, création, modification, dossier médical.
"""
from datetime import datetime, timezone

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, send_from_directory
from flask_login import login_required, current_user
from sqlalchemy import or_

from app.extensions import db
from app.models.patient import Patient, PatientDocument
from app.models.consultation import Consultation
from app.patients.forms import PatientForm, PatientDocumentForm
from app.utils.decorators import permission_required
from app.utils.helpers import save_uploaded_file
from app.utils.audit import log_action

patients_bp = Blueprint("patients", __name__, template_folder="../templates/patients")


@patients_bp.route("/")
@login_required
@permission_required("manage_patients")
def list_patients():
    search_query = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)

    query = Patient.query.filter_by(is_deleted=False)

    if search_query:
        like_pattern = f"%{search_query}%"
        query = query.filter(
            or_(
                Patient.first_name.ilike(like_pattern),
                Patient.last_name.ilike(like_pattern),
                Patient.file_number.ilike(like_pattern),
                Patient.phone.ilike(like_pattern),
            )
        )

    pagination = query.order_by(Patient.created_at.desc()).paginate(
        page=page, per_page=current_app.config["PATIENTS_PER_PAGE"], error_out=False
    )

    return render_template(
        "patients/list.html", patients=pagination.items, pagination=pagination, search_query=search_query
    )


@patients_bp.route("/nouveau", methods=["GET", "POST"])
@login_required
@permission_required("manage_patients")
def create_patient():
    form = PatientForm()
    if form.validate_on_submit():
        patient = Patient(
            file_number=Patient.generate_file_number(db.session),
            first_name=form.first_name.data.strip(),
            last_name=form.last_name.data.strip(),
            birth_date=form.birth_date.data,
            gender=form.gender.data,
            phone=form.phone.data,
            email=form.email.data,
            address=form.address.data,
            city=form.city.data,
            emergency_contact_name=form.emergency_contact_name.data,
            emergency_contact_phone=form.emergency_contact_phone.data,
            blood_type=form.blood_type.data,
            allergies=form.allergies.data,
            chronic_diseases=form.chronic_diseases.data,
            past_surgeries=form.past_surgeries.data,
            general_notes=form.general_notes.data,
            created_by_id=current_user.id,
        )
        db.session.add(patient)
        db.session.flush()
        log_action("creation_patient", entity_type="Patient", entity_id=patient.id,
                    description=f"Création du patient {patient.full_name} ({patient.file_number})")
        db.session.commit()
        flash(f"Patient créé avec succès. Numéro de dossier : {patient.file_number}", "success")
        return redirect(url_for("patients.view_patient", patient_id=patient.id))

    return render_template("patients/form.html", form=form, is_edit=False)


@patients_bp.route("/<int:patient_id>")
@login_required
@permission_required("manage_patients")
def view_patient(patient_id):
    patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first_or_404()
    consultations = (
        Consultation.query.filter_by(patient_id=patient.id, is_deleted=False)
        .order_by(Consultation.visit_date.desc())
        .all()
    )
    document_form = PatientDocumentForm()
    return render_template(
        "patients/detail.html", patient=patient, consultations=consultations, document_form=document_form
    )


@patients_bp.route("/<int:patient_id>/modifier", methods=["GET", "POST"])
@login_required
@permission_required("manage_patients")
def edit_patient(patient_id):
    patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first_or_404()
    form = PatientForm(obj=patient)

    if form.validate_on_submit():
        form.populate_obj(patient)
        log_action("modification_patient", entity_type="Patient", entity_id=patient.id,
                    description=f"Modification du patient {patient.full_name}")
        db.session.commit()
        flash("Informations du patient mises à jour avec succès.", "success")
        return redirect(url_for("patients.view_patient", patient_id=patient.id))

    return render_template("patients/form.html", form=form, is_edit=True, patient=patient)


@patients_bp.route("/<int:patient_id>/supprimer", methods=["POST"])
@login_required
@permission_required("manage_patients")
def delete_patient(patient_id):
    patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first_or_404()
    patient.soft_delete()
    log_action("suppression_patient", entity_type="Patient", entity_id=patient.id,
                description=f"Suppression (douce) du patient {patient.full_name}")
    db.session.commit()
    flash("Le patient a été archivé avec succès.", "success")
    return redirect(url_for("patients.list_patients"))


@patients_bp.route("/<int:patient_id>/documents", methods=["POST"])
@login_required
@permission_required("manage_patients")
def upload_document(patient_id):
    patient = Patient.query.filter_by(id=patient_id, is_deleted=False).first_or_404()
    form = PatientDocumentForm()

    if form.validate_on_submit():
        file_storage = request.files.get("file")
        result = save_uploaded_file(file_storage, subfolder="patient_documents")

        if result is None:
            flash("Fichier invalide. Extensions autorisées : PDF, JPG, JPEG, PNG, WEBP.", "danger")
        else:
            document = PatientDocument(
                patient_id=patient.id,
                original_filename=result["original_filename"],
                stored_filename=result["stored_filename"],
                file_type=result["file_type"],
                file_size_bytes=result["file_size_bytes"],
                description=form.description.data,
                uploaded_by_id=current_user.id,
            )
            db.session.add(document)
            log_action("ajout_document_patient", entity_type="Patient", entity_id=patient.id,
                        description=f"Ajout du document {result['original_filename']}")
            db.session.commit()
            flash("Document téléversé avec succès.", "success")

    return redirect(url_for("patients.view_patient", patient_id=patient.id))


@patients_bp.route("/documents/<int:document_id>/telecharger")
@login_required
@permission_required("manage_patients")
def download_document(document_id):
    document = PatientDocument.query.get_or_404(document_id)
    directory = current_app.config["UPLOAD_FOLDER"]
    return send_from_directory(directory, document.stored_filename, as_attachment=True,
                                download_name=document.original_filename)
