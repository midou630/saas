"""
Modèle Consultation - représente une visite médicale unique du patient.
Contient toutes les informations variables : diagnostic, prix, statut de paiement...
"""
import enum

from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, PublicIdMixin


class ConsultationStatus(str, enum.Enum):
    SCHEDULED = "planifiee"
    IN_PROGRESS = "en_cours"
    COMPLETED = "terminee"
    NO_SHOW = "absent"
    CANCELLED = "annulee"


CONSULTATION_STATUS_LABELS_FR = {
    ConsultationStatus.SCHEDULED: "Planifiée",
    ConsultationStatus.IN_PROGRESS: "En cours",
    ConsultationStatus.COMPLETED: "Terminée",
    ConsultationStatus.NO_SHOW: "Patient absent",
    ConsultationStatus.CANCELLED: "Annulée",
}


class PaymentStatus(str, enum.Enum):
    UNPAID = "non_paye"
    PARTIAL = "paiement_partiel"
    PAID = "paye"


PAYMENT_STATUS_LABELS_FR = {
    PaymentStatus.UNPAID: "Non payé",
    PaymentStatus.PARTIAL: "Payé partiellement",
    PaymentStatus.PAID: "Payé",
}


class Consultation(TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "consultations"

    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False, index=True)
    patient = db.relationship("Patient", back_populates="consultations")

    doctor_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    doctor = db.relationship("User", back_populates="consultations", foreign_keys=[doctor_id])

    visit_date = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    reason = db.Column(db.String(255), nullable=True)
    diagnosis = db.Column(db.Text, nullable=True)
    treatment = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)

    status = db.Column(
        db.Enum(ConsultationStatus), nullable=False, default=ConsultationStatus.SCHEDULED, index=True
    )

    consultation_price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    amount_paid = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    payment_status = db.Column(
        db.Enum(PaymentStatus), nullable=False, default=PaymentStatus.UNPAID, index=True
    )

    prescriptions = db.relationship(
        "Prescription", back_populates="consultation", cascade="all, delete-orphan"
    )
    lab_requests = db.relationship(
        "LabTestRequest", back_populates="consultation", cascade="all, delete-orphan"
    )
    radiology_requests = db.relationship(
        "RadiologyRequest", back_populates="consultation", cascade="all, delete-orphan"
    )
    payments = db.relationship(
        "Payment", back_populates="consultation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.Index("ix_consultations_patient_date", "patient_id", "visit_date"),
    )

    @property
    def status_label(self):
        return CONSULTATION_STATUS_LABELS_FR.get(self.status, self.status.value)

    @property
    def payment_status_label(self):
        return PAYMENT_STATUS_LABELS_FR.get(self.payment_status, self.payment_status.value)

    @property
    def balance_due(self):
        return (self.consultation_price or 0) - (self.amount_paid or 0)

    def refresh_payment_status(self):
        """Recalcule automatiquement le statut de paiement selon le solde."""
        if self.amount_paid <= 0:
            self.payment_status = PaymentStatus.UNPAID
        elif self.amount_paid < self.consultation_price:
            self.payment_status = PaymentStatus.PARTIAL
        else:
            self.payment_status = PaymentStatus.PAID

    def __repr__(self):
        return f"<Consultation #{self.id} patient={self.patient_id} {self.visit_date}>"
