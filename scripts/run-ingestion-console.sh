#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
local_python_packages="$project_root/.runtime/python-packages/root/usr/lib/python3/dist-packages"
export PYTHONPATH="${local_python_packages}${PYTHONPATH:+:$PYTHONPATH}"
"$project_root/data-service/venv/bin/python" \
  "$project_root/data-service/scripts/recalculate_local_coverage.py" \
  --db "$project_root/artifacts/local-ingestion.sqlite3" \
  --export "$project_root/artifacts/local-coverage-latest.csv"
"$project_root/data-service/venv/bin/python" \
  "$project_root/data-service/scripts/plan_local_recovery.py" \
  --db "$project_root/artifacts/local-ingestion.sqlite3" \
  --out "$project_root/artifacts/local-recovery-plan.csv"
exec "$project_root/data-service/venv/bin/python" \
  "$project_root/data-service/scripts/ingestion_console.py" \
  --db "$project_root/artifacts/local-ingestion.sqlite3" \
  --ssh-target boursnegar
