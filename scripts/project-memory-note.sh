#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <slug>" >&2
  exit 2
fi

slug=$1
case "$slug" in
  (*[!A-Za-z0-9_-]*|'') echo "slug must contain only ASCII letters, numbers, _ or -" >&2; exit 2 ;;
esac

notes_dir=${CODEX_MEMORY_ROOT:-"$HOME/.codex/memories"}/extensions/ad_hoc/notes
mkdir -p "$notes_dir"
stamp=$(date -u +%Y%m%dT%H%M%SZ)
target="$notes_dir/${stamp}-${slug}.md"
if [ -e "$target" ]; then
  echo "note already exists: $target" >&2
  exit 1
fi

umask 077
printf '%s\n' \
  "# Project note: $slug" \
  "" \
  "Date and scope:" \
  "Root cause or finding:" \
  "Evidence and backup/checksum:" \
  "Change made:" \
  "Tests and Production proof:" \
  "Remaining gates:" \
  "Continuation rule:" > "$target"
printf '%s\n' "$target"
