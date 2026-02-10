def calculate_weighted_score(skills_present, job_requirements):
    """
    Scoring Formula:
    - Required Skills: 70%
    - Preferred Skills: 30%
    """
    req_skills = set(job_requirements.get('required', []))
    pref_skills = set(job_requirements.get('preferred', []))
    present = set(skills_present)

    # Calculate match percentages
    req_match = len(present.intersection(req_skills)) / len(req_skills) if req_skills else 0
    pref_match = len(present.intersection(pref_skills)) / len(pref_skills) if pref_skills else 0

    total_score = (req_match * 0.70) + (pref_match * 0.30)
    return round(total_score * 100, 2)