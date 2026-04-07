import streamlit as st
import json
from utils.pdf_parser import extract_resume_text
from agents.resume_agent import analyze_resume
from agents.job_match_agent import match_jobs
from agents.dsa.streamlit_ui import render_dsa_tutor
from agents.interview.streamlit_ui import render_interview_prep
from utils.rag_pipeline import get_index_status, index_job_descriptions
from utils.database import init_db, save_resume_analysis, save_interview_session
from auth.login_page import render_auth_page
from auth.profile_page import render_profile_page
from agents.coordinator_ui import render_coordinator_report   # ← coordinator
from agents.extras_ui import render_extras_page               # ← AI tools

st.set_page_config(page_title="Career AI Assistant", layout="wide")

# ── Init DB on startup ────────────────────────────────────────────────────────
try:
    init_db()
except Exception as e:
    st.error(f"⚠️ Database connection failed: {e}\n\nCheck your .env MySQL settings.")
    st.stop()

# ── Auth gate ─────────────────────────────────────────────────────────────────
if "user" not in st.session_state or not st.session_state.user:
    render_auth_page()
    st.stop()

user         = st.session_state.user
user_id      = st.session_state.user_id
display_name = user.get("full_name") or user.get("username", "User")


# ── Resume + Job Match ────────────────────────────────────────────────────────

def render_resume_job_match():
    st.title("💼 Resume + Job Matching Agent")

    resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
    target_role = st.text_input("Enter Target Job Role (e.g., Data Analyst)")

    if st.button("Run Analysis"):
        if resume_file and target_role:
            with st.spinner("Agents are working..."):
                resume_text = extract_resume_text(resume_file)

                if not resume_text.strip():
                    st.error("Could not extract text from the PDF. Please check the file.")
                    st.stop()

                col1, col2 = st.columns(2)
                resume_data = None
                match_score = 0

                with col1:
                    st.subheader("Resume Analysis")
                    raw_resume = analyze_resume(resume_text, target_role)
                    try:
                        resume_data = json.loads(raw_resume)
                        st.success("Resume Analyzed Successfully")

                        if resume_data.get("rag_used"):
                            st.caption("🔍 RAG-augmented analysis — grounded in real job descriptions")

                        st.write(f"**Experience Level:** {resume_data.get('experience_level')}")
                        st.write("**Summary:**")
                        st.write(resume_data.get("summary"))
                        st.write("**Skills Present:**")
                        st.write(", ".join(resume_data.get("skills_present", [])))

                        if resume_data.get("most_relevant_jd"):
                            st.info(f"📄 Most relevant JD retrieved: **{resume_data['most_relevant_jd']}**")

                        with st.expander("View Full Analysis"):
                            st.json(resume_data)

                        # Save for coordinator + extras
                        st.session_state.resume_analysis_data = resume_data
                        st.session_state.target_role_used = target_role
                        st.session_state.resume_raw_text = resume_text

                    except json.JSONDecodeError:
                        st.error("The Resume Agent returned an invalid response.")
                        st.code(raw_resume)
                        resume_data = None

                if resume_data:
                    with col2:
                        st.subheader("Job Matching Score")
                        raw_job = match_jobs(resume_data, target_role)
                        try:
                            job_data = json.loads(raw_job)
                            roles = job_data.get("suitable_roles", [])

                            if roles:
                                for role in roles:
                                    if not role.get("valid_role", True):
                                        st.error(f"❌ Invalid Job Role: **{role.get('role')}**")
                                        st.warning(role.get("reasoning"))
                                        st.info("💡 Try: *Data Analyst, Backend Developer, ML Engineer*")
                                        continue

                                    match_score    = role.get("readiness_score", 0)
                                    semantic_score = role.get("semantic_score", 0)
                                    overlap_bonus  = role.get("overlap_bonus", 0)
                                    rag_used       = role.get("rag_used", False)
                                    jd_count       = role.get("retrieved_jd_count", 0)

                                    # Save for coordinator
                                    st.session_state.job_match_result = role

                                    st.metric(label=f"Match for: {role.get('role')}", value=f"{match_score}%")
                                    st.progress(int(match_score) / 100)

                                    if rag_used:
                                        st.caption(f"🔍 RAG-augmented scoring — {jd_count} real JDs retrieved")

                                    with st.expander("📊 Score Breakdown"):
                                        bc1, bc2 = st.columns(2)
                                        bc1.metric("Semantic Similarity", f"{semantic_score}%")
                                        bc2.metric("Skill Overlap Bonus", f"+{overlap_bonus}%")
                                        ds         = role.get("dataset_source", "unknown")
                                        matched_ds = role.get("matched_dataset_roles", [])
                                        st.caption(f"📦 Dataset source: **{ds}** | Matched roles: {', '.join(matched_ds)}")

                                    sk1, sk2 = st.columns(2)
                                    with sk1:
                                        matched = role.get("matched_skills", [])
                                        st.markdown("**✅ Skills You Have**")
                                        if matched:
                                            for s in matched: st.markdown(f"- {s}")
                                        else:
                                            st.caption("None matched")
                                    with sk2:
                                        missing = role.get("missing_skills", [])
                                        st.markdown("**❌ Skills to Gain**")
                                        if missing:
                                            for s in missing: st.markdown(f"- {s}")
                                        else:
                                            st.caption("None missing 🎉")

                                    st.write("### 💬 Reasoning")
                                    st.info(role.get("reasoning"))
                            else:
                                st.warning("No matching data returned for this role.")

                            # Save to DB
                            try:
                                save_resume_analysis(
                                    user_id=user_id,
                                    target_role=target_role,
                                    analysis_data=resume_data,
                                    match_score=match_score,
                                )
                            except Exception:
                                pass

                        except json.JSONDecodeError:
                            st.error("The Job Match Agent returned an invalid response.")
                            st.code(raw_job)
        else:
            st.warning("Please upload a resume and enter a target role first.")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🎯 Career AI Assistant")
    st.markdown("---")

    # User card
    st.markdown(
    f'<div style="background:#1e293b;border-radius:10px;padding:0.75rem 1rem;margin-bottom:1rem;">'
    f'<div style="display:flex;align-items:center;gap:0.6rem;">'
    f'<div style="width:36px;height:36px;background:linear-gradient(135deg,#6366f1,#8b5cf6);'
    f'border-radius:50%;display:flex;align-items:center;justify-content:center;'
    f'color:#fff;font-weight:800;font-size:1rem;flex-shrink:0;">{display_name[0].upper()}</div>'
    f'<div><div style="color:#e2e8f0;font-weight:600;font-size:0.9rem;">{display_name}</div>'
    f'<div style="color:#64748b;font-size:0.75rem;">@{user.get("username","")}</div></div>'
    f'</div>'
    + (
        f'<div style="color:#94a3b8;font-size:0.78rem;margin-top:6px;">&#127919; {user.get("target_role","")}</div>'
        if user.get("target_role") else ''
    )
    + f'</div>',
    unsafe_allow_html=True,
)

    page = st.radio(
        "Select Module:",
        [
            "Resume & Job Match",
            "🎯 DSA Tutor",
            "🎤 Interview Prep",
            "🎯 Readiness Report",
            "🚀 AI Tools",
            "👤 My Profile",
        ],
        help="Choose what you want to work on",
    )

    st.markdown("---")

    if page == "Resume & Job Match":
        st.markdown("### 🔍 RAG Knowledge Base")
        status = get_index_status()
        if status["is_ready"]:
            st.success(f"✅ Indexed: {status['indexed_documents']} job descriptions")
        else:
            st.warning("⚠️ Knowledge base not indexed yet.")
            if st.button("⚡ Build Index Now", use_container_width=True):
                with st.spinner("Indexing job descriptions into vector DB..."):
                    count = index_job_descriptions()
                    st.success(f"✅ Indexed {count} job descriptions!")
                    st.rerun()
        st.markdown("---")
        st.info("💼 Resume Analysis & Job Matching\n\nRAG-powered: Retrieves real JDs from vector DB to ground the analysis.")

    elif page == "🎤 Interview Prep":
        st.markdown("### 🎤 Interview Prep")
        st.markdown("---")
        st.info(
            "**How it works:**\n\n"
            "1. 📄 Upload your resume\n"
            "2. 🎯 Enter target role\n"
            "3. 🗂️ Pick interview type\n"
            "4. ⚡ Choose difficulty\n"
            "5. 🚀 Get AI questions\n"
            "6. ✍️ Practice & get feedback\n"
            "7. 📊 View performance report"
        )
        st.markdown("---")
        st.caption("Sessions are saved to your profile automatically.")

    elif page == "🎯 Readiness Report":
        st.markdown("### 🎯 Readiness Report")
        st.markdown("---")
        st.info(
            "**Coordinator Agent synthesises:**\n\n"
            "1. 📄 Resume analysis\n"
            "2. 🧠 DSA progress\n"
            "3. 🎤 Interview performance\n"
            "4. 💼 Job match score\n\n"
            "→ Detects contradictions\n"
            "→ Unified readiness verdict\n"
            "→ Live job market data"
        )

    elif page == "🚀 AI Tools":
        st.markdown("### 🚀 AI Career Tools")
        st.markdown("---")
        st.info(
            "Three tools to go beyond analysis:\n\n"
            "📄 **Resume Builder** — AI rewrites your resume\n"
            "with ATS keywords from real JDs\n\n"
            "📚 **Learning Roadmap** — Maps skill gaps to\n"
            "free resources + estimated time\n\n"
            "🎯 **Answer Coach** — Rewrites your interview\n"
            "answers using STAR / Technical framework"
        )
        st.markdown("---")
        st.caption("Run Resume & Job Match first to unlock all features.")

    elif page == "👤 My Profile":
        st.info("View your interview history, resume analyses, and update your profile.")

    else:
        st.info("🎯 DSA Tutor\n\nPersonalized DSA learning path with practice problems and progress tracking.")

    st.markdown("---")
    if st.button("🚪 Logout", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ── Page routing ──────────────────────────────────────────────────────────────
if page == "Resume & Job Match":
    render_resume_job_match()

elif page == "🎤 Interview Prep":
    render_interview_prep()
    if (
        st.session_state.get("session_complete")
        and st.session_state.get("session_summary")
        and not st.session_state.get("session_saved_to_db")
    ):
        try:
            questions = st.session_state.interview_questions.get("questions", [])
            qa_pairs  = [
                {
                    "question": q.get("question", ""),
                    "answer":   st.session_state.user_answers.get(str(q.get("id", i + 1)), ""),
                }
                for i, q in enumerate(questions)
            ]
            save_interview_session(
                user_id=user_id,
                session_summary=st.session_state.session_summary,
                config=st.session_state.interview_config,
                qa_pairs=qa_pairs,
            )
            st.session_state.session_saved_to_db = True
        except Exception:
            pass

elif page == "🎯 Readiness Report":
    render_coordinator_report()

elif page == "🚀 AI Tools":
    render_extras_page()

elif page == "👤 My Profile":
    render_profile_page()

else:
    render_dsa_tutor()
