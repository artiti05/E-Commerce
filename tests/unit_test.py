import unittest
import decimal
import sys
import os

# Ensure package root is in sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shopping_cart.repo_interface import CartRepo, ProductRepo
from implementations.service_layer import CartService
from shopping_cart.domain_layer import Cart, Product, CartItem

# A fake Cart repository just for testing the service logic
class MockCartRepo(CartRepo):
    def __init__(self):
        self.mock_cart = Cart(customer_id=1)
        self.save_was_called = False
    
    def get_by_customer_id(self, customer_id: int) -> Cart: 
        return self.mock_cart

    def save(self, cart: Cart) -> None:
        self.save_was_called = True
        self.mock_cart = cart

# A fake Product repository for testing catalog lookup
class MockProductRepo(ProductRepo):
    def __init__(self):
        self.products = {}

    def save(self, product: Product) -> None:
        self.products[product.id] = product

    def get_by_id(self, product_id: int) -> Product:
        return self.products.get(product_id)

    def get_all(self) -> list:
        return list(self.products.values())

    def delete(self, product_id: int) -> None:
        self.products.pop(product_id, None)


class UnitTestCartService(unittest.TestCase):
    def setUp(self):
        self.mock_cart_repo = MockCartRepo()
        self.mock_product_repo = MockProductRepo()
        self.service = CartService(self.mock_cart_repo, self.mock_product_repo)
        
        # Create standard test products and save to fake catalog
        self.laptop = Product(product_id=101, name="Laptop", price=decimal.Decimal("1000.00"), qty=5)
        self.mock_product_repo.save(self.laptop)

    def test_add_product_calculates_total_correctly(self):
        # Act
        self.service.add_product(customer_id=1, product_id=101, qty=2)

        # Assert
        self.assertEqual(self.mock_cart_repo.mock_cart.total_price(), decimal.Decimal("2000.00"))
        self.assertTrue(self.mock_cart_repo.save_was_called)

    def test_add_product_exceeding_stock_raises_value_error(self):
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.service.add_product(customer_id=1, product_id=101, qty=6)
        self.assertIn("Cannot add more items than available in stock", str(context.exception))

    def test_add_product_invalid_quantity_raises_value_error(self):
        # Act & Assert
        with self.assertRaises(ValueError):
            self.service.add_product(customer_id=1, product_id=101, qty=0)

    def test_add_nonexistent_product_raises_value_error(self):
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            self.service.add_product(customer_id=1, product_id=999, qty=1)
        self.assertIn("Product with ID 999 not found in catalog", str(context.exception))

    def test_remove_product_removes_from_cart(self):
        # Arrange
        self.service.add_product(customer_id=1, product_id=101, qty=2)
        self.assertEqual(len(self.mock_cart_repo.mock_cart.items), 1)

        # Act
        self.service.remove_product(customer_id=1, product_id=101)

        # Assert
        self.assertEqual(len(self.mock_cart_repo.mock_cart.items), 0)
        self.assertEqual(self.mock_cart_repo.mock_cart.total_price(), decimal.Decimal("0.00"))
        self.assertTrue(self.mock_cart_repo.save_was_called)

    def test_negative_product_price_raises_value_error(self):
        # Act & Assert
        with self.assertRaises(ValueError) as context:
            Product(product_id=102, name="Phone", price=decimal.Decimal("-100.00"), qty=5)
        self.assertIn("Price cannot be negative", str(context.exception))