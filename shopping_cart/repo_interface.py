import json
import decimal
import os
import logging
from abc import ABC, abstractmethod
from typing import List

from shopping_cart.domain_layer import Cart, Product, CartItem
from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship, joinedload
from shopping_cart.database import Base, engine, SessionLocal

logger = logging.getLogger("app.repository")

class CartRepo(ABC):
    @abstractmethod
    def save(self, cart: Cart) -> None:
        pass

    @abstractmethod
    def get_by_customer_id(self, customer_id: int) -> Cart:
        pass


class ProductRepo(ABC):
    @abstractmethod
    def save(self, product: Product) -> None:
        pass

    @abstractmethod
    def get_by_id(self, product_id: int) -> Product:
        pass

    @abstractmethod
    def get_all(self) -> List[Product]:
        pass

    @abstractmethod
    def delete(self, product_id: int) -> None:
        pass


# ==========================================
# JSON Implementation
# ==========================================
class JsonCartRepo(CartRepo):
    def __init__(self, json_file: str = "Carts.json"):
        self.file_path = json_file
        if not os.path.exists(self.file_path):
            self._write_file()

    def _write_file(self) -> None:
        with open(self.file_path, 'w') as f:
            json.dump({}, f)

    def _read_file(self) -> dict:
        with open(self.file_path, 'r') as f:
            return json.load(f)

    def save(self, cart: Cart) -> None:
        logger.debug(f"[JSON] Saving cart for customer_id {cart.customer_id}")
        data = self._read_file()
        data[str(cart.customer_id)] = {
            "customer_id": cart.customer_id,
            "items": [
                {
                    "product": {
                        "id": item.product.id,
                        "name": item.product.name,
                        "price": str(item.product.price),
                        "qty": item.product.qty
                    },
                    "qty": item.qty
                }
                for item in cart.items
            ]
        }
        data[str(cart.customer_id)]["total_price"] = str(cart.total_price())
        
        # Write to JSON file
        with open(self.file_path, 'w') as f:
            json.dump(data, f, indent=4)
        logger.info(f"[Database Log] Cart saved for Customer {cart.customer_id}")

    def get_by_customer_id(self, customer_id: int) -> Cart:
        logger.debug(f"[JSON] Fetching cart for customer_id {customer_id}")
        data = self._read_file()
        if str(customer_id) in data:
            cart_data = data[str(customer_id)]
            items = []
            for item_data in cart_data["items"]:
                product = Product(
                    product_id=item_data["product"]["id"],
                    name=item_data["product"]["name"],
                    price=decimal.Decimal(item_data["product"]["price"]),
                    qty=item_data["product"]["qty"]
                )
                items.append(CartItem(product=product, qty=item_data["qty"]))
            return Cart(customer_id=cart_data["customer_id"], items=items)
        return Cart(customer_id)


# ==========================================
# SQLite ORM Implementation
# ==========================================
class DbProduct(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2, asdecimal=True), nullable=False)
    qty = Column(Integer, nullable=False)  # stock quantity


class DbCart(Base):
    __tablename__ = "carts"

    customer_id = Column(Integer, primary_key=True)
    items = relationship("DbCartItem", back_populates="cart", cascade="all, delete-orphan")


class DbCartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.customer_id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)

    cart = relationship("DbCart", back_populates="items")
    product = relationship("DbProduct")


# Initialize database tables
Base.metadata.create_all(bind=engine)


class SqliteCartRepo(CartRepo):
    def __init__(self, db_session_factory=None):
        self.session_factory = db_session_factory or SessionLocal

    def save(self, cart: Cart) -> None:
        logger.debug(f"[SQLite] Saving cart for customer_id {cart.customer_id}")
        session = self.session_factory()
        try:
            # 1. Ensure DbCart exists
            db_cart = session.query(DbCart).filter_by(customer_id=cart.customer_id).first()
            if not db_cart:
                db_cart = DbCart(customer_id=cart.customer_id)
                session.add(db_cart)
                session.flush()

            # 2. Reconcile Cart Items
            # Delete old database items for this cart to prevent duplicates
            session.query(DbCartItem).filter_by(cart_id=cart.customer_id).delete()

            # Add current items, verifying product existence/quantity in DB
            for item in cart.items:
                db_product = session.query(DbProduct).filter_by(id=item.product.id).first()
                if not db_product:
                    # Create product in database if it doesn't exist
                    db_product = DbProduct(
                        id=item.product.id,
                        name=item.product.name,
                        price=item.product.price,
                        qty=item.product.qty
                    )
                    session.add(db_product)
                    session.flush()
                else:
                    # Update stock level in DB
                    db_product.qty = item.product.qty

                db_item = DbCartItem(
                    cart_id=cart.customer_id,
                    product_id=item.product.id,
                    qty=item.qty
                )
                session.add(db_item)

            session.commit()
            logger.info(f"[Database Log] Cart saved successfully in SQLite for Customer {cart.customer_id}")
        except Exception as e:
            session.rollback()
            logger.error(f"[SQLite] Error saving cart for Customer {cart.customer_id}: {str(e)}")
            raise e
        finally:
            session.close()

    def get_by_customer_id(self, customer_id: int) -> Cart:
        logger.debug(f"[SQLite] Fetching cart for customer_id {customer_id}")
        session = self.session_factory()
        try:
            db_cart = (
                session.query(DbCart)
                .options(joinedload(DbCart.items).joinedload(DbCartItem.product))
                .filter_by(customer_id=customer_id)
                .first()
            )
            if not db_cart:
                logger.debug(f"[SQLite] No cart found in DB for customer_id {customer_id}. Creating new empty Cart.")
                return Cart(customer_id=customer_id)

            # Map DbCart to Domain Cart
            domain_items = []
            for db_item in db_cart.items:
                domain_product = Product(
                    product_id=db_item.product.id,
                    name=db_item.product.name,
                    price=db_item.product.price,
                    qty=db_item.product.qty
                )
                domain_items.append(CartItem(product=domain_product, qty=db_item.qty))

            return Cart(customer_id=db_cart.customer_id, items=domain_items)
        except Exception as e:
            logger.error(f"[SQLite] Error fetching cart for Customer {customer_id}: {str(e)}")
            raise e
        finally:
            session.close()


class SqliteProductRepo(ProductRepo):
    def __init__(self, db_session_factory=None):
        self.session_factory = db_session_factory or SessionLocal

    def save(self, product: Product) -> None:
        logger.debug(f"[SQLite] Saving product {product.id} to catalog")
        session = self.session_factory()
        try:
            db_product = session.query(DbProduct).filter_by(id=product.id).first()
            if not db_product:
                db_product = DbProduct(
                    id=product.id,
                    name=product.name,
                    price=product.price,
                    qty=product.qty
                )
                session.add(db_product)
            else:
                db_product.name = product.name
                db_product.price = product.price
                db_product.qty = product.qty
            session.commit()
            logger.info(f"[Database Log] Product {product.id} ({product.name}) saved in database catalog.")
        except Exception as e:
            session.rollback()
            logger.error(f"[SQLite] Error saving product {product.id}: {str(e)}")
            raise e
        finally:
            session.close()

    def get_by_id(self, product_id: int) -> Product:
        logger.debug(f"[SQLite] Fetching product {product_id} from catalog")
        session = self.session_factory()
        try:
            db_product = session.query(DbProduct).filter_by(id=product_id).first()
            if not db_product:
                return None
            return Product(
                product_id=db_product.id,
                name=db_product.name,
                price=db_product.price,
                qty=db_product.qty
            )
        except Exception as e:
            logger.error(f"[SQLite] Error fetching product {product_id}: {str(e)}")
            raise e
        finally:
            session.close()

    def get_all(self) -> List[Product]:
        logger.debug("[SQLite] Fetching all products from catalog")
        session = self.session_factory()
        try:
            db_products = session.query(DbProduct).all()
            return [
                Product(
                    product_id=db_p.id,
                    name=db_p.name,
                    price=db_p.price,
                    qty=db_p.qty
                )
                for db_p in db_products
            ]
        except Exception as e:
            logger.error(f"[SQLite] Error fetching all products: {str(e)}")
            raise e
        finally:
            session.close()

    def delete(self, product_id: int) -> None:
        logger.debug(f"[SQLite] Deleting product {product_id} from catalog")
        session = self.session_factory()
        try:
            session.query(DbCartItem).filter_by(product_id=product_id).delete()
            db_product = session.query(DbProduct).filter_by(id=product_id).first()
            if db_product:
                session.delete(db_product)
                session.commit()
                logger.info(f"[Database Log] Product {product_id} deleted successfully.")
            else:
                logger.warning(f"[SQLite] Product {product_id} not found for deletion.")
        except Exception as e:
            session.rollback()
            logger.error(f"[SQLite] Error deleting product {product_id}: {str(e)}")
            raise e
        finally:
            session.close()