BEGIN;

ALTER TABLE plans DROP CONSTRAINT IF EXISTS plans_code_check;
ALTER TABLE plans DROP CONSTRAINT IF EXISTS plans_code_format_check;
ALTER TABLE plans
  ADD CONSTRAINT plans_code_format_check
  CHECK (code ~ '^[a-z0-9][a-z0-9_-]{1,47}$');

INSERT INTO schema_migrations(version)
VALUES ('007_product_hardening')
ON CONFLICT DO NOTHING;

COMMIT;
