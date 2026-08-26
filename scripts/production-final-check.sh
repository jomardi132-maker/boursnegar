#!/usr/bin/env bash
set -euo pipefail
echo SERVICES
pm2 status --no-color
systemctl is-active boursnegar-data-service.service
echo DB
sudo -u postgres psql -At -d boursnegar_db <<'SQL'
SELECT version FROM schema_migrations ORDER BY applied_at;
SELECT 'email_identities=' || count(*) FROM email_identities;
SELECT 'password_reset_tokens=' || count(*) FROM password_reset_tokens;
SELECT 'reports_1404=' || count(*) FROM financial_reports WHERE period_end_date LIKE '1404%';
SELECT 'reports_1405=' || count(*) FROM financial_reports WHERE period_end_date LIKE '1405%';
SQL
echo ENV_STATUS
while IFS="=" read -r key value; do
  case "$key" in
    AUTH_SESSION_SECRET|OTP_PEPPER|PASSWORD_PEPPER|OTP_ENABLED|OTP_PENDING_APPROVAL|SMS_ENABLED|SMTP_HOST|SMTP_USER|SMTP_PASSWORD|SMTP_FROM)
      if [ -n "$value" ]; then echo "$key=SET"; else echo "$key=EMPTY"; fi
      ;;
  esac
done </var/www/boursnegar-shared/web.env
stat -c '%a %n' /var/www/boursnegar-shared/web.env
curl -fsS https://boursnegar.ir/healthz
curl -fsS https://boursnegar.ir/readyz
