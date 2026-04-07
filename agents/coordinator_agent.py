"""
coordinator_agent.py
---------------------
Meta-agent that:
  1. Collects outputs from all four specialist agents
     (Resume, DSA Tutor, Interview, Job Match)
  2. Detects contradictions / inconsistencies between them
  3. Resolves conflicts with LLM reasoning
  4. Produces a single unified Placement Readiness Report

Place this file at:  agents/coordinator_agent.py
"""

import json
from utils.llm import call_llm


# ── Contradiction detection (rule-based, runs before LLM) ────────────────────

def _detect_contradictions(
    resume_data: dict,
    dsa_data: dict,
    interview_data: dict,
    job_match_data: dict,
) -> list[str]:
    """
    Check for logical inconsistencies across agent outputs.
    Returns a list of human-readable contradiction strings for the LLM to resolve.
    """
    contradictions = []

    resume_exp   = (resume_data.get("experience_level") or "").lower()
    interview_score = float(interview_data.get("overall_score") or 0)
    match_score     = float(job_match_data.get("readiness_score") or 0)

    dsa_overall  = dsa_data.get("overall_completion", 0)
    dsa_streak   = dsa_data.get("streak", {}).get("current", 0)

    resume_skills   = set(s.lower() for s in resume_data.get("skills_present", []))
    job_matched     = set(s.lower() for s in job_match_data.get("matched_skills", []))
    job_missing     = set(s.lower() for s in job_match_data.get("missing_skills", []))

    # ── 1. Experience level vs interview score ────────────────────────────────
    if "advanced" in resume_exp and interview_score < 5:
        contradictions.append(
            f"Resume claims Advanced experience level, but interview score is only "
            f"{interview_score}/10 — suggests over-representation of skills on resume."
        )
    if "beginner" in resume_exp and interview_score >= 8:
        contradictions.append(
            f"Resume claims Beginner experience, but interview score is {interview_score}/10 "
            f"— candidate may be undervaluing themselves."
        )

    # ── 2. Job match score vs interview readiness ─────────────────────────────
    if match_score >= 75 and interview_score < 5:
        contradictions.append(
            f"Job match score is high ({match_score}%) but interview performance is low "
            f"({interview_score}/10) — candidate has the skills on paper but struggles under pressure."
        )
    if match_score < 40 and interview_score >= 8:
        contradictions.append(
            f"Interview score is strong ({interview_score}/10) but job match is low ({match_score}%) "
            f"— candidate communicates well but has skill gaps for this specific role."
        )

    # ── 3. DSA completion vs technical interview score ────────────────────────
    if dsa_overall < 20 and interview_score >= 7:
        contradictions.append(
            f"DSA completion is only {dsa_overall}% but technical interview score is {interview_score}/10 "
            f"— good natural problem-solving, but structured DSA practice would further strengthen performance."
        )
    if dsa_overall >= 60 and interview_score < 5:
        contradictions.append(
            f"DSA completion is {dsa_overall}% (significant practice) but interview score is low "
            f"({interview_score}/10) — practicing problems may not be translating to interview performance; "
            f"focus on explaining thought process out loud."
        )

    # ── 4. Skills: resume says present, job match says missing ───────────────
    overlap_contradiction = resume_skills & job_missing
    if overlap_contradiction:
        skills_str = ", ".join(list(overlap_contradiction)[:5])
        contradictions.append(
            f"Resume lists these skills as present, but job match flags them as missing: {skills_str}. "
            f"Either the resume descriptions are vague or the skill depth is insufficient for this role."
        )

    # ── 5. DSA streak vs overall commitment ───────────────────────────────────
    if dsa_streak == 0 and dsa_overall > 50:
        contradictions.append(
            "Candidate has completed over half the DSA curriculum but has a broken streak — "
            "progress may have stalled recently."
        )

    return contradictions


# ── Main coordinator function ─────────────────────────────────────────────────

def generate_readiness_report(
    resume_data: dict,
    dsa_data: dict,
    interview_data: dict,
    job_match_data: dict,
    target_role: str,
) -> dict:
    """
    Accepts structured outputs from all four agents and produces a unified
    Placement Readiness Report.

    Parameters
    ----------
    resume_data    : parsed JSON output from resume_agent.analyze_resume()
    dsa_data       : output from progress_tracker.get_all_progress()
    interview_data : parsed session summary from interview_agent.generate_session_summary()
    job_match_data : first item in suitable_roles[] from job_match_agent.match_jobs()
    target_role    : the user's target job title

    Returns
    -------
    dict with keys:
        overall_readiness_score  (0-100)
        readiness_label          (Not Ready / Developing / Almost Ready / Ready)
        contradiction_count      (int)
        contradictions_detected  (list[str])
        resolution               (str — LLM reasoning about contradictions)
        dimension_scores         (dict)
        strengths                (list[str])
        critical_gaps            (list[str])
        priority_actions         (list[str])
        personalized_roadmap     (list[str])
        estimated_weeks_to_ready (int)
        encouragement            (str)
    """

    # ── Step 1: Rule-based contradiction detection ────────────────────────────
    contradictions = _detect_contradictions(
        resume_data, dsa_data, interview_data, job_match_data
    )

    # ── Step 2: Compute weighted readiness score (no LLM for numbers) ─────────
    resume_exp_map = {"beginner": 30, "intermediate": 60, "advanced": 85}
    resume_exp_score = resume_exp_map.get(
        (resume_data.get("experience_level") or "beginner").lower(), 40
    )
    interview_score  = float(interview_data.get("overall_score") or 0) * 10
    job_match_score  = float(job_match_data.get("readiness_score") or 0)
    dsa_score        = float(dsa_data.get("overall_completion") or 0)

    # Weights: interview 35%, job match 35%, resume 20%, DSA 10%
    weighted = (
        interview_score  * 0.35 +
        job_match_score  * 0.35 +
        resume_exp_score * 0.20 +
        dsa_score        * 0.10
    )
    overall_score = round(min(100, max(0, weighted)), 1)

    if overall_score >= 75:
        readiness_label = "Ready"
    elif overall_score >= 55:
        readiness_label = "Almost Ready"
    elif overall_score >= 35:
        readiness_label = "Developing"
    else:
        readiness_label = "Not Ready"

    dimension_scores = {
        "resume_strength":     round(resume_exp_score, 1),
        "interview_readiness": round(interview_score, 1),
        "job_match":           round(job_match_score, 1),
        "dsa_completion":      round(dsa_score, 1),
    }

    # ── Step 3: LLM — reasoning, resolution, and personalized plan ───────────
    contradictions_block = (
        "\n".join(f"  - {c}" for c in contradictions)
        if contradictions
        else "  None detected."
    )

    prompt = f"""
You are a senior career coach and placement readiness advisor.
You have received outputs from four AI specialist agents for a candidate.

═══ CANDIDATE DATA ═══

TARGET ROLE: {target_role}

RESUME ANALYSIS:
- Skills present: {', '.join(resume_data.get('skills_present', [])[:15])}
- Skills missing: {', '.join(resume_data.get('skills_missing', [])[:10])}
- Experience level: {resume_data.get('experience_level', 'Unknown')}
- Strengths: {', '.join(resume_data.get('strengths', [])[:5])}
- Weaknesses: {', '.join(resume_data.get('weaknesses', [])[:5])}

DSA PROGRESS:
- Overall completion: {dsa_data.get('overall_completion', 0)}%
- Problems completed: {dsa_data.get('completed_problems', 0)} / {dsa_data.get('total_problems', 0)}
- Current streak: {dsa_data.get('streak', {}).get('current', 0)} days
- Longest streak: {dsa_data.get('streak', {}).get('longest', 0)} days

INTERVIEW PERFORMANCE:
- Overall score: {interview_data.get('overall_score', 0)}/10
- Grade: {interview_data.get('overall_grade', 'N/A')}
- Readiness verdict: {interview_data.get('readiness_verdict', 'N/A')}
- Strengths: {', '.join(interview_data.get('strengths', [])[:4])}
- Areas for improvement: {', '.join(interview_data.get('areas_for_improvement', [])[:4])}
- Score breakdown: {json.dumps(interview_data.get('score_breakdown', {}))}

JOB MATCH:
- Match score: {job_match_data.get('readiness_score', 0)}%
- Matched skills: {', '.join(job_match_data.get('matched_skills', [])[:8])}
- Missing skills: {', '.join(job_match_data.get('missing_skills', [])[:8])}

COMPUTED WEIGHTED READINESS SCORE: {overall_score}/100
READINESS LABEL: {readiness_label}

═══ CONTRADICTIONS DETECTED ═══
{contradictions_block}

═══ YOUR TASK ═══

1. RESOLVE the contradictions above with nuanced reasoning — explain WHY each
   contradiction exists and what the candidate should do about it.
   If no contradictions, write "No contradictions — all agents are aligned."

2. SYNTHESIZE a unified, honest assessment of where this candidate stands.

3. GENERATE a prioritized, specific action plan for this candidate.

Return ONLY valid JSON with this exact structure:
{{
  "resolution": "2-3 sentences resolving any contradictions, or confirming alignment",
  "unified_assessment": "3-4 sentence honest overall assessment of the candidate",
  "strengths": [
    "Specific strength 1 grounded in the data",
    "Specific strength 2",
    "Specific strength 3"
  ],
  "critical_gaps": [
    "Most important gap to address",
    "Second most important gap",
    "Third most important gap"
  ],
  "priority_actions": [
    "Most impactful action to take this week",
    "Second priority action",
    "Third priority action",
    "Fourth priority action"
  ],
  "personalized_roadmap": [
    "Week 1-2: specific focus area",
    "Week 3-4: specific focus area",
    "Week 5-6: specific focus area",
    "Week 7-8: specific focus area"
  ],
  "estimated_weeks_to_ready": 6,
  "encouragement": "One warm, specific, motivating sentence for this candidate"
}}
"""

    raw = call_llm(prompt)

    try:
        import re
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        llm_output = json.loads(clean)
    except Exception:
        llm_output = {
            "resolution": "Could not parse LLM output.",
            "unified_assessment": "Please try again.",
            "strengths": [],
            "critical_gaps": [],
            "priority_actions": [],
            "personalized_roadmap": [],
            "estimated_weeks_to_ready": 8,
            "encouragement": "Keep going — consistency is key!",
        }

    # ── Step 4: Assemble final report ─────────────────────────────────────────
    return {
        "overall_readiness_score":  overall_score,
        "readiness_label":          readiness_label,
        "contradiction_count":      len(contradictions),
        "contradictions_detected":  contradictions,
        "dimension_scores":         dimension_scores,
        **llm_output,
    }
