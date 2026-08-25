BEGIN;
CREATE TABLE IF NOT EXISTS comment_automation_actions (
  comment_id uuid PRIMARY KEY REFERENCES comments(id) ON DELETE CASCADE,
  quality_score integer NOT NULL CHECK (quality_score BETWEEN 0 AND 100),
  action_kind text NOT NULL CHECK (action_kind IN ('feedback_logged','task_candidate','safety_review')),
  reward_credits integer NOT NULL DEFAULT 0 CHECK (reward_credits >= 0),
  reply_comment_id uuid REFERENCES comments(id) ON DELETE SET NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS comment_automation_action_kind_idx ON comment_automation_actions(action_kind, created_at DESC);
INSERT INTO schema_migrations(version) VALUES ('019_comment_automation') ON CONFLICT DO NOTHING;
COMMIT;
