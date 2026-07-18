"""
Mixins réutilisables pour tous les modèles SQLAlchemy.
Fournissent : horodatage automatique, suppression douce (soft delete) et
un identifiant public non-séquentiel pour éviter l'énumération d'IDs.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import event

from app.extensions import db


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    """Ajoute des colonnes created_at / updated_at maintenues automatiquement."""

    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class SoftDeleteMixin:
    """
    Implémente la suppression douce : les enregistrements ne sont jamais
    supprimés physiquement, uniquement marqués comme supprimés.
    """

    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime(timezone=True), nullable=True)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = utcnow()

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None


class PublicIdMixin:
    """Ajoute un identifiant public UUID, utilisé dans les URLs plutôt que l'ID auto-incrémenté."""

    public_id = db.Column(
        db.String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4()), index=True
    )
