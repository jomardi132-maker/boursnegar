#!/usr/bin/env bash
set -euo pipefail
test "$(sed -n 's/^EMAIL_ENABLED=//p' /var/www/bourse-analyzer/.env | tail -1)" = true
test "$(stat -c '%a' /var/www/bourse-analyzer/.env)" = 600
curl -fsS http://127.0.0.1:3000/readyz | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ready" and d["mail"]=="ready"'
curl -fsS http://127.0.0.1:8001/health >/dev/null
curl -fsS https://boursnegar.ir/healthz >/dev/null
systemctl is-active --quiet boursnegar-data-service.service
pm2 pid bourse-app | grep -Eq '^[1-9][0-9]*$'
test ! -e /tmp/boursnegar-test-email.input
test ! -e /tmp/boursnegar-e2e-reset-token
sudo -u postgres psql -At -d boursnegar_db <<'SQL' | python3 -c 'import sys; assert sys.stdin.read().split()==["0","0"]'
SELECT count(*) FROM email_identities;
SELECT count(*) FROM password_reset_tokens;
SQL
echo REMOTE_FINAL_GATE=PASS
