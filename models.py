from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()

class Product(db.Model):
  __tablename__ = "products"
  id = db.Column(db.Integer,primary_key=True, nullable=False)
  name = db.Column(db.String(256), nullable = False)
  buying_price = db.Column(db.Float, nullable = False)
  selling_price = db.Column(db.Float, nullable = False)  

class Sale(db.Model):
  __tablename__ = "sales"
  id = db.Column(db.Integer,primary_key=True)
  quantity = db.Column(db.Float, nullable =False)
  product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable = False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  product = db.relationship("Product", backref = db.backref("sales", lazy=True))

class Purchase(db.Model):
  __tablename__ = "purchases"
  id = db.Column(db.Integer,primary_key=True)
  quantity = db.Column(db.Float, nullable =False)
  product_id = db.Column(db.Integer, db.ForeignKey("products.id"), nullable = False)
  created_at = db.Column(db.DateTime, default=datetime.utcnow)
  product = db.relationship("Product", backref = db.backref("purchases", lazy=True))

class User(db.Model):
  __tablename__ = "users"
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(256), nullable=False)
  email = db.Column(db.String(256), unique = True, nullable=False)
  password = db.Column(db.String(256), nullable=False) # hashed

# Sales and purchases