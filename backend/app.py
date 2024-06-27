from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, sessionmaker
from starlette.requests import Request
from starlette.responses import JSONResponse
from pydantic import BaseModel
from db_control.mymodels import Products, Transaction, TransactionDetails
from db_control.connect import engine
from datetime import datetime
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class ProductIn(BaseModel):
    prd_id: int
    code: int
    name: str
    price: int

class ProductPurchase(BaseModel):
    code: int
    quantity: int

class PurchaseRequest(BaseModel):
    emp_code: str
    store_code: str
    pos_no: str
    products: List[ProductPurchase]

class PurchaseResponse(BaseModel):
    success: bool
    total_price: int
    total_price_ex_tax: int

def get_prd_info(db_session: Session, code: int):
    return db_session.query(Products).filter(Products.code == code).first()

def get_db(request: Request):
    return request.state.db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application"}

@app.get("/products/")
def read_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    response_data = jsonable_encoder(products)
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")

@app.get("/products/{code}")
def read_product(code: int, db: Session = Depends(get_db)):
    product = get_prd_info(db, code)
    if not product:
        return JSONResponse(content={"message": "Product not found"}, status_code=404)
    response_data = jsonable_encoder(product)
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")

@app.post("/products/")
async def create_products(products_in: ProductIn, db: Session = Depends(get_db)):
    product = Products(prd_id=products_in.prd_id, code=products_in.code, name=products_in.name, price=products_in.price)
    db.add(product)
    db.commit()
    db.refresh(product)
    product = get_prd_info(db, product.prd_id)
    response_data = jsonable_encoder(product)
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")

@app.put("/products/{prd_id}")
async def update_product(prd_id: int, code: int, name: str, products_in: ProductIn, db: Session = Depends(get_db)):
    product = get_prd_info(db, prd_id)
    if not product:
        return JSONResponse(content={"message": "Product not found"}, status_code=404)
    product.prd_id = products_in.prd_id
    product.code = products_in.code
    product.name = products_in.name
    product.price = products_in.price
    db.commit()
    db.refresh(product)
    response_data = jsonable_encoder(product)
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")

@app.delete("/products/{prd_id}")
async def delete_product(prd_id: int, db: Session = Depends(get_db)):
    product = get_prd_info(db, prd_id)
    db.delete(product)
    db.commit()
    return JSONResponse(content={"message": "Product deleted"}, media_type="application/json; charset=utf-8")

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    try:
        response = await call_next(request)
    finally:
        request.state.db.close()
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response

@app.post("/purchase/")
async def purchase_product(purchase_request: PurchaseRequest, db: Session = Depends(get_db)):
    logger.info("Received purchase request: %s", purchase_request)
    transaction = Transaction(
        datetime=datetime.now(),
        emp_cd=purchase_request.emp_code if purchase_request.emp_code else '9999999999',
        store_cd=purchase_request.store_code if purchase_request.store_code else '55555',
        pos_no=purchase_request.pos_no if purchase_request.pos_no else '333',
        total_amt=0
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    total_ex_tax = 0
    total = 0
    tax_rate = 0.1  # 消費税率10%

    for product in purchase_request.products:
        db_product = get_prd_info(db, product.code)
        if not db_product:
            logger.error("Product not found: %s", product.code)
            return JSONResponse(content={"message": "Product not found"}, status_code=404)
        total_ex_tax += db_product.price * product.quantity
        total += int(db_product.price * product.quantity * (1 + tax_rate))
        transaction_detail = TransactionDetails(
            trd_id=transaction.trd_id,
            prd_id=db_product.prd_id,
            prd_code=db_product.code,
            prd_name=db_product.name,
            prd_price=db_product.price,
            quantity=product.quantity,
            tax_type='10'
        )
        db.add(transaction_detail)

    transaction.total_amt = total
    db.commit()
    db.refresh(transaction)

    response_data = PurchaseResponse(success=True, total_price=total, total_price_ex_tax=total_ex_tax)
    logger.info("Returning response: %s", response_data)
    return JSONResponse(content=jsonable_encoder(response_data), media_type="application/json; charset=utf-8")
