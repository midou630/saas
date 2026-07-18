"""
Fonctions utilitaires génériques : téléversement sécurisé de fichiers,
formatage de montants, etc.
"""
import os
import uuid

from flask import current_app
from werkzeug.utils import secure_filename


def allowed_file(filename, allowed_extensions):
    if "." not in filename:
        return False
    extension = filename.rsplit(".", 1)[1].lower()
    return extension in allowed_extensions


def save_uploaded_file(file_storage, subfolder="documents"):
    """
    Sauvegarde un fichier téléversé de manière sécurisée :
    - Vérifie l'extension autorisée.
    - Génère un nom de fichier unique pour éviter les collisions et
      empêcher toute tentative de path traversal.
    Retourne un tuple (nom_stocke, nom_original, taille_octets) ou None si invalide.
    """
    if not file_storage or file_storage.filename == "":
        return None

    original_filename = secure_filename(file_storage.filename)
    if not allowed_file(original_filename, current_app.config["ALLOWED_DOCUMENT_EXTENSIONS"]):
        return None

    extension = original_filename.rsplit(".", 1)[1].lower()
    stored_filename = f"{uuid.uuid4().hex}.{extension}"

    target_dir = os.path.join(current_app.config["UPLOAD_FOLDER"], subfolder)
    os.makedirs(target_dir, exist_ok=True)

    destination_path = os.path.join(target_dir, stored_filename)
    file_storage.save(destination_path)
    file_size = os.path.getsize(destination_path)

    return {
        "stored_filename": os.path.join(subfolder, stored_filename),
        "original_filename": original_filename,
        "file_size_bytes": file_size,
        "file_type": extension,
    }


def format_currency(amount):
    """Formate un montant en dinars algériens selon la convention française."""
    if amount is None:
        amount = 0
    return f"{amount:,.2f} DA".replace(",", " ").replace(".", ",")
