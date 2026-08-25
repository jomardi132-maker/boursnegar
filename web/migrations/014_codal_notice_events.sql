BEGIN;

CREATE TABLE IF NOT EXISTS codal_notice_events (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  source text NOT NULL,
  symbol text NOT NULL,
  tracing_no text NOT NULL,
  title text,
  notice_type text NOT NULL,
  published_at_jalali text,
  period_end_jalali text,
  raw_payload jsonb NOT NULL,
  content_checksum text,
  retrieved_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(source, symbol, tracing_no)
);
CREATE INDEX IF NOT EXISTS codal_notice_events_symbol_idx ON codal_notice_events(symbol, published_at_jalali);

COMMIT;
