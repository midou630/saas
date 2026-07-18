"""
Modèle AuditLog - trace toutes les actions sensibles effectuées dans le système.
"""
from app.extensions import db


class AuditLog(db.Model):
    __tablename__ = "audit_logs"

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    user = db.relationship("User", foreign_keys=[user_id])

    action = db.Column(db.String(100), nullable=False, index=True)
    entity_type = db.Column(db.String(80), nullable=True, index=True)
    entity_id = db.Column(db.Integer, nullable=True)
    description = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)

    def __repr__(self):
        return f"<AuditLog {self.action} par user={self.user_id}>"
