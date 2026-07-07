from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from models import db
from models.user import User
from models.recruiter import Recruiter

auth_bp = Blueprint("auth", __name__)


# ---------------- Candidate Auth ----------------

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fullname = request.form.get("fullname", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not fullname or not email or not password:
            flash("Please fill in all fields.", "danger")
            return redirect(url_for("auth.register"))

        if User.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("auth.register"))

        user = User(fullname=fullname, email=email, role="candidate")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash(f"Welcome back, {user.fullname}!", "success")
            if user.role == "admin":
                return redirect(url_for("admin.dashboard"))
            return redirect(url_for("candidate.dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("auth.login"))

    return render_template("login.html")


# ---------------- Recruiter Auth ----------------

@auth_bp.route("/recruiter/register", methods=["GET", "POST"])
def recruiter_register():
    if request.method == "POST":
        company_name = request.form.get("company_name", "").strip()
        contact_person = request.form.get("contact_person", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        industry = request.form.get("industry", "").strip()

        if not company_name or not email or not password:
            flash("Please fill in all required fields.", "danger")
            return redirect(url_for("auth.recruiter_register"))

        if Recruiter.query.filter_by(email=email).first():
            flash("An account with this email already exists.", "warning")
            return redirect(url_for("auth.recruiter_register"))

        recruiter = Recruiter(
            company_name=company_name,
            contact_person=contact_person,
            email=email,
            industry=industry,
        )
        recruiter.set_password(password)
        db.session.add(recruiter)
        db.session.commit()

        flash("Recruiter account created! Please log in.", "success")
        return redirect(url_for("auth.recruiter_login"))

    return render_template("recruiter_register.html")


@auth_bp.route("/recruiter/login", methods=["GET", "POST"])
def recruiter_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        recruiter = Recruiter.query.filter_by(email=email).first()
        if recruiter and recruiter.check_password(password):
            login_user(recruiter)
            flash(f"Welcome back, {recruiter.company_name}!", "success")
            return redirect(url_for("recruiter.dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("auth.recruiter_login"))

    return render_template("recruiter_login.html")


# ---------------- Shared ----------------

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("main.home"))
