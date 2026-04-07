"""
streamlit_ui.py  —  Interview Prep Agent
-----------------------------------------
UI flow:
  Step 1  → Upload resume + configure session (role, type, difficulty, #questions)
  Step 2  → Question-by-question practice mode with timer + answer input
  Step 3  → Per-question AI feedback (score, strengths, model answer)
  Step 4  → Full session summary with readiness verdict
"""

import time
import streamlit as st
from utils.pdf_parser import extract_resume_text
from agents.interview.interview_agent import (
    INTERVIEW_TYPES,
    DIFFICULTY_LEVELS,
    generate_interview_questions,
    evaluate_answer,
    generate_session_summary,
)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _score_color(score: float) -> str:
    if score >= 8:
        return "#10B981"
    if score >= 6:
        return "#F59E0B"
    return "#EF4444"


def _grade_emoji(grade: str) -> str:
    mapping = {
        "Excellent": "🏆",
        "Good": "✅",
        "Average": "📊",
        "Needs Improvement": "📝",
        "Not Attempted": "⬜",
        "Unable to evaluate": "❓",
    }
    return mapping.get(grade, "📊")


def _reset_session():
    for key in [
        "interview_questions", "interview_config", "current_q_index",
        "user_answers", "answer_feedback", "session_complete",
        "session_summary", "show_answer", "answer_submitted",
        "timer_start", "answer_text",
    ]:
        if key in st.session_state:
            del st.session_state[key]


def _init_session_state():
    defaults = {
        "interview_questions": None,
        "interview_config": None,
        "current_q_index": 0,
        "user_answers": {},
        "answer_feedback": {},
        "session_complete": False,
        "session_summary": None,
        "show_answer": {},
        "answer_submitted": {},
        "timer_start": None,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


# ── Step 1: Setup ─────────────────────────────────────────────────────────────

def _render_setup():
    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 2rem;
    ">
        <h2 style="color: #e2e8f0; margin: 0 0 0.5rem 0; font-size: 1.6rem;">
            🎤 Interview Prep Agent
        </h2>
        <p style="color: #94a3b8; margin: 0; font-size: 0.95rem;">
            AI-powered mock interviews tailored to your resume and target role.
            Get questions, practice answers, and receive instant expert feedback.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("#### 📄 Resume Upload")
        resume_file = st.file_uploader(
            "Upload your resume (PDF)",
            type=["pdf"],
            key="interview_resume_upload",
            help="Your resume is used to personalise questions to your background",
        )

        if resume_file:
            st.success(f"✅ **{resume_file.name}** uploaded")

        st.markdown("#### 🎯 Target Role")
        target_role = st.text_input(
            "Job role you're interviewing for",
            placeholder="e.g. Backend Engineer, Data Scientist, Product Manager",
            key="interview_target_role",
        )

        st.markdown("#### 🔢 Number of Questions")
        num_questions = st.slider(
            "How many questions?",
            min_value=3,
            max_value=15,
            value=7,
            step=1,
            key="interview_num_q",
            help="Recommended: 7–10 for a realistic session (~35–50 mins)",
        )

    with col_right:
        st.markdown("#### 🗂️ Interview Type")
        interview_type = st.radio(
            "Select interview type",
            options=list(INTERVIEW_TYPES.keys()),
            key="interview_type_select",
            format_func=lambda t: f"{INTERVIEW_TYPES[t]['icon']}  {t}",
        )

        if interview_type:
            info = INTERVIEW_TYPES[interview_type]
            st.markdown(f"""
            <div style="
                background: #1e293b;
                border-left: 3px solid {info['color']};
                border-radius: 8px;
                padding: 0.75rem 1rem;
                margin: 0.5rem 0 1.5rem 0;
                font-size: 0.85rem;
                color: #94a3b8;
            ">
                {info['description']}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("#### ⚡ Difficulty Level")
        difficulty = st.radio(
            "Select difficulty",
            options=list(DIFFICULTY_LEVELS.keys()),
            key="interview_difficulty",
            format_func=lambda d: f"{DIFFICULTY_LEVELS[d]['icon']}  {d} — {DIFFICULTY_LEVELS[d]['description']}",
        )

    # Optional focus areas
    with st.expander("🎛️ Advanced: Focus Areas (optional)", expanded=False):
        st.markdown("Add specific topics you want to focus on:")
        focus_col1, focus_col2 = st.columns(2)
        with focus_col1:
            focus_text = st.text_area(
                "Topics to focus on (one per line)",
                placeholder="e.g.\nSQL query optimization\nSystem design patterns\nLeadership experience",
                height=100,
                key="interview_focus_areas",
            )
        with focus_col2:
            st.markdown("""
            <div style="color: #64748b; font-size: 0.82rem; padding-top: 0.5rem;">
            <b>Examples:</b><br>
            &#8226; React hooks and state management<br>
            &#8226; Handling conflicts in teams<br>
            &#8226; Distributed systems design<br>
            &#8226; Your specific project work<br>
            &#8226; Domain-specific algorithms
            </div>
            """, unsafe_allow_html=True)

    focus_areas = [f.strip() for f in focus_text.split("\n") if f.strip()] if "focus_text" in dir() else []

    st.markdown("<br>", unsafe_allow_html=True)

    # Validation + launch
    ready = resume_file and target_role and target_role.strip()

    if not ready:
        st.info("👆 Upload your resume and enter a target role to get started.")

    launch_col, _ = st.columns([1, 2])
    with launch_col:
        launch = st.button(
            "🚀 Generate Interview Questions",
            disabled=not ready,
            use_container_width=True,
            type="primary",
        )

    if launch and ready:
        with st.spinner("🤖 Crafting your personalised interview session..."):
            resume_text = extract_resume_text(resume_file)

            if not resume_text or not resume_text.strip():
                st.error("❌ Could not extract text from the resume PDF. Please check the file.")
                return

            fa = focus_areas if focus_areas else None
            result = generate_interview_questions(
                resume_text=resume_text,
                target_role=target_role.strip(),
                interview_type=interview_type,
                difficulty=difficulty,
                num_questions=num_questions,
                focus_areas=fa,
            )

            if "error" in result:
                st.error(f"❌ {result['error']}")
                return

            st.session_state.interview_questions = result
            st.session_state.interview_config = {
                "role": target_role.strip(),
                "type": interview_type,
                "difficulty": difficulty,
                "num_questions": num_questions,
                "resume_text": resume_text,
            }
            st.session_state.current_q_index = 0
            st.session_state.user_answers = {}
            st.session_state.answer_feedback = {}
            st.session_state.show_answer = {}
            st.session_state.answer_submitted = {}
            st.rerun()


# ── Step 2 & 3: Practice ──────────────────────────────────────────────────────

def _render_question_card(q: dict, q_index: int, total: int, config: dict):
    q_num = q_index + 1
    question_text = q.get("question", "")
    q_type = q.get("type", config["type"])
    tags = q.get("tags", [])
    time_est = q.get("time_estimate_mins", 5)
    difficulty = q.get("difficulty", config["difficulty"])
    is_coding = q.get("is_coding_problem", False)
    answer_guide = q.get("answer_guide", {})

    type_color = INTERVIEW_TYPES.get(q_type, {}).get("color", "#4F8EF7")
    type_icon = INTERVIEW_TYPES.get(q_type, {}).get("icon", "💬")

    progress_pct = int((q_index / total) * 100)
    st.markdown(
        f'<div style="margin-bottom:1.5rem;">'
        f'<div style="display:flex;justify-content:space-between;color:#94a3b8;font-size:0.82rem;margin-bottom:6px;">'
        f'<span>Question {q_num} of {total}</span><span>{progress_pct}% complete</span>'
        f'</div>'
        f'<div style="background:#1e293b;border-radius:99px;height:6px;">'
        f'<div style="background:linear-gradient(90deg,#6366f1,#8b5cf6);width:{progress_pct}%;height:100%;border-radius:99px;transition:width 0.3s;"></div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    tag_pills = "".join([
        f'<span style="background:#1e293b;color:#94a3b8;border-radius:99px;padding:2px 10px;font-size:0.75rem;margin-right:6px;">{t}</span>'
        for t in tags
    ])
    coding_badge = (
        '<span style="background:#4F8EF722;color:#4F8EF7;border-radius:8px;'
        'padding:4px 12px;font-size:0.8rem;font-weight:700;margin-left:6px;">&#9000; Coding Problem</span>'
    ) if is_coding else ""

    # ⚠️  FIX: emoji chars (⏱ •) break st.markdown on Windows — use HTML entities instead
    card_html = (
        f'<div style="background:linear-gradient(135deg,#0f172a,#1a1f3a);border:1px solid #334155;'
        f'border-top:3px solid {type_color};border-radius:12px;padding:1.75rem;margin-bottom:1rem;">'
        f'<div style="display:flex;align-items:center;gap:10px;margin-bottom:1rem;flex-wrap:wrap;">'
        f'<span style="background:{type_color}22;color:{type_color};border-radius:8px;padding:4px 12px;font-size:0.8rem;font-weight:600;">'
        f'{type_icon} {q_type}</span>'
        f'{coding_badge}'
        f'<span style="color:#64748b;font-size:0.8rem;">&#9201; ~{time_est} mins</span>'
        f'<span style="color:#64748b;font-size:0.8rem;">&#8226; {difficulty}</span>'
        f'</div>'
        f'<p style="color:#e2e8f0;font-size:1.1rem;line-height:1.7;margin:0 0 1rem 0;font-weight:500;">{question_text}</p>'
        f'<div style="margin-top:0.5rem;">{tag_pills}</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

    # For coding problems: show the full LeetCode-style problem statement
    if is_coding:
        problem_statement = answer_guide.get("problem_statement", "")
        companies = answer_guide.get("companies", [])
        if problem_statement:
            company_badges = "".join([
                f'<span style="background:#1e293b;color:#94a3b8;border:1px solid #334155;'
                f'border-radius:6px;padding:2px 10px;font-size:0.75rem;margin-right:5px;">{c}</span>'
                for c in companies
            ])
            st.markdown(
                f'<div style="background:#0d1117;border:1px solid #30363d;border-left:4px solid #4F8EF7;'
                f'border-radius:10px;padding:1.5rem;margin-bottom:1rem;">'
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'margin-bottom:1rem;flex-wrap:wrap;gap:8px;">'
                f'<span style="color:#4F8EF7;font-weight:700;font-size:0.9rem;">&#128203; Problem Statement</span>'
                f'<div>{company_badges}</div></div>'
                f'<div style="color:#c9d1d9;font-size:0.88rem;line-height:1.8;white-space:pre-wrap;">'
                f'{problem_statement}</div></div>',
                unsafe_allow_html=True,
            )


def _render_answer_section(q: dict, q_index: int, config: dict):
    q_id = str(q.get("id", q_index + 1))
    question_text = q.get("question", "")
    answer_guide = q.get("answer_guide", {})
    is_coding = q.get("is_coding_problem", False)

    already_submitted = st.session_state.answer_submitted.get(q_id, False)
    feedback = st.session_state.answer_feedback.get(q_id)
    show_answer_flag = st.session_state.show_answer.get(q_id, False)

    col_answer, col_hint = st.columns([3, 1])

    with col_answer:
        if not already_submitted:
            if is_coding:
                st.markdown("##### ✍️ Your Solution")
                placeholder = (
                    "Write your approach and code here.\n\n"
                    "Tip: Start by explaining your approach in plain English, then write the code.\n"
                    "Example:\n"
                    "Approach: Use a hash map to store seen values...\n\n"
                    "def solution(nums, target):\n"
                    "    seen = {}\n"
                    "    for i, n in enumerate(nums):\n"
                    "        ..."
                )
            else:
                st.markdown("##### ✍️ Your Answer")
                placeholder = "Structure your thoughts clearly. For behavioral questions, use the STAR framework: Situation → Task → Action → Result"

            user_answer = st.text_area(
                "answer",
                height=200 if is_coding else 160,
                key=f"answer_input_{q_id}",
                placeholder=placeholder,
                label_visibility="collapsed",
            )
        else:
            user_answer = st.session_state.user_answers.get(q_id, "")
            label = "##### ✍️ Your Solution" if is_coding else "##### ✍️ Your Answer"
            st.markdown(label)
            font_fam = "monospace" if is_coding else "inherit"
            fallback = '<em style="color:#475569">No answer provided</em>'

            st.markdown(
                f'<div style="background:#0f172a;border:1px solid #334155;border-radius:8px;'
                f'padding:1rem;color:#cbd5e1;font-size:0.88rem;line-height:1.7;min-height:80px;'
                f'white-space:pre-wrap;font-family:{font_fam};">'
                f'{user_answer or fallback}</div>',
                unsafe_allow_html=True,
            )

    with col_hint:
        if is_coding:
            st.markdown("##### 🧠 Hints")
            key_points = answer_guide.get("key_points", [])
            hint_text = key_points[0] if key_points else "Think about what data structure gives the best lookup time."
            edge_cases = answer_guide.get("edge_cases", [])
            edge_text = ", ".join(edge_cases[:2]) if edge_cases else "empty input, single element"
            st.markdown(
                f'<div style="background:#1e293b;border-left:3px solid #4F8EF7;border-radius:6px;'
                f'padding:0.8rem;font-size:0.8rem;color:#94a3b8;line-height:1.5;margin-bottom:0.5rem;">'
                f'<b style="color:#4F8EF7;">&#128161; Hint:</b><br>{hint_text}</div>'
                f'<div style="background:#1e293b;border-left:3px solid #F59E0B;border-radius:6px;'
                f'padding:0.8rem;font-size:0.8rem;color:#94a3b8;line-height:1.5;">'
                f'<b style="color:#F59E0B;">&#9888; Edge cases:</b><br>{edge_text}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown("##### 💡 Quick Tips")
            overview = answer_guide.get("overview", "Think through this carefully before answering.")
            st.markdown(
                f'<div style="background:#1e293b;border-left:3px solid #6366f1;border-radius:6px;'
                f'padding:0.8rem;font-size:0.8rem;color:#94a3b8;line-height:1.5;">{overview}</div>',
                unsafe_allow_html=True,
            )

    # Action buttons
    btn_col1, btn_col2, btn_col3 = st.columns([1, 1, 2])

    if not already_submitted:
        with btn_col1:
            submit_label = "✅ Submit Solution" if is_coding else "✅ Submit Answer"
            submit = st.button(submit_label, key=f"submit_{q_id}", type="primary", use_container_width=True)
        with btn_col2:
            skip = st.button("⏭ Skip", key=f"skip_{q_id}", use_container_width=True)

        if submit:
            ans = st.session_state.get(f"answer_input_{q_id}", "")
            st.session_state.user_answers[q_id] = ans
            st.session_state.answer_submitted[q_id] = True
            with st.spinner("🤖 Evaluating your answer..."):
                fb = evaluate_answer(
                    question=question_text,
                    candidate_answer=ans,
                    role=config["role"],
                    difficulty=config["difficulty"],
                    is_coding=is_coding,
                )
                st.session_state.answer_feedback[q_id] = fb
            st.rerun()

        if skip:
            st.session_state.user_answers[q_id] = ""
            st.session_state.answer_submitted[q_id] = True
            st.session_state.answer_feedback[q_id] = {
                "score": 0, "grade": "Not Attempted",
                "strengths": [], "improvements": ["Question was skipped."],
                "model_answer": answer_guide.get("ideal_answer", ""),
                "follow_up": "", "encouragement": "No worries — review the solution below!",
            }
            st.rerun()
    else:
        with btn_col2:
            toggle_label = "🙈 Hide Solution" if show_answer_flag else "👁️ Show Full Solution"
            if st.button(toggle_label, key=f"toggle_answer_{q_id}", use_container_width=True):
                st.session_state.show_answer[q_id] = not show_answer_flag
                st.rerun()

    # Feedback panel
    if already_submitted and feedback:
        _render_feedback(feedback, answer_guide, show_answer_flag, is_coding)


def _render_code_block(title: str, code: str, time_c: str = "", space_c: str = "",
                       accent: str = "#4F8EF7", explanation: str = "", key_insight: str = ""):
    """Render a titled code block with complexity badges."""
    time_badge = (
        f'<span style="background:#10B98122;color:#10B981;border-radius:6px;'
        f'padding:3px 10px;font-size:0.78rem;font-weight:600;">Time: {time_c}</span>'
    ) if time_c else ""
    space_badge = (
        f'<span style="background:#6366f122;color:#a5b4fc;border-radius:6px;'
        f'padding:3px 10px;font-size:0.78rem;font-weight:600;">Space: {space_c}</span>'
    ) if space_c else ""
    complexity_html = (
        f'<div style="display:flex;gap:8px;margin-bottom:0.75rem;flex-wrap:wrap;">'
        f'{time_badge}{space_badge}</div>'
    ) if (time_c or space_c) else ""

    insight_html = (
        f'<div style="background:#F59E0B18;border-left:3px solid #F59E0B;border-radius:6px;'
        f'padding:0.6rem 0.8rem;margin-bottom:0.75rem;color:#fbbf24;font-size:0.82rem;line-height:1.5;">'
        f'<b>&#128161; Key Insight:</b> {key_insight}</div>'
    ) if key_insight else ""

    explanation_html = (
        f'<div style="color:#94a3b8;font-size:0.83rem;line-height:1.6;margin-bottom:0.75rem;">'
        f'{explanation}</div>'
    ) if explanation else ""

    st.markdown(
        f'<div style="background:#0d1117;border:1px solid #30363d;border-left:4px solid {accent};'
        f'border-radius:10px;padding:1.2rem;margin-bottom:0.75rem;">'
        f'<p style="color:{accent};font-weight:700;margin:0 0 0.75rem 0;font-size:0.88rem;">{title}</p>'
        f'{insight_html}{explanation_html}{complexity_html}</div>',
        unsafe_allow_html=True,
    )
    st.code(code, language="python")


def _render_feedback(feedback: dict, answer_guide: dict, show_model: bool, is_coding: bool = False):
    score = feedback.get("score", 0)
    grade = feedback.get("grade", "")
    strengths = feedback.get("strengths", [])
    improvements = feedback.get("improvements", [])
    model_answer = feedback.get("model_answer", answer_guide.get("ideal_answer", ""))
    follow_up = feedback.get("follow_up", "")
    encouragement = feedback.get("encouragement", "")

    color = _score_color(score)
    emoji = _grade_emoji(grade)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("#### 🤖 AI Feedback")

    fb_col1, fb_col2 = st.columns([1, 3])
    with fb_col1:
        st.markdown(
            f'<div style="background:linear-gradient(135deg,{color}22,{color}11);'
            f'border:2px solid {color};border-radius:12px;padding:1.2rem;text-align:center;">'
            f'<div style="font-size:2.5rem;font-weight:800;color:{color};">{score}'
            f'<span style="font-size:1rem;color:#64748b;">/10</span></div>'
            f'<div style="color:#e2e8f0;font-size:0.9rem;margin-top:4px;">{emoji} {grade}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    with fb_col2:
        if encouragement:
            st.markdown(
                f'<div style="background:#1e293b;border-radius:8px;padding:0.75rem 1rem;'
                f'color:#a5b4fc;font-style:italic;margin-bottom:0.75rem;font-size:0.9rem;">'
                f'"{encouragement}"</div>',
                unsafe_allow_html=True,
            )
        if strengths:
            s_items = "".join([f"<li style='margin-bottom:4px;'>{s}</li>" for s in strengths])
            st.markdown(
                f'<p style="color:#10B981;font-weight:600;margin:0 0 4px 0;font-size:0.85rem;">&#10003; Strengths</p>'
                f'<ul style="color:#94a3b8;font-size:0.85rem;margin:0 0 0.5rem 0;padding-left:1.2rem;">{s_items}</ul>',
                unsafe_allow_html=True,
            )
        if improvements:
            i_items = "".join([f"<li style='margin-bottom:4px;'>{i}</li>" for i in improvements])
            st.markdown(
                f'<p style="color:#F59E0B;font-weight:600;margin:0 0 4px 0;font-size:0.85rem;">&#128161; Areas to Improve</p>'
                f'<ul style="color:#94a3b8;font-size:0.85rem;margin:0;padding-left:1.2rem;">{i_items}</ul>',
                unsafe_allow_html=True,
            )

    # Show full solution panel (toggle)
    if show_model:
        st.markdown("<br>", unsafe_allow_html=True)

        if is_coding:
            brute = answer_guide.get("brute_force", {})
            optimal = answer_guide.get("optimal_solution", {})
            dry_run = answer_guide.get("dry_run_example", "")
            edge_cases = answer_guide.get("edge_cases", [])

            st.markdown("#### 📖 Full Solution Breakdown")

            if brute:
                with st.expander("🐢 Brute Force Approach", expanded=True):
                    _render_code_block(
                        title="Brute Force — Naive Solution",
                        code=brute.get("code", "# Code not available"),
                        time_c=brute.get("time_complexity", ""),
                        space_c=brute.get("space_complexity", ""),
                        accent="#94a3b8",
                        explanation=brute.get("explanation", ""),
                    )

            if optimal:
                with st.expander("🚀 Optimal Approach", expanded=True):
                    _render_code_block(
                        title="Optimal Solution",
                        code=optimal.get("code", "# Code not available"),
                        time_c=optimal.get("time_complexity", ""),
                        space_c=optimal.get("space_complexity", ""),
                        accent="#10B981",
                        explanation=optimal.get("explanation", ""),
                        key_insight=optimal.get("key_insight", ""),
                    )

            if dry_run:
                with st.expander("🔍 Dry Run / Step-by-Step Trace", expanded=False):
                    st.markdown(
                        f'<div style="background:#0d1117;border:1px solid #30363d;'
                        f'border-left:4px solid #A855F7;border-radius:10px;padding:1.2rem;">'
                        f'<p style="color:#A855F7;font-weight:700;margin:0 0 0.75rem 0;font-size:0.88rem;">'
                        f'&#128269; Example Walkthrough</p>'
                        f'<div style="color:#c9d1d9;font-size:0.86rem;line-height:1.9;'
                        f'white-space:pre-wrap;font-family:monospace;">{dry_run}</div></div>',
                        unsafe_allow_html=True,
                    )

            if edge_cases:
                with st.expander("⚠️ Edge Cases to Handle", expanded=False):
                    ec_items = "".join([
                        f'<li style="margin-bottom:6px;color:#94a3b8;">{ec}</li>'
                        for ec in edge_cases
                    ])
                    st.markdown(
                        f'<ul style="font-size:0.87rem;padding-left:1.2rem;">{ec_items}</ul>',
                        unsafe_allow_html=True,
                    )

        else:
            if model_answer:
                st.markdown(
                    f'<div style="background:linear-gradient(135deg,#0f172a,#1a2744);'
                    f'border:1px solid #4F8EF766;border-left:4px solid #4F8EF7;'
                    f'border-radius:10px;padding:1.2rem;margin-top:0.75rem;">'
                    f'<p style="color:#4F8EF7;font-weight:700;margin:0 0 0.75rem 0;font-size:0.9rem;">'
                    f'&#128214; Model Answer</p>'
                    f'<p style="color:#cbd5e1;font-size:0.88rem;line-height:1.7;margin:0;'
                    f'white-space:pre-wrap;">{model_answer}</p></div>',
                    unsafe_allow_html=True,
                )

    # Key points always visible for non-coding
    if not is_coding:
        key_points = answer_guide.get("key_points", [])
        if key_points:
            kp_items = "".join([f"<li style='margin-bottom:3px;'>{p}</li>" for p in key_points])
            st.markdown(
                f'<div style="background:#1e293b;border-radius:8px;padding:0.9rem 1rem;margin-top:0.75rem;">'
                f'<p style="color:#6366f1;font-weight:600;margin:0 0 6px 0;font-size:0.85rem;">&#128273; Key Points to Cover</p>'
                f'<ul style="color:#94a3b8;font-size:0.85rem;margin:0;padding-left:1.2rem;">{kp_items}</ul></div>',
                unsafe_allow_html=True,
            )

    if follow_up:
        st.markdown(
            f'<div style="background:#1e293b;border-radius:8px;padding:0.75rem 1rem;margin-top:0.75rem;">'
            f'<p style="color:#F59E0B;font-weight:600;margin:0 0 4px 0;font-size:0.82rem;">&#128260; Likely Follow-up Question</p>'
            f'<p style="color:#e2e8f0;font-size:0.88rem;margin:0;font-style:italic;">"{follow_up}"</p></div>',
            unsafe_allow_html=True,
        )

    rubric = answer_guide.get("scoring_rubric", {})
    if rubric:
        with st.expander("📊 Scoring Rubric", expanded=False):
            for level, desc in rubric.items():
                lvl_color = {
                    "excellent": "#10B981",
                    "good": "#F59E0B",
                    "needs_improvement": "#EF4444",
                }.get(level, "#94a3b8")
                st.markdown(
                    f'<div style="margin-bottom:0.5rem;">'
                    f'<span style="color:{lvl_color};font-weight:700;font-size:0.85rem;text-transform:capitalize;">'
                    f'{level.replace("_", " ")}:</span>'
                    f'<span style="color:#94a3b8;font-size:0.85rem;"> {desc}</span></div>',
                    unsafe_allow_html=True,
                )


def _render_practice_mode():
    config = st.session_state.interview_config
    data = st.session_state.interview_questions
    questions = data.get("questions", [])
    session_info = data.get("interview_session", {})
    total = len(questions)

    if not questions:
        st.error("No questions were generated. Please go back and try again.")
        if st.button("← Start Over"):
            _reset_session()
            st.rerun()
        return

    q_index = st.session_state.current_q_index

    # Header bar
    col_title, col_meta, col_restart = st.columns([3, 2, 1])
    with col_title:
        type_info = INTERVIEW_TYPES.get(config["type"], {})
        st.markdown(
            f'<div style="padding:0.5rem 0;">'
            f'<h3 style="color:#e2e8f0;margin:0;font-size:1.25rem;">'
            f'{type_info.get("icon","🎤")} {config["role"]} Interview</h3>'
            f'<p style="color:#64748b;margin:0;font-size:0.82rem;">'
            f'{config["type"]} &#183; {config["difficulty"]} &#183; {total} Questions '
            f'&#183; ~{session_info.get("estimated_duration_mins", total * 5)} mins</p></div>',
            unsafe_allow_html=True,
        )
    with col_restart:
        if st.button("🔄 Restart", use_container_width=True):
            _reset_session()
            st.rerun()

    tips = session_info.get("tips", [])
    if tips:
        with st.expander("💡 Quick Interview Tips", expanded=False):
            for tip in tips:
                st.markdown(f"- {tip}")

    st.markdown("---")

    all_answered = all(
        st.session_state.answer_submitted.get(str(q.get("id", i + 1)), False)
        for i, q in enumerate(questions)
    )

    # Question navigator dots
    dot_html = '<div style="display:flex;gap:6px;margin-bottom:1rem;flex-wrap:wrap;">'
    for i, q in enumerate(questions):
        qid = str(q.get("id", i + 1))
        is_current = (i == q_index)
        is_done = st.session_state.answer_submitted.get(qid, False)
        if is_done:
            fb = st.session_state.answer_feedback.get(qid, {})
            bg = _score_color(fb.get("score", 0))
        elif is_current:
            bg = "#6366f1"
        else:
            bg = "#334155"
        border = "2px solid #818cf8" if is_current else "2px solid transparent"
        dot_html += (
            f'<div style="width:28px;height:28px;background:{bg};border:{border};'
            f'border-radius:6px;display:flex;align-items:center;justify-content:center;'
            f'color:#fff;font-size:0.75rem;font-weight:600;">{i + 1}</div>'
        )
    dot_html += "</div>"
    st.markdown(dot_html, unsafe_allow_html=True)

    if q_index < total:
        q = questions[q_index]
        _render_question_card(q, q_index, total, config)
        _render_answer_section(q, q_index, config)

        st.markdown("<br>", unsafe_allow_html=True)
        nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])

        q_id = str(q.get("id", q_index + 1))
        submitted_this = st.session_state.answer_submitted.get(q_id, False)

        with nav_col1:
            if q_index > 0:
                if st.button("← Previous", use_container_width=True):
                    st.session_state.current_q_index -= 1
                    st.rerun()
        with nav_col3:
            if q_index < total - 1:
                if st.button("Next →", disabled=not submitted_this, type="primary", use_container_width=True):
                    st.session_state.current_q_index += 1
                    st.rerun()
            elif submitted_this and all_answered:
                if st.button("📊 View Results", type="primary", use_container_width=True):
                    qa_pairs = [
                        {
                            "question": q2.get("question", ""),
                            "answer": st.session_state.user_answers.get(str(q2.get("id", i2 + 1)), ""),
                        }
                        for i2, q2 in enumerate(questions)
                    ]
                    with st.spinner("📊 Generating your performance report..."):
                        summary = generate_session_summary(
                            role=config["role"],
                            interview_type=config["type"],
                            difficulty=config["difficulty"],
                            qa_pairs=qa_pairs,
                        )
                        st.session_state.session_summary = summary
                        st.session_state.session_complete = True
                    st.rerun()

    with st.expander("🗂️ Jump to Question", expanded=False):
        for i, q in enumerate(questions):
            qid = str(q.get("id", i + 1))
            done = st.session_state.answer_submitted.get(qid, False)
            status = "✅" if done else "⬜"
            if st.button(
                f"{status} Q{i + 1}: {q.get('question', '')[:70]}...",
                key=f"jump_{i}",
                use_container_width=True,
            ):
                st.session_state.current_q_index = i
                st.rerun()


# ── Step 4: Session Summary ───────────────────────────────────────────────────

def _render_session_summary():
    summary = st.session_state.session_summary
    config = st.session_state.interview_config
    data = st.session_state.interview_questions
    questions = data.get("questions", [])

    if not summary:
        st.error("No summary data. Please complete the session first.")
        return

    overall_score = summary.get("overall_score", 0)
    overall_grade = summary.get("overall_grade", "")
    readiness = summary.get("readiness_verdict", "")
    readiness_color = {
        "Ready": "#10B981",
        "Almost Ready": "#F59E0B",
        "Needs More Prep": "#EF4444",
    }.get(readiness, "#6366f1")

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0f172a 0%,#1e1b4b 60%,#0f172a 100%);'
        f'border:1px solid #334155;border-radius:16px;padding:2.5rem;text-align:center;margin-bottom:2rem;">'
        f'<div style="font-size:0.9rem;color:#94a3b8;margin-bottom:0.5rem;'
        f'text-transform:uppercase;letter-spacing:2px;">Session Complete</div>'
        f'<div style="font-size:4rem;font-weight:900;color:{_score_color(overall_score)};line-height:1;">'
        f'{overall_score}<span style="font-size:1.5rem;color:#475569;">/10</span></div>'
        f'<div style="font-size:1.1rem;color:#e2e8f0;margin:0.5rem 0;">{_grade_emoji(overall_grade)} {overall_grade}</div>'
        f'<div style="display:inline-block;background:{readiness_color}22;border:1px solid {readiness_color};'
        f'color:{readiness_color};border-radius:99px;padding:4px 20px;font-size:0.9rem;font-weight:600;margin-top:0.75rem;">'
        f'{readiness}</div>'
        f'<p style="color:#94a3b8;margin-top:1rem;max-width:600px;margin-left:auto;margin-right:auto;'
        f'font-size:0.9rem;line-height:1.6;">{summary.get("summary", "")}</p>'
        f'<p style="color:#475569;font-size:0.82rem;margin-top:0.5rem;">'
        f'{summary.get("readiness_explanation", "")}</p></div>',
        unsafe_allow_html=True,
    )

    breakdown = summary.get("score_breakdown", {})
    if breakdown:
        st.markdown("#### 📊 Score Breakdown")
        bd_cols = st.columns(len(breakdown))
        for col, (metric, val) in zip(bd_cols, breakdown.items()):
            color = _score_color(val)
            with col:
                st.markdown(
                    f'<div style="background:#1e293b;border-top:3px solid {color};'
                    f'border-radius:10px;padding:1rem;text-align:center;">'
                    f'<div style="font-size:1.6rem;font-weight:800;color:{color};">{val}</div>'
                    f'<div style="color:#64748b;font-size:0.78rem;text-transform:capitalize;margin-top:4px;">'
                    f'{metric.replace("_", " ")}</div></div>',
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        strengths = summary.get("strengths", [])
        if strengths:
            st.markdown("#### ✅ Strengths")
            for s in strengths:
                st.markdown(
                    f'<div style="background:#1e293b;border-left:3px solid #10B981;border-radius:6px;'
                    f'padding:0.6rem 0.9rem;margin-bottom:6px;color:#94a3b8;font-size:0.88rem;">&#10003; {s}</div>',
                    unsafe_allow_html=True,
                )

        recommended = summary.get("recommended_topics", [])
        if recommended:
            st.markdown("#### 📚 Topics to Study")
            for t in recommended:
                st.markdown(
                    f'<div style="background:#1e293b;border-left:3px solid #6366f1;border-radius:6px;'
                    f'padding:0.6rem 0.9rem;margin-bottom:6px;color:#94a3b8;font-size:0.88rem;">&#128214; {t}</div>',
                    unsafe_allow_html=True,
                )

    with col_right:
        areas = summary.get("areas_for_improvement", [])
        if areas:
            st.markdown("#### 💡 Areas to Improve")
            for a in areas:
                st.markdown(
                    f'<div style="background:#1e293b;border-left:3px solid #F59E0B;border-radius:6px;'
                    f'padding:0.6rem 0.9rem;margin-bottom:6px;color:#94a3b8;font-size:0.88rem;">&#128161; {a}</div>',
                    unsafe_allow_html=True,
                )

        next_steps = summary.get("next_steps", [])
        if next_steps:
            st.markdown("#### 🚀 Next Steps")
            for i, step in enumerate(next_steps, 1):
                st.markdown(
                    f'<div style="background:#1e293b;border-left:3px solid #4F8EF7;border-radius:6px;'
                    f'padding:0.6rem 0.9rem;margin-bottom:6px;color:#94a3b8;font-size:0.88rem;">{i}. {step}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("---")
    st.markdown("#### 📋 Question-by-Question Recap")
    for i, q in enumerate(questions):
        qid = str(q.get("id", i + 1))
        fb = st.session_state.answer_feedback.get(qid, {})
        user_ans = st.session_state.user_answers.get(qid, "")
        score = fb.get("score", 0)
        grade = fb.get("grade", "Not Attempted")

        with st.expander(
            f"Q{i + 1}: {q.get('question', '')[:80]}...  —  {_grade_emoji(grade)} {score}/10",
            expanded=False,
        ):
            if user_ans:
                st.markdown(f"**Your Answer:**\n\n{user_ans}")
            else:
                st.markdown("*Question was skipped.*")
            st.markdown("---")
            model = fb.get("model_answer", q.get("answer_guide", {}).get("ideal_answer", ""))
            if model:
                st.markdown(f"**Model Answer:**\n\n{model}")

    tips = summary.get("interview_tips", [])
    if tips:
        st.markdown("---")
        st.markdown("#### 🎯 Final Interview Tips")
        tips_cols = st.columns(min(3, len(tips)))
        for col, tip in zip(tips_cols, tips):
            with col:
                st.markdown(
                    f'<div style="background:#1e293b;border-radius:10px;padding:1rem;'
                    f'font-size:0.85rem;color:#94a3b8;line-height:1.5;height:100%;">&#127919; {tip}</div>',
                    unsafe_allow_html=True,
                )

    st.markdown("<br>", unsafe_allow_html=True)
    restart_col, _ = st.columns([1, 3])
    with restart_col:
        if st.button("🔄 Start New Interview", type="primary", use_container_width=True):
            _reset_session()
            st.rerun()


# ── Main entry point ──────────────────────────────────────────────────────────

def render_interview_prep():
    _init_session_state()

    st.markdown("""
    <style>
    .stTextArea textarea {
        background: #0f172a !important;
        color: #e2e8f0 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
        font-size: 0.9rem !important;
    }
    .stTextArea textarea:focus {
        border-color: #6366f1 !important;
        box-shadow: 0 0 0 2px #6366f133 !important;
    }
    div[data-testid="stRadio"] label {
        color: #cbd5e1 !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if st.session_state.session_complete and st.session_state.session_summary:
        _render_session_summary()
    elif st.session_state.interview_questions:
        _render_practice_mode()
    else:
        _render_setup()