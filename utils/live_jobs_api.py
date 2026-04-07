"""
live_jobs_api.py
----------------
Fetches REAL live job postings for a target role using the Adzuna API.
Adzuna is free to sign up: https://developer.adzuna.com/

Add these to your .env file:
    ADZUNA_APP_ID=your_app_id
    ADZUNA_APP_KEY=your_app_key

Falls back gracefully to mock data if keys are missing or API is unreachable.

Place this file at:  utils/live_jobs_api.py
"""

import os
import time
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID  = os.getenv("ADZUNA_APP_ID", "")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY", "")

# Adzuna country endpoint — change to "in" for India, "gb" for UK, "us" for USA
ADZUNA_COUNTRY = os.getenv("ADZUNA_COUNTRY", "in")
ADZUNA_BASE    = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1"

# Simple in-memory cache: key → (timestamp, data)
_cache: dict[str, tuple[float, list]] = {}
CACHE_TTL_SECONDS = 600  # 10 minutes


# ── Internal helpers ──────────────────────────────────────────────────────────

def _cache_get(key: str) -> list | None:
    if key in _cache:
        ts, data = _cache[key]
        if time.time() - ts < CACHE_TTL_SECONDS:
            return data
    return None


def _cache_set(key: str, data: list):
    _cache[key] = (time.time(), data)


def _parse_job(raw: dict) -> dict:
    """Normalise a raw Adzuna job dict into a clean flat structure."""
    return {
        "title":       raw.get("title", "Unknown Role"),
        "company":     raw.get("company", {}).get("display_name", "Unknown Company"),
        "location":    raw.get("location", {}).get("display_name", "Remote / Unknown"),
        "salary_min":  raw.get("salary_min"),
        "salary_max":  raw.get("salary_max"),
        "description": (raw.get("description") or "")[:400],
        "url":         raw.get("redirect_url", ""),
        "posted_date": raw.get("created", ""),
        "category":    raw.get("category", {}).get("label", ""),
        "source":      "adzuna",
    }


def _mock_jobs(role: str, count: int = 5) -> list[dict]:
    """
    Fallback mock data — used when API keys are absent or request fails.
    Returns plausible-looking job cards so the UI never breaks.
    """
    companies = [
        "Infosys", "TCS", "Wipro", "Zoho", "Freshworks",
        "Swiggy", "Razorpay", "PhonePe", "CRED", "Meesho",
    ]
    base_salaries = {
        "data analyst": (400000, 800000),
        "data scientist": (700000, 1400000),
        "backend developer": (600000, 1200000),
        "frontend developer": (500000, 1000000),
        "ml engineer": (800000, 1600000),
        "fullstack developer": (700000, 1300000),
        "devops engineer": (700000, 1400000),
        "product manager": (900000, 1800000),
    }
    role_lower = role.lower()
    sal = next(
        (v for k, v in base_salaries.items() if k in role_lower),
        (500000, 1000000),
    )

    jobs = []
    for i in range(min(count, len(companies))):
        jobs.append({
            "title":       f"{role} — {['Junior', 'Mid-Level', 'Senior', 'Lead', 'Principal'][i % 5]}",
            "company":     companies[i],
            "location":    ["Bengaluru", "Chennai", "Hyderabad", "Pune", "Mumbai"][i % 5],
            "salary_min":  sal[0] + i * 50000,
            "salary_max":  sal[1] + i * 50000,
            "description": (
                f"We are looking for a {role} to join our growing team. "
                f"You will work on cutting-edge projects, collaborating with cross-functional teams. "
                f"Strong communication and problem-solving skills required."
            ),
            "url":         "",
            "posted_date": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"),
            "category":    "IT Jobs",
            "source":      "mock",
        })
    return jobs


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_live_jobs(
    role: str,
    location: str = "India",
    results_per_page: int = 5,
) -> dict:
    """
    Fetch live job postings for a role.

    Returns
    -------
    {
        "jobs": [...],          # list of normalised job dicts
        "total_count": int,     # total results available on API
        "source": "adzuna" | "mock",
        "cached": bool,
        "location": str,
        "role": str,
    }
    """
    cache_key = f"{role.lower()}::{location.lower()}::{results_per_page}"
    cached = _cache_get(cache_key)
    if cached:
        return {
            "jobs": cached,
            "total_count": len(cached),
            "source": cached[0].get("source", "cache") if cached else "cache",
            "cached": True,
            "location": location,
            "role": role,
        }

    # No API keys — skip straight to mock
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("[LiveJobsAPI] No Adzuna credentials — using mock data.")
        jobs = _mock_jobs(role, results_per_page)
        _cache_set(cache_key, jobs)
        return {
            "jobs": jobs,
            "total_count": len(jobs),
            "source": "mock",
            "cached": False,
            "location": location,
            "role": role,
        }

    # ── Adzuna API call ───────────────────────────────────────────────────────
    params = {
        "app_id":           ADZUNA_APP_ID,
        "app_key":          ADZUNA_APP_KEY,
        "results_per_page": results_per_page,
        "what":             role,
        "where":            location,
        "sort_by":          "date",
        "content-type":     "application/json",
    }

    try:
        response = requests.get(ADZUNA_BASE, params=params, timeout=8)
        response.raise_for_status()
        data     = response.json()
        raw_jobs = data.get("results", [])
        total    = data.get("count", len(raw_jobs))
        jobs     = [_parse_job(j) for j in raw_jobs]

        if not jobs:
            jobs = _mock_jobs(role, results_per_page)

        _cache_set(cache_key, jobs)
        return {
            "jobs":        jobs,
            "total_count": total,
            "source":      "adzuna",
            "cached":      False,
            "location":    location,
            "role":        role,
        }

    except requests.exceptions.Timeout:
        print("[LiveJobsAPI] Adzuna request timed out — falling back to mock.")
    except requests.exceptions.HTTPError as e:
        print(f"[LiveJobsAPI] HTTP error: {e} — falling back to mock.")
    except Exception as e:
        print(f"[LiveJobsAPI] Unexpected error: {e} — falling back to mock.")

    jobs = _mock_jobs(role, results_per_page)
    _cache_set(cache_key, jobs)
    return {
        "jobs":        jobs,
        "total_count": len(jobs),
        "source":      "mock",
        "cached":      False,
        "location":    location,
        "role":        role,
    }


def extract_trending_skills_from_jobs(jobs: list[dict]) -> list[str]:
    """
    Extract the most-mentioned tech skills from a list of live job descriptions.
    Used to augment RAG skill requirements with real-time market signals.
    """
    import re

    TECH_KEYWORDS = {
        "python", "java", "javascript", "typescript", "react", "node", "sql",
        "nosql", "mongodb", "postgres", "mysql", "docker", "kubernetes", "aws",
        "gcp", "azure", "git", "linux", "html", "css", "flask", "django",
        "fastapi", "tensorflow", "pytorch", "pandas", "numpy", "scikit",
        "tableau", "powerbi", "spark", "kafka", "airflow", "redis", "graphql",
        "rest", "api", "agile", "scrum", "figma", "swift", "kotlin", "flutter",
        "golang", "rust", "scala", "excel", "llm", "langchain", "rag",
        "machine learning", "deep learning", "nlp", "mlops", "ci/cd",
    }

    counts: dict[str, int] = {}
    for job in jobs:
        text = (job.get("description") or "").lower()
        for keyword in TECH_KEYWORDS:
            if keyword in text:
                counts[keyword] = counts.get(keyword, 0) + 1

    sorted_skills = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return [skill for skill, _ in sorted_skills[:15]]


def get_salary_insights(jobs: list[dict]) -> dict:
    """
    Compute salary statistics from a list of live job dicts.
    Returns avg, min, max in INR (or whatever currency Adzuna returns).
    """
    salaries = [
        j["salary_min"] for j in jobs if j.get("salary_min")
    ] + [
        j["salary_max"] for j in jobs if j.get("salary_max")
    ]

    if not salaries:
        return {"available": False}

    return {
        "available":  True,
        "min":        min(salaries),
        "max":        max(salaries),
        "avg":        round(sum(salaries) / len(salaries)),
        "currency":   "INR" if ADZUNA_COUNTRY == "in" else "USD",
        "count":      len(jobs),
    }
