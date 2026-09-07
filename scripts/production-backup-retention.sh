#!/usr/bin/env bash
set -euo pipefail

keep=2
apply=0
backup_root=${BOURSNEGAR_BACKUP_ROOT:-/var/backups/boursnegar}
lock_file=${BOURSNEGAR_RETENTION_LOCK:-/var/lock/boursnegar-backup-retention.lock}

usage() {
  cat <<'EOF'
Usage: production-backup-retention.sh [--apply] [--keep COUNT]

Without --apply, validate and report the retention plan without deleting files.
Only valid PostgreSQL custom-format *.dump files under the backup root are
eligible. Other backup, rollback, provenance, and raw-evidence files remain.
EOF
}

while (($#)); do
  case "$1" in
    --apply) apply=1; shift ;;
    --keep)
      (($# >= 2)) || { echo "--keep requires a count" >&2; exit 2; }
      keep=$2; shift 2 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

[[ "$keep" =~ ^[1-9][0-9]*$ ]] || { echo "keep must be a positive integer" >&2; exit 2; }
[ -d "$backup_root" ] || { echo "backup root does not exist: $backup_root" >&2; exit 1; }

install -d -m 700 "$(dirname "$lock_file")"
exec 9>"$lock_file"
flock -n 9 || { echo "retention already running" >&2; exit 1; }

if pgrep -x pg_dump >/dev/null || pgrep -x pg_restore >/dev/null; then
  echo "active PostgreSQL backup/restore process; refusing retention" >&2
  exit 1
fi
for unit in boursnegar-codal-financials.service boursnegar-codal-backfill.service; do
  if systemctl is-active --quiet "$unit" 2>/dev/null; then
    echo "active ingestion unit $unit; refusing retention" >&2
    exit 1
  fi
done

mapfile -d '' candidates < <(
  find "$backup_root" -type f -name '*.dump' -printf '%T@ %p\0' | sort -z -nr
)
valid=()
for entry in "${candidates[@]}"; do
  path=${entry#* }
  if pg_restore -l "$path" >/dev/null 2>&1; then
    valid+=("$entry")
  else
    echo "invalid PostgreSQL dump; refusing to classify: $path" >&2
    exit 1
  fi
done

if ((${#valid[@]} < keep)); then
  echo "only ${#valid[@]} valid dumps found; retention requires $keep" >&2
  exit 1
fi

stamp=$(date -u +%Y%m%dT%H%M%SZ)
report="$backup_root/${stamp}-retention-report.tsv"
umask 077
{
  printf 'generated_utc\t%s\n' "$stamp"
  printf 'policy\tkeep_%s_newest_valid_custom_postgresql_dumps\n' "$keep"
  printf 'mode\t%s\n' "$([ "$apply" -eq 1 ] && echo apply || echo dry-run)"
  printf 'total_valid_dumps\t%s\n' "${#valid[@]}"
  printf 'status\tmtime_epoch\tsize_bytes\tsha256\tpath\n'
  for i in "${!valid[@]}"; do
    entry=${valid[$i]}
    mtime=${entry%% *}
    path=${entry#* }
    size=$(stat -c %s "$path")
    sha=$(sha256sum "$path" | awk '{print $1}')
    if ((i < keep)); then
      status=KEPT
    elif ((apply)); then
      status=DELETED
    else
      status=WOULD_DELETE
    fi
    printf '%s\t%s\t%s\t%s\t%s\n' "$status" "$mtime" "$size" "$sha" "$path"
  done
} >"$report"
chmod 600 "$report"

if ((apply)); then
  for ((i=keep; i<${#valid[@]}; i++)); do
    rm -f -- "${valid[$i]#* }"
  done
fi

printf 'REPORT=%s\nVALID_DUMPS=%s\nKEPT=%s\nMODE=%s\n' \
  "$report" "${#valid[@]}" "$keep" "$([ "$apply" -eq 1 ] && echo apply || echo dry-run)"
