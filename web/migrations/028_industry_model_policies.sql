-- Versioned registry for the explicit model families in industry_valuation.py.
-- These are internal scenario policies, not market-consensus claims.
BEGIN;

INSERT INTO industry_model_policies
  (industry_id, version, model_type, status, assumptions, effective_from)
SELECT i.id, 'industry-family-v1', v.model_type, 'ACTIVE', v.assumptions::jsonb, now()
FROM industries i
JOIN (VALUES
  ('bank', 'price_to_book', '{"multiple":1.0,"downside":0.20,"upside":0.15}'::text),
  ('cement', 'normalized_pe', '{"multiple":7.0,"downside":0.20,"upside":0.20}'::text),
  ('ceramics', 'normalized_pe', '{"multiple":7.0,"downside":0.20,"upside":0.20}'::text),
  ('financial', 'price_to_book', '{"multiple":0.9,"downside":0.25,"upside":0.20}'::text),
  ('food', 'normalized_pe', '{"multiple":7.0,"downside":0.20,"upside":0.20}'::text),
  ('fund', 'nav', '{"multiple":1.0,"downside":0.20,"upside":0.20}'::text),
  ('general', 'normalized_pe', '{"multiple":5.0,"downside":0.25,"upside":0.25}'::text),
  ('holding', 'price_to_book', '{"multiple":1.0,"downside":0.30,"upside":0.20}'::text),
  ('metals', 'normalized_pe', '{"multiple":6.0,"downside":0.20,"upside":0.20}'::text),
  ('petrochemical', 'normalized_pe', '{"multiple":6.5,"downside":0.20,"upside":0.20}'::text),
  ('pharmaceutical', 'normalized_pe', '{"multiple":7.0,"downside":0.20,"upside":0.20}'::text),
  ('real_estate', 'price_to_book', '{"multiple":1.0,"downside":0.25,"upside":0.25}'::text)
) AS v(model_family, model_type, assumptions) ON i.model_family = v.model_family
ON CONFLICT (industry_id, version, model_type) DO NOTHING;

INSERT INTO schema_migrations(version)
VALUES ('028_industry_model_policies')
ON CONFLICT (version) DO NOTHING;

COMMIT;
