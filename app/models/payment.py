"""
Modèle Payment - historique des paiements liés à une consultation.
"""
import enum

from app.extensions import db
from app.models.base import TimestampMixin, PublicIdMixin


class PaymentMethod(str, enum.Enum):
    CASH = "especes"
    CARD = "carte"
    TRANSFER = "virement"
    CHEQUE = "cheque"
    OTHER = "autre"


PAYMENT_METHOD_LABELS_FR = {
    PaymentMethod.CASH: "Espèces",
    PaymentMethod.CARD: "Carte bancaire",
    PaymentMethod.TRANSFER: "Virement",
    PaymentMethod.CHEQUE: "Chèque",
    PaymentMethod.OTHER: "Autre",
}


class Payment(TimestampMixin, PublicIdMixin, db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True)

    consultation_id = db.Column(
        db.Integer, db.ForeignKey("consultations.id"), nullable=False, index=True
    )
    consultation = db.relationship("Consultation", back_populates="payments")

    amount = db.Column(db.Numeric(10, 2), nullable=False)
    method = db.Column(db.Enum(PaymentMethod), nullable=False, default=PaymentMethod.CASH)
    payment_date = db.Column(db.DateTime(timezone=True), nullable=False)
    note = db.Column(db.String(255), nullable=True)

    received_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    received_by = db.relationship("User", foreign_keys=[received_by_id])

    @property
    def method_label(self):
        return PAYMENT_METHOD_LABELS_FR.get(self.method, self.method.value)

    def __repr__(self):
        return f"<Payment #{self.id} consultation={self.consultation_id} montant={self.amount}>"
