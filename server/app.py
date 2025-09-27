from server.models import User, Job, Application
from flask import Flask, request, jsonify, session, g
from flask_migrate import Migrate
from sqlalchemy_serializer import SerializerMixin
from flask_cors import CORS
from server.extensions import db, bcrypt

app = Flask(__name__)
app.secret_key = "super-secret-key"

CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)


# ----------------------
# Before request hook
# ----------------------
@app.before_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        g.user = User.query.get(user_id)


# ----------------------
# Route tester
# ----------------------
@app.route("/")
def home():
    return "<h1>JOMO THE GOAT</h1>"


# ----------------------
# Authentication
# ----------------------
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"success": False, "message": "Invalid username or password"}), 401

    # Store session
    session["user_id"] = user.id
    session["role"] = user.role

    return jsonify({
        "success": True,
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "role": user.role
        }
    }), 200


@app.route("/check-session", methods=["GET"])
def check_session():
    if not g.user:
        return jsonify({"logged_in": False}), 401

    return jsonify({
        "logged_in": True,
        "user": {
            "id": g.user.id,
            "username": g.user.username,
            "role": g.user.role
        }
    }), 200


@app.route("/logout", methods=["POST"])
def logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out"}), 200



# ----------------------
# User routes
# ----------------------
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return [user.to_dict(only=("id", "username", "email", "role")) for user in users], 200


@app.route("/users/<int:id>")
def get_user_by_id(id):
    user = User.query.get(id)
    return user.to_dict(only=("id", "username", "email", "role")), 200


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"success": False, "message": "Email already registered"}), 400

    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "username, email and password are required"})

    new_user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role=data.get("role", "jobseeker")  # default role
    )

    db.session.add(new_user)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "User created successfully",
        "user": new_user.to_dict(only=("id", "username", "email", "role"))
    }), 201


# ----------------------
# Job routes
# ----------------------
@app.route("/jobs", methods=["GET"])
def get_jobs():
    jobs = Job.query.all()
    return [job.to_dict(only=("id", "title", "description", "company", "location", "user_id")) for job in jobs], 200


@app.route("/jobs", methods=["POST"])
def create_job():
    if not g.user:
        return jsonify({"error": "Unauthorized"}), 401
    if g.user.role.lower() != "employer":
        return jsonify({"error": "Only employers can post jobs"}), 403

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")
    company = data.get("company")
    location = data.get("location")

    if not title or not description:
        return jsonify({"error": "Title and description are required"}), 400

    job = Job(
        title=title,
        description=description,
        company=company,
        location=location,
        user_id=g.user.id  # ✅ use logged-in employer
    )
    db.session.add(job)
    db.session.commit()
    return jsonify(job.to_dict(only=("id", "title", "description", "company", "location", "user_id"))), 201


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


# ----------------------
# Applications routes
# ----------------------
@app.route("/applications", methods=["GET"])
def get_applications():
    applications = Application.query.all()
    return jsonify([application.to_dict() for application in applications])


@app.route("/applications", methods=["POST"])
def create_application():
    data = request.get_json()

    # Validate required fields
    if not data.get("user_id") or not data.get("job_id") or not data.get("cover_letter"):
        return jsonify({"error": "user_id, job_id and cover_letter are required"}), 400

    new_application = Application(
        user_id=data["user_id"],
        job_id=data["job_id"],
        cover_letter=data["cover_letter"],
        status=data.get("status", "pending")
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify(new_application.to_dict()), 201


@app.route("/jobs/<int:job_id>/applications", methods=["GET"])
def get_applications_by_id(job_id):
    apps = Application.query.filter_by(job_id=job_id).all()
    return jsonify([application.to_dict() for application in apps])


@app.route("/users/<int:user_id>/applications", methods=["GET"])
def get_user_applications(user_id):
    apps = Application.query.filter_by(user_id=user_id).all()

    if not apps:
        return jsonify({"message": "No applications found for this user"}), 404

    return jsonify([a.to_dict() for a in apps]), 200


if __name__ == "__main__":
    app.run(port=5000, debug=True)
