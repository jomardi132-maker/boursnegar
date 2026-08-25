BEGIN;

ALTER TABLE financial_periods
  DROP CONSTRAINT IF EXISTS financial_periods_scope_check;

ALTER TABLE financial_periods
  ADD CONSTRAINT financial_periods_scope_check
  CHECK (scope IN ('separate', 'consolidated', 'unknown'));

COMMIT;
