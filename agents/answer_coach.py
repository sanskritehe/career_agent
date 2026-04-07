"""
answer_coach.py
---------------
Takes a candidate's rough/weak interview answer and:
  1. Scores it on multiple dimensions
  2. Rewrites it using the STAR framework (for behavioral) or structured
     technical format (for coding/system design questions)
  3. Explains exactly what was weak and why the rewrite is stronger

Place at: agents/answer_coach.py
"""

import json
import re
from utils.llm import call_llm


QUESTION_TYPES = ["Behavioral", "Technical", "System Design", "HR / Cultural Fit"]


def coach_answer(
    question: str,
    raw_answer: str,
    question_type: str = "Behavioral",
    target_role: str = "",
    difficulty: str = "Mid Level",
) -> dict:
    """
    Analyses a candidate's interview answer and returns a coaching report.

    Returns
    -------
    {
        "original_score":    int (0-10),
        "improved_score":    int (0-10),
        "question_type":     str,
        "dimension_scores":  dict,
        "weaknesses":        list[str],
        "rewritten_answer":  str,
        "framework_used":    str,
        "key_improvements":  list[str],
        "what_interviewer_wants": str,
        "follow_up_prep":    list[str],
    }
    """

    framework_guidance = {
        "Behavioral": (
            "STAR Framework: Situation → Task → Action → Result. "
            "Each component must be explicit. Result must be quantified if possible."
        ),
        "Technical": (
            "Structured Technical Format: Clarify → Brute Force → Optimise → Complexity. "
            "Show thought process, don't jump to solution."
        ),
        "System Design": (
            "System Design Format: Requirements → Estimates → High-Level Design → "
            "Deep Dive → Trade-offs → Bottlenecks."
        ),
        "HR / Cultural Fit": (
            "CARL Framework: Context → Action → Result → Learning. "
            "Show self-awareness and growth mindset."
        ),
    }

    framework = framework_guidance.get(question_type, framework_guidance["Behavioral"])

    prompt = f"""
You are an expert interview coach preparing candidates for top tech company interviews.

QUESTION: {question}
QUESTION TYPE: {question_type}
TARGET ROLE: {target_role or "Software Engineer"}
DIFFICULTY: {difficulty}

CANDIDATE'S ANSWER:
{raw_answer}

FRAMEWORK TO USE: {framework}

YOUR TASKS:

1. SCORE the original answer on these dimensions (0-10 each):
   - clarity: How clearly is the answer communicated?
   - relevance: Does it answer what was actually asked?
   - depth: Is there sufficient technical/situational depth?
   - structure: Is it well-organised using the expected framework?
   - impact: Does it demonstrate measurable outcomes or insight?

2. IDENTIFY the top 3 specific weaknesses in the original answer.

3. REWRITE the answer using the {framework.split(':')[0]} framework.
   The rewrite should:
   - Be 200-350 words
   - Use the framework structure explicitly
   - Quantify outcomes where possible (even estimated numbers are fine)
   - Sound natural, not robotic
   - Keep the candidate's actual experience (do not invent facts)

4. LIST the key improvements made — be specific about what changed and why.

5. STATE what the interviewer is really testing with this question.

6. SUGGEST 2-3 likely follow-up questions the interviewer might ask next.

Return ONLY valid JSON:
{{
  "original_score": 5,
  "dimension_scores": {{
    "clarity": 6,
    "relevance": 5,
    "depth": 4,
    "structure": 3,
    "impact": 4
  }},
  "weaknesses": [
    "Specific weakness 1",
    "Specific weakness 2",
    "Specific weakness 3"
  ],
  "rewritten_answer": "Full rewritten answer using the framework...",
  "framework_used": "{question_type} — STAR / Technical / etc.",
  "improved_score": 9,
  "key_improvements": [
    "What changed and why it's stronger",
    "Second improvement",
    "Third improvement"
  ],
  "what_interviewer_wants": "One sentence on what this question really tests",
  "follow_up_prep": [
    "Likely follow-up question 1",
    "Likely follow-up question 2",
    "Likely follow-up question 3"
  ]
}}
"""

    raw = call_llm(prompt)
    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        result = json.loads(clean)
        result["question_type"] = question_type
        result["original_answer"] = raw_answer
        result["question"] = question
        return result
    except Exception:
        return {
            "error": "Could not parse coaching output.",
            "raw": raw,
            "original_answer": raw_answer,
            "question": question,
        }


def batch_coach(qa_pairs: list[dict], target_role: str = "", difficulty: str = "Mid Level") -> list[dict]:
    """
    Coach multiple Q&A pairs at once.
    Each item in qa_pairs should have keys: "question", "answer", "type" (optional).

    Useful for post-interview session coaching.
    """
    results = []
    for pair in qa_pairs:
        if not pair.get("answer", "").strip():
            continue
        result = coach_answer(
            question=pair.get("question", ""),
            raw_answer=pair.get("answer", ""),
            question_type=pair.get("type", "Behavioral"),
            target_role=target_role,
            difficulty=difficulty,
        )
        results.append(result)
    return results
