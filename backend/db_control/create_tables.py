import platform
print(platform.uname())

from mymodels import Products, Transaction, TransactionDetails
from connect import engine

print("Creating tables >>> ")
Products.metadata.create_all(bind=engine)
Transaction.metadata.create_all(bind=engine)
TransactionDetails.metadata.create_all(bind=engine)