# Boursnegar — کارت اجرای سریع

مرجع شروع روزانه: `BOURSNEGAR_CONTROL_PANEL.md`. این کارت فقط قواعد ایمنی اجرای
workflowهای ingestion و promotion را تکمیل می‌کند.

## ترتیب ثابت

1. این کارت را بخوان؛ سپس فقط آخرین entry از `CURRENT_STATE.md` و جدیدترین report را بررسی کن.
2. اگر delta واقعی نیست، اجرا نکن و همان blocker/checkpoint را حفظ کن.
3. local/browser artifact بگیر؛ Production هرگز منبع مستقیم Codal یا انتخاب نماد نیست.
4. فقط `manifest.json` معتبر + فایل واقعی + SHA-256 را آمادهٔ promotion بدان.
5. پیش از هر write یک backup بگیر؛ import را دوبار اجرا کن؛ replay باید `inserted=0` باشد.
6. بعد از write، snapshot refresh و `/healthz` و `/readyz` را تأیید کن.

## صف‌ها

- recovery را از `plan_local_recovery.py` و registry محلی بگیر؛ exclusionهای پایدار را تکرار نکن.
- کمبود comparable/core facts/notice را جدا پیگیری کن.
- NAV صندوق را با issuer، period، source و unit تطبیق بده؛ join بر اساس symbol کافی نیست.
- برای FCFE/DCF فقط OCF + CapEx + net borrowing صریح و هم‌دوره معتبر است؛ ماندهٔ بدهی جای جریان نقدی نیست.

## توقف فوری

- `non_json_response`، captcha، child-entity، Chrome/session unavailable، checksum/manifest failure: `BLOCKED` + checkpoint؛ import ممنوع.
- zero-result یا 404 فقط نبود evidence واردشده در آن مسیر است، نه نبود تاریخی.
- `INSUFFICIENT_DATA`، `REVIEW`، `UNIT_UNKNOWN` و گیت‌های باز را با حدس پر نکن.
- batch، audit یا backup تکراری بدون تغییر واقعی ممنوع.

## پایش

- timerهای user: `local-codal-monitor`، `coverage-audit`، `backup-retention`.
- health، readiness، freshness، analytical readiness، render و authenticated E2E گیت‌های مستقل‌اند.
- در پاسخ upstream تکراری، backoff کن؛ فقط با تغییر response/session یا موعد schedule دوباره probe کن.

## وضعیت مرجع ثبت‌شده

۱۵۲۴ نماد فعال؛ ۷۲۱ `CORE_READY`، ۴۱۹ `FUND_MODEL_REQUIRED`، ۳۸۴ `MISSING_COMPARABLE_PERIODS`. آخرین مانع شناخته‌شده: `search.codal.ir` پاسخ API JSON معتبر نمی‌دهد و Chrome مستقل متصل نیست.
