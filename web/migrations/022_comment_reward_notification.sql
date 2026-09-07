BEGIN;
ALTER TABLE user_notifications DROP CONSTRAINT IF EXISTS user_notifications_kind_check;
ALTER TABLE user_notifications ADD CONSTRAINT user_notifications_kind_check CHECK(kind IN ('comment_reply','comment_reward','stock_update'));
INSERT INTO schema_migrations(version) VALUES ('022_comment_reward_notification') ON CONFLICT DO NOTHING;
COMMIT;
