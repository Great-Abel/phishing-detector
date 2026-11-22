import streamlit as st
from services.auth_service import login, register
from services.rate_limiter import is_locked_email, is_locked_ip, remaining_attempts


def _get_client_ip() -> str:
    """
    Ambil IP client dari header HTTP.
    Pakai st.context.headers (API resmi Streamlit 1.37+).
    Prioritas: X-Forwarded-For → fallback 'unknown'.
    """
    try:
        headers = st.context.headers
        forwarded = headers.get("X-Forwarded-For") or headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    except Exception:
        pass
    return "unknown"


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


# ── Forms ──────────────────────────────────────────────────────────────────────

def _login_form() -> None:
    st.subheader("Login")

    # Cek IP lock sebelum form ditampilkan
    ip = _get_client_ip()
    locked_ip, sisa_ip = is_locked_ip(ip)
    if locked_ip:
        menit = sisa_ip // 60
        detik = sisa_ip % 60
        waktu = f"{menit} menit {detik} detik" if menit > 0 else f"{detik} detik"
        st.error(
            "🚫 Akses Login Diblokir Sementara\n\n"
            f"Terlalu banyak percobaan login gagal dari jaringan kamu. "
            f"Sebagai langkah keamanan, akses login dinonaktifkan selama **{waktu}**.\n\n"
            "Jika ini bukan kamu, kemungkinan ada yang mencoba mengakses akun dari jaringan ini. "
            "Pastikan password kamu aman."
        )
        st.info("💡 Sudah menunggu cukup lama? Muat ulang halaman untuk mencoba kembali.")
        return

    with st.form("form_login", clear_on_submit=False):
        email    = st.text_input("Email", placeholder="email@contoh.com")
        password = st.text_input("Password", type="password", placeholder="••••••••")
        submitted = st.form_submit_button("Login", use_container_width=True, type="primary")

    if submitted:
        if not email or not password:
            st.warning("Email dan password tidak boleh kosong.")
            return

        clean_email = email.strip().lower()

        # Cek email lock
        locked_email, sisa_email = is_locked_email(clean_email)
        if locked_email:
            menit = sisa_email // 60
            detik = sisa_email % 60
            waktu = f"{menit} menit {detik} detik" if menit > 0 else f"{detik} detik"
            st.error(
                "🔒 Akun Dikunci Sementara\n\n"
                f"Terlalu banyak percobaan login yang gagal untuk akun ini. "
                f"Akun dikunci selama **{waktu}** untuk melindungi keamananmu.\n\n"
                "Jika kamu lupa password, gunakan fitur **Lupa Password** melalui Supabase."
            )
            return

        # Tampilkan sisa percobaan
        sisa_coba = remaining_attempts(clean_email)
        if sisa_coba == 4:
            st.warning("⚠️ Password salah. Kamu punya **4 percobaan lagi** sebelum akun dikunci 60 detik.")
        elif sisa_coba == 3:
            st.warning("⚠️ Password salah. Tersisa **3 percobaan** sebelum akun dikunci.")
        elif sisa_coba == 2:
            st.warning("⚠️ Hati-hati! Hanya tersisa **2 percobaan** lagi.")
        elif sisa_coba == 1:
            st.warning("🚨 Peringatan! Ini percobaan **terakhirmu**. Gagal lagi = akun dikunci 60 detik.")

        with st.spinner("Memverifikasi..."):
            ok, msg = login(email, password, ip=ip)
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


def _register_form() -> None:
    st.subheader("Buat Akun Baru")
    with st.form("form_register", clear_on_submit=True):
        email    = st.text_input("Email", placeholder="email@contoh.com")
        password = st.text_input("Password", type="password", placeholder="Minimal 8 karakter")
        confirm  = st.text_input("Konfirmasi Password", type="password", placeholder="Ulangi password")
        submitted = st.form_submit_button("Daftar", use_container_width=True, type="primary")

    if submitted:
        if not email or not password or not confirm:
            st.warning("Semua kolom harus diisi.")
            return
        if password != confirm:
            st.error("Password dan konfirmasi password tidak cocok.")
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
