import os
from dotenv import load_dotenv

load_dotenv()

# ── Supabase ───────────────────────────────────────────────────────────────────
SUPABASE_URL: str      = os.getenv("SUPABASE_URL", "")
SUPABASE_ANON_KEY: str = os.getenv("SUPABASE_ANON_KEY", "")

# ── Model ──────────────────────────────────────────────────────────────────────
MODEL_PATH: str = os.getenv("MODEL_PATH", "model/phishing_model.pkl")

# ── Audit Trail ────────────────────────────────────────────────────────────────
AUDIT_TRAIL_TABLE: str = "audit_trail"
AUDIT_TRAIL_LIMIT: int = 50

# ── Timezone WIB (UTC+7) ───────────────────────────────────────────────────────
WIB_OFFSET_HOURS: int = 7

# ── Upstash Redis ──────────────────────────────────────────────────────────────
UPSTASH_REDIS_URL: str   = os.getenv("UPSTASH_REDIS_REST_URL", "")
UPSTASH_REDIS_TOKEN: str = os.getenv("UPSTASH_REDIS_REST_TOKEN", "")

# ── Auth ───────────────────────────────────────────────────────────────────────
MIN_PASSWORD_LENGTH: int = 8


def validate_config() -> list[str]:
    """Return nama env vars wajib yang belum diisi."""
    missing = []
    if not SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not SUPABASE_ANON_KEY:
        missing.append("SUPABASE_ANON_KEY")
    return missing
