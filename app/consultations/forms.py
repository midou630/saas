"""
Formulaires liés aux consultations médicales.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, TextAreaField, DecimalField, SelectField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

from app.models.consultation import ConsultationStatus


class ConsultationForm(FlaskForm):
    visit_date = DateTimeField(
        "Date et heure de la visite",
        validators=[DataRequired(message="La date est obligatoire.")],
        format="%Y-%m-%dT%H:%M",
    )
    reason = StringField("Motif de la visite", validators=[Optional(), Length(max=255)])
    diagnosis = TextAreaField("Diagnostic", validators=[Optional()])
    treatment = TextAreaField("Traitement", validators=[Optional()])
    notes = TextAreaField("Notes", validators=[Optional()])
    status = SelectField(
        "Statut",
        choices=[(s.value, s.value) for s in ConsultationStatus],
        validators=[DataRequired()],
    )
    consultation_price = DecimalField(
        "Prix de la consultation (DA)",
        validators=[DataRequired(message="Le prix est obligatoire."), NumberRange(min=0)],
        places=2,
    )
    submit = SubmitField("Enregistrer la consultation")


class QuickPaymentForm(FlaskForm):
    amount = DecimalField(
        "Montant reçu (DA)", validators=[DataRequired(message="Le montant est obligatoire."), NumberRange(min=0.01)], places=2
    )
    method = SelectField(
        "Méthode de paiement",
        choices=[
            ("especes", "Espèces"),
            ("carte", "Carte bancaire"),
            ("virement", "Virement"),
            ("cheque", "Chèque"),
            ("autre", "Autre"),
        ],
    )
    note = StringField("Note", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Enregistrer le paiement")
