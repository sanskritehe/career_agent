"""
utils/database.py
-----------------
MySQL database connection and schema management.

Tables:
  users               — login credentials + profile
  interview_sessions  — history of completed mock interview sessions
  resume_history      — saved resume analysis results

DSA progress is intentionally kept in dsa_progress.json (unchanged).
"""

import os
import mysql.connector
from mysql.connector import pooling
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

_pool = None


def _get_pool():
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="career_ai_pool",
            pool_size=5,
            host=os.getenv("MYSQL_HOST", "localhost"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER", "root"),
            password=os.getenv("MYSQL_PASSWORD", ""),
            database=os.getenv("MYSQL_DATABASE", "career_ai"),
            autocommit=True,
        )
    return _pool


def get_connection():
    return _get_pool().get_connection()


def init_db():
    """Create all tables if they don't exist. Safe to call on every startup."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            username         VARCHAR(50)  UNIQUE NOT NULL,
            email            VARCHAR(100) UNIQUE NOT NULL,
            password_hash    VARCHAR(255) NOT NULL,
            full_name        VARCHAR(100) DEFAULT '',
            target_role      VARCHAR(100) DEFAULT '',
            experience_level VARCHAR(20)  DEFAULT 'Beginner',
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_login       DATETIME,
            INDEX idx_username (username),
            INDEX idx_email    (email)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interview_sessions (
            id                INT AUTO_INCREMENT PRIMARY KEY,
            user_id           INT NOT NULL,
            role              VARCHAR(100),
            interview_type    VARCHAR(50),
            difficulty        VARCHAR(30),
            overall_score     FLOAT,
            overall_grade     VARCHAR(30),
            readiness_verdict VARCHAR(30),
            num_questions     INT,
            session_data      LONGTEXT,
            created_at        DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_sessions (user_id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resume_history (
            id               INT AUTO_INCREMENT PRIMARY KEY,
            user_id          INT NOT NULL,
            target_role      VARCHAR(100),
            experience_level VARCHAR(30),
            skills_present   TEXT,
            summary          TEXT,
            match_score      FLOAT DEFAULT 0,
            analysis_data    LONGTEXT,
            created_at       DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_resume (user_id)
        )
    """)

    cursor.close()
    conn.close()


# ── User CRUD ─────────────────────────────────────────────────────────────────

def create_user(username: str, email: str, password_hash: str, full_name: str = "") -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, full_name) VALUES (%s, %s, %s, %s)",
        (username.strip().lower(), email.strip().lower(), password_hash, full_name.strip()),
    )
    user_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return user_id


def get_user_by_username(username: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username.strip().lower(),))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def get_user_by_email(email: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email.strip().lower(),))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


def update_last_login(user_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET last_login = %s WHERE id = %s", (datetime.now(), user_id))
    cursor.close()
    conn.close()


def update_user_profile(user_id: int, full_name: str = None, target_role: str = None, experience_level: str = None):
    fields, vals = [], []
    if full_name        is not None: fields.append("full_name = %s");        vals.append(full_name)
    if target_role      is not None: fields.append("target_role = %s");      vals.append(target_role)
    if experience_level is not None: fields.append("experience_level = %s"); vals.append(experience_level)
    if not fields:
        return
    vals.append(user_id)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE id = %s", vals)
    cursor.close()
    conn.close()


def username_exists(username: str) -> bool:
    return get_user_by_username(username) is not None


def email_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


# ── Interview sessions ────────────────────────────────────────────────────────

def save_interview_session(user_id: int, session_summary: dict, config: dict, qa_pairs: list):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO interview_sessions
            (user_id, role, interview_type, difficulty, overall_score,
            overall_grade, readiness_verdict, num_questions)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        config.get("role", ""),
        config.get("type", ""),
        config.get("difficulty", ""),
        float(session_summary.get("overall_score", 0)),
        session_summary.get("overall_grade", ""),
        session_summary.get("readiness_verdict", ""),
        int(config.get("num_questions", 0)),
    ))
    cursor.close()
    conn.close()


def get_interview_history(user_id: int, limit: int = 10) -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, role, interview_type, difficulty, overall_score,
               overall_grade, readiness_verdict, num_questions, created_at
        FROM interview_sessions
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# ── Resume history ────────────────────────────────────────────────────────────

def save_resume_analysis(user_id: int, target_role: str, analysis_data: dict, match_score: float = 0):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO resume_history
            (user_id, target_role, experience_level, skills_present, summary, match_score)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        user_id,
        target_role,
        analysis_data.get("experience_level", ""),
        ", ".join(analysis_data.get("skills_present", [])),
        analysis_data.get("summary", ""),
        float(match_score),
    ))
    cursor.close()
    conn.close()


def get_resume_history(user_id: int, limit: int = 5) -> list:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT id, target_role, experience_level, skills_present,
               summary, match_score, created_at
        FROM resume_history
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
    """, (user_id, limit))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows


# ── Dashboard stats ───────────────────────────────────────────────────────────

def get_user_stats(user_id: int) -> dict:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT COUNT(*) AS total_sessions,
               ROUND(AVG(overall_score), 1) AS avg_score,
               MAX(overall_score) AS best_score
        FROM interview_sessions WHERE user_id = %s
    """, (user_id,))
    interview = cursor.fetchone()

    cursor.execute(
        "SELECT COUNT(*) AS total FROM resume_history WHERE user_id = %s",
        (user_id,),
    )
    resume = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "interview_sessions":   int(interview["total_sessions"] or 0),
        "interview_avg_score":  float(interview["avg_score"] or 0),
        "interview_best_score": float(interview["best_score"] or 0),
        "resume_analyses":      int(resume["total"] or 0),
    }
print("MYSQL_PASSWORD:", os.getenv("MYSQL_PASSWORD"))