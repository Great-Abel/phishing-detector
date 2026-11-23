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

MAX_ATTEMPTS  = 5   # maks percobaan gagal login
WINDOW_SECS   = 60  # window tracking login
COOLDOWN_SECS = 60  # durasi kunci login

# ── Reset password rate limit ──────────────────────────────────────────────────
RESET_MAX        = 2     # maks kirim email reset per window
RESET_WINDOW     = 3600  # window 1 jam (detik)
RESET_COOLDOWN   = 3600  # kunci 1 jam setelah maks tercapai


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


# ── Reset password rate limit ──────────────────────────────────────────────────

def _key_reset_attempts(email: str) -> str:
    return f"rl:reset:attempts:{email}"

def _key_reset_locked(email: str) -> str:
    return f"rl:reset:locked:{email}"


def is_reset_locked(email: str) -> tuple[bool, int]:
    """
    Cek apakah email dikunci untuk kirim reset password.
    Return (locked, sisa_detik).
    """
    r = _redis()
    if r is None:
        return False, 0
    try:
        ttl = r.ttl(_key_reset_locked(email))
        return (True, ttl) if ttl > 0 else (False, 0)
    except Exception:
        return False, 0


def record_reset(email: str) -> int:
    """
    Catat satu pengiriman email reset.
    Return sisa kuota (0 = baru saja dikunci).
    """
    r = _redis()
    if r is None:
        return RESET_MAX

    key_att = _key_reset_attempts(email)
    key_lck = _key_reset_locked(email)
    try:
        count = r.incr(key_att)
        if count == 1:
            r.expire(key_att, RESET_WINDOW)
        if count >= RESET_MAX:
            r.set(key_lck, 1, ex=RESET_COOLDOWN)
            r.delete(key_att)
            return 0
        return RESET_MAX - count
    except Exception:
        return RESET_MAX
