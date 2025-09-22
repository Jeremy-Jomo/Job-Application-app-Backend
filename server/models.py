from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(
    naming_convention={
        "ix": "ix_%(table_name)s_%(column_0_name)s",   # indexes
        "uq": "uq_%(table_name)s_%(column_0_name)s",   # unique constraints
        "ck": "ck_%(table_name)s_%(constraint_name)s", # check constraints
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s", # foreign keys
        "pk": "pk_%(table_name)s"                      # primary keys
    }
)

db = SQLAlchemy(metadata=metadata)

#creates user model
class User(db.Model, SerializerMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    role = db.Column(db.String, nullable=False, default='user')
    password = db.Column(db.String, nullable=False)

#creates job model
class Job (db.Model, SerializerMixin):
    __tablename__ = 'jobs'



    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    company = db.Column(db.String, nullable=False)
    # confirm the relationship(sharon)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

#creates application model
class Application(db.Model, SerializerMixin):
    __tablename__ = 'applications'



    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String, nullable=False, default='pending')
    cover_letter = db.Column(db.String, nullable=True)
    # confirm the relationship(sharon)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)


