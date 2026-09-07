BEGIN;

CREATE TABLE IF NOT EXISTS issuer_profiles (
  issuer_id uuid PRIMARY KEY REFERENCES issuers(id) ON DELETE CASCADE,
  official_website_url text,
  logo_url text,
  source_type text NOT NULL,
  source_reference text NOT NULL,
  evidence_checksum char(64) NOT NULL,
  status text NOT NULL DEFAULT 'PENDING',
  verified_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK (official_website_url IS NULL OR official_website_url ~ '^https://'),
  CHECK (logo_url IS NULL OR logo_url ~ '^https://'),
  CHECK (source_type IN ('official_website', 'official_registry', 'exchange_profile', 'manual_review')),
  CHECK (status IN ('PENDING', 'VERIFIED', 'REJECTED')),
  CHECK (status <> 'VERIFIED' OR verified_at IS NOT NULL)
);

CREATE INDEX IF NOT EXISTS issuer_profiles_verified_idx
  ON issuer_profiles(status) WHERE status = 'VERIFIED';

COMMIT;
