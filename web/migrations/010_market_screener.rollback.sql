DROP INDEX CONCURRENTLY IF EXISTS daily_prices_date_instrument_idx;
DELETE FROM schema_migrations WHERE version='010_market_screener';
