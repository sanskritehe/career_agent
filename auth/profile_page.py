"""
auth/profile_page.py
--------------------
User profile, settings, interview history and resume history page.
"""

import json
import streamlit as st
from utils.database import (
    update_user_profile,
    get_interview_history,
    get_resume_history,
    get_user_stats,
)


def _score_color(score: float) -> str:
    if score >= 8: return "#10B981"
    if score >= 6: return "#F59E0B"
    return "#EF4444"


def _readiness_color(verdict: str) -> str:
    return {"Ready": "#10B981", "Almost Ready": "#F59E0B"}.get(verdict, "#EF4444")


def render_profile_page():
    user = st.session_state.get("user", {})
    user_id = st.session_state.get("user_id")

    if not user or not user_id:
        st.error("Not logged in.")
        return

    # ── Header ──────────────────────────────────────────────────────────────────
    display_name = user.get("full_name") or user.get("username", "User")
    joined = user.get("created_at", "")
    joined_str = joined.strftime("%B %Y") if hasattr(joined, "strftime") else str(joined)[:7]

    st.markdown(
        f'<div style="background:linear-gradient(135deg,#0f172a,#1e1b4b);border:1px solid #334155;'
        f'border-radius:16px;padding:2rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1.5rem;">'
        f'<div style="width:64px;height:64px;background:linear-gradient(135deg,#6366f1,#8b5cf6);'
        f'border-radius:50%;display:flex;align-items:center;justify-content:center;'
        f'font-size:1.8rem;font-weight:800;color:#fff;flex-shrink:0;">'
        f'{display_name[0].upper()}</div>'
        f'<div>'
        f'<h2 style="color:#e2e8f0;margin:0;font-size:1.4rem;">{display_name}</h2>'
        f'<p style="color:#64748b;margin:0;font-size:0.85rem;">@{user.get("username","")} &nbsp;&#183;&nbsp; Joined {joined_str}</p>'
        f'<p style="color:#94a3b8;margin:0.25rem 0 0 0;font-size:0.85rem;">{user.get("email","")}</p>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # ── Stats ────────────────────────────────────────────────────────────────────
    try:
        stats = get_user_stats(user_id)
        s_col1, s_col2, s_col3, s_col4 = st.columns(4)
        for col, label, val, color in [
            (s_col1, "Interview Sessions", stats["interview_sessions"], "#6366f1"),
            (s_col2, "Avg Interview Score", f"{stats['interview_avg_score']}/10", _score_color(stats["interview_avg_score"])),
            (s_col3, "Best Score", f"{stats['interview_best_score']}/10", "#10B981"),
            (s_col4, "Resume Analyses", stats["resume_analyses"], "#F59E0B"),
        ]:
            with col:
                st.markdown(
                    f'<div style="background:#1e293b;border-top:3px solid {color};border-radius:10px;padding:1rem;text-align:center;">'
                    f'<div style="font-size:1.5rem;font-weight:800;color:{color};">{val}</div>'
                    f'<div style="color:#64748b;font-size:0.78rem;margin-top:4px;">{label}</div></div>',
                    unsafe_allow_html=True,
                )
        st.markdown("<br>", unsafe_allow_html=True)
    except Exception:
        pass

    # ── Tabs ─────────────────────────────────────────────────────────────────────
    tab_history, tab_resume_hist, tab_settings = st.tabs([
        "🎤 Interview History",
        "📄 Resume History",
        "⚙️ Edit Profile",
    ])

    # ── INTERVIEW HISTORY ────────────────────────────────────────────────────────
    with tab_history:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            sessions = get_interview_history(user_id, limit=15)
        except Exception as e:
            st.error(f"Could not load history: {e}")
            sessions = []

        if not sessions:
            st.markdown(
                '<div style="text-align:center;color:#475569;padding:3rem;">'
                '&#127908; No interview sessions yet.<br>'
                '<span style="font-size:0.85rem;">Complete a mock interview to see your history here.</span>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            for s in sessions:
                score = float(s.get("overall_score") or 0)
                verdict = s.get("readiness_verdict", "")
                created = s.get("created_at", "")
                created_str = created.strftime("%d %b %Y, %I:%M %p") if hasattr(created, "strftime") else str(created)[:16]

                sc = _score_color(score)
                vc = _readiness_color(verdict)

                with st.expander(
                    f"{'🟢' if score >= 8 else '🟡' if score >= 6 else '🔴'} "
                    f"{s.get('role','Unknown Role')} — {s.get('interview_type','')} — "
                    f"{score}/10 — {created_str}",
                    expanded=False,
                ):
                    c1, c2, c3, c4 = st.columns(4)
                    for col, lbl, v, cl in [
                        (c1, "Score", f"{score}/10", sc),
                        (c2, "Grade", s.get("overall_grade",""), sc),
                        (c3, "Readiness", verdict, vc),
                        (c4, "Questions", s.get("num_questions", 0), "#6366f1"),
                    ]:
                        with col:
                            st.markdown(
                                f'<div style="background:#1e293b;border-radius:8px;padding:0.75rem;text-align:center;">'
                                f'<div style="color:{cl};font-weight:700;font-size:1.1rem;">{v}</div>'
                                f'<div style="color:#64748b;font-size:0.75rem;">{lbl}</div></div>',
                                unsafe_allow_html=True,
                            )

                    st.markdown(
                        f'<div style="margin-top:0.75rem;color:#64748b;font-size:0.8rem;">'
                        f'&#128197; {created_str} &nbsp;&#183;&nbsp; Difficulty: {s.get("difficulty","")}</div>',
                        unsafe_allow_html=True,
                    )

    # ── RESUME HISTORY ───────────────────────────────────────────────────────────
    with tab_resume_hist:
        st.markdown("<br>", unsafe_allow_html=True)
        try:
            analyses = get_resume_history(user_id, limit=10)
        except Exception as e:
            st.error(f"Could not load history: {e}")
            analyses = []

        if not analyses:
            st.markdown(
                '<div style="text-align:center;color:#475569;padding:3rem;">'
                '&#128196; No resume analyses yet.<br>'
                '<span style="font-size:0.85rem;">Run a Resume + Job Match to see results here.</span>'
                '</div>',
                unsafe_allow_html=True,
            )
        else:
            for a in analyses:
                created = a.get("created_at", "")
                created_str = created.strftime("%d %b %Y") if hasattr(created, "strftime") else str(created)[:10]
                score = float(a.get("match_score") or 0)
                sc = _score_color(score / 10)

                with st.expander(
                    f"&#128196; {a.get('target_role','Unknown Role')} — Match: {score:.0f}% — {created_str}",
                    expanded=False,
                ):
                    r1, r2 = st.columns(2)
                    with r1:
                        st.markdown(
                            f'<div style="background:#1e293b;border-radius:8px;padding:0.9rem;margin-bottom:0.5rem;">'
                            f'<p style="color:#6366f1;font-weight:600;font-size:0.82rem;margin:0 0 4px 0;">Target Role</p>'
                            f'<p style="color:#e2e8f0;margin:0;">{a.get("target_role","")}</p></div>',
                            unsafe_allow_html=True,
                        )
                        st.markdown(
                            f'<div style="background:#1e293b;border-radius:8px;padding:0.9rem;">'
                            f'<p style="color:#6366f1;font-weight:600;font-size:0.82rem;margin:0 0 4px 0;">Experience Level</p>'
                            f'<p style="color:#e2e8f0;margin:0;">{a.get("experience_level","")}</p></div>',
                            unsafe_allow_html=True,
                        )
                    with r2:
                        match_color = _score_color(score / 10)
                        st.markdown(
                            f'<div style="background:#1e293b;border-top:3px solid {match_color};'
                            f'border-radius:8px;padding:0.9rem;text-align:center;margin-bottom:0.5rem;">'
                            f'<div style="font-size:1.8rem;font-weight:800;color:{match_color};">{score:.0f}%</div>'
                            f'<div style="color:#64748b;font-size:0.75rem;">Job Match Score</div></div>',
                            unsafe_allow_html=True,
                        )

                    skills = a.get("skills_present", "")
                    if skills:
                        skill_pills = "".join([
                            f'<span style="background:#1e293b;color:#94a3b8;border:1px solid #334155;'
                            f'border-radius:99px;padding:2px 10px;font-size:0.75rem;margin:2px;">{s.strip()}</span>'
                            for s in skills.split(",") if s.strip()
                        ])
                        st.markdown(
                            f'<p style="color:#6366f1;font-weight:600;font-size:0.82rem;margin:0.75rem 0 4px 0;">Skills Detected</p>'
                            f'<div style="display:flex;flex-wrap:wrap;gap:4px;">{skill_pills}</div>',
                            unsafe_allow_html=True,
                        )

                    summary = a.get("summary", "")
                    if summary:
                        st.markdown(
                            f'<p style="color:#6366f1;font-weight:600;font-size:0.82rem;margin:0.75rem 0 4px 0;">Summary</p>'
                            f'<p style="color:#94a3b8;font-size:0.85rem;line-height:1.6;">{summary}</p>',
                            unsafe_allow_html=True,
                        )

    # ── EDIT PROFILE ─────────────────────────────────────────────────────────────
    with tab_settings:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### ✏️ Update Your Profile")

        with st.form("profile_form"):
            new_name = st.text_input(
                "Full Name",
                value=user.get("full_name", ""),
                key="profile_name",
            )
            new_role = st.text_input(
                "Target Role",
                value=user.get("target_role", ""),
                placeholder="e.g. Backend Engineer, Data Scientist",
                key="profile_role",
            )
            new_exp = st.selectbox(
                "Experience Level",
                ["Beginner", "Intermediate", "Advanced"],
                index=["Beginner", "Intermediate", "Advanced"].index(
                    user.get("experience_level", "Beginner")
                ),
                key="profile_exp",
            )
            st.markdown("<br>", unsafe_allow_html=True)
            save = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)

        if save:
            try:
                update_user_profile(
                    user_id=user_id,
                    full_name=new_name,
                    target_role=new_role,
                    experience_level=new_exp,
                )
                # Update session state so sidebar reflects change immediately
                st.session_state.user["full_name"] = new_name
                st.session_state.user["target_role"] = new_role
                st.session_state.user["experience_level"] = new_exp
                st.success("✅ Profile updated successfully!")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to update profile: {e}")