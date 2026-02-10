import streamlit as st
import json
from utils.pdf_parser import extract_resume_text
from agents.resume_agent import analyze_resume
from agents.job_match_agent import match_jobs

st.set_page_config(page_title="Career AI Assistant", layout="wide")
st.title("GenAI Resume + Job Matching Agent")

# Sidebar for additional info or settings
with st.sidebar:
    st.info("This system uses a multi-agent approach to analyze resumes and match them against specific job roles using Llama 3.3.")

# User Inputs
resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
target_role = st.text_input("Enter Target Job Role (e.g., Frontend Developer)")

if st.button("Run Analysis"):
    if resume_file and target_role:
        with st.spinner("Agents are working..."):
            # 1. Extract text from the PDF
            resume_text = extract_resume_text(resume_file)

            if not resume_text.strip():
                st.error("Could not extract text from the PDF. Please check the file.")
                st.stop()

            col1, col2 = st.columns(2)

            # 2. Resume Agent Execution
            with col1:
                st.subheader("Resume Analysis")
                raw_resume = analyze_resume(resume_text, target_role)
                
                try:
                    resume_data = json.loads(raw_resume)
                    st.success("Resume Analyzed Successfully")
                    
                    # Display structured data nicely
                    st.write(f"**Experience Level:** {resume_data.get('experience_level')}")
                    st.write("**Summary:**")
                    st.write(resume_data.get('summary'))
                    
                    st.write("**Skills Present:**")
                    st.write(", ".join(resume_data.get('skills_present', [])))
                    
                    with st.expander("View Full Analysis"):
                        st.json(resume_data)
                        
                except json.JSONDecodeError:
                    st.error("The Resume Agent returned an invalid response.")
                    st.code(raw_resume)
                    resume_data = None

            # 3. Job Match Agent Execution (Passing target_role for 1:1 matching)
            if resume_data:
                with col2:
                    st.subheader("Job Matching Score")
                    # We pass both the analysis and the specific role entered by the user
                    raw_job = match_jobs(resume_data, target_role)
                    
                    try:
                        job_data = json.loads(raw_job)
                        
                        # Loop through and display the score for the specific role
                        roles = job_data.get("suitable_roles", [])
                        if roles:
                            for role in roles:
                                # Metric shows the score clearly
                                st.metric(
                                    label=f"Match for: {role.get('role')}", 
                                    value=f"{role.get('readiness_score')}%"
                                )
                                st.write("### Reasoning")
                                st.info(role.get("reasoning"))
                        else:
                            st.warning("No matching data returned for this role.")
                            
                    except json.JSONDecodeError:
                        st.error("The Job Match Agent returned an invalid response.")
                        st.code(raw_job)

    else:
        st.warning("Please upload a resume and enter a target role first.")