"""
Routes de gestion des notifications utilisateur.
"""
from flask import Blueprint, redirect, url_for, request
from flask_login import login_required, current_user

from app.extensions import db
from app.models.notification import Notification

notifications_bp = Blueprint("notifications", __name__, template_folder="../templates/notifications")


@notifications_bp.route("/<int:notification_id>/lu", methods=["POST"])
@login_required
def mark_as_read(notification_id):
    notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
    notification.is_read = True
    db.session.commit()
    return redirect(request.referrer or url_for("dashboard.index"))


@notifications_bp.route("/tout-marquer-lu", methods=["POST"])
@login_required
def mark_all_as_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return redirect(request.referrer or url_for("dashboard.index"))
