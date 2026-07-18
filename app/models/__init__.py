"""
Point d'entrée unique pour tous les modèles - facilite les imports
et garantit que tous les modèles sont enregistrés auprès de SQLAlchemy
avant la création des migrations.
"""
from app.models.user import User, UserRole
from app.models.patient import Patient, PatientDocument, FileNumberSequence, Gender
from app.models.consultation import Consultation, ConsultationStatus, PaymentStatus
from app.models.prescription import (
    Prescription,
    PrescriptionItem,
    PrescriptionTemplate,
    PrescriptionTemplateItem,
)
from app.models.lab import LabTestRequest, LabRequestStatus
from app.models.radiology import RadiologyRequest, RadiologyRequestStatus
from app.models.inventory import (
    ProductCategory,
    Supplier,
    Product,
    StockMovement,
    StockMovementType,
)
from app.models.payment import Payment, PaymentMethod
from app.models.audit_log import AuditLog
from app.models.notification import Notification, NotificationType

__all__ = [
    "User", "UserRole",
    "Patient", "PatientDocument", "FileNumberSequence", "Gender",
    "Consultation", "ConsultationStatus", "PaymentStatus",
    "Prescription", "PrescriptionItem", "PrescriptionTemplate", "PrescriptionTemplateItem",
    "LabTestRequest", "LabRequestStatus",
    "RadiologyRequest", "RadiologyRequestStatus",
    "ProductCategory", "Supplier", "Product", "StockMovement", "StockMovementType",
    "Payment", "PaymentMethod",
    "AuditLog",
    "Notification", "NotificationType",
]
