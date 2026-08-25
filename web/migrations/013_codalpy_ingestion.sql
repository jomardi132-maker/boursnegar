BEGIN;

CREATE TABLE IF NOT EXISTS codalpy_records (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), source text NOT NULL,
  output_type text NOT NULL CHECK(output_type IN ('income_statement','balance_sheet','monthly_activity')),
  source_action_id text NOT NULL, tracing_no text NOT NULL, period_end_jalali text,
  fact_key text, source_label text NOT NULL, value numeric NOT NULL, raw_value text,
  unit text, payload jsonb NOT NULL, retrieved_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(source, source_action_id)
);
CREATE INDEX IF NOT EXISTS codalpy_records_period_idx ON codalpy_records(source, period_end_jalali, output_type);

COMMIT;
