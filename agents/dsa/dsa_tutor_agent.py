import json
import os
from datetime import datetime, date, timedelta
from agents.dsa.dsa_topics_db import DSA_TOPICS_MAP
from utils.llm import call_llm

PROGRESS_FILE = "dsa_progress.json"


class DSAProgressTracker:
    """
    Tracks DSA learning progress: completions, notes, time spent, streaks.
    """

    def __init__(self):
        self.progress_data = self.load_progress()

    # ─── Persistence ────────────────────────────────────────────────────────

    def load_progress(self):
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, "r") as f:
                    data = json.load(f)
                # Migrate old data that lacks new keys
                data.setdefault("streak", {"current": 0, "longest": 0, "last_active_date": None})
                data.setdefault("daily_log", {})
                for topic_data in data.get("topics", {}).values():
                    topic_data.setdefault("topic_name", topic_data.get("topic_name", ""))
                # Ensure all problems from DSA_TOPICS_MAP are present
                self._migrate_progress_data(data)
                return data
            except Exception:
                return self._initialize_progress()
        return self._initialize_progress()

    def _initialize_progress(self):
        progress = {
            "user_info": {
                "experience_level": "Beginner",
                "study_duration_months": 6,
                "roadmap_created_date": datetime.now().isoformat(),
            },
            "streak": {
                "current": 0,
                "longest": 0,
                "last_active_date": None,
            },
            "daily_log": {},   # "YYYY-MM-DD" -> count of problems solved that day
            "topics": {},
        }

        for topic_name, topic_data in DSA_TOPICS_MAP.items():
            progress["topics"][topic_name] = {
                "topic_name": topic_name,
                "description": topic_data["description"],
                "total_problems": len(topic_data["problems"]),
                "completed_problems": 0,
                "problems": {},
            }
            for problem in topic_data["problems"]:
                progress["topics"][topic_name]["problems"][problem["id"]] = {
                    "id": problem["id"],
                    "name": problem["name"],
                    "difficulty": problem["difficulty"],
                    "leetcode_link": problem["leetcode_link"],
                    "completed": False,
                    "solved_date": None,
                    "time_spent_mins": 0,
                    "notes": "",
                    "revisions": 0,
                }

        return progress

    def _migrate_progress_data(self, data):
        """Ensure all problems from DSA_TOPICS_MAP are present in progress data."""
        topics = data.setdefault("topics", {})
        
        for topic_name, topic_data in DSA_TOPICS_MAP.items():
            if topic_name not in topics:
                topics[topic_name] = {
                    "topic_name": topic_name,
                    "description": topic_data["description"],
                    "total_problems": len(topic_data["problems"]),
                    "completed_problems": 0,
                    "problems": {},
                }
            
            topic_progress = topics[topic_name]
            topic_progress.setdefault("problems", {})
            
            # Add any missing problems
            for problem in topic_data["problems"]:
                if problem["id"] not in topic_progress["problems"]:
                    topic_progress["problems"][problem["id"]] = {
                        "id": problem["id"],
                        "name": problem["name"],
                        "difficulty": problem["difficulty"],
                        "leetcode_link": problem["leetcode_link"],
                        "completed": False,
                        "solved_date": None,
                        "time_spent_mins": 0,
                        "notes": "",
                        "revisions": 0,
                    }
            
            # Update total_problems count
            topic_progress["total_problems"] = len(topic_data["problems"])
            
            # Recalculate completed_problems
            topic_progress["completed_problems"] = sum(
                1 for p in topic_progress["problems"].values() if p.get("completed", False)
            )

    def save_progress(self):
        with open(PROGRESS_FILE, "w") as f:
            json.dump(self.progress_data, f, indent=2)

    # ─── Streak helpers ──────────────────────────────────────────────────────

    def _update_streak(self):
        today = date.today().isoformat()
        streak = self.progress_data["streak"]
        last = streak.get("last_active_date")

        if last == today:
            return  # Already counted today

        if last is None:
            streak["current"] = 1
        else:
            last_date = date.fromisoformat(last)
            delta = (date.today() - last_date).days
            if delta == 1:
                streak["current"] += 1
            elif delta > 1:
                streak["current"] = 1  # Streak broken

        streak["longest"] = max(streak["longest"], streak["current"])
        streak["last_active_date"] = today

        # Log daily activity
        daily_log = self.progress_data.setdefault("daily_log", {})
        daily_log[today] = daily_log.get(today, 0) + 1

    def get_streak(self):
        return self.progress_data.get("streak", {"current": 0, "longest": 0, "last_active_date": None})

    def get_activity_heatmap_data(self, days: int = 90):
        """Return list of (date_str, count) for the last `days` days."""
        daily_log = self.progress_data.get("daily_log", {})
        result = []
        for i in range(days - 1, -1, -1):
            d = (date.today() - timedelta(days=i)).isoformat()
            result.append({"date": d, "count": daily_log.get(d, 0)})
        return result

    # ─── Problem completion ──────────────────────────────────────────────────

    def mark_problem_completed(self, topic_name: str, problem_id: str,
                                time_spent_mins: int = 0, notes: str = ""):
        topics = self.progress_data["topics"]
        if topic_name in topics and problem_id in topics[topic_name]["problems"]:
            p = topics[topic_name]["problems"][problem_id]
            p["completed"] = True
            p["solved_date"] = datetime.now().isoformat()
            if time_spent_mins:
                p["time_spent_mins"] = time_spent_mins
            if notes:
                p["notes"] = notes
            topics[topic_name]["completed_problems"] = sum(
                1 for x in topics[topic_name]["problems"].values() if x["completed"]
            )
            self._update_streak()
            self.save_progress()
            return True
        return False

    def mark_problem_incomplete(self, topic_name: str, problem_id: str):
        topics = self.progress_data["topics"]
        if topic_name in topics and problem_id in topics[topic_name]["problems"]:
            p = topics[topic_name]["problems"][problem_id]
            p["completed"] = False
            p["solved_date"] = None
            topics[topic_name]["completed_problems"] = sum(
                1 for x in topics[topic_name]["problems"].values() if x["completed"]
            )
            self.save_progress()
            return True
        return False

    def update_problem_notes(self, topic_name: str, problem_id: str,
                              notes: str = "", time_spent_mins: int = 0):
        topics = self.progress_data["topics"]
        if topic_name in topics and problem_id in topics[topic_name]["problems"]:
            p = topics[topic_name]["problems"][problem_id]
            p["notes"] = notes
            if time_spent_mins:
                p["time_spent_mins"] = time_spent_mins
            self.save_progress()
            return True
        return False

    def add_revision(self, topic_name: str, problem_id: str):
        topics = self.progress_data["topics"]
        if topic_name in topics and problem_id in topics[topic_name]["problems"]:
            topics[topic_name]["problems"][problem_id]["revisions"] += 1
            self.save_progress()
            return True
        return False

    # ─── Queries ─────────────────────────────────────────────────────────────

    def get_topic_progress(self, topic_name: str):
        if topic_name not in self.progress_data["topics"]:
            return None
        topic = self.progress_data["topics"][topic_name]
        total = topic["total_problems"]
        completed = topic["completed_problems"]
        return {
            "topic_name": topic_name,
            "description": topic["description"],
            "total_problems": total,
            "completed_problems": completed,
            "completion_percentage": round(completed / total * 100) if total else 0,
            "problems": topic["problems"],
        }

    def get_all_progress(self):
        all_topics = self.progress_data["topics"]
        total = sum(t["total_problems"] for t in all_topics.values())
        completed = sum(t["completed_problems"] for t in all_topics.values())

        topic_summaries = [
            {
                "topic_name": name,
                "total": data["total_problems"],
                "completed": data["completed_problems"],
                "percentage": round(data["completed_problems"] / data["total_problems"] * 100)
                if data["total_problems"] else 0,
            }
            for name, data in all_topics.items()
        ]

        return {
            "overall_completion": round(completed / total * 100) if total else 0,
            "total_problems": total,
            "completed_problems": completed,
            "remaining_problems": total - completed,
            "user_info": self.progress_data["user_info"],
            "topics": topic_summaries,
            "streak": self.get_streak(),
        }

    def get_progress_by_difficulty(self):
        counts = {
            "easy":   {"total": 0, "completed": 0},
            "medium": {"total": 0, "completed": 0},
            "hard":   {"total": 0, "completed": 0},
        }
        for topic_data in self.progress_data["topics"].values():
            for p in topic_data["problems"].values():
                key = p["difficulty"].lower()
                if key in counts:
                    counts[key]["total"] += 1
                    if p["completed"]:
                        counts[key]["completed"] += 1

        result = {}
        for diff, data in counts.items():
            result[diff] = {
                **data,
                "percentage": round(data["completed"] / data["total"] * 100)
                if data["total"] else 0,
            }
        return result

    def get_completed_problems_by_difficulty(self):
        """Return completed problems grouped by difficulty. (Bug-fixed)"""
        easy, medium, hard = [], [], []
        for topic_name, topic_data in self.progress_data["topics"].items():
            for p in topic_data["problems"].values():
                if not p["completed"]:
                    continue
                info = {
                    "id": p["id"],
                    "name": p["name"],
                    "topic": topic_name,        # ← fixed: was topic_data["topic_name"]
                    "solved_date": p["solved_date"],
                    "revisions": p["revisions"],
                    "time_spent_mins": p.get("time_spent_mins", 0),
                    "notes": p.get("notes", ""),
                }
                diff = p["difficulty"]
                if diff == "Easy":
                    easy.append(info)
                elif diff == "Medium":
                    medium.append(info)
                else:
                    hard.append(info)
        return {"easy": easy, "medium": medium, "hard": hard}

    def get_uncompleted_problems_by_topic(self, topic_name: str):
        if topic_name not in self.progress_data["topics"]:
            return []
        return [
            p for p in self.progress_data["topics"][topic_name]["problems"].values()
            if not p["completed"]
        ]

    def search_problems(self, query: str):
        """Full-text search across all problems (name, tags, topic)."""
        query = query.lower()
        results = []
        for topic_name, topic_data in self.progress_data["topics"].items():
            for p in topic_data["problems"].values():
                if query in p["name"].lower() or query in topic_name.lower():
                    results.append({**p, "topic": topic_name})
        return results

    def set_user_info(self, experience_level: str, study_duration_months: int):
        self.progress_data["user_info"]["experience_level"] = experience_level
        self.progress_data["user_info"]["study_duration_months"] = study_duration_months
        self.save_progress()

    def reset_all_progress(self):
        """Wipe all completion data (keep user_info)."""
        user_info = self.progress_data.get("user_info", {})
        self.progress_data = self._initialize_progress()
        self.progress_data["user_info"] = user_info
        self.save_progress()


# ─── AI-Powered DSA Functions ───────────────────────────────────────────────

def generate_dsa_roadmap(experience_level: str, study_duration_months: int, focus_areas: list = None):
    """
    Generate a personalized DSA learning roadmap based on user profile.
    """
    prompt = f"""
    Generate a personalized DSA (Data Structures & Algorithms) learning roadmap for a {experience_level} level programmer 
    who has {study_duration_months} months to prepare. {"Focus on: " + ", ".join(focus_areas) if focus_areas else ""}
    
    Available topics: {list(DSA_TOPICS_MAP.keys())}
    
    Return a JSON with:
    - "roadmap": array of phases, each with "phase_name", "duration_weeks", "topics" (array of topic names), "milestones"
    - "estimated_total_problems": number
    - "recommended_daily_problems": number
    - "tips": array of strings
    """
    
    response = call_llm(prompt)
    try:
        return json.loads(response)
    except:
        return {
            "roadmap": [
                {
                    "phase_name": "Foundation",
                    "duration_weeks": 4,
                    "topics": ["Arrays & Hashing", "Two Pointers"],
                    "milestones": ["Complete 50 easy problems"]
                }
            ],
            "estimated_total_problems": 150,
            "recommended_daily_problems": 3,
            "tips": ["Practice daily", "Review weak areas"]
        }


def generate_problem_explanation(problem_id: str, problem_name: str, difficulty: str):
    """
    Generate detailed explanation for a DSA problem.
    """
    # Find the problem across all topics
    problem = None
    topic_name = None
    for t_name, t_data in DSA_TOPICS_MAP.items():
        for p in t_data["problems"]:
            if p["id"] == problem_id:
                problem = p
                topic_name = t_name
                break
        if problem:
            break
    
    if not problem:
        return {"error": "Problem not found"}
    
    prompt = f"""
    Provide a detailed explanation for the LeetCode problem: {problem_name} (ID: {problem_id})
    Difficulty: {difficulty}
    Topic: {topic_name}
    
    Problem details: {problem}
    
    Return JSON with:
    - "problem_understanding": brief description of what the problem asks
    - "approach": object with "algorithm_name", "strategy", "steps" (array)
    - "complexity_analysis": object with "time_complexity", "space_complexity"
    - "solution_code": object with "code" (string) and "language" (string)
    - "key_insights": array of important points
    """
    
    response = call_llm(prompt)
    try:
        return json.loads(response)
    except:
        return {
            "problem_understanding": f"{problem_name} - {difficulty} problem from {topic_name} topic",
            "approach": {
                "algorithm_name": "Hash Map",
                "strategy": "Use hash map to track frequencies",
                "steps": ["Initialize hash map", "Iterate through array", "Check conditions"]
            },
            "complexity_analysis": {
                "time_complexity": "O(n)",
                "space_complexity": "O(n)"
            },
            "solution_code": {
                "code": "# Solution code here\ndef solution():\n    pass",
                "language": "python"
            },
            "key_insights": ["Use hash map for O(1) lookups"]
        }


def suggest_next_topic(current_progress: dict):
    """
    Suggest the next topic to study based on current progress.
    """
    completed_topics = [t for t in current_progress["topics"] if t["percentage"] == 100]
    incomplete_topics = [t for t in current_progress["topics"] if t["percentage"] < 100]
    
    if not incomplete_topics:
        return "All topics completed! Focus on revisions."
    
    # Simple logic: suggest the first incomplete topic
    next_topic = incomplete_topics[0]["topic_name"]
    
    prompt = f"""
    Based on progress: {current_progress}
    Completed topics: {[t["topic_name"] for t in completed_topics]}
    Suggest the next best topic to study.
    
    Return JSON with:
    - "suggested_topic": topic name
    - "reason": why this topic
    - "estimated_time": weeks needed
    """
    
    response = call_llm(prompt)
    try:
        return json.loads(response)
    except:
        return {
            "suggested_topic": next_topic,
            "reason": "Continue with incomplete topics",
            "estimated_time": 2
        }


def evaluate_readiness(progress_data: dict):
    """
    Evaluate user's interview readiness based on progress.
    """
    prompt = f"""
    Evaluate DSA interview readiness based on this progress data: {progress_data}
    
    Return JSON with:
    - "readiness_score": 0-100
    - "strengths": array of strings
    - "weaknesses": array of strings
    - "recommendations": array of strings
    - "estimated_interview_success": percentage
    """
    
    response = call_llm(prompt)
    try:
        return json.loads(response)
    except:
        return {
            "readiness_score": 50,
            "strengths": ["Good progress"],
            "weaknesses": ["Need more practice"],
            "recommendations": ["Practice more problems"],
            "estimated_interview_success": 60
        }


def generate_hint(problem_id: str, problem_name: str, difficulty: str, hint_level: int):
    """
    Generate a hint for a stuck problem.
    """
    # Find the topic
    topic_name = None
    for t_name, t_data in DSA_TOPICS_MAP.items():
        for p in t_data["problems"]:
            if p["id"] == problem_id:
                topic_name = t_name
                break
        if topic_name:
            break
    
    hint_types = {
        1: "gentle nudge",
        2: "algorithm name", 
        3: "step-by-step outline"
    }
    
    prompt = f"""
    Generate a {hint_types.get(hint_level, "helpful")} hint for the {difficulty} LeetCode problem: {problem_name} (ID: {problem_id})
    Topic: {topic_name}
    
    Hint level {hint_level}: {hint_types.get(hint_level, "general")}
    
    Return JSON with:
    - "hint": the hint text
    - "difficulty_level": "subtle" or "direct"
    - "encouragement": optional encouraging message
    """
    
    response = call_llm(prompt)
    try:
        return json.loads(response)
    except:
        return {
            "hint": "Think about using a hash map to track frequencies",
            "difficulty_level": "subtle",
            "encouragement": "You're on the right track!"
        }


# Global singleton
progress_tracker = DSAProgressTracker()