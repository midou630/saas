"""
Modèles Prescription (ordonnance) et PrescriptionItem (ligne de médicament).
"""
from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, PublicIdMixin


class Prescription(TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "prescriptions"

    id = db.Column(db.Integer, primary_key=True)

    consultation_id = db.Column(
        db.Integer, db.ForeignKey("consultations.id"), nullable=False, index=True
    )
    consultation = db.relationship("Consultation", back_populates="prescriptions")

    issued_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    issued_by = db.relationship("User", foreign_keys=[issued_by_id])

    template_name = db.Column(db.String(120), nullable=True)
    additional_instructions = db.Column(db.Text, nullable=True)

    items = db.relationship(
        "PrescriptionItem",
        back_populates="prescription",
        cascade="all, delete-orphan",
        order_by="PrescriptionItem.position",
    )

    def __repr__(self):
        return f"<Prescription #{self.id} consultation={self.consultation_id}>"


class PrescriptionItem(db.Model):
    """Une ligne de médicament au sein d'une ordonnance."""

    __tablename__ = "prescription_items"

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(
        db.Integer, db.ForeignKey("prescriptions.id"), nullable=False, index=True
    )
    prescription = db.relationship("Prescription", back_populates="items")

    position = db.Column(db.Integer, nullable=False, default=0)
    medication_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(120), nullable=True)
    frequency = db.Column(db.String(120), nullable=True)
    duration = db.Column(db.String(120), nullable=True)
    instructions = db.Column(db.String(255), nullable=True)


class PrescriptionTemplate(TimestampMixin, PublicIdMixin, db.Model):
    """Modèles d'ordonnances réutilisables pour accélérer la saisie."""

    __tablename__ = "prescription_templates"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_by = db.relationship("User", foreign_keys=[created_by_id])

    items = db.relationship(
        "PrescriptionTemplateItem", back_populates="template", cascade="all, delete-orphan"
    )


class PrescriptionTemplateItem(db.Model):
    __tablename__ = "prescription_template_items"

    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(
        db.Integer, db.ForeignKey("prescription_templates.id"), nullable=False, index=True
    )
    template = db.relationship("PrescriptionTemplate", back_populates="items")

    position = db.Column(db.Integer, nullable=False, default=0)
    medication_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(120), nullable=True)
    frequency = db.Column(db.String(120), nullable=True)
    duration = db.Column(db.String(120), nullable=True)
    instructions = db.Column(db.String(255), nullable=True)
