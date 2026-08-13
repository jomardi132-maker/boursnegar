BEGIN;

CREATE TABLE IF NOT EXISTS industries (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE,
  title_fa text NOT NULL, model_family text NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS issuers (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), stable_code text NOT NULL UNIQUE,
  legal_name text NOT NULL, national_id text UNIQUE, industry_id uuid REFERENCES industries(id),
  active boolean NOT NULL DEFAULT true, created_at timestamptz NOT NULL DEFAULT now(), updated_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS instruments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), issuer_id uuid NOT NULL REFERENCES issuers(id),
  isin text UNIQUE, market_instrument_id text UNIQUE, instrument_type text NOT NULL DEFAULT 'equity',
  currency_code char(3) NOT NULL DEFAULT 'IRR', active boolean NOT NULL DEFAULT true,
  listed_at date, delisted_at date, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS symbol_aliases (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), instrument_id uuid NOT NULL REFERENCES instruments(id),
  symbol text NOT NULL, valid_from date NOT NULL, valid_to date,
  source text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(instrument_id,symbol,valid_from), CHECK(valid_to IS NULL OR valid_to >= valid_from)
);
CREATE UNIQUE INDEX IF NOT EXISTS symbol_aliases_current_unique ON symbol_aliases(symbol) WHERE valid_to IS NULL;

CREATE TABLE IF NOT EXISTS disclosures (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), issuer_id uuid NOT NULL REFERENCES issuers(id),
  instrument_id uuid REFERENCES instruments(id), source text NOT NULL, source_disclosure_id text NOT NULL,
  letter_code text, disclosure_type text NOT NULL, title text NOT NULL,
  published_at timestamptz, published_date_jalali text, is_audited boolean,
  scope text CHECK(scope IN ('separate','consolidated','unknown')),
  status text NOT NULL DEFAULT 'active', created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(source,source_disclosure_id)
);
CREATE TABLE IF NOT EXISTS disclosure_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), disclosure_id uuid NOT NULL REFERENCES disclosures(id),
  version_number integer NOT NULL CHECK(version_number>0), revision_of_id uuid REFERENCES disclosure_versions(id),
  source_version_id text, published_at timestamptz, retrieved_at timestamptz NOT NULL,
  content_checksum char(64) NOT NULL, metadata jsonb NOT NULL DEFAULT '{}',
  is_current boolean NOT NULL DEFAULT true, UNIQUE(disclosure_id,version_number), UNIQUE(disclosure_id,content_checksum)
);
CREATE UNIQUE INDEX IF NOT EXISTS disclosure_versions_current_unique ON disclosure_versions(disclosure_id) WHERE is_current;
CREATE TABLE IF NOT EXISTS raw_documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), disclosure_version_id uuid NOT NULL REFERENCES disclosure_versions(id),
  source_url text NOT NULL, storage_key text NOT NULL UNIQUE, checksum_sha256 char(64) NOT NULL,
  mime_type text NOT NULL, byte_size bigint NOT NULL CHECK(byte_size>=0), retrieved_at timestamptz NOT NULL,
  parser_status text NOT NULL DEFAULT 'PENDING', UNIQUE(disclosure_version_id,checksum_sha256)
);

CREATE TABLE IF NOT EXISTS parser_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parser_name text NOT NULL, version text NOT NULL,
  document_type text NOT NULL, checksum char(64), active boolean NOT NULL DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(parser_name,version,document_type)
);
CREATE TABLE IF NOT EXISTS financial_periods (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), issuer_id uuid NOT NULL REFERENCES issuers(id),
  period_type text NOT NULL, start_date date NOT NULL, end_date date NOT NULL,
  start_date_jalali text NOT NULL, end_date_jalali text NOT NULL, length_months smallint NOT NULL CHECK(length_months>0),
  fiscal_year integer NOT NULL, audited boolean NOT NULL, scope text NOT NULL CHECK(scope IN ('separate','consolidated')),
  disclosure_version_id uuid NOT NULL REFERENCES disclosure_versions(id), UNIQUE(issuer_id,end_date,length_months,audited,scope,disclosure_version_id)
);
CREATE TABLE IF NOT EXISTS financial_facts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), issuer_id uuid NOT NULL REFERENCES issuers(id),
  period_id uuid NOT NULL REFERENCES financial_periods(id), fact_key text NOT NULL,
  raw_value numeric, normalized_value numeric, raw_unit text, normalized_unit text NOT NULL,
  unit_multiplier numeric NOT NULL DEFAULT 1, currency_code char(3), parser_version_id uuid REFERENCES parser_versions(id),
  quality_status text NOT NULL DEFAULT 'VALID', created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(period_id,fact_key,parser_version_id)
);
CREATE TABLE IF NOT EXISTS statement_line_items (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), financial_fact_id uuid NOT NULL REFERENCES financial_facts(id),
  statement_type text NOT NULL, source_label text NOT NULL, normalized_label text,
  row_locator text, column_locator text, UNIQUE(financial_fact_id,row_locator,column_locator)
);
CREATE TABLE IF NOT EXISTS monthly_sales (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), issuer_id uuid NOT NULL REFERENCES issuers(id), instrument_id uuid REFERENCES instruments(id),
  period_start date NOT NULL, period_end date NOT NULL, period_end_jalali text NOT NULL,
  product_key text NOT NULL, quantity numeric, quantity_unit text, revenue numeric, currency_code char(3) NOT NULL DEFAULT 'IRR',
  disclosure_version_id uuid NOT NULL REFERENCES disclosure_versions(id), UNIQUE(issuer_id,period_end,product_key,disclosure_version_id)
);
CREATE TABLE IF NOT EXISTS production_metrics (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), issuer_id uuid NOT NULL REFERENCES issuers(id),
  period_end date NOT NULL, period_end_jalali text NOT NULL, metric_key text NOT NULL,
  raw_value numeric, normalized_value numeric, raw_unit text, normalized_unit text,
  disclosure_version_id uuid NOT NULL REFERENCES disclosure_versions(id), UNIQUE(issuer_id,period_end,metric_key,disclosure_version_id)
);
CREATE TABLE IF NOT EXISTS corporate_actions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), instrument_id uuid NOT NULL REFERENCES instruments(id),
  action_type text NOT NULL, announced_at timestamptz, effective_date date, effective_date_jalali text,
  payload jsonb NOT NULL, disclosure_version_id uuid REFERENCES disclosure_versions(id), source text NOT NULL,
  source_action_id text NOT NULL, UNIQUE(source,source_action_id)
);
CREATE TABLE IF NOT EXISTS daily_prices (
  id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY, instrument_id uuid NOT NULL REFERENCES instruments(id),
  trading_date date NOT NULL, trading_date_jalali text NOT NULL, price_timestamp timestamptz NOT NULL,
  open numeric, high numeric, low numeric, close numeric, last numeric, adjusted_close numeric,
  volume numeric, value numeric, trade_count integer, market_cap numeric, shares_outstanding numeric,
  trading_status text, source text NOT NULL, adjustment_version text NOT NULL DEFAULT 'unadjusted',
  retrieved_at timestamptz NOT NULL, quality_status text NOT NULL DEFAULT 'VALID',
  UNIQUE(instrument_id,trading_date,source,adjustment_version)
);
CREATE INDEX IF NOT EXISTS daily_prices_instrument_time_idx ON daily_prices(instrument_id,trading_date DESC);

CREATE TABLE IF NOT EXISTS macro_series (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE, title_fa text NOT NULL,
  source text NOT NULL, unit text NOT NULL, frequency text NOT NULL, base_year text, active boolean NOT NULL DEFAULT true
);
CREATE TABLE IF NOT EXISTS macro_observations (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), series_id uuid NOT NULL REFERENCES macro_series(id),
  reference_start date NOT NULL, reference_end date NOT NULL, reference_period_jalali text NOT NULL,
  publication_date date NOT NULL, effective_date date NOT NULL, value numeric NOT NULL,
  revision integer NOT NULL DEFAULT 0, retrieved_at timestamptz NOT NULL,
  source_reference text NOT NULL, checksum char(64), quality_status text NOT NULL, confidence numeric NOT NULL CHECK(confidence BETWEEN 0 AND 100),
  UNIQUE(series_id,reference_start,reference_end,revision)
);

CREATE TABLE IF NOT EXISTS ingestion_runs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), pipeline text NOT NULL, source text NOT NULL,
  partition_key text, status text NOT NULL, started_at timestamptz NOT NULL DEFAULT now(), finished_at timestamptz,
  watermark jsonb NOT NULL DEFAULT '{}', metrics jsonb NOT NULL DEFAULT '{}', error_summary text,
  CHECK(status IN ('RUNNING','PASSED','FAILED','BLOCKED','CANCELLED'))
);
CREATE TABLE IF NOT EXISTS ingestion_checkpoints (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), source text NOT NULL, pipeline text NOT NULL, partition_key text NOT NULL,
  cursor jsonb NOT NULL, watermark_at timestamptz, updated_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(source,pipeline,partition_key)
);
CREATE TABLE IF NOT EXISTS ingestion_dead_letters (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), ingestion_run_id uuid REFERENCES ingestion_runs(id),
  source_reference text NOT NULL, stage text NOT NULL, error_code text NOT NULL, retry_count integer NOT NULL DEFAULT 0,
  payload_reference text, next_retry_at timestamptz, resolved_at timestamptz, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS data_quality_issues (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), entity_type text NOT NULL, entity_id uuid,
  severity text NOT NULL CHECK(severity IN ('INFO','WARNING','ERROR','CRITICAL')),
  issue_code text NOT NULL, cause text NOT NULL, status text NOT NULL DEFAULT 'OPEN',
  detected_at timestamptz NOT NULL DEFAULT now(), resolved_at timestamptz, resolution text,
  UNIQUE(entity_type,entity_id,issue_code,status)
);
CREATE TABLE IF NOT EXISTS source_lineage (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), output_type text NOT NULL, output_id uuid NOT NULL,
  input_type text NOT NULL, input_id uuid NOT NULL, formula text, locator jsonb NOT NULL DEFAULT '{}',
  created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(output_type,output_id,input_type,input_id,formula)
);

CREATE TABLE IF NOT EXISTS recommendation_policies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), version text NOT NULL UNIQUE, status text NOT NULL,
  parameters jsonb NOT NULL, effective_from timestamptz NOT NULL, effective_to timestamptz,
  created_at timestamptz NOT NULL DEFAULT now(), CHECK(effective_to IS NULL OR effective_to>effective_from)
);
CREATE TABLE IF NOT EXISTS industry_model_policies (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), industry_id uuid NOT NULL REFERENCES industries(id),
  version text NOT NULL, model_type text NOT NULL, status text NOT NULL, assumptions jsonb NOT NULL,
  effective_from timestamptz NOT NULL, effective_to timestamptz, UNIQUE(industry_id,version,model_type)
);
CREATE TABLE IF NOT EXISTS analytical_snapshots (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), instrument_id uuid NOT NULL REFERENCES instruments(id),
  report_mode text NOT NULL CHECK(report_mode IN ('audited','latest_codal')),
  status text NOT NULL, data_as_of timestamptz NOT NULL, calculated_at timestamptz NOT NULL DEFAULT now(),
  stale_after timestamptz NOT NULL, coverage numeric NOT NULL CHECK(coverage BETWEEN 0 AND 100),
  confidence numeric NOT NULL CHECK(confidence BETWEEN 0 AND 100), model_version text NOT NULL,
  policy_version text NOT NULL, payload_checksum char(64) NOT NULL, quality_summary jsonb NOT NULL DEFAULT '{}',
  UNIQUE(instrument_id,report_mode,data_as_of,model_version,policy_version)
);
CREATE INDEX IF NOT EXISTS analytical_snapshots_latest_idx ON analytical_snapshots(instrument_id,report_mode,calculated_at DESC);
CREATE TABLE IF NOT EXISTS health_score_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), snapshot_id uuid NOT NULL REFERENCES analytical_snapshots(id) ON DELETE CASCADE,
  score numeric CHECK(score BETWEEN 0 AND 100), dimensions jsonb NOT NULL, reasons jsonb NOT NULL, risks jsonb NOT NULL,
  UNIQUE(snapshot_id)
);
CREATE TABLE IF NOT EXISTS valuation_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), snapshot_id uuid NOT NULL REFERENCES analytical_snapshots(id) ON DELETE CASCADE,
  model_type text NOT NULL, model_version text NOT NULL, fair_value_low numeric, fair_value_base numeric, fair_value_high numeric,
  buy_zone jsonb, hold_zone jsonb, sell_zone jsonb, scenarios jsonb NOT NULL, assumptions jsonb NOT NULL,
  CHECK(fair_value_low IS NULL OR fair_value_base IS NULL OR fair_value_high IS NULL OR (fair_value_low<=fair_value_base AND fair_value_base<=fair_value_high)),
  UNIQUE(snapshot_id,model_type,model_version)
);
CREATE TABLE IF NOT EXISTS recommendation_results (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), snapshot_id uuid NOT NULL REFERENCES analytical_snapshots(id) ON DELETE CASCADE,
  decision text NOT NULL CHECK(decision IN ('BUY','HOLD','SELL','INSUFFICIENT_DATA')),
  top_reasons jsonb NOT NULL, top_risks jsonb NOT NULL, critical_warning text,
  policy_version text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(snapshot_id)
);

ALTER TABLE plans ADD COLUMN IF NOT EXISTS description_fa text;
ALTER TABLE plans ADD COLUMN IF NOT EXISTS unlimited_analyses boolean NOT NULL DEFAULT false;
ALTER TABLE plans ADD COLUMN IF NOT EXISTS features jsonb NOT NULL DEFAULT '[]';
ALTER TABLE plans ADD COLUMN IF NOT EXISTS display_order integer NOT NULL DEFAULT 0;
ALTER TABLE plans ADD COLUMN IF NOT EXISTS discount jsonb;
ALTER TABLE plans ADD COLUMN IF NOT EXISTS sale_starts_at timestamptz;
ALTER TABLE plans ADD COLUMN IF NOT EXISTS sale_ends_at timestamptz;
ALTER TABLE plans ADD COLUMN IF NOT EXISTS publicly_visible boolean NOT NULL DEFAULT true;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS entitlement_snapshot jsonb;
ALTER TABLE subscriptions ADD COLUMN IF NOT EXISTS purchased_price_toman bigint;
CREATE TABLE IF NOT EXISTS analysis_usage (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id),
  snapshot_id uuid NOT NULL REFERENCES analytical_snapshots(id), analysis_history_id uuid REFERENCES analysis_history(id),
  idempotency_key text NOT NULL, status text NOT NULL, credit_delta integer NOT NULL DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(user_id,idempotency_key), UNIQUE(analysis_history_id)
);

INSERT INTO schema_migrations(version) VALUES ('006_data_engine_v1') ON CONFLICT DO NOTHING;
COMMIT;
