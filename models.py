from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

db = SQLAlchemy()
class User(db.Model):
    __tablename__ = "users"
    userId = db.Column(db.Integer, auto_increment = True, primary_key = True )
    username = db.Column(db.String, nullable = False)
    passwordHahs = db.Column(db.String , nullable = False)
    role = db.Column(db.String, nullable = False)
    status = db.Column(db.String, nullable = False)
class Admin(db.Model):
    __tablename__ = "admins"
    adminId = db.Column(db.Integer, primary_key = True, auto_increment = True)
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable = False)
    name = db.Column(db.String, nullable = False)
    email = db.Column(db.String, nullable = False)
    contactNumber = db.Column(db.Integer, nullable = False)

class Company(db.Model):
    __tablename__ = "companies"
    companyId = db.Column(db.Integer, auto_increment = True, primary_key = True)