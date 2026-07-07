"""
skill_matcher.py
-----------------
Compares a candidate's extracted resume skills against a job's
required skills and computes the AI Resume Match Score.

Formula:
    Resume Score = (Matching Skills / Total Required Skills) * 100

Also provides a TF-IDF + cosine-similarity based "semantic" score
using scikit-learn, blended with the exact-skill-match score for a
more robust final ranking signal.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def normalize_skills(skill_list):
    return set(s.strip().lower() for s in skill_list if s.strip())


def match_skills(resume_skills, required_skills):
    """
    Returns a dict with matching_skills, missing_skills and exact match percentage.
    """
    resume_set = normalize_skills(resume_skills)
    required_set = normalize_skills(required_skills)

    if not required_set:
        return {
            "matching_skills": [],
            "missing_skills": [],
            "match_percent": 0.0,
        }

    matching = sorted(resume_set & required_set)
    missing = sorted(required_set - resume_set)

    match_percent = (len(matching) / len(required_set)) * 100
    return {
        "matching_skills": matching,
        "missing_skills": missing,
        "match_percent": round(match_percent, 2),
    }


def semantic_similarity(resume_text, job_description):
    """
    Uses TF-IDF vectorization + cosine similarity to gauge overall
    textual relevance between resume and job description, returned as 0-100.
    """
    if not resume_text.strip() or not job_description.strip():
        return 0.0

    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf_matrix = vectorizer.fit_transform([resume_text, job_description])
        sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
    except ValueError:
        return 0.0
    return round(sim * 100, 2)


def calculate_final_score(resume_skills, required_skills, resume_text="", job_description=""):
    """
    Blends the exact skill-match formula (primary, 70% weight) with the
    semantic TF-IDF similarity (secondary, 30% weight) to produce a
    final, more nuanced Resume Match Score.
    """
    skill_result = match_skills(resume_skills, required_skills)
    exact_score = skill_result["match_percent"]

    semantic_score = semantic_similarity(resume_text, job_description) if resume_text and job_description else 0.0

    final_score = round((exact_score * 0.7) + (semantic_score * 0.3), 2)

    return {
        "final_score": final_score,
        "exact_score": exact_score,
        "semantic_score": semantic_score,
        "matching_skills": skill_result["matching_skills"],
        "missing_skills": skill_result["missing_skills"],
    }


def rank_candidates(applications):
    """
    Given a list of Application objects (with match_score set),
    returns them sorted descending by score with rank assigned.
    """
    sorted_apps = sorted(applications, key=lambda a: a.match_score or 0, reverse=True)
    ranked = []
    for idx, app in enumerate(sorted_apps, start=1):
        ranked.append({"rank": idx, "application": app})
    return ranked
