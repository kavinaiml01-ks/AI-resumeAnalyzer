"""
resume_parser.py
-----------------
Handles reading PDF resumes, cleaning the extracted text using NLTK,
and pulling out probable skills using a curated skill dictionary +
NLTK tokenization/stopword filtering.
"""

import re
import PyPDF2
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Ensure required NLTK data is available. download() is safe to call
# repeatedly — it skips anything already present.
for pkg in ["punkt", "punkt_tab", "stopwords"]:
    try:
        nltk.download(pkg, quiet=True)
    except Exception:
        pass

STOP_WORDS = set(stopwords.words("english"))

# A curated master list of common tech/business skills the system can detect.
# Extend this list freely — it powers both resume parsing and job matching.
SKILL_DATABASE = [
    "python", "java", "javascript", "typescript", "c++", "c", "c#", "php", "ruby", "go", "kotlin", "swift",
    "html", "css", "html5", "css3", "bootstrap", "tailwind", "react", "angular", "vue", "node.js", "nodejs",
    "express", "flask", "django", "fastapi", "spring", "spring boot", ".net", "laravel",
    "mysql", "postgresql", "mongodb", "sqlite", "oracle", "redis", "firebase", "sql",
    "machine learning", "deep learning", "data science", "data analysis", "nlp",
    "pandas", "numpy", "scikit-learn", "tensorflow", "keras", "pytorch", "opencv",
    "power bi", "tableau", "excel", "data visualization", "statistics",
    "aws", "azure", "gcp", "docker", "kubernetes", "jenkins", "ci/cd", "linux", "git", "github",
    "rest api", "graphql", "microservices", "agile", "scrum",
    "communication", "leadership", "teamwork", "problem solving", "project management",
    "android", "ios", "flutter", "react native",
    "cybersecurity", "networking", "blockchain", "devops",
]


def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


def extract_text_from_pdf(filepath):
    """Reads a PDF file and returns its raw concatenated text."""
    text = ""
    with open(filepath, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
    return text


def clean_text(raw_text):
    """Lowercases, removes special characters, tokenizes and strips stopwords."""
    text = raw_text.lower()
    text = re.sub(r"[^a-z0-9\s.#+]", " ", text)
    tokens = word_tokenize(text)
    cleaned_tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1]
    return " ".join(cleaned_tokens)


def extract_skills(raw_text):
    """
    Scans the resume text for any known skill phrases from SKILL_DATABASE.
    Handles multi-word skills (e.g. 'machine learning') via substring search
    on the lowercased raw text (more reliable than tokens for phrases).
    """
    text_lower = raw_text.lower()
    found = set()
    for skill in SKILL_DATABASE:
        # word-boundary-safe search, tolerant of punctuation like C++ / C#
        pattern = re.escape(skill)
        if re.search(rf"(?<![a-z0-9]){pattern}(?![a-z0-9])", text_lower):
            found.add(skill)
    return sorted(found)


def calculate_resume_strength(raw_text, extracted_skills):
    """
    A simple heuristic 'Resume Strength Meter' score out of 100, based on:
      - number of skills detected
      - presence of key resume sections
      - resume length (very short resumes score lower)
    """
    score = 0
    score += min(len(extracted_skills) * 5, 50)  # up to 50 pts for skills

    sections = ["experience", "education", "project", "skill", "certification", "achievement"]
    text_lower = raw_text.lower()
    section_hits = sum(1 for s in sections if s in text_lower)
    score += section_hits * 7  # up to 42 pts

    word_count = len(raw_text.split())
    if word_count > 150:
        score += 8

    return min(round(score, 2), 100)


def parse_resume(filepath):
    """
    Full pipeline: PDF -> raw text -> cleaned text -> skills -> strength score.
    Returns a dict ready to be stored in the Resume model.
    """
    raw_text = extract_text_from_pdf(filepath)
    cleaned = clean_text(raw_text)
    skills = extract_skills(raw_text)
    strength = calculate_resume_strength(raw_text, skills)

    return {
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "skills": skills,
        "strength_score": strength,
    }
