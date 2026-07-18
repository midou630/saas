"""
Point d'entrée de l'application - utilisé pour le développement local.
En production, utiliser Gunicorn : gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
"""
import os

from app import create_app
from app.extensions import db
from app.models import (
    User, Patient, Consultation, Prescription, PrescriptionItem,
    LabTestRequest, RadiologyRequest, Product, ProductCategory, Supplier,
    StockMovement, Payment, AuditLog, Notification,
)

app = create_app(os.environ.get("FLASK_ENV", "development"))


@app.shell_context_processor
def make_shell_context():
    """Rend les modèles disponibles automatiquement dans `flask shell`."""
    return {
        "db": db, "User": User, "Patient": Patient, "Consultation": Consultation,
        "Prescription": Prescription, "PrescriptionItem": PrescriptionItem,
        "LabTestRequest": LabTestRequest, "RadiologyRequest": RadiologyRequest,
        "Product": Product, "ProductCategory": ProductCategory, "Supplier": Supplier,
        "StockMovement": StockMovement, "Payment": Payment, "AuditLog": AuditLog,
        "Notification": Notification,
    }


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
