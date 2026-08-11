#!/usr/bin/env bash
set -euo pipefail

backup="$(find /var/backups/boursnegar -maxdepth 1 -type d -name '*-emailauth*' | sort | tail -1)"
test -n "$backup"
test -f "$backup/boursnegar_db.dump"
echo "BACKUP=$backup"
find "$backup" -maxdepth 1 -type f -printf '%m %f\n' | sort

testdb="boursnegar_migration_test"
cleanup() {
  sudo -u postgres dropdb --if-exists "$testdb" >/dev/null 2>&1 || true
  rm -f /tmp/005_email_password_auth.sql /tmp/boursnegar-migration-test.log /tmp/boursnegar-migration-test.dump
}
trap cleanup EXIT

sudo -u postgres dropdb --if-exists "$testdb"
sudo -u postgres createdb -O boursnegar "$testdb"
install -o postgres -g postgres -m 600 "$backup/boursnegar_db.dump" /tmp/boursnegar-migration-test.dump
sudo -u postgres pg_restore --no-owner --role=boursnegar -d "$testdb" /tmp/boursnegar-migration-test.dump
sudo -u postgres psql -v ON_ERROR_STOP=1 -d "$testdb" -f /tmp/005_email_password_auth.sql \
  >/tmp/boursnegar-migration-test.log

sudo -u postgres psql -At -d "$testdb" <<'SQL'
SELECT version FROM schema_migrations WHERE version='005_email_password_auth';
SELECT to_regclass('public.email_identities');
SELECT to_regclass('public.password_reset_tokens');
SQL
