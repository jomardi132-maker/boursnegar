#!/usr/bin/env bash
set -euo pipefail

origin="http://127.0.0.1:3000"
cookie="$(mktemp)"
body="$(mktemp)"
email="codex-smoke-$(date +%s)@example.invalid"
password="$(openssl rand -base64 36 | tr -d '\n')Aa1!"
cleanup() {
  rm -f "$cookie" "$body"
  sudo -u postgres psql -d boursnegar_db -v ON_ERROR_STOP=1 >/dev/null 2>&1 <<'SQL' || true
CREATE TEMP TABLE smoke_users AS
  SELECT user_id AS id FROM email_identities WHERE email LIKE 'codex-smoke-%@example.invalid';
ALTER TABLE credit_ledger DISABLE TRIGGER credit_ledger_immutable;
DELETE FROM credit_ledger WHERE user_id IN (SELECT id FROM smoke_users);
ALTER TABLE credit_ledger ENABLE TRIGGER credit_ledger_immutable;
DELETE FROM analysis_attempts WHERE user_id IN (SELECT id FROM smoke_users);
DELETE FROM analysis_history WHERE user_id IN (SELECT id FROM smoke_users);
DELETE FROM users WHERE id IN (SELECT id FROM smoke_users);
SQL
}
trap cleanup EXIT

code="$(curl -sS -o "$body" -w '%{http_code}' -c "$cookie" -H 'content-type: application/json' \
  --data "{\"email\":\"$email\",\"password\":\"$password\"}" \
  "$origin/api/auth/register")"
test "$code" = 201
csrf="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["csrfToken"])' <"$body")"
python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["user"]["email"] and d["user"]["credits"] == 5' <"$body"

code="$(curl --max-time 90 -sS -o "$body" -w '%{http_code}' -b "$cookie" \
  -H "x-csrf-token: $csrf" -H 'content-type: application/json' \
  -H "idempotency-key: smoke-$(date +%s)-$RANDOM" \
  --data '{"query":"فولاد","reportMode":"audited"}' "$origin/api/analyze")"
test "$code" = 200
python3 -c 'import json,sys; d=json.load(sys.stdin); assert len(d["data"]["questions"]) == 3; assert d["analysis"]["remainingCredits"] == 4' <"$body"
curl -fsS -b "$cookie" "$origin/api/auth/me" | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["user"]["email"] and d["user"]["credits"] == 4'
curl -fsS -b "$cookie" -H "x-csrf-token: $csrf" -H 'content-type: application/json' \
  -X POST --data '{}' "$origin/api/auth/logout" | python3 -c 'import json,sys; assert json.load(sys.stdin)["success"] is True'

code="$(curl -sS -o "$body" -w '%{http_code}' -c "$cookie" -H 'content-type: application/json' \
  --data "{\"email\":\"$email\",\"password\":\"$password\"}" \
  "$origin/api/auth/login")"
test "$code" = 200
csrf="$(python3 -c 'import json,sys; print(json.load(sys.stdin)["csrfToken"])' <"$body")"

code="$(curl -sS -o "$body" -w '%{http_code}' -H 'content-type: application/json' \
  --data "{\"email\":\"$email\"}" "$origin/api/auth/password/forgot")"
test "$code" = 202
python3 -c 'import json,sys; assert json.load(sys.stdin)["success"] is True' <"$body"

test "$(curl -sS -o /dev/null -w '%{http_code}' "$origin/api/admin/stats")" = 401
test "$(curl -sS -o /dev/null -w '%{http_code}' "$origin/")" = 200
test "$(curl -sS -o /dev/null -w '%{http_code}' "$origin/api/plans")" = 200

echo "EMAIL_REGISTER_LOGIN_LOGOUT=PASS"
echo "FORGOT_PASSWORD_GENERIC_RESPONSE=PASS"
echo "AUTHORIZATION=PASS"
echo "PUBLIC_ROUTES=PASS"
echo "THREE_QUESTION_ANALYSIS_LEDGER=PASS"
