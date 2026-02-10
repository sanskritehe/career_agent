from utils.llm import call_llm

def analyze_resume(resume_text, target_role):

    prompt = f"""
You are a Resume Analysis Agent.

Resume:
{resume_text}

Target Job Role:
{target_role}

Tasks:
1. Extract technical skills.
2. Identify missing skills required for the target role.
3. Estimate experience level (Beginner/Intermediate/Advanced).
4. Provide strengths and weaknesses.
5. Provide short professional summary.

Return STRICTLY in JSON format:

{{
 "skills_present": [],
 "skills_missing": [],
 "experience_level": "",
 "strengths": [],
 "weaknesses": [],
 "summary": ""
}}
"""

    return call_llm(prompt)
