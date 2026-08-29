BEGIN;
GRANT SELECT, INSERT ON TABLE comment_automation_actions TO boursnegar;
INSERT INTO schema_migrations(version) VALUES ('023_comment_automation_permissions') ON CONFLICT DO NOTHING;
COMMIT;
