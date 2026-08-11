#!/usr/bin/env bash
set -euo pipefail

stamp="$(date -u +%Y%m%dT%H%M%SZ)"
release="/var/www/boursnegar-releases/${stamp}-emailauth"
previous="$(pm2 pid bourse-app >/dev/null 2>&1 && pm2 describe bourse-app --no-color | awk -F'│' '/script path/{gsub(/^ +| +$/,"",$3); print $3; exit}' || true)"
previous="${previous%/dist/server.cjs}"
backup="$(find /var/backups/boursnegar -maxdepth 1 -type d -name '*-emailauth*' | sort | tail -1)"

rollback() {
  code=$?
  if [ "$code" -eq 0 ]; then return; fi
  echo "DEPLOY_FAILED_ROLLBACK_STARTED"
  if [ -n "$previous" ] && [ -f "$previous/dist/server.cjs" ]; then
    pm2 delete bourse-app >/dev/null 2>&1 || true
    (cd "$previous" && NODE_ENV=production pm2 start dist/server.cjs --name bourse-app --cwd "$previous") >/dev/null
  fi
  if [ -n "$backup" ] && [ -f "$backup/data-service.tgz" ]; then
    tar -xzf "$backup/data-service.tgz" -C /var/www
    systemctl restart boursnegar-data-service.service || true
  fi
  pm2 save --force >/dev/null 2>&1 || true
  exit "$code"
}
trap rollback ERR

install -d -m 755 "$release"
tar -xzf /tmp/boursnegar-web-emailauth.tgz -C "$release"
ln -s /var/www/bourse-analyzer/.env "$release/.env"
if [ -d /var/www/bourse-analyzer/uploads ]; then ln -s /var/www/bourse-analyzer/uploads "$release/uploads"; fi

env_file=/var/www/bourse-analyzer/.env
env_backup="/var/www/bourse-analyzer/.env.${stamp}.bak"
cp -p "$env_file" "$env_backup"
chmod 600 "$env_file" "$env_backup"
ensure_secret() {
  key="$1"
  if ! awk -F= -v k="$key" '$1==k && length(substr($0,index($0,"=")+1))>0{found=1} END{exit !found}' "$env_file"; then
    tmp="$(mktemp)"
    awk -F= -v k="$key" '$1!=k' "$env_file" >"$tmp"
    printf '%s=' "$key" >>"$tmp"
    openssl rand -base64 96 | tr -d '\n' >>"$tmp"
    printf '\n' >>"$tmp"
    install -o root -g root -m 600 "$tmp" "$env_file"
    rm -f "$tmp"
  fi
}
set_flag() {
  key="$1" value="$2" tmp="$(mktemp)"
  awk -F= -v k="$key" '$1!=k' "$env_file" >"$tmp"
  printf '%s=%s\n' "$key" "$value" >>"$tmp"
  install -o root -g root -m 600 "$tmp" "$env_file"
  rm -f "$tmp"
}
ensure_secret AUTH_SESSION_SECRET
ensure_secret OTP_PEPPER
ensure_secret PASSWORD_PEPPER
set_flag OTP_ENABLED false
set_flag OTP_PENDING_APPROVAL true
set_flag SMS_ENABLED false
set_flag OTP_GATEWAY disabled
set_flag PUBLIC_ORIGIN https://boursnegar.ir

cd "$release"
npm ci --omit=dev=false
npm run typecheck
npm test -- --run
npm run build
npm audit --omit=dev
npm run migrate

tar -xzf /tmp/boursnegar-data-emailauth.tgz -C /var/www/boursnegar-data-service
/var/www/boursnegar-data-service/venv/bin/python -m compileall -q /var/www/boursnegar-data-service/app
(cd /var/www/boursnegar-data-service && venv/bin/python -m unittest discover -s tests -v)
systemctl restart boursnegar-data-service.service

pm2 delete bourse-app >/dev/null 2>&1 || true
NODE_ENV=production pm2 start dist/server.cjs --name bourse-app --cwd "$release" >/dev/null
pm2 save --force >/dev/null

for attempt in $(seq 1 15); do
  if curl -fsS http://127.0.0.1:3000/healthz >/dev/null && curl -fsS http://127.0.0.1:8001/health >/dev/null; then break; fi
  sleep 2
  if [ "$attempt" -eq 15 ]; then false; fi
done
curl -fsS http://127.0.0.1:3000/readyz
curl -fsS https://boursnegar.ir/healthz
systemctl is-active --quiet boursnegar-data-service.service
pm2 pid bourse-app | grep -Eq '^[1-9][0-9]*$'

rm -f /tmp/boursnegar-web-emailauth.tgz /tmp/boursnegar-data-emailauth.tgz
trap - ERR
echo "RELEASE=$release"
echo "ENV_BACKUP=$env_backup"
echo "AUTH_SESSION_SECRET=SET"
echo "OTP_PEPPER=SET"
echo "PASSWORD_PEPPER=SET"
