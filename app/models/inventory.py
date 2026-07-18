"""
Modèles de gestion du stock : Catégories, Fournisseurs, Produits, Mouvements de stock.
"""
import enum

from app.extensions import db
from app.models.base import TimestampMixin, SoftDeleteMixin, PublicIdMixin


class StockMovementType(str, enum.Enum):
    IN = "entree"
    OUT = "sortie"
    ADJUSTMENT = "ajustement"


STOCK_MOVEMENT_LABELS_FR = {
    StockMovementType.IN: "Entrée",
    StockMovementType.OUT: "Sortie",
    StockMovementType.ADJUSTMENT: "Ajustement",
}


class ProductCategory(TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "product_categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    products = db.relationship("Product", back_populates="category")


class Supplier(TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "suppliers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    contact_name = db.Column(db.String(150), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    email = db.Column(db.String(255), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    products = db.relationship("Product", back_populates="supplier")


class Product(TimestampMixin, SoftDeleteMixin, PublicIdMixin, db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    sku = db.Column(db.String(60), unique=True, nullable=True)

    category_id = db.Column(db.Integer, db.ForeignKey("product_categories.id"), nullable=True)
    category = db.relationship("ProductCategory", back_populates="products")

    supplier_id = db.Column(db.Integer, db.ForeignKey("suppliers.id"), nullable=True)
    supplier = db.relationship("Supplier", back_populates="products")

    unit = db.Column(db.String(30), nullable=False, default="unité")
    quantity_in_stock = db.Column(db.Integer, nullable=False, default=0)
    minimum_stock_threshold = db.Column(db.Integer, nullable=False, default=5)
    unit_purchase_price = db.Column(db.Numeric(10, 2), nullable=True)
    unit_sale_price = db.Column(db.Numeric(10, 2), nullable=True)
    expiration_date = db.Column(db.Date, nullable=True)

    movements = db.relationship(
        "StockMovement", back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (
        db.Index("ix_products_stock_threshold", "quantity_in_stock", "minimum_stock_threshold"),
    )

    @property
    def is_low_stock(self):
        return self.quantity_in_stock <= self.minimum_stock_threshold

    def __repr__(self):
        return f"<Product {self.name} qty={self.quantity_in_stock}>"


class StockMovement(TimestampMixin, db.Model):
    """Journal des mouvements de stock (entrées / sorties / ajustements)."""

    __tablename__ = "stock_movements"

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable=False, index=True)
    product = db.relationship("Product", back_populates="movements")

    movement_type = db.Column(db.Enum(StockMovementType), nullable=False, index=True)
    quantity = db.Column(db.Integer, nullable=False)
    reason = db.Column(db.String(255), nullable=True)

    performed_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    performed_by = db.relationship("User", foreign_keys=[performed_by_id])

    @property
    def movement_type_label(self):
        return STOCK_MOVEMENT_LABELS_FR.get(self.movement_type, self.movement_type.value)
