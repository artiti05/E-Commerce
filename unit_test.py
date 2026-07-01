import unittest
from repo_interface import CartRepo
from service_layer import CartService
from domain_layer import Cart,Product

# A fake repository just for testing the service logic
class MockCartRepo(CartRepo):
    def __init__(self):
        self.mock_cart = Cart(customer_id=1)
        self.save_was_called = False
    
    def get_by_customer_id(self, customer_id:int) -> Cart: 
        return self.mock_cart
    def save(self, cart:Cart) -> None:
        self.save_was_called = True

class UnitTestCartService(unittest.TestCase):
    def test_add_item_calculates_total_correctly(self):
        # Arrange
        mock_repo = MockCartRepo()
        service = CartService(mock_repo)
        laptop = Product(product_id=101, name="Laptop", price=1000.0, qty=5)

        # Act
        service.add_item(customer_id=1, product=laptop, qty=2)

        # Assert
        self.assertEqual(mock_repo.mock_cart.total_price, 2000.0)
        self.assertTrue(mock_repo.save_was_called)

        