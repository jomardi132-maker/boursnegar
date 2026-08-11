#!/usr/bin/env bash
set -euo pipefail
cd /var/www/bourse-analyzer

for key in SMTP_HOST SMTP_PORT SMTP_USER SMTP_PASSWORD SMTP_FROM; do
  value="$(sed -n "s/^${key}=//p" .env | tail -1)"
  if [ -n "$value" ]; then echo "$key=SET"; else echo "$key=MISSING_OR_EMPTY"; fi
done

from="$(sed -n 's/^SMTP_FROM=//p' .env | tail -1)"
address="$from"
case "$address" in
  *'<'*'>'*) address="${address#*<}"; address="${address%%>*}" ;;
esac
domain="${address##*@}"
if [ "$domain" = "mail.boursnegar.ir" ]; then
  echo SMTP_FROM_DOMAIN=MATCH
else
  echo SMTP_FROM_DOMAIN=MISMATCH
fi
echo ENV_MODE="$(stat -c '%a' .env)"
