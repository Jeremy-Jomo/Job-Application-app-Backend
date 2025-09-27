# seed.py
from app import app
from server.models import  User, Job, Application
from faker import Faker
import random
from extensions import db

fake = Faker()

with app.app_context():
    print("Clearing database...")
    db.drop_all()
    db.create_all()

    print("Seeding users...")
    users = []
    for i in range(5):
        user = User(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            role=random.choice([ "Job Seeker", "Employer"]),
            password="password123"
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    print("Seeding jobs...")
    jobs = []
    for i in range(8):
        job = Job(
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            location=fake.city(),
            company=fake.company(),
            user_id=random.choice(users).id  # jobseeker/employer
        )
        jobs.append(job)
    db.session.add_all(jobs)
    db.session.commit()

    print("Seeding applications...")
    applications = []
    for i in range(15):
        application = Application(
            status=random.choice(["pending", "accepted", "rejected"]),
            cover_letter=fake.paragraph(nb_sentences=3),
            user_id=random.choice(users).id,  # applicant
            job_id=random.choice(jobs).id
        )
        applications.append(application)
    db.session.add_all(applications)
    db.session.commit()

    print("Done seeding database!")
