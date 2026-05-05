"""
api_client.py — Reusable HTTP client for NexusAI FastAPI backend.
Handles JWT Bearer authentication, error handling, and all endpoint calls.
Upgraded with Refresh Token support and Auto-rotation.
"""

import requests
from typing import Any
import os
import streamlit as st

# Environment-based Configuration
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
BASE_URL = BACKEND_URL.rstrip("/")
API_PREFIX = "/api/v1"


class NexusAPIError(Exception):
    """Custom exception for API errors."""
    pass


def _get_headers() -> dict[str, str]:
    """Build request headers with Bearer token if available."""
    headers = {"Content-Type": "application/json"}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _handle_response(response: requests.Response, retry_on_auth_fail: bool = True) -> Any:
    """Parse response and raise on error. Retries once if 401 using refresh token."""
    if response.status_code == 401 and retry_on_auth_fail:
        if st.session_state.get("refresh_token"):
            try:
                # Attempt to refresh
                refresh_access_token()
                # Retry original request (this is tricky since we don't have the original req params here easily)
                # For simplicity, we'll raise an error and expect the UI to rerun
                st.rerun()
            except Exception:
                # If refresh fails, logout
                logout()
                st.rerun()

    try:
        response.raise_for_status()
        return response.json()
    except requests.HTTPError as e:
        try:
            detail = response.json().get("detail", str(e))
        except Exception:
            detail = response.text or str(e)
        raise NexusAPIError(detail)
    except requests.RequestException as e:
        raise NexusAPIError(str(e))


# ── Auth ───────────────────────────────────────────────

def register(email: str, password: str, full_name: str) -> dict:
    """Register a new user."""
    payload = {"email": email, "password": password, "full_name": full_name}
    resp = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/register",
        json=payload,
        headers={"Content-Type": "application/json"},
        timeout=10,
    )
    return _handle_response(resp)


def login(email: str, password: str) -> dict:
    """Authenticate and return token payload."""
    resp = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        timeout=10,
    )
    data = _handle_response(resp)
    # Store tokens in session state
    st.session_state["access_token"] = data.get("access_token")
    st.session_state["refresh_token"] = data.get("refresh_token")
    st.session_state["token_type"] = data.get("token_type", "bearer")
    return data


def refresh_access_token():
    """Use refresh token to get a new access token."""
    refresh_token = st.session_state.get("refresh_token")
    if not refresh_token:
        raise NexusAPIError("No refresh token available")

    resp = requests.post(
        f"{BASE_URL}{API_PREFIX}/auth/refresh",
        params={"refresh_token": refresh_token},
        timeout=10,
    )
    data = _handle_response(resp, retry_on_auth_fail=False)
    st.session_state["access_token"] = data.get("access_token")
    return data


def get_me() -> dict:
    """Fetch current authenticated user."""
    resp = requests.get(
        f"{BASE_URL}{API_PREFIX}/auth/me",
        headers=_get_headers(),
        timeout=10,
    )
    data = _handle_response(resp)
    # Ensure consistent keys for frontend
    if "name" in data and "full_name" not in data:
        data["full_name"] = data["name"]
    # Normalize role to lowercase
    if "role" in data:
        data["role"] = data["role"].lower()
    return data


def update_user_preferences(preferences: dict) -> dict:
    """Update current user's preferences."""
    payload = {"preferences": preferences}
    resp = requests.patch(
        f"{BASE_URL}{API_PREFIX}/user/profile",
        json=payload,
        headers=_get_headers(),
        timeout=10,
    )
    return _handle_response(resp)


# ── Chat ───────────────────────────────────────────────

def send_chat(message: str, session_id: int = None, skip_routing: bool = False, system_prompt: str = None) -> dict:
    """Send a chat message to the AI."""
    payload = {"prompt": message, "skip_routing": skip_routing}
    if session_id:
        payload["session_id"] = session_id
    if system_prompt:
        payload["system_prompt"] = system_prompt
        
    resp = requests.post(
        f"{BASE_URL}{API_PREFIX}/chat/",
        json=payload,
        headers=_get_headers(),
        timeout=60,
    )
    return _handle_response(resp)


def get_chat_sessions() -> list[dict]:
    """Fetch all chat sessions for the user."""
    resp = requests.get(
        f"{BASE_URL}{API_PREFIX}/chat/sessions",
        headers=_get_headers(),
        timeout=10,
    )
    return _handle_response(resp)


def get_session_messages(session_id: int) -> list[dict]:
    """Fetch all messages for a specific session."""
    resp = requests.get(
        f"{BASE_URL}{API_PREFIX}/chat/{session_id}/messages",
        headers=_get_headers(),
        timeout=10,
    )
    return _handle_response(resp)


def get_dashboard_stats() -> dict:
    """Fetch user dashboard statistics."""
    resp = requests.get(
        f"{BASE_URL}{API_PREFIX}/dashboard/stats",
        headers=_get_headers(),
        timeout=10,
    )
    return _handle_response(resp)


# ── Files ──────────────────────────────────────────────

def get_files() -> list[dict]:
    """Fetch all files uploaded by the user."""
    resp = requests.get(
        f"{BASE_URL}{API_PREFIX}/files/list",
        headers=_get_headers(),
        timeout=10,
    )
    return _handle_response(resp)


def delete_file(file_id: int) -> dict:
    """Delete a specific file."""
    resp = requests.delete(
        f"{BASE_URL}{API_PREFIX}/files/{file_id}",
        headers=_get_headers(),
        timeout=10,
    )
    return _handle_response(resp)


def upload_file(file_bytes: bytes, filename: str, content_type: str, category: str = "general") -> dict:
    """Upload a file to the backend."""
    files = {"file": (filename, file_bytes, content_type)}
    data = {"category": category}
    
    headers = {}
    token = st.session_state.get("access_token")
    if token:
        headers["Authorization"] = f"Bearer {token}"
        
    resp = requests.post(
        f"{BASE_URL}{API_PREFIX}/files/upload",
        files=files,
        data=data,
        headers=headers,
        timeout=30,
    )
    return _handle_response(resp)


def query_docs(question: str, file_id: int = None) -> dict:
    """Ask a question about documents."""
    payload = {"question": question}
    if file_id:
        payload["file_id"] = file_id
        
    resp = requests.post(
        f"{BASE_URL}{API_PREFIX}/files/query",
        json=payload,
        headers=_get_headers(),
        timeout=60,
    )
    return _handle_response(resp)


# ── Admin ──────────────────────────────────────────────

def get_admin_dashboard() -> dict:
    """Fetch admin dashboard statistics."""
    resp = requests.get(
        f"{BASE_URL}{API_PREFIX}/admin/dashboard",
        headers=_get_headers(),
        timeout=10,
    )
    return _handle_response(resp)


def get_admin_users() -> list[dict]:
    """Fetch all users (admin only)."""
    resp = requests.get(
        f"{BASE_URL}{API_PREFIX}/admin/users",
        headers=_get_headers(),
        timeout=10,
    )
    return _handle_response(resp)


def logout():
    """Clear session state authentication."""
    keys_to_clear = [
        "access_token",
        "refresh_token",
        "token_type",
        "user",
        "chat_history",
    ]
    for key in keys_to_clear:
        st.session_state.pop(key, None)