#!/usr/bin/env bash
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
matches="$(grep -RIl --exclude-dir=node_modules --exclude-dir=dist --exclude='*.map' \
  --exclude='verify-no-legacy-paths.sh' 'bourse-analyzer' \
  "$root/scripts" "$root/web" "$root/data-service" 2>/dev/null || true)"

if [ -n "$matches" ]; then
  printf '%s\n' "$matches" >&2
  echo LEGACY_PATH_CHECK=FAIL >&2
  exit 1
fi

echo LEGACY_PATH_CHECK=PASS
