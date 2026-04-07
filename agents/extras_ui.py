"""
extras_ui.py
------------
Streamlit UI for three bonus features:
  Tab 1 — AI Resume Builder
  Tab 2 — Learning Roadmap
  Tab 3 — Answer Coach

HOW TO PLUG INTO app.py
------------------------
1. Add import:
       from agents.extras_ui import render_extras_page

2. Add to sidebar radio:
       "🚀 AI Tools"   ← add this option

3. Add sidebar info block:
       elif page == "🚀 AI Tools":
           st.info("Resume Builder · Learning Roadmap · Answer Coach")

4. Add page routing:
       elif page == "🚀 AI Tools":
           render_extras_page()

Place at: agents/extras_ui.py
"""

import streamlit as st
from agents.resume_builder import build_improved_resume, render_resume_as_text
from agents.learning_recommender import recommend_resources
from agents.answer_coach import coach_answer, QUESTION_TYPES


# ── Helpers ───────────────────────────────────────────────────────────────────

def _score_bar(score: int, out_of: int = 10):
    pct = int(score / out_of * 100)
    color = "#10B981" if pct >= 70 else "#F59E0B" if pct >= 45 else "#EF4444"
    st.markdown(
        f'<div style="background:#1e293b;border-radius:99px;height:8px;margin:4px 0 10px 0;">'
        f'<div style="background:{color};width:{pct}%;height:8px;border-radius:99px;"></div></div>',
        unsafe_allow_html=True,
    )


def _pill(text: str, color: str = "#1e293b", text_color: str = "#94a3b8"):
    return (
        f'<span style="background:{color};color:{text_color};border-radius:99px;'
        f'padding:3px 12px;font-size:0.78rem;margin:2px;display:inline-block;">{text}</span>'
    )


def _priority_color(p: str) -> str:
    return {"High": "#EF4444", "Medium": "#F59E0B", "Low": "#10B981"}.get(p, "#64748b")


# ── Main render ───────────────────────────────────────────────────────────────

def render_extras_page():
    st.title("🚀 AI Career Tools")
    st.markdown(
        '<p style="color:#64748b;">Three tools to go beyond analysis — build, learn, and perfect.</p>',
        unsafe_allow_html=True,
    )

    tab1, tab2, tab3 = st.tabs([
        "📄 AI Resume Builder",
        "📚 Learning Roadmap",
        "🎯 Answer Coach",
    ])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — AI Resume Builder
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        st.markdown("#### 📄 AI Resume Builder")
        st.markdown(
            '<p style="color:#64748b;font-size:0.88rem;">Rewrites your resume to be '
            'ATS-optimised for your target role — using your gap analysis as input.</p>',
            unsafe_allow_html=True,
        )

        # Check for prerequisites
        if not st.session_state.get("resume_analysis_data"):
            st.warning(
                "⚠️ Run a **Resume & Job Match** analysis first — "
                "the builder needs your skill gap data."
            )
            return

        resume_analysis = st.session_state.resume_analysis_data
        target_role     = st.session_state.get("target_role_used", "")

        col_info1, col_info2, col_info3 = st.columns(3)
        col_info1.metric("Experience Level", resume_analysis.get("experience_level", "—"))
        col_info2.metric("Skills Present", len(resume_analysis.get("skills_present", [])))
        col_info3.metric("Skill Gaps", len(resume_analysis.get("skills_missing", [])))

        st.markdown("<br>", unsafe_allow_html=True)

        # Original resume text input
        original_text = st.text_area(
            "Paste your original resume text here",
            height=200,
            placeholder="Paste the full text of your resume here...",
            key="builder_resume_text",
        )

        role_override = st.text_input(
            "Target Role",
            value=target_role,
            key="builder_role",
        )

        if st.button("✨ Build Improved Resume", type="primary", use_container_width=True):
            if not original_text.strip():
                st.warning("Please paste your resume text above.")
            else:
                with st.spinner("AI is rewriting your resume..."):
                    result = build_improved_resume(
                        original_resume_text=original_text,
                        resume_analysis=resume_analysis,
                        target_role=role_override or target_role,
                    )
                    st.session_state.built_resume = result

        # Display result
        result = st.session_state.get("built_resume")
        if not result:
            st.info("💡 The builder rewrites your bullet points, adds ATS keywords from real JDs, "
                    "recommends certifications for your skill gaps, and suggests projects to add.")
            return

        if result.get("error"):
            st.error(result["error"])
            return

        st.success("✅ Resume rebuilt successfully!")
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Summary ──────────────────────────────────────────────────────────
        st.markdown("#### 📝 Rewritten Professional Summary")
        st.markdown(
            f'<div style="background:#1e293b;border-left:3px solid #6366f1;'
            f'border-radius:8px;padding:1rem;color:#e2e8f0;line-height:1.7;">'
            f'{result.get("summary", "")}</div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        col_l, col_r = st.columns(2)

        # ── Skills ────────────────────────────────────────────────────────────
        with col_l:
            st.markdown("#### 🛠️ Skills")
            skills = result.get("skills", {})
            current = skills.get("current", [])
            to_learn = skills.get("to_learn", [])
            if current:
                pills = "".join(_pill(s, "#0f172a", "#10B981") for s in current)
                st.markdown(
                    f'<p style="color:#10B981;font-size:0.8rem;font-weight:600;">Currently have</p>'
                    f'<div style="display:flex;flex-wrap:wrap;gap:4px;">{pills}</div>',
                    unsafe_allow_html=True,
                )
            if to_learn:
                st.markdown("<br>", unsafe_allow_html=True)
                pills2 = "".join(_pill(s, "#1e293b", "#F59E0B") for s in to_learn)
                st.markdown(
                    f'<p style="color:#F59E0B;font-size:0.8rem;font-weight:600;">To acquire [*]</p>'
                    f'<div style="display:flex;flex-wrap:wrap;gap:4px;">{pills2}</div>',
                    unsafe_allow_html=True,
                )

        # ── ATS Keywords ──────────────────────────────────────────────────────
        with col_r:
            st.markdown("#### 🔍 ATS Keywords")
            st.caption("These must appear in your resume to pass ATS filters")
            kws = result.get("ats_keywords", [])
            if kws:
                pills3 = "".join(_pill(k, "#0f172a", "#6366f1") for k in kws)
                st.markdown(
                    f'<div style="display:flex;flex-wrap:wrap;gap:4px;">{pills3}</div>',
                    unsafe_allow_html=True,
                )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Experience ────────────────────────────────────────────────────────
        experience = result.get("experience", [])
        if experience:
            st.markdown("#### 💼 Rewritten Experience")
            for exp in experience:
                with st.expander(
                    f"🏢 {exp.get('role', '')} — {exp.get('company', '')}  ({exp.get('duration', '')})"
                ):
                    for bullet in exp.get("bullets", []):
                        st.markdown(f"- {bullet}")

        # ── Projects ──────────────────────────────────────────────────────────
        projects = result.get("projects", [])
        if projects:
            st.markdown("#### 🔧 Projects")
            for proj in projects:
                tag = "💡 Suggested" if proj.get("is_suggested") else "✅ Existing"
                with st.expander(f"{tag} — {proj.get('name', '')}"):
                    st.write(proj.get("description", ""))
                    stack = proj.get("tech_stack", [])
                    if stack:
                        st.caption("Tech: " + " · ".join(stack))

        # ── Certifications ────────────────────────────────────────────────────
        certs = result.get("certifications", [])
        if certs:
            st.markdown("#### 🏅 Recommended Certifications")
            for cert in certs:
                c1, c2, c3 = st.columns([2, 1.5, 1.5])
                c1.markdown(f"**{cert.get('name', '')}**")
                c2.caption(cert.get("provider", ""))
                c3.caption(f"Covers: {cert.get('addresses_skill', '')}")
                if cert.get("url"):
                    st.markdown(f"[🔗 Link]({cert['url']})")

        # ── Improvement Notes ─────────────────────────────────────────────────
        notes = result.get("improvement_notes", [])
        if notes:
            with st.expander("📋 What the AI changed and why"):
                for note in notes:
                    st.markdown(f"- {note}")

        # ── Plain text export ─────────────────────────────────────────────────
        st.markdown("<br>", unsafe_allow_html=True)
        plain_text = render_resume_as_text(result)
        st.download_button(
            label="⬇️ Download as Plain Text",
            data=plain_text,
            file_name="improved_resume.txt",
            mime="text/plain",
            use_container_width=True,
        )

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — Learning Roadmap
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        st.markdown("#### 📚 Personalised Learning Roadmap")
        st.markdown(
            '<p style="color:#64748b;font-size:0.88rem;">Maps every skill gap to '
            'free resources, courses, and a prioritised learning order.</p>',
            unsafe_allow_html=True,
        )

        if not st.session_state.get("resume_analysis_data"):
            st.warning("⚠️ Run a **Resume & Job Match** analysis first.")
            return

        resume_analysis = st.session_state.resume_analysis_data
        target_role     = st.session_state.get("target_role_used", "Software Engineer")
        exp_level       = resume_analysis.get("experience_level", "Beginner")
        skills_missing  = resume_analysis.get("skills_missing", [])

        if not skills_missing:
            st.success("🎉 No skill gaps found — you're already a strong match!")
            return

        # Skill gap pills
        pills_html = "".join(_pill(s, "#1e293b", "#EF4444") for s in skills_missing[:12])
        st.markdown(
            f'<p style="color:#94a3b8;font-size:0.85rem;">Gaps identified:</p>'
            f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:1rem;">{pills_html}</div>',
            unsafe_allow_html=True,
        )

        if st.button("🗺️ Generate Learning Roadmap", type="primary", use_container_width=True):
            with st.spinner("Building your personalised roadmap..."):
                roadmap = recommend_resources(
                    skills_missing=skills_missing,
                    target_role=target_role,
                    experience_level=exp_level,
                )
                st.session_state.learning_roadmap = roadmap

        roadmap = st.session_state.get("learning_roadmap")
        if not roadmap:
            st.info("💡 The roadmap prioritises skills by role-importance, estimates learning time, "
                    "and links to free YouTube channels, official docs, and curated courses.")
            return

        # ── Summary metrics ───────────────────────────────────────────────────
        total_weeks = roadmap.get("total_estimated_weeks", 0)
        quick_wins  = roadmap.get("quick_wins", [])
        tip         = roadmap.get("learning_tip", "")

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Learning Time", f"~{total_weeks} weeks")
        m2.metric("Quick Wins (≤2 weeks)", len(quick_wins))
        m3.metric("Skills to Cover", len(roadmap.get("learning_plan", [])))

        if tip:
            st.info(f"💡 **Personalised tip:** {tip}")

        # ── Suggested order ───────────────────────────────────────────────────
        order = roadmap.get("suggested_order", [])
        if order:
            st.markdown("**📋 Recommended learning order:**")
            order_pills = "".join(
                f'<span style="background:#1e293b;color:#94a3b8;border-radius:99px;'
                f'padding:3px 12px;font-size:0.78rem;margin:2px;display:inline-block;">'
                f'{i+1}. {s}</span>'
                for i, s in enumerate(order)
            )
            st.markdown(
                f'<div style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:1rem;">{order_pills}</div>',
                unsafe_allow_html=True,
            )

        # ── Learning plan cards ───────────────────────────────────────────────
        st.markdown("#### 🎯 Skill-by-Skill Plan")
        plan = roadmap.get("learning_plan", [])
        for item in plan:
            priority = item.get("priority", "Medium")
            pc = _priority_color(priority)
            skill = item.get("skill", "")
            weeks = item.get("estimated_weeks", "?")

            with st.expander(
                f"{'🔴' if priority=='High' else '🟡' if priority=='Medium' else '🟢'} "
                f"{skill}  ·  ~{weeks} weeks  ·  {priority} priority"
            ):
                st.markdown(
                    f'<p style="color:{pc};font-size:0.82rem;font-weight:600;">{priority} Priority</p>',
                    unsafe_allow_html=True,
                )
                st.markdown(f"**Why this matters:** {item.get('reason', '')}")

                prereqs = item.get("prerequisite_of", [])
                if prereqs:
                    st.caption(f"📌 Learn this before: {', '.join(prereqs)}")

                # Free resources
                free = item.get("free_resources", [])
                if free:
                    st.markdown("**🆓 Free Resources:**")
                    for url in free:
                        st.markdown(f"  - [{url}]({url})")

                # Course recommendation
                course = item.get("recommended_course", "")
                if course:
                    st.markdown(f"**🎓 Recommended Course:** {course}")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — Answer Coach
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        st.markdown("#### 🎯 Interview Answer Coach")
        st.markdown(
            '<p style="color:#64748b;font-size:0.88rem;">Paste any interview question '
            'and your rough answer — the AI rewrites it using the right framework '
            '(STAR, Technical, System Design) and scores both versions.</p>',
            unsafe_allow_html=True,
        )

        target_role_coach = st.session_state.get("target_role_used", "")

        c1, c2, c3 = st.columns(3)
        with c1:
            q_type = st.selectbox("Question Type", QUESTION_TYPES, key="coach_qtype")
        with c2:
            difficulty = st.selectbox(
                "Difficulty", ["Entry Level", "Mid Level", "Senior Level"], index=1, key="coach_diff"
            )
        with c3:
            role_coach = st.text_input("Role", value=target_role_coach, key="coach_role")

        question_input = st.text_area(
            "Interview Question",
            height=80,
            placeholder="e.g. Tell me about a time you handled a conflict in your team.",
            key="coach_question",
        )

        answer_input = st.text_area(
            "Your Answer (rough draft — be honest, don't polish)",
            height=150,
            placeholder="Write your answer as you would naturally say it in an interview...",
            key="coach_answer",
        )

        if st.button("🔍 Coach My Answer", type="primary", use_container_width=True):
            if not question_input.strip() or not answer_input.strip():
                st.warning("Please fill in both the question and your answer.")
            else:
                with st.spinner("Analysing and rewriting your answer..."):
                    coaching = coach_answer(
                        question=question_input,
                        raw_answer=answer_input,
                        question_type=q_type,
                        target_role=role_coach,
                        difficulty=difficulty,
                    )
                    st.session_state.coaching_result = coaching

        coaching = st.session_state.get("coaching_result")
        if not coaching:
            st.info(
                "💡 **How it works:** Paste a rough answer → the coach scores it across 5 dimensions "
                "(clarity, relevance, depth, structure, impact) → rewrites it using the correct "
                "framework → shows exactly what improved and why."
            )
            return

        if coaching.get("error"):
            st.error(coaching["error"])
            return

        # ── Score comparison ──────────────────────────────────────────────────
        orig_score = coaching.get("original_score", 0)
        impr_score = coaching.get("improved_score", 0)
        delta      = impr_score - orig_score

        st.markdown("<br>", unsafe_allow_html=True)
        sc1, sc2, sc3 = st.columns(3)

        def score_card(col, label, score, color):
            col.markdown(
                f'<div style="background:#1e293b;border-top:3px solid {color};'
                f'border-radius:10px;padding:1rem;text-align:center;">'
                f'<div style="font-size:2rem;font-weight:800;color:{color};">{score}/10</div>'
                f'<div style="color:#64748b;font-size:0.78rem;">{label}</div></div>',
                unsafe_allow_html=True,
            )

        orig_color = "#EF4444" if orig_score < 5 else "#F59E0B" if orig_score < 7 else "#10B981"
        impr_color = "#10B981"
        delta_color = "#10B981" if delta > 0 else "#EF4444"

        score_card(sc1, "Your Original Score", orig_score, orig_color)
        score_card(sc2, "After Coaching", impr_score, impr_color)
        sc3.markdown(
            f'<div style="background:#1e293b;border-top:3px solid {delta_color};'
            f'border-radius:10px;padding:1rem;text-align:center;">'
            f'<div style="font-size:2rem;font-weight:800;color:{delta_color};">+{delta}</div>'
            f'<div style="color:#64748b;font-size:0.78rem;">Score Improvement</div></div>',
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Dimension scores ──────────────────────────────────────────────────
        dims = coaching.get("dimension_scores", {})
        if dims:
            st.markdown("**📊 Dimension Breakdown (original answer)**")
            for dim, score in dims.items():
                col_d1, col_d2 = st.columns([2, 8])
                col_d1.markdown(
                    f'<p style="color:#94a3b8;font-size:0.85rem;margin:0;padding-top:4px;">'
                    f'{dim.capitalize()}: {score}/10</p>',
                    unsafe_allow_html=True,
                )
                with col_d2:
                    _score_bar(score)

        # ── Weaknesses ────────────────────────────────────────────────────────
        weaknesses = coaching.get("weaknesses", [])
        if weaknesses:
            st.markdown("**❌ What was weak:**")
            for w in weaknesses:
                st.markdown(f"- {w}")

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Rewritten answer ──────────────────────────────────────────────────
        framework = coaching.get("framework_used", "")
        st.markdown(f"#### ✅ Rewritten Answer  ·  <span style='color:#6366f1;font-size:0.85rem;'>{framework}</span>", unsafe_allow_html=True)
        st.markdown(
            f'<div style="background:#0f172a;border:1px solid #334155;'
            f'border-radius:10px;padding:1.2rem;color:#e2e8f0;line-height:1.8;font-size:0.92rem;">'
            f'{coaching.get("rewritten_answer", "").replace(chr(10), "<br>")}'
            f'</div>',
            unsafe_allow_html=True,
        )

        st.download_button(
            label="⬇️ Copy Rewritten Answer",
            data=coaching.get("rewritten_answer", ""),
            file_name="coached_answer.txt",
            mime="text/plain",
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Improvements ──────────────────────────────────────────────────────
        improvements = coaching.get("key_improvements", [])
        if improvements:
            with st.expander("💡 What the AI improved and why"):
                for imp in improvements:
                    st.markdown(f"- {imp}")

        # ── What interviewer wants ─────────────────────────────────────────────
        what_they_want = coaching.get("what_interviewer_wants", "")
        if what_they_want:
            st.info(f"🧠 **What this question really tests:** {what_they_want}")

        # ── Follow-up prep ────────────────────────────────────────────────────
        followups = coaching.get("follow_up_prep", [])
        if followups:
            st.markdown("**🔮 Likely follow-up questions — prepare for these:**")
            for fq in followups:
                st.markdown(
                    f'<div style="background:#1e293b;border-left:3px solid #F59E0B;'
                    f'border-radius:4px;padding:0.6rem 0.9rem;margin:4px 0;color:#e2e8f0;'
                    f'font-size:0.88rem;">{fq}</div>',
                    unsafe_allow_html=True,
                )
