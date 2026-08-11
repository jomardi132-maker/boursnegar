CREATE TEMP TABLE smoke_users AS
  SELECT user_id AS id FROM email_identities WHERE email LIKE 'codex-smoke-%@example.invalid';
BEGIN;
ALTER TABLE credit_ledger DISABLE TRIGGER credit_ledger_immutable;
DELETE FROM credit_ledger WHERE user_id IN (SELECT id FROM smoke_users);
ALTER TABLE credit_ledger ENABLE TRIGGER credit_ledger_immutable;
DELETE FROM analysis_attempts WHERE user_id IN (SELECT id FROM smoke_users);
DELETE FROM analysis_history WHERE user_id IN (SELECT id FROM smoke_users);
DELETE FROM users WHERE id IN (SELECT id FROM smoke_users);
COMMIT;

SELECT tracing_no, period_end_date, publish_datetime, left(title, 100)
FROM financial_reports
WHERE company_id=(SELECT id FROM companies WHERE symbol='فولاد')
ORDER BY publish_datetime DESC
LIMIT 20;
