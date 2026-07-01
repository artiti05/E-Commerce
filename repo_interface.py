from domain_layer import Cart, Product
# from typing import List,Optional
from abc import ABC, abstractmethod

class CartRepo(ABC):

    @abstractmethod
    def save(self, cart:Cart):
        pass
    @abstractmethod
    def get_by_customer_id(self, customer_id:int) ->Cart:
        pass
    
class InMemoCartRepo(CartRepo):
    def __init__(self):
        self._db_storage = {}
    
    def save(self,cart: Cart) -> None:
        self._db_storage[cart.customer_id] = cart
        print(f"[Database Log] Cart saved for Customer {cart.customer_id}")

    def get_by_customer_id(self, customer_id:int) -> Cart: 
        if customer_id in self._db_storage:
            return self._db_storage[customer_id]
        return Cart(customer_id)
