import streamlit as st

from config.settings import validate_config
from services.auth_service import is_logged_in
from services.detector_service import is_valid_url, predict
from services.audit_service import save_audit
from ui.styles import inject_css
from ui.auth_page import show_auth_page
from ui.reset_page import show_reset_page
from ui.components import render_sidebar, render_hero, render_result, render_audit_trail

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Detektor Phishing URL",
    page_icon="🛡️",
    layout="centered",
)

inject_css()

# ── Config check ───────────────────────────────────────────────────────────────
missing = validate_config()
if missing:
    st.error(f"❌ ENV vars belum diisi: {', '.join(missing)}. Periksa file .env kamu.")
    st.stop()

# ── Recovery token check (dari link email reset password) ──────────────────────
params = st.query_params
access_token  = params.get("access_token", "")
refresh_token = params.get("refresh_token", "")
token_type    = params.get("type", "")

if token_type == "recovery" and access_token:
    show_reset_page(access_token, refresh_token)
    st.stop()

# ── Auth guard ─────────────────────────────────────────────────────────────────
if not is_logged_in():
    show_auth_page()
    st.stop()

# ── Layout ─────────────────────────────────────────────────────────────────────
render_sidebar()
render_hero()

# ── Input card ─────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="input-label">🔗 Masukkan URL yang ingin diperiksa</div>', unsafe_allow_html=True)

url_input = st.text_input(
    label="url",
    label_visibility="collapsed",
    placeholder="https://contoh-website.com/path?query=value",
)

col_btn, col_clear = st.columns([3, 1])
with col_btn:
    check = st.button("🔍 Periksa URL", type="primary", use_container_width=True)
with col_clear:
    if st.button("🗑️ Reset", use_container_width=True):
        st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# ── Scan & result ──────────────────────────────────────────────────────────────
if check:
    raw = url_input.strip()
    if not raw:
        st.warning("⚠️ Masukkan URL terlebih dahulu.")
    elif not is_valid_url(raw):
        st.error("❌ Input bukan URL yang valid. Gunakan format: `https://contoh.com`")
        st.caption("URL harus diawali `http://` atau `https://` dan memiliki domain yang valid.")
    else:
        with st.spinner("Menganalisis URL..."):
            result = predict(raw)
            save_audit(result)
        render_result(result)

# ── Audit trail ────────────────────────────────────────────────────────────────
render_audit_trail()
