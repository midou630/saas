"""
Modèle RadiologyRequest - demandes d'examens radiologiques.
"""
import enum

from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, PublicIdMixin


class RadiologyRequestStatus(str, enum.Enum):
    REQUESTED = "demande"
    RESULTS_RECEIVED = "resultats_recus"
    ARCHIVED = "archive"


RADIOLOGY_STATUS_LABELS_FR = {
    RadiologyRequestStatus.REQUESTED: "Demandé",
    RadiologyRequestStatus.RESULTS_RECEIVED: "Résultats reçus",
    RadiologyRequestStatus.ARCHIVED: "Archivé",
}


class RadiologyRequest(TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "radiology_requests"

    id = db.Column(db.Integer, primary_key=True)

    consultation_id = db.Column(
        db.Integer, db.ForeignKey("consultations.id"), nullable=False, index=True
    )
    consultation = db.relationship("Consultation", back_populates="radiology_requests")

    requested_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    requested_by = db.relationship("User", foreign_keys=[requested_by_id])

    exam_type = db.Column(db.String(200), nullable=False)
    body_area = db.Column(db.String(150), nullable=True)
    clinical_notes = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum(RadiologyRequestStatus),
        nullable=False,
        default=RadiologyRequestStatus.REQUESTED,
        index=True,
    )

    result_summary = db.Column(db.Text, nullable=True)
    result_document_id = db.Column(
        db.Integer, db.ForeignKey("patient_documents.id"), nullable=True
    )
    result_document = db.relationship("PatientDocument", foreign_keys=[result_document_id])
    result_received_at = db.Column(db.DateTime(timezone=True), nullable=True)

    @property
    def status_label(self):
        return RADIOLOGY_STATUS_LABELS_FR.get(self.status, self.status.value)

    def __repr__(self):
        return f"<RadiologyRequest #{self.id} consultation={self.consultation_id}>"
