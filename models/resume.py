from datetime import datetime
from . import db


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    raw_text = db.Column(db.Text)
    extracted_skills = db.Column(db.Text)   # comma-separated
    match_score = db.Column(db.Float, default=0.0)  # generic resume strength score
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def skills_list(self):
        if not self.extracted_skills:
            return []
        return [s.strip() for s in self.extracted_skills.split(",") if s.strip()]

    def __repr__(self):
        return f"<Resume {self.filename}>"
