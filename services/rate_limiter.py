"""
Rate limiter berbasis Upstash Redis.
Strategi: sliding window per identifier (email).
- Maks 5 percobaan gagal dalam window 60 detik
- Setelah maks tercapai, kunci selama 60 detik
"""
import streamlit as st
from upstash_redis import Redis
from config.settings import (
    UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN,
    RATE_LIMIT_MAX_ATTEMPTS, RATE_LIMIT_WINDOW_SECS, RATE_LIMIT_COOLDOWN_SECS
)

_KEY_PREFIX_ATTEMPTS = "login_attempts:"
_KEY_PREFIX_LOCKED   = "login_locked:"


@st.cache_resource
def _get_redis() -> Redis | None:
    """
    Inisialisasi koneksi Redis sekali per app instance.
    Return None kalau credentials belum diisi — rate limiter dinonaktifkan.
    """
    if not UPSTASH_REDIS_URL or not UPSTASH_REDIS_TOKEN:
        return None
    try:
        return Redis(url=UPSTASH_REDIS_URL, token=UPSTASH_REDIS_TOKEN)
    except Exception:
        return None


# ── Public API ─────────────────────────────────────────────────────────────────

def is_locked(identifier: str) -> tuple[bool, int]:
    """
    Cek apakah identifier (email) sedang dikunci.
    Return (locked: bool, sisa_ttl_detik: int)
    """
    r = _get_redis()
    if r is None:
        return False, 0

    try:
        ttl = r.ttl(f"{_KEY_PREFIX_LOCKED}{identifier}")
        if ttl > 0:
            return True, ttl
    except Exception:
        pass
    return False, 0


def record_failed(identifier: str) -> int:
    """
    Catat satu percobaan gagal.
    Return jumlah percobaan gagal saat ini.
    Otomatis kunci kalau sudah mencapai MAX_ATTEMPTS.
    """
    r = _get_redis()
    if r is None:
        return 0

    key = f"{_KEY_PREFIX_ATTEMPTS}{identifier}"
    try:
        attempts = r.incr(key)
        # Set TTL window hanya pada percobaan pertama
        if attempts == 1:
            r.expire(key, RATE_LIMIT_WINDOW_SECS)

        if attempts >= RATE_LIMIT_MAX_ATTEMPTS:
            # Kunci identifier
            r.set(f"{_KEY_PREFIX_LOCKED}{identifier}", 1, ex=RATE_LIMIT_COOLDOWN_SECS)
            # Reset counter
            r.delete(key)
            return RATE_LIMIT_MAX_ATTEMPTS

        return attempts
    except Exception:
        return 0


def reset(identifier: str) -> None:
    """Reset semua state rate limiter untuk identifier (setelah login berhasil)."""
    r = _get_redis()
    if r is None:
        return
    try:
        r.delete(f"{_KEY_PREFIX_ATTEMPTS}{identifier}")
        r.delete(f"{_KEY_PREFIX_LOCKED}{identifier}")
    except Exception:
        pass


def remaining_attempts(identifier: str) -> int:
    """Sisa percobaan sebelum dikunci."""
    r = _get_redis()
    if r is None:
        return RATE_LIMIT_MAX_ATTEMPTS

    try:
        val = r.get(f"{_KEY_PREFIX_ATTEMPTS}{identifier}")
        current = int(val) if val else 0
        return max(0, RATE_LIMIT_MAX_ATTEMPTS - current)
    except Exception:
        return RATE_LIMIT_MAX_ATTEMPTS
