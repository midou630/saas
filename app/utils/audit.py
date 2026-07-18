"""
Utilitaire d'enregistrement des actions dans le journal d'audit.
"""
from datetime import datetime, timezone

from flask import request
from flask_login import current_user

from app.extensions import db
from app.models.audit_log import AuditLog


def log_action(action, entity_type=None, entity_id=None, description=None):
    """
    Enregistre une action dans le journal d'audit.
    Doit être appelée après les opérations sensibles : connexion, modification
    de patient, suppression, création d'ordonnance, paiement, etc.
    """
    entry = AuditLog(
        created_at=datetime.now(timezone.utc),
        user_id=current_user.id if current_user.is_authenticated else None,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        description=description,
        ip_address=request.remote_addr if request else None,
    )
    db.session.add(entry)
