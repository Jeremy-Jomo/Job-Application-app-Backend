from server.models import User, Job, Application
from flask import Flask, request, jsonify, session, g
from flask_migrate import Migrate
from sqlalchemy_serializer import SerializerMixin
from flask_cors import CORS
from server.extensions import db, bcrypt
import os

app = Flask(__name__)
app.secret_key = "super-secret-key"
app.config.update(
    SESSION_COOKIE_SAMESITE="None",
    SESSION_COOKIE_SECURE=True
)

app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = False  # ⚠️ allow cookies over http://localhost

# 🔧 CRITICAL FIX: Add your actual frontend domain
CORS(app, supports_credentials=True, origins=[
    "http://localhost:5173",
    "https://your-frontend-domain.vercel.app",  # Replace with your actual frontend URL
    "https://your-frontend-domain.netlify.app"   # Or whatever your frontend domain is
])

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
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
        g.user = User.query.filter_by(id=user_id).first()
        print("Loaded user:", g.user)  # Debug


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
            "role": user.role,
            "email": user.email
        }
    }), 200


# 🔧 CRITICAL FIX: Don't return 401 when no session exists
@app.route("/check-session", methods=["GET"])
def check_session():
    if not g.user:
        return jsonify({"logged_in": False}), 200  # Changed from 401 to 200

    return jsonify({
        "logged_in": True,
        "user": {
            "id": g.user.id,
            "username": g.user.username,
            "role": g.user.role,
            "email": g.user.email,
        }
    }), 200


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()  # 🔧 Clear entire session instead of just popping user_id
    return jsonify({"message": "Logged out"}), 200


# ----------------------
# User routes
# ----------------------
@app.route("/users", methods=["GET"])
def get_users():
    users = User.query.all()
    return jsonify([user.to_dict(only=("id", "username", "email", "role")) for user in users]), 200


@app.route("/users/<int:id>")
def get_user_by_id(id):
    user = User.query.get(id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict(only=("id", "username", "email", "role"))), 200


@app.route("/users", methods=["POST"])
def create_user():
    data = request.get_json()
    existing_user = User.query.filter_by(email=data["email"]).first()
    if existing_user:
        return jsonify({"success": False, "message": "Email already registered"}), 400

    if not data.get("username") or not data.get("email") or not data.get("password"):
        return jsonify({"error": "username, email and password are required"}), 400

    new_user = User(
        username=data["username"],
        email=data["email"],
        password=data["password"],
        role=data.get("role", "jobseeker")
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
    return jsonify([
        job.to_dict(only=("id", "title", "description", "company", "location", "user_id"))
        for job in jobs
    ]), 200


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
        user_id=g.user.id
    )
    db.session.add(job)
    db.session.commit()

    return jsonify(job.to_dict(only=("id", "title", "description", "company", "location", "user_id"))), 201


@app.route("/jobs/<int:id>", methods=["GET"])
def get_job(id):
    job = Job.query.get_or_404(id)
    return jsonify(job.to_dict(only=("id", "title", "description", "company", "location", "user_id"))), 200


@app.route("/jobs/<int:id>", methods=["PATCH"])
def update_job(id):
    if not g.user:
        return jsonify({"error": "Unauthorized"}), 401

    job = Job.query.get_or_404(id)
    if job.user_id != g.user.id:
        return jsonify({"error": "Forbidden – you don't own this job"}), 403

    data = request.get_json()
    job.title = data.get("title", job.title)
    job.description = data.get("description", job.description)
    job.company = data.get("company", job.company)
    job.location = data.get("location", job.location)

    db.session.commit()
    return jsonify(job.to_dict(only=("id", "title", "description", "company", "location", "user_id"))), 200


@app.route("/jobs/<int:id>", methods=["DELETE"])
def delete_job(id):
    if not g.user:
        return jsonify({"error": "Unauthorized"}), 401

    job = Job.query.get_or_404(id)
    if job.user_id != g.user.id:
        return jsonify({"error": "Forbidden – you don't own this job"}), 403

    db.session.delete(job)
    db.session.commit()
    return jsonify({"message": "Job deleted successfully"}), 200


# ----------------------
# Applications routes
# ----------------------
# 🔧 FIXED: Add username from user relationship
@app.route("/applications", methods=["GET"])
def get_applications():
    applications = Application.query.all()
    result = []
    for app in applications:
        app_data = app.to_dict()
        # Add username from user relationship if it exists
        if hasattr(app, 'user') and app.user:
            app_data['username'] = app.user.username
        result.append(app_data)
    return jsonify(result)


@app.route("/applications", methods=["POST"])
def create_application():
    data = request.get_json()

    if not data.get("user_id") or not data.get("job_id") or not data.get("cover_letter"):
        return jsonify({"error": "user_id, job_id and cover_letter are required"}), 400

    # 🔧 Check for duplicate applications
    existing_app = Application.query.filter_by(
        user_id=data["user_id"],
        job_id=data["job_id"]
    ).first()
    if existing_app:
        return jsonify({"error": "You have already applied for this job"}), 400

    new_application = Application(
        user_id=data["user_id"],
        job_id=data["job_id"],
        cover_letter=data["cover_letter"],
        name=data.get("name"),
        email=data.get("email"),
        status=data.get("status", "pending")
    )

    db.session.add(new_application)
    db.session.commit()

    return jsonify(new_application.to_dict()), 201


# 🔧 FIXED: Add username from user relationship
@app.route("/jobs/<int:job_id>/applications", methods=["GET"])
def get_applications_by_id(job_id):
    apps = Application.query.filter_by(job_id=job_id).all()
    result = []
    for app in apps:
        app_data = app.to_dict()
        # Add username from user relationship if it exists
        if hasattr(app, 'user') and app.user:
            app_data['username'] = app.user.username
        result.append(app_data)
    return jsonify(result)


@app.route("/users/<int:user_id>/applications", methods=["GET"])
def get_user_applications(user_id):
    apps = Application.query.filter_by(user_id=user_id).all()
    result = []

    for a in apps:
        job_info = None
        if hasattr(a, 'job') and a.job:
            job_info = {
                "title": a.job.title,
                "company": a.job.company,
                "location": a.job.location
            }

        result.append({
            "id": a.id,
            "user_id": a.user_id,
            "job_id": a.job_id,
            "cover_letter": a.cover_letter,
            "status": a.status,
            "name": a.name,
            "email": a.email,
            "job": job_info
        })

    return jsonify(result), 200


@app.route("/applications/<int:application_id>", methods=["PATCH"])
def update_application(application_id):
    application = Application.query.get_or_404(application_id)
    data = request.get_json()

    new_status = data.get("status")
    if new_status not in ["pending", "accepted", "rejected"]:
        return jsonify({"error": "Invalid status"}), 400

    application.status = new_status
    db.session.commit()

    # Return updated application with username if available
    app_data = application.to_dict()
    if hasattr(application, 'user') and application.user:
        app_data['username'] = application.user.username

    return jsonify(app_data), 200


@app.route('/applications/<int:id>', methods=['DELETE'])
def delete_application(id):
    app = Application.query.get_or_404(id)
    db.session.delete(app)
    db.session.commit()
    return jsonify({"message": "Application deleted"}), 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=True
    )