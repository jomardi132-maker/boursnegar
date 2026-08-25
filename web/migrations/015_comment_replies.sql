BEGIN;
ALTER TABLE comments ADD COLUMN IF NOT EXISTS parent_id uuid REFERENCES comments(id) ON DELETE CASCADE;
CREATE INDEX IF NOT EXISTS comments_parent_idx ON comments(parent_id, created_at ASC);
INSERT INTO schema_migrations(version) VALUES ('015_comment_replies') ON CONFLICT DO NOTHING;
COMMIT;
