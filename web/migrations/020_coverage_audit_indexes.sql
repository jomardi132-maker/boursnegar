BEGIN;

-- Keep evidence/coverage queries bounded as the raw Codalpy mirror grows.
CREATE INDEX IF NOT EXISTS financial_facts_valid_period_idx
  ON financial_facts(period_id)
  WHERE quality_status = 'VALID';
CREATE INDEX IF NOT EXISTS codalpy_records_linked_symbol_idx
  ON codalpy_records(symbol)
  WHERE symbol IS NOT NULL;
CREATE INDEX IF NOT EXISTS codalpy_records_output_linked_symbol_idx
  ON codalpy_records(output_type, symbol)
  WHERE symbol IS NOT NULL;
CREATE INDEX IF NOT EXISTS daily_prices_valid_quality_idx
  ON daily_prices(quality_status)
  WHERE quality_status = 'VALID';

INSERT INTO schema_migrations(version)
VALUES ('020_coverage_audit_indexes')
ON CONFLICT DO NOTHING;
COMMIT;
