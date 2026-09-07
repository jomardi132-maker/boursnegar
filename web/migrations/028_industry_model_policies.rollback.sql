BEGIN;
DELETE FROM industry_model_policies WHERE version='industry-family-v1';
DELETE FROM schema_migrations WHERE version='028_industry_model_policies';
COMMIT;
