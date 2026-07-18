"""
Formulaires liés aux ordonnances médicales.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FieldList, FormField, SubmitField
from wtforms.validators import DataRequired, Optional, Length


class PrescriptionItemForm(FlaskForm):
    class Meta:
        csrf = False

    medication_name = StringField(
        "Médicament", validators=[DataRequired(message="Le nom du médicament est obligatoire."), Length(max=200)]
    )
    dosage = StringField("Dosage", validators=[Optional(), Length(max=120)])
    frequency = StringField("Fréquence", validators=[Optional(), Length(max=120)])
    duration = StringField("Durée", validators=[Optional(), Length(max=120)])
    instructions = StringField("Instructions particulières", validators=[Optional(), Length(max=255)])


class PrescriptionForm(FlaskForm):
    additional_instructions = TextAreaField("Instructions générales", validators=[Optional()])
    items = FieldList(FormField(PrescriptionItemForm), min_entries=1)
    submit = SubmitField("Enregistrer l'ordonnance")
