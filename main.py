from domain_layer import Product
from repo_interface import JsonCartRepo
from service_layer import CartService
import random
import decimal

def main():
    print("--- Starting Shopping Cart ---\n")
    FILE = "Carts.json"
    cart = CartService(JsonCartRepo(FILE))
    store_products = {
        1: Product(1,"Laptop",decimal.Decimal("1000"),5),
        2: Product(2,"Mobile",decimal.Decimal("500"),50),
        3: Product(3,"Smartwatch",decimal.Decimal("200"),500)
    }
    cart.add_product(1,store_products[1],1) 

if __name__ == "__main__":
    main()