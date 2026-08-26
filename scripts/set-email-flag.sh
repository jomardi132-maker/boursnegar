#!/usr/bin/env bash
set -euo pipefail
value="${1:-false}"
case "$value" in true|false) ;; *) exit 2;; esac
env_file=/var/www/boursnegar-shared/web.env
tmp="$(mktemp)"
awk -F= '$1!="EMAIL_ENABLED"' "$env_file" >"$tmp"
printf 'EMAIL_ENABLED=%s\n' "$value" >>"$tmp"
install -o root -g root -m 600 "$tmp" "$env_file"
rm -f "$tmp"
echo "EMAIL_ENABLED=$value"
