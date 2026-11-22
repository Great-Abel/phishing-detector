import re
from dataclasses import dataclass

import joblib
import pandas as pd
import streamlit as st

from config.settings import MODEL_PATH
from feature_extractor import extract_features

# ── URL validator ──────────────────────────────────────────────────────────────

_URL_REGEX = re.compile(
    r'^(https?://)'                         # wajib http:// atau https://
    r'(([a-zA-Z0-9\-]+\.)+[a-zA-Z]{2,})'   # domain
    r'(:\d+)?'                              # port opsional
    r'(/[^\s]*)?$',                         # path opsional
    re.IGNORECASE,
)


def is_valid_url(url: str) -> bool:
    return bool(_URL_REGEX.match(url.strip()))


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class PredictionResult:
    url: str
    prediction: str          # "phishing" | "legitimate"
    phishing_pct: float
    legit_pct: float
    features: dict


# ── Model loader ───────────────────────────────────────────────────────────────

@st.cache_resource
def load_model():
    """Load model sekali, cached di session."""
    return joblib.load(MODEL_PATH)


# ── Prediction ─────────────────────────────────────────────────────────────────

def predict(url: str) -> PredictionResult:
    """
    Ekstrak fitur dari URL lalu prediksi dengan model.
    Asumsi: URL sudah divalidasi dengan is_valid_url() sebelum dipanggil.
    """
    model = load_model()
    features = extract_features(url)
    feature_df = pd.DataFrame([features])

    prediction_int = model.predict(feature_df)[0]
    probability = model.predict_proba(feature_df)[0]

    return PredictionResult(
        url=url,
        prediction="phishing" if prediction_int == 1 else "legitimate",
        phishing_pct=round(probability[1] * 100, 2),
        legit_pct=round(probability[0] * 100, 2),
        features=features,
    )
