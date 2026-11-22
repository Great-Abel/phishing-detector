import streamlit as st
import pandas as pd

from services.auth_service import get_current_user, logout
from services.audit_service import get_audit_trail, format_wib
from services.detector_service import PredictionResult

FEATURE_LABELS = {
    "url_length":          "Panjang URL",
    "domain_length":       "Panjang Domain",
    "num_dots":            "Jumlah Titik (.)",
    "num_hyphens":         "Jumlah Tanda Hubung (-)",
    "num_underscores":     "Jumlah Underscore (_)",
    "num_question_marks":  "Jumlah Tanda Tanya (?)",
    "num_equal_signs":     "Jumlah Tanda Sama (=)",
    "num_slashes":         "Jumlah Slash (/)",
    "num_digits":          "Jumlah Angka",
    "has_at_symbol":       "Ada Simbol @",
    "has_https":           "Menggunakan HTTPS",
    "has_ip_address":      "Domain Berupa IP",
    "has_suspicious_word": "Ada Kata Mencurigakan",
    "path_length":         "Panjang Path",
    "num_special_chars":   "Jumlah Karakter Spesial",
}


# ── Sidebar ────────────────────────────────────────────────────────────────────

def render_sidebar() -> None:
    user = get_current_user()
    with st.sidebar:
        st.markdown("## 🛡️ Phishing Detector")
        st.divider()
        st.markdown("### 👤 Akun")
        st.markdown(f"**{user.email}**")
        st.caption("Status: ✅ Terautentikasi")
        st.divider()
        st.markdown("**Tentang Aplikasi**")
        st.caption(
            "Mendeteksi URL phishing menggunakan model "
            "Machine Learning berbasis Random Forest "
            "dengan akurasi 99.57%."
        )
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()


# ── Hero ───────────────────────────────────────────────────────────────────────

def render_hero() -> None:
    st.markdown("""
<div class="hero">
    <h1>🛡️ Detektor Phishing URL</h1>
    <p>Periksa apakah sebuah URL aman atau berbahaya menggunakan kecerdasan buatan secara instan.</p>
</div>
""", unsafe_allow_html=True)


# ── Result card ────────────────────────────────────────────────────────────────

def render_result(result: PredictionResult) -> None:
    if result.prediction == "phishing":
        st.markdown(
            '<div class="result-phishing">⚠️ URL ini terdeteksi sebagai <strong>PHISHING</strong></div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="result-legitimate">✅ URL ini terdeteksi sebagai <strong>LEGITIMATE</strong></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        pct_color = "#ff6b6b" if result.phishing_pct > 50 else "#fff"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">🎯 Kemungkinan Phishing</div>
            <div class="metric-value" style="color:{pct_color}">{result.phishing_pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        pct_color = "#48c78e" if result.legit_pct > 50 else "#fff"
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-label">✅ Kemungkinan Legitimate</div>
            <div class="metric-value" style="color:{pct_color}">{result.legit_pct:.1f}%</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 Tingkat Kepercayaan</div>', unsafe_allow_html=True)
    st.progress(result.phishing_pct / 100, text=f"Phishing: {result.phishing_pct:.1f}%")

    with st.expander("🔬 Lihat detail fitur URL yang dianalisis"):
        df = pd.DataFrame([result.features]).T.rename(columns={0: "Nilai"})
        df.index = [FEATURE_LABELS.get(i, i) for i in df.index]
        st.dataframe(df, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("⚠️ Hasil bersifat prediktif. Selalu verifikasi dengan sumber keamanan resmi.")


# ── Audit trail table ──────────────────────────────────────────────────────────

def render_audit_trail() -> None:
    st.markdown("---")
    st.markdown('<div class="section-title">🕵️ Riwayat Audit Trail</div>', unsafe_allow_html=True)

    col_refresh, _ = st.columns([1, 4])
    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    trail = get_audit_trail()

    if not trail:
        st.info("Belum ada riwayat scan. Coba periksa URL di atas terlebih dahulu.")
        return

    rows_html = ""
    for row in trail:
        badge = (
            '<span class="badge-phishing">⚠ Phishing</span>'
            if row["prediction"] == "phishing"
            else '<span class="badge-legitimate">✓ Legitimate</span>'
        )
        pct_color = "#ff6b6b" if row["prediction"] == "phishing" else "#48c78e"
        # Escape URL untuk mencegah XSS pada HTML attribute
        safe_url = row["url"].replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")
        rows_html += f"""
        <tr>
            <td style="color:#a0aec0;font-size:0.78rem">{format_wib(row['scanned_at'])}</td>
            <td style="color:#90cdf4">{row['user_email']}</td>
            <td class="url-cell" title="{safe_url}">{safe_url}</td>
            <td>{badge}</td>
            <td style="color:{pct_color};font-weight:600">{row['phishing_pct']:.1f}%</td>
        </tr>"""

    st.markdown(f"""
<div class="card" style="padding:1rem">
    <table class="trail-table">
        <thead>
            <tr>
                <th>Waktu (WIB)</th>
                <th>User</th>
                <th>URL</th>
                <th>Status</th>
                <th>% Phishing</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table>
</div>
""", unsafe_allow_html=True)

    st.caption(f"Menampilkan {len(trail)} riwayat terakhir milik akun kamu.")
