# server/seed.py
from .app import app
from .models import User, Job, Application
from .extensions import db
from faker import Faker
import random

fake = Faker()

with app.app_context():
    print("Clearing database...")
    # Uncomment the next line if you really want to drop all tables
    # db.drop_all()

    db.create_all()
    print("Database tables created successfully!")

    # Seed Users
    print("Seeding users...")
    users = []
    for _ in range(5):
        user = User(
            username=fake.unique.user_name(),
            email=fake.unique.email(),
            role=random.choice(["Job Seeker", "Employer"]),
            password="password123"
        )
        users.append(user)
    db.session.add_all(users)
    db.session.commit()

    # Seed Jobs
    print("Seeding jobs...")
    jobs = []
    for _ in range(8):
        job = Job(
            title=fake.job(),
            description=fake.text(max_nb_chars=200),
            location=fake.city(),
            company=fake.company(),
            user_id=random.choice(users).id  # assign to random user
        )
        jobs.append(job)
    db.session.add_all(jobs)
    db.session.commit()

    # Seed Applications
    print("Seeding applications...")
    applications = []
    for _ in range(15):
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
