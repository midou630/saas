# Système de Gestion de Cabinet Médical (SaaS)

Application web professionnelle de gestion de cabinets médicaux, construite avec
Flask, SQLAlchemy et Jinja2. Interface entièrement en **français**.

## 🧱 Stack technique

- **Backend** : Python, Flask, SQLAlchemy (ORM), Flask-Login, Flask-Migrate
- **Base de données** : SQLite (développement) / PostgreSQL (production)
- **Frontend** : HTML, CSS, JavaScript natif (aucun framework front-end)
- **PDF** : WeasyPrint (ordonnances, demandes, rapports)
- **Excel** : openpyxl (export des rapports)

## 🚀 Installation

### 1. Créer un environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate   # Sous Windows : venv\Scripts\activate
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer les variables d'environnement

```bash
cp .env.example .env
# Modifiez ensuite le fichier .env avec vos propres valeurs
```

### 4. Initialiser la base de données

```bash
export FLASK_APP=run.py        # Sous Windows : set FLASK_APP=run.py
flask db init
flask db migrate -m "Initialisation de la base de données"
flask db upgrade
```

### 5. Créer le compte administrateur

```bash
flask creer-admin
```

### 6. Lancer l'application

```bash
flask run
# ou : python run.py
```

L'application est accessible sur `http://127.0.0.1:5000`.

## 📦 Déploiement en production

1. Définissez `FLASK_ENV=production` et une variable `DATABASE_URL` PostgreSQL.
2. Définissez une `SECRET_KEY` robuste (obligatoire, sinon le démarrage échoue).
3. Lancez l'application avec Gunicorn :

```bash
gunicorn -w 4 -b 0.0.0.0:8000 "run:app"
```

4. Placez l'application derrière un reverse proxy (Nginx) avec HTTPS activé,
   puis définissez `SESSION_COOKIE_SECURE=True`.

## 🗂️ Structure du projet

```
clinic_saas/
├── config.py                 # Configuration (dev / test / production)
├── run.py                    # Point d'entrée de l'application
├── requirements.txt
├── app/
│   ├── __init__.py           # Fabrique de l'application (Application Factory)
│   ├── extensions.py         # Instances des extensions Flask
│   ├── models/                # Modèles SQLAlchemy
│   ├── auth/                  # Authentification
│   ├── dashboard/              # Tableau de bord
│   ├── patients/                # Gestion des patients
│   ├── consultations/           # Gestion des visites médicales
│   ├── prescriptions/            # Ordonnances (+ PDF)
│   ├── lab_tests/                # Demandes d'analyses (+ PDF)
│   ├── radiology/                 # Demandes de radiologie (+ PDF)
│   ├── inventory/                  # Gestion du stock
│   ├── payments/                    # Suivi des paiements
│   ├── reports/                      # Rapports (PDF / Excel)
│   ├── users/                         # Gestion des utilisateurs (admin)
│   ├── notifications/                  # Alertes système
│   ├── utils/                            # Fonctions utilitaires transverses
│   ├── static/                            # CSS / JS
│   └── templates/                          # Vues Jinja2
```

## 🔐 Sécurité intégrée

- Hachage des mots de passe (PBKDF2-SHA256, 600 000 itérations)
- Protection CSRF sur tous les formulaires
- Verrouillage de compte après 5 tentatives de connexion échouées
- En-têtes de sécurité HTTP (CSP, HSTS en production) via Flask-Talisman
- Limitation du débit sur la page de connexion (anti brute-force)
- Suppression douce (Soft Delete) : aucune donnée patient n'est jamais perdue
- Journal d'audit complet des actions sensibles

## 👥 Rôles utilisateurs

| Rôle | Permissions principales |
|---|---|
| Administrateur | Accès complet, gestion des utilisateurs, journal d'audit |
| Docteur | Patients, consultations, ordonnances, analyses/radiologie, rapports |
| Secrétaire | Patients, paiements, consultations |
| Assistant(e) | Patients, analyses/radiologie |

## 💾 Sauvegarde

En développement (SQLite) :

```bash
flask sauvegarder-db
```

En production (PostgreSQL), utilisez `pg_dump` planifié via une tâche cron.

## 📄 Licence

Propriétaire — Tous droits réservés.
