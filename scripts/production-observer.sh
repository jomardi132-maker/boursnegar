#!/usr/bin/env bash
set -euo pipefail

readonly disk_warn_percent="${DISK_WARN_PERCENT:-98}"
readonly origin="${BOURSNEGAR_ORIGIN:-http://127.0.0.1:3000}"

fail() { printf 'BOURSNEGAR_OBSERVER=FAIL %s\n' "$*" >&2; exit 1; }

failed_units="$(systemctl --failed --no-legend --plain 2>/dev/null | awk '$1 ~ /^boursnegar-/ {print $1}')"
if [[ -n "$failed_units" ]]; then
  fail "failed units: $(tr '\n' ',' <<<"$failed_units" | sed 's/,$//')"
fi

required_timers=(
  boursnegar-market-daily.timer
  boursnegar-market-intraday.timer
  boursnegar-snapshot-refresh.timer
  boursnegar-backup-retention.timer
)
for timer in "${required_timers[@]}"; do
  systemctl is-active --quiet "$timer" || fail "required timer inactive: $timer"
done

if systemctl is-active --quiet boursnegar-codal-financials.timer 2>/dev/null; then
  fail "retired zero-delta timer active: boursnegar-codal-financials.timer"
fi

worker_enabled="$(sed -n 's/^ALERT_WORKER_ENABLED=//p' /var/www/boursnegar-current/.env | tail -1)"
sms_enabled="$(sed -n 's/^SMS_ENABLED=//p' /var/www/boursnegar-current/.env | tail -1)"
alert_worker="not-scheduled"
if [[ "$worker_enabled" = true && "$sms_enabled" = true ]]; then
  systemctl is-active --quiet boursnegar-alert-worker.timer || fail "enabled alert worker timer inactive"
  test -s /var/www/boursnegar-current/dist/alert-worker.cjs || fail "missing alert worker artifact"
  test "$(systemctl show boursnegar-alert-worker.service -p Result --value)" = success || fail "alert worker last result"
  alert_worker="ready"
elif systemctl is-active --quiet boursnegar-alert-worker.timer 2>/dev/null; then
  fail "disabled alert worker timer active"
fi

ready="$(curl --max-time 10 --fail --silent "$origin/readyz")" || fail "web readiness"
python3 -c 'import json,sys; d=json.load(sys.stdin); assert d.get("status")=="ready" and d.get("mail")=="ready"' <<<"$ready" || fail "web readiness payload"

data="$(curl --max-time 10 --fail --silent http://127.0.0.1:8001/health)" || fail "data service health"
python3 -c 'import json,sys; assert json.load(sys.stdin).get("status")=="ok"' <<<"$data" || fail "data service payload"

screener="$(curl --max-time 20 --fail --silent "$origin/api/market/screener?limit=50")" || fail "screener endpoint"
coverage_summary=$(python3 -c '
import json, sys
d = json.loads(sys.argv[1])
rows = d.get("rows") or []
if len(rows) != 50 or int(d.get("total") or 0) < 50:
    raise SystemExit("screener row count")
coverage = [float(row["data_coverage"]) for row in rows if row.get("data_coverage") is not None]
if not coverage:
    raise SystemExit("screener coverage unavailable")
print(f"coverage_min={min(coverage):g} coverage_max={max(coverage):g} coverage_100={sum(value == 100 for value in coverage)}")
' "$screener")

used="$(df -P / | awk 'NR==2 {gsub(/%/,"",$5); print $5}')"
case "$used" in ''|*[!0-9]*) fail "invalid disk usage";; esac
if (( used >= disk_warn_percent )); then
  fail "disk usage ${used}% >= ${disk_warn_percent}%"
fi

printf 'BOURSNEGAR_OBSERVER=PASS disk=%s%% failed_units=0 required_timers=%s alert_worker=%s rows=50 %s\n' "$used" "${#required_timers[@]}" "$alert_worker" "$coverage_summary"
