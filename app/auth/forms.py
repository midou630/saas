"""
Formulaires liés à l'authentification.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class LoginForm(FlaskForm):
    email = StringField(
        "Adresse e-mail",
        validators=[DataRequired(message="L'adresse e-mail est obligatoire."), Email(message="Adresse e-mail invalide.")],
    )
    password = PasswordField(
        "Mot de passe", validators=[DataRequired(message="Le mot de passe est obligatoire.")]
    )
    remember_me = BooleanField("Se souvenir de moi")
    submit = SubmitField("Se connecter")


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField(
        "Mot de passe actuel", validators=[DataRequired(message="Champ obligatoire.")]
    )
    new_password = PasswordField(
        "Nouveau mot de passe",
        validators=[
            DataRequired(message="Champ obligatoire."),
            Length(min=8, message="Le mot de passe doit contenir au moins 8 caractères."),
        ],
    )
    confirm_password = PasswordField(
        "Confirmer le nouveau mot de passe",
        validators=[
            DataRequired(message="Champ obligatoire."),
            EqualTo("new_password", message="Les mots de passe ne correspondent pas."),
        ],
    )
    submit = SubmitField("Modifier le mot de passe")
