from datetime import datetime
from . import db


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)
    recruiter_id = db.Column(db.Integer, db.ForeignKey("recruiters.id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    required_skills = db.Column(db.Text, nullable=False)  # comma-separated skills
    experience = db.Column(db.String(50))
    salary = db.Column(db.String(50))
    location = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    applications = db.relationship("Application", backref="job", lazy=True, cascade="all, delete-orphan")

    def skills_list(self):
        return [s.strip().lower() for s in self.required_skills.split(",") if s.strip()]

    def __repr__(self):
        return f"<Job {self.title}>"
