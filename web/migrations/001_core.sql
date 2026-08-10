BEGIN;

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE TABLE IF NOT EXISTS schema_migrations (
  version text PRIMARY KEY,
  applied_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS roles (
  id smallserial PRIMARY KEY,
  code text NOT NULL UNIQUE CHECK (code ~ '^[a-z_]+$'),
  title_fa text NOT NULL
);
INSERT INTO roles(code, title_fa) VALUES ('user','کاربر'),('admin','مدیر') ON CONFLICT DO NOTHING;

CREATE TABLE IF NOT EXISTS users (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mobile_e164 varchar(13) NOT NULL UNIQUE CHECK (mobile_e164 ~ '^\+989[0-9]{9}$'),
  role_id smallint NOT NULL REFERENCES roles(id),
  status text NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','deleted')),
  referral_code varchar(16) NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS mobile_identities (
  user_id uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  mobile_e164 varchar(13) NOT NULL UNIQUE,
  verified_at timestamptz NOT NULL,
  last_login_at timestamptz
);

CREATE TABLE IF NOT EXISTS otp_requests (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  mobile_e164 varchar(13) NOT NULL,
  code_hash char(64) NOT NULL,
  expires_at timestamptz NOT NULL,
  attempts smallint NOT NULL DEFAULT 0 CHECK (attempts >= 0),
  max_attempts smallint NOT NULL DEFAULT 5,
  consumed_at timestamptz,
  locked_until timestamptz,
  request_ip inet NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS otp_mobile_created_idx ON otp_requests(mobile_e164, created_at DESC);
CREATE INDEX IF NOT EXISTS otp_ip_created_idx ON otp_requests(request_ip, created_at DESC);

CREATE TABLE IF NOT EXISTS otp_attempts (
  id bigserial PRIMARY KEY,
  otp_request_id uuid NOT NULL REFERENCES otp_requests(id) ON DELETE CASCADE,
  success boolean NOT NULL,
  attempt_ip inet NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS sessions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  token_hash char(64) NOT NULL UNIQUE,
  csrf_hash char(64) NOT NULL,
  expires_at timestamptz NOT NULL,
  revoked_at timestamptz,
  created_ip inet NOT NULL,
  user_agent_hash char(64),
  created_at timestamptz NOT NULL DEFAULT now(),
  last_seen_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS sessions_user_active_idx ON sessions(user_id, expires_at) WHERE revoked_at IS NULL;

CREATE TABLE IF NOT EXISTS plans (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  code text NOT NULL UNIQUE CHECK (code IN ('free','1_month','3_months','12_months')),
  title_fa text NOT NULL,
  duration_days integer NOT NULL CHECK (duration_days >= 0),
  price_toman bigint NOT NULL CHECK (price_toman >= 0),
  analysis_credits integer NOT NULL CHECK (analysis_credits >= 0),
  active boolean NOT NULL DEFAULT true,
  updated_at timestamptz NOT NULL DEFAULT now()
);
INSERT INTO plans(code,title_fa,duration_days,price_toman,analysis_credits) VALUES
('free','رایگان',0,0,5),('1_month','یک‌ماهه',30,0,0),('3_months','سه‌ماهه',90,0,0),('12_months','یک‌ساله',365,0,0)
ON CONFLICT (code) DO NOTHING;

CREATE TABLE IF NOT EXISTS subscriptions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id),
  plan_id uuid NOT NULL REFERENCES plans(id),
  status text NOT NULL CHECK (status IN ('pending','active','expired','cancelled')),
  starts_at timestamptz,
  ends_at timestamptz,
  created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS analysis_credits (
  user_id uuid PRIMARY KEY REFERENCES users(id) ON DELETE CASCADE,
  balance integer NOT NULL DEFAULT 0 CHECK (balance >= 0),
  updated_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS credit_ledger (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id),
  delta integer NOT NULL CHECK (delta <> 0),
  balance_after integer NOT NULL CHECK (balance_after >= 0),
  reason text NOT NULL CHECK (reason IN ('welcome','analysis','purchase','referral','campaign','admin_adjustment','rollback')),
  reference_type text,
  reference_id text,
  idempotency_key text NOT NULL UNIQUE,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS credit_ledger_user_idx ON credit_ledger(user_id, created_at DESC);

CREATE OR REPLACE FUNCTION deny_credit_ledger_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN RAISE EXCEPTION 'credit_ledger is append-only'; END $$;
DROP TRIGGER IF EXISTS credit_ledger_immutable ON credit_ledger;
CREATE TRIGGER credit_ledger_immutable BEFORE UPDATE OR DELETE ON credit_ledger
FOR EACH ROW EXECUTE FUNCTION deny_credit_ledger_mutation();

CREATE TABLE IF NOT EXISTS analysis_history (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES users(id),
  symbol varchar(32) NOT NULL,
  report_mode text NOT NULL CHECK (report_mode IN ('audited','latest_codal')),
  result jsonb NOT NULL,
  source_metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS analysis_history_user_idx ON analysis_history(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS payment_submissions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id),
  plan_id uuid REFERENCES plans(id), amount_toman bigint NOT NULL CHECK(amount_toman > 0),
  tracking_number varchar(80) NOT NULL, paid_at timestamptz NOT NULL,
  receipt_storage_key text NOT NULL, receipt_mime text NOT NULL,
  status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','approved','rejected')),
  created_at timestamptz NOT NULL DEFAULT now(), UNIQUE(user_id, tracking_number)
);
CREATE TABLE IF NOT EXISTS payment_approvals (
  payment_id uuid PRIMARY KEY REFERENCES payment_submissions(id), admin_user_id uuid NOT NULL REFERENCES users(id),
  decision text NOT NULL CHECK(decision IN ('approved','rejected')), note text, created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS promotions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), code text NOT NULL UNIQUE, title_fa text NOT NULL,
  starts_at timestamptz NOT NULL, ends_at timestamptz NOT NULL, capacity integer,
  credit_amount integer NOT NULL CHECK(credit_amount >= 0), price_toman bigint CHECK(price_toman >= 0),
  active boolean NOT NULL DEFAULT false, rules jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE TABLE IF NOT EXISTS referrals (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), referrer_user_id uuid NOT NULL REFERENCES users(id),
  referred_user_id uuid NOT NULL UNIQUE REFERENCES users(id), status text NOT NULL DEFAULT 'pending' CHECK(status IN ('pending','qualified','rewarded','rejected')),
  rewarded_at timestamptz, created_at timestamptz NOT NULL DEFAULT now(), CHECK(referrer_user_id <> referred_user_id)
);

CREATE TABLE IF NOT EXISTS alerts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid NOT NULL REFERENCES users(id), symbol varchar(32) NOT NULL,
  kind text NOT NULL CHECK(kind IN ('price','pe','codal')), comparator text CHECK(comparator IN ('gte','lte')),
  target_value numeric, active boolean NOT NULL DEFAULT true, last_trigger_key text, created_at timestamptz NOT NULL DEFAULT now(),
  CHECK ((kind='codal' AND target_value IS NULL) OR (kind<>'codal' AND target_value IS NOT NULL))
);
CREATE INDEX IF NOT EXISTS alerts_active_idx ON alerts(active, kind, symbol);

CREATE TABLE IF NOT EXISTS sms_delivery_attempts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(), user_id uuid REFERENCES users(id), mobile_e164 varchar(13) NOT NULL,
  purpose text NOT NULL CHECK(purpose IN ('otp','alert')), provider_message_id text, status text NOT NULL,
  error_code text, deduplication_key text UNIQUE, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS admin_audit_logs (
  id bigserial PRIMARY KEY, admin_user_id uuid REFERENCES users(id), action text NOT NULL, target_type text,
  target_id text, metadata jsonb NOT NULL DEFAULT '{}'::jsonb, ip inet NOT NULL, created_at timestamptz NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS system_settings (
  key text PRIMARY KEY, value jsonb NOT NULL, is_public boolean NOT NULL DEFAULT false,
  updated_by uuid REFERENCES users(id), updated_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO schema_migrations(version) VALUES ('001_core') ON CONFLICT DO NOTHING;
COMMIT;
