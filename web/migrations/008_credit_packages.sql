BEGIN;

UPDATE plans
SET active=false, publicly_visible=false, updated_at=now()
WHERE code IN ('1_month','3_months','12_months');

INSERT INTO plans(
  code,title_fa,description_fa,duration_days,price_toman,analysis_credits,
  unlimited_analyses,features,active,display_order,publicly_visible
)
SELECT
  'credits_' || credits,
  credits::text || ' تحلیل',
  'بسته اعتباری بدون تاریخ انقضا؛ فعال‌سازی پس از تأیید رسید کارت‌به‌کارت.',
  0,
  (credits - 1) * 100000,
  credits,
  false,
  to_jsonb(ARRAY['بدون تاریخ انقضا','ثبت رسید کارت‌به‌کارت','فعال‌سازی پس از تأیید مدیر']),
  true,
  credits,
  true
FROM generate_series(6,20) AS credits
ON CONFLICT(code) DO UPDATE SET
  title_fa=excluded.title_fa,
  description_fa=excluded.description_fa,
  duration_days=excluded.duration_days,
  price_toman=excluded.price_toman,
  analysis_credits=excluded.analysis_credits,
  unlimited_analyses=excluded.unlimited_analyses,
  features=excluded.features,
  active=excluded.active,
  display_order=excluded.display_order,
  publicly_visible=excluded.publicly_visible,
  updated_at=now();

INSERT INTO schema_migrations(version)
VALUES ('008_credit_packages')
ON CONFLICT DO NOTHING;

COMMIT;
