
from models import db, User, Admin, Student, Company, JobPosition, Application, Placement
from datetime import datetime
import random

def seed():
        print("Seeding database...")

        admin_user1 = User(username="admin1", passwordHash="admin123", role="admin")
        admin1 = Admin(name="Placement Officer", contactNumber=9876543210, user=admin_user1)

        admin_user2 = User(username="admin2", passwordHash="admin123", role="admin")
        admin2 = Admin(name="Assistant Admin", contactNumber=9123456780, user=admin_user2)

        db.session.add_all([admin1, admin2])


        company_names = [
            ("Google", "Technology"),
            ("TCS", "IT Services"),
            ("Infosys", "IT Services"),
            ("Amazon", "E-Commerce"),
            ("Microsoft", "Technology"),
            ("Wipro", "IT Services"),
        ]

        companies = []
        for name, industry in company_names:
            user = User(username=name.lower(), passwordHash="company123", role="company")
            company = Company(
                companyName=name,
                industry=industry,
                description=f"{name} is a leading company in {industry}.",
                companyEmail=f"hr@{name.lower()}.com",
                approved=random.choice([True, False]),
                user=user
            )
            companies.append(company)

        db.session.add_all(companies)


        departments = ["CSE", "IT", "ECE", "EEE", "MECH"]
        skills_list = ["Python, SQL", "Java, Spring", "C++, DSA", "Machine Learning", "Web Development"]

        students = []
        for i in range(1, 16):
            user = User(username=f"student{i}", passwordHash="student123", role="student")
            student = Student(
                name=f"Student {i}",
                contactNumber=9000000000 + i,
                deartment=random.choice(departments),
                resume="resume.pdf",
                experience=random.choice(["0 years", "1 year", "Internship"]),
                skills=random.choice(skills_list),
                user=user
            )
            students.append(student)

        db.session.add_all(students)

        db.session.commit()

        jobs = []
        for company in companies:
            if company.approved:
                for j in range(2):
                    job = JobPosition(
                        company=company,
                        driveName=f"{company.companyName} Drive {j+1}",
                        positionOpen=random.choice(["Software Engineer", "Data Analyst", "Backend Developer"]),
                        description="Exciting role in development team.",
                        skillsRequired="Python, SQL, DSA",
                        experienceRequired="0-1 years",
                        salary=random.choice(["6 LPA", "8 LPA", "10 LPA"]),
                        location=random.choice(["Chennai", "Bangalore", "Hyderabad"]),
                        active=True
                    )
                    jobs.append(job)

        db.session.add_all(jobs)
        db.session.commit()

        applications = []
        for student in students:
            applied_jobs = random.sample(jobs, k=min(3, len(jobs)))
            for job in applied_jobs:
                app_obj = Application(
                    student=student,
                    job=job,
                    status=random.choice(["Applied", "Shortlisted", "Rejected"])
                )
                applications.append(app_obj)

        db.session.add_all(applications)
        db.session.commit()

        # --------------------
        # FINAL PLACEMENTS (only shortlisted)
        # --------------------
        for app_obj in applications:
            if app_obj.status == "Shortlisted" and random.choice([True, False]):
                placement = Placement(
                    application=app_obj,
                    package=random.choice([600000, 800000, 1200000])
                )
                db.session.add(placement)

        db.session.commit()
        print("Seeding complete!")

if __name__ == "__main__":
    seed()