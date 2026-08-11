#!/usr/bin/env bash
set -euo pipefail

origin="http://127.0.0.1:3000"
recipient_file="/tmp/boursnegar-test-email.input"
token_file="/tmp/boursnegar-e2e-reset-token"
test -s "$recipient_file"
chmod 600 "$recipient_file"
email="$(cat "$recipient_file")"
[[ "$email" =~ ^[^[:space:]@]+@[^[:space:]@]+\.[^[:space:]@]+$ ]]
old_password="$(openssl rand -base64 36 | tr -d '\n')Aa1!"
new_password="$(openssl rand -base64 36 | tr -d '\n')Bb2!"
cookie="$(mktemp)"
body="$(mktemp)"
body_other="$(mktemp)"

cleanup() {
  rm -f "$cookie" "$body" "$body_other" "$token_file" "$recipient_file"
  sudo -u postgres psql -d boursnegar_db -v ON_ERROR_STOP=1 -v test_email="$email" >/dev/null 2>&1 <<'SQL' || true
CREATE TEMP TABLE reset_test_users AS
  SELECT user_id AS id FROM email_identities WHERE email=:'test_email';
BEGIN;
ALTER TABLE credit_ledger DISABLE TRIGGER credit_ledger_immutable;
DELETE FROM credit_ledger WHERE user_id IN (SELECT id FROM reset_test_users);
ALTER TABLE credit_ledger ENABLE TRIGGER credit_ledger_immutable;
DELETE FROM analysis_attempts WHERE user_id IN (SELECT id FROM reset_test_users);
DELETE FROM analysis_history WHERE user_id IN (SELECT id FROM reset_test_users);
DELETE FROM users WHERE id IN (SELECT id FROM reset_test_users);
COMMIT;
SQL
}
trap cleanup EXIT

existing="$(sudo -u postgres psql -At -d boursnegar_db -v test_email="$email" -c "SELECT count(*) FROM email_identities WHERE email=:'test_email';")"
test "$existing" = 0
audit_before="$(sudo -u postgres psql -At -d boursnegar_db -c "SELECT count(*) FROM admin_audit_logs WHERE action LIKE 'password_reset_%';")"

code="$(curl -sS -o "$body" -w '%{http_code}' -c "$cookie" -H 'content-type: application/json' \
  --data "{\"email\":\"$email\",\"password\":\"$old_password\"}" "$origin/api/auth/register")"
test "$code" = 201
csrf="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["csrfToken"])' <"$body")"

code="$(curl -sS -o "$body" -w '%{http_code}' -H 'content-type: application/json' \
  --data "{\"email\":\"$email\"}" "$origin/api/auth/password/forgot")"
test "$code" = 202
code="$(curl -sS -o "$body_other" -w '%{http_code}' -H 'content-type: application/json' \
  --data '{"email":"does-not-exist-reset-test@example.invalid"}' "$origin/api/auth/password/forgot")"
test "$code" = 202
cmp -s "$body" "$body_other"

npx tsx scripts/create-e2e-reset.ts send
test -s "$token_file"
token="$(cat "$token_file")"
code="$(curl -sS -o "$body" -w '%{http_code}' -H 'content-type: application/json' \
  --data "{\"token\":\"$token\",\"password\":\"$new_password\"}" "$origin/api/auth/password/reset")"
test "$code" = 200

test "$(curl -sS -o /dev/null -w '%{http_code}' -b "$cookie" "$origin/api/auth/me")" = 401
test "$(curl -sS -o /dev/null -w '%{http_code}' -H 'content-type: application/json' \
  --data "{\"token\":\"$token\",\"password\":\"$old_password\"}" "$origin/api/auth/password/reset")" = 400
test "$(curl -sS -o /dev/null -w '%{http_code}' -H 'content-type: application/json' \
  --data "{\"email\":\"$email\",\"password\":\"$old_password\"}" "$origin/api/auth/login")" = 401
test "$(curl -sS -o "$body" -w '%{http_code}' -H 'content-type: application/json' \
  --data "{\"email\":\"$email\",\"password\":\"$new_password\"}" "$origin/api/auth/login")" = 200

npx tsx scripts/create-e2e-reset.ts no-send
sudo -u postgres psql -d boursnegar_db -v ON_ERROR_STOP=1 -v test_email="$email" \
  -c "UPDATE password_reset_tokens SET expires_at=now()-interval '1 second' WHERE id=(SELECT p.id FROM password_reset_tokens p JOIN email_identities e ON e.user_id=p.user_id WHERE e.email=:'test_email' ORDER BY p.created_at DESC LIMIT 1);" >/dev/null
token="$(cat "$token_file")"
test "$(curl -sS -o /dev/null -w '%{http_code}' -H 'content-type: application/json' \
  --data "{\"token\":\"$token\",\"password\":\"$old_password\"}" "$origin/api/auth/password/reset")" = 400

rate_limited=false
for _ in 1 2 3 4 5 6; do
  status="$(curl -sS -o /dev/null -w '%{http_code}' -H 'content-type: application/json' \
    --data '{"email":"rate-limit-reset-test@example.invalid"}' "$origin/api/auth/password/forgot")"
  if [ "$status" = 429 ]; then rate_limited=true; fi
done
test "$rate_limited" = true

audit_after="$(sudo -u postgres psql -At -d boursnegar_db -c "SELECT count(*) FROM admin_audit_logs WHERE action LIKE 'password_reset_%';")"
test "$audit_after" -gt "$audit_before"
sudo -u postgres psql -At -d boursnegar_db -v test_email="$email" <<'SQL' | grep -qx '1|0|1'
SELECT
  (SELECT count(*) FROM admin_audit_logs WHERE action='password_reset_completed' AND target_id=(SELECT user_id::text FROM email_identities WHERE email=:'test_email'))
  || '|' ||
  (SELECT count(*) FROM sessions s JOIN email_identities e ON e.user_id=s.user_id WHERE e.email=:'test_email' AND s.revoked_at IS NULL AND s.created_at < e.password_changed_at)
  || '|' ||
  (SELECT count(*) FROM email_identities WHERE email=:'test_email' AND password_changed_at > created_at);
SQL

unset email old_password new_password token csrf
echo GENERIC_FORGOT_RESPONSE=PASS
echo RESET_LINK_SINGLE_USE=PASS
echo RESET_EXPIRY=PASS
echo SESSION_REVOCATION=PASS
echo NEW_PASSWORD_LOGIN=PASS
echo RATE_LIMIT=PASS
echo AUDIT_LOG=PASS
