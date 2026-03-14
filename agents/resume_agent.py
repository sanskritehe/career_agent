"""
resume_agent.py  (RAG-powered version)
---------------------------------------
RAG loop:
  1. Retrieve top-k real job descriptions from ChromaDB for the target role
  2. Inject retrieved JDs as grounded context into the LLM prompt
  3. LLM analyzes resume WITH retrieved context — not just its own knowledge

This is proper RAG: Query → Retrieve → Augment → Generate
"""

import json
from utils.llm import call_llm
from utils.job_skills_dataset import get_role_requirements
from utils.rag_pipeline import build_rag_context, retrieve_relevant_jds


def analyze_resume(resume_text: str, target_role: str) -> str:

    # ── 1. RETRIEVAL ─────────────────────────────────────────────────────────
    simple_skill_hints = _extract_keyword_hints(resume_text)

    # ✅ most_relevant_jd — query with ROLE ONLY so it's not polluted by resume keywords
    role_only_jds = retrieve_relevant_jds(query=target_role, top_k=1)
    most_relevant_jd = role_only_jds[0]["job_title"] if role_only_jds else "N/A"

    # RAG context for the prompt — uses role + skills for richer retrieval
    rag_context = build_rag_context(
        target_role=target_role,
        candidate_skills=simple_skill_hints,
        top_k=3,
    )

    # ── 2. STRUCTURED DATA ────────────────────────────────────────────────────
    role_data       = get_role_requirements(target_role, top_k=3)
    matched_roles   = role_data["matched_roles"]
    required_skills = role_data["required_skills"]
    data_source     = role_data["source"]

    # ── 3. AUGMENTATION ───────────────────────────────────────────────────────
    prompt = f"""
You are a Resume Analysis Agent with access to a real job descriptions knowledge base.

Resume Text:
{resume_text}

Target Job Role: {target_role}

--- DATASET SKILL REQUIREMENTS ---
Closest matching role(s): {', '.join(matched_roles)}
Expected skills for this role: {', '.join(required_skills) if required_skills else 'See RAG context below'}
Data source: {data_source}
--- END DATASET REQUIREMENTS ---

{rag_context}

INSTRUCTIONS:
You have been provided with:
  (a) The candidate's resume
  (b) A structured list of required skills from a job-skills dataset
  (c) Real job descriptions retrieved from a vector database (RAG context above)

Use ALL THREE sources to perform a thorough analysis:

1. Extract ALL technical and soft skills present in the resume.
2. Cross-reference skills against BOTH the dataset requirements AND the
   retrieved job descriptions to identify missing skills.
3. Estimate experience level: Beginner / Intermediate / Advanced.
4. List strengths and weaknesses relative to the target role.
5. Write a short professional summary.

Base "skills_missing" on the dataset requirements AND patterns seen in the
retrieved JDs — this ensures the gap analysis reflects real hiring expectations.

Return STRICTLY in JSON format:

{{
  "skills_present": [],
  "skills_missing": [],
  "experience_level": "",
  "strengths": [],
  "weaknesses": [],
  "summary": "",
  "dataset_source": "{data_source}",
  "matched_dataset_roles": {json.dumps(matched_roles)},
  "rag_used": true
}}
"""

    raw = call_llm(prompt)

    # ── 4. INJECT most_relevant_jd after LLM response — guaranteed correct ───
    try:
        parsed = json.loads(raw)
        parsed["most_relevant_jd"] = most_relevant_jd
        return json.dumps(parsed)
    except json.JSONDecodeError:
        return raw


# ── Helper ────────────────────────────────────────────────────────────────────

def _extract_keyword_hints(text: str, max_hints: int = 15) -> list[str]:
    import re

    TECH_KEYWORDS = {
        "python", "java", "javascript", "typescript", "react", "node", "sql",
        "nosql", "mongodb", "postgres", "mysql", "docker", "kubernetes", "aws",
        "gcp", "azure", "git", "linux", "html", "css", "flask", "django",
        "fastapi", "tensorflow", "pytorch", "pandas", "numpy", "scikit",
        "tableau", "powerbi", "spark", "kafka", "airflow", "redis", "graphql",
        "rest", "api", "agile", "scrum", "figma", "swift", "kotlin", "flutter",
        "c++", "c#", "golang", "rust", "scala", "r", "matlab", "excel",
    }

    words = re.findall(r'\b\w+\b', text.lower())
    found = [w for w in words if w in TECH_KEYWORDS]

    seen, unique = set(), []
    for w in found:
        if w not in seen:
            seen.add(w)
            unique.append(w)

    return unique[:max_hints]
