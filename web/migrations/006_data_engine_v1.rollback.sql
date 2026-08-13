BEGIN;
-- Safe only before v1 ingestion. Production rollback after writes must preserve/export v1 data.
DROP TABLE IF EXISTS analysis_usage, recommendation_results, valuation_results, health_score_results,
  analytical_snapshots, industry_model_policies, recommendation_policies, source_lineage,
  data_quality_issues, ingestion_dead_letters, ingestion_checkpoints, ingestion_runs,
  macro_observations, macro_series, daily_prices, corporate_actions, production_metrics,
  monthly_sales, statement_line_items, financial_facts, financial_periods, parser_versions,
  raw_documents, disclosure_versions, disclosures, symbol_aliases, instruments, issuers, industries;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS purchased_price_toman;
ALTER TABLE subscriptions DROP COLUMN IF EXISTS entitlement_snapshot;
ALTER TABLE plans DROP COLUMN IF EXISTS publicly_visible;
ALTER TABLE plans DROP COLUMN IF EXISTS sale_ends_at;
ALTER TABLE plans DROP COLUMN IF EXISTS sale_starts_at;
ALTER TABLE plans DROP COLUMN IF EXISTS discount;
ALTER TABLE plans DROP COLUMN IF EXISTS display_order;
ALTER TABLE plans DROP COLUMN IF EXISTS features;
ALTER TABLE plans DROP COLUMN IF EXISTS unlimited_analyses;
ALTER TABLE plans DROP COLUMN IF EXISTS description_fa;
DELETE FROM schema_migrations WHERE version='006_data_engine_v1';
COMMIT;
