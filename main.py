from fastapi import FastAPI
from routes import auth, products, carts

app = FastAPI(title="GuG Kitchenwares & Plastics")

# Include routers
app.include_router(auth.router, prefix="/auth")
app.include_router(products.router, prefix="/products")
app.include_router(carts.router, prefix="/cart")

@app.get("/")
def root():
    return {"message": "Welcome to GuG Kitchenwares & Plastics"}
