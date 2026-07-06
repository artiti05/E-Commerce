import decimal
import logging
from typing import List
from shopping_cart.domain_layer import Product
from shopping_cart.repo_interface import ProductRepo

logger = logging.getLogger("app.service")

class ProductService:
    def __init__(self, repo: ProductRepo):
        self.repository = repo

    def add_product_to_catalog(self, product_id: int, name: str, price: decimal.Decimal, stock_qty: int) -> None:
        logger.debug(f"Admin action: adding product {product_id} ({name}) to catalog")
        try:
            # Domain model validation checks are run during instantiation
            product = Product(
                product_id=product_id,
                name=name,
                price=price,
                qty=stock_qty
            )
            self.repository.save(product)
            logger.info(f"[Admin Log] Added Product {product_id} ({name}) with price ${price} and stock {stock_qty} to the catalog.")
        except ValueError as ve:
            logger.warning(f"Business rule validation failed for new product {product_id}: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error in add_product_to_catalog: {str(e)}", exc_info=True)
            raise e

    def update_stock(self, product_id: int, qty: int) -> None:
        logger.debug(f"Admin action: updating stock of product {product_id} with adjustment {qty}")
        try:
            product = self.repository.get_by_id(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found in catalog.")
            
            new_qty = product.qty + qty
            if new_qty < 0:
                raise ValueError(f"Stock quantity cannot drop below zero. Current: {product.qty}, Adjustment: {qty}")
            
            product.qty = new_qty
            self.repository.save(product)
            logger.info(f"[Admin Log] Product {product_id} ({product.name}) stock updated. New stock level: {product.qty}")
        except ValueError as ve:
            logger.warning(f"Business rule validation failed for update_stock: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error in update_stock: {str(e)}", exc_info=True)
            raise e

    def remove_product_from_catalog(self, product_id: int) -> None:
        logger.debug(f"Admin action: removing product {product_id} from catalog")
        try:
            self.repository.delete(product_id)
            logger.info(f"[Admin Log] Product {product_id} removed from database catalog.")
        except Exception as e:
            logger.error(f"Unexpected error in remove_product_from_catalog: {str(e)}", exc_info=True)
            raise e

    def get_catalog(self) -> List[Product]:
        logger.debug("Fetching catalog list")
        try:
            return self.repository.get_all()
        except Exception as e:
            logger.error(f"Unexpected error fetching catalog: {str(e)}", exc_info=True)
            raise e
