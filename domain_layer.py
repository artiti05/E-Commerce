from typing import List

class Product:
    def __init__(self, product_id:int, name:str, price:float,qty:int):
        self.id = product_id
        self.name = name
        self.price = price
        self.qty = qty
class CartItem:
    def __init__(self, product:Product,qty:int):
        self.product = product
        self.qty = qty
    def get_subtotal(self) ->float:
        return self.product.price * self.qty 
class Cart:
    def __init__(self, customer_id:int):
        self.customer_id = customer_id
        self.items:List[CartItem] = []
        self.total_price: float = 0.0
