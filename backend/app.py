from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session, sessionmaker
from starlette.requests import Request
from starlette.responses import JSONResponse
from pydantic import BaseModel
from db_control.mymodels import Products
from db_control.connect import engine
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

# DB接続用のセッションクラス インスタンスが作成されると接続する
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydanticを用いたAPIに渡されるデータの定義 ValidationやDocumentationの機能が追加される
class ProductIn(BaseModel):
    prd_id: int
    code: int
    name: str
    price: int

# 単一のproduct_infoを取得するためのユーティリティ
def get_prd_info(db_session: Session, prd_id: int):
    return db_session.query(Products).filter(Products.prd_id == prd_id).first()

# DB接続のセッションを各エンドポイントの関数に渡す
def get_db(request: Request):
    return request.state.db

# このインスタンスをアノテーションに利用することでエンドポイントを定義できる
app = FastAPI()

# CORS設定の追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 必要に応じてドメインを指定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ルートパス (/) のエンドポイントの追加
@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI application"}

# Productsの全取得
@app.get("/products/")
def read_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    response_data = jsonable_encoder(products)
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")

# 単一のProductsを取得
@app.get("/products/{prd_id}")
def read_product(prd_id: int, db: Session = Depends(get_db)):
    product = get_prd_info(db, prd_id)
    # エラーハンドリングの追加 
    if not product:
        return JSONResponse(content={"message": "Product not found"}, status_code=404)
    response_data = jsonable_encoder(product)
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")

# Productsを登録
@app.post("/products/")
async def create_products(products_in: ProductIn, db: Session = Depends(get_db)):
    product = Products(prd_id=products_in.prd_id, code=products_in.code, name=products_in.name, price=products_in.price)
    db.add(product)
    db.commit()
    # コミット後にセッションをリフレッシュして最新のデータを取得
    db.refresh(product)
    product = get_prd_info(db, product.prd_id)
    response_data = jsonable_encoder(product)
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")

# Productsを更新
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
    # update_product エンドポイントの修正
    db.refresh(product)
    response_data = jsonable_encoder(product)
    return JSONResponse(content=response_data, media_type="application/json; charset=utf-8")

# Productsを削除
@app.delete("/products/{prd_id}")
async def delete_product(prd_id: int, db: Session = Depends(get_db)):
    product = get_prd_info(db, prd_id)
    db.delete(product)
    db.commit()
    return JSONResponse(content={"message": "Product deleted"}, media_type="application/json; charset=utf-8")

# リクエストの度に呼ばれるミドルウェア DB接続用のセッションインスタンスを作成
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    request.state.db = SessionLocal()
    # try-finally を使ったセッションクローズ処理の修正
    try:
        response = await call_next(request)
    finally:
        request.state.db.close()
    response.headers["Content-Type"] = "application/json; charset=utf-8"
    return response
