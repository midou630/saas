"""
Décorateurs de contrôle d'accès basés sur les permissions des rôles.
"""
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def permission_required(permission):
    """Vérifie que l'utilisateur connecté possède la permission demandée."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if not current_user.has_permission(permission):
                flash("Vous n'avez pas les droits nécessaires pour accéder à cette page.", "danger")
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator


def roles_required(*allowed_roles):
    """Restreint l'accès à une vue à une liste de rôles précis."""

    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.role not in allowed_roles:
                flash("Accès refusé : rôle insuffisant.", "danger")
                abort(403)
            return view_func(*args, **kwargs)

        return wrapped_view

    return decorator
