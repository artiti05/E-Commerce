# E-Commerce and Calculator Sandbox Project
This repository contains two independent, modular Python applications demonstrating clean architecture and SOLID design principles.
The e-commerce module implements domain models (Product, Cart, CartItem) and a service layer to manage user carts.
It utilizes repository patterns with an abstract interface (CartRepo) and an in-memory database implementation (InMemoCartRepo).
Unit and integration tests verify the shopping cart's workflows, including adding, updating, and removing items in the cart.
The Calc directory contains calculator applications showcasing SRP, OCP, and separation of UI from execution logic.
Within Calc, the engine registers operations (addition, division, mod, power) dynamically using an operation factory.
Each math operation is encapsulated in its own class, adhering to the Open/Closed Principle for easy extensibility.
Overall, this sandbox serves as a reference for applying design patterns like KISS, DRY, and Layered Architecture in Python.
Run main.py to see the shopping cart simulation, or run Calc/calculator.py/calc2.py for the calculator.
