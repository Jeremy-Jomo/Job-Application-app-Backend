from models import db ,User,Job,Application
from flask import Flask,request ,jsonify

from flask_migrate import Migrate
from sqlalchemy_serializer import SerializerMixin


app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate = Migrate(app, db)

#route tester
@app.route("/")
def home():
    return "<h1>JOMO THE GOAT</h1>"


#USER routes
@app.route("/users",methods=["GET"])
def get_users ():
    users = User.query.all()
    return [user.to_dict(only=("id", "username", "email", "role")) for user in users], 200

@app.route("/users/<int:id>")
def get_user_by_id(id):
    user = User.query.get(id)
    return user.to_dict(only=("id", "username", "email", "role")),200

@app.route("/users",methods=["POST"])
def create_user():
    data = request.get_json()

    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error":"username, email and password are required"})
    new_user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role=data.get("role", "jobseeker")  # default role
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify(new_user.to_dict(only=("id", "username", "email", "role"))),201

#JOB routes
@app.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = Job.query.all()
    return [job.to_dict(only=("id", "title", "description", "company", "location", "user_id")) for job in jobs], 200


@app.route("/jobs", methods=["POST"])
def create_job():
    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    company = data.get("company")
    location = data.get("location")
    user_id = data.get("user_id")

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    employer = User.query.get(user_id)
    if not employer or employer.role != "employer":
        return jsonify({"error": "Invalid employer"}), 400

    job = Job(title=title, description=description, company=company,
              location=location, user_id=user_id)
    db.session.add(job)
    db.session.commit()
    return [job.to_dict(only=("id", "title", "description", "company", "location", "user_id")) for job in jobs], 200


@app.route("/jobs/<int:id>", methods=["GET"])
def get_job(id):
    job = Job.query.get_or_404(id)
    return jsonify(job.to_dict(only=("id", "title", "description", "company", "location", "user_id")))



@app.route("/jobs/<int:id>", methods=["PUT"])
def update_job(id):
    job = Job.query.get_or_404(id)
    data = request.get_json()
    job.title = data.get("title", job.title)
    job.description = data.get("description", job.description)
    job.company = data.get("company", job.company)
    job.location = data.get("location", job.location)
    db.session.commit()
    return jsonify(job.to_dict(only=("id", "title", "description", "company", "location", "user_id")))

@app.route("/jobs/<int:id>", methods=["DELETE"])
def delete_job(id):
    job = Job.query.get_or_404(id)
    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted"})

#APPLICATIONS routes
@app.route("/applications", methods = ["GET"])
def get_applications():
    applications = Application.query.all()
    return jsonify([application.to_dict() for application in applications])

@app.route("applications", method = ["POST"])
def create_application():
    data = request.get_json()

    if not data.get("user_id") or not data.get("job_id") or not data.get("cover_letter"):
        return jsonify({"error": "user id, job id and cover letter required"}), 400

    new_application = Application(
        user_id = data["user_id"]
        job_id = data["job_id"]
        cover_letter =  data["cover_letter"]
        status = data.get("status", "pending")
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify(new_application.to_dict()), 201

@app.route("/jobs/<int:job_id>/applications", methods = ["GET"])
def get_applications_by_id(job_id):
    apps = Application.query.filter_by(job_id=job_id).all()
    return jsonify([application.to_dict() for application in apps])


if __name__ == "__main__":
    app.run(port=5000, debug=True)


