from flask import Flask, render_template, redirect, url_for,request , flash
from flask_sqlalchemy import SQLAlchemy
from seed_ata import seed
from models import db,Student, Company, Admin, JobPosition, Application, User, Placement

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///placementapp.db'
app.config['SECRET_KEY'] = 'da1417b94cc6998e458868c66d8d4f85f8bef30762605829'

db.init_app(app)
with app.app_context():
    db.create_all()
    if User.query.first() is None:
        print("Database empty. Seeding initial data...")
        seed()

@app.before_request
def method_override():
    if request.method == "POST":
        override = request.form.get("_method")
        if override:
            request.environ["REQUEST_METHOD"] = override.upper()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin//<int:userId>/dashboard', methods = ['GET'])
def showAdminDash(userId):
    admin = Admin.query.filter_by(userId = userId).first()
    totalStudents = Student.query.count()
    totalCompanies = Company.query.count()
    totalJobs = JobPosition.query.count()
    totalApplications = Application.query.count()
    return render_template('./admin/dashboard.html', totalStudents = totalStudents, totalCompanies = totalCompanies, totalJobs = totalJobs, totalApplications = totalApplications)

@app.route('/admin/companies', methods = ['GET'])
def showCompanies():
    if request.method == 'GET':
        search = request.args.get('search')
        if search:
            companies = Company.query.filter((Company.companyName.ilike(f"%{search}")) | Company.industry.ilike(f"%{search}%")).all()
        else:
            companies = Company.query.all()
        return render_template('./admin/company.html', companies = companies)

@app.route('/admin/companies/<int:companyId>/approve')
def approveCompany(companyId):
    company = Company.query.filter_by(companyId = companyId).first_or_404()
    company.approved = True
    db.session.commit()
    flash('Company approved successfully!!')
    return redirect(url_for('showCompanies'))

@app.route('/admin/companies/<int:companyId>/reject')
def rejectCompany(companyId):
    company = Company.query.filter_by(companyId = companyId).first_or_404()
    company.approved = False
    db.session.commit()
    flash('Company rejected successfully!!')
    return redirect(url_for('showCompanies'))


@app.route('/admin/companies/<int:userId>/toggleCompany')
def toggleCompany(userId):
    user = User.query.filter_by(userId = userId).first()
    if user.active == True:
        user.active = False
        db.session.commit()
        flash('Company blacklisted successfully!!')
        return redirect(url_for('showCompanies'))
    else:
        user.active = True
        db.session.commit()
        flash('Company approved successfully!!')
        return redirect(url_for('showCompanies'))
    
#students 
@app.route('/admin/students', methods = ['GET'])
def showStudents():
    if request.method == 'GET':
        search = request.args.get('search')
        if search:
            students = Student.query.filter((Student.name.ilike(f"%{search}")) | Student.studentId.ilike(f"%{search}%") | Student.contactNumber.ilike(f"%{search}%")).all()
        else:
            students = Student.query.all()
        return render_template('./admin/students.html', students = students)
       
@app.route('/admin/students/<int:userId>/toggleStudent')
def togglestudent(userId):
    user = User.query.filter_by(userId = userId)
    if user.active == True:
        user.active = False
        db.session.commit()
        flash('student blacklisted successfully!!')
        return redirect(url_for('showStudents'))
    else:
        user.active = True
        db.session.commit()
        flash('student approved successfully!!')
        return redirect(url_for('showStudents'))

@app.route('/admin/jobDrives')
def showDrives():
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
    return(render_template('./admin/jobpositions.html', drives = drives, applications = applications, selectedApplication = selectedApplication, selectedDrive = selectedDrive))

@app.route('/admin/completeDrive/<int:jobId>')
def completeDrive(jobId):
    drive = JobPosition.query.filter_by(jobId = jobId).first()
    drive.active = False
    db.session.commit()


#company routes 
@app.route('/company/<int:companyId>/dashboard')
def showCompanyDash(companyId):
    company = Company.query.filter_by(companyId = companyId).first()
    if company.approved:
        drives = JobPosition.query.filter_by(companyId = companyId).all()
        totalDrives = JobPosition.query.filter_by(companyId = companyId).count()
        applications = []
        placements = []
        for drive in drives:
            placement = Placement.query.filter_by(jobId = drive.jobId).first()
            application = Application.query.filter_by(jobId = drive.jobId).first()
            applications.append(application)
            placements.append(placement)
        totalApplications = len(applications)
        return render_template('./company/dashboard.html', company = company, drives = drives, applications = applications, totalApplications = totalApplications, totalDrives = totalDrives)

@app.route('/company/<int:companyId>/createDrive', methods = ['GET', 'POST'])
def createDrive(companyId):
    if request.method == 'GET':
        return render_template('./company/createDrive.html', companyId = companyId
        
        )
    if request.method == 'POST':
        newJob = JobPosition(companyId = companyId,
                             driveName = request.form['name'],
                            position = request.form['position'],
                            description = request.form['desc'],
                            skills = request.form['skills'],
                            experience = request.form['exp'],
                            salary = request.form['sal'],
                            location = request.form['location'])
        db.session.add(newJob)
        db.session.commit()
        flash('Added new drive successfully!')
        return redirect(url_for('showCompanyDash', companyId = companyId))

@app.route('/company/<int:companyId>/viewApplications')
def showCompanyAppplications(companyId):
    jobId = request.args.get('jobId')
    if jobId:
        applications = Application.query.filter_by(jobId = jobId).all()
    drives = JobPosition.query.filter_by(companyId = companyId).all()
    for drive in drives:
        applications = []
        application = Application.query.filter_by(jobId = drive.jobId).first()
        applications.append(application)

    return render_template('./company/viewApplications', applications = applications,companyId = companyId )

@app.route('/company/<int:companyId>/viewApplications/<int:applicationId>')
def updateApplicationStatus(companyId, applicationId):
    updatedStatus = request.args['status']
    application = Application.query.filter_by(applicationId = applicationId).first_or_404()
    application.status = updatedStatus
    db.session.commit()
    return redirect(url_for('showApplications', companyId = companyId))

@app.route('/company/<int:companyId>/closeDrive/<int:jobId>')
def closeDrive(companyId, jobId):
    job = JobPosition.query.filter_by(jobId = jobId).first_or_404()
    job.active = False
    db.session.commit()
    return redirect(url_for('showDrives', companyId = companyId ))

#students login routes 
@app.route('/student/<int:studentId>/dashboard')
def showStudentDash(studentId):
    student = Student.query.filter_by(studentId = studentId).first()
    return render_template('./student/dashboard.html', student = student)
if __name__ == "__main__":
    app.run(debug=True)