"""
Routes de gestion des utilisateurs du système (réservées à l'administrateur).
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo

from app.extensions import db
from app.models.user import User, UserRole, ROLE_LABELS_FR
from app.models.audit_log import AuditLog
from app.utils.decorators import permission_required
from app.utils.audit import log_action

users_bp = Blueprint("users", __name__, template_folder="../templates/users")


class UserForm(FlaskForm):
    first_name = StringField("Prénom", validators=[DataRequired(), Length(max=80)])
    last_name = StringField("Nom", validators=[DataRequired(), Length(max=80)])
    email = StringField("Adresse e-mail", validators=[DataRequired(), Email(), Length(max=255)])
    phone = StringField("Téléphone", validators=[Optional(), Length(max=30)])
    role = SelectField(
        "Rôle", choices=[(r.value, ROLE_LABELS_FR[r]) for r in UserRole], validators=[DataRequired()]
    )
    password = PasswordField(
        "Mot de passe", validators=[Optional(), Length(min=8, message="Minimum 8 caractères.")]
    )
    confirm_password = PasswordField(
        "Confirmer le mot de passe",
        validators=[Optional(), EqualTo("password", message="Les mots de passe ne correspondent pas.")],
    )
    is_active_account = BooleanField("Compte actif", default=True)
    submit = SubmitField("Enregistrer")


@users_bp.route("/")
@login_required
@permission_required("manage_users")
def list_users():
    users = User.query.filter_by(is_deleted=False).order_by(User.last_name).all()
    return render_template("users/list.html", users=users)


@users_bp.route("/nouveau", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def create_user():
    form = UserForm()
    if form.validate_on_submit():
        if not form.password.data:
            flash("Le mot de passe est obligatoire pour un nouvel utilisateur.", "danger")
        elif User.query.filter_by(email=form.email.data.lower().strip()).first():
            flash("Cette adresse e-mail est déjà utilisée.", "danger")
        else:
            user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                email=form.email.data.lower().strip(),
                phone=form.phone.data,
                role=form.role.data,
                is_active_account=form.is_active_account.data,
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.flush()
            log_action("creation_utilisateur", entity_type="User", entity_id=user.id, description=user.email)
            db.session.commit()
            flash("Utilisateur créé avec succès.", "success")
            return redirect(url_for("users.list_users"))

    return render_template("users/form.html", form=form, is_edit=False)


@users_bp.route("/<int:user_id>/modifier", methods=["GET", "POST"])
@login_required
@permission_required("manage_users")
def edit_user(user_id):
    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    form = UserForm(obj=user)

    if form.validate_on_submit():
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.email = form.email.data.lower().strip()
        user.phone = form.phone.data
        user.role = form.role.data
        user.is_active_account = form.is_active_account.data
        if form.password.data:
            user.set_password(form.password.data)

        log_action("modification_utilisateur", entity_type="User", entity_id=user.id)
        db.session.commit()
        flash("Utilisateur mis à jour avec succès.", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/form.html", form=form, is_edit=True, user=user)


@users_bp.route("/<int:user_id>/supprimer", methods=["POST"])
@login_required
@permission_required("manage_users")
def delete_user(user_id):
    if user_id == current_user.id:
        flash("Vous ne pouvez pas supprimer votre propre compte.", "danger")
        return redirect(url_for("users.list_users"))

    user = User.query.filter_by(id=user_id, is_deleted=False).first_or_404()
    user.soft_delete()
    log_action("suppression_utilisateur", entity_type="User", entity_id=user.id)
    db.session.commit()
    flash("Utilisateur archivé avec succès.", "success")
    return redirect(url_for("users.list_users"))


@users_bp.route("/journal-audit")
@login_required
@permission_required("view_audit_log")
def audit_log():
    page = request.args.get("page", 1, type=int)
    pagination = AuditLog.query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=50, error_out=False
    )
    return render_template("users/audit_log.html", logs=pagination.items, pagination=pagination)
