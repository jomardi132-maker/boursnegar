#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
MEMORY_ROOT=${CODEX_MEMORY_ROOT:-"$HOME/.codex/memories"}
NOTES="$MEMORY_ROOT/extensions/ad_hoc/notes"

test -s "$ROOT/CURRENT_STATE.md"
test -s "$ROOT/docs/PROJECT_MEMORY_PROTOCOL.md"
test -d "$NOTES"

echo "CURRENT_STATE: OK"
echo "PROJECT_MEMORY_PROTOCOL: OK"
echo "AD_HOC_NOTES: $(find "$NOTES" -maxdepth 1 -type f -name '*.md' | wc -l | tr -d ' ')"
echo "LATEST_NOTES:"
find "$NOTES" -maxdepth 1 -type f -name '*.md' -printf '%f\n' | sort | tail -5

if git -C "$ROOT" diff --quiet -- CURRENT_STATE.md; then
  echo "CURRENT_STATE_WORKTREE: clean"
else
  echo "CURRENT_STATE_WORKTREE: changed (record before handoff)"
fi
