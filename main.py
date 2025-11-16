import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Product, Order, OrderItem

app = FastAPI(title="Shop API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Helpers
class ProductOut(BaseModel):
    id: str
    title: str
    description: Optional[str]
    price: float
    category: str
    image: Optional[str]
    in_stock: bool

class OrderOut(BaseModel):
    id: str
    customer_name: str
    customer_email: str
    shipping_address: str
    items: List[OrderItem]
    subtotal: float
    tax: float
    total: float
    status: str


def to_product_out(doc) -> ProductOut:
    return ProductOut(
        id=str(doc.get("_id")),
        title=doc.get("title"),
        description=doc.get("description"),
        price=float(doc.get("price")),
        category=doc.get("category"),
        image=doc.get("image"),
        in_stock=bool(doc.get("in_stock", True)),
    )


def to_order_out(doc) -> OrderOut:
    return OrderOut(
        id=str(doc.get("_id")),
        customer_name=doc.get("customer_name"),
        customer_email=doc.get("customer_email"),
        shipping_address=doc.get("shipping_address"),
        items=doc.get("items", []),
        subtotal=float(doc.get("subtotal", 0)),
        tax=float(doc.get("tax", 0)),
        total=float(doc.get("total", 0)),
        status=doc.get("status", "pending"),
    )


@app.get("/")
def read_root():
    return {"message": "Shop API running"}


@app.get("/products", response_model=List[ProductOut])
def list_products(category: Optional[str] = None, q: Optional[str] = None):
    if db is None:
        return []
    filter_dict = {}
    if category:
        filter_dict["category"] = category
    if q:
        filter_dict["title"] = {"$regex": q, "$options": "i"}
    docs = get_documents("product", filter_dict)
    return [to_product_out(d) for d in docs]


@app.post("/products", response_model=str)
def create_product(product: Product):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    new_id = create_document("product", product)
    return new_id


@app.get("/orders", response_model=List[OrderOut])
def list_orders():
    if db is None:
        return []
    docs = get_documents("order")
    return [to_order_out(d) for d in docs]


@app.post("/orders", response_model=str)
def create_order(order: Order):
    if db is None:
        raise HTTPException(status_code=500, detail="Database not configured")
    new_id = create_document("order", order)
    return new_id


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
