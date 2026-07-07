from datetime import datetime
from . import db


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    resume_id = db.Column(db.Integer, db.ForeignKey("resumes.id"))

    match_score = db.Column(db.Float, default=0.0)
    matching_skills = db.Column(db.Text)   # comma-separated
    missing_skills = db.Column(db.Text)    # comma-separated
    application_status = db.Column(db.String(30), default="Applied")  # Applied / Shortlisted / Rejected
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)

    resume = db.relationship("Resume")

    def matching_list(self):
        return [s.strip() for s in (self.matching_skills or "").split(",") if s.strip()]

    def missing_list(self):
        return [s.strip() for s in (self.missing_skills or "").split(",") if s.strip()]

    def __repr__(self):
        return f"<Application user={self.user_id} job={self.job_id} score={self.match_score}>"
