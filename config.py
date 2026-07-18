"""
Configuration de l'application - Système de Gestion de Cabinet Médical
Gère les environnements: développement (SQLite) et production (PostgreSQL).
"""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """Configuration de base commune à tous les environnements."""

    # ---- Sécurité ----
    SECRET_KEY = os.environ.get("SECRET_KEY", "changez-cette-cle-en-production-absolument")
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600

    # ---- Session ----
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    REMEMBER_COOKIE_DURATION = timedelta(days=7)
    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "False") == "True"

    # ---- Base de données ----
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # ---- Téléversement de fichiers ----
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "app", "static", "uploads")
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024  # 8 Mo maximum par requête
    ALLOWED_DOCUMENT_EXTENSIONS = {"pdf", "jpg", "jpeg", "png", "webp"}
    ALLOWED_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp"}

    # ---- Pagination ----
    PATIENTS_PER_PAGE = 20
    CONSULTATIONS_PER_PAGE = 20
    INVENTORY_PER_PAGE = 25
    PAYMENTS_PER_PAGE = 25

    # ---- Localisation ----
    LANGUAGE = "fr"
    TIMEZONE = "Africa/Algiers"

    # ---- Nom de la clinique (personnalisable par le client SaaS) ----
    CLINIC_NAME = os.environ.get("CLINIC_NAME", "Cabinet Médical")

    # ---- Cache ----
    CACHE_TYPE = "SimpleCache"
    CACHE_DEFAULT_TIMEOUT = 120

    # ---- Limitation du débit (anti brute-force) ----
    RATELIMIT_STORAGE_URI = "memory://"
    RATELIMIT_DEFAULT = "200 per day, 50 per hour"

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Configuration de développement - utilise SQLite."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DEV_DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'clinic_dev.db')}"
    )


class TestingConfig(Config):
    """Configuration de test."""

    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


class ProductionConfig(Config):
    """Configuration de production - utilise PostgreSQL."""

    DEBUG = False
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "").replace(
        "postgres://", "postgresql://", 1
    ) or "postgresql://clinic_user:changeme@localhost:5432/clinic_production"

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        # En production, forcer la présence d'une clé secrète robuste
        if app.config["SECRET_KEY"] == "changez-cette-cle-en-production-absolument":
            raise RuntimeError(
                "SECRET_KEY doit être définie via une variable d'environnement en production."
            )


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
