import json
import os
from datetime import datetime, date, timedelta
from agents.dsa.dsa_topics_db import DSA_TOPICS_MAP

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
                # Migrate top-level keys added in newer versions
                data.setdefault("streak", {"current": 0, "longest": 0, "last_active_date": None})
                data.setdefault("daily_log", {})
                data.setdefault("topics", {})

                # Sync topics and problems from the canonical db.
                # This handles: new topics, new problems added to existing topics,
                # and problems removed/renamed in the db (old keys are kept intact
                # so existing completion data is never lost).
                for topic_name, topic_db in DSA_TOPICS_MAP.items():
                    if topic_name not in data["topics"]:
                        # Brand-new topic — add it fresh
                        data["topics"][topic_name] = {
                            "topic_name": topic_name,
                            "description": topic_db["description"],
                            "total_problems": len(topic_db["problems"]),
                            "completed_problems": 0,
                            "problems": {},
                        }
                    else:
                        # Existing topic — update metadata
                        data["topics"][topic_name]["topic_name"] = topic_name
                        data["topics"][topic_name]["description"] = topic_db["description"]

                    saved_problems = data["topics"][topic_name].setdefault("problems", {})

                    # Add any problem that exists in the db but not in the saved file
                    for problem in topic_db["problems"]:
                        pid = problem["id"]
                        if pid not in saved_problems:
                            saved_problems[pid] = {
                                "id": pid,
                                "name": problem["name"],
                                "difficulty": problem["difficulty"],
                                "leetcode_link": problem["leetcode_link"],
                                "completed": False,
                                "solved_date": None,
                                "time_spent_mins": 0,
                                "notes": "",
                                "revisions": 0,
                            }

                    # Keep total_problems in sync with the db (source of truth)
                    data["topics"][topic_name]["total_problems"] = len(topic_db["problems"])
                    # Recount completed (in case new problems were inserted)
                    data["topics"][topic_name]["completed_problems"] = sum(
                        1 for p in saved_problems.values() if p.get("completed")
                    )

                self.save_progress_data(data)
                return data
            except Exception:
                return self._initialize_progress()
        return self._initialize_progress()

    def save_progress_data(self, data: dict):
        """Write arbitrary progress dict to disk (used during migration)."""
        with open(PROGRESS_FILE, "w") as f:
            json.dump(data, f, indent=2)

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


# Global singleton
progress_tracker = DSAProgressTracker()