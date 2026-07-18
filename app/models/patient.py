"""
Modèle Patient - contient uniquement les informations stables du patient.
Les informations variables (diagnostic, prix, ordonnances...) vivent dans Consultation.
"""
import enum
from datetime import date

from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, PublicIdMixin


class Gender(str, enum.Enum):
    MALE = "homme"
    FEMALE = "femme"


GENDER_LABELS_FR = {
    Gender.MALE: "Homme",
    Gender.FEMALE: "Femme",
}


class FileNumberSequence(db.Model):
    """
    Compteur transactionnel utilisé pour générer les numéros de dossier
    médical de façon séquentielle et sans collision, par année civile.
    """

    __tablename__ = "file_number_sequences"

    year = db.Column(db.Integer, primary_key=True)
    last_value = db.Column(db.Integer, nullable=False, default=0)


class Patient(TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    file_number = db.Column(db.String(20), unique=True, nullable=False, index=True)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date, nullable=True)
    gender = db.Column(db.Enum(Gender), nullable=False)

    phone = db.Column(db.String(30), nullable=True, index=True)
    email = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    city = db.Column(db.String(100), nullable=True)

    emergency_contact_name = db.Column(db.String(150), nullable=True)
    emergency_contact_phone = db.Column(db.String(30), nullable=True)

    blood_type = db.Column(db.String(5), nullable=True)
    allergies = db.Column(db.Text, nullable=True)
    chronic_diseases = db.Column(db.Text, nullable=True)
    past_surgeries = db.Column(db.Text, nullable=True)
    general_notes = db.Column(db.Text, nullable=True)

    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by = db.relationship("User", foreign_keys=[created_by_id])

    consultations = db.relationship(
        "Consultation",
        back_populates="patient",
        order_by="desc(Consultation.visit_date)",
        cascade="all, delete-orphan",
    )
    documents = db.relationship(
        "PatientDocument", back_populates="patient", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.Index("ix_patients_name", "last_name", "first_name"),
    )

    @property
    def full_name(self):
        return f"{self.last_name} {self.first_name}"

    @property
    def age(self):
        if not self.birth_date:
            return None
        today = date.today()
        years = today.year - self.birth_date.year
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            years -= 1
        return years

    @property
    def gender_label(self):
        return GENDER_LABELS_FR.get(self.gender, self.gender.value)

    @staticmethod
    def generate_file_number(session, year=None):
        """
        Génère le prochain numéro de dossier médical au format PAT-AAAA-000001
        de manière atomique grâce à un verrou de ligne (SELECT ... FOR UPDATE).
        """
        from datetime import datetime

        year = year or datetime.utcnow().year
        counter = (
            session.query(FileNumberSequence)
            .filter_by(year=year)
            .with_for_update()
            .first()
        )
        if counter is None:
            counter = FileNumberSequence(year=year, last_value=0)
            session.add(counter)
            session.flush()

        counter.last_value += 1
        session.flush()
        return f"PAT-{year}-{counter.last_value:06d}"

    def __repr__(self):
        return f"<Patient {self.file_number} {self.full_name}>"


class PatientDocument(TimestampMixin, PublicIdMixin, db.Model):
    """Documents et images attachés au dossier médical du patient."""

    __tablename__ = "patient_documents"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    patient = db.relationship("Patient", back_populates="documents")

    original_filename = db.Column(db.String(255), nullable=False)
    stored_filename = db.Column(db.String(255), nullable=False, unique=True)
    file_type = db.Column(db.String(10), nullable=False)
    file_size_bytes = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    uploaded_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    uploaded_by = db.relationship("User", foreign_keys=[uploaded_by_id])
