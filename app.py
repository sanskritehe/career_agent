import streamlit as st
import json
from utils.pdf_parser import extract_resume_text
from agents.resume_agent import analyze_resume
from agents.job_match_agent import match_jobs
from agents.dsa.streamlit_ui import render_dsa_tutor
from utils.rag_pipeline import get_index_status, index_job_descriptions

st.set_page_config(page_title="Career AI Assistant", layout="wide")


def render_resume_job_match():
    """Resume and Job Matching Module"""
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

                # ── Resume Agent ──────────────────────────────────────────────
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
                        st.write(resume_data.get('summary'))
                        st.write("**Skills Present:**")
                        st.write(", ".join(resume_data.get('skills_present', [])))

                        if resume_data.get("most_relevant_jd"):
                            st.info(f"📄 Most relevant JD retrieved: **{resume_data['most_relevant_jd']}**")

                        with st.expander("View Full Analysis"):
                            st.json(resume_data)

                    except json.JSONDecodeError:
                        st.error("The Resume Agent returned an invalid response.")
                        st.code(raw_resume)
                        resume_data = None

                # ── Job Match Agent ───────────────────────────────────────────
                if resume_data:
                    with col2:
                        st.subheader("Job Matching Score")
                        raw_job = match_jobs(resume_data, target_role)

                        try:
                            job_data = json.loads(raw_job)
                            roles    = job_data.get("suitable_roles", [])

                            if roles:
                                for role in roles:

                                    # Invalid role
                                    if not role.get("valid_role", True):
                                        st.error(f"❌ Invalid Job Role: **{role.get('role')}**")
                                        st.warning(role.get("reasoning"))
                                        st.info("💡 Try: *Data Analyst, Backend Developer, ML Engineer*")
                                        continue

                                    final_score    = role.get("readiness_score", 0)
                                    semantic_score = role.get("semantic_score", 0)
                                    overlap_bonus  = role.get("overlap_bonus", 0)
                                    rag_used       = role.get("rag_used", False)
                                    jd_count       = role.get("retrieved_jd_count", 0)

                                    # Main score
                                    st.metric(
                                        label=f"Match for: {role.get('role')}",
                                        value=f"{final_score}%"
                                    )
                                    st.progress(int(final_score) / 100)

                                    if rag_used:
                                        st.caption(f"🔍 RAG-augmented scoring — {jd_count} real JDs retrieved from vector DB")

                                    # Score breakdown
                                    with st.expander("📊 Score Breakdown"):
                                        bc1, bc2 = st.columns(2)
                                        bc1.metric("Semantic Similarity", f"{semantic_score}%")
                                        bc2.metric("Skill Overlap Bonus", f"+{overlap_bonus}%")

                                        ds = role.get("dataset_source", "unknown")
                                        matched_ds = role.get("matched_dataset_roles", [])
                                        st.caption(f"📦 Dataset source: **{ds}** | Matched roles: {', '.join(matched_ds)}")

                                    # Skills
                                    sk1, sk2 = st.columns(2)
                                    with sk1:
                                        matched = role.get("matched_skills", [])
                                        st.markdown("**✅ Skills You Have**")
                                        if matched:
                                            for s in matched:
                                                st.markdown(f"- {s}")
                                        else:
                                            st.caption("None matched")

                                    with sk2:
                                        missing = role.get("missing_skills", [])
                                        st.markdown("**❌ Skills to Gain**")
                                        if missing:
                                            for s in missing:
                                                st.markdown(f"- {s}")
                                        else:
                                            st.caption("None missing 🎉")

                                    st.write("### 💬 Reasoning")
                                    st.info(role.get("reasoning"))

                            else:
                                st.warning("No matching data returned for this role.")

                        except json.JSONDecodeError:
                            st.error("The Job Match Agent returned an invalid response.")
                            st.code(raw_job)
        else:
            st.warning("Please upload a resume and enter a target role first.")


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🎯 Career AI Assistant")
    st.markdown("---")

    page = st.radio(
        "Select Module:",
        ["Resume & Job Match", "🎯 DSA Tutor"],
        help="Choose what you want to work on"
    )

    st.markdown("---")

    # RAG index status
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

    else:
        st.info("🎯 DSA Tutor\n\nPersonalized DSA learning path with practice problems and progress tracking.")


# ── Routing ───────────────────────────────────────────────────────────────────
if page == "Resume & Job Match":
    render_resume_job_match()
else:
    render_dsa_tutor()
