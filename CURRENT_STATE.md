# وضعیت فعلی بورس‌نگار

آخرین بررسی: ۱۴۰۵/۰۶/۰۶، 2026-08-28T07:35:00+03:30؛ آخرین recovery audit: 2026-08-28T01:02:06Z

## بررسی اسکرینر صفحه اصلی، 2026-08-28

علت «داده ناکافی» برای بخشی از نمادها فقط ناقص‌بودن پایگاه داده نبود: انتخاب‌گر گزارش جدیدترین دوره‌ی ناقص یا گزارش یکی از زیرمجموعه‌ها را قبل از دوره‌ی کامل تلفیقی انتخاب می‌کرد. منطق انتخاب در `data-service/app/main.py` اصلاح شد تا دوره‌ای که حداقل درآمد و سود خالص معتبر ندارد مبنای تحلیل نشود و گزارش تلفیقی هم‌دوره اولویت بگیرد.

در نتیجه هر ۱۰ نماد صفحه‌ی اول پاسخ تحلیلی ساختاریافته دارند. وضعیت‌های رسمی فعلی عبارت‌اند از: وبملت/فزر/فملی/شپنا «بررسی مشروط»، فولاد «نگهداری»، خودرو «فروش»، تیپیکو/دلقما «تکمیل داده»، و ومعادن/میدکو «تکمیل داده». برای نمادهای مشروط، بازه‌ی ارزش‌گذاری و محدوده‌ی خرید/فروش نمایش داده می‌شود؛ اما تا رسیدن پوشش و اطمینان به حد لازم، توصیه‌ی قطعی ساخته نمی‌شود.

برای «ومعادن» و «میدکو» پس از اصلاح، تحلیل به‌ترتیب با پوشش ۴۲٫۸۶٪ و ارزش سناریویی ۱۹۰۸ و ۵۵۸ ریال ثبت شد. داده‌ی محلی واقعی است و در Production هم اکنون قابل استفاده است، ولی به‌دلیل نبود چند سنجه‌ی اصلی هنوز برای تصمیم قطعی کافی نیست. لینک اطلاعیه‌ها از رکوردهای رسمی کدال یا پیوند جست‌وجوی رسمی همان نماد ارائه می‌شود.

کد و تست این اصلاح در PR شمارهٔ ۲۹ با merge commit `92a1c23` وارد `main` شد؛ سرویس فعال روی release `complete-period-selection` است. بکاپ‌های قبل از انتشار و قبل از refresh تحلیل حفظ شده‌اند.

## خلاصه اجرایی

Production فعال است و مسیر اجرایی واقعی همچنان Nginx -> PM2 `bourse-app` -> `127.0.0.1:3000` و FastAPI روی `127.0.0.1:8001` است. پس از بررسی read-only، یک پاک‌سازی محدود و transaction-guarded برای ۹ رکورد تکراری/بی‌وابستگی انجام شد؛ قبل از تغییر backup و rollback SQL ساخته شد و هیچ داده‌ای حذف نشد.

شکاف ارتباطی GitHub قبلی رفع شده است: remote پیش‌فرض repo اکنون HTTPS است و تغییرات audit از مسیر Pull Request شمارهٔ ۱ با merge commit `09fcac38` وارد `main` شده‌اند. هیچ force-push انجام نشد.

## وضعیت لوکال و Git

- شاخه فعلی: `agent/data-engine-v1`
- آخرین commit شاخهٔ کاری: `07aab8ab458ea2d3ef9530191e822a13ac5ce11c`
- آخرین merge commit مستندات در `main`: `9c6aec22cc761f349528a7a90536bc199381eb25`
- `origin`: `https://github.com/jomardi132-maker/boursnegar.git`
- `origin/agent/data-engine-v1`: با HEAD شاخهٔ کاری همسان است (`e2e241a7`).
- `origin/main`: شامل تغییرات این دوره با merge commit `09fcac38` است.
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
  - post-cleanup JSON: `artifacts/production-audits/coverage-after-alias-cleanup-20260827T055539Z.json`
  - post-cleanup symbol JSON/CSV: `artifacts/production-audits/symbol-coverage-after-alias-cleanup-20260827T055609Z.json` و `.csv`
  - post-sync JSON: `artifacts/production-audits/coverage-after-sync-20260827T1316Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T1947Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2008Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2027Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2043Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2101Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2115Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2133Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2203Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2232Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2258Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2321Z.json`
  - post-supervisor JSON: `artifacts/production-audits/coverage-after-supervisor-20260827T2351Z.json`
  - final post-supervisor JSON: `artifacts/production-audits/boursnegar-coverage-final-20260828T0101Z.json`

این artifactها برای reconciliation ارزشمندند، اما نباید با پوشش کامل Production یکی گرفته شوند. هر ارسال جدید به Production باید manifest/schema/checksum، advisory lock و اجرای تکراری با inserted=0 داشته باشد.

آخرین اعداد Production در 2026-08-28:

- Active instruments: 1,524
- Industry-level current aliases: 1,524
- Active instruments with current alias: 1,524
- Active instruments without current alias: 0
- Financial periods: 15,138
- Financial facts: 55,051
- Valid facts: 26,663
- Raw Codalpy records: 1,371,661
- Linked Codalpy records: 1,323,453
- Monthly records: 928,101
- Linked monthly records: 885,720
- Symbol-level tiers: `CORE_READY=215`, `MISSING_CORE_FACTS=418`, `MISSING_COMPARABLE_PERIODS=891`, `NO_CURRENT_ALIAS=0`
- Latest decisions: `INSUFFICIENT_DATA=1,520`, `SELL=3`, `HOLD=1`, `BUY=0`
- Backup پاک‌سازی alias: `/var/backups/boursnegar/20260827T055454Z-duplicate-symbol-instruments.json`
- Rollback SQL: `/var/backups/boursnegar/20260827T055454Z-duplicate-symbol-instruments.rollback.sql`

## موارد باز

1. پوشش داده: همچنان نباید ادعای «تحلیل کامل همه نمادها» کرد. معیار فعلی باید provenance، دوره، نوع fact، واحد و source باشد.
2. رکوردهای Codalpy بدون نماد: فقط با artifact/manifest/source رسمی قابل اصلاح‌اند؛ انتساب حدسی ممنوع است.
3. comment automation: مسیر بدون نشست احراز هویت‌شده end-to-end هنوز معیار تکمیل نیست.
4. UI: health و HTTP 200 کافی نیست؛ برای تغییرات UI بعدی باید DOM/console/network و viewport موبایل/دسکتاپ بررسی شود.

آخرین چرخهٔ supervisor: batchهای 0131 تا 0141، مجموعاً ۱۰۸ نماد با exit code صفر، و صف recovery به صفر رسید. ممیزی نهایی با `generatedAt=2026-08-28T01:02:06.755565Z` ثبت شد؛ پس از پایان کار، health سبز بود و هیچ Chrome/profile متعلق به ingestion باقی نماند. این پایان صف recovery است، نه پایان پوشش تحلیلی؛ tierهای fact، دوره و provenance همچنان معیار اعتبار هستند.

## شواهد رندر زنده

- صفحهٔ اصلی `https://boursnegar.ir/` در مرورگر واقعی روی desktop رندر شد؛ عنوان، وضعیت اتصال، اعداد عملیاتی، screener و جدول قابل مشاهده بودند و خطای کنسول ثبت نشد.
- همان صفحه در viewport موبایل ۳۹۰×۸۴۴ رندر شد؛ DOM خوانا بود، دکمهٔ منو حاضر بود، خطای کنسول ثبت نشد و `scrollWidth` با عرض viewport برابر بود.
- احراز هویت‌شدهٔ moderator و چرخهٔ واقعی comment/reward هنوز اجرا نشده است؛ بدون نشست معتبر یا هویت مجاز، ایجاد comment یا reward ممنوع است.

## اقدام بعدی پیشنهادی

اولویت عملی بعدی، ادامهٔ batchهای محدود local-first برای نمادهای `MISSING_COMPARABLE_PERIODS` و `MISSING_CORE_FACTS` است. supervisor اکنون فقط artifactهای نمادهای همان batch را aggregate می‌کند و از خواندن کل تاریخچه جلوگیری می‌شود. تا زمانی که tierها بهتر نشده‌اند، افزایش تعداد تصمیم‌های BUY/HOLD/SELL هدف درستی نیست.
