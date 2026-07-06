from domain_layer import *
from repo_interface import *

class CartService:
    def __init__(self, repo:CartRepo):
        self.repository = repo
    def add_product(self,customer_id:int,product:Product,qty:int) -> None:

        cart = self.repository.get_by_customer_id(customer_id)
        cart.add_item(product, qty)
        self.repository.save(cart)
        print(f"Customer {customer_id} added Product {product.name} | Quantity : {qty} | to cart")
        print(f"Total Price of cart for customer {customer_id} is {cart.total_price()}")
    def remove_product(self, customer_id:int,product_id:int) -> None:
        cart = self.repository.get_by_customer_id(customer_id)
        cart.remove_item(product_id)
        self.repository.save(cart)
        print(f"Removed Product {product_id} from cart for customer {cart.customer_id}")