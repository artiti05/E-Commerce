from domain_layer import Product,CartItem
from repo_interface import CartRepo
class CartService:
    def __init__(self, repo:CartRepo):
        self.repository = repo
    def add_item(self,customer_id:int,product:Product,qty:int) -> None:

        cart = self.repository.get_by_customer_id(customer_id)

        existing_item = next((item for item in cart.items if item.product.id == product.id),None)

        if existing_item:
            existing_item.qty += qty
        else:
            cart.items.append(CartItem(product,qty))

        cart.total_price = sum(item.get_subtotal() for item in cart.items)

        self.repository.save(cart)
    def remove_item(self, customer_id:int,product_id:int) -> None:
        cart = self.repository.get_by_customer_id(customer_id)
        cart.items = [item for item in cart.items if item.product.id != product_id]
        cart.total_price = sum(item.get_subtotal() for item in cart.items)
        self.repository.save(cart)
