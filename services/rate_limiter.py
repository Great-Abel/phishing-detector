"""
Rate limiter login per email menggunakan Upstash Redis.

Aturan:
- Maks 5 percobaan gagal dalam window 60 detik
- Setelah ke-5, akun dikunci 60 detik
- Login berhasil → counter direset
"""
import streamlit as st
from upstash_redis import Redis
from config.settings import UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN

MAX_ATTEMPTS  = 5   # maks percobaan gagal
WINDOW_SECS   = 60  # window tracking
COOLDOWN_SECS = 60  # durasi kunci


@st.cache_resource
def _redis() -> Redis | None:
    """Koneksi Redis sekali per instance. None jika credentials kosong."""
    if not UPSTASH_REDIS_URL or not UPSTASH_REDIS_TOKEN:
        return None
    try:
        return Redis(url=UPSTASH_REDIS_URL, token=UPSTASH_REDIS_TOKEN)
    except Exception:
        return None


def _key_attempts(email: str) -> str:
    return f"rl:attempts:{email}"


def _key_locked(email: str) -> str:
    return f"rl:locked:{email}"


# ── Public API ─────────────────────────────────────────────────────────────────

def is_locked(email: str) -> tuple[bool, int]:
    """
    Cek apakah email sedang dikunci.
    Return (locked, sisa_detik).
    """
    r = _redis()
    if r is None:
        return False, 0
    try:
        ttl = r.ttl(_key_locked(email))
        return (True, ttl) if ttl > 0 else (False, 0)
    except Exception:
        return False, 0


def remaining(email: str) -> int:
    """Sisa percobaan sebelum dikunci."""
    r = _redis()
    if r is None:
        return MAX_ATTEMPTS
    try:
        val = r.get(_key_attempts(email))
        return max(0, MAX_ATTEMPTS - (int(val) if val else 0))
    except Exception:
        return MAX_ATTEMPTS


def record_fail(email: str) -> int:
    """
    Catat satu percobaan gagal.
    Return sisa percobaan (0 = baru saja dikunci).
    """
    r = _redis()
    if r is None:
        return MAX_ATTEMPTS

    key_att = _key_attempts(email)
    key_lck = _key_locked(email)
    try:
        count = r.incr(key_att)
        if count == 1:
            r.expire(key_att, WINDOW_SECS)

        if count >= MAX_ATTEMPTS:
            r.set(key_lck, 1, ex=COOLDOWN_SECS)
            r.delete(key_att)
            return 0

        return MAX_ATTEMPTS - count
    except Exception:
        return MAX_ATTEMPTS


def reset(email: str) -> None:
    """Reset counter setelah login berhasil."""
    r = _redis()
    if r is None:
        return
    try:
        r.delete(_key_attempts(email))
        r.delete(_key_locked(email))
    except Exception:
        pass
