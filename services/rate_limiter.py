"""
Rate limiter berbasis Upstash Redis — dual layer: per email + per IP.

Strategi:
- Layer 1 (per email) : maks 5 gagal → kunci 60 detik
- Layer 2 (per IP)    : maks 20 gagal → kunci 15 menit
  IP-based lebih longgar karena bisa shared (NAT, kantor, kampus).
  VPN bypass IP? Tidak masalah — email layer tetap aktif.
"""
import streamlit as st
from upstash_redis import Redis
from config.settings import (
    UPSTASH_REDIS_URL, UPSTASH_REDIS_TOKEN,
    RATE_LIMIT_MAX_ATTEMPTS, RATE_LIMIT_WINDOW_SECS, RATE_LIMIT_COOLDOWN_SECS,
    RATE_LIMIT_IP_MAX_ATTEMPTS, RATE_LIMIT_IP_COOLDOWN_SECS,
)

_PFX_EMAIL_ATTEMPTS = "rl:email:attempts:"
_PFX_EMAIL_LOCKED   = "rl:email:locked:"
_PFX_IP_ATTEMPTS    = "rl:ip:attempts:"
_PFX_IP_LOCKED      = "rl:ip:locked:"


@st.cache_resource
def _get_redis() -> Redis | None:
    if not UPSTASH_REDIS_URL or not UPSTASH_REDIS_TOKEN:
        return None
    try:
        return Redis(url=UPSTASH_REDIS_URL, token=UPSTASH_REDIS_TOKEN)
    except Exception:
        return None


# ── Internal helpers ───────────────────────────────────────────────────────────

def _is_locked(r: Redis, locked_key: str) -> tuple[bool, int]:
    try:
        ttl = r.ttl(locked_key)
        if ttl > 0:
            return True, ttl
    except Exception:
        pass
    return False, 0


def _record(r: Redis, attempts_key: str, locked_key: str,
            max_attempts: int, window: int, cooldown: int) -> int:
    try:
        count = r.incr(attempts_key)
        if count == 1:
            r.expire(attempts_key, window)
        if count >= max_attempts:
            r.set(locked_key, 1, ex=cooldown)
            r.delete(attempts_key)
            return max_attempts
        return count
    except Exception:
        return 0


def _reset(r: Redis, attempts_key: str, locked_key: str) -> None:
    try:
        r.delete(attempts_key)
        r.delete(locked_key)
    except Exception:
        pass


# ── Public API — Email layer ───────────────────────────────────────────────────

def is_locked_email(email: str) -> tuple[bool, int]:
    r = _get_redis()
    if r is None:
        return False, 0
    return _is_locked(r, f"{_PFX_EMAIL_LOCKED}{email}")


def record_failed_email(email: str) -> int:
    r = _get_redis()
    if r is None:
        return 0
    return _record(
        r,
        f"{_PFX_EMAIL_ATTEMPTS}{email}",
        f"{_PFX_EMAIL_LOCKED}{email}",
        RATE_LIMIT_MAX_ATTEMPTS,
        RATE_LIMIT_WINDOW_SECS,
        RATE_LIMIT_COOLDOWN_SECS,
    )


def reset_email(email: str) -> None:
    r = _get_redis()
    if r is None:
        return
    _reset(r, f"{_PFX_EMAIL_ATTEMPTS}{email}", f"{_PFX_EMAIL_LOCKED}{email}")


def remaining_attempts(email: str) -> int:
    r = _get_redis()
    if r is None:
        return RATE_LIMIT_MAX_ATTEMPTS
    try:
        val = r.get(f"{_PFX_EMAIL_ATTEMPTS}{email}")
        return max(0, RATE_LIMIT_MAX_ATTEMPTS - (int(val) if val else 0))
    except Exception:
        return RATE_LIMIT_MAX_ATTEMPTS


# ── Public API — IP layer ──────────────────────────────────────────────────────

def is_locked_ip(ip: str) -> tuple[bool, int]:
    r = _get_redis()
    if r is None:
        return False, 0
    return _is_locked(r, f"{_PFX_IP_LOCKED}{ip}")


def record_failed_ip(ip: str) -> int:
    r = _get_redis()
    if r is None:
        return 0
    return _record(
        r,
        f"{_PFX_IP_ATTEMPTS}{ip}",
        f"{_PFX_IP_LOCKED}{ip}",
        RATE_LIMIT_IP_MAX_ATTEMPTS,
        RATE_LIMIT_WINDOW_SECS,
        RATE_LIMIT_IP_COOLDOWN_SECS,
    )


def reset_ip(ip: str) -> None:
    r = _get_redis()
    if r is None:
        return
    _reset(r, f"{_PFX_IP_ATTEMPTS}{ip}", f"{_PFX_IP_LOCKED}{ip}")


# ── Backward-compat aliases (dipakai auth_service) ────────────────────────────

def is_locked(identifier: str) -> tuple[bool, int]:
    return is_locked_email(identifier)


def record_failed(identifier: str) -> int:
    return record_failed_email(identifier)


def reset(identifier: str) -> None:
    reset_email(identifier)
