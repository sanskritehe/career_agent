"""
resume_builder.py
-----------------
Generates an improved, ATS-optimised resume from:
  - The candidate's original resume text
  - Skills gap analysis (from resume_agent)
  - Target role + RAG-retrieved JD patterns

Place at: agents/resume_builder.py
"""

import json
import re
from utils.llm import call_llm
from utils.rag_pipeline import build_rag_context


def build_improved_resume(
    original_resume_text: str,
    resume_analysis: dict,
    target_role: str,
) -> dict:
    """
    Takes original resume text + analysis dict from resume_agent
    and returns a fully rewritten, ATS-optimised resume as structured JSON.

    Returns
    -------
    {
        "name":            str,
        "contact":         str,
        "summary":         str,   ← rewritten professional summary
        "skills":          list,  ← merged present + recommended skills
        "experience":      list,  ← rewritten bullet points (STAR format)
        "projects":        list,  ← highlighted / new project suggestions
        "education":       str,
        "certifications":  list,  ← recommended certs for missing skills
        "ats_keywords":    list,  ← keywords pulled from real JDs
        "improvement_notes": list ← what changed and why
    }
    """

    skills_present = resume_analysis.get("skills_present", [])
    skills_missing = resume_analysis.get("skills_missing", [])
    strengths      = resume_analysis.get("strengths", [])
    weaknesses     = resume_analysis.get("weaknesses", [])
    exp_level      = resume_analysis.get("experience_level", "")

    # Pull ATS keywords from real JDs
    rag_context = build_rag_context(
        target_role=target_role,
        candidate_skills=skills_present,
        top_k=3,
    )

    prompt = f"""
You are an expert resume writer and ATS optimisation specialist.

ORIGINAL RESUME:
{original_resume_text[:4000]}

TARGET ROLE: {target_role}
EXPERIENCE LEVEL: {exp_level}

SKILLS ALREADY PRESENT: {', '.join(skills_present)}
SKILL GAPS TO ADDRESS: {', '.join(skills_missing[:12])}
STRENGTHS TO HIGHLIGHT: {', '.join(strengths[:5])}
WEAKNESSES TO MITIGATE: {', '.join(weaknesses[:5])}

{rag_context}

YOUR TASK:
Rewrite this resume to be optimised for the target role. Follow these rules:
1. Rewrite the professional summary to be punchy, role-specific, and 3 sentences max.
2. Rewrite experience bullet points using strong action verbs + quantified impact where possible.
3. Add a "Skills" section that includes all present skills AND flags which missing skills
   the candidate should add once they acquire them (mark these with [*] to learn).
4. Suggest 2-3 projects the candidate could add or highlight to cover the skill gaps.
5. Recommend 2-3 certifications that would directly address the missing skills.
6. Extract ATS keywords from the retrieved JDs that must appear in the resume.
7. List improvement notes explaining every significant change you made.

IMPORTANT: Do NOT invent work experience or degrees. Only rewrite/enhance what exists.
Flag genuinely new additions clearly in improvement_notes.

Return ONLY valid JSON:
{{
  "name": "Candidate name from resume or 'Your Name'",
  "contact": "email | phone | linkedin | github — from resume",
  "summary": "Rewritten 3-sentence professional summary targeting {target_role}",
  "skills": {{
    "current": ["skill1", "skill2"],
    "to_learn": ["[*] skill_gap1 — reason why needed for this role"]
  }},
  "experience": [
    {{
      "company": "Company name",
      "role": "Job title",
      "duration": "Dates",
      "bullets": [
        "Strong action-verb led bullet with quantified impact",
        "Second rewritten bullet"
      ]
    }}
  ],
  "projects": [
    {{
      "name": "Project name (existing or suggested)",
      "description": "1-2 sentence description showing impact",
      "tech_stack": ["tech1", "tech2"],
      "is_suggested": false
    }}
  ],
  "education": "Degree, Institution, Year",
  "certifications": [
    {{
      "name": "Certification name",
      "provider": "Provider (Coursera / Google / AWS etc.)",
      "addresses_skill": "Which skill gap this covers",
      "url": "https://..."
    }}
  ],
  "ats_keywords": ["keyword1", "keyword2"],
  "improvement_notes": [
    "What was changed and why — be specific"
  ]
}}
"""

    raw = call_llm(prompt)
    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        return json.loads(clean)
    except Exception:
        return {"error": "Could not parse resume builder output.", "raw": raw}


def render_resume_as_text(built_resume: dict) -> str:
    """
    Converts the structured JSON resume into clean plain text
    suitable for copy-paste into a Word doc or PDF.
    """
    lines = []

    lines.append(built_resume.get("name", "Your Name").upper())
    lines.append(built_resume.get("contact", ""))
    lines.append("")

    lines.append("PROFESSIONAL SUMMARY")
    lines.append("-" * 40)
    lines.append(built_resume.get("summary", ""))
    lines.append("")

    skills = built_resume.get("skills", {})
    lines.append("SKILLS")
    lines.append("-" * 40)
    current = skills.get("current", [])
    to_learn = skills.get("to_learn", [])
    if current:
        lines.append("Current: " + " · ".join(current))
    if to_learn:
        lines.append("To Acquire: " + " · ".join(to_learn))
    lines.append("")

    experience = built_resume.get("experience", [])
    if experience:
        lines.append("EXPERIENCE")
        lines.append("-" * 40)
        for exp in experience:
            lines.append(f"{exp.get('role', '')} — {exp.get('company', '')}  ({exp.get('duration', '')})")
            for bullet in exp.get("bullets", []):
                lines.append(f"  • {bullet}")
            lines.append("")

    projects = built_resume.get("projects", [])
    if projects:
        lines.append("PROJECTS")
        lines.append("-" * 40)
        for proj in projects:
            tag = "  [Suggested]" if proj.get("is_suggested") else ""
            lines.append(f"{proj.get('name', '')}{tag}")
            lines.append(f"  {proj.get('description', '')}")
            stack = proj.get("tech_stack", [])
            if stack:
                lines.append(f"  Tech: {', '.join(stack)}")
            lines.append("")

    lines.append("EDUCATION")
    lines.append("-" * 40)
    lines.append(built_resume.get("education", ""))
    lines.append("")

    certs = built_resume.get("certifications", [])
    if certs:
        lines.append("RECOMMENDED CERTIFICATIONS")
        lines.append("-" * 40)
        for cert in certs:
            lines.append(f"  • {cert.get('name', '')} — {cert.get('provider', '')}")
            lines.append(f"    Covers: {cert.get('addresses_skill', '')}")
        lines.append("")

    return "\n".join(lines)
