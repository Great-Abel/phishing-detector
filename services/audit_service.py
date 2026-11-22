from datetime import datetime, timezone, timedelta

from config.settings import AUDIT_TRAIL_TABLE, AUDIT_TRAIL_LIMIT, WIB_OFFSET_HOURS
from services.auth_service import get_client, get_current_user
from services.detector_service import PredictionResult


# ── Save ───────────────────────────────────────────────────────────────────────

def save_audit(result: PredictionResult) -> tuple[bool, str]:
    """
    Simpan satu hasil scan ke tabel audit_trail.
    Hanya dipanggil setelah URL tervalidasi dan prediksi selesai.
    """
    user = get_current_user()
    if not user:
        return False, "User tidak terautentikasi."

    try:
        get_client().table(AUDIT_TRAIL_TABLE).insert({
            "user_id":      user.id,
            "user_email":   user.email,
            "url":          result.url,
            "prediction":   result.prediction,
            "phishing_pct": result.phishing_pct,
            "legit_pct":    result.legit_pct,
        }).execute()
        return True, "Audit tersimpan."
    except Exception as e:
        return False, str(e)


# ── Fetch ──────────────────────────────────────────────────────────────────────

def get_audit_trail(limit: int = AUDIT_TRAIL_LIMIT) -> list[dict]:
    """
    Ambil riwayat scan milik user yang sedang login.
    Diurutkan dari yang terbaru.
    """
    user = get_current_user()
    if not user:
        return []

    try:
        response = (
            get_client()
            .table(AUDIT_TRAIL_TABLE)
            .select("user_email, url, prediction, phishing_pct, legit_pct, scanned_at")
            .eq("user_id", user.id)
            .order("scanned_at", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []
    except Exception:
        return []


# ── Helpers ────────────────────────────────────────────────────────────────────

def format_wib(iso_str: str) -> str:
    """Konversi ISO timestamp UTC ke string WIB (UTC+7)."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        wib = dt.astimezone(timezone.utc) + timedelta(hours=WIB_OFFSET_HOURS)
        return wib.strftime("%d %b %Y  %H:%M:%S")
    except Exception:
        return iso_str
