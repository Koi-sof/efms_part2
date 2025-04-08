from app import db
from datetime import datetime

class Product(db.model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200))
    category = db.Column(db.String(50), nullable=False)#carbs, fruits n vegies, proteins
    price = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.eatnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.eatnow)
    quantity = db.Column(db.Integer, default=0)
    transactions = db.relationship('Transaction', backref='product', lazy=True)
    def __repr__(self):
        return f"Product('{self.name}', '{self.price}', '{self.quantity}')"
    

class Transaction(db.model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    transaction_date = db.Column(db.DateTime, default=datetime.eatnow)
    transaction_type = db.Column(db.String(20), nullable=False)    #types zikuwe add, delete, edit a pdt
    
    def __repr__(self):
        return f"Transaction('{self.product_id}', '{self.quantity}', '{self.transaction_date}')"
    
    #from app import db

    #db.create_all()
    # in the python shell #

