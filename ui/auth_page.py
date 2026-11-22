import streamlit as st
from services.auth_service import login, register


def show_auth_page() -> None:
    st.markdown("""
<div class="hero">
    <h1>🛡️ Detektor Phishing URL</h1>
    <p>Login atau buat akun untuk mulai memeriksa URL.</p>
</div>
""", unsafe_allow_html=True)

    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    col_login, col_register = st.columns(2)
    with col_login:
        if st.button(
            "🔑 Login", use_container_width=True,
            type="primary" if st.session_state["auth_page"] == "login" else "secondary",
        ):
            st.session_state["auth_page"] = "login"
            st.rerun()
    with col_register:
        if st.button(
            "📝 Register", use_container_width=True,
            type="primary" if st.session_state["auth_page"] == "register" else "secondary",
        ):
            st.session_state["auth_page"] = "register"
            st.rerun()

    st.divider()

    if st.session_state["auth_page"] == "login":
        _login_form()
    else:
        _register_form()


# ── Forms ──────────────────────────────────────────────────────────���───────────

def _login_form() -> None:
    st.subheader("Login")

    with st.form("form_login", clear_on_submit=False):
        email     = st.text_input("Email", placeholder="email@contoh.com")
        password  = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

    if submitted:
        if not email or not password:
            st.warning("Email dan password tidak boleh kosong.")
            return
        with st.spinner("Memverifikasi..."):
            ok, msg = login(email, password)
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


def _register_form() -> None:
    st.subheader("Buat Akun Baru")

    with st.form("form_register", clear_on_submit=True):
        email     = st.text_input("Email", placeholder="email@contoh.com")
        password  = st.text_input("Password", type="password", placeholder="Minimal 8 karakter")
        confirm   = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password")
        submitted = st.form_submit_button("Daftar", use_container_width=True, type="primary")

    if submitted:
        if not email or not password or not confirm:
            st.warning("Semua kolom harus diisi.")
            return
        if password != confirm:
            st.error("Password dan konfirmasi tidak cocok.")
            return
        with st.spinner("Mendaftarkan akun..."):
            ok, msg = register(email, password)
        if ok:
            st.success(msg)
            st.info("Silakan login setelah mengkonfirmasi email kamu.")
            st.session_state["auth_page"] = "login"
            st.rerun()
        else:
            st.error(msg)
