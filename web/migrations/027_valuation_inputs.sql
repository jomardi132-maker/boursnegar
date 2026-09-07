-- Evidence-gated intrinsic valuation inputs. No seed values belong here.
CREATE TABLE IF NOT EXISTS valuation_inputs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  issuer_id uuid NOT NULL REFERENCES issuers(id),
  period_id uuid REFERENCES financial_periods(id),
  input_key text NOT NULL CHECK (input_key IN (
    'fcff', 'fcfe', 'capital_expenditure', 'net_borrowing',
    'cost_of_equity', 'wacc', 'terminal_growth', 'nav_per_share',
    'units_outstanding'
  )),
  value numeric NOT NULL,
  normalized_unit text NOT NULL,
  source text NOT NULL,
  source_disclosure_id text,
  content_checksum text,
  quality_status text NOT NULL DEFAULT 'REVIEW'
    CHECK (quality_status IN ('VALID', 'REVIEW', 'REJECTED')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (issuer_id, period_id, input_key, source, source_disclosure_id)
);

CREATE INDEX IF NOT EXISTS valuation_inputs_period_key_idx
  ON valuation_inputs (period_id, input_key, quality_status);
