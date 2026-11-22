import streamlit as st
from supabase import create_client, Client
from config.settings import (
    SUPABASE_URL, SUPABASE_ANON_KEY,
    MIN_PASSWORD_LENGTH, validate_config
)
from services import rate_limiter


# ── Supabase client (singleton per session) ────────────────────────────────────

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
    """
    Daftarkan user baru lewat Supabase Auth.
    Supabase kirim email konfirmasi otomatis.
    """
    email = email.strip().lower()

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password minimal {MIN_PASSWORD_LENGTH} karakter."

    try:
        response = get_client().auth.sign_up({
            "email": email,
            "password": password,
        })
        if response.user:
            return True, "Registrasi berhasil! Cek email untuk konfirmasi akun."
        return False, "Registrasi gagal. Coba lagi."
    except Exception as e:
        msg = str(e).lower()
        if "already registered" in msg or "user already registered" in msg:
            return False, "Email ini sudah terdaftar. Silakan login."
        return False, f"Error: {e}"


def login(email: str, password: str) -> tuple[bool, str]:
    """
    Login user lewat Supabase Auth.
    Dilindungi rate limiter Upstash Redis — maks 5x gagal, kunci 60 detik.
    """
    email = email.strip().lower()

    # Cek rate limit per email
    locked, sisa = rate_limiter.is_locked(email)
    if locked:
        return False, f"🔒 Terlalu banyak percobaan. Coba lagi dalam {sisa} detik."

    try:
        response = get_client().auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        if response.user:
            rate_limiter.reset(email)
            _set_session(response.user)
            return True, f"Selamat datang, {response.user.email}!"
        rate_limiter.record_failed(email)
        return False, "Login gagal. Periksa email dan password kamu."
    except Exception as e:
        msg = str(e).lower()
        if "invalid login credentials" in msg:
            rate_limiter.record_failed(email)
            sisa_coba = rate_limiter.remaining_attempts(email)
            if sisa_coba > 0:
                return False, f"Email atau password salah. Sisa percobaan: {sisa_coba}x"
            return False, "🔒 Terlalu banyak percobaan. Coba lagi dalam 60 detik."
        if "email not confirmed" in msg:
            return False, "Email belum dikonfirmasi. Cek inbox kamu."
        rate_limiter.record_failed(email)
        return False, f"Error: {e}"


def logout() -> None:
    """Logout dan hapus session."""
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    clear_session()
