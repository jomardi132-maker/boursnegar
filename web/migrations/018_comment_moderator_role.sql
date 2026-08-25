BEGIN;
INSERT INTO roles(code, title_fa)
VALUES ('comment_moderator', 'مدیر نظرات')
ON CONFLICT (code) DO UPDATE SET title_fa = EXCLUDED.title_fa;
INSERT INTO schema_migrations(version)
VALUES ('018_comment_moderator_role') ON CONFLICT DO NOTHING;
COMMIT;
