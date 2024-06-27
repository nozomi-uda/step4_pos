from sqlalchemy import ForeignKey, Integer, String, DateTime, create_engine, Column
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime

Base = declarative_base()

class Products(Base):
    __tablename__ = 'product_master'
    prd_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Integer, unique=True, nullable=False)  # 修正: String -> Integer
    name = Column(String(50), nullable=False)
    price = Column(Integer, nullable=False)
    transaction_details = relationship("TransactionDetails", back_populates="product")

class Transaction(Base):
    __tablename__ = 'transaction'
    trd_id = Column(Integer, primary_key=True, autoincrement=True)
    datetime = Column(DateTime, nullable=False, default=datetime.utcnow)
    emp_cd = Column(String(10), nullable=False)
    store_cd = Column(String(5), nullable=False)
    pos_no = Column(String(3), nullable=False)
    total_amt = Column(Integer, nullable=False)
    transaction_details = relationship("TransactionDetails", back_populates="transaction")

class TransactionDetails(Base):
    __tablename__ = 'transaction_details'
    trd_id = Column(Integer, ForeignKey("transaction.trd_id"))
    dtl_id = Column(Integer, primary_key=True, autoincrement=True)
    prd_id = Column(Integer, ForeignKey("product_master.prd_id"), nullable=False)
    prd_code = Column(Integer, nullable=False)  # 修正: String -> Integer
    prd_name = Column(String(50), nullable=False)
    prd_price = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    transaction = relationship("Transaction", back_populates="transaction_details")
    product = relationship("Products", back_populates="transaction_details")
    tax_type = Column(String)  # 修正消費税追加

# # データベースエンジンの作成
# engine = create_engine('sqlite:///POS.db', echo=True, connect_args={'check_same_thread': False})

# # テーブルの作成
# Base.metadata.create_all(engine)

# # セッションの作成
# Session = sessionmaker(bind=engine)
# session = Session()

# # 商品データの追加
# new_product = Products(code='1234567890123', name='ビール', price=220)
# session.add(new_product)
# new_product = Products(code='1234567890124', name='ティッシュ', price=275)
# session.add(new_product)
# new_product = Products(code='1234567890125', name='ヘアワックス', price=660)
# session.add(new_product)
# new_product = Products(code='1234567890126', name='お茶', price=165)
# session.add(new_product)
# new_product = Products(code='1234567890127', name='シュークリーム', price=242)
# session.add(new_product)
# new_product = Products(code='1234567890128', name='からあげ', price=253)
# session.add(new_product)
# new_product = Products(code='1234567890129', name='雑誌', price=550)
# session.add(new_product)
# new_product = Products(code='1234567890130', name='カップラーメン', price=231)
# session.add(new_product)
# new_product = Products(code='1234567890131', name='ビニール傘', price=550)
# session.add(new_product)
# new_product = Products(code='1234567890132', name='たばこ', price=770)
# session.add(new_product)
# session.commit()

# # データ追加確認のためのクエリ
# products = session.query(Products).all()
# for product in products:
#     print(f'商品ID: {product.prd_id}, コード: {product.code}, 名前: {product.name}, 価格: {product.price}')