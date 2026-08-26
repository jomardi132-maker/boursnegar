#!/usr/bin/env bash
set -euo pipefail
stamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup="/var/backups/boursnegar/${stamp}-smtp"
install -d -m 700 "$backup"
web_root="$(readlink -f /var/www/boursnegar-current)"
tar --exclude=.env --exclude=node_modules --exclude=dist -czf "$backup/boursnegar-web.tgz" -C "$web_root" .
tar --exclude=.env --exclude=venv --exclude=__pycache__ -czf "$backup/data-service.tgz" -C /var/www boursnegar-data-service
if [ -f /var/www/boursnegar-current/data/db.json ]; then cp -p /var/www/boursnegar-current/data/db.json "$backup/db.json"; fi
sudo -u postgres pg_dump -Fc boursnegar_db >"$backup/boursnegar_db.dump"
cp -p /var/www/boursnegar-shared/web.env "$backup/app.env"
chmod 600 "$backup"/*
echo "BACKUP=$backup"
find "$backup" -maxdepth 1 -type f -printf '%m %f\n' | sort
