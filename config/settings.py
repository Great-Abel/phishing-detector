import os
from dotenv import load_dotenv

load_dotenv()

# ── Supabase ───────────────────────────────────────────────────────────────────
SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")

# ── Model ──────────────────────────────────────────────────────────────────────
MODEL_PATH: str = os.getenv("MODEL_PATH", "model/phishing_model.pkl")

# ── Audit Trail ────────────────────────────────────────────────────────────────
AUDIT_TRAIL_TABLE: str = "audit_trail"
AUDIT_TRAIL_LIMIT: int = 50

# ── Timezone offset WIB (UTC+7) ────────────────────────────────────────────────
WIB_OFFSET_HOURS: int = 7

# ── Upstash Redis ──────────────────────────────────────────────────────────────
UPSTASH_REDIS_URL: str   = os.getenv("UPSTASH_REDIS_URL", "")
UPSTASH_REDIS_TOKEN: str = os.getenv("UPSTASH_REDIS_TOKEN", "")

# ── Rate Limiter ───────────────────────────────────────────────────────────────
RATE_LIMIT_MAX_ATTEMPTS: int  = 5   # maks percobaan gagal
RATE_LIMIT_WINDOW_SECS: int   = 60  # window tracking (detik)
RATE_LIMIT_COOLDOWN_SECS: int = 60  # durasi kunci setelah maks tercapai


def validate_config() -> list[str]:
    """
    Periksa apakah semua env vars wajib sudah diisi.
    Return list of missing variable names.
    """
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_ANON_KEY:
        missing.append("SUPABASE_ANON_KEY")
    return missing
