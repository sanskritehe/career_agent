"""
interview_agent.py
------------------
Core logic for the Interview Prep Agent.
Generates contextual interview questions based on:
- Resume content
- Target job role
- Interview type (Technical, HR, Behavioral, System Design, Mixed)
- Difficulty level (Entry / Mid / Senior)

Technical questions include full LeetCode-style coding problems with:
- Problem statement + constraints + examples
- Brute force → optimal approach walkthrough
- Full working code solution
- Time & space complexity analysis
- Common edge cases and follow-ups

Inspired by interview simulation research (arxiv 2405.18113):
- Role-aware questioning
- Difficulty-calibrated prompts
- Structured answer frameworks (STAR for behavioral, step-by-step for technical)
"""

import json
import re
from utils.llm import call_llm


# ── Question type definitions ────────────────────────────────────────────────

INTERVIEW_TYPES = {
    "Technical": {
        "description": "Coding problems, algorithms, data structures, and role-specific tech stack questions",
        "icon": "💻",
        "color": "#4F8EF7",
    },
    "HR / Cultural Fit": {
        "description": "Company culture, motivation, values alignment, and situational questions",
        "icon": "🤝",
        "color": "#F7844F",
    },
    "Behavioral (STAR)": {
        "description": "Past experience questions using the STAR framework (Situation, Task, Action, Result)",
        "icon": "⭐",
        "color": "#A855F7",
    },
    "System Design": {
        "description": "Architecture, scalability, trade-offs, and high-level design questions",
        "icon": "🏗️",
        "color": "#10B981",
    },
    "Mixed": {
        "description": "A balanced mix of all question types — closest to a real interview",
        "icon": "🎯",
        "color": "#F59E0B",
    },
}

DIFFICULTY_LEVELS = {
    "Entry Level": {
        "label": "Entry Level",
        "description": "Fresher / 0–1 years experience",
        "icon": "🟢",
        "depth": "basic understanding, definitions, simple examples",
        "leetcode_range": "Easy problems — arrays, strings, basic loops, simple hash maps",
        "coding_split": "50% conceptual, 50% coding (Easy LeetCode-style)",
    },
    "Mid Level": {
        "label": "Mid Level",
        "description": "2–4 years experience",
        "icon": "🟡",
        "depth": "applied knowledge, trade-offs, real-world scenarios",
        "leetcode_range": "Medium problems — two pointers, sliding window, DFS/BFS, dynamic programming basics",
        "coding_split": "30% conceptual, 70% coding (Medium LeetCode-style)",
    },
    "Senior Level": {
        "label": "Senior Level",
        "description": "5+ years experience",
        "icon": "🔴",
        "depth": "deep expertise, architectural decisions, mentoring, ambiguity handling",
        "leetcode_range": "Hard problems — advanced DP, graphs, segment trees, complex optimization",
        "coding_split": "20% conceptual, 80% coding (Medium-Hard LeetCode-style)",
    },
}

# Maps role keywords to relevant DSA topics and coding domains
ROLE_CODING_FOCUS = {
    "frontend": ["DOM manipulation", "async/await/promises", "React hooks state logic", "browser APIs", "string parsing"],
    "backend": ["REST API design", "SQL query optimization", "caching strategies", "concurrency patterns", "string/text processing"],
    "fullstack": ["REST APIs", "database design", "async patterns", "data structures"],
    "data scientist": ["pandas/numpy operations", "statistical algorithms", "matrix operations", "sliding window on time series"],
    "data engineer": ["ETL pipelines logic", "SQL window functions", "stream processing patterns", "graph problems for pipelines"],
    "ml engineer": ["gradient descent implementation", "matrix operations", "model optimization logic", "feature engineering algorithms"],
    "devops": ["scripting/automation logic", "graph problems for infra dependencies", "interval scheduling"],
    "mobile": ["memory management patterns", "async patterns", "UI state management logic"],
    "default": ["arrays", "strings", "hash maps", "trees", "graphs", "dynamic programming", "sorting & searching"],
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_role_coding_focus(target_role: str) -> list:
    role_lower = target_role.lower()
    for key, topics in ROLE_CODING_FOCUS.items():
        if key in role_lower:
            return topics
    return ROLE_CODING_FOCUS["default"]


# ── Prompt builders ───────────────────────────────────────────────────────────

def _build_technical_prompt(
    resume_text: str,
    target_role: str,
    difficulty: str,
    num_questions: int,
    focus_areas: list = None,
) -> str:
    difficulty_info = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["Mid Level"])
    coding_topics = _get_role_coding_focus(target_role)
    focus_str = ""
    if focus_areas:
        focus_str = f"Additionally focus on these specific areas: {', '.join(focus_areas)}."

    num_coding = max(1, round(num_questions * 0.6))
    num_conceptual = num_questions - num_coding

    return f"""
You are a senior software engineer conducting a technical interview at a top tech company (FAANG-level).

CANDIDATE RESUME:
{resume_text[:3000]}

TARGET ROLE: {target_role}
DIFFICULTY: {difficulty} — {difficulty_info['depth']}
CODING LEVEL: {difficulty_info['leetcode_range']}
RELEVANT TOPICS FOR THIS ROLE: {', '.join(coding_topics)}
{focus_str}

TASK:
Generate exactly {num_questions} technical interview questions:
- {num_coding} must be full CODING PROBLEMS (LeetCode-style, with real problem statements)
- {num_conceptual} can be conceptual/theory questions specific to the role's tech stack

═══════════════════════════════════════════════════════
CRITICAL RULES FOR CODING PROBLEMS:
═══════════════════════════════════════════════════════

For every coding question, the answer_guide MUST contain ALL of these fields with REAL content:

1. "problem_statement": Full problem description like on LeetCode. Include:
   - Clear problem description
   - Input/output format
   - At least 2-3 concrete examples with inputs and expected outputs
   - Constraints (e.g., 1 <= n <= 10^5, -10^9 <= nums[i] <= 10^9)

2. "brute_force": The naive/simple approach
   - Explain the logic in plain English
   - Full working code in the most relevant language for the role (Python preferred)
   - Time complexity and Space complexity

3. "optimal_solution": The best approach
   - Explain the KEY INSIGHT that makes it optimal
   - Step-by-step walkthrough of the algorithm
   - Full working code with inline comments
   - Time complexity and Space complexity

4. "dry_run_example": Walk through one example step-by-step showing exactly how the optimal solution executes

5. "edge_cases": Important edge cases to handle (empty input, single element, all same values, negatives, etc.)

6. "companies": Real companies known to ask this type of problem

═══════════════════════════════════════════════════════
DIFFICULTY CALIBRATION:
═══════════════════════════════════════════════════════
- Entry Level: Two Sum, Valid Parentheses, Reverse String, FizzBuzz, Find Duplicates
- Mid Level: Longest Substring Without Repeating Characters, Merge Intervals, Binary Search, Tree Traversal, BFS/DFS
- Senior Level: Hard DP (Edit Distance, Word Break II), Dijkstra, Topological Sort, Advanced Sliding Window, LRU Cache

Tailor problems to the {target_role} role where possible.

Respond ONLY with a valid JSON object:
{{
  "interview_session": {{
    "role": "{target_role}",
    "type": "Technical",
    "difficulty": "{difficulty}",
    "total_questions": {num_questions},
    "estimated_duration_mins": {num_questions * 8},
    "tips": [
      "Think out loud — interviewers care about your thought process",
      "Always clarify constraints before coding",
      "Start with brute force, then optimize",
      "Test your solution with edge cases before saying you're done"
    ]
  }},
  "questions": [
    {{
      "id": 1,
      "question": "The problem title / question as the interviewer would say it",
      "is_coding_problem": true,
      "type": "Technical",
      "difficulty": "{difficulty}",
      "tags": ["Arrays", "Hash Map"],
      "time_estimate_mins": 20,
      "answer_guide": {{
        "overview": "What DSA concept or pattern this problem tests",
        "problem_statement": "Full LeetCode-style problem statement with examples and constraints",
        "brute_force": {{
          "explanation": "Plain English explanation of the naive approach",
          "code": "def solution(nums):\\n    # full working code\\n    pass",
          "time_complexity": "O(n^2)",
          "space_complexity": "O(1)"
        }},
        "optimal_solution": {{
          "key_insight": "The crucial observation that leads to the optimal solution",
          "explanation": "Step-by-step explanation of the optimal algorithm",
          "code": "def solution(nums):\\n    # full working optimized code with comments\\n    pass",
          "time_complexity": "O(n)",
          "space_complexity": "O(n)"
        }},
        "dry_run_example": "Walk through: input=[2,7,11,15], target=9 → step1: ... → output: [0,1]",
        "edge_cases": ["Empty array", "Single element", "No valid answer", "Duplicates"],
        "companies": ["Google", "Amazon", "Microsoft"],
        "key_points": ["Always ask about constraints first", "Hash map gives O(1) lookup"],
        "what_to_avoid": ["Don't jump to code without clarifying", "Don't forget edge cases"],
        "follow_up_questions": ["What if the array is sorted?", "What if you need all pairs?"],
        "scoring_rubric": {{
          "excellent": "Arrives at optimal, explains complexity, handles edge cases",
          "good": "Gets brute force, partially optimizes",
          "needs_improvement": "Cannot code a working solution"
        }}
      }}
    }}
  ]
}}
"""


def _build_question_prompt(
    resume_text: str,
    target_role: str,
    interview_type: str,
    difficulty: str,
    num_questions: int = 8,
    focus_areas: list = None,
) -> str:
    # Technical gets its own dedicated prompt with LeetCode-style coding
    if interview_type == "Technical":
        return _build_technical_prompt(
            resume_text=resume_text,
            target_role=target_role,
            difficulty=difficulty,
            num_questions=num_questions,
            focus_areas=focus_areas,
        )

    focus_str = ""
    if focus_areas:
        focus_str = f"\nFocus especially on these areas: {', '.join(focus_areas)}."

    difficulty_info = DIFFICULTY_LEVELS.get(difficulty, DIFFICULTY_LEVELS["Mid Level"])
    type_info = INTERVIEW_TYPES.get(interview_type, INTERVIEW_TYPES["Mixed"])

    type_instructions = {
        "HR / Cultural Fit": f"""
Generate {num_questions} HR and cultural fit interview questions for a {target_role} role.
Cover: motivation/goals (25%), culture/values alignment (25%), conflict resolution (25%), career trajectory (25%).
Make questions open-ended and introspective.
""",
        "Behavioral (STAR)": f"""
Generate {num_questions} behavioral interview questions for a {target_role} role using the STAR framework.
Focus on: leadership, teamwork, handling failure, problem ownership, communication under pressure.
Each question should start with "Tell me about a time..." or "Describe a situation where..."
""",
        "System Design": f"""
Generate {num_questions} system design interview questions appropriate for a {target_role}.
Cover: scalability, database design, API design, caching, trade-offs, real-world architecture.
Questions should be open-ended design challenges.
""",
        "Mixed": f"""
Generate {num_questions} interview questions for a {target_role} role across all categories:
- 2-3 Coding/Technical questions (LeetCode-style with full problem statements and solutions)
- 2 Behavioral/STAR questions
- 1-2 HR/motivation questions
- 1-2 System design or problem-solving questions
For each coding question, set "is_coding_problem": true and include brute_force and optimal_solution with code.
Label each question with its type in the "type" field.
""",
    }

    instruction = type_instructions.get(interview_type, type_instructions["Mixed"])

    prompt = f"""
You are an expert technical interviewer and career coach conducting a realistic job interview simulation.

CANDIDATE RESUME:
{resume_text[:3000]}

TARGET ROLE: {target_role}
INTERVIEW TYPE: {interview_type} — {type_info['description']}
DIFFICULTY: {difficulty} — {difficulty_info['depth']}
{focus_str}

TASK:
{instruction}

For EACH question provide a comprehensive answer_guide. For coding questions ALSO include:
problem_statement (with examples + constraints), brute_force (with code + complexity), optimal_solution (with code + complexity), dry_run_example, edge_cases, companies.

IMPORTANT: Tailor every question to the candidate's actual background from their resume.

Respond ONLY with a valid JSON object:
{{
  "interview_session": {{
    "role": "{target_role}",
    "type": "{interview_type}",
    "difficulty": "{difficulty}",
    "total_questions": {num_questions},
    "estimated_duration_mins": {num_questions * 6},
    "tips": ["tip1", "tip2", "tip3"]
  }},
  "questions": [
    {{
      "id": 1,
      "question": "The interview question text",
      "is_coding_problem": false,
      "type": "{interview_type if interview_type != 'Mixed' else 'Technical/Behavioral/HR/System Design'}",
      "difficulty": "{difficulty}",
      "tags": ["tag1", "tag2"],
      "time_estimate_mins": 5,
      "answer_guide": {{
        "overview": "What this question tests and why it's asked",
        "ideal_answer": "Comprehensive model answer",
        "key_points": ["point1", "point2", "point3"],
        "what_to_avoid": ["mistake1", "mistake2"],
        "follow_up_questions": ["follow_up1", "follow_up2"],
        "scoring_rubric": {{
          "excellent": "What an excellent answer looks like",
          "good": "What a good answer looks like",
          "needs_improvement": "What a weak answer looks like"
        }}
      }}
    }}
  ]
}}
"""
    return prompt


def _build_followup_prompt(
    question: str,
    candidate_answer: str,
    role: str,
    difficulty: str,
    is_coding: bool = False,
) -> str:
    coding_instructions = ""
    if is_coding:
        coding_instructions = """
Since this is a coding problem, also evaluate:
- Correctness of their algorithm/approach
- Whether they identified the right data structure or pattern
- Time and space complexity awareness
- Code quality and edge case handling
- Whether they thought through brute force before optimizing
"""

    return f"""
You are an expert interviewer providing real-time feedback on a candidate's interview answer.

ROLE: {role}
DIFFICULTY: {difficulty}
QUESTION: {question}
CANDIDATE'S ANSWER: {candidate_answer}
{coding_instructions}

Evaluate the answer and provide structured feedback.

Respond ONLY with valid JSON:
{{
  "score": 7,
  "grade": "Good",
  "strengths": ["strength1", "strength2"],
  "improvements": ["improvement1", "improvement2"],
  "model_answer": "The ideal answer / correct solution with explanation",
  "follow_up": "A natural follow-up question the interviewer would ask",
  "encouragement": "A brief encouraging note for the candidate"
}}
"""


def _build_session_summary_prompt(
    role: str,
    interview_type: str,
    difficulty: str,
    qa_pairs: list,
) -> str:
    qa_text = ""
    for i, pair in enumerate(qa_pairs, 1):
        qa_text += f"\nQ{i}: {pair.get('question', '')}\n"
        qa_text += f"A{i}: {pair.get('answer', '(skipped)')}\n"

    return f"""
You are an expert interview coach. Analyze this completed mock interview session and provide comprehensive feedback.

ROLE: {role}
INTERVIEW TYPE: {interview_type}
DIFFICULTY: {difficulty}

INTERVIEW TRANSCRIPT:
{qa_text}

Provide a detailed post-interview analysis.

Respond ONLY with valid JSON:
{{
  "overall_score": 7.5,
  "overall_grade": "Good",
  "summary": "2-3 sentence overall assessment",
  "strengths": ["strength1", "strength2", "strength3"],
  "areas_for_improvement": ["area1", "area2", "area3"],
  "readiness_verdict": "Ready / Almost Ready / Needs More Prep",
  "readiness_explanation": "Why this verdict",
  "recommended_topics": ["topic1", "topic2"],
  "next_steps": ["step1", "step2", "step3"],
  "interview_tips": ["tip1", "tip2", "tip3"],
  "score_breakdown": {{
    "technical_depth": 7,
    "communication": 8,
    "problem_solving": 7,
    "confidence": 6
  }}
}}
"""


# ── Public API ────────────────────────────────────────────────────────────────

def generate_interview_questions(
    resume_text: str,
    target_role: str,
    interview_type: str = "Mixed",
    difficulty: str = "Mid Level",
    num_questions: int = 8,
    focus_areas: list = None,
) -> dict:
    """
    Generate a complete interview question set tailored to the candidate.
    Returns a parsed dict with session info and questions list.
    """
    prompt = _build_question_prompt(
        resume_text=resume_text,
        target_role=target_role,
        interview_type=interview_type,
        difficulty=difficulty,
        num_questions=num_questions,
        focus_areas=focus_areas,
    )

    raw = call_llm(prompt)

    try:
        # Strip markdown fences if present
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        return json.loads(clean)
    except (json.JSONDecodeError, TypeError):
        return {
            "error": "Failed to parse interview questions. Please try again.",
            "raw": raw,
        }


def evaluate_answer(
    question: str,
    candidate_answer: str,
    role: str,
    difficulty: str = "Mid Level",
    is_coding: bool = False,
) -> dict:
    """
    Evaluate a candidate's answer to a question and return structured feedback.
    """
    if not candidate_answer or not candidate_answer.strip():
        return {
            "score": 0,
            "grade": "Not Attempted",
            "strengths": [],
            "improvements": ["No answer was provided."],
            "model_answer": "Please attempt the question to receive feedback.",
            "follow_up": "",
            "encouragement": "Don't be afraid to attempt! Even an imperfect answer shows your thought process.",
        }

    prompt = _build_followup_prompt(
        question=question,
        candidate_answer=candidate_answer,
        role=role,
        difficulty=difficulty,
        is_coding=is_coding,
    )

    raw = call_llm(prompt)

    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        return json.loads(clean)
    except (json.JSONDecodeError, TypeError):
        return {
            "score": 5,
            "grade": "Unable to evaluate",
            "strengths": ["Answer was provided"],
            "improvements": ["Evaluation service encountered an issue"],
            "model_answer": "Please try again for a full evaluation.",
            "follow_up": "",
            "encouragement": "Keep practicing!",
        }


def generate_session_summary(
    role: str,
    interview_type: str,
    difficulty: str,
    qa_pairs: list,
) -> dict:
    """
    Generate a comprehensive post-session performance summary.
    """
    prompt = _build_session_summary_prompt(
        role=role,
        interview_type=interview_type,
        difficulty=difficulty,
        qa_pairs=qa_pairs,
    )

    raw = call_llm(prompt)

    try:
        clean = re.sub(r"```(?:json)?|```", "", raw).strip()
        return json.loads(clean)
    except (json.JSONDecodeError, TypeError):
        return {
            "overall_score": 6,
            "overall_grade": "Good",
            "summary": "Session completed. Keep practicing to improve your performance.",
            "strengths": ["Completed the session"],
            "areas_for_improvement": ["Continue practicing"],
            "readiness_verdict": "Almost Ready",
            "readiness_explanation": "More practice will build confidence.",
            "recommended_topics": [],
            "next_steps": ["Review the questions you found difficult", "Practice more mock interviews"],
            "interview_tips": ["Be concise", "Use examples", "Ask clarifying questions"],
            "score_breakdown": {
                "technical_depth": 6,
                "communication": 6,
                "problem_solving": 6,
                "confidence": 6,
            },
        }