import re
from dataclasses import dataclass
from urllib.parse import urlparse

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


# ── Whitelist domain terpercaya ────────────────────────────────────────────────
# Domain ini langsung legitimate tanpa lewat model

_TRUSTED_DOMAINS = {
    # Google — hanya subdomain resmi yang dikenal
    "google.com", "www.google.com",
    "translate.google.com", "mail.google.com",
    "drive.google.com", "docs.google.com",
    "maps.google.com", "accounts.google.com",
    "calendar.google.com", "meet.google.com",
    "classroom.google.com", "play.google.com",
    "scholar.google.com", "news.google.com",
    # GitHub
    "github.com", "www.github.com",
    "raw.githubusercontent.com", "gist.github.com",
    "docs.github.com", "api.github.com",
    # YouTube
    "youtube.com", "www.youtube.com", "youtu.be",
    # Microsoft
    "microsoft.com", "www.microsoft.com",
    "office.com", "www.office.com",
    "outlook.com", "www.outlook.com",
    "live.com", "www.live.com",
    # LinkedIn
    "linkedin.com", "www.linkedin.com",
    # Twitter / X
    "twitter.com", "www.twitter.com",
    "x.com", "www.x.com",
    # Instagram & Facebook
    "instagram.com", "www.instagram.com",
    "facebook.com", "www.facebook.com",
    # Wikipedia
    "wikipedia.org", "www.wikipedia.org",
    "id.wikipedia.org", "en.wikipedia.org",
    # Developer
    "stackoverflow.com", "www.stackoverflow.com",
    "npmjs.com", "www.npmjs.com",
    "pypi.org", "www.pypi.org",
    # Streamlit & Supabase
    "streamlit.io", "docs.streamlit.io",
    "supabase.com", "app.supabase.com",
    # E-commerce & fintech Indonesia
    "tokopedia.com", "www.tokopedia.com",
    "shopee.co.id", "www.shopee.co.id",
    "bukalapak.com", "www.bukalapak.com",
    "lazada.co.id", "www.lazada.co.id",
    "gojek.com", "www.gojek.com",
    "grab.com", "www.grab.com",
    # Perbankan Indonesia
    "bca.co.id", "www.bca.co.id", "klikbca.com",
    "mandiri.co.id", "www.mandiri.co.id",
    "bni.co.id", "www.bni.co.id",
    "bri.co.id", "www.bri.co.id",
}


def _is_trusted(url: str) -> bool:
    """
    Cek apakah domain URL masuk whitelist terpercaya.
    Pakai exact match pada registrable domain (bukan suffix)
    untuk mencegah subdomain spoofing seperti google.com.evil.xyz
    maupun subdomain yang dicompromise seperti evil.google.com.

    Yang diwhitelist hanya subdomain resmi yang dikenal,
    bukan seluruh *.google.com.
    """
    try:
        hostname = urlparse(url).hostname or ""
        return hostname.lower() in _TRUSTED_DOMAINS
    except Exception:
        return False


# ── Result dataclass ───────────────────────────────────────────────────────────

@dataclass
class PredictionResult:
    url: str
    prediction: str          # "phishing" | "legitimate"
    phishing_pct: float
    legit_pct: float
    features: dict
    is_whitelisted: bool = False


# ── Model loader ───────────────────────────────────────────────────────────────

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


# ── Prediction ─────────────────────────────────────────────────────────────────

def predict(url: str) -> PredictionResult:
    """
    Prediksi URL.
    Domain terpercaya langsung legitimate tanpa lewat model.
    """
    features = extract_features(url)

    # Shortcut: domain terpercaya
    if _is_trusted(url):
        return PredictionResult(
            url=url,
            prediction="legitimate",
            phishing_pct=0.0,
            legit_pct=100.0,
            features=features,
            is_whitelisted=True,
        )

    model = load_model()
    feature_df = pd.DataFrame([features])
    prediction_int = model.predict(feature_df)[0]
    probability    = model.predict_proba(feature_df)[0]

    return PredictionResult(
        url=url,
        prediction="phishing" if prediction_int == 1 else "legitimate",
        phishing_pct=round(probability[1] * 100, 2),
        legit_pct=round(probability[0] * 100, 2),
        features=features,
    )
