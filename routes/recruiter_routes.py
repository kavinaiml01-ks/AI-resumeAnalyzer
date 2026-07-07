from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from models import db
from models.job import Job
from models.application import Application
from utils.skill_matcher import rank_candidates

recruiter_bp = Blueprint("recruiter", __name__, url_prefix="/recruiter")


def recruiter_only():
    if not current_user.is_authenticated or not hasattr(current_user, "company_name"):
        abort(403)


@recruiter_bp.route("/dashboard")
@login_required
def dashboard():
    recruiter_only()
    jobs = Job.query.filter_by(recruiter_id=current_user.id).all()
    total_jobs = len(jobs)
    job_ids = [j.id for j in jobs]
    total_applicants = Application.query.filter(Application.job_id.in_(job_ids)).count() if job_ids else 0

    top_candidates = (
        Application.query.filter(Application.job_id.in_(job_ids))
        .order_by(Application.match_score.desc())
        .limit(5)
        .all()
        if job_ids else []
    )

    shortlisted = (
        Application.query.filter(Application.job_id.in_(job_ids), Application.application_status == "Shortlisted").count()
        if job_ids else 0
    )

    return render_template(
        "recruiter/dashboard.html",
        jobs=jobs,
        total_jobs=total_jobs,
        total_applicants=total_applicants,
        top_candidates=top_candidates,
        shortlisted=shortlisted,
    )


@recruiter_bp.route("/profile")
@login_required
def profile():
    recruiter_only()
    return render_template("recruiter/profile.html")


@recruiter_bp.route("/jobs/create", methods=["GET", "POST"])
@login_required
def create_job():
    recruiter_only()
    if request.method == "POST":
        job = Job(
            recruiter_id=current_user.id,
            title=request.form.get("title", "").strip(),
            description=request.form.get("description", "").strip(),
            required_skills=request.form.get("required_skills", "").strip(),
            experience=request.form.get("experience", "").strip(),
            salary=request.form.get("salary", "").strip(),
            location=request.form.get("location", "").strip(),
        )
        db.session.add(job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for("recruiter.dashboard"))

    return render_template("recruiter/job_form.html", job=None)


@recruiter_bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@login_required
def edit_job(job_id):
    recruiter_only()
    job = Job.query.get_or_404(job_id)
    if job.recruiter_id != current_user.id:
        abort(403)

    if request.method == "POST":
        job.title = request.form.get("title", "").strip()
        job.description = request.form.get("description", "").strip()
        job.required_skills = request.form.get("required_skills", "").strip()
        job.experience = request.form.get("experience", "").strip()
        job.salary = request.form.get("salary", "").strip()
        job.location = request.form.get("location", "").strip()
        db.session.commit()
        flash("Job updated successfully!", "success")
        return redirect(url_for("recruiter.dashboard"))

    return render_template("recruiter/job_form.html", job=job)


@recruiter_bp.route("/jobs/<int:job_id>/delete", methods=["POST"])
@login_required
def delete_job(job_id):
    recruiter_only()
    job = Job.query.get_or_404(job_id)
    if job.recruiter_id != current_user.id:
        abort(403)
    db.session.delete(job)
    db.session.commit()
    flash("Job deleted.", "info")
    return redirect(url_for("recruiter.dashboard"))


@recruiter_bp.route("/jobs/<int:job_id>/applicants")
@login_required
def view_applicants(job_id):
    recruiter_only()
    job = Job.query.get_or_404(job_id)
    if job.recruiter_id != current_user.id:
        abort(403)

    applications = Application.query.filter_by(job_id=job.id).all()
    ranked = rank_candidates(applications)

    return render_template("recruiter/applicants.html", job=job, ranked=ranked)


@recruiter_bp.route("/applications/<int:application_id>/shortlist", methods=["POST"])
@login_required
def shortlist(application_id):
    recruiter_only()
    application = Application.query.get_or_404(application_id)
    if application.job.recruiter_id != current_user.id:
        abort(403)

    application.application_status = "Shortlisted"
    db.session.commit()
    flash("Candidate shortlisted.", "success")
    return redirect(url_for("recruiter.view_applicants", job_id=application.job_id))


@recruiter_bp.route("/applications/<int:application_id>/reject", methods=["POST"])
@login_required
def reject(application_id):
    recruiter_only()
    application = Application.query.get_or_404(application_id)
    if application.job.recruiter_id != current_user.id:
        abort(403)

    application.application_status = "Rejected"
    db.session.commit()
    flash("Candidate rejected.", "info")
    return redirect(url_for("recruiter.view_applicants", job_id=application.job_id))


@recruiter_bp.route("/candidates/search")
@login_required
def search_candidates():
    recruiter_only()
    skill = request.args.get("skill", "").strip().lower()
    results = []
    if skill:
        applications = Application.query.join(Job).filter(Job.recruiter_id == current_user.id).all()
        for app in applications:
            if app.resume and skill in (app.resume.extracted_skills or "").lower():
                results.append(app)
    return render_template("recruiter/search_candidates.html", results=results, skill=skill)
