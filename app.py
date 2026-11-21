import streamlit as st
import pandas as pd
import joblib
from feature_extractor import extract_features

MODEL_PATH = "model/phishing_model.pkl"

st.set_page_config(
    page_title="Detektor Phishing URL",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ Detektor Phishing URL")
st.write(
    "Masukkan URL untuk memeriksa kemungkinan tautan tersebut merupakan phishing "
    "menggunakan model Machine Learning."
)

model = joblib.load(MODEL_PATH)

url_input = st.text_input(
    "Masukkan URL",
    placeholder="contoh: https://contoh-website.com"
)

if st.button("Periksa URL"):
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
            st.metric(
                "Kemungkinan Phishing",
                f"{phishing_probability:.2f}%"
            )

        with col2:
            st.metric(
                "Kemungkinan Legitimate",
                f"{legitimate_probability:.2f}%"
            )

        st.subheader("Fitur URL yang Dianalisis")
        st.dataframe(feature_df.T.rename(columns={0: "Nilai"}))

        st.caption(
            "Hasil ini bersifat prediktif dan tidak menggantikan verifikasi "
            "keamanan dari sumber resmi."
        )