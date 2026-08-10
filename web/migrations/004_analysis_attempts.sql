BEGIN;

CREATE TABLE IF NOT EXISTS analysis_attempts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES users(id) ON DELETE SET NULL,
  symbol text,
  report_mode text,
  success boolean NOT NULL,
  error_code text,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS analysis_attempts_created_idx
  ON analysis_attempts(created_at DESC, success);
CREATE INDEX IF NOT EXISTS analysis_attempts_user_idx
  ON analysis_attempts(user_id, created_at DESC);

INSERT INTO schema_migrations(version) VALUES ('004_analysis_attempts')
ON CONFLICT DO NOTHING;

COMMIT;
