# SmartHire AI — Intelligent Resume Screening & Candidate Ranking System

A full-stack Flask application that automates resume screening: candidates upload PDF resumes, the AI engine extracts skills using NLTK + PyPDF2, computes a match score against recruiter job postings, and ranks applicants automatically.

## Tech Stack

- **Frontend:** HTML5, CSS3, Bootstrap 5, JavaScript
- **Backend:** Python, Flask
- **Database:** MySQL + Flask-SQLAlchemy
- **AI / ML:** Pandas, Scikit-learn (TF-IDF + cosine similarity), NLTK, PyPDF2
- **Auth:** Flask-Login (separate sessions for Candidates/Admin and Recruiters)

## Folder Structure

```
smarthire-ai/
├── app.py                  # App factory, blueprint registration, login manager
├── config.py                # Configuration (DB, uploads)
├── requirements.txt
├── models/                  # SQLAlchemy models (User, Recruiter, Job, Resume, Application)
├── routes/                  # Blueprints: main, auth, candidate, recruiter, admin
├── templates/                # Jinja2 templates (Bootstrap 5 UI)
├── static/css, static/js     # Custom styling and JS
├── uploads/                  # Uploaded resumes + generated PDF reports
├── utils/
│   ├── resume_parser.py      # PDF text extraction, cleaning, skill extraction
│   ├── skill_matcher.py      # Match scoring formula + TF-IDF semantic similarity
│   └── report_generator.py   # PDF resume report generation (reportlab)
└── database/schema.sql       # Manual MySQL schema (optional — app auto-creates tables)
```

## Setup Instructions (VS Code, Python 3.12)

1. **Clone/extract the project**, then open the `smarthire-ai/` folder in VS Code.

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   source venv/bin/activate     # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL:**
   - Make sure MySQL Server is running locally.
   - Either let the app auto-create the database/tables on first run, or manually run `database/schema.sql` in MySQL Workbench / CLI.
   - Update credentials in `config.py` (or set environment variables `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_NAME`).

5. **Run the app:**
   ```bash
   python app.py
   ```
   The app starts at `http://127.0.0.1:5000`.

6. **First-run notes:**
   - NLTK will auto-download `punkt` and `stopwords` data on first launch (requires internet once).
   - A default admin account is created automatically:
     - Email: `admin@smarthire.ai`
     - Password: `Admin@123`

## Key Workflows

- **Candidates:** Register → Login → Upload Resume (PDF) → View AI Analysis (skills + strength score) → Browse Jobs → Apply (auto-scored) → Track Application Status.
- **Recruiters:** Register company → Login → Post Jobs → View Applicants (ranked leaderboard) → Shortlist/Reject → Search Candidates by Skill.
- **Admin:** Login → Dashboard Analytics (popular skills, monthly applications) → Manage Candidates/Recruiters/Jobs/Applications → AI Statistics.

## AI Scoring Formula

```
Resume Score = (Matching Skills ÷ Total Required Skills) × 100
```

This exact-match score (70% weight) is blended with a TF-IDF + cosine-similarity semantic score (30% weight) computed between the full resume text and job description, producing the **Final Match Score** shown to recruiters and on application records.

## Security Features

- Password hashing via Werkzeug (`generate_password_hash` / `check_password_hash`)
- Session-based authentication via Flask-Login, with separate identity prefixes for candidates/admins vs recruiters
- Role-based route guards (`candidate_only`, `recruiter_only`, `admin_only`)
- File upload validation (PDF-only, 5MB max)
- SQLAlchemy ORM (parameterized queries — no raw SQL injection risk)

## Notes for Extension

- Add more skills to `SKILL_DATABASE` in `utils/resume_parser.py` to widen detection coverage.
- The `Resume Strength Meter` heuristic in `resume_parser.py` can be tuned to weight different resume sections.
- Swap the `SQLALCHEMY_DATABASE_URI` in `config.py` to point at any MySQL-compatible host (e.g. cloud MySQL) without code changes elsewhere.
