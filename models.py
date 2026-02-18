from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 

db = SQLAlchemy()
class User(db.Model):
    __tablename__ = "users"
    userId = db.Column(db.Integer, auto_increment = True, primary_key = True )
    username = db.Column(db.String, nullable = False)
    passwordHash = db.Column(db.String , nullable = False)
    role = db.Column(db.String, nullable = False)
    status = db.Column(db.String, nullable = False)

class Admin(db.Model):
    __tablename__ = "admins"
    adminId = db.Column(db.Integer, primary_key = True, auto_increment = True)
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable = False)
    name = db.Column(db.String, nullable = False)
    contactNumber = db.Column(db.Integer, nullable = False)

class Company(db.Model):
    __tablename__ = "companies"
    companyId = db.Column(db.Integer, auto_increment = True, primary_key = True)
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable = False)
    companyName = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    companyEmail = db.Column(db.String,nullable = False)
    approved = db.Column(db.Boolean, default = "False", nullable = False)

class Student(db.Model):
    __tablename__ = "students"
    studentId = db.Column(db.Integer,auto_increment = True, primary_key = True )
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable = False)
    name = db.Column(db.String, nullable = False)
    contactNumber = db.Column(db.Integer , nullable = False)
    course = db.Column(db.String, nullable = False)
    resume = db.Column(db.String, nullable = False)
    experience = db.Column(db.String, nullable = False)
    skills = db.column(db.String, ullable = False)

class JobPosition(db.Model):
    __tablename__ = "jobpositions"
    jobId = db.Column(db.Integer, primary_key = True, auto_increment = True)
    companyId = db.Column(db.Integer, db.ForeignKey("companies.companyId"), nullable = False)
    title = db.Column(db.String, nullable = False) 
    description = db.Column(db.String, nullable = False)
    skillsRequired = db.Column(db.String, nullable = False)
    experienceRequired = db.Colmn(db.String, nullable = False)
    status = db.Column(db.String, ullale = False, default = "Active")
    salary = db.Column(db.String, nullale = False)

class Applications(db.Model):
    __tablename__ = "applications"
    applicationId = db.Column(db.Integer, auto_increment = True , primary_key = True)
    studentId = db.Column(db.Integer, db.ForeignKey("students.studentId"))
    jobId  = db.Column(db.Integer, db.ForeignKey("jobpositions.jobId"))
    status = db.Column(db.String, default = "Applied", nullable = False)
    appliedOn = db.Column(db.DateTime, default = datetime.ctime)

class Placement(db.Model):
    __tablename__ = "placements"
    placementId = db.Column(db.Integer, auto_increment = True, primary_key = True)
    applicationId = db.Column(db.Integer, db.ForeignKey("applications.applicationId"), nullable = False )
    package = db.Column(db.Integer, nullable = False)
    placedOn = db.Column(db.DateTime, default = datetime.ctime)