import json
from utils.llm import call_llm
from agents.dsa.dsa_topics_db import DSA_TOPICS_MAP, TIME_PLAN_CONFIGS, get_all_topics

def generate_dsa_roadmap(user_experience_level, time_available_months, learning_style="problem-solving"):
    """
    Generate a personalized DSA roadmap based on user preferences
    
    Args:
        user_experience_level: "Beginner", "Intermediate", or "Advanced"
        time_available_months: 3, 6, or 9 months
        learning_style: "problem-solving" (focused on coding problems)
    
    Returns:
        JSON with personalized roadmap
    """
    
    # Select time plan configuration
    time_key = f"{time_available_months}_months"
    if time_key not in TIME_PLAN_CONFIGS:
        time_key = "6_months"  # Default fallback
    
    time_plan = TIME_PLAN_CONFIGS[time_key]
    
    # Get all topics and their info
    topics_list = list(DSA_TOPICS_MAP.keys())
    topics_info = []
    for topic in topics_list:
        topic_data = DSA_TOPICS_MAP[topic]
        topics_info.append({
            "topic_name": topic,
            "description": topic_data["description"],
            "problem_count": len(topic_data["problems"]),
            "estimated_weeks": topic_data["estimated_weeks"]
        })
    
    # Create prompt for roadmap generation
    prompt = f"""
You are a DSA Roadmap Generator AI.

User Profile:
- Experience Level: {user_experience_level}
- Time Available: {time_available_months} months
- Learning Style: Problem-solving focused (LeetCode-style)

Roadmap Configuration:
- Total Duration: {time_plan['total_weeks']} weeks
- Problems per Week: {time_plan['problems_per_week']}
- Total Target Problems: ~{time_plan['total_problems']}

Available DSA Topics and their details:
{json.dumps(topics_info, indent=2)}

TASK:
1. Create a personalized roadmap for {user_experience_level} learners
2. Allocate topics based on importance and difficulty progression
3. Ensure balanced learning (easy → medium → hard)
4. Provide week-by-week breakdown
5. Set priority and order of topics

Considerations for different levels:
- Beginner: Start with fundamentals (Arrays, Strings, Basics). Add Trees, DP later.
- Intermediate: Focus on advanced patterns (DP, Graphs, Backtracking)
- Advanced: Optimize for interview prep - all topics with harder problems first

Return STRICTLY in JSON format:
{{
  "roadmap_summary": {{
    "duration_months": {time_available_months},
    "total_weeks": {time_plan['total_weeks']},
    "target_problems": {time_plan['total_problems']},
    "experience_level": "{user_experience_level}",
    "description": "Brief description of this roadmap"
  }},
  "weekly_schedule": [
    {{
      "week": 1,
      "topics": [
        {{
          "topic_name": "Topic Name",
          "focus_areas": ["area1", "area2"],
          "suggested_problems": 6,
          "difficulty_mix": "50% Easy, 40% Medium, 10% Hard",
          "key_concepts": ["concept1", "concept2"]
        }}
      ],
      "weekly_goal": "Understand fundamentals of topic"
    }}
  ],
  "topic_sequence": [
    {{
      "order": 1,
      "topic_name": "Topic Name",
      "priority": "Critical",
      "description": "Why this is first",
      "estimated_hours": 20,
      "problem_count": 8
    }}
  ],
  "learning_tips": [
    "Tip 1",
    "Tip 2"
  ],
  "milestone_checkpoints": [
    {{
      "week": 4,
      "checkpoint": "Completed Arrays, Strings, and Basics fundamentals",
      "expected_problems_solved": 32
    }}
  ]
}}
"""
    
    return call_llm(prompt)


def generate_problem_explanation(problem_id, problem_name, difficulty):
    """
    Generate detailed explanation for a specific problem
    
    Args:
        problem_id: LeetCode problem ID
        problem_name: Name of the problem
        difficulty: Easy/Medium/Hard
    
    Returns:
        JSON with approach, solution, and explanation
    """
    
    prompt = f"""
You are an expert DSA tutor.

Problem Details:
- LeetCode ID: {problem_id}
- Problem Name: {problem_name}
- Difficulty: {difficulty}

TASK: Provide a comprehensive problem explanation including:

1. **Problem Understanding** - Clear explanation of what needs to be solved
2. **Approach** - Algorithm/strategy to solve it
3. **Solution Code** - Provide Python solution with comments
4. **Complexity Analysis** - Time and space complexity
5. **Key Insights** - Important tips and edge cases
6. **Similar Problems** - Related LeetCode problems to practice

Return STRICTLY in JSON format:
{{
  "problem_id": "{problem_id}",
  "problem_name": "{problem_name}",
  "difficulty": "{difficulty}",
  "problem_understanding": "Detailed explanation of the problem",
  "approach": {{
    "strategy": "Describe the overall approach",
    "steps": ["Step 1", "Step 2", "Step 3"],
    "algorithm_name": "e.g., Two Pointers, DP, Graph BFS"
  }},
  "solution_code": {{
    "language": "python",
    "code": "Complete working Python code with comments"
  }},
  "complexity_analysis": {{
    "time_complexity": "O(n)",
    "space_complexity": "O(n)",
    "explanation": "Why this complexity"
  }},
  "key_insights": [
    "Insight 1",
    "Insight 2"
  ],
  "edge_cases": [
    "Edge case 1",
    "Edge case 2"
  ],
  "similar_problems": [
    {{"id": "XXX", "name": "Problem Name", "reason": "Why similar"}}
  ],
  "common_mistakes": [
    "Mistake 1",
    "Mistake 2"
  ]
}}
"""
    
    return call_llm(prompt)


def suggest_next_topic(completed_problems_count, current_level):
    """
    Suggest the next topic to study based on progress
    
    Args:
        completed_problems_count: Number of problems solved
        current_level: Current proficiency level
    
    Returns:
        Recommendation for next topic
    """
    
    topics = get_all_topics()
    
    prompt = f"""
You are a DSA Learning Assistant.

User Progress:
- Problems Completed: {completed_problems_count}
- Current Level: {current_level}

Available Topics to Learn:
{json.dumps(topics, indent=2)}

Based on the user's progress and current proficiency level, suggest:
1. Most relevant next topic
2. Why this topic is recommended
3. What skills will be gained
4. Expected difficulty increase
5. Estimated time required

Return as JSON:
{{
  "recommended_topic": "Topic Name",
  "reason": "Why this topic",
  "skills_to_gain": ["Skill 1", "Skill 2"],
  "difficulty_level": "Medium",
  "estimated_hours": 20,
  "prerequisites_review": ["Topic or skill to review first"],
  "learning_path_progress": "You are at X% of your learning journey"
}}
"""
    
    return call_llm(prompt)


def evaluate_readiness(problems_solved_list, target_level="Interview Ready"):
    """
    Evaluate user's readiness for interviews based on problems solved
    
    Args:
        problems_solved_list: List of problem IDs solved
        target_level: Interview level, internship level, etc.
    
    Returns:
        Evaluation report with strengths and gaps
    """
    
    prompt = f"""
You are a DSA Interview Prep Coach.

Problems Solved (by ID): {json.dumps(problems_solved_list)}

Target Level: {target_level}

Evaluate the candidate's readiness:
1. Strong Areas (topics mastered)
2. Weaker Areas (topics needing work)
3. Overall Readiness Score (0-100%)
4. Recommended Focus Areas
5. Time estimate to reach target

Return as JSON:
{{
  "readiness_score": 75,
  "target_level": "{target_level}",
  "strong_areas": ["Area 1", "Area 2"],
  "weak_areas": ["Area 1", "Area 2"],
  "readiness_level": "Good",
  "detailed_feedback": "Comprehensive assessment",
  "top_3_focus_areas": [
    {{"area": "Topic", "importance": "Critical", "time_needed_hours": 15}}
  ],
  "estimated_time_to_ready": "4 weeks",
  "practice_recommendation": "Practice hard problems, focus on X"
}}
"""
    
    return call_llm(prompt)
