"""
Modèle LabTestRequest - demandes d'analyses médicales (laboratoire).
"""
import enum

from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, PublicIdMixin


class LabRequestStatus(str, enum.Enum):
    REQUESTED = "demande"
    RESULTS_RECEIVED = "resultats_recus"
    ARCHIVED = "archive"


LAB_STATUS_LABELS_FR = {
    LabRequestStatus.REQUESTED: "Demandée",
    LabRequestStatus.RESULTS_RECEIVED: "Résultats reçus",
    LabRequestStatus.ARCHIVED: "Archivée",
}


class LabTestRequest(TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "lab_test_requests"

    id = db.Column(db.Integer, primary_key=True)

    consultation_id = db.Column(
        db.Integer, db.ForeignKey("consultations.id"), nullable=False, index=True
    )
    consultation = db.relationship("Consultation", back_populates="lab_requests")

    requested_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    requested_by = db.relationship("User", foreign_keys=[requested_by_id])

    tests_requested = db.Column(db.Text, nullable=False)
    clinical_notes = db.Column(db.Text, nullable=True)
    status = db.Column(
        db.Enum(LabRequestStatus), nullable=False, default=LabRequestStatus.REQUESTED, index=True
    )

    result_summary = db.Column(db.Text, nullable=True)
    result_document_id = db.Column(
        db.Integer, db.ForeignKey("patient_documents.id"), nullable=True
    )
    result_document = db.relationship("PatientDocument", foreign_keys=[result_document_id])
    result_received_at = db.Column(db.DateTime(timezone=True), nullable=True)

    @property
    def status_label(self):
        return LAB_STATUS_LABELS_FR.get(self.status, self.status.value)

    def __repr__(self):
        return f"<LabTestRequest #{self.id} consultation={self.consultation_id}>"
