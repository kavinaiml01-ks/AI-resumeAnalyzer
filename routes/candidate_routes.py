import os
from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
    current_app, send_file, abort
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from models import db
from models.job import Job
from models.resume import Resume
from models.application import Application
from utils.resume_parser import allowed_file, parse_resume
from utils.skill_matcher import calculate_final_score
from utils.report_generator import generate_resume_report

candidate_bp = Blueprint("candidate", __name__, url_prefix="/candidate")


def candidate_only():
    if not current_user.is_authenticated or getattr(current_user, "role", None) != "candidate":
        abort(403)


@candidate_bp.route("/dashboard")
@login_required
def dashboard():
    candidate_only()
    total_applications = Application.query.filter_by(user_id=current_user.id).count()
    latest_resume = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    recommended_jobs = []
    if latest_resume:
        all_jobs = Job.query.filter_by(is_active=True).limit(20).all()
        scored = []
        for job in all_jobs:
            result = calculate_final_score(latest_resume.skills_list(), job.skills_list())
            scored.append((job, result["final_score"]))
        scored.sort(key=lambda x: x[1], reverse=True)
        recommended_jobs = scored[:5]

    recent_applications = (
        Application.query.filter_by(user_id=current_user.id)
        .order_by(Application.applied_at.desc())
        .limit(5)
        .all()
    )

    return render_template(
        "candidate/dashboard.html",
        total_applications=total_applications,
        latest_resume=latest_resume,
        recommended_jobs=recommended_jobs,
        recent_applications=recent_applications,
    )


@candidate_bp.route("/profile")
@login_required
def profile():
    candidate_only()
    return render_template("candidate/profile.html")


@candidate_bp.route("/resume/upload", methods=["GET", "POST"])
@login_required
def upload_resume():
    candidate_only()
    if request.method == "POST":
        file = request.files.get("resume")
        if not file or file.filename == "":
            flash("Please choose a PDF file to upload.", "danger")
            return redirect(url_for("candidate.upload_resume"))

        if not allowed_file(file.filename, current_app.config["ALLOWED_EXTENSIONS"]):
            flash("Only PDF files are allowed.", "danger")
            return redirect(url_for("candidate.upload_resume"))

        filename = secure_filename(f"user{current_user.id}_{file.filename}")
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        parsed = parse_resume(filepath)

        resume = Resume(
            user_id=current_user.id,
            filename=filename,
            raw_text=parsed["raw_text"],
            extracted_skills=", ".join(parsed["skills"]),
            match_score=parsed["strength_score"],
        )
        db.session.add(resume)
        db.session.commit()

        flash("Resume uploaded and analyzed successfully!", "success")
        return redirect(url_for("candidate.resume_analysis", resume_id=resume.id))

    return render_template("candidate/upload_resume.html")


@candidate_bp.route("/resume/<int:resume_id>/analysis")
@login_required
def resume_analysis(resume_id):
    candidate_only()
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)
    return render_template("candidate/resume_analysis.html", resume=resume)


@candidate_bp.route("/resume/<int:resume_id>/download-report")
@login_required
def download_report(resume_id):
    candidate_only()
    resume = Resume.query.get_or_404(resume_id)
    if resume.user_id != current_user.id:
        abort(403)

    output_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"], f"report_{resume.id}.pdf"
    )
    generate_resume_report(output_path, current_user.fullname, resume)
    return send_file(output_path, as_attachment=True, download_name=f"Resume_Report_{resume.id}.pdf")


@candidate_bp.route("/jobs")
@login_required
def job_listing():
    candidate_only()
    search = request.args.get("q", "").strip()
    location = request.args.get("location", "").strip()

    query = Job.query.filter_by(is_active=True)
    if search:
        query = query.filter(Job.title.ilike(f"%{search}%"))
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))

    jobs = query.order_by(Job.created_at.desc()).all()
    return render_template("candidate/job_listing.html", jobs=jobs, search=search, location=location)


@candidate_bp.route("/jobs/<int:job_id>/apply", methods=["POST"])
@login_required
def apply_job(job_id):
    candidate_only()
    job = Job.query.get_or_404(job_id)

    existing = Application.query.filter_by(user_id=current_user.id, job_id=job.id).first()
    if existing:
        flash("You have already applied for this job.", "warning")
        return redirect(url_for("candidate.job_listing"))

    latest_resume = (
        Resume.query.filter_by(user_id=current_user.id)
        .order_by(Resume.uploaded_at.desc())
        .first()
    )
    if not latest_resume:
        flash("Please upload your resume before applying.", "warning")
        return redirect(url_for("candidate.upload_resume"))

    result = calculate_final_score(
        latest_resume.skills_list(), job.skills_list(),
        resume_text=latest_resume.raw_text or "", job_description=job.description or "",
    )

    application = Application(
        user_id=current_user.id,
        job_id=job.id,
        resume_id=latest_resume.id,
        match_score=result["final_score"],
        matching_skills=", ".join(result["matching_skills"]),
        missing_skills=", ".join(result["missing_skills"]),
        application_status="Applied",
    )
    db.session.add(application)
    db.session.commit()

    flash(f"Application submitted! Match Score: {result['final_score']}%", "success")
    return redirect(url_for("candidate.my_applications"))


@candidate_bp.route("/applications")
@login_required
def my_applications():
    candidate_only()
    applications = (
        Application.query.filter_by(user_id=current_user.id)
        .order_by(Application.applied_at.desc())
        .all()
    )
    return render_template("candidate/applications.html", applications=applications)
