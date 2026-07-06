import decimal
import os
import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from implementations.logger_config import setup_logging
from shopping_cart.database import Base, engine
from shopping_cart.repo_interface import SqliteCartRepo, SqliteProductRepo
from implementations.service_layer import CartService
from implementations.product_service import ProductService

# Setup standard logging
setup_logging()
logger = logging.getLogger("app.web")

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="NexShop Shopping Cart System")

# Initialize repositories and services
cart_repo = SqliteCartRepo()
product_repo = SqliteProductRepo()
cart_service = CartService(cart_repo, product_repo)
product_service = ProductService(product_repo)

# --- Pydantic Schemas ---
class AddToCartRequest(BaseModel):
    customer_id: int
    product_id: int
    qty: int

class RemoveFromCartRequest(BaseModel):
    customer_id: int
    product_id: int

# --- API Endpoints ---

@app.get("/api/products")
def get_products():
    logger.debug("API Request: get_products")
    try:
        catalog = product_service.get_catalog()
        return [
            {
                "id": p.id,
                "name": p.name,
                "price": float(p.price),
                "qty": p.qty
            }
            for p in catalog
        ]
    except Exception as e:
        logger.error(f"API Error get_products: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error fetching products.")

@app.get("/api/cart/{customer_id}")
def get_cart(customer_id: int):
    logger.debug(f"API Request: get_cart for customer {customer_id}")
    try:
        cart = cart_repo.get_by_customer_id(customer_id)
        return {
            "customer_id": cart.customer_id,
            "total_price": float(cart.total_price()),
            "items": [
                {
                    "product": {
                        "id": item.product.id,
                        "name": item.product.name,
                        "price": float(item.product.price),
                        "qty": item.product.qty
                    },
                    "qty": item.qty
                }
                for item in cart.items
            ]
        }
    except Exception as e:
        logger.error(f"API Error get_cart for customer {customer_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error loading cart.")

@app.post("/api/cart/add")
def add_to_cart(request: AddToCartRequest):
    logger.debug(f"API Request: add_to_cart {request}")
    try:
        cart_service.add_product(
            customer_id=request.customer_id,
            product_id=request.product_id,
            qty=request.qty
        )
        return {"status": "success"}
    except ValueError as ve:
        # Business rule violations
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"API Error add_to_cart: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error adding to cart.")

@app.post("/api/cart/remove")
def remove_from_cart(request: RemoveFromCartRequest):
    logger.debug(f"API Request: remove_from_cart {request}")
    try:
        cart_service.remove_product(
            customer_id=request.customer_id,
            product_id=request.product_id
        )
        return {"status": "success"}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"API Error remove_from_cart: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error removing from cart.")

# Endpoint to tail logs for the web terminal console
@app.get("/api/logs")
def get_logs(offset: int = Query(0)):
    log_file_path = os.path.join("logs", "app.log")
    if not os.path.exists(log_file_path):
        return {"lines": [], "new_offset": 0}
    
    try:
        with open(log_file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        # Return new lines from offset
        new_lines = lines[offset:]
        return {
            "lines": [line.strip() for line in new_lines],
            "new_offset": len(lines)
        }
    except Exception as e:
        logger.error(f"API Error fetching logs: {str(e)}")
        return {"lines": [], "new_offset": offset}

# --- Serve Web Frontend ---
@app.get("/")
def serve_index():
    return FileResponse("static/index.html")

# Mount remaining static assets (style.css, app.js, images/)
app.mount("/", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Start the server on port 1111 as requested
    host = os.getenv("HOST", "0.0.0.0")
    logger.info(f"Launching FastAPI server on {host}:1111...")
    uvicorn.run("app_entrypoint:app", host=host, port=1111, reload=True)
