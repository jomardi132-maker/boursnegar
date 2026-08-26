#!/usr/bin/env bash
set -euo pipefail
project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec "$project_root/data-service/venv/bin/python" \
  "$project_root/data-service/scripts/ingestion_console.py" \
  --db "$project_root/artifacts/local-ingestion.sqlite3" \
  --ssh-target boursnegar
