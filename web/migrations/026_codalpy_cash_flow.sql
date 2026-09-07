BEGIN;

ALTER TABLE codalpy_records
  DROP CONSTRAINT IF EXISTS codalpy_records_output_type_check;

ALTER TABLE codalpy_records
  ADD CONSTRAINT codalpy_records_output_type_check
  CHECK(output_type IN ('income_statement','balance_sheet','cash_flow','monthly_activity'));

COMMIT;
