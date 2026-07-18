"""
Formulaires liés à la gestion du stock : produits, catégories, fournisseurs.
"""
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, DateField, SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Optional, NumberRange, Length


class ProductForm(FlaskForm):
    name = StringField(
        "Nom du produit", validators=[DataRequired(message="Le nom du produit est obligatoire."), Length(max=200)]
    )
    sku = StringField("Référence (SKU)", validators=[Optional(), Length(max=60)])
    category_id = SelectField("Catégorie", coerce=int, validators=[Optional()])
    supplier_id = SelectField("Fournisseur", coerce=int, validators=[Optional()])
    unit = StringField("Unité", default="unité", validators=[DataRequired(), Length(max=30)])
    quantity_in_stock = IntegerField(
        "Quantité en stock", validators=[DataRequired(), NumberRange(min=0)], default=0
    )
    minimum_stock_threshold = IntegerField(
        "Seuil d'alerte", validators=[DataRequired(), NumberRange(min=0)], default=5
    )
    unit_purchase_price = DecimalField("Prix d'achat unitaire (DA)", validators=[Optional(), NumberRange(min=0)], places=2)
    unit_sale_price = DecimalField("Prix de vente unitaire (DA)", validators=[Optional(), NumberRange(min=0)], places=2)
    expiration_date = DateField("Date de péremption", validators=[Optional()], format="%Y-%m-%d")
    submit = SubmitField("Enregistrer le produit")


class CategoryForm(FlaskForm):
    name = StringField("Nom de la catégorie", validators=[DataRequired(), Length(max=120)])
    description = StringField("Description", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Enregistrer")


class SupplierForm(FlaskForm):
    name = StringField("Nom du fournisseur", validators=[DataRequired(), Length(max=150)])
    contact_name = StringField("Nom du contact", validators=[Optional(), Length(max=150)])
    phone = StringField("Téléphone", validators=[Optional(), Length(max=30)])
    email = StringField("E-mail", validators=[Optional(), Length(max=255)])
    address = StringField("Adresse", validators=[Optional(), Length(max=255)])
    notes = TextAreaField("Notes", validators=[Optional()])
    submit = SubmitField("Enregistrer")


class StockMovementForm(FlaskForm):
    movement_type = SelectField(
        "Type de mouvement",
        choices=[("entree", "Entrée"), ("sortie", "Sortie"), ("ajustement", "Ajustement")],
        validators=[DataRequired()],
    )
    quantity = IntegerField("Quantité", validators=[DataRequired(), NumberRange(min=1)])
    reason = StringField("Motif", validators=[Optional(), Length(max=255)])
    submit = SubmitField("Enregistrer le mouvement")
