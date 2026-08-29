-- Evidence-backed alerts use the persisted valuation range; no user target is needed.
ALTER TABLE alerts DROP CONSTRAINT IF EXISTS alerts_kind_check;
ALTER TABLE alerts DROP CONSTRAINT IF EXISTS alerts_check;
ALTER TABLE alerts ADD CONSTRAINT alerts_kind_check CHECK(kind IN ('price','pe','codal','buy_zone','sell_zone'));
ALTER TABLE alerts ADD CONSTRAINT alerts_target_check CHECK (
  (kind IN ('codal','buy_zone','sell_zone') AND target_value IS NULL)
  OR (kind IN ('price','pe') AND target_value IS NOT NULL)
);
