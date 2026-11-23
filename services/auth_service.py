import streamlit as st
from supabase import create_client, Client
from config.settings import SUPABASE_URL, SUPABASE_ANON_KEY, MIN_PASSWORD_LENGTH, validate_config
from services import rate_limiter


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


# ── Auth ───────────────────────────────────────────────────────────────────────

def register(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()

    if len(password) < MIN_PASSWORD_LENGTH:
        return False, f"Password minimal {MIN_PASSWORD_LENGTH} karakter."

    try:
        res = get_client().auth.sign_up({"email": email, "password": password})
        if res.user:
            return True, "Registrasi berhasil! Cek email untuk konfirmasi akun."
        return False, "Registrasi gagal. Coba lagi."
    except Exception as e:
        msg = str(e).lower()
        if "already registered" in msg or "user already registered" in msg:
            return False, "Email ini sudah terdaftar. Silakan login."
        return False, f"Error: {e}"


def login(email: str, password: str) -> tuple[bool, str]:
    email = email.strip().lower()

    # 1. Cek apakah sedang dikunci
    locked, sisa = rate_limiter.is_locked(email)
    if locked:
        return False, f"🔒 Akun dikunci. Coba lagi dalam {sisa} detik."

    # 2. Proses login
    try:
        res = get_client().auth.sign_in_with_password({"email": email, "password": password})

        if res.user:
            rate_limiter.reset(email)
            _set_session(res.user)
            return True, f"Selamat datang, {res.user.email}!"

        # Gagal tanpa exception
        sisa_coba = rate_limiter.record_fail(email)
        return False, _fail_message(sisa_coba)

    except Exception as e:
        msg = str(e).lower()

        if "invalid login credentials" in msg:
            sisa_coba = rate_limiter.record_fail(email)
            return False, _fail_message(sisa_coba)

        if "email not confirmed" in msg:
            return False, "Email belum dikonfirmasi. Cek inbox kamu."

        return False, f"Error: {e}"


def logout() -> None:
    try:
        get_client().auth.sign_out()
    except Exception:
        pass
    clear_session()


def reset_password(email: str) -> tuple[bool, str]:
    """Kirim email reset password via Supabase Auth dengan rate limiter."""
    email = email.strip().lower()
    if not email:
        return False, "Email tidak boleh kosong."

    # Cek rate limit per email (maks 2x per jam)
    locked, sisa = rate_limiter.is_reset_locked(email)
    if locked:
        menit = sisa // 60
        return False, f"⏳ Sudah terlalu banyak permintaan. Coba lagi dalam {menit} menit."

    try:
        get_client().auth.reset_password_for_email(
            email,
            options={"redirect_to": "https://great-abel.github.io/phishing-detector/"}
        )
        # Catat pengiriman
        rate_limiter.record_reset(email)
        return True, "Link reset password telah dikirim ke email kamu."
    except Exception as e:
        msg = str(e).lower()
        if "rate limit" in msg or "email rate limit" in msg:
            # Paksa kunci supaya tidak bisa coba lagi
            rate_limiter.record_reset(email)
            return False, "⏳ Terlalu banyak permintaan email. Coba lagi dalam 1 jam."
        return False, "Gagal mengirim email. Coba lagi nanti."


def update_password(new_password: str) -> tuple[bool, str]:
    """Update password user yang sedang dalam sesi recovery."""
    if len(new_password) < MIN_PASSWORD_LENGTH:
        return False, f"Password minimal {MIN_PASSWORD_LENGTH} karakter."
    try:
        get_client().auth.update_user({"password": new_password})
        return True, "Password berhasil diperbarui! Silakan login."
    except Exception as e:
        return False, f"Error: {e}"


def exchange_recovery_token(access_token: str, refresh_token: str) -> tuple[bool, str]:
    """Tukar token recovery (implicit flow) jadi sesi aktif."""
    try:
        res = get_client().auth.set_session(access_token, refresh_token)
        if res.user:
            _set_session(res.user)
            return True, "Token valid."
        return False, "Token tidak valid atau sudah kadaluarsa."
    except Exception as e:
        return False, f"Token error: {e}"


def exchange_pkce_code(code: str) -> tuple[bool, str]:
    """Tukar PKCE code (flow terbaru Supabase) jadi sesi aktif."""
    try:
        res = get_client().auth.exchange_code_for_session({"auth_code": code})
        if res.user:
            _set_session(res.user)
            return True, "Code valid."
        return False, "Code tidak valid atau sudah kadaluarsa."
    except Exception as e:
        return False, f"Code error: {e}"


# ── Helper ─────────────────────────────────────────────────────────────────────

def _fail_message(sisa_coba: int) -> str:
    """Satu pesan konsisten berdasarkan sisa percobaan."""
    if sisa_coba == 0:
        return f"🔒 Terlalu banyak percobaan. Akun dikunci {rate_limiter.COOLDOWN_SECS} detik."
    if sisa_coba == 1:
        return f"Email atau password salah. ⚠️ Sisa {sisa_coba} percobaan terakhir!"
    return f"Email atau password salah. Sisa {sisa_coba} percobaan."
