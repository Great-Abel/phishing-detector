import streamlit as st
from services.auth_service import login, register, reset_password


def show_auth_page() -> None:
    st.markdown("""
<div class="hero">
    <h1>🛡️ Detektor Phishing URL</h1>
    <p>Login atau buat akun untuk mulai memeriksa URL.</p>
</div>
""", unsafe_allow_html=True)

    if "auth_page" not in st.session_state:
        st.session_state["auth_page"] = "login"

    col1, col2 = st.columns(2)
    with col1:
        if st.button(
            "🔑 Login", use_container_width=True,
            type="primary" if st.session_state["auth_page"] == "login" else "secondary",
        ):
            st.session_state["auth_page"] = "login"
            st.rerun()
    with col2:
        if st.button(
            "📝 Register", use_container_width=True,
            type="primary" if st.session_state["auth_page"] == "register" else "secondary",
        ):
            st.session_state["auth_page"] = "register"
            st.rerun()

    st.divider()

    if st.session_state["auth_page"] == "login":
        _login_form()
    elif st.session_state["auth_page"] == "register":
        _register_form()
    else:
        _forgot_form()


# ── Forms ──────────────────────────────────────────────────────────────────────

def _login_form() -> None:
    st.subheader("Login")

    with st.form("form_login", clear_on_submit=False):
        email     = st.text_input("Email", placeholder="email@contoh.com")
        password  = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

    # Link "Lupa Password?" — teks italic biru underline di kanan bawah
    _, col_link = st.columns([3, 1])
    with col_link:
        st.markdown("""
<style>
.link-forgot {
    display: block;
    text-align: right;
    color: #4a9eff;
    font-style: italic;
    font-size: 0.85rem;
    text-decoration: underline;
    cursor: pointer;
    background: none;
    border: none;
    padding: 0;
    margin-top: 4px;
}
.link-forgot:hover { color: #1a7de0; }
</style>
<a class="link-forgot" href="?auth=forgot" target="_self">Lupa Password?</a>
""", unsafe_allow_html=True)

    # Tangkap klik via query params
    params = st.query_params
    if params.get("auth") == "forgot":
        st.query_params.clear()
        st.session_state["auth_page"] = "forgot"
        st.rerun()

    # CSS: warnai tombol lupa password jadi merah kecil
    st.markdown("""
<style>
div[data-testid="stButton"]:has(button[kind="secondary"]#btn_forgot) button,
button[kind="secondary"][data-testid="baseButton-secondary"] {
    all: unset;
}
/* Target tombol Lupa Password? via key */
div[data-testid="column"]:last-child .stButton button {
    background: transparent !important;
    color: #ff4b4b !important;
    border: none !important;
    font-size: 0.82rem !important;
    padding: 0 !important;
    text-decoration: underline !important;
    cursor: pointer !important;
    box-shadow: none !important;
    width: auto !important;
    min-height: unset !important;
}
div[data-testid="column"]:last-child .stButton button:hover {
    color: #ff2222 !important;
    background: transparent !important;
}
</style>
""", unsafe_allow_html=True)

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


def _forgot_form() -> None:
    st.subheader("Lupa Password")
    st.caption("Masukkan email akunmu. Kami akan kirimkan link untuk reset password.")

    with st.form("form_forgot", clear_on_submit=True):
        email     = st.text_input("Email", placeholder="email@contoh.com")
        submitted = st.form_submit_button("Kirim Link Reset", use_container_width=True, type="primary")

    if submitted:
        if not email:
            st.warning("Masukkan email terlebih dahulu.")
            return
        with st.spinner("Mengirim email..."):
            ok, msg = reset_password(email)
        if ok:
            st.success(msg)
            st.info("Cek inbox atau folder spam kamu. Link berlaku selama 1 jam.")
        else:
            st.error(msg)
