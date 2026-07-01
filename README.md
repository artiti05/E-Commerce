# E-Commerce Shopping Cart System
### This repository implements a clean, modular e-commerce shopping cart system in Python.
### The system is structured using Domain-Driven Design and Separation of Concerns principles.
### In domain_layer.py, core entities like Product, CartItem, and Cart are defined.
### Data access is managed through the abstract CartRepo interface in repo_interface.py.
### An in-memory repository (InMemoCartRepo) simulates database operations and logging.
### The service_layer.py houses CartService to coordinate adding and removing items.
### Main execution entry point in main.py executes a mock checkout receipt simulation.
### Automated unit and integration tests are provided to verify core business logic.
### Run the shopping cart workflow via python main.py or run unit_test.py and integration_test.py.
