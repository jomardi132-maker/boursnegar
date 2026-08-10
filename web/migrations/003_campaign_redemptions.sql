BEGIN;

ALTER TABLE payment_submissions
  ADD COLUMN IF NOT EXISTS promotion_id uuid REFERENCES promotions(id);

CREATE TABLE IF NOT EXISTS promotion_redemptions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  promotion_id uuid NOT NULL REFERENCES promotions(id),
  user_id uuid NOT NULL REFERENCES users(id),
  payment_id uuid REFERENCES payment_submissions(id),
  credits_awarded integer NOT NULL CHECK (credits_awarded >= 0),
  redeemed_at timestamptz NOT NULL DEFAULT now(),
  UNIQUE (promotion_id, user_id),
  UNIQUE (payment_id)
);
CREATE INDEX IF NOT EXISTS promotion_redemptions_campaign_idx
  ON promotion_redemptions(promotion_id, redeemed_at);

INSERT INTO schema_migrations(version) VALUES ('003_campaign_redemptions')
ON CONFLICT DO NOTHING;
COMMIT;
