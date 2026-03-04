import json
import os
import hashlib
import re
from datetime import datetime

USERS_FILE = "data/users.json"


def _load_users():
    os.makedirs("data", exist_ok=True)

    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except json.JSONDecodeError:
        # Reset corrupted file
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({}, f)
        return {}


def _save_users(users):
    os.makedirs("data", exist_ok=True)
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2, ensure_ascii=False)


def _hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _is_valid_email(email):
    return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email) is not None


def signup_user(username, email, password, confirm_password):
    """
    Returns (success: bool, message: str)
    """
    # ── Validations ───────────────────────────────────────────────────────────
    if not username or not email or not password or not confirm_password:
        return False, "All fields are required."

    username = username.strip()
    email    = email.strip()

    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    if not _is_valid_email(email):
        return False, "Enter a valid email address."

    if len(password) < 6:
        return False, "Password must be at least 6 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    # ── Check duplicates ──────────────────────────────────────────────────────
    users = _load_users()

    for uid, data in users.items():
        if data["username"].lower() == username.lower():
            return False, "Username already taken. Please choose another."
        if data["email"].lower() == email.lower():
            return False, "Email already registered. Please login instead."

    # ── Create user ───────────────────────────────────────────────────────────
    user_id = f"user_{len(users) + 1}_{int(datetime.now().timestamp())}"

    users[user_id] = {
        "user_id":    user_id,
        "username":   username,
        "email":      email,
        "password":   _hash_password(password),
        "created_at": datetime.now().isoformat(),
        "gen_count":  0,
    }

    _save_users(users)
    return True, f"Account created successfully! Welcome, {username} 🎉"


def login_user(email_or_username, password):
    """
    Returns (success: bool, message: str, user_data: dict | None)
    """
    if not email_or_username or not password:
        return False, "All fields are required.", None

    email_or_username = email_or_username.strip()
    hashed            = _hash_password(password)
    users             = _load_users()

    for uid, data in users.items():
        match_email    = data["email"].lower()    == email_or_username.lower()
        match_username = data["username"].lower() == email_or_username.lower()

        if match_email or match_username:
            if data["password"] == hashed:
                return True, f"Welcome back, {data['username']}! 👋", data
            else:
                return False, "Incorrect password. Please try again.", None

    return False, "No account found with that email or username.", None


def update_gen_count(user_id):
    """
    Increments generation count for a user after each image generation
    """
    users = _load_users()

    if user_id in users:
        users[user_id]["gen_count"] = users[user_id].get("gen_count", 0) + 1
        _save_users(users)


def get_user_by_id(user_id):
    """
    Returns user data dict or None
    """
    users = _load_users()
    return users.get(user_id, None)


def update_password(user_id, old_password, new_password):
    """
    Returns (success: bool, message: str)
    """
    if not old_password or not new_password:
        return False, "All fields are required."

    if len(new_password) < 6:
        return False, "New password must be at least 6 characters."

    users = _load_users()

    if user_id not in users:
        return False, "User not found."

    if users[user_id]["password"] != _hash_password(old_password):
        return False, "Old password is incorrect."

    users[user_id]["password"] = _hash_password(new_password)
    _save_users(users)
    return True, "Password updated successfully! ✅"


def delete_account(user_id, password):
    """
    Returns (success: bool, message: str)
    """
    users = _load_users()

    if user_id not in users:
        return False, "User not found."

    if users[user_id]["password"] != _hash_password(password):
        return False, "Incorrect password."

    del users[user_id]
    _save_users(users)
    return True, "Account deleted successfully."


def get_all_users_count():
    """
    Returns total number of registered users
    """
    return len(_load_users())
