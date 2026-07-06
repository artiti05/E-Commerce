# E-Commerce Shopping Cart System

A clean, modular e-commerce shopping cart system built in Python, showcasing Domain-Driven Design (DDD) principles and Separation of Concerns.

## Project Structure & File Guide

Below is an explanation of each file in this repository (excluding temporary files and external developer workspaces like `Calc/`):

### Core Application Files
* **[domain_layer.py](file:///c:/Users/VICTUS/Desktop/E-Commerce/domain_layer.py)**: Defines the core domain models and business entities:
  * `Product`: A catalog item with a name, price (using `decimal.Decimal`), and stock quantity.
  * `CartItem`: A reference to a product and a purchase quantity.
  * `Cart`: Represents a customer's shopping cart, tracks selected items, calculates totals, and enforces inventory stock constraints.
* **[repo_interface.py](file:///c:/Users/VICTUS/Desktop/E-Commerce/repo_interface.py)**: Manages data persistence:
  * `CartRepo`: Abstract interface defining the data access contract.
  * `JsonCartRepo`: Concrete repository implementing JSON serialization to save and load carts.
* **[service_layer.py](file:///c:/Users/VICTUS/Desktop/E-Commerce/service_layer.py)**: Houses `CartService`, which coordinates domain logic operations (e.g., adding/removing products) and database saves.
* **[main.py](file:///c:/Users/VICTUS/Desktop/E-Commerce/main.py)**: The main execution entry point demonstrating a complete checkout flow using the JSON-backed repository.

### Data & Notebooks
* **[Carts.json](file:///c:/Users/VICTUS/Desktop/E-Commerce/Carts.json)**: The local JSON database where cart states are serialized by `JsonCartRepo`.
* **[EXPLORE_JSON.ipynb](file:///c:/Users/VICTUS/Desktop/E-Commerce/EXPLORE_JSON.ipynb)**: A Jupyter Notebook used to interactively explore and inspect JSON data.

### Testing
* **[unit_test.py](file:///c:/Users/VICTUS/Desktop/E-Commerce/unit_test.py)**: Runs isolated tests for business operations utilizing a mock/fake repository.
* **[integration_test.py](file:///c:/Users/VICTUS/Desktop/E-Commerce/integration_test.py)**: Runs end-to-end integration tests using the actual `JsonCartRepo` to verify the persistence layer.

### Infrastructure
* **[.gitignore](file:///c:/Users/VICTUS/Desktop/E-Commerce/.gitignore)**: Configured to ignore standard Python cache, build dependencies, and temporary developer workspaces (like `Calc/`).

---

## How to Run

### Run the App Simulation
```bash
python main.py
```

### Run Tests
```bash
python -m unittest unit_test.py integration_test.py
```
