import json
import decimal
import os
from domain_layer import *
from abc import ABC, abstractmethod

class CartRepo(ABC):

    @abstractmethod
    def save(self, cart:Cart):
        pass
    @abstractmethod
    def get_by_customer_id(self, customer_id:int) ->Cart:
        pass
    
class JsonCartRepo(CartRepo):
    def __init__(self, json_file:str="Carts.json"):
        self.file_path = json_file
        if not os.path.exists(self.file_path):
            self._write_file()
    def _write_file(self)-> None:
        with open(self.file_path, 'w') as f:
            json.dump({}, f)
    def _read_file(self)-> dict:
        with open(self.file_path, 'r') as f:
            return json.load(f)
    
    def save(self,cart: Cart) -> None:
        data = self._read_file()
        data[str(cart.customer_id)] = {
            "customer_id": cart.customer_id,
            "items": [
                {
                    "product":{
                        
                        "id": item.product.id,
                        "name": item.product.name,
                        "price": str(item.product.price),
                        "qty": item.product.qty
                    },
                    "qty": item.qty
                }
                for item in cart.items
            ]
        }
        data[str(cart.customer_id)]["total_price"] = str(cart.total_price)
        self._write_file()
        # Here you would typically write `to_json` to a JSON file or database
        print(f"[Database Log] Cart saved for Customer {cart.customer_id}")

    def get_by_customer_id(self, customer_id:int) -> Cart: 
        data = self._read_file()
        if str(customer_id) in data:
            cart_data = data[str(customer_id)]
            items = []
            for item_data in cart_data["items"]:
                product = Product(
                    product_id=item_data["product"]["id"],
                    name=item_data["product"]["name"],
                    price=decimal.Decimal(item_data["product"]["price"]),
                    qty=item_data["product"]["qty"]
                )
                items.append(CartItem(product=product, qty=item_data["qty"]))
            return Cart(customer_id=cart_data["customer_id"], items=items)
        return Cart(customer_id)