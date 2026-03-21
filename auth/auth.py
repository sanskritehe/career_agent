"""
auth/auth.py
------------
Authentication logic — register, login, password hashing with bcrypt.
"""

import bcrypt
import re
from utils.database import (
    create_user,
    get_user_by_username,
    get_user_by_email,
    update_last_login,
    username_exists,
    email_exists,
)


# ── Password helpers ──────────────────────────────────────────────────────────

def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))


# ── Validation ────────────────────────────────────────────────────────────────

def _valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))


def _valid_username(username: str) -> bool:
    # 3-30 chars, letters/numbers/underscores only
    return bool(re.match(r"^\w{3,30}$", username))


def _strong_password(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""


# ── Public API ────────────────────────────────────────────────────────────────

def register_user(username: str, email: str, password: str, full_name: str = "") -> tuple[bool, str]:
    """
    Register a new user.
    Returns (success: bool, message: str).
    """
    username = username.strip().lower()
    email    = email.strip().lower()

    if not _valid_username(username):
        return False, "Username must be 3-30 characters and contain only letters, numbers, or underscores."

    if not _valid_email(email):
        return False, "Please enter a valid email address."

    ok, msg = _strong_password(password)
    if not ok:
        return False, msg

    if username_exists(username):
        return False, "That username is already taken. Please choose another."

    if email_exists(email):
        return False, "An account with this email already exists. Try logging in."

    try:
        hashed = hash_password(password)
        create_user(username, email, hashed, full_name)
        return True, "Account created successfully!"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def login_user(username_or_email: str, password: str) -> tuple[bool, str, dict | None]:
    """
    Log in with username or email.
    Returns (success: bool, message: str, user_dict | None).
    """
    val = username_or_email.strip().lower()

    # Try username first, then email
    user = get_user_by_username(val) or get_user_by_email(val)

    if not user:
        return False, "No account found with that username or email.", None

    if not verify_password(password, user["password_hash"]):
        return False, "Incorrect password. Please try again.", None

    update_last_login(user["id"])
    return True, f"Welcome back, {user['full_name'] or user['username']}!", user