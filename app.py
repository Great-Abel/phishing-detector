import re
import streamlit as st
import pandas as pd
import joblib
from datetime import datetime, timezone
from feature_extractor import extract_features
from auth import (
    show_auth_page, is_logged_in, logout, get_current_user,
    save_audit, get_audit_trail
)

MODEL_PATH = "model/phishing_model.pkl"

st.set_page_config(
    page_title="Detektor Phishing URL",
    page_icon="🛡️",
    layout="centered"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

.hero {
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
}
.hero h1 { font-size: 2.4rem; font-weight: 700; color: #fff; margin-bottom: 0.4rem; }
.hero p  { font-size: 1rem; color: #a0aec0; max-width: 520px; margin: 0 auto; }

.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 2rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
}

.result-phishing {
    background: linear-gradient(135deg, rgba(255,75,75,0.15), rgba(255,75,75,0.05));
    border: 1px solid rgba(255,75,75,0.4);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    color: #ff6b6b;
    font-size: 1.2rem;
    font-weight: 600;
}
.result-legitimate {
    background: linear-gradient(135deg, rgba(72,199,142,0.15), rgba(72,199,142,0.05));
    border: 1px solid rgba(72,199,142,0.4);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    text-align: center;
    color: #48c78e;
    font-size: 1.2rem;
    font-weight: 600;
}

.metric-box {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}
.metric-label {
    font-size: 0.8rem; color: #a0aec0;
    margin-bottom: 0.3rem;
    text-transform: uppercase; letter-spacing: 0.05em;
}
.metric-value { font-size: 1.8rem; font-weight: 700; color: #fff; }

.input-label { font-size: 0.9rem; font-weight: 500; color: #cbd5e0; margin-bottom: 0.4rem; }
.section-title {
    font-size: 1rem; font-weight: 600; color: #e2e8f0;
    margin: 1.2rem 0 0.8rem;
}

/* Trail table */
.trail-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    color: #e2e8f0;
}
.trail-table th {
    background: rgba(255,255,255,0.08);
    padding: 0.6rem 0.8rem;
    text-align: left;
    font-weight: 600;
    color: #a0aec0;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 0.75rem;
}
.trail-table td {
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    vertical-align: middle;
}
.trail-table tr:hover td { background: rgba(255,255,255,0.03); }
.badge-phishing {
    background: rgba(255,75,75,0.2);
    color: #ff6b6b;
    border-radius: 6px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 0.75rem;
}
.badge-legitimate {
    background: rgba(72,199,142,0.2);
    color: #48c78e;
    border-radius: 6px;
    padding: 2px 8px;
    font-weight: 600;
    font-size: 0.75rem;
}
.url-cell {
    max-width: 220px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    color: #90cdf4;
}

section[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.9) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: opacity 0.2s ease !important;
    width: 100%;
}
.stButton > button:hover { opacity: 0.88 !important; }
hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)

# ── Guard ──────────────────────────────────────────────────────────────────────
if not is_logged_in():
    show_auth_page()
    st.stop()

# ── Sidebar ────────────────────────────────────────────────────────────────────
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
        "Aplikasi ini mendeteksi URL phishing menggunakan "
        "model Machine Learning berbasis Random Forest "
        "dengan akurasi 99.57%."
    )
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

# ── Load model ─────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

# ── Helper: validasi URL ───────────────────────────────────────────────────────
URL_REGEX = re.compile(
    r'^(https?://)'                        # wajib http:// atau https://
    r'(([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,})'  # domain
    r'(:\d+)?'                             # port opsional
    r'(/[^\s]*)?$',                        # path opsional
    re.IGNORECASE
)

def is_valid_url(url: str) -> bool:
    return bool(URL_REGEX.match(url.strip()))

# ── Helper: format waktu WIB ───────────────────────────────────────────────────
def fmt_time(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        wib = dt.astimezone(timezone.utc)
        # +7 jam manual (WIB)
        from datetime import timedelta
        wib = wib + timedelta(hours=7)
        return wib.strftime("%d %b %Y  %H:%M:%S")
    except Exception:
        return iso_str

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>🛡️ Detektor Phishing URL</h1>
    <p>Periksa apakah sebuah URL aman atau berbahaya menggunakan kecerdasan buatan secara instan.</p>
</div>
""", unsafe_allow_html=True)

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

# ── Hasil analisis ─────────────────────────────────────────────────────────────
if check:
    raw = url_input.strip()
    if not raw:
        st.warning("⚠️ Masukkan URL terlebih dahulu.")
    elif not is_valid_url(raw):
        st.error("❌ Input bukan URL yang valid. Gunakan format: `https://contoh.com`")
        st.caption("URL harus diawali dengan `http://` atau `https://` dan memiliki domain yang valid.")
    else:
        with st.spinner("Menganalisis URL..."):
            features    = extract_features(raw)
            feature_df  = pd.DataFrame([features])
            prediction  = model.predict(feature_df)[0]
            probability = model.predict_proba(feature_df)[0]

        phishing_pct = probability[1] * 100
        legit_pct    = probability[0] * 100
        pred_label   = "phishing" if prediction == 1 else "legitimate"

        # Simpan ke Supabase audit trail
        save_audit(raw, pred_label, phishing_pct, legit_pct)

        # Verdict
        if prediction == 1:
            st.markdown(
                '<div class="result-phishing">⚠️ URL ini terdeteksi sebagai <strong>PHISHING</strong></div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                '<div class="result-legitimate">✅ URL ini terdeteksi sebagai <strong>LEGITIMATE</strong></div>',
                unsafe_allow_html=True
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Probabilitas
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">🎯 Kemungkinan Phishing</div>
                <div class="metric-value" style="color:{'#ff6b6b' if phishing_pct > 50 else '#fff'}">
                    {phishing_pct:.1f}%
                </div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-box">
                <div class="metric-label">✅ Kemungkinan Legitimate</div>
                <div class="metric-value" style="color:{'#48c78e' if legit_pct > 50 else '#fff'}">
                    {legit_pct:.1f}%
                </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<div class="section-title">📊 Tingkat Kepercayaan</div>', unsafe_allow_html=True)
        st.progress(phishing_pct / 100, text=f"Phishing: {phishing_pct:.1f}%")

        with st.expander("🔬 Lihat detail fitur URL yang dianalisis"):
            renamed = {
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
            display_df = feature_df.T.rename(columns={0: "Nilai"})
            display_df.index = [renamed.get(i, i) for i in display_df.index]
            st.dataframe(display_df, use_container_width=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("⚠️ Hasil bersifat prediktif. Selalu verifikasi dengan sumber keamanan resmi.")

# ── Audit Trail ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<div class="section-title">🕵️ Riwayat Audit Trail</div>', unsafe_allow_html=True)

col_refresh, _ = st.columns([1, 4])
with col_refresh:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

trail = get_audit_trail(limit=50)

if not trail:
    st.info("Belum ada riwayat scan. Coba periksa URL di atas terlebih dahulu.")
else:
    rows_html = ""
    for row in trail:
        badge = (
            '<span class="badge-phishing">⚠ Phishing</span>'
            if row["prediction"] == "phishing"
            else '<span class="badge-legitimate">✓ Legitimate</span>'
        )
        pct_color = "#ff6b6b" if row["prediction"] == "phishing" else "#48c78e"
        rows_html += f"""
        <tr>
            <td style="color:#a0aec0;font-size:0.78rem">{fmt_time(row['scanned_at'])}</td>
            <td style="color:#90cdf4">{row['user_email']}</td>
            <td class="url-cell" title="{row['url']}">{row['url']}</td>
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
