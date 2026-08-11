CREATE TEMP TABLE reset_test_users AS
  SELECT user_id AS id FROM email_identities WHERE email=:'test_email';
BEGIN;
ALTER TABLE credit_ledger DISABLE TRIGGER credit_ledger_immutable;
DELETE FROM credit_ledger WHERE user_id IN (SELECT id FROM reset_test_users);
ALTER TABLE credit_ledger ENABLE TRIGGER credit_ledger_immutable;
DELETE FROM analysis_attempts WHERE user_id IN (SELECT id FROM reset_test_users);
DELETE FROM analysis_history WHERE user_id IN (SELECT id FROM reset_test_users);
DELETE FROM users WHERE id IN (SELECT id FROM reset_test_users);
COMMIT;
