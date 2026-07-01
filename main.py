from domain_layer import Product
from repo_interface import InMemoCartRepo
from service_layer import CartService

def main():
    print("--- Starting Shopping Cart ---\n")
    
    repository = InMemoCartRepo()
    cart_service = CartService(repository)

    laptop = Product(product_id=101, name="Laptop", price=1200.0, qty=10)
    mouse = Product(product_id=102, name="Wireless Mouse", price=50.0, qty=100)
    keyboard = Product(product_id=103, name="Mechanical Keyboard", price=150.0, qty=20)

    customer_id = 42

    print(f"[Action] Customer {customer_id} adds 1 Laptop and 2 Mice to their cart.")
    cart_service.add_item(customer_id, laptop,  qty=1)
    cart_service.add_item(customer_id, mouse, qty=2)

    cart = repository.get_by_customer_id(customer_id)
    print(f"Current Total: ${cart.total_price}\n")

    print(f"[Action] Customer {customer_id} removes the Mouse.")
    cart_service.remove_item(customer_id, product_id=102)

    print(f"[Action] Customer {customer_id} adds a Keyboard.")
    cart_service.add_item(customer_id, keyboard, qty=1)

    final_cart = repository.get_by_customer_id(customer_id)
    print("\n--- Final Checkout Receipt ---")
    print(f"Customer ID: {final_cart.customer_id}")
    for item in final_cart.items:
        print(f"- {item.qty}x {item.product.name} @ ${item.product.price} = ${item.get_subtotal()}")
    
    print("-" * 30)
    print(f"Grand Total: ${final_cart.total_price}")

if __name__ == "__main__":
    main()