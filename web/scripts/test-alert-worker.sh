#!/usr/bin/env bash
set -euo pipefail

node scripts/fake-analysis-server.mjs >/tmp/boursnegar-fake-analysis.log 2>&1 &
fixture_pid=$!
trap 'kill "$fixture_pid" 2>/dev/null || true' EXIT
sleep 0.2

export ALERT_WORKER_ENABLED=true
export SMS_ENABLED=false
export ALERT_SMS_MAX_PER_RUN=2
export PYTHON_API_BASE=http://127.0.0.1:3394

./node_modules/.bin/tsx server/alertWorker.ts
first=$(psql "$DATABASE_URL" -Atc "SELECT count(*) FROM sms_delivery_attempts")
./node_modules/.bin/tsx server/alertWorker.ts
second=$(psql "$DATABASE_URL" -Atc "SELECT count(*) FROM sms_delivery_attempts")
./node_modules/.bin/tsx server/alertWorker.ts
third=$(psql "$DATABASE_URL" -Atc "SELECT count(*) FROM sms_delivery_attempts")

test "$first" = 2
test "$second" = 3
test "$third" = 3
test "$(psql "$DATABASE_URL" -Atc "SELECT count(*) FROM sms_delivery_attempts WHERE status='failed' AND error_code='SMS_DISABLED'")" = 3
echo "alert-worker integration: PASS (rate=2, dedup=PASS, sms=disabled)"
