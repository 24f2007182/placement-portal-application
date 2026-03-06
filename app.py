from functools import wraps
import os
from flask_security import login_required
from flask_login import LoginManager, current_user, login_user, logout_user
from flask import Flask, abort, render_template, redirect, send_file, url_for,request , flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from sqlalchemy import String, cast
from seed_data import seed
from werkzeug.security import check_password_hash, generate_password_hash
from models import db,Student, Company, Admin, JobPosition, Application, User, Placement

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placementapp.db'
app.config['SECRET_KEY'] = 'da1417b94cc6998e458868c66d8d4f85f8bef30762605829'

UPLOAD_FOLDER = 'static/resumes'

loginManager = LoginManager()
loginManager.init_app(app)
loginManager.login_view = "login"

db.init_app(app)
with app.app_context():
    db.create_all()
    if User.query.first() is None:
        seed()

@loginManager.user_loader
def load_user(userId):
    return db.session.get(User, int(userId))

def role_required(role):
    def wrapper(func):
        @wraps(func)
        @login_required
        def decorated_function(*args, **kwargs):
            if current_user.role != role:
                abort(403)

            return func(*args,**kwargs)
        return decorated_function
    return wrapper

@app.route('/login', methods = ['POST','GET'])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username = username).first()
        if user and check_password_hash(user.passwordHash ,password):
            if user.role == 'Company':
                company = Company.query.filter_by(userId = user.userId).first()
                if not company.approved:
                    flash("Waiting for admin approval","danger")
            login_user(user)
            return redirect(url_for("redirectDashboard"))
        flash("Invalid Credentials","danger")
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logged out user successfully!", "success")
    return redirect(url_for('index'))

@app.route('/redirect')
@login_required
def redirectDashboard():
    if current_user.role == "Admin":
        admin = Admin.query.filter_by(userId = current_user.userId).first()
        return redirect(url_for('showAdminDash',adminId = admin.adminId))
    elif current_user.role == "Company":
        company = Company.query.filter_by(userId = current_user.userId).first()
        return redirect(url_for('showCompanyDash' , companyId = company.companyId))
    elif current_user.role == "Student":
        student = Student.query.filter_by(userId = current_user.userId).first()
        return redirect(url_for('showStudentDashboard', studentId = student.studentId))
    

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin/<int:adminId>/dashboard', methods = ['GET'])
@role_required('Admin')
def showAdminDash(adminId):
    admin = Admin.query.filter_by(adminId = adminId).first()
    totalStudents = Student.query.count()
    totalCompanies = Company.query.count()
    totalJobs = JobPosition.query.count()
    totalApplications = Application.query.count()
    return render_template('./admin/dashboard.html',admin=admin, adminId = adminId, totalStudents = totalStudents, totalCompanies = totalCompanies, totalJobs = totalJobs, totalApplications = totalApplications)

@app.route('/admin/<int:adminId>/companies', methods = ['GET'])
@role_required('Admin')
def showCompanies(adminId):
    if request.method == 'GET':
        search = request.args.get('search')
        if search:
            companies = Company.query.filter((Company.companyName.ilike(f"%{search}")) | Company.industry.ilike(f"%{search}%")).all()
        else:
            companies = Company.query.all()
        return render_template('./admin/company.html', adminId = adminId, companies = companies)

@app.route('/admin/<int:adminId>/companies/<int:companyId>/approve')
@role_required('Admin')
def approveCompany(adminId,companyId):
    company = Company.query.filter_by(companyId = companyId).first_or_404()
    company.approved = True
    db.session.commit()
    flash('Company approved successfully!!')
    return redirect(url_for('showCompanies', adminId = adminId))

@app.route('/admin/<int:adminId>/companies/<int:companyId>/reject')
@role_required('Admin')
def rejectCompany(adminId, companyId):
    company = Company.query.filter_by(companyId = companyId).first_or_404()
    company.approved = False
    db.session.commit()
    flash('Company rejected successfully!!')
    return redirect(url_for('showCompanies', adminId = adminId))


@app.route('/admin/<int:adminId>/companies/<int:userId>/toggleCompany')
@role_required('Admin')
def toggleCompany(adminId, userId):
    user = User.query.filter_by(userId = userId).first()
    if user.active == True:
        user.active = False
        db.session.commit()
        flash('Company blacklisted successfully!!')
        return redirect(url_for('showCompanies',adminId = adminId))
    else:
        user.active = True
        db.session.commit()
        flash('Company approved successfully!!')
        return redirect(url_for('showCompanies', adminId = adminId))
    
@app.route('/admin/<int:adminId>/students', methods = ['GET','POST'])
@role_required('Admin')
def showStudents(adminId):
    drives = JobPosition.query.all()
    students = Student.query.all()
    applications = Application.query.all()
    selectedApplication = None

    if request.method == 'POST':
        search = request.form.get('search')
        jobId = request.form.get('jobId')
        statusVal = request.form.get('statusVal')
        
        if jobId:
            query = Application.query.filter_by(jobId = jobId)
            if statusVal:
                    query = query.filter_by(status = statusVal)
            applications = query.all()
                      
        if search:
            students = Student.query.filter((Student.name.ilike(f"%{search}%")) | cast(Student.studentId, String).ilike(f"%{search}%") | Student.contactNumber.ilike(f"%{search}%")).all()
                
        return render_template('./admin/students.html',drives = drives,adminId = adminId,selectedApplication = selectedApplication, applications = applications,students = students)
    viewAppId = request.args.get("viewAppId")
    if viewAppId:
        selectedApplication = Application.query.filter_by(applicationId = viewAppId).first()
    return render_template('./admin/students.html',drives = drives,adminId = adminId,applications=applications, selectedApplication = selectedApplication, students = students)
    
       
@app.route('/admin/<int:adminId>/students/<int:userId>/toggleStudent')
@role_required('Admin')
def togglestudent(adminId, userId):
    user = User.query.filter_by(userId = userId).first()
    if user.active == True:
        user.active = False
        db.session.commit()
        flash('student blacklisted successfully!!')
        return redirect(url_for('showStudents',adminId=adminId))
    else:
        user.active = True
        db.session.commit()
        flash('student approved successfully!!')
        return redirect(url_for('showStudents', adminId = adminId))

@app.route('/admin/<int:adminId>/jobDrives')
@role_required('Admin')
def showDrives(adminId):
    viewAppId = request.args.get("viewAppId")
    viewDriveId = request.args.get("viewDriveId")

    selectedApplication = None
    selectedDrive = None

    if viewAppId:
        selectedApplication = Application.query.filter_by(applicationId = viewAppId).first()    
    if viewDriveId:
        selectedDrive = JobPosition.query.filter_by(jobId = viewDriveId).first()
    drives = JobPosition.query.all()
    applications = Application.query.all()
    return(render_template('./admin/jobpositions.html', adminId = adminId, drives = drives, applications = applications, selectedApplication = selectedApplication, selectedDrive = selectedDrive))

@app.route('/admin/<int:adminId>/completeDrive/<int:jobId>')
@role_required('Admin')
def completeDrive(adminId,jobId):
    drive = JobPosition.query.filter_by(jobId = jobId).first()
    drive.active = False
    db.session.commit()
    drives = JobPosition.query.all()
    applications = Application.query.all()
    return(render_template('./admin/jobpositions.html', adminId = adminId, drives = drives, applications = applications))


#company routes 
@app.route('/company/<int:companyId>/dashboard')
@role_required('Company')
def showCompanyDash(companyId):
    company = Company.query.filter_by(companyId = companyId).first()
    if company.approved:
        drives = JobPosition.query.filter_by(companyId = companyId).all()
        totalDrives = JobPosition.query.filter_by(companyId = companyId).count()
        applications = []
        placements = []
        for drive in drives:            
            application = Application.query.filter_by(jobId = drive.jobId).first()
            if application != None:
                placement = Placement.query.filter_by(applicationId = application.applicationId).first()
            applications.append(application)
            placements.append(placement)
        totalApplications = len(applications)
        totalPlacements = len(placements)
        return render_template('./company/dashboard.html',totalPlacements = totalPlacements, company = company, drives = drives, applications = applications, totalApplications = totalApplications, totalDrives = totalDrives)

@app.route('/company/<int:companyId>/createDrive', methods = ['GET', 'POST'])
@role_required('Company')
def createDrive(companyId):
    if request.method == 'GET':
        return render_template('./company/createDrive.html', companyId = companyId
        
        )
    if request.method == 'POST':
        newJob = JobPosition(companyId = companyId,
                             driveName = request.form['name'],
                            positionOpen = request.form['position'],
                            description = request.form['desc'],
                            skillsRequired = request.form['skills'],
                            experienceRequired = request.form['exp'],
                            salary = request.form['sal'],
                            location = request.form['location'])
        db.session.add(newJob)
        db.session.commit()
        flash('Added new drive successfully!')
        return redirect(url_for('showCompanyDash', companyId = companyId))

@app.route('/company/<int:companyId>/viewApplications', methods = ["GET", "POST"])
@role_required('Company')
def showCompanyApplications(companyId):
    
    if request.method == "GET":
        viewAppId = request.args.get("viewAppId")
        selectedApplication = None
        drives = JobPosition.query.filter_by(companyId = companyId).all()

        

        if viewAppId:
            selectedApplication = Application.query.filter_by(applicationId = viewAppId).first()   
        
        applications = []
        for drive in drives:
            
            applicationsList = Application.query.filter_by(jobId = drive.jobId).all()
            for application in applicationsList:
                applications.append(application)

        return render_template('./company/viewApplications.html',drives = drives, applications = applications,companyId = companyId, selectedApplication = selectedApplication )
    
    if request.method == "POST":
        jobId = request.form['jobId']
        statusVal = None
        statusVal = request.form.get('statusVal')
        viewAppId = request.args.get("viewAppId")
        selectedApplication = None
        drives = JobPosition.query.filter_by(companyId = companyId).all()
        applications = []
        applicationsList = Application.query.filter_by(jobId = jobId).all()
        for application in applicationsList:
            if statusVal:
                if application.status == statusVal:
                    applications.append(application)
            else:
                applications.append(application)

        return render_template('./company/viewApplications.html',drives = drives, applications = applications,companyId = companyId, selectedApplication = selectedApplication )


    
@app.route('/company/<int:companyId>/viewApplications/<int:applicationId>', methods = ["POST"])
@role_required('Company')
def updateApplicationStatus(companyId, applicationId):
    updatedStatus = request.form['status']
    application = Application.query.filter_by(applicationId = applicationId).first_or_404()
    application.status = updatedStatus
    if updatedStatus == 'Placed':
        
        newPlacement = Placement(applicationId = application.applicationId, package = application.job.salary, placedOn = datetime.now() )
        db.session.add(newPlacement)

    db.session.commit()
        
    return redirect(url_for('showCompanyApplications', companyId = companyId))
    

@app.route('/company/<int:companyId>/viewDrives')
@role_required('Company')
def showCompanyDrives(companyId):
    query = JobPosition.query.filter_by(companyId = companyId)
    activeDrives = query.filter_by(active = True).all()
    
    completedDrives = query.filter_by(active = False).all()
    viewDriveId = request.args.get("viewDriveId")
    selectedDrive = None  
    if viewDriveId:
        selectedDrive = JobPosition.query.filter_by(jobId = viewDriveId).first()
    return render_template('./company/existingDrives.html', companyId = companyId, selectedDrive = selectedDrive, activeDrives = activeDrives, completedDrives = completedDrives)

@app.route('/company/<int:companyId>/closeDrive/<int:jobId>')
@role_required('Company')
def closeDrive(companyId, jobId):
    job = JobPosition.query.filter_by(jobId = jobId).first_or_404()
    job.active = False
    db.session.commit()
    return redirect(url_for('showCompanyDrives', companyId = companyId ))

@app.route('/viewApplications/<int:studentId>')
def viewResume(studentId):
    student = Student.query.get(studentId)
    return send_file(student.resume, as_attachment=False)

@app.route('/registerCompany', methods = ['GET', 'POST'])
def registerCompany():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        name = request.form.get('name')
        email = request.form.get('email')
        description = request.form.get('description')
        industry = request.form.get('industry')
        user = User(username = username, passwordHash = generate_password_hash(password), role = 'Company')
        db.session.add(user)
        db.session.commit()

        company = Company(userId = user.userId, companyName = name, industry = industry, description = description, companyEmail = email)
        db.session.add(company)
        db.session.commit()
        flash('Regiestered Company Successfully! You will be able to login pending admin approval.')
        return redirect(url_for('index'))
    return render_template('registerCompany.html')

#students login routes 
@app.route('/registerStudent', methods = ['GET', 'POST'])

def registerStudent():
    if request.method == 'POST':
        username = request.form['username']
        password =request.form['password']
        name = request.form['name']
        contactNumber = request.form['contact']
        department = request.form['dept']
        resume = request.files['resume']
        experience = request.form['exp']
        skills = request.form['skills']
        
        resumePath = f'resumes/{resume.filename}'
        resume.save(os.path.join(app.root_path, 'static', resumePath))
        userCheck = User.query.filter_by(username = username).first()

        if not userCheck:
            user = User(username = username, passwordHash = generate_password_hash(password), role = "student", active = True)
            db.session.add(user)
            db.session.commit()
            student = Student(userId = user.userId, name = name,contactNumber = contactNumber, department = department, experience = experience, skills = skills, resume = resumePath )
            db.session.add(student)
            db.session.commit()

        else:
            flash("Username already exists. Please choose another", "danger")
        
        return render_template('index.html')
    return render_template('registerStudent.html')

@app.route('/student/<int:studentId>/dashboard')
@role_required('Student')
def showStudentDashboard(studentId):
    student = Student.query.filter_by(studentId = studentId).first()
    drives = JobPosition.query.filter(
        Company.approved == True, JobPosition.active == True
    ).all()
    viewDriveId = request.args.get('viewDriveId')
    selectedDrive = None
    if viewDriveId:
        selectedDrive = JobPosition.query.filter_by(jobId = viewDriveId).first()
    companies = Company.query.filter(Company.approved == True).all()
    applications = Application.query.filter_by(studentId = studentId).all()
    notifications = Application.query.filter(
        Application.studentId == studentId,
        Application.status != 'Applied').order_by(Application.appliedOn.asc()).all()

    return (render_template('./student/dashboard.html',notifications = notifications, selectedDrive = selectedDrive, applications = applications, student = student, companies = companies,drives = drives))

@app.route('/student/<int:studentId>/viewJobs', methods = ['POST'])
@role_required('Student')
def searchPostion(studentId):
    search = request.form.get('search')
    print(search)
    companyId = request.args.get('companyId')
    jobs = JobPosition.query.join(Company).filter(
        Company.companyName.ilike(f'%{search}%') |
        JobPosition.positionOpen.ilike(f'%{search}%') | 
        JobPosition.skillsRequired.ilike(f'%{search}%')).all()
    company = None 
    if companyId:
        company = Company.query.filter_by(companyId = companyId).first()
    print(jobs,studentId)
    return render_template('./student/viewJobs.html', studentId = studentId, company = company,drives = jobs)
    
@app.route('/student/<int:studentId>/apply/<int:jobId>')
@role_required('Student')
def applyJob(studentId, jobId):
    app = Application.query.filter_by(studentId = studentId ,  jobId = jobId).first()
    companyId = request.args.get('companyId')
    company = None 
    if companyId:
        company = Company.query.filter_by(companyId = companyId).first()
    job = JobPosition.query.filter_by(jobId = jobId).first()
    if app == None:
        application = Application(studentId = studentId, jobId =jobId)
        db.session.add(application)
        db.session.commit()
        return redirect(url_for('viewJobs', studentId = studentId))
    else:
        flash("Already applied for the drive!", 'error')
        return redirect(url_for('viewJobs' , studentId = studentId))

@app.route('/student/<int:studentId>/viewJobs')
@role_required('Student')
def viewJobs(studentId):
    companyId = request.args.get('companyId')
    search = request.args.get('search')
    if search:
        drives = JobPosition.query.filter(
            Company.companyName.ilike(f'%{search}%') |
            JobPosition.positionOpen.ilike(f'%{search}%') | 
            JobPosition.skillsRequired.ilike(f'%{search}%')).all()
    if companyId:
        drives = JobPosition.query.filter_by(companyId = companyId).all()
    else:
        drives = JobPosition.query.all()

    company = Company.query.filter_by(companyId = companyId).first()
    viewDriveId = request.args.get('viewDriveId')
    selectedDrive = None
    if viewDriveId:
        selectedDrive = JobPosition.query.filter_by(jobId = viewDriveId).first()

    return render_template('./student/viewJobs.html',selectedDrive = selectedDrive, company = company,studentId =studentId, drives = drives)

@app.route('/student/<int:studentId>/viewHistory')
@role_required('Student')
def viewHistory(studentId):
    applications = Application.query.filter_by(studentId = studentId).all()
    student = Student.query.filter_by(studentId = studentId).first()

    return render_template('./student/viewHistory.html', student = student, applications = applications)

@app.route('/student/<int:studentId>/editProfile', methods = ['GET','POST'])
@role_required('Student')
def editProfile(studentId):
    if request.method == 'GET':
        student = Student.query.filter_by(studentId = studentId).first_or_404()
        return render_template('./student/editProfile.html', student = student)
    if request.method == 'POST':
        student = Student.query.filter_by(studentId = studentId).first()
        student.name = request.form.get('name')
        student.contactNumber = request.form.get('contact')
        student.department = request.form.get('dept')
        student.experience = request.form.get('exp')
        student.skills = request.form.get('skills')
        resume = request.files.get('resume')

        if resume and resume.filename != "":
            filename = resume.filename
            resumePath = f'resumes/{filename}'
            resume.save(os.path.join(app.root_path, 'static', resumePath))
            student.resume = resumePath
            username = request.form['username']
            if username:
                student.user.username = username
            newPassword = request.form.get('password')
            if newPassword:
                student.user.passwordHash = newPassword
            db.session.commit()
        db.session.commit()
        flash("Profile updated successfully!")
        return redirect(url_for('editProfile', studentId = studentId))
 
             
if __name__ == "__main__":
    app.run(debug=True)