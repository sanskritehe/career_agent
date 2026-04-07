"""
coordinator_ui.py
-----------------
Streamlit UI for:
  1. Coordinator Agent — Placement Readiness Report
  2. Live Jobs Panel — real postings via Adzuna API

HOW TO PLUG INTO app.py
------------------------
1. Add this import at the top of app.py:
       from agents.coordinator_ui import render_coordinator_report, render_live_jobs_panel

2. Add "🎯 Readiness Report" to the sidebar radio:
       page = st.radio("Select Module:", [
           "Resume & Job Match",
           "🎯 DSA Tutor",
           "🎤 Interview Prep",
           "🎯 Readiness Report",   ← add this
           "👤 My Profile",
       ])

3. Add the routing at the bottom of app.py:
       elif page == "🎯 Readiness Report":
           render_coordinator_report()

Place this file at:  agents/coordinator_ui.py
"""

import json
import streamlit as st

from agents.coordinator_agent import generate_readiness_report
from utils.live_jobs_api import fetch_live_jobs, extract_trending_skills_from_jobs, get_salary_insights
from agents.dsa.progress_tracker import progress_tracker   # adjust path if needed


# ── Color helpers (match your existing app style) ─────────────────────────────

def _score_color(score: float, out_of: float = 100) -> str:
    pct = score / out_of * 100
    if pct >= 70: return "#10B981"
    if pct >= 45: return "#F59E0B"
    return "#EF4444"


def _label_color(label: str) -> str:
    return {
        "Ready":        "#10B981",
        "Almost Ready": "#F59E0B",
        "Developing":   "#6366f1",
        "Not Ready":    "#EF4444",
    }.get(label, "#94a3b8")


def _pill(text: str, color: str = "#334155") -> str:
    return (
        f'<span style="background:{color};color:#e2e8f0;border-radius:99px;'
        f'padding:3px 12px;font-size:0.78rem;margin:2px;display:inline-block;">'
        f'{text}</span>'
    )


# ── Coordinator Report ────────────────────────────────────────────────────────

def render_coordinator_report():
    st.title("🎯 Placement Readiness Report")
    st.markdown(
        '<p style="color:#64748b;">Powered by the Coordinator Agent — '
        'synthesises all four agents into a single placement verdict.</p>',
        unsafe_allow_html=True,
    )

    # ── Check prerequisites ───────────────────────────────────────────────────
    missing = []
    if not st.session_state.get("resume_analysis_data"):
        missing.append("Resume Analysis")
    if not st.session_state.get("session_summary"):
        missing.append("Interview Session")
    if not st.session_state.get("job_match_result"):
        missing.append("Job Match")

    if missing:
        st.warning(
            f"⚠️  Please complete these steps first: **{', '.join(missing)}**\n\n"
            "Run the Resume & Job Match and at least one Interview session, "
            "then come back here."
        )
        st.info(
            "💡 **Quick guide:**\n"
            "1. Go to **Resume & Job Match** → upload resume + enter role → Run Analysis\n"
            "2. Go to **Interview Prep** → complete a mock interview session\n"
            "3. Return here for your unified Readiness Report"
        )
        return

    # ── Collect agent outputs from session state ──────────────────────────────
    resume_data   = st.session_state.resume_analysis_data
    interview_data = st.session_state.session_summary
    job_match_data = st.session_state.job_match_result
    target_role    = st.session_state.get("target_role_used", "Software Engineer")

    dsa_data = progress_tracker.get_all_progress()

    # ── Generate or retrieve cached report ────────────────────────────────────
    if st.button("🔄 Generate / Refresh Report", type="primary", use_container_width=True):
        st.session_state.coordinator_report = None

    if not st.session_state.get("coordinator_report"):
        with st.spinner("Coordinator Agent is synthesising all agent outputs…"):
            report = generate_readiness_report(
                resume_data=resume_data,
                dsa_data=dsa_data,
                interview_data=interview_data,
                job_match_data=job_match_data,
                target_role=target_role,
            )
            st.session_state.coordinator_report = report

    report = st.session_state.coordinator_report

    # ── 1. Hero score card ────────────────────────────────────────────────────
    score  = report["overall_readiness_score"]
    label  = report["readiness_label"]
    s_col  = _label_color(label)

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid #334155;'
        f'border-radius:16px;padding:2rem;text-align:center;margin-bottom:1.5rem;">'
        f'<div style="font-size:3.5rem;font-weight:800;color:{s_col};">{score}</div>'
        f'<div style="font-size:0.85rem;color:#94a3b8;margin-top:4px;">/ 100 overall readiness</div>'
        f'<div style="display:inline-block;background:{s_col}22;border:1px solid {s_col};'
        f'color:{s_col};border-radius:99px;padding:4px 20px;margin-top:0.75rem;font-weight:600;">'
        f'{label}</div>'
        f'<p style="color:#94a3b8;font-size:0.85rem;margin-top:1rem;font-style:italic;">'
        f'{report.get("encouragement","")}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # ── 2. Dimension scores ───────────────────────────────────────────────────
    dims = report.get("dimension_scores", {})
    d_col1, d_col2, d_col3, d_col4 = st.columns(4)
    for col, key, label_text in [
        (d_col1, "resume_strength",     "Resume"),
        (d_col2, "interview_readiness", "Interview"),
        (d_col3, "job_match",           "Job Match"),
        (d_col4, "dsa_completion",      "DSA"),
    ]:
        val = dims.get(key, 0)
        c   = _score_color(val)
        with col:
            st.markdown(
                f'<div style="background:#1e293b;border-top:3px solid {c};border-radius:10px;'
                f'padding:1rem;text-align:center;">'
                f'<div style="font-size:1.5rem;font-weight:800;color:{c};">{val:.0f}</div>'
                f'<div style="color:#64748b;font-size:0.75rem;margin-top:4px;">{label_text}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 3. Contradictions panel ───────────────────────────────────────────────
    contradictions = report.get("contradictions_detected", [])
    if contradictions:
        with st.expander(
            f"⚡ {len(contradictions)} contradiction(s) detected between agents", expanded=True
        ):
            for c in contradictions:
                st.markdown(f"- {c}")
            st.markdown("**🤖 Coordinator resolution:**")
            st.info(report.get("resolution", ""))
    else:
        st.success("✅ All agents are aligned — no contradictions detected.")
        st.caption(report.get("resolution", ""))

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 4. Assessment + Strengths + Gaps ─────────────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("#### 💬 Unified Assessment")
        st.markdown(
            f'<div style="background:#1e293b;border-radius:10px;padding:1.1rem;'
            f'color:#94a3b8;font-size:0.88rem;line-height:1.7;">'
            f'{report.get("unified_assessment","")}</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ✅ Strengths")
        for s in report.get("strengths", []):
            st.markdown(f"- {s}")

    with col_b:
        st.markdown("#### ❌ Critical Gaps")
        for g in report.get("critical_gaps", []):
            st.markdown(f"- {g}")
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ⚡ Priority Actions")
        for i, a in enumerate(report.get("priority_actions", []), 1):
            st.markdown(f"**{i}.** {a}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── 5. Personalised roadmap ───────────────────────────────────────────────
    st.markdown("#### 🗓️ Personalised Roadmap")
    roadmap = report.get("personalized_roadmap", [])
    weeks   = report.get("estimated_weeks_to_ready", 8)

    st.caption(f"Estimated time to placement-ready: **{weeks} weeks**")

    r_cols = st.columns(len(roadmap)) if 1 < len(roadmap) <= 4 else st.columns(1)
    for i, (col, step) in enumerate(zip(r_cols * len(roadmap), roadmap)):
        with col:
            st.markdown(
                f'<div style="background:#1e293b;border-left:3px solid #6366f1;'
                f'border-radius:8px;padding:0.9rem;margin-bottom:0.5rem;">'
                f'<div style="color:#6366f1;font-size:0.75rem;font-weight:600;">Phase {i+1}</div>'
                f'<div style="color:#e2e8f0;font-size:0.85rem;margin-top:4px;">{step}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # ── 6. Live jobs panel embedded at bottom of report ──────────────────────
    st.markdown("---")
    render_live_jobs_panel(target_role=target_role)


# ── Live Jobs Panel ───────────────────────────────────────────────────────────

def render_live_jobs_panel(target_role: str = ""):
    st.markdown("#### 🌐 Live Job Market")

    col_role, col_loc, col_btn = st.columns([2, 1.5, 1])

    with col_role:
        role_input = st.text_input(
            "Role",
            value=target_role,
            placeholder="e.g. Data Analyst",
            key="live_job_role",
            label_visibility="collapsed",
        )
    with col_loc:
        location = st.text_input(
            "Location",
            value="India",
            placeholder="India / Bengaluru",
            key="live_job_location",
            label_visibility="collapsed",
        )
    with col_btn:
        fetch_clicked = st.button("🔍 Fetch Jobs", use_container_width=True)

    if not fetch_clicked and not st.session_state.get("live_jobs_result"):
        st.caption("Enter a role and click **Fetch Jobs** to see live openings.")
        return

    if fetch_clicked:
        with st.spinner(f"Fetching live jobs for **{role_input}** in **{location}**…"):
            result = fetch_live_jobs(role=role_input, location=location, results_per_page=6)
            st.session_state.live_jobs_result = result

    result = st.session_state.get("live_jobs_result", {})
    jobs   = result.get("jobs", [])
    source = result.get("source", "unknown")
    cached = result.get("cached", False)

    if not jobs:
        st.warning("No jobs found. Try a broader role or different location.")
        return

    # Source badge
    badge_color = "#10B981" if source == "adzuna" else "#F59E0B"
    badge_text  = "🟢 Live data (Adzuna)" if source == "adzuna" else "🟡 Sample data (add Adzuna keys for live)"
    if cached:
        badge_text += " · cached"

    st.markdown(
        f'<span style="background:{badge_color}22;color:{badge_color};border:1px solid {badge_color};'
        f'border-radius:99px;padding:2px 12px;font-size:0.78rem;">{badge_text}</span>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Trending skills from JDs ──────────────────────────────────────────────
    trending = extract_trending_skills_from_jobs(jobs)
    if trending:
        pills = "".join(_pill(s, "#1e293b") for s in trending[:10])
        st.markdown("**📈 Skills trending in these postings:**")
        st.markdown(
            f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:1rem;">{pills}</div>',
            unsafe_allow_html=True,
        )

    # ── Salary insights ───────────────────────────────────────────────────────
    salary = get_salary_insights(jobs)
    if salary.get("available"):
        curr = salary["currency"]
        s1, s2, s3 = st.columns(3)
        for col, lbl, val in [
            (s1, "Min Salary", f"{curr} {salary['min']:,.0f}"),
            (s2, "Avg Salary", f"{curr} {salary['avg']:,.0f}"),
            (s3, "Max Salary", f"{curr} {salary['max']:,.0f}"),
        ]:
            with col:
                st.markdown(
                    f'<div style="background:#1e293b;border-radius:8px;padding:0.75rem;text-align:center;">'
                    f'<div style="color:#6366f1;font-weight:700;font-size:1rem;">{val}</div>'
                    f'<div style="color:#64748b;font-size:0.75rem;">{lbl}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)

    # ── Job cards ─────────────────────────────────────────────────────────────
    for job in jobs:
        sal_parts = []
        if job.get("salary_min"):
            sal_parts.append(f"₹{job['salary_min']:,.0f}")
        if job.get("salary_max"):
            sal_parts.append(f"₹{job['salary_max']:,.0f}")
        sal_str = " – ".join(sal_parts) if sal_parts else "Salary not listed"

        url_html = (
            f'<a href="{job["url"]}" target="_blank" style="color:#6366f1;font-size:0.8rem;">'
            f'View posting →</a>'
            if job.get("url") else ""
        )

        with st.expander(f"🏢 {job['company']}  ·  {job['title']}", expanded=False):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(
                    f'<p style="color:#94a3b8;font-size:0.85rem;margin:0;">'
                    f'📍 {job["location"]}</p>'
                    f'<p style="color:#10B981;font-size:0.85rem;margin:4px 0;">'
                    f'💰 {sal_str}</p>',
                    unsafe_allow_html=True,
                )
            with c2:
                st.markdown(url_html, unsafe_allow_html=True)

            if job.get("description"):
                st.markdown(
                    f'<p style="color:#64748b;font-size:0.83rem;line-height:1.6;margin-top:0.5rem;">'
                    f'{job["description"]}…</p>',
                    unsafe_allow_html=True,
                )
