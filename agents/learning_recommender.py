"""
learning_recommender.py
-----------------------
For each skill gap identified by the resume agent, recommends:
  - Curated free resources (YouTube channels, docs, courses)
  - Estimated time to learn
  - A prioritised learning order based on the target role

Place at: agents/learning_recommender.py
"""

import json
import re
from utils.llm import call_llm


# ── Curated static resource map (no API needed, always works) ─────────────────
# Kept intentionally broad — LLM adds role-specific picks on top of these.

RESOURCE_MAP: dict[str, dict] = {
    "python": {
        "free": ["https://docs.python.org/3/tutorial/", "https://www.youtube.com/c/CoreySchafer"],
        "course": "Python for Everybody — Coursera (free audit)",
        "time_weeks": 3,
    },
    "sql": {
        "free": ["https://sqlzoo.net", "https://mode.com/sql-tutorial/"],
        "course": "SQL for Data Science — Coursera (free audit)",
        "time_weeks": 2,
    },
    "machine learning": {
        "free": ["https://www.youtube.com/c/3blue1brown", "https://fast.ai"],
        "course": "Machine Learning Specialization — Andrew Ng, Coursera",
        "time_weeks": 8,
    },
    "docker": {
        "free": ["https://docs.docker.com/get-started/", "https://www.youtube.com/watch?v=fqMOX6JJhGo"],
        "course": "Docker and Kubernetes — Udemy (TechWorld with Nana)",
        "time_weeks": 2,
    },
    "kubernetes": {
        "free": ["https://kubernetes.io/docs/tutorials/", "https://www.youtube.com/c/TechWorldwithNana"],
        "course": "Kubernetes for Beginners — KodeKloud",
        "time_weeks": 3,
    },
    "aws": {
        "free": ["https://aws.amazon.com/training/free/", "https://www.youtube.com/c/AmazonWebServices"],
        "course": "AWS Certified Cloud Practitioner — AWS Skill Builder (free)",
        "time_weeks": 4,
    },
    "react": {
        "free": ["https://react.dev/learn", "https://www.youtube.com/c/TraversyMedia"],
        "course": "The Ultimate React Course — Jonas Schmedtmann, Udemy",
        "time_weeks": 4,
    },
    "tensorflow": {
        "free": ["https://www.tensorflow.org/tutorials", "https://www.youtube.com/c/TensorFlow"],
        "course": "DeepLearning.AI TensorFlow Developer — Coursera",
        "time_weeks": 6,
    },
    "pytorch": {
        "free": ["https://pytorch.org/tutorials/", "https://www.youtube.com/c/AladdinPersson"],
        "course": "PyTorch for Deep Learning — freeCodeCamp YouTube",
        "time_weeks": 5,
    },
    "system design": {
        "free": ["https://github.com/donnemartin/system-design-primer", "https://www.youtube.com/c/GauravSensei"],
        "course": "Grokking the System Design Interview — Educative.io",
        "time_weeks": 4,
    },
    "data structures": {
        "free": ["https://www.youtube.com/c/NeetCode", "https://leetcode.com/explore/"],
        "course": "Data Structures and Algorithms — Abdul Bari, Udemy",
        "time_weeks": 6,
    },
    "langchain": {
        "free": ["https://python.langchain.com/docs/", "https://www.youtube.com/c/SamWitteveen"],
        "course": "LangChain for LLM Application Development — DeepLearning.AI (free)",
        "time_weeks": 2,
    },
    "tableau": {
        "free": ["https://public.tableau.com/en-us/s/resources", "https://www.youtube.com/c/TableauTim"],
        "course": "Tableau 2024 A-Z — Udemy",
        "time_weeks": 2,
    },
    "powerbi": {
        "free": ["https://learn.microsoft.com/en-us/power-bi/", "https://www.youtube.com/c/GuyInACube"],
        "course": "Microsoft Power BI Desktop — Udemy",
        "time_weeks": 2,
    },
    "git": {
        "free": ["https://git-scm.com/book/en/v2", "https://www.youtube.com/watch?v=RGOj5yH7evk"],
        "course": "Git & GitHub Crash Course — freeCodeCamp YouTube",
        "time_weeks": 1,
    },
    "fastapi": {
        "free": ["https://fastapi.tiangolo.com/tutorial/", "https://www.youtube.com/c/ArjanCodes"],
        "course": "FastAPI — The Complete Course — Udemy",
        "time_weeks": 2,
    },
    "kafka": {
        "free": ["https://kafka.apache.org/documentation/", "https://www.youtube.com/c/ConfluentInc"],
        "course": "Apache Kafka Series — Udemy (Stéphane Maarek)",
        "time_weeks": 3,
    },
    "spark": {
        "free": ["https://spark.apache.org/docs/latest/", "https://www.youtube.com/c/SparkbyExamples"],
        "course": "Taming Big Data with Apache Spark — Udemy",
        "time_weeks": 3,
    },
    "mlops": {
        "free": ["https://mlops.community/", "https://www.youtube.com/c/MadeWithML"],
        "course": "MLOps Specialization — DeepLearning.AI, Coursera",
        "time_weeks": 6,
    },
    "agile": {
        "free": ["https://www.atlassian.com/agile", "https://www.youtube.com/watch?v=Z9QbYZh1YXY"],
        "course": "Professional Scrum Master — Scrum.org (free learning path)",
        "time_weeks": 1,
    },
}


def _lookup_static(skill: str) -> dict | None:
    skill_lower = skill.lower()
    for key, data in RESOURCE_MAP.items():
        if key in skill_lower or skill_lower in key:
            return {**data, "skill": skill, "source": "curated"}
    return None


def recommend_resources(
    skills_missing: list[str],
    target_role: str,
    experience_level: str = "Beginner",
    top_n: int = 8,
) -> dict:
    """
    Returns a prioritised learning plan for the skill gaps.

    Returns
    -------
    {
        "learning_plan": [
            {
                "skill": str,
                "priority": "High" | "Medium" | "Low",
                "reason": str,
                "estimated_weeks": int,
                "free_resources": [str],
                "recommended_course": str,
                "prerequisite_of": [str],
            }
        ],
        "total_estimated_weeks": int,
        "suggested_order": [str],
        "quick_wins": [str],   ← skills learnable in ≤ 2 weeks
    }
    """

    # Cap to top_n most important gaps
    gaps = skills_missing[:top_n]

    # Build static lookups for known skills
    static_hits = {}
    unknown_skills = []
    for skill in gaps:
        hit = _lookup_static(skill)
        if hit:
            static_hits[skill] = hit
        else:
            unknown_skills.append(skill)

    # LLM fills in prioritisation + unknown skills
    prompt = f"""
You are a senior technical learning advisor helping a candidate become job-ready
for the role of {target_role} at {experience_level} level.

SKILL GAPS TO ADDRESS:
{json.dumps(gaps, indent=2)}

SKILLS WITH KNOWN RESOURCES (already mapped):
{json.dumps(list(static_hits.keys()))}

SKILLS NEEDING RESOURCE RECOMMENDATIONS:
{json.dumps(unknown_skills)}

YOUR TASKS:
1. For EVERY skill in the gaps list, assign:
   - priority: "High" (core to the role), "Medium" (expected), "Low" (nice to have)
   - reason: one sentence explaining why this matters for {target_role}
   - estimated_weeks: realistic time to reach working proficiency
   - prerequisite_of: which other skills on this list depend on this one

2. For UNKNOWN skills (not in the mapped list), also provide:
   - free_resources: 1-2 real URLs (official docs, YouTube channels, GitHub repos)
   - recommended_course: one specific course name + platform

3. Suggest the ideal learning ORDER considering prerequisites and priority.

4. Identify "quick wins" — skills learnable in 2 weeks or less.

Return ONLY valid JSON:
{{
  "skill_priorities": [
    {{
      "skill": "skill name",
      "priority": "High",
      "reason": "one sentence",
      "estimated_weeks": 3,
      "prerequisite_of": ["other_skill"],
      "free_resources": ["url1", "url2"],
      "recommended_course": "Course name — Platform"
    }}
  ],
  "suggested_order": ["skill1", "skill2", "skill3"],
  "quick_wins": ["skill_a", "skill_b"],
  "total_estimated_weeks": 12,
  "learning_tip": "One personalised tip for this candidate at {experience_level} level"
}}
"""

    raw = call_llm(prompt)
    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        llm_output = json.loads(clean)
    except Exception:
        llm_output = {"skill_priorities": [], "suggested_order": gaps,
                      "quick_wins": [], "total_estimated_weeks": 0, "learning_tip": ""}

    # Merge static resource data into LLM skill priorities
    skill_priorities = llm_output.get("skill_priorities", [])
    for item in skill_priorities:
        skill = item.get("skill", "")
        static = _lookup_static(skill)
        if static:
            # Prefer static curated resources over LLM-generated URLs
            if not item.get("free_resources"):
                item["free_resources"] = static.get("free", [])
            if not item.get("recommended_course"):
                item["recommended_course"] = static.get("course", "")
            if not item.get("estimated_weeks"):
                item["estimated_weeks"] = static.get("time_weeks", 3)

    return {
        "learning_plan":           skill_priorities,
        "suggested_order":         llm_output.get("suggested_order", gaps),
        "quick_wins":              llm_output.get("quick_wins", []),
        "total_estimated_weeks":   llm_output.get("total_estimated_weeks", 0),
        "learning_tip":            llm_output.get("learning_tip", ""),
        "target_role":             target_role,
        "experience_level":        experience_level,
    }
