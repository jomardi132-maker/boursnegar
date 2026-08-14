BEGIN;

CREATE EXTENSION IF NOT EXISTS pg_trgm;

CREATE INDEX IF NOT EXISTS symbol_aliases_symbol_trgm_idx
ON symbol_aliases USING gin (symbol gin_trgm_ops);

CREATE INDEX IF NOT EXISTS issuers_legal_name_trgm_idx
ON issuers USING gin (legal_name gin_trgm_ops);

INSERT INTO schema_migrations(version)
VALUES ('009_symbol_search')
ON CONFLICT DO NOTHING;

COMMIT;
