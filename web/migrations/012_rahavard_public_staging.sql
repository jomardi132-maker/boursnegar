CREATE TABLE IF NOT EXISTS rahavard_public_reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id text NOT NULL UNIQUE,
  image_id text,
  symbol text,
  title text,
  subtitle jsonb NOT NULL DEFAULT '[]'::jsonb,
  report_date timestamptz,
  fiscal_year timestamptz,
  pdf_url text NOT NULL,
  checksum_sha256 text NOT NULL,
  storage_path text NOT NULL,
  text_path text,
  text_status text NOT NULL DEFAULT 'PENDING_TEXT_EXTRACTION',
  source_status text NOT NULL DEFAULT 'QUARANTINED',
  raw_json jsonb NOT NULL,
  collected_at timestamptz NOT NULL DEFAULT now(),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS rahavard_public_reports_symbol_idx ON rahavard_public_reports(symbol);
CREATE INDEX IF NOT EXISTS rahavard_public_reports_collected_idx ON rahavard_public_reports(collected_at DESC);
