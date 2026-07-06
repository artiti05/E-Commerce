import decimal
import logging
from implementations.logger_config import setup_logging
from shopping_cart.database import SessionLocal, Base, engine
from shopping_cart.repo_interface import SqliteCartRepo, SqliteProductRepo, DbProduct
from implementations.service_layer import CartService

logger = logging.getLogger("app.main")

def seed_database():
    session = SessionLocal()
    try:
        # Check if products table is empty
        product_count = session.query(DbProduct).count()
        if product_count == 0:
            logger.info("Database empty. Seeding initial products...")
            products = [
                DbProduct(id=1, name="Laptop", price=decimal.Decimal("1200.00"), qty=10),
                DbProduct(id=2, name="Wireless Mouse", price=decimal.Decimal("50.00"), qty=100),
                DbProduct(id=3, name="Mechanical Keyboard", price=decimal.Decimal("150.00"), qty=20)
            ]
            session.add_all(products)
            session.commit()
            logger.info("Database seeded successfully.")
    except Exception as e:
        session.rollback()
        logger.error(f"Error seeding database: {str(e)}")
        raise e
    finally:
        session.close()

def main():
    # Setup standard hierarchical logging
    setup_logging()
    
    logger.info("--- Starting Shopping Cart Application ---")
    
    # Initialize SQLite database schema
    Base.metadata.create_all(bind=engine)
    
    # Seed products if empty
    seed_database()
    
    # Initialize repository and service layers
    cart_repo = SqliteCartRepo()
    product_repo = SqliteProductRepo()
    cart_service = CartService(cart_repo, product_repo)
    
    # Simulation Details
    customer_id = 42
        
    logger.info(f"Simulation: Customer {customer_id} starting shopping session.")
    
    # Action 1: Add items to cart (passing product IDs instead of domain objects)
    cart_service.add_product(customer_id, product_id=1, qty=1)  # Laptop
    cart_service.add_product(customer_id, product_id=2, qty=2)  # Wireless Mouse
    
    # Action 2: Remove mouse from cart
    cart_service.remove_product(customer_id, product_id=2)
    
    # Action 3: Add keyboard
    cart_service.add_product(customer_id, product_id=3, qty=1)  # Mechanical Keyboard
    
    # Final Receipt Output
    final_cart = cart_repo.get_by_customer_id(customer_id)
    print("\n" + "="*40)
    print("           FINAL CHECKOUT RECEIPT")
    print("="*40)
    print(f"Customer ID: {final_cart.customer_id}")
    print("-"*40)
    for item in final_cart.items:
        print(f"- {item.qty}x {item.product.name:<20} @ ${item.product.price:>8} = ${item.get_subtotal():>8}")
    print("-"*40)
    print(f"Grand Total: ${final_cart.total_price():>30}")
    print("="*40 + "\n")

if __name__ == "__main__":
    main()