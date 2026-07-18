"""
Routes de gestion du stock : produits, catégories, fournisseurs, mouvements.
"""
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import login_required, current_user

from app.extensions import db
from app.models.inventory import Product, ProductCategory, Supplier, StockMovement, StockMovementType
from app.inventory.forms import ProductForm, CategoryForm, SupplierForm, StockMovementForm
from app.utils.decorators import permission_required
from app.utils.audit import log_action

inventory_bp = Blueprint("inventory", __name__, template_folder="../templates/inventory")


def _populate_choices(form):
    form.category_id.choices = [(0, "— Aucune catégorie —")] + [
        (c.id, c.name) for c in ProductCategory.query.filter_by(is_deleted=False).order_by(ProductCategory.name).all()
    ]
    form.supplier_id.choices = [(0, "— Aucun fournisseur —")] + [
        (s.id, s.name) for s in Supplier.query.filter_by(is_deleted=False).order_by(Supplier.name).all()
    ]


@inventory_bp.route("/")
@login_required
@permission_required("manage_inventory")
def list_products():
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get("q", "").strip()
    low_stock_only = request.args.get("low_stock") == "1"

    query = Product.query.filter_by(is_deleted=False)
    if search_query:
        query = query.filter(Product.name.ilike(f"%{search_query}%"))
    if low_stock_only:
        query = query.filter(Product.quantity_in_stock <= Product.minimum_stock_threshold)

    pagination = query.order_by(Product.name).paginate(
        page=page, per_page=current_app.config["INVENTORY_PER_PAGE"], error_out=False
    )
    return render_template(
        "inventory/list.html", products=pagination.items, pagination=pagination,
        search_query=search_query, low_stock_only=low_stock_only,
    )


@inventory_bp.route("/nouveau", methods=["GET", "POST"])
@login_required
@permission_required("manage_inventory")
def create_product():
    form = ProductForm()
    _populate_choices(form)

    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            sku=form.sku.data or None,
            category_id=form.category_id.data or None,
            supplier_id=form.supplier_id.data or None,
            unit=form.unit.data,
            quantity_in_stock=form.quantity_in_stock.data,
            minimum_stock_threshold=form.minimum_stock_threshold.data,
            unit_purchase_price=form.unit_purchase_price.data,
            unit_sale_price=form.unit_sale_price.data,
            expiration_date=form.expiration_date.data,
        )
        db.session.add(product)
        db.session.flush()
        log_action("creation_produit", entity_type="Product", entity_id=product.id, description=product.name)
        db.session.commit()
        flash("Produit ajouté avec succès.", "success")
        return redirect(url_for("inventory.list_products"))

    return render_template("inventory/form.html", form=form, is_edit=False)


@inventory_bp.route("/<int:product_id>/modifier", methods=["GET", "POST"])
@login_required
@permission_required("manage_inventory")
def edit_product(product_id):
    product = Product.query.filter_by(id=product_id, is_deleted=False).first_or_404()
    form = ProductForm(obj=product)
    _populate_choices(form)
    if request.method == "GET":
        form.category_id.data = product.category_id or 0
        form.supplier_id.data = product.supplier_id or 0

    if form.validate_on_submit():
        form.populate_obj(product)
        product.category_id = form.category_id.data or None
        product.supplier_id = form.supplier_id.data or None
        log_action("modification_produit", entity_type="Product", entity_id=product.id)
        db.session.commit()
        flash("Produit mis à jour avec succès.", "success")
        return redirect(url_for("inventory.list_products"))

    return render_template("inventory/form.html", form=form, is_edit=True, product=product)


@inventory_bp.route("/<int:product_id>/supprimer", methods=["POST"])
@login_required
@permission_required("manage_inventory")
def delete_product(product_id):
    product = Product.query.filter_by(id=product_id, is_deleted=False).first_or_404()
    product.soft_delete()
    log_action("suppression_produit", entity_type="Product", entity_id=product.id)
    db.session.commit()
    flash("Produit archivé avec succès.", "success")
    return redirect(url_for("inventory.list_products"))


@inventory_bp.route("/<int:product_id>/mouvement", methods=["GET", "POST"])
@login_required
@permission_required("manage_inventory")
def add_movement(product_id):
    product = Product.query.filter_by(id=product_id, is_deleted=False).first_or_404()
    form = StockMovementForm()

    if form.validate_on_submit():
        movement_type = form.movement_type.data
        quantity = form.quantity.data

        if movement_type == "sortie" and quantity > product.quantity_in_stock:
            flash("Quantité insuffisante en stock pour cette sortie.", "danger")
        else:
            movement = StockMovement(
                product_id=product.id,
                movement_type=movement_type,
                quantity=quantity,
                reason=form.reason.data,
                performed_by_id=current_user.id,
            )
            db.session.add(movement)

            if movement_type == "entree":
                product.quantity_in_stock += quantity
            elif movement_type == "sortie":
                product.quantity_in_stock -= quantity
            else:
                product.quantity_in_stock = quantity

            log_action("mouvement_stock", entity_type="Product", entity_id=product.id,
                        description=f"{movement_type} de {quantity} {product.unit}")
            db.session.commit()
            flash("Mouvement de stock enregistré avec succès.", "success")
            return redirect(url_for("inventory.list_products"))

    return render_template("inventory/movement_form.html", form=form, product=product)


# ---- Catégories ----
@inventory_bp.route("/categories", methods=["GET", "POST"])
@login_required
@permission_required("manage_inventory")
def manage_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = ProductCategory(name=form.name.data, description=form.description.data)
        db.session.add(category)
        log_action("creation_categorie", entity_type="ProductCategory", description=category.name)
        db.session.commit()
        flash("Catégorie créée avec succès.", "success")
        return redirect(url_for("inventory.manage_categories"))

    categories = ProductCategory.query.filter_by(is_deleted=False).order_by(ProductCategory.name).all()
    return render_template("inventory/categories.html", form=form, categories=categories)


# ---- Fournisseurs ----
@inventory_bp.route("/fournisseurs", methods=["GET", "POST"])
@login_required
@permission_required("manage_inventory")
def manage_suppliers():
    form = SupplierForm()
    if form.validate_on_submit():
        supplier = Supplier(
            name=form.name.data, contact_name=form.contact_name.data, phone=form.phone.data,
            email=form.email.data, address=form.address.data, notes=form.notes.data,
        )
        db.session.add(supplier)
        log_action("creation_fournisseur", entity_type="Supplier", description=supplier.name)
        db.session.commit()
        flash("Fournisseur créé avec succès.", "success")
        return redirect(url_for("inventory.manage_suppliers"))

    suppliers = Supplier.query.filter_by(is_deleted=False).order_by(Supplier.name).all()
    return render_template("inventory/suppliers.html", form=form, suppliers=suppliers)
