import os
import streamlit as st
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY", "")


def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        st.error("❌ Konfigurasi Supabase belum diisi. Periksa file .env kamu.")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


# ── Session helpers ────────────────────────────────────────────────────────────

def is_logged_in() -> bool:
    return st.session_state.get("user") is not None


def get_current_user():
    return st.session_state.get("user")


def set_session(user):
    st.session_state["user"] = user


def clear_session():
    st.session_state["user"] = None
    st.session_state["auth_page"] = "login"


# ── Auth actions ───────────────────────────────────────────────────────────────

def register(email: str, password: str) -> tuple[bool, str]:
    """
    Daftarkan user baru lewat Supabase Auth.
    Supabase akan kirim email konfirmasi otomatis.
    Return (success: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password minimal 8 karakter."

    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })
        # sign_up sukses meski belum konfirmasi email
        if response.user:
            return True, "Registrasi berhasil! Cek email kamu untuk konfirmasi akun."
        return False, "Registrasi gagal. Coba lagi."
    except Exception as e:
        msg = str(e)
        if "already registered" in msg.lower() or "user already registered" in msg.lower():
            return False, "Email ini sudah terdaftar. Silakan login."
        return False, f"Error: {msg}"


def login(email: str, password: str) -> tuple[bool, str]:
    """
    Login user lewat Supabase Auth.
    Return (success: bool, message: str)
    """
    supabase = get_supabase_client()
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
        if response.user:
            set_session(response.user)
            return True, f"Selamat datang, {response.user.email}!"
        return False, "Login gagal. Periksa email dan password kamu."
    except Exception as e:
        msg = str(e)
        if "invalid login credentials" in msg.lower():
            return False, "Email atau password salah."
        if "email not confirmed" in msg.lower():
            return False, "Email belum dikonfirmasi. Cek inbox kamu."
        return False, f"Error: {msg}"


def logout():
    """Logout dan hapus session."""
    supabase = get_supabase_client()
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    clear_session()


# ── Audit Trail ────────────────────────────────────────────────────────────────

def save_audit(url: str, prediction: str, phishing_pct: float, legit_pct: float) -> tuple[bool, str]:
    """
    Simpan hasil scan URL ke tabel audit_trail di Supabase.
    Hanya dipanggil setelah URL tervalidasi sebagai URL yang benar.
    """
    user = get_current_user()
    if not user:
        return False, "User tidak terautentikasi."

    supabase = get_supabase_client()
    try:
        supabase.table("audit_trail").insert({
            "user_id":      user.id,
            "user_email":   user.email,
            "url":          url,
            "prediction":   prediction,
            "phishing_pct": round(phishing_pct, 2),
            "legit_pct":    round(legit_pct, 2),
        }).execute()
        return True, "Audit tersimpan."
    except Exception as e:
        return False, str(e)


def get_audit_trail(limit: int = 50) -> list[dict]:
    """
    Ambil riwayat scan milik user yang sedang login.
    Diurutkan dari yang terbaru, maksimal `limit` baris.
    """
    user = get_current_user()
    if not user:
        return []

    supabase = get_supabase_client()
    try:
        response = (
            supabase.table("audit_trail")
            .select("user_email, url, prediction, phishing_pct, legit_pct, scanned_at")
            .eq("user_id", user.id)
            .order("scanned_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception:
        return []


# ── UI ─────────────────────────────────────────────────────────────────────────

def show_auth_page():
    """
    Tampilkan halaman Login / Register.
    Dipanggil dari app.py saat user belum login.
    """
    st.title("🛡️ Detektor Phishing URL")

    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    col_login, col_register = st.columns(2)
    with col_login:
        if st.button("🔑 Login", use_container_width=True,
                     type="primary" if st.session_state["auth_page"] == "login" else "secondary"):
            st.session_state["auth_page"] = "login"
            st.rerun()
    with col_register:
        if st.button("📝 Register", use_container_width=True,
                     type="primary" if st.session_state["auth_page"] == "register" else "secondary"):
            st.session_state["auth_page"] = "register"
            st.rerun()

    st.divider()

    if st.session_state["auth_page"] == "login":
        _show_login_form()
    else:
        _show_register_form()


def _show_login_form():
    st.subheader("Login")
    with st.form("form_login", clear_on_submit=False):
        email = st.text_input("Email", placeholder="email@contoh.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

    if submitted:
        if not email or not password:
            st.warning("Email dan password tidak boleh kosong.")
            return
        with st.spinner("Memverifikasi..."):
            success, message = login(email, password)
        if success:
            st.success(message)
            st.rerun()
        else:
            st.error(message)


def _show_register_form():
    st.subheader("Buat Akun Baru")
    with st.form("form_register", clear_on_submit=True):
        email = st.text_input("Email", placeholder="email@contoh.com")
        password = st.text_input("Password", type="password",
                                 placeholder="Minimal 8 karakter")
        confirm = st.text_input("Konfirmasi Password", type="password",
                                placeholder="Ulangi password")
        submitted = st.form_submit_button("Daftar", use_container_width=True, type="primary")

    if submitted:
        if not email or not password or not confirm:
            st.warning("Semua kolom harus diisi.")
            return
        if password != confirm:
            st.error("Password dan konfirmasi password tidak cocok.")
            return
        with st.spinner("Mendaftarkan akun..."):
            success, message = register(email, password)
        if success:
            st.success(message)
            st.info("Silakan login setelah mengkonfirmasi email kamu.")
            st.session_state["auth_page"] = "login"
            st.rerun()
        else:
            st.error(message)
