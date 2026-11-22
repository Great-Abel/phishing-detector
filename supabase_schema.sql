-- ============================================================
-- Jalankan SQL ini di Supabase:
-- Dashboard → SQL Editor → New Query → Paste → Run
-- ============================================================

CREATE TABLE IF NOT EXISTS audit_trail (
    id          UUID        DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id     UUID        NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    user_email  TEXT        NOT NULL,
    url         TEXT        NOT NULL,
    prediction  TEXT        NOT NULL CHECK (prediction IN ('phishing', 'legitimate')),
    phishing_pct  NUMERIC(5,2) NOT NULL,
    legit_pct     NUMERIC(5,2) NOT NULL,
    scanned_at  TIMESTAMPTZ DEFAULT NOW()
);

-- Index supaya query per user cepat
CREATE INDEX IF NOT EXISTS idx_audit_trail_user_id
    ON audit_trail (user_id, scanned_at DESC);

-- Row Level Security: user hanya bisa lihat & insert data miliknya sendiri
ALTER TABLE audit_trail ENABLE ROW LEVEL SECURITY;

CREATE POLICY "user can insert own audit"
    ON audit_trail FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY "user can select own audit"
    ON audit_trail FOR SELECT
    USING (auth.uid() = user_id);
