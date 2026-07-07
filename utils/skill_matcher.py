"""
skill_matcher.py
-----------------
Compares a candidate's extracted resume skills against a job's
required skills and computes the AI Resume Match Score.

Formula:
    Resume Score = (Matching Skills / Total Required Skills) * 100

Also provides a lightweight semantic score based on shared words and
keyword overlap, blended with the exact-skill-match score for a
simple but effective ranking signal.
"""

import re


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
    Computes a lightweight semantic score using shared keyword overlap.
    Returns a value between 0 and 100.
    """
    if not resume_text or not job_description:
        return 0.0

    def tokenize(text):
        words = re.findall(r"[a-zA-Z0-9#+.]+", text.lower())
        return [w for w in words if len(w) > 2]

    resume_words = set(tokenize(resume_text))
    job_words = set(tokenize(job_description))

    if not resume_words or not job_words:
        return 0.0

    overlap = resume_words & job_words
    if not overlap:
        return 0.0

    score = (len(overlap) / max(len(resume_words), len(job_words))) * 100
    return round(score, 2)


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
