BEGIN;

CREATE TABLE IF NOT EXISTS comment_likes (
  comment_id uuid NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(comment_id,user_id)
);
CREATE TABLE IF NOT EXISTS comment_reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  comment_id uuid NOT NULL REFERENCES comments(id) ON DELETE CASCADE,
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  reason text NOT NULL DEFAULT 'نامناسب',
  status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','reviewed','dismissed')),
  created_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE(comment_id,user_id)
);
CREATE TABLE IF NOT EXISTS stock_follows (
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  symbol varchar(32) NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY(user_id,symbol)
);
CREATE TABLE IF NOT EXISTS user_notifications (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  kind text NOT NULL CHECK(kind IN ('comment_reply','stock_update')),
  title text NOT NULL,
  body text NOT NULL,
  target_url text,
  read_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS user_notifications_unread_idx ON user_notifications(user_id,read_at,created_at DESC);
INSERT INTO schema_migrations(version) VALUES ('016_stock_community') ON CONFLICT DO NOTHING;
COMMIT;
