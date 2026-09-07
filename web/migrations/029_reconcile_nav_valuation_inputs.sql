-- Reconcile legacy NAV rows against the curated browser/Codal evidence.
-- Run only after a database backup; this preserves the superseded original as REJECTED.
BEGIN;

UPDATE valuation_inputs
SET source_disclosure_id = '1516095:nav_per_share:1404/11/30',
    normalized_unit = 'IRR', quality_status = 'VALID',
    content_checksum = '0b831042a8acef38538061c17c94b76f4ebdd2e99cbe606269d50ba94af275b6'
WHERE input_key = 'nav_per_share' AND source = 'browser/codal.ir'
  AND source_disclosure_id = '1516095:balance_sheet';

UPDATE valuation_inputs
SET source_disclosure_id = '1457062:nav_per_share:1404/08/22',
    normalized_unit = 'IRR', quality_status = 'VALID',
    content_checksum = '84f5f7100937a0214b39fd8db56c84a9009acdf5c98c6d52ddce6652546aad13'
WHERE input_key = 'nav_per_share' AND source = 'browser/codal.ir'
  AND source_disclosure_id = '1457062:balance_sheet';

UPDATE valuation_inputs
SET source_disclosure_id = '1572614:nav_per_share:1405/03/31',
    normalized_unit = 'IRR', quality_status = 'VALID',
    content_checksum = '9267c6f90dcba794943cddd8ad11edb2553b6e7b4ef128fb0cd710f563b6a34'
WHERE input_key = 'nav_per_share' AND source = 'browser/codal.ir'
  AND source_disclosure_id = '1572614:balance_sheet';

UPDATE valuation_inputs
SET source_disclosure_id = '1573834:nav_per_share:1405/03/31',
    normalized_unit = 'IRR', quality_status = 'VALID',
    content_checksum = '264804136ae0d774005f36d4a80062e91ffe78d8514c977ce3197f3c27605937'
WHERE input_key = 'nav_per_share' AND source = 'browser/codal.ir'
  AND source_disclosure_id = '1573834:balance_sheet';

UPDATE valuation_inputs
SET source_disclosure_id = '1573540:nav_per_share:1405/03/31',
    quality_status = 'REJECTED'
WHERE input_key = 'nav_per_share' AND source = 'browser/codal.ir'
  AND source_disclosure_id = '1573540:balance_sheet';

COMMIT;
