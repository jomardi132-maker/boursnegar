# وضعیت فعلی بورس‌نگار

آخرین بررسی: ۱۴۰۵/۰۶/۰۵، 2026-08-27T09:21:00+03:30

## خلاصه اجرایی

Production فعال است و مسیر اجرایی واقعی همچنان Nginx -> PM2 `bourse-app` -> `127.0.0.1:3000` و FastAPI روی `127.0.0.1:8001` است. در این بررسی read-only هیچ اقدام عملیاتی روی Production انجام نشد.

شکاف GitHub قبلی رفع شده است: remote پیش‌فرض repo اکنون HTTPS است و `git push --dry-run origin agent/data-engine-v1` وضعیت `Everything up-to-date` داد. شاخه‌های `agent/data-engine-v1` و `main` روی GitHub با HEAD همین شاخه همسان‌اند.

## وضعیت لوکال و Git

- شاخه فعلی: `agent/data-engine-v1`
- HEAD پیش از ثبت گزارش وضعیت: `ee4e926605da3dbe5931e813b8847afcfa29804c`
- این گزارش و اصلاحات بعدی خودش به‌عنوان commit مستندات روی همین شاخه ثبت می‌شود؛ برای hash نهایی از `git rev-parse HEAD origin/agent/data-engine-v1 origin/main` استفاده شود.
- `origin`: `https://github.com/jomardi132-maker/boursnegar.git`
- `origin/agent/data-engine-v1`: با HEAD همین شاخه همسان است.
- `origin/main`: با HEAD همین شاخه همسان است.
- worktree tracked: تمیز
- `git diff --check`: بدون خطا

commitهای اصلی که قبل از مستندسازی از remote جلوتر بودند:

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
- زمان بررسی سرور: `2026-08-27T05:45:54+00:00`
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
- backup entries: ۶۳ در بررسی قبلی؛ در این بررسی شمارش backup تکرار نشد.
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

## وضعیت coverage و artifact

- `artifacts/local-ingestion.sqlite3`: به‌روزشده در 2026-08-26 22:29، اندازه حدود ۸۴.۸ MB
- `artifacts/local-coverage-latest.csv`: ۱۵۲۴ نماد + header
- `artifacts/local-recovery-plan.csv`: ۱۵۲۴ نماد + header
- `artifacts/promoted-remote-batch/normalized.jsonl`: موجود، حدود ۱.۲ MB
- `artifacts/candidate-review.csv`: موجود، حدود ۱۸۹ KB
- Production coverage audit امروز:
  - `docs/audits/production-coverage-2026-08-27.md`
  - raw JSON: `artifacts/production-audits/coverage-20260827T054703Z.json`
  - symbol-level raw JSON: `artifacts/production-audits/symbol-coverage-20260827T055105Z.json`

این artifactها برای reconciliation ارزشمندند، اما نباید با پوشش کامل Production یکی گرفته شوند. هر ارسال جدید به Production باید manifest/schema/checksum، advisory lock و اجرای تکراری با inserted=0 داشته باشد.

آخرین اعداد Production در 2026-08-27:

- Active instruments: 1,533
- Industry-level current aliases: 1,524
- Financial periods: 12,018
- Financial facts: 44,088
- Valid facts: 17,761
- Raw Codalpy records: 1,127,218
- Linked Codalpy records: 1,079,010
- Symbol-level tiers: `CORE_READY=215`, `MISSING_CORE_FACTS=418`, `MISSING_COMPARABLE_PERIODS=891`, `NO_CURRENT_ALIAS=9`
- Latest decisions: `INSUFFICIENT_DATA=1,529`, `SELL=3`, `HOLD=1`, `BUY=0`

## موارد باز

1. پوشش داده: همچنان نباید ادعای «تحلیل کامل همه نمادها» کرد. معیار فعلی باید provenance، دوره، نوع fact، واحد و source باشد.
2. ۹ ابزار فعال بدون current alias باید فقط با شواهد هویتی رسمی reconcile شوند.
3. رکوردهای Codalpy بدون نماد: فقط با artifact/manifest/source رسمی قابل اصلاح‌اند؛ انتساب حدسی ممنوع است.
4. comment automation: مسیر بدون نشست احراز هویت‌شده end-to-end هنوز معیار تکمیل نیست.
5. UI: health و HTTP 200 کافی نیست؛ برای تغییرات UI بعدی باید DOM/console/network و viewport موبایل/دسکتاپ بررسی شود.

## اقدام بعدی پیشنهادی

اولویت عملی بعدی، reconcile کردن ۹ ابزار بدون alias و سپس برنامه‌ریزی ingestion برای نمادهای `MISSING_COMPARABLE_PERIODS` است. تا زمانی که tierها بهتر نشده‌اند، افزایش تعداد تصمیم‌های BUY/HOLD/SELL هدف درستی نیست.
