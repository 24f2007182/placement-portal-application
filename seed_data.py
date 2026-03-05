
from models import Admin, db
from models import User, Student, Company, JobPosition, Application
from werkzeug.security import generate_password_hash
from datetime import datetime
import random


def seed():

    if User.query.first():
        return

    admin_user = User(
        username="admin",
        passwordHash =generate_password_hash("admin123"),
        role="Admin",
        active=True
    )

    db.session.add(admin_user)
    db.session.flush()

    admin = Admin(
        userId=admin_user.userId,
        name="System Administrator",
        contactNumber = "827456738290"
    )

    db.session.add(admin)


    companies_data = [
        ("Google", "Technology"),
        ("Microsoft", "Technology"),
        ("Amazon", "E-commerce"),
        ("Infosys", "IT Services"),
        ("TCS", "IT Services"),
        ("Accenture", "Consulting"),
        ("IBM", "Technology"),
        ("Flipkart", "E-commerce"),
        ("Deloitte", "Consulting"),
        ("Wipro", "IT Services")
    ]

    companies = []

    for name, industry in companies_data:

        user = User(username = name.lower(),passwordHash = generate_password_hash("company123"), role ="Company", active=True)

        db.session.add(user)
        db.session.flush()

        company = Company(
            userId=user.userId,
            companyName=name,
            industry=industry,
            description=f"{name} is a leading company in the {industry} industry, known for innovation and global technology solutions.",
            companyEmail=f"careers@{name.lower()}.com",
            approved=random.choice([True,False])
        )

        db.session.add(company)
        companies.append(company)

    student_names = [
        "Aarav Sharma",
        "Riya Patel",
        "Aditya Verma",
        "Sneha Kapoor",
        "Rahul Mehta",
        "Ananya Iyer",
        "Karan Singh",
        "Neha Gupta",
        "Arjun Nair",
        "Priya Desai",
        "Vikram Joshi",
        "Simran Kaur",
        "Rohan Das",
        "Meera Pillai",
        "Yash Shah"
    ]

    departments = [
        "Computer Science",
        "Information Technology",
        "Electronics and Communication",
        "Mechanical Engineering",
        "Data Science"
    ]

    skills_list = [
        "Python, SQL, Flask",
        "Java, Spring Boot, REST APIs",
        "React, JavaScript, Node.js",
        "Machine Learning, Python, Pandas",
        "C++, Data Structures, Algorithms",
        "HTML, CSS, JavaScript",
        "AWS, Docker, Kubernetes"
    ]

    experience_levels = [
        "Fresher",
        "0-1 Years",
        "1-3 Years"
    ]

    students = []

    for i, name in enumerate(student_names):

        user = User(
            username=f"student{i+1}",
            passwordHash = generate_password_hash("student123"),
            role="Student",
            active=True
        )

        db.session.add(user)
        db.session.flush()

        student = Student(
            name=name,
            department=random.choice(departments),
            contactNumber=f"98{random.randint(10000000,99999999)}",
            skills=random.choice(skills_list),
            experience=random.choice(experience_levels),
            resume="./static/resumes/resume.pdf",
            userId=user.userId
        )

        db.session.add(student)
        students.append(student)

    job_titles = [
        "Software Engineer",
        "Backend Developer",
        "Frontend Developer",
        "Full Stack Developer",
        "Data Analyst",
        "Machine Learning Engineer",
        "Cloud Engineer"
    ]

    job_descriptions = [
        "Design and develop scalable software solutions while collaborating with cross-functional engineering teams to deliver high quality applications.",
        "Build and maintain backend services, APIs, and databases ensuring reliability, performance, and security of large scale systems.",
        "Develop responsive and user-friendly web interfaces using modern frontend frameworks while ensuring seamless user experience.",
        "Work across the full technology stack to develop robust applications including backend services, APIs, and interactive frontend systems.",
        "Analyze large datasets to uncover insights, build reports, and support data-driven decision making across business teams.",
        "Develop and deploy machine learning models to solve real-world problems using modern data science and AI tools.",
        "Design, implement, and maintain cloud infrastructure while ensuring scalability, security, and reliability of applications."
    ]

    jobs = []

    for company in companies:

        for i in range(2):

            title_index = random.randint(0, len(job_titles) - 1)

            job = JobPosition(
                driveName=f"{company.companyName} Campus Recruitment Drive {i+1}",
                positionOpen=job_titles[title_index],
                description= job_descriptions[title_index],
                skillsRequired=random.choice(skills_list),
                salary=random.randint(6, 18) * 100000,
                experienceRequired = random.choice(['Fresher', '0-1 years']),
                location=random.choice(["Bangalore", "Hyderabad", "Mumbai", "Pune", "Chennai"]),
                companyId=company.companyId,
                active = random.choice([True, False])
            )

            db.session.add(job)
            jobs.append(job)

    db.session.flush()

    statuses = ["Applied", "Shortlisted", "Rejected", "Accepted"]

    for student in students:

        applied_jobs = random.sample(jobs, 3)

        for job in applied_jobs:

            application = Application(
                studentId=student.studentId,
                jobId=job.jobId,
                status=random.choice(statuses),
                appliedOn=datetime.now()
            )

            db.session.add(application)

    db.session.commit()

if __name__ == "__main__":
    seed()