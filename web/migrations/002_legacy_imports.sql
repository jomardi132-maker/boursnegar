BEGIN;
CREATE TABLE IF NOT EXISTS legacy_analysis_imports(
  legacy_id text PRIMARY KEY,
  legacy_user_id text,
  symbol varchar(32) NOT NULL,
  report_mode text NOT NULL DEFAULT 'audited',
  result jsonb NOT NULL,
  legacy_created_at timestamptz,
  imported_at timestamptz NOT NULL DEFAULT now(),
  claimed_by_user_id uuid REFERENCES users(id),
  claimed_at timestamptz
);
CREATE INDEX IF NOT EXISTS legacy_analysis_claim_idx ON legacy_analysis_imports(claimed_by_user_id,legacy_created_at DESC);
INSERT INTO schema_migrations(version) VALUES('002_legacy_imports') ON CONFLICT DO NOTHING;
COMMIT;
