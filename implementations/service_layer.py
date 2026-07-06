import logging
from shopping_cart.domain_layer import Product
from shopping_cart.repo_interface import CartRepo, ProductRepo

logger = logging.getLogger("app.service")

class CartService:
    def __init__(self, cart_repo: CartRepo, product_repo: ProductRepo):
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def add_product(self, customer_id: int, product_id: int, qty: int) -> None:
        logger.debug(f"Entering add_product: customer_id={customer_id}, product_id={product_id}, qty={qty}")
        try:
            # 1. Fetch official product details from database catalog
            product = self.product_repo.get_by_id(product_id)
            if not product:
                raise ValueError(f"Product with ID {product_id} not found in catalog.")
            
            # 2. Get or create the customer's cart
            cart = self.cart_repo.get_by_customer_id(customer_id)
            
            # 3. Add item and validate stock constraints in the Domain entity
            cart.add_item(product, qty)
            
            # 4. Save updated cart state
            self.cart_repo.save(cart)
            
            logger.info(f"Customer {customer_id} successfully added Product {product.name} (Qty: {qty}) to cart.")
            logger.debug(f"Current cart total price for customer {customer_id} is ${cart.total_price()}")
        except ValueError as ve:
            logger.warning(f"Business rule violation in add_product: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error in add_product: {str(e)}", exc_info=True)
            raise e

    def remove_product(self, customer_id: int, product_id: int) -> None:
        logger.debug(f"Entering remove_product: customer_id={customer_id}, product_id={product_id}")
        try:
            cart = self.cart_repo.get_by_customer_id(customer_id)
            
            # Delegate item removal to domain model Cart
            cart.remove_item(product_id)
            
            # Save updated cart state
            self.cart_repo.save(cart)
            
            logger.info(f"Customer {customer_id} successfully removed Product {product_id} from cart.")
            logger.debug(f"Current cart total price for customer {customer_id} is ${cart.total_price()}")
        except ValueError as ve:
            logger.warning(f"Business rule violation in remove_product: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Unexpected error in remove_product: {str(e)}", exc_info=True)
            raise e