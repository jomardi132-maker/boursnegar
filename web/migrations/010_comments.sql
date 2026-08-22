BEGIN;
CREATE TABLE IF NOT EXISTS comments (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  kind text NOT NULL CHECK (kind IN ('site_feedback','symbol_comment')),
  symbol varchar(32),
  body text NOT NULL CHECK (length(body) BETWEEN 3 AND 2000),
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','published','hidden','rejected')),
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now(),
  CHECK ((kind='site_feedback' AND symbol IS NULL) OR (kind='symbol_comment' AND symbol IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS comments_public_idx ON comments(kind,symbol,status,created_at DESC);
CREATE TABLE IF NOT EXISTS comment_rewards (
  comment_id uuid PRIMARY KEY REFERENCES comments(id) ON DELETE CASCADE,
  admin_user_id uuid NOT NULL REFERENCES users(id),
  credits integer NOT NULL CHECK (credits > 0),
  created_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO schema_migrations(version) VALUES ('010_comments') ON CONFLICT DO NOTHING;
COMMIT;
