"""
Routes d'authentification : connexion, déconnexion, changement de mot de passe.
"""
from datetime import datetime, timezone, timedelta

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.extensions import db, limiter
from app.models.user import User
from app.auth.forms import LoginForm, ChangePasswordForm
from app.utils.audit import log_action

auth_bp = Blueprint("auth", __name__, template_folder="../templates/auth")

MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 15


@auth_bp.route("/connexion", methods=["GET", "POST"])
@limiter.limit("15 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower().strip(), is_deleted=False).first()

        if user and user.locked_until and user.locked_until > datetime.now(timezone.utc):
            flash("Compte temporairement verrouillé suite à plusieurs tentatives échouées. Réessayez plus tard.", "danger")
            return render_template("auth/login.html", form=form)

        if user and user.is_active and user.check_password(form.password.data):
            user.failed_login_attempts = 0
            user.locked_until = None
            user.last_login_at = datetime.now(timezone.utc)
            login_user(user, remember=form.remember_me.data)
            log_action("connexion", entity_type="User", entity_id=user.id, description="Connexion réussie")
            db.session.commit()

            next_page = request.args.get("next")
            if not next_page or not next_page.startswith("/"):
                next_page = url_for("dashboard.index")
            return redirect(next_page)

        if user:
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                flash("Trop de tentatives échouées. Compte verrouillé pendant 15 minutes.", "danger")
            db.session.commit()

        flash("Adresse e-mail ou mot de passe incorrect.", "danger")

    return render_template("auth/login.html", form=form)


@auth_bp.route("/deconnexion")
@login_required
def logout():
    log_action("deconnexion", entity_type="User", entity_id=current_user.id, description="Déconnexion")
    db.session.commit()
    logout_user()
    flash("Vous avez été déconnecté avec succès.", "success")
    return redirect(url_for("auth.login"))


@auth_bp.route("/mot-de-passe", methods=["GET", "POST"])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Le mot de passe actuel est incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            log_action("modification_mot_de_passe", entity_type="User", entity_id=current_user.id)
            db.session.commit()
            flash("Votre mot de passe a été modifié avec succès.", "success")
            return redirect(url_for("dashboard.index"))
    return render_template("auth/change_password.html", form=form)
