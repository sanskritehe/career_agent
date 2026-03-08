import json
import os
from datetime import datetime
from agents.dsa.dsa_topics_db import DSA_TOPICS_MAP

# Store progress in a JSON file
PROGRESS_FILE = "dsa_progress.json"

class DSAProgressTracker:
    """
    Tracks user's DSA learning progress with checkboxes for problems
    """
    
    def __init__(self):
        self.progress_data = self.load_progress()
    
    def load_progress(self):
        """Load progress from file or create new"""
        if os.path.exists(PROGRESS_FILE):
            try:
                with open(PROGRESS_FILE, 'r') as f:
                    return json.load(f)
            except:
                return self._initialize_progress()
        return self._initialize_progress()
    
    def _initialize_progress(self):
        """Initialize progress structure for all topics and problems"""
        progress = {
            "user_info": {
                "experience_level": "Beginner",
                "study_duration_months": 6,
                "roadmap_created_date": datetime.now().isoformat()
            },
            "topics": {}
        }
        
        # Create entry for each topic
        for topic_name, topic_data in DSA_TOPICS_MAP.items():
            progress["topics"][topic_name] = {
                "topic_name": topic_name,
                "description": topic_data["description"],
                "total_problems": len(topic_data["problems"]),
                "completed_problems": 0,
                "problems": {}
            }
            
            # Create entry for each problem with checkbox status
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
                    "revisions": 0
                }
        
        return progress
    
    def save_progress(self):
        """Save progress to file"""
        with open(PROGRESS_FILE, 'w') as f:
            json.dump(self.progress_data, f, indent=2)
    
    def mark_problem_completed(self, topic_name, problem_id, time_spent_mins=0, notes=""):
        """Mark a problem as completed"""
        if topic_name in self.progress_data["topics"]:
            if problem_id in self.progress_data["topics"][topic_name]["problems"]:
                problem = self.progress_data["topics"][topic_name]["problems"][problem_id]
                problem["completed"] = True
                problem["solved_date"] = datetime.now().isoformat()
                problem["time_spent_mins"] = time_spent_mins
                problem["notes"] = notes
                
                # Update completed count
                total_completed = sum(
                    1 for p in self.progress_data["topics"][topic_name]["problems"].values() 
                    if p["completed"]
                )
                self.progress_data["topics"][topic_name]["completed_problems"] = total_completed
                
                self.save_progress()
                return True
        return False
    
    def mark_problem_incomplete(self, topic_name, problem_id):
        """Uncheck a problem (mark as incomplete)"""
        if topic_name in self.progress_data["topics"]:
            if problem_id in self.progress_data["topics"][topic_name]["problems"]:
                problem = self.progress_data["topics"][topic_name]["problems"][problem_id]
                problem["completed"] = False
                problem["solved_date"] = None
                
                # Update completed count
                total_completed = sum(
                    1 for p in self.progress_data["topics"][topic_name]["problems"].values() 
                    if p["completed"]
                )
                self.progress_data["topics"][topic_name]["completed_problems"] = total_completed
                
                self.save_progress()
                return True
        return False
    
    def get_topic_progress(self, topic_name):
        """Get progress for a specific topic"""
        if topic_name in self.progress_data["topics"]:
            topic = self.progress_data["topics"][topic_name]
            return {
                "topic_name": topic_name,
                "description": topic["description"],
                "total_problems": topic["total_problems"],
                "completed_problems": topic["completed_problems"],
                "completion_percentage": round((topic["completed_problems"] / topic["total_problems"]) * 100) if topic["total_problems"] > 0 else 0,
                "problems": topic["problems"]
            }
        return None
    
    def get_all_progress(self):
        """Get overall progress summary"""
        all_topics = self.progress_data["topics"]
        total_problems = sum(t["total_problems"] for t in all_topics.values())
        completed_problems = sum(t["completed_problems"] for t in all_topics.values())
        
        topic_summaries = []
        for topic_name, topic_data in all_topics.items():
            topic_summaries.append({
                "topic_name": topic_name,
                "total": topic_data["total_problems"],
                "completed": topic_data["completed_problems"],
                "percentage": round((topic_data["completed_problems"] / topic_data["total_problems"]) * 100) if topic_data["total_problems"] > 0 else 0
            })
        
        return {
            "overall_completion": round((completed_problems / total_problems) * 100) if total_problems > 0 else 0,
            "total_problems": total_problems,
            "completed_problems": completed_problems,
            "remaining_problems": total_problems - completed_problems,
            "user_info": self.progress_data["user_info"],
            "topics": topic_summaries
        }
    
    def add_revision(self, topic_name, problem_id):
        """Track revision count for a problem"""
        if topic_name in self.progress_data["topics"]:
            if problem_id in self.progress_data["topics"][topic_name]["problems"]:
                problem = self.progress_data["topics"][topic_name]["problems"][problem_id]
                problem["revisions"] += 1
                self.save_progress()
                return True
        return False
    
    def get_completed_problems_by_difficulty(self):
        """Get completed problems grouped by difficulty"""
        easy, medium, hard = [], [], []
        
        for topic_data in self.progress_data["topics"].values():
            for problem in topic_data["problems"].values():
                if problem["completed"]:
                    problem_info = {
                        "id": problem["id"],
                        "name": problem["name"],
                        "topic": topic_data["topic_name"],
                        "solved_date": problem["solved_date"],
                        "revisions": problem["revisions"]
                    }
                    
                    if problem["difficulty"] == "Easy":
                        easy.append(problem_info)
                    elif problem["difficulty"] == "Medium":
                        medium.append(problem_info)
                    else:
                        hard.append(problem_info)
        
        return {"easy": easy, "medium": medium, "hard": hard}
    
    def set_user_info(self, experience_level, study_duration_months):
        """Set user's learning profile"""
        self.progress_data["user_info"]["experience_level"] = experience_level
        self.progress_data["user_info"]["study_duration_months"] = study_duration_months
        self.save_progress()
    
    def get_uncompleted_problems_by_topic(self, topic_name):
        """Get all uncompleted problems in a topic"""
        if topic_name in self.progress_data["topics"]:
            topic = self.progress_data["topics"][topic_name]
            uncompleted = [
                p for p in topic["problems"].values() 
                if not p["completed"]
            ]
            return uncompleted
        return []
    
    def get_progress_by_difficulty(self):
        """Get progress statistics by difficulty level"""
        all_topics = self.progress_data["topics"]
        easy_total, easy_completed = 0, 0
        medium_total, medium_completed = 0, 0
        hard_total, hard_completed = 0, 0
        
        for topic_data in all_topics.values():
            for problem in topic_data["problems"].values():
                if problem["difficulty"] == "Easy":
                    easy_total += 1
                    if problem["completed"]:
                        easy_completed += 1
                elif problem["difficulty"] == "Medium":
                    medium_total += 1
                    if problem["completed"]:
                        medium_completed += 1
                else:
                    hard_total += 1
                    if problem["completed"]:
                        hard_completed += 1
        
        return {
            "easy": {
                "total": easy_total,
                "completed": easy_completed,
                "percentage": round((easy_completed / easy_total) * 100) if easy_total > 0 else 0
            },
            "medium": {
                "total": medium_total,
                "completed": medium_completed,
                "percentage": round((medium_completed / medium_total) * 100) if medium_total > 0 else 0
            },
            "hard": {
                "total": hard_total,
                "completed": hard_completed,
                "percentage": round((hard_completed / hard_total) * 100) if hard_total > 0 else 0
            }
        }

# Global progress tracker instance
progress_tracker = DSAProgressTracker()
