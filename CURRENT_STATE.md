# وضعیت فعلی بورس‌نگار

آخرین بررسی: ۱۴۰۵/۰۶/۰۴، 2026-08-26T22:29:58+03:30

## خلاصه اجرایی

Production فعال است و مسیر اجرایی واقعی همچنان Nginx -> PM2 `bourse-app` -> `127.0.0.1:3000` و FastAPI روی `127.0.0.1:8001` است. در این بررسی read-only هیچ اقدام عملیاتی روی Production انجام نشد.

مهم‌ترین شکاف فعلی Git است: checkout لوکال روی `agent/data-engine-v1` تمیز است، اما ۱۳ commit از `origin/agent/data-engine-v1` جلوتر است. اتصال SSH به GitHub در این نوبت طی ۲۰ ثانیه پاسخ نداد و push محدود ۳۰ ثانیه‌ای هم timeout شد، بنابراین push یا تأیید remote انجام نشد.

## وضعیت لوکال و Git

- شاخه فعلی: `agent/data-engine-v1`
- HEAD پیش از ثبت این گزارش: `ee4e926605da3dbe5931e813b8847afcfa29804c`
- این گزارش خودش به‌عنوان commit مستندات روی همین شاخه ثبت شده است؛ بنابراین وضعیت نهایی شاخه ۱۳ commit جلوتر از `origin/agent/data-engine-v1` است.
- `origin/agent/data-engine-v1`: `238af8dc94871c8191a604a4f5e7bede9372b92e`
- `main` لوکال: `017d830d647309a996d76011f43cfb83a9c435fa`
- `origin/main`: `3934e2d480383c29dbedf683a8b045d374006687`
- worktree tracked: تمیز
- `git diff --check`: بدون خطا

۱۳ commit جلوتر از remote فعلی:

- commit مستندات فعلی: `docs: capture current production state`
- `ee4e9266` Make auto local sync DB-aware
- `3f361adb` reuse per-symbol ingestion checkpoints
- `e6ba303d` propagate local ingestion import path
- `e49c73fd` upgrade ingestion console visual system
- `c37349fe` polish ingestion console navigation and status colors
- `ca3bebda` speed up ingestion console startup
- `36c7d139` ignore local runtime packages
- `ee1fe7d1` make ingestion console RTL runtime self-contained
- `90f30ce2` fix ingestion console Persian RTL and artifact coverage
- `19c8e51e` fix Persian text rendering dependency gate
- `16232538` complete local ingestion operations dashboard
- `5d62b96d` automate local Codal completion and production sync

## تست‌های لوکال

- Web typecheck: موفق
- Web Vitest: ۸ فایل، ۶۱ تست موفق
- Web production build: موفق، asset جدید build محلی `index.production-DYyIX7si.js`
- Python compileall با venv پروژه: موفق
- Python unittest با `data-service/venv/bin/python`: ۶۹ تست موفق

اجرای Python با `python3` سیستم معتبر نیست، چون dependencyهای پروژه مثل `pandas`، `jdatetime`، `psycopg2` و `fastapi` در آن interpreter نصب نیستند. معیار معتبر فعلی venv پروژه است.

## وضعیت Production

- host: `srv6626362878`
- زمان بررسی سرور: `2026-08-26T18:58:15+00:00`
- PM2 process: `bourse-app`
- PM2 status: `online`
- PM2 cwd: `/var/www/boursnegar-releases/20260826T103100Z-mobile-screener-fix`
- PM2 script: `/var/www/boursnegar-releases/20260826T103100Z-mobile-screener-fix/dist/server.cjs`
- data service: `boursnegar-data-service.service`, `active/running`
- data service WorkingDirectory: `/var/www/boursnegar-data-current`
- resolved web symlink: `/var/www/boursnegar-releases/20260826T103100Z-mobile-screener-fix`
- resolved data symlink: `/var/www/boursnegar-data-releases/20260825T173000Z-all-industry-models`
- web releases: ۱۷
- data releases: ۱۶
- backup entries: ۶۳
- `nginx -t`: موفق

Health/smoke checks:

- internal `http://127.0.0.1:3000/healthz`: `{"status":"ok","auth":"email_password"}`
- internal `http://127.0.0.1:3000/readyz`: `{"status":"ready","auth":"email_password","mail":"ready"}`
- internal `http://127.0.0.1:8001/health`: `{"status":"ok"}`
- internal `http://127.0.0.1:3000/api/health`: `{"status":"ok","auth":"email_password"}`
- public `/healthz`: HTTP 200
- public `/readyz`: HTTP 200
- public `/api/market/overview`: HTTP 200
- public `/api/market/dashboard`: HTTP 200
- public `/login`: HTTP 200
- public `/api/stocks/فولاد`: HTTP 200

## وضعیت artifact و ingestion محلی

- `artifacts/local-ingestion.sqlite3`: به‌روزشده در 2026-08-26 22:29، اندازه حدود ۸۴.۸ MB
- `artifacts/local-coverage-latest.csv`: ۱۵۲۴ نماد + header
- `artifacts/local-recovery-plan.csv`: ۱۵۲۴ نماد + header
- `artifacts/promoted-remote-batch/normalized.jsonl`: موجود، حدود ۱.۲ MB
- `artifacts/candidate-review.csv`: موجود، حدود ۱۸۹ KB

این artifactها برای reconciliation ارزشمندند، اما نباید با پوشش کامل Production یکی گرفته شوند. هر ارسال جدید به Production باید manifest/schema/checksum، advisory lock و اجرای تکراری با inserted=0 داشته باشد.

## موارد باز

1. همگام‌سازی GitHub: اتصال SSH به GitHub در این نوبت timeout شد. تا تأیید دسترسی، ۱۳ commit جلوتر از remote باید local-only فرض شوند.
2. پوشش داده: همچنان نباید ادعای «تحلیل کامل همه نمادها» کرد. معیار فعلی باید provenance، دوره، نوع fact، واحد و source باشد.
3. رکوردهای Codalpy بدون نماد: فقط با artifact/manifest/source رسمی قابل اصلاح‌اند؛ انتساب حدسی ممنوع است.
4. comment automation: مسیر بدون نشست احراز هویت‌شده end-to-end هنوز معیار تکمیل نیست.
5. UI: health و HTTP 200 کافی نیست؛ برای تغییرات UI بعدی باید DOM/console/network و viewport موبایل/دسکتاپ بررسی شود.

## اقدام بعدی پیشنهادی

اولویت عملی بعدی، رفع مانع GitHub و push کردن commitهای local بعد از تأیید دسترسی SSH است. پس از آن باید گزارش coverage تفکیک‌شده و قابل بازتولید از Production گرفته شود و فقط بر اساس آن برای ingestion بعدی تصمیم گرفت.
