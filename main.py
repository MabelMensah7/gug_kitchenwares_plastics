from fastapi import FastAPI
from routes import auth, products, carts, reviews, orders

app = FastAPI(title="GuG Kitchenwares & Plastics")

# Routers
app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
app.include_router(carts.router, prefix="/cart")
app.include_router(reviews.router, prefix="/reviews")
app.include_router(orders.router, prefix="/orders")

@app.get("/")
def root():
    return {"message": "Welcome to GuG Kitchenwares & Plastics"}
# how come it says i do not have main.py
