import streamlit as st


def inject_css() -> None:
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Background ── */
.stApp {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    min-height: 100vh;
}

/* ── Hero ── */
.hero { text-align: center; padding: 2.5rem 1rem 1.5rem; }
.hero h1 { font-size: 2.4rem; font-weight: 700; color: #fff; margin-bottom: 0.4rem; }
.hero p  { font-size: 1rem; color: #a0aec0; max-width: 520px; margin: 0 auto; }

/* ── Card ── */
.card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px;
    padding: 2rem;
    backdrop-filter: blur(12px);
    margin-bottom: 1.5rem;
}

/* ── Result verdict ── */
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

/* ── Metric box ── */
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

/* ── Typography helpers ── */
.input-label  { font-size: 0.9rem; font-weight: 500; color: #cbd5e0; margin-bottom: 0.4rem; }
.section-title { font-size: 1rem; font-weight: 600; color: #e2e8f0; margin: 1.2rem 0 0.8rem; }

/* ── Audit trail table ── */
.trail-table {
    width: 100%; border-collapse: collapse;
    font-size: 0.82rem; color: #e2e8f0;
}
.trail-table th {
    background: rgba(255,255,255,0.08);
    padding: 0.6rem 0.8rem; text-align: left;
    font-weight: 600; color: #a0aec0;
    text-transform: uppercase; letter-spacing: 0.04em; font-size: 0.75rem;
}
.trail-table td {
    padding: 0.6rem 0.8rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
    vertical-align: middle;
}
.trail-table tr:hover td { background: rgba(255,255,255,0.03); }
.badge-phishing {
    background: rgba(255,75,75,0.2); color: #ff6b6b;
    border-radius: 6px; padding: 2px 8px;
    font-weight: 600; font-size: 0.75rem;
}
.badge-legitimate {
    background: rgba(72,199,142,0.2); color: #48c78e;
    border-radius: 6px; padding: 2px 8px;
    font-weight: 600; font-size: 0.75rem;
}
.url-cell {
    max-width: 220px; overflow: hidden;
    text-overflow: ellipsis; white-space: nowrap;
    color: #90cdf4;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: rgba(15,12,41,0.9) !important;
    border-right: 1px solid rgba(255,255,255,0.08);
}

/* ── Button ── */
.stButton > button {
    background: linear-gradient(135deg, #667eea, #764ba2) !important;
    color: white !important; border: none !important;
    border-radius: 10px !important; padding: 0.6rem 1.5rem !important;
    font-weight: 600 !important; font-size: 0.95rem !important;
    transition: opacity 0.2s ease !important; width: 100%;
}
.stButton > button:hover { opacity: 0.88 !important; }

hr { border-color: rgba(255,255,255,0.1) !important; }
</style>
""", unsafe_allow_html=True)
