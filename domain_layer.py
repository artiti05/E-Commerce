from typing import List
import decimal

class Product:
    def __init__(self, product_id:int, name:str, price:decimal.Decimal,qty:int):
        self.id = product_id
        self.name = name
        if price < 0:
            raise ValueError("Price cannot be negative")
        self.price = price
        self.qty = qty
class CartItem:
    def __init__(self, product:Product,qty:int):
        if qty <= 0:
            raise ValueError("Quantity must be greater than zero")
        self.product = product
        self.qty = qty
    def get_subtotal(self) ->decimal.Decimal:
        return self.product.price * self.qty 

class Cart:
    def __init__(self, customer_id:int):
        self.customer_id = customer_id
        self.items:List[CartItem] = []
    def total_price(self) -> decimal.Decimal:
        return sum(item.get_subtotal() for item in self.items)
    def add_item(self, product: Product, qty:int)-> None:
        if qty <= 0:
            raise ValueError("Quantity must be greater than zero")
        existing_item = next((item for item in self.items if item.product.id == product.id), None)
        curr_qty = existing_item.qty if existing_item else 0
        if curr_qty + qty > product.qty:
            raise ValueError("Cannot add more items than available in stock")
        
        if existing_item:
            existing_item.qty += qty
        else:
            self.items.append(CartItem(product, qty))
    def remove_item(self, product_id:int) -> None:
        existing_item = next((item for item in self.items if item.product.id == product_id), None)
        if not existing_item:
            raise ValueError("Item not found in cart")
        self.items = [item for item in self.items if item.product.id != product_id]        
        