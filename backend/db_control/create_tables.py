import platform
print(platform.uname())

from mymodels import Products, Transaction, TransactionDetail
from connect import engine

print("Creating tables >>> ")
Products.metadata.create_all(bind=engine)
Transaction.metadata.create_all(bind=engine)
TransactionDetail.metadata.create_all(bind=engine)