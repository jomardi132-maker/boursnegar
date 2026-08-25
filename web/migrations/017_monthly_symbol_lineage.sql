BEGIN;

ALTER TABLE codalpy_records ADD COLUMN IF NOT EXISTS symbol text;

UPDATE codalpy_records r
SET symbol=n.symbol
FROM codal_notice_events n
WHERE r.symbol IS NULL AND n.tracing_no=r.tracing_no;

UPDATE codalpy_records r
SET symbol=sa.symbol
FROM disclosures d
JOIN instruments i ON i.id=d.instrument_id
JOIN symbol_aliases sa ON sa.instrument_id=i.id AND sa.valid_to IS NULL
WHERE r.symbol IS NULL
  AND split_part(d.source_disclosure_id, ':', 1)=r.tracing_no;

CREATE INDEX IF NOT EXISTS codalpy_records_symbol_monthly_idx
  ON codalpy_records(symbol,period_end_jalali,tracing_no)
  WHERE output_type='monthly_activity';

COMMIT;
