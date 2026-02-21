from flask_sqlalchemy import SQLAlchemy
from datetime import datetime 


db = SQLAlchemy()
class User(db.Model):
    __tablename__ = "users"
    userId = db.Column(db.Integer, autoincrement = True, primary_key = True )
    username = db.Column(db.String, nullable = False)
    passwordHash = db.Column(db.String , nullable = False)
    role = db.Column(db.String, nullable = False)
    active = db.Column(db.Boolean, nullable = False, default = True)

    student = db.relationship('Student', back_populates = "user", uselist = False, cascade = "all, delete-orphan")
    admin = db.relationship('Admin', back_populates = "user", uselist = False, cascade = "all, delete-orphan")
    company = db.relationship('Company', back_populates = "user", uselist = False, cascade = "all, delete-orphan")




class Admin(db.Model):
    __tablename__ = "admins"
    adminId = db.Column(db.Integer, primary_key = True, autoincrement = True)
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable = False)
    name = db.Column(db.String, nullable = False)
    contactNumber = db.Column(db.Integer, nullable = False)

    user = db.relationship('User', back_populates = "admin")


class Company(db.Model):
    __tablename__ = "companies"
    companyId = db.Column(db.Integer, autoincrement = True, primary_key = True)
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable = False)
    companyName = db.Column(db.String, nullable = False)
    industry = db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    companyEmail = db.Column(db.String,nullable = False)
    approved = db.Column(db.Boolean, default = False, nullable = False)

    jobs = db.relationship('JobPosition', back_populates = "company", lazy = True, cascade = "all, delete-orphan")
    user = db.relationship('User', back_populates = "company")


class Student(db.Model):
    __tablename__ = "students"
    studentId = db.Column(db.Integer,autoincrement = True, primary_key = True )
    userId = db.Column(db.Integer, db.ForeignKey("users.userId"), nullable = False)
    name = db.Column(db.String, nullable = False)
    contactNumber = db.Column(db.Integer , nullable = False)
    department = db.Column(db.String, nullable = False)
    resume = db.Column(db.String, nullable = False)
    experience = db.Column(db.String, nullable = False)
    skills = db.Column(db.String, nullable = False)

    user = db.relationship('User', back_populates = "student")
    applications = db.relationship('Application', back_populates = "student", lazy = True, cascade = "all, delete-orphan")

class JobPosition(db.Model):
    __tablename__ = "jobpositions"
    jobId = db.Column(db.Integer, primary_key = True, autoincrement = True)
    companyId = db.Column(db.Integer, db.ForeignKey("companies.companyId"), nullable = False)
    driveName = db.Column(db.String, nullable = False) 
    positionOpen= db.Column(db.String, nullable = False)
    description = db.Column(db.String, nullable = False)
    skillsRequired = db.Column(db.String, nullable = False)
    experienceRequired = db.Column(db.String, nullable = False)
    active = db.Column(db.Boolean, default = True, nullable = False)
    salary = db.Column(db.String, nullable = False)
    location = db.Column(db.String, nullable = False)



    company = db.relationship('Company', back_populates = "jobs")
    applications = db.relationship('Application', back_populates = 'job', lazy = True, cascade = "all, delete-orphan")

class Application(db.Model):
    __tablename__ = "applications"
    applicationId = db.Column(db.Integer, autoincrement = True , primary_key = True)
    studentId = db.Column(db.Integer, db.ForeignKey("students.studentId"))
    jobId  = db.Column(db.Integer, db.ForeignKey("jobpositions.jobId"))
    status = db.Column(db.String, default = "Applied", nullable = False)
    appliedOn = db.Column(db.DateTime, default = datetime.utcnow)

    student = db.relationship('Student', back_populates = "applications")
    job = db.relationship('JobPosition', back_populates = 'applications')
    placement = db.relationship('Placement', back_populates = "application" , uselist = False, cascade = "all, delete-orphan")

class Placement(db.Model):
    __tablename__ = "placements"
    placementId = db.Column(db.Integer, autoincrement = True, primary_key = True)
    applicationId = db.Column(db.Integer, db.ForeignKey("applications.applicationId"), nullable = False )
    package = db.Column(db.Integer, nullable = False)
    placedOn = db.Column(db.DateTime, default = datetime.utcnow)

    application = db.relationship('Application', back_populates = "placement")