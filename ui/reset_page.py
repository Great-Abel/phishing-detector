import streamlit as st
from services.auth_service import exchange_recovery_token, exchange_pkce_code, update_password, clear_session


def show_reset_page(access_token: str, refresh_token: str, pkce_code: str = "") -> None:
    st.markdown("""
<div class="hero">
    <h1>🛡️ Detektor Phishing URL</h1>
    <p>Buat password baru untuk akunmu.</p>
</div>
""", unsafe_allow_html=True)

    # Tukar token/code jadi sesi aktif — hanya sekali
    if not st.session_state.get("recovery_verified"):
        with st.spinner("Memverifikasi link..."):
            if pkce_code:
                ok, msg = exchange_pkce_code(pkce_code)
            else:
                ok, msg = exchange_recovery_token(access_token, refresh_token)

        if not ok:
            st.error("❌ Link tidak valid atau sudah kadaluarsa. Silakan minta link baru.")
            if st.button("Kembali ke Login"):
                st.query_params.clear()
                st.rerun()
            return

        st.session_state["recovery_verified"] = True

    st.subheader("🔑 Buat Password Baru")

    with st.form("form_reset_password", clear_on_submit=True):
        new_password = st.text_input("Password Baru", type="password", placeholder="Minimal 8 karakter")
        confirm      = st.text_input("Konfirmasi Password Baru", type="password", placeholder="Ulangi password baru")
        submitted    = st.form_submit_button("Simpan Password Baru", use_container_width=True, type="primary")

    if submitted:
        if not new_password or not confirm:
            st.warning("Semua kolom harus diisi.")
            return
        if new_password != confirm:
            st.error("Password dan konfirmasi tidak cocok.")
            return
        with st.spinner("Menyimpan password baru..."):
            ok, msg = update_password(new_password)
        if ok:
            st.success("✅ Password berhasil diperbarui! Silakan login.")
            st.session_state.pop("recovery_verified", None)
            clear_session()
            st.query_params.clear()
            st.rerun()
        else:
            st.error(msg)
