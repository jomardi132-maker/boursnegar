BEGIN;
CREATE INDEX IF NOT EXISTS comment_rewards_created_idx ON comment_rewards(created_at DESC);
CREATE INDEX IF NOT EXISTS comments_user_created_idx ON comments(user_id,created_at DESC);
INSERT INTO schema_migrations(version) VALUES ('024_comment_reward_indexes') ON CONFLICT DO NOTHING;
COMMIT;
