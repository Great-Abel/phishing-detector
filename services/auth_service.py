import time
import streamlit as st
from supabase import create_client, Client
from config.settings import (
    SUPABASE_URL, SUPABASE_ANON_KEY,
    MIN_PASSWORD_LENGTH, validate_config
)

# ── Rate limiter constants ─────────────────────────────────────────────────────
_MAX_ATTEMPTS   = 5     # maks percobaan gagal
_COOLDOWN_SECS  = 60    # cooldown dalam detik setelah maks tercapai


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


# ── Rate limiter ───────────────────────────────────────────────────────────────

def _init_rate_limiter() -> None:
    """Inisialisasi state rate limiter kalau belum ada."""
    if "login_attempts" not in st.session_state:
        st.session_state["login_attempts"] = 0
    if "login_locked_until" not in st.session_state:
        st.session_state["login_locked_until"] = 0.0


def is_login_locked() -> tuple[bool, int]:
    """
    Cek apakah login sedang dikunci.
    Return (locked: bool, sisa_detik: int)
    """
    _init_rate_limiter()
    now = time.time()
    locked_until = st.session_state["login_locked_until"]
    if locked_until > now:
        return True, int(locked_until - now)
    return False, 0


def _record_failed_attempt() -> None:
    """Catat satu percobaan login gagal, kunci kalau sudah melebihi batas."""
    _init_rate_limiter()
    st.session_state["login_attempts"] += 1
    if st.session_state["login_attempts"] >= _MAX_ATTEMPTS:
        st.session_state["login_locked_until"] = time.time() + _COOLDOWN_SECS
        st.session_state["login_attempts"] = 0  # reset counter setelah dikunci


def _reset_attempts() -> None:
    """Reset counter setelah login berhasil."""
    st.session_state["login_attempts"] = 0
    st.session_state["login_locked_until"] = 0.0


def remaining_attempts() -> int:
    """Sisa percobaan sebelum dikunci."""
    _init_rate_limiter()
    return max(0, _MAX_ATTEMPTS - st.session_state["login_attempts"])


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
    Dilindungi rate limiter — maks 5 kali gagal, lalu kena cooldown 60 detik.
    """
    # Cek rate limit sebelum proses
    locked, sisa = is_login_locked()
    if locked:
        return False, f"🔒 Terlalu banyak percobaan. Coba lagi dalam {sisa} detik."

    email = email.strip().lower()

    try:
        response = get_client().auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        if response.user:
            _reset_attempts()
            _set_session(response.user)
            return True, f"Selamat datang, {response.user.email}!"
        _record_failed_attempt()
        return False, "Login gagal. Periksa email dan password kamu."
    except Exception as e:
        msg = str(e).lower()
        if "invalid login credentials" in msg:
            _record_failed_attempt()
            sisa_coba = remaining_attempts()
            if sisa_coba > 0:
                return False, f"Email atau password salah. Sisa percobaan: {sisa_coba}x"
            return False, f"🔒 Terlalu banyak percobaan. Coba lagi dalam {_COOLDOWN_SECS} detik."
        if "email not confirmed" in msg:
            return False, "Email belum dikonfirmasi. Cek inbox kamu."
        _record_failed_attempt()
        return False, f"Error: {e}"


def logout() -> None:
    """Logout dan hapus session."""
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    clear_session()
