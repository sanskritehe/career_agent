from utils.llm import call_llm

def match_jobs(resume_analysis_json, target_role):
    # Instead of searching the database for many roles, 
    # we target the specific role entered by the user.
    
    prompt = f"""
    You are a Job Matching Agent.
    
    Target Role: {target_role}
    Candidate Skill Profile: {resume_analysis_json}

    TASK: 
    Evaluate the candidate strictly for the "Target Role" provided.
    Compare their present skills and experience level against the standard requirements for a {target_role}.
    
    SCORING RUBRIC:
    - 0-30%: Missing core technical stack.
    - 31-60%: Has base skills but lacks specialized tools/experience.
    - 61-90%: Strong match; has core stack and relevant experience.
    - 91-100%: Perfect match in skills and experience.

    Return a JSON object:
    {{
      "suitable_roles": [
        {{ 
          "role": "{target_role}", 
          "readiness_score": 0, 
          "reasoning": "Explain based on skill overlap" 
        }}
      ]
    }}
    """
    return call_llm(prompt)