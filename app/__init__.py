"""
Fabrique de l'application Flask (Application Factory Pattern).
Centralise l'initialisation des extensions, blueprints, gestion des erreurs
et commandes CLI.
"""
import os
from datetime import datetime, timezone

from flask import Flask, render_template
from flask_talisman import Talisman

from config import config
from app.extensions import db, migrate, login_manager, csrf, cache, limiter


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

    _register_extensions(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_context_processors(app)
    _register_cli_commands(app)

    return app


def _register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    # ---- En-têtes de sécurité HTTP (protection XSS, clickjacking, etc.) ----
    csp = {
        "default-src": "'self'",
        "style-src": ["'self'", "'unsafe-inline'"],
        "script-src": ["'self'", "'unsafe-inline'"],
        "img-src": ["'self'", "data:"],
        "font-src": ["'self'", "data:"],
    }
    Talisman(
        app,
        content_security_policy=csp,
        force_https=app.config.get("SESSION_COOKIE_SECURE", False),
        strict_transport_security=app.config.get("SESSION_COOKIE_SECURE", False),
    )

    from app.models.user import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))


def _register_blueprints(app):
    from app.auth.routes import auth_bp
    from app.dashboard.routes import dashboard_bp
    from app.patients.routes import patients_bp
    from app.consultations.routes import consultations_bp
    from app.prescriptions.routes import prescriptions_bp
    from app.lab_tests.routes import lab_tests_bp
    from app.radiology.routes import radiology_bp
    from app.inventory.routes import inventory_bp
    from app.payments.routes import payments_bp
    from app.notifications.routes import notifications_bp
    from app.reports.routes import reports_bp
    from app.users.routes import users_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(dashboard_bp, url_prefix="/")
    app.register_blueprint(patients_bp, url_prefix="/patients")
    app.register_blueprint(consultations_bp, url_prefix="/consultations")
    app.register_blueprint(prescriptions_bp, url_prefix="/ordonnances")
    app.register_blueprint(lab_tests_bp, url_prefix="/analyses")
    app.register_blueprint(radiology_bp, url_prefix="/radiologie")
    app.register_blueprint(inventory_bp, url_prefix="/stock")
    app.register_blueprint(payments_bp, url_prefix="/paiements")
    app.register_blueprint(notifications_bp, url_prefix="/notifications")
    app.register_blueprint(reports_bp, url_prefix="/rapports")
    app.register_blueprint(users_bp, url_prefix="/utilisateurs")


def _register_error_handlers(app):
    @app.errorhandler(403)
    def forbidden(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(413)
    def file_too_large(error):
        return render_template("errors/413.html"), 413

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template("errors/500.html"), 500


def _register_context_processors(app):
    from flask_login import current_user
    from app.models.notification import Notification

    @app.context_processor
    def inject_globals():
        unread_count = 0
        if current_user.is_authenticated:
            unread_count = Notification.query.filter_by(
                user_id=current_user.id, is_read=False
            ).count()
        return {
            "clinic_name": app.config.get("CLINIC_NAME"),
            "current_year": datetime.now(timezone.utc).year,
            "unread_notifications_count": unread_count,
        }


def _register_cli_commands(app):
    @app.cli.command("creer-admin")
    def create_admin():
        """Crée un compte administrateur initial de manière interactive."""
        import getpass
        from app.models.user import User, UserRole

        email = input("E-mail de l'administrateur : ").strip().lower()
        first_name = input("Prénom : ").strip()
        last_name = input("Nom : ").strip()
        password = getpass.getpass("Mot de passe (min. 8 caractères) : ")

        if len(password) < 8:
            print("Erreur : le mot de passe doit contenir au moins 8 caractères.")
            return

        if User.query.filter_by(email=email).first():
            print("Erreur : un utilisateur avec cet e-mail existe déjà.")
            return

        admin = User(
            email=email, first_name=first_name, last_name=last_name,
            role=UserRole.ADMIN, is_active_account=True,
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        print(f"Administrateur '{email}' créé avec succès.")

    @app.cli.command("sauvegarder-db")
    def backup_database():
        """Crée une sauvegarde horodatée de la base de données SQLite (développement)."""
        import shutil

        db_uri = app.config["SQLALCHEMY_DATABASE_URI"]
        if not db_uri.startswith("sqlite:///"):
            print("La sauvegarde automatique via cette commande ne s'applique qu'à SQLite.")
            print("Pour PostgreSQL, utilisez pg_dump.")
            return

        source_path = db_uri.replace("sqlite:///", "")
        backup_dir = os.path.join(app.instance_path, "backups")
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        destination_path = os.path.join(backup_dir, f"clinic_backup_{timestamp}.db")
        shutil.copy2(source_path, destination_path)
        print(f"Sauvegarde créée : {destination_path}")
