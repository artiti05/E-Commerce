import decimal
import sys
import os

# Add root folder to sys.path to allow correct package resolution
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from implementations.logger_config import setup_logging
from shopping_cart.database import Base, engine
from shopping_cart.repo_interface import SqliteProductRepo
from implementations.product_service import ProductService

def print_menu():
    print("\n" + "="*55)
    print("      E-COMMERCE CATALOG MANAGEMENT SYSTEM (ADMIN)")
    print("="*55)
    print("1. Add a New Product to Catalog")
    print("2. Restock / Update Product Inventory Quantity")
    print("3. View Current Database Catalog")
    print("4. Delete a Product from Catalog")
    print("5. Exit Application")
    print("="*55)

def main():
    # Setup logging configuration (outputs to app.log and stdout)
    setup_logging()
    
    # Initialize SQLite schemas if they do not exist
    Base.metadata.create_all(bind=engine)
    
    # Instantiate the repository and catalog services
    repo = SqliteProductRepo()
    product_service = ProductService(repo)
    
    while True:
        print_menu()
        choice = input("Enter option (1-5): ").strip()
        
        if choice == "1":
            print("\n--- Add Product ---")
            try:
                p_id = int(input("Enter Product ID (integer): ").strip())
                name = input("Enter Product Name: ").strip()
                price = decimal.Decimal(input("Enter Product Price (e.g. 19.99): ").strip())
                qty = int(input("Enter Initial Stock Quantity: ").strip())
                
                product_service.add_product_to_catalog(p_id, name, price, qty)
                print(f"\n[Success] Product '{name}' added to catalog successfully!")
            except ValueError as ve:
                print(f"\n[Error] Invalid input: {ve}")
            except Exception as e:
                print(f"\n[Error] Failed to add product: {e}")
                
        elif choice == "2":
            print("\n--- Update Stock ---")
            try:
                p_id = int(input("Enter Product ID: ").strip())
                qty = int(input("Enter Adjustment Quantity (positive to restock, negative to reduce): ").strip())
                
                product_service.update_stock(p_id, qty)
                print(f"\n[Success] Stock updated successfully!")
            except ValueError as ve:
                print(f"\n[Error] {ve}")
            except Exception as e:
                print(f"\n[Error] Failed to update stock: {e}")
                
        elif choice == "3":
            print("\n--- Current Catalog ---")
            try:
                catalog = product_service.get_catalog()
                if not catalog:
                    print("Catalog is empty.")
                else:
                    print(f"{'ID':<6} | {'Name':<25} | {'Price':<10} | {'Stock':<6}")
                    print("-" * 56)
                    for product in catalog:
                        print(f"{product.id:<6} | {product.name:<25} | ${product.price:<9} | {product.qty:<6}")
            except Exception as e:
                print(f"\n[Error] Failed to load catalog: {e}")
                
        elif choice == "4":
            print("\n--- Delete Product ---")
            try:
                p_id = int(input("Enter Product ID to delete: ").strip())
                confirm = input(f"Are you sure you want to delete Product ID {p_id}? (y/n): ").strip().lower()
                if confirm == 'y':
                    product_service.remove_product_from_catalog(p_id)
                    print(f"\n[Success] Product deleted successfully.")
                else:
                    print("\nDeletion cancelled.")
            except ValueError as ve:
                print(f"\n[Error] Invalid input: {ve}")
            except Exception as e:
                print(f"\n[Error] Failed to delete product: {e}")
                
        elif choice == "5":
            print("\nExiting Admin Catalog Management. Goodbye!")
            sys.exit(0)
            
        else:
            print("\n[Invalid Selection] Please choose a number between 1 and 5.")

if __name__ == "__main__":
    main()
