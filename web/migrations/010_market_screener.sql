CREATE INDEX CONCURRENTLY IF NOT EXISTS daily_prices_date_instrument_idx
  ON daily_prices(trading_date DESC,instrument_id)
  INCLUDE(adjusted_close,close,volume,value,trade_count)
  WHERE quality_status='VALID';
INSERT INTO schema_migrations(version) VALUES ('010_market_screener') ON CONFLICT DO NOTHING;
