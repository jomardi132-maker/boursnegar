BEGIN;
DROP INDEX IF EXISTS financial_facts_valid_period_idx;
DROP INDEX IF EXISTS codalpy_records_linked_symbol_idx;
DROP INDEX IF EXISTS codalpy_records_output_linked_symbol_idx;
DROP INDEX IF EXISTS daily_prices_valid_quality_idx;
DELETE FROM schema_migrations WHERE version='020_coverage_audit_indexes';
COMMIT;
