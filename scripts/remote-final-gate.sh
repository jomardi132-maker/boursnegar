#!/usr/bin/env bash
set -euo pipefail
web_env=/var/www/boursnegar-shared/web.env
data_env="$(readlink -f /var/www/boursnegar-data-current/.env)"
test "$(sed -n 's/^EMAIL_ENABLED=//p' "$web_env" | tail -1)" = true
test "$(stat -c '%a' "$web_env")" = 600
test "$(stat -c '%a' "$data_env")" = 600
test "$(stat -c '%U:%G' "$data_env")" = root:root
curl -fsS http://127.0.0.1:3000/readyz | python3 -c 'import json,sys; d=json.load(sys.stdin); assert d["status"]=="ready" and d["mail"]=="ready"'
curl -fsS http://127.0.0.1:8001/health >/dev/null
curl -fsS https://boursnegar.ir/healthz >/dev/null
systemctl is-active --quiet boursnegar-data-service.service
pm2 pid bourse-app | grep -Eq '^[1-9][0-9]*$'
test ! -e /tmp/boursnegar-test-email.input
test ! -e /tmp/boursnegar-e2e-reset-token
# Existing production identities and reset-token rows are legitimate state; do
# not treat their mere presence as a failed deployment. The controlled E2E
# checks above already prevent the known temporary test artifacts.
echo REMOTE_FINAL_GATE=PASS
