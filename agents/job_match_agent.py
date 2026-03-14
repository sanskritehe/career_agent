"""
job_match_agent.py  (RAG + Semantic Similarity version)
--------------------------------------------------------
Scoring pipeline:
  ① Role validity check       — sentence-transformers (local)
  ② Retrieve JDs from ChromaDB — RAG retrieval (local)
  ③ Semantic similarity score  — sentence-transformers (local)
  ④ Skill overlap bonus        — pure Python set math
  ⑤ Reasoning blurb            — Groq LLM (uses retrieved JDs as context)
"""

import json
import numpy as np
from sentence_transformers import SentenceTransformer, util

from utils.job_skills_dataset import get_role_requirements
from utils.rag_pipeline import build_rag_context, retrieve_relevant_jds
from utils.llm import call_llm

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _cosine_score(vec_a, vec_b) -> float:
    sim = util.cos_sim(vec_a, vec_b).item()
    return round(max(0.0, sim) * 100, 1)


# ── Role validity anchors ─────────────────────────────────────────────────────
KNOWN_JOB_ANCHORS = [
    "software engineer", "frontend developer", "backend developer",
    "fullstack developer", "data analyst", "data scientist", "data engineer",
    "machine learning engineer", "ai engineer", "devops engineer",
    "cloud engineer", "product manager", "ux designer", "ui designer",
    "android developer", "ios developer", "qa engineer", "cybersecurity analyst",
    "business analyst", "site reliability engineer", "solutions architect",
    "database administrator", "embedded systems engineer", "blockchain developer",
    "game developer", "network engineer", "it support", "scrum master",
    "technical lead", "engineering manager",
]

_anchor_vecs = None

def _get_anchor_vecs():
    global _anchor_vecs
    if _anchor_vecs is None:
        _anchor_vecs = _get_model().encode(KNOWN_JOB_ANCHORS, convert_to_tensor=True)
    return _anchor_vecs


def _is_valid_job_role(target_role: str) -> tuple[bool, float]:
    role_vec = _get_model().encode(target_role, convert_to_tensor=True)
    scores   = util.cos_sim(role_vec, _get_anchor_vecs())[0]
    best     = float(scores.max().item())
    return best >= 0.35, round(best, 3)


def _invalid_role_response(target_role: str, validity_score: float) -> str:
    return json.dumps({
        "suitable_roles": [{
            "role":                  target_role,
            "readiness_score":       0,
            "reasoning":             (
                f'"{target_role}" does not appear to be a recognised professional '
                f"job role. Please enter a valid title such as "
                f'"Data Analyst", "Backend Developer", or "Product Manager".'
            ),
            "semantic_score":        0,
            "overlap_bonus":         0,
            "matched_skills":        [],
            "missing_skills":        [],
            "dataset_source":        "n/a",
            "matched_dataset_roles": [],
            "valid_role":            False,
            "validity_score":        validity_score,
            "rag_used":              False,
        }]
    })


def match_jobs(resume_analysis_json: dict, target_role: str) -> str:
    """
    Match resume against a target role.
    Scoring is local (no LLM). LLM only writes the reasoning, with RAG context.
    """

    # ── 0. Validate role ──────────────────────────────────────────────────────
    is_valid, validity_score = _is_valid_job_role(target_role)
    if not is_valid:
        return _invalid_role_response(target_role, validity_score)

    model = _get_model()

    # ── 1. Candidate profile ──────────────────────────────────────────────────
    skills_present:   list = resume_analysis_json.get("skills_present", [])
    experience_level: str  = resume_analysis_json.get("experience_level", "")
    summary:          str  = resume_analysis_json.get("summary", "")

    candidate_text = (
        f"Skills: {', '.join(skills_present)}. "
        f"Experience: {experience_level}. "
        f"Profile: {summary}"
    )

    # ── 2. Dataset skill requirements ─────────────────────────────────────────
    role_data        = get_role_requirements(target_role, top_k=3)
    required_skills: list = role_data["required_skills"]
    matched_roles:   list = role_data["matched_roles"]
    data_source:     str  = role_data["source"]

    # ── 3. RAG — retrieve real JDs for this role ──────────────────────────────
    rag_context = build_rag_context(
        target_role=target_role,
        candidate_skills=skills_present,
        top_k=3,
    )

    # Also get raw JDs for skill augmentation
    raw_jds = retrieve_relevant_jds(
        query=f"{target_role} {' '.join(skills_present)}",
        top_k=3,
    )

    # Augment required skills with skills found in retrieved JDs
    jd_skills: set[str] = set()
    for jd in raw_jds:
        for s in jd.get("skills", "").split(","):
            s = s.strip()
            if s:
                jd_skills.add(s)

    # Merge dataset skills + JD skills (JD skills expand the required set)
    all_required_skills = list(set(required_skills) | jd_skills)

    role_text = (
        f"Role: {target_role}. "
        f"Required skills: {', '.join(all_required_skills)}."
    )

    # ── 4. Semantic similarity (local) ────────────────────────────────────────
    candidate_vec = model.encode(candidate_text, convert_to_tensor=True)
    role_vec      = model.encode(role_text,      convert_to_tensor=True)
    raw_score     = _cosine_score(candidate_vec, role_vec)

    # ── 5. Skill overlap bonus (local, up to +15) ─────────────────────────────
    present_lower  = {s.lower() for s in skills_present}
    required_lower = {s.lower() for s in all_required_skills}

    if required_lower:
        overlap_ratio = len(present_lower & required_lower) / len(required_lower)
        overlap_bonus = round(overlap_ratio * 15, 1)
    else:
        overlap_bonus = 0.0

    final_score = min(100, round(raw_score + overlap_bonus, 1))

    # ── 6. Matched / missing ──────────────────────────────────────────────────
    matched_skills = sorted(present_lower & required_lower)
    missing_skills = sorted(required_lower - present_lower)

    # ── 7. LLM reasoning — augmented with retrieved JDs ──────────────────────
    reasoning_prompt = f"""
You are a concise recruitment assistant with access to real job descriptions.

Candidate Profile:
- Skills Present: {', '.join(skills_present)}
- Experience Level: {experience_level}

Target Role: {target_role}
Required Skills (dataset + retrieved JDs): {', '.join(all_required_skills)}

Matched Skills: {', '.join(matched_skills) or 'None'}
Missing Skills: {', '.join(missing_skills[:8]) or 'None'}

Semantic Match Score: {final_score}%

{rag_context}

Using the candidate profile AND the retrieved job descriptions above as context,
write a SHORT (3-4 sentence) reasoning paragraph explaining this score.
Mention specific matched and missing skills. Reference what real JDs expect.
Be direct and factual.

Return ONLY this JSON:
{{
  "reasoning": "your 3-4 sentence explanation here"
}}
"""
    raw_llm = call_llm(reasoning_prompt)

    try:
        llm_json  = json.loads(raw_llm)
        reasoning = llm_json.get("reasoning", raw_llm)
    except Exception:
        reasoning = raw_llm

    # ── 8. Final response ─────────────────────────────────────────────────────
    return json.dumps({
        "suitable_roles": [{
            "role":                  target_role,
            "readiness_score":       final_score,
            "reasoning":             reasoning,
            "semantic_score":        raw_score,
            "overlap_bonus":         overlap_bonus,
            "matched_skills":        matched_skills,
            "missing_skills":        missing_skills[:10],
            "dataset_source":        data_source,
            "matched_dataset_roles": matched_roles,
            "valid_role":            True,
            "validity_score":        validity_score,
            "rag_used":              True,
            "retrieved_jd_count":    len(raw_jds),
        }]
    })
