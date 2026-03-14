"""
job_skills_dataset.py
---------------------
Dataset fields: 'Job Title', 'Skills', 'Job Description'  (capital + spaces)
"""

import json
import re
from difflib import SequenceMatcher

_dataset_cache = None

def _load_dataset():
    global _dataset_cache
    if _dataset_cache is not None:
        return _dataset_cache
    try:
        from datasets import load_dataset
        ds = load_dataset("NxtGenIntern/job_titles_and_descriptions", split="train")
        _dataset_cache = ds
        print(f"[JobSkillsDataset] Loaded {len(ds)} job roles from HuggingFace.")
        return ds
    except Exception as e:
        print(f"[JobSkillsDataset] Could not load dataset: {e}")
        return None


def _parse_skills(raw_skills) -> list[str]:
    if isinstance(raw_skills, list):
        return [s.strip() for s in raw_skills if s.strip()]
    if isinstance(raw_skills, str):
        # Skills in this dataset are already comma-separated plain strings
        # e.g. "Web Accessibility Guidelines, HTML, CSS, JavaScript"
        return [s.strip() for s in raw_skills.split(",") if s.strip()]
    return []


def _score_row(target_lower: str, title_lower: str) -> float:
    target_words = set(target_lower.split())
    title_words  = set(title_lower.split())
    overlap      = len(target_words & title_words) / len(title_words) if title_words else 0.0
    seq_score    = SequenceMatcher(None, target_lower, title_lower).ratio()
    return (overlap * 0.7) + (seq_score * 0.3)


def get_role_requirements(target_role: str, top_k: int = 3) -> dict:
    ds = _load_dataset()

    if ds is None:
        return _fallback_requirements(target_role)

    target_lower = target_role.lower().strip()
    scored = []

    for row in ds:
        # ✅ Correct field names
        title = (row.get("Job Title", "") or "").strip()
        if not title:
            continue
        score = _score_row(target_lower, title.lower())
        scored.append((score, row))

    scored.sort(key=lambda x: x[0], reverse=True)
    best       = scored[:top_k]
    best_score = best[0][0] if best else 0

    if best:
        print(f"[JobSkillsDataset] Best match for '{target_role}': "
              f"'{best[0][1].get('Job Title', '')}' (score: {best_score:.2f})")

    if best_score < 0.2:
        return _fallback_requirements(target_role)

    matched_titles:      list     = []
    all_skills:          set[str] = set()
    description_snippet: str      = ""

    for score, row in best:
        title      = row.get("Job Title", "")
        skills_raw = row.get("Skills", "")        # ✅ correct
        desc       = row.get("Job Description", "") or ""  # ✅ correct

        matched_titles.append(title)
        all_skills.update(_parse_skills(skills_raw))

        if not description_snippet and desc:
            description_snippet = desc[:400]

    return {
        "matched_roles":           matched_titles,
        "required_skills":         sorted(all_skills),
        "job_description_snippet": description_snippet,
        "source":                  "dataset",
    }


def _fallback_requirements(target_role: str) -> dict:
    role_lower = target_role.lower()

    FALLBACK_MAP = {
        "data analyst": [
            "SQL", "Excel", "Python", "Pandas", "Data Visualization",
            "Tableau", "Power BI", "Statistics", "Google Sheets", "Report Writing",
        ],
        "data scientist": [
            "Python", "Machine Learning", "Statistics", "SQL", "Pandas",
            "NumPy", "Scikit-learn", "Data Visualization", "TensorFlow", "Jupyter",
        ],
        "data engineer": [
            "Python", "SQL", "ETL", "Apache Spark", "Airflow",
            "Data Warehousing", "AWS", "Kafka", "dbt",
        ],
        "business analyst": [
            "SQL", "Excel", "Requirements Gathering", "Data Analysis",
            "Stakeholder Management", "Power BI", "Tableau", "Documentation",
        ],
        "ml engineer": [
            "Python", "Machine Learning", "TensorFlow", "PyTorch",
            "MLOps", "Docker", "Model Deployment", "Scikit-learn",
        ],
        "ai engineer": [
            "Python", "LLMs", "LangChain", "Prompt Engineering",
            "RAG", "Vector Databases", "API Integration", "Machine Learning",
        ],
        "frontend": [
            "HTML", "CSS", "JavaScript", "React", "TypeScript",
            "REST APIs", "Git", "Responsive Design",
        ],
        "backend": [
            "Python", "Node.js", "SQL", "REST APIs", "Git",
            "Docker", "Databases", "Authentication",
        ],
        "fullstack": [
            "JavaScript", "React", "Node.js", "SQL", "REST APIs",
            "Git", "HTML", "CSS", "Docker",
        ],
        "devops": [
            "Linux", "Docker", "Kubernetes", "CI/CD", "Terraform",
            "AWS", "Shell Scripting", "Git",
        ],
        "cloud engineer": [
            "AWS", "Azure", "GCP", "Terraform", "Docker",
            "Kubernetes", "Networking", "CI/CD",
        ],
        "android": [
            "Kotlin", "Java", "Android SDK", "REST APIs", "Git", "Room DB",
        ],
        "ios": [
            "Swift", "Xcode", "UIKit", "REST APIs", "Git", "Auto Layout",
        ],
        "product manager": [
            "Roadmapping", "Agile", "Stakeholder Management", "SQL",
            "A/B Testing", "JIRA", "User Research", "Prioritization",
        ],
        "ux designer": [
            "Figma", "Wireframing", "Prototyping", "User Research",
            "Usability Testing", "Design Systems", "Adobe XD",
        ],
        "qa engineer": [
            "Manual Testing", "Selenium", "Test Cases", "Bug Reporting",
            "API Testing", "Postman", "Automation", "Python",
        ],
        "cybersecurity": [
            "Network Security", "Linux", "SIEM", "Penetration Testing",
            "Firewalls", "Python", "Incident Response", "Compliance",
        ],
        "software engineer": [
            "Data Structures", "Algorithms", "Python", "Git",
            "System Design", "REST APIs", "SQL", "OOP",
        ],
    }

    best_key   = None
    best_score = 0.0

    for key in FALLBACK_MAP:
        score = _score_row(role_lower, key)
        if score > best_score:
            best_score = score
            best_key   = key

    if best_key is None or best_score < 0.15:
        best_key = "software engineer"

    print(f"[JobSkillsDataset] Fallback: '{target_role}' → '{best_key}' (score: {best_score:.2f})")

    return {
        "matched_roles":           [target_role],
        "required_skills":         FALLBACK_MAP[best_key],
        "job_description_snippet": f"Standard requirements for {target_role}.",
        "source":                  "fallback",
    }


def list_available_roles(limit: int = 50) -> list[str]:
    ds = _load_dataset()
    if ds is None:
        return []
    titles = list({row.get("Job Title", "") for row in ds})
    return sorted(titles)[:limit]
