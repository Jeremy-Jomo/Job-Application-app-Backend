from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
from extensions import db, bcrypt

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",   # indexes
        "uq": "uq_%(table_name)s_%(column_0_name)s",   # unique constraints
        "ck": "ck_%(table_name)s_%(constraint_name)s", # check constraints
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s", # foreign keys
        "pk": "pk_%(table_name)s"                      # primary keys
    }
)



#creates user model
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    role = db.Column(db.String, nullable=False, default='job-seeker')
    _password = db.Column("password", db.String, nullable=False)

    #relatioships
    jobs = db.relationship("Job", back_populates="poster", cascade="all, delete-orphan")
    applications = db.relationship("Application", back_populates="applicant", cascade="all, delete-orphan")

    #serialization
    serialize_rules = ("-jobs.poster", "-applications.applicant",)

      # password property
    @property
    def password(self):
        raise AttributeError("Password is write-only.")

    @password.setter
    def password(self, plaintext_password):
        self._password = bcrypt.generate_password_hash(plaintext_password).decode("utf-8")

    def check_password(self, plaintext_password):
        return bcrypt.check_password_hash(self._password, plaintext_password)

#creates job model
class Job (db.Model, SerializerMixin):
    __tablename__ = 'jobs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    company = db.Column(db.String, nullable=False)

    #foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    #relationships
    poster = db.relationship("User", back_populates="jobs")
    applications = db.relationship("Application", back_populates="job", cascade="all, delete-orphan")

    #serialization
    serialize_rules = ("-poster.jobs", "-applications.job",)

#creates application model
class Application(db.Model, SerializerMixin):
    __tablename__ = 'applications'

    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False, default='pending')
    cover_letter = db.Column(db.String, nullable=True)

    #foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)

    #relationships
    applicant = db.relationship("User", back_populates="applications")
    job = db.relationship("Job", back_populates="applications")

    #serialization
    serialize_rules = ("-applicant.applications", "-job.applications",)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "job_id": self.job_id,
            "cover_letter": self.cover_letter,
            "status": self.status,
            "job_title": self.job.title if self.job else None,
            "company": self.job.company if self.job else None,
            "location": self.job.location if self.job else None,
        }
