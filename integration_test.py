import unittest
from repo_interface import CartRepo
from service_layer import CartService
from domain_layer import Cart,Product
from repo_interface import InMemoCartRepo

class IntegrationTestCartService(unittest.TestCase):
    def test_full_cart_workflow(self):
        # Arrange
        repo = InMemoCartRepo()
        service = CartService(repo)

        mouse = Product(1, "Mouse", 50, 100)
        keyboard = Product(2,"Keyboard", 100, 50)

        # Act
        service.add_item(customer_id=99, product=mouse, qty=3)
        service.add_item(customer_id=99, product=keyboard, qty=2)
        
        service.remove_item(customer_id=99, product_id=1)
        cart = repo.get_by_customer_id(99)

        # Assert
        self.assertEqual(len(cart.items), 1)
        self.assertEqual(cart.items[0].product.id, 2)
        self.assertEqual(cart.total_price, 200)