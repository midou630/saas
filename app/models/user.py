"""
Modèle Utilisateur avec système de rôles et permissions.
"""
import enum

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, PublicIdMixin


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    DOCTOR = "docteur"
    SECRETARY = "secretaire"
    ASSISTANT = "assistant"


ROLE_LABELS_FR = {
    UserRole.ADMIN: "Administrateur",
    UserRole.DOCTOR: "Docteur",
    UserRole.SECRETARY: "Secrétaire",
    UserRole.ASSISTANT: "Assistant(e)",
}

# ---- Matrice des permissions par rôle ----
PERMISSIONS = {
    UserRole.ADMIN: {
        "manage_users", "manage_settings", "view_reports", "manage_patients",
        "manage_consultations", "manage_prescriptions", "manage_inventory",
        "manage_payments", "view_dashboard", "manage_lab_radiology", "view_audit_log",
    },
    UserRole.DOCTOR: {
        "manage_patients", "manage_consultations", "manage_prescriptions",
        "view_dashboard", "manage_lab_radiology", "view_reports",
    },
    UserRole.SECRETARY: {
        "manage_patients", "manage_payments", "view_dashboard", "manage_consultations",
    },
    UserRole.ASSISTANT: {
        "manage_patients", "view_dashboard", "manage_lab_radiology",
    },
}


class User(UserMixin, TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(30), nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.SECRETARY)
    is_active_account = db.Column(db.Boolean, default=True, nullable=False)
    last_login_at = db.Column(db.DateTime(timezone=True), nullable=True)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    locked_until = db.Column(db.DateTime(timezone=True), nullable=True)

    consultations = db.relationship(
        "Consultation", back_populates="doctor", foreign_keys="Consultation.doctor_id"
    )

    __table_args__ = (
        db.Index("ix_users_role_active", "role", "is_active_account"),
    )

    # ---- Mots de passe ----
    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password, method="pbkdf2:sha256:600000")

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    # ---- Flask-Login requiert un identifiant stable ----
    def get_id(self):
        return str(self.id)

    @property
    def is_active(self):
        return self.is_active_account and not self.is_deleted

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def role_label(self):
        return ROLE_LABELS_FR.get(self.role, self.role.value)

    def has_permission(self, permission):
        return permission in PERMISSIONS.get(self.role, set())

    def __repr__(self):
        return f"<User {self.email} ({self.role.value})>"
