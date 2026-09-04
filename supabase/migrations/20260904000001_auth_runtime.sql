-- T19 runtime persistence additions.
-- Passwords are never stored; only one-way password hashes are stored.
BEGIN;
ALTER TABLE users ADD COLUMN IF NOT EXISTS password_hash TEXT NULL;
CREATE TABLE IF NOT EXISTS user_sessions (
    token_hash TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL,
    revoked_at TIMESTAMPTZ NULL
);
CREATE INDEX IF NOT EXISTS ix_user_sessions_user ON user_sessions(user_id);
CREATE INDEX IF NOT EXISTS ix_user_sessions_expiry ON user_sessions(expires_at);
COMMIT;
