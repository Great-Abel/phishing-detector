import streamlit as st
import pandas as pd
import joblib
from feature_extractor import extract_features
from auth import show_auth_page, is_logged_in, logout, get_current_user

MODEL_PATH = "model/phishing_model.pkl"

st.set_page_config(
    page_title="Detektor Phishing URL",
    page_icon="🛡️",
    layout="centered"
)

# ── Guard: tampilkan halaman auth kalau belum login ────────────────────────────
if not is_logged_in():
    show_auth_page()
    st.stop()

# ── Sidebar: info user + tombol logout ────────────────────────────────────────
user = get_current_user()
with st.sidebar:
    st.markdown("### 👤 Akun")
    st.write(f"**{user.email}**")
    st.divider()
    if st.button("🚪 Logout", use_container_width=True):
        logout()
        st.rerun()

# ── Halaman utama ──────────────────────────────────────────────────────────────
st.title("🛡️ Detektor Phishing URL")
st.write(
    "Masukkan URL untuk memeriksa kemungkinan tautan tersebut merupakan phishing "
    "menggunakan model Machine Learning."
)

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)

model = load_model()

url_input = st.text_input(
    "Masukkan URL",
    placeholder="contoh: https://contoh-website.com"
)

if st.button("Periksa URL", type="primary"):
    if not url_input:
        st.warning("Masukkan URL terlebih dahulu.")
    else:
        features = extract_features(url_input)
        feature_df = pd.DataFrame([features])

        prediction = model.predict(feature_df)[0]
        probability = model.predict_proba(feature_df)[0]

        phishing_probability = probability[1] * 100
        legitimate_probability = probability[0] * 100

        st.subheader("Hasil Analisis")

        if prediction == 1:
            st.error("⚠️ URL terdeteksi sebagai **Phishing**")
        else:
            st.success("✅ URL terdeteksi sebagai **Legitimate**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Kemungkinan Phishing", f"{phishing_probability:.2f}%")
        with col2:
            st.metric("Kemungkinan Legitimate", f"{legitimate_probability:.2f}%")

        st.subheader("Fitur URL yang Dianalisis")
        st.dataframe(feature_df.T.rename(columns={0: "Nilai"}))

        st.caption(
            "Hasil ini bersifat prediktif dan tidak menggantikan verifikasi "
            "keamanan dari sumber resmi."
        )
