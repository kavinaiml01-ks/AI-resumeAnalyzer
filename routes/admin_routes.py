from collections import Counter
from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from models import db
from models.user import User
from models.recruiter import Recruiter
from models.job import Job
from models.application import Application
from models.resume import Resume

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def admin_only():
    if not current_user.is_authenticated or getattr(current_user, "role", None) != "admin":
        abort(403)


@admin_bp.route("/dashboard")
@login_required
def dashboard():
    admin_only()
    total_users = User.query.filter_by(role="candidate").count()
    total_recruiters = Recruiter.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()

    # Most popular skills across all job postings
    all_jobs = Job.query.all()
    skill_counter = Counter()
    for job in all_jobs:
        skill_counter.update(job.skills_list())
    popular_skills = skill_counter.most_common(8)

    # Monthly application chart data (last 6 months by month number)
    apps = Application.query.all()
    month_counter = Counter()
    for app in apps:
        key = app.applied_at.strftime("%b %Y") if app.applied_at else "Unknown"
        month_counter[key] += 1
    monthly_data = sorted(month_counter.items())

    return render_template(
        "admin/dashboard.html",
        total_users=total_users,
        total_recruiters=total_recruiters,
        total_jobs=total_jobs,
        total_applications=total_applications,
        popular_skills=popular_skills,
        monthly_data=monthly_data,
    )


@admin_bp.route("/candidates")
@login_required
def manage_candidates():
    admin_only()
    candidates = User.query.filter_by(role="candidate").order_by(User.created_at.desc()).all()
    return render_template("admin/manage_candidates.html", candidates=candidates)


@admin_bp.route("/candidates/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_candidate(user_id):
    admin_only()
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash("Candidate account removed.", "info")
    return redirect(url_for("admin.manage_candidates"))


@admin_bp.route("/recruiters")
@login_required
def manage_recruiters():
    admin_only()
    recruiters = Recruiter.query.order_by(Recruiter.created_at.desc()).all()
    return render_template("admin/manage_recruiters.html", recruiters=recruiters)


@admin_bp.route("/recruiters/<int:recruiter_id>/delete", methods=["POST"])
@login_required
def delete_recruiter(recruiter_id):
    admin_only()
    recruiter = Recruiter.query.get_or_404(recruiter_id)
    db.session.delete(recruiter)
    db.session.commit()
    flash("Recruiter account removed.", "info")
    return redirect(url_for("admin.manage_recruiters"))


@admin_bp.route("/jobs")
@login_required
def manage_jobs():
    admin_only()
    jobs = Job.query.order_by(Job.created_at.desc()).all()
    return render_template("admin/manage_jobs.html", jobs=jobs)


@admin_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    admin_only()
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash("Job post removed.", "info")
    return redirect(url_for("admin.manage_jobs"))


@admin_bp.route("/applications")
@login_required
def manage_applications():
    admin_only()
    applications = Application.query.order_by(Application.applied_at.desc()).all()
    return render_template("admin/manage_applications.html", applications=applications)


@admin_bp.route("/ai-statistics")
@login_required
def ai_statistics():
    admin_only()
    total_resumes = Resume.query.count()
    avg_strength = db.session.query(db.func.avg(Resume.match_score)).scalar() or 0
    avg_application_score = db.session.query(db.func.avg(Application.match_score)).scalar() or 0

    return render_template(
        "admin/ai_statistics.html",
        total_resumes=total_resumes,
        avg_strength=round(avg_strength, 2),
        avg_application_score=round(avg_application_score, 2),
    )
