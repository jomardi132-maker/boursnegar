BEGIN;

ALTER TABLE email_identities ADD COLUMN IF NOT EXISTS email_verified_at timestamptz;
UPDATE email_identities SET email_verified_at=coalesce(email_verified_at, created_at);

CREATE TABLE IF NOT EXISTS email_verification_tokens (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  code_hash char(64) NOT NULL,
  expires_at timestamptz NOT NULL,
  consumed_at timestamptz,
  request_ip inet,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS email_verification_active_idx ON email_verification_tokens(user_id, expires_at) WHERE consumed_at IS NULL;
INSERT INTO schema_migrations(version) VALUES ('009_email_verification') ON CONFLICT DO NOTHING;

COMMIT;
