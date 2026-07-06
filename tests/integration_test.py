import unittest
import decimal
import sys
import os

# Ensure package root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from shopping_cart.database import Base
from shopping_cart.domain_layer import Product
from shopping_cart.repo_interface import SqliteCartRepo, SqliteProductRepo
from implementations.service_layer import CartService

class IntegrationTestCartService(unittest.TestCase):
    def setUp(self):
        # Setup temporary in-memory database
        self.engine = create_engine("sqlite:///:memory:")
        self.SessionLocal = sessionmaker(bind=self.engine)
        Base.metadata.create_all(bind=self.engine)
        
        # Instantiate repositories with the in-memory session factory
        self.cart_repo = SqliteCartRepo(db_session_factory=self.SessionLocal)
        self.product_repo = SqliteProductRepo(db_session_factory=self.SessionLocal)
        self.service = CartService(self.cart_repo, self.product_repo)

    def tearDown(self):
        # Drop all tables
        Base.metadata.drop_all(bind=self.engine)

    def test_full_cart_workflow(self):
        # Arrange
        mouse = Product(1, "Mouse", decimal.Decimal("50.00"), 100)
        keyboard = Product(2, "Keyboard", decimal.Decimal("100.00"), 50)
        
        # Seed the catalog first (owner putting products on shop)
        self.product_repo.save(mouse)
        self.product_repo.save(keyboard)

        # Act
        self.service.add_product(customer_id=99, product_id=1, qty=3)
        self.service.add_product(customer_id=99, product_id=2, qty=2)
        
        # Verify
        cart = self.cart_repo.get_by_customer_id(99)
        self.assertEqual(len(cart.items), 2)
        self.assertEqual(cart.total_price(), decimal.Decimal("350.00"))

        # Act: remove product 1 (Mouse)
        self.service.remove_product(customer_id=99, product_id=1)
        cart = self.cart_repo.get_by_customer_id(99)

        # Assert
        self.assertEqual(len(cart.items), 1)
        self.assertEqual(cart.items[0].product.id, 2)
        self.assertEqual(cart.total_price(), decimal.Decimal("200.00"))