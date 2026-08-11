#!/usr/bin/env bash
set -euo pipefail

pm2 restart bourse-app --update-env >/dev/null
pm2 save --force >/dev/null
for attempt in $(seq 1 15); do
  if curl -fsS http://127.0.0.1:3000/healthz >/dev/null; then break; fi
  sleep 2
  test "$attempt" -ne 15
done

curl -fsS http://127.0.0.1:3000/healthz | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d=={"status":"ok","auth":"email_password"}'
curl -fsS http://127.0.0.1:3000/readyz | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ready" and d["mail"]=="ready"'
curl -fsS http://127.0.0.1:8001/health | python3 -c 'import json,sys; assert json.load(sys.stdin)["status"]=="ok"'
curl -fsS https://boursnegar.ir/healthz | python3 -c 'import json,sys; assert json.load(sys.stdin)["status"]=="ok"'
curl -fsS https://boursnegar.ir/readyz | python3 -c 'import json,sys; assert json.load(sys.stdin)["mail"]=="ready"'
test "$(curl -sS -o /dev/null -w '%{http_code}' https://boursnegar.ir/)" = 200
test "$(curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:3000/api/plans)" = 200
test "$(curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:3000/api/auth/me)" = 401
test "$(curl -sS -o /dev/null -w '%{http_code}' http://127.0.0.1:3000/api/admin/stats)" = 401
test "$(curl -sS -o /dev/null -w '%{http_code}' -H 'content-type: application/json' --data '{"email":"missing-final-smoke@example.invalid"}' http://127.0.0.1:3000/api/auth/password/forgot)" = 202

sudo -u postgres psql -At -d boursnegar_db <<'SQL' | grep -qx '1|1|1|0|0'
SELECT
  (SELECT count(*) FROM schema_migrations WHERE version='005_email_password_auth')
  || '|' ||
  (SELECT CASE WHEN count(*)>0 THEN 1 ELSE 0 END FROM admin_audit_logs WHERE action='password_reset_completed')
  || '|' ||
  (SELECT CASE WHEN count(*)>0 THEN 1 ELSE 0 END FROM admin_audit_logs WHERE action='password_reset_requested')
  || '|' ||
  (SELECT count(*) FROM email_identities)
  || '|' ||
  (SELECT count(*) FROM password_reset_tokens);
SQL

test "$(systemctl is-active boursnegar-data-service.service)" = active
pm2 pid bourse-app | grep -Eq '^[1-9][0-9]*$'
flag="$(sed -n 's/^EMAIL_ENABLED=//p' /var/www/bourse-analyzer/.env | tail -1)"
test "$flag" = true
test "$(stat -c '%a' /var/www/bourse-analyzer/.env)" = 600

echo PM2=PASS
echo FASTAPI=PASS
echo POSTGRESQL=PASS
echo PUBLIC_DOMAIN=PASS
echo AUTH_ROUTES=PASS
echo EMAIL_FEATURE_FLAG=ENABLED
