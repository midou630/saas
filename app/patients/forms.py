"""
Formulaires liés à la gestion des patients.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, Email

from app.models.patient import Gender


class PatientForm(FlaskForm):
    first_name = StringField(
        "Prénom", validators=[DataRequired(message="Le prénom est obligatoire."), Length(max=100)]
    )
    last_name = StringField(
        "Nom", validators=[DataRequired(message="Le nom est obligatoire."), Length(max=100)]
    )
    birth_date = DateField("Date de naissance", validators=[Optional()], format="%Y-%m-%d")
    gender = SelectField(
        "Genre",
        choices=[(Gender.MALE.value, "Homme"), (Gender.FEMALE.value, "Femme")],
        validators=[DataRequired(message="Le genre est obligatoire.")],
    )
    phone = StringField("Téléphone", validators=[Optional(), Length(max=30)])
    email = StringField("E-mail", validators=[Optional(), Email(message="E-mail invalide."), Length(max=255)])
    address = StringField("Adresse", validators=[Optional(), Length(max=255)])
    city = StringField("Ville", validators=[Optional(), Length(max=100)])

    emergency_contact_name = StringField("Nom du contact d'urgence", validators=[Optional(), Length(max=150)])
    emergency_contact_phone = StringField("Téléphone du contact d'urgence", validators=[Optional(), Length(max=30)])

    blood_type = StringField("Groupe sanguin", validators=[Optional(), Length(max=5)])
    allergies = TextAreaField("Allergies", validators=[Optional()])
    chronic_diseases = TextAreaField("Maladies chroniques", validators=[Optional()])
    past_surgeries = TextAreaField("Antécédents chirurgicaux", validators=[Optional()])
    general_notes = TextAreaField("Notes générales", validators=[Optional()])

    submit = SubmitField("Enregistrer")


class PatientDocumentForm(FlaskForm):
    description = StringField("Description du document", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Téléverser")
