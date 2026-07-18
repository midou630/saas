"""
Modèle Notification - alertes système destinées aux utilisateurs.
"""
import enum

from app.extensions import db
from app.models.base import TimestampMixin


class NotificationType(str, enum.Enum):
    LOW_STOCK = "stock_faible"
    PATIENT = "patient"
    BACKUP = "sauvegarde"
    SYSTEM = "systeme"


NOTIFICATION_TYPE_LABELS_FR = {
    NotificationType.LOW_STOCK: "Stock faible",
    NotificationType.PATIENT: "Patient",
    NotificationType.BACKUP: "Sauvegarde",
    NotificationType.SYSTEM: "Système",
}


class Notification(TimestampMixin, db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    user = db.relationship("User", foreign_keys=[user_id])

    notification_type = db.Column(db.Enum(NotificationType), nullable=False, index=True)
    title = db.Column(db.String(150), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    link_url = db.Column(db.String(255), nullable=True)

    @property
    def type_label(self):
        return NOTIFICATION_TYPE_LABELS_FR.get(self.notification_type, self.notification_type.value)
