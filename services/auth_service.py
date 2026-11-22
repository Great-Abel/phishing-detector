import streamlit as st
from supabase import create_client, Client
from config.settings import (
    SUPABASE_URL, SUPABASE_ANON_KEY,
    MIN_PASSWORD_LENGTH, validate_config,
)


# ── Supabase client ────────────────────────────────────────────────────────────

@st.cache_resource
def get_client() -> Client:
    missing = validate_config()
    if missing:
        st.error(f"❌ ENV vars belum diisi: {', '.join(missing)}. Periksa file .env kamu.")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# ── Session ────────────────────────────────────────────────────────────────────

def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def get_current_user():
    return st.session_state.get("user")


def _set_session(user) -> None:
    st.session_state["user"] = user


def clear_session() -> None:
    st.session_state["user"] = None
    st.session_state["auth_page"] = "login"


# ── Auth actions ───────────────────────────────────────────────────────────────

def register(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password minimal {MIN_PASSWORD_LENGTH} karakter."

    try:
        response = get_client().auth.sign_up({"email": email, "password": password})
        if response.user:
            return True, "Registrasi berhasil! Cek email untuk konfirmasi akun."
        return False, "Registrasi gagal. Coba lagi."
    except Exception as e:
        msg = str(e).lower()
        if "already registered" in msg or "user already registered" in msg:
            return False, "Email ini sudah terdaftar. Silakan login."
        return False, f"Error: {e}"


def login(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()

    try:
        response = get_client().auth.sign_in_with_password({"email": email, "password": password})
        if response.user:
            _set_session(response.user)
            return True, f"Selamat datang, {response.user.email}!"
        return False, "Login gagal. Periksa email dan password kamu."
    except Exception as e:
        msg = str(e).lower()
        if "invalid login credentials" in msg:
            return False, "Email atau password salah."
        if "email not confirmed" in msg:
            return False, "Email belum dikonfirmasi. Cek inbox kamu."
        return False, f"Error: {e}"


def logout() -> None:
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    clear_session()
