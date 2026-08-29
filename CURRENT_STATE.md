# وضعیت فعلی بورس‌نگار

آخرین بررسی: ۱۴۰۵/۰۶/۰۶، 2026-08-28T07:35:00+03:30؛ آخرین recovery audit: 2026-08-28T01:02:06Z

## بررسی اسکرینر صفحه اصلی، 2026-08-28

علت «داده ناکافی» برای بخشی از نمادها فقط ناقص‌بودن پایگاه داده نبود: انتخاب‌گر گزارش جدیدترین دوره‌ی ناقص یا گزارش یکی از زیرمجموعه‌ها را قبل از دوره‌ی کامل تلفیقی انتخاب می‌کرد. منطق انتخاب در `data-service/app/main.py` اصلاح شد تا دوره‌ای که حداقل درآمد و سود خالص معتبر ندارد مبنای تحلیل نشود و گزارش تلفیقی هم‌دوره اولویت بگیرد.

در نتیجه هر ۱۰ نماد صفحه‌ی اول پاسخ تحلیلی ساختاریافته دارند. وضعیت‌های رسمی فعلی عبارت‌اند از: وبملت/فزر/فملی/شپنا «بررسی مشروط»، فولاد «نگهداری»، خودرو «فروش»، تیپیکو/دلقما «تکمیل داده»، و ومعادن/میدکو «تکمیل داده». برای نمادهای مشروط، بازه‌ی ارزش‌گذاری و محدوده‌ی خرید/فروش نمایش داده می‌شود؛ اما تا رسیدن پوشش و اطمینان به حد لازم، توصیه‌ی قطعی ساخته نمی‌شود.

برای «ومعادن» و «میدکو» پس از اصلاح، تحلیل به‌ترتیب با پوشش ۴۲٫۸۶٪ و ارزش سناریویی ۱۹۰۸ و ۵۵۸ ریال ثبت شد. داده‌ی محلی واقعی است و در Production هم اکنون قابل استفاده است، ولی به‌دلیل نبود چند سنجه‌ی اصلی هنوز برای تصمیم قطعی کافی نیست. لینک اطلاعیه‌ها از رکوردهای رسمی کدال یا پیوند جست‌وجوی رسمی همان نماد ارائه می‌شود.

کد و تست این اصلاح در PR شمارهٔ ۲۹ با merge commit `92a1c23` وارد `main` شد؛ سرویس فعال روی release `complete-period-selection` است. بکاپ‌های قبل از انتشار و قبل از refresh تحلیل حفظ شده‌اند.

## تکمیل‌های 2026-08-29

- داده‌های استانداردشده‌ی معتبر کچاد و همراه با manifest و checksum بررسی و به‌صورت idempotent replay شدند؛ چون رکوردهای مرکزی از قبل موجود بودند، import جدید رکورد تکراری ایجاد نکرد.
- snapshot تحلیلی هر ۱۰ نماد فعلی صفحه اصلی با FastAPI داخلی refresh شد. شبندر از حالت بدون snapshot خارج شد؛ نمادهای بدون پوشش قبلی نیز اکنون وضعیت واقعی خود را نشان می‌دهند.
- اسکرینر وب اکنون برداشت سریع کاربرمحور، روند بر پایه قیمت/میانگین ۲۰ و ۵۰ روزه، و عنوان صریح «محدوده خرید/فروش ارزش‌گذاری» دارد. روند تکنیکال مکمل ارزش‌گذاری است و به‌تنهایی سیگنال خرید محسوب نمی‌شود.
- release فعال وب `20260829T055849Z-technical-screener-real` و سرویس داده `complete-period-selection` هستند؛ health عمومی و داخلی موفق است. بکاپ‌های `20260829T055125Z-homepage-symbol-promotion.dump` و `20260829T055849Z-web-before-technical-screener.tar.gz` حفظ شده‌اند.
- PRهای ۳۱ و ۳۲ merge شده‌اند. تست وب ۶۳ مورد، تست Python سرویس داده ۷۳ مورد، typecheck و build موفق‌اند. تست یکپارچه هشدار پیامکی به‌دلیل نبود `DATABASE_URL` محلی اجرا نشد؛ کد worker همچنان opt-in و SMS-disabled پیش‌فرض است.
- گیت‌های باقی‌مانده‌ی واقعی: دریافت artifact مالی معتبر برای شبندر در صورت نیاز به refresh عمیق‌تر، تکمیل پوشش سنجه‌های ناقص همه نمادها، ساخت لینک مستقیم Codal فقط وقتی `LetterSerial` واقعی موجود باشد، و E2E مدیریت دیدگاه/پاداش با نشست مجاز واقعی.

## تکمیل سراسری 2026-08-29

- پس از بررسی checksum و import idempotent artifactهای محلی، ۶۶۸ نماد دارای درآمد معتبر با endpoint داخلی تحلیل refresh شدند؛ برای هر ۶۶۸ درخواست، پاسخ JSON معتبر و HTTP 200 ثبت شد.
- snapshot اسکرینر Production اکنون برای ۶۰۷ نماد قابل استفاده است: ۸۶ `CONDITIONAL_REVIEW`، ۴۸۱ `DATA_REVIEW`، ۲۹ فروش، ۹ نگهداری و ۲ خرید. ۶۲ نماد همچنان `NOT_EVALUABLE` هستند و گزارش مالی معتبر قابل مبنا ندارند.
- کل universe فعال ۶۶۹ نماد است و هر ۱۰ ردیف صفحه اصلی فعلی snapshot، پوشش، محدوده ارزش‌گذاری، روند ۲۰/۵۰ روزه، بنیاد و برداشت سریع دارند.
- محدوده‌ها عمداً valuation-based هستند و در کنار روند تکنیکال نمایش داده می‌شوند؛ سیستم آن‌ها را حمایت/مقاومت قطعی یا توصیه سرمایه‌گذاری معرفی نمی‌کند.
- بکاپ پیش از import گسترده: `/var/backups/boursnegar/20260829T060528Z-all-local-normalized-before-import.dump`؛ release وب فعال پس از لینک‌های رسمی: `20260829T060145Z-codal-links-real`.

ممیزی نهایی 2026-08-29 نشان داد ۶۲ نماد `NOT_EVALUABLE` باقی‌مانده، با وجود اینکه بعضی در ledger محلی status کامل دارند، الزاماً درآمد و سود خالص معتبر هم‌دوره ندارند یا صندوق/هلدینگ هستند؛ این وضعیت کمبود واقعی evidence است و با عددسازی رفع نمی‌شود. endpointهای حساس هشدار/دیدگاه بدون نشست معتبر ۴۰۱ برمی‌گردانند و worker پیامکی به‌صورت opt-in و خاموش باقی مانده است.

پروتکل ثبت حافظه‌ی زنده و قابل تکرار در [docs/PROJECT_MEMORY_PROTOCOL.md](docs/PROJECT_MEMORY_PROTOCOL.md) ثبت شد؛ اجرای بعدی باید قبل/بعد از کار آن را رعایت کند.

### اصلاح انتخاب گزارش‌های هم‌دوره، 2026-08-29

برای حالتی که صورت سود و زیان و ترازنامه در دو اطلاعیه‌ی کدال با `period_id` متفاوت اما با تاریخ پایان، طول دوره، دامنه‌ی تلفیقی/شرکت اصلی و وضعیت حسابرسی یکسان منتشر شده‌اند، انتخاب‌گر اکنون همان مجموعه‌ی دقیق را با هم ارزیابی می‌کند. این تغییر از ترکیب داده‌ی شرکت اصلی و زیرمجموعه جلوگیری می‌کند.

در آزمون Production برای میدکو، کچاد، همراه و ومعادن، پوشش همچنان ۴۲٫۸۶٪ و سنجه‌های گمشده شامل جریان نقد عملیاتی و اقلام ترازنامه باقی ماند؛ برای شپنا پوشش ۸۵٫۷۱٪ و تنها جریان نقد عملیاتی گمشده بود. بنابراین این اصلاح یکپارچگی را بهتر کرد، اما بدون وجود evidence معتبر جدید، پوشش را مصنوعی افزایش نداد. release فعال سرویس داده `20260829T063021Z-same-period-merge` و بکاپ قبل از انتشار `/var/backups/boursnegar/20260829T063021Z-data-before-same-period-merge.tar.gz` است.

آخرین اعتبارسنجی لوکال: ۷۳ تست Python و ۶۳ تست وب موفق، lint، typecheck، build و `git diff --check` موفق. گیت‌های باقی‌مانده محدود به دریافت evidence معتبر برای نمادهای ناقص/غیرقابل‌ارزیابی، اجرای تست worker هشدار با `DATABASE_URL` واقعی و اجرای E2E دیدگاه/پاداش با نشست مجاز واقعی هستند؛ هیچ‌کدام با داده یا هویت ساختگی قابل بستن نیستند.

### تاریخچه‌ی چنددوره‌ای و aliasهای فاصله‌دار، 2026-08-29

پاسخ v2 اکنون چهار گروه مالی اخیرِ هم‌دامنه و هم‌وضعیت حسابرسی را، با درآمد، سود خالص، جریان نقد عملیاتی و رشد فقط در برابر دوره‌ی قبلیِ هم‌طول، به snapshot و گزارش کاربر منتقل می‌کند. در refresh سراسری ۶۶۲ از ۶۶۸ نماد پاسخ معتبر و دارای فیلد تاریخچه ثبت شد؛ شش مورد باقی‌مانده فقط به‌دلیل فاصله‌ی داخلی در alias رد شده بودند و پس از اصلاح validator هر شش مورد نیز پاسخ معتبر گرفتند. audit اصلی در `/var/backups/boursnegar/20260829T064125Z-financial-history-refresh.json` ثبت شده است.

release فعال وب و داده هر دو `20260829T101500Z-financial-history` هستند؛ health واقعی وب `/healthz` و سرویس داده `/health` موفق‌اند. backupهای این انتشار شامل `/var/backups/boursnegar/20260829T101500Z-financial-history-data-before-financial-history.tar.gz` و `/var/backups/boursnegar/20260829T101500Z-financial-history-web-before-financial-history.tar.gz` و backup اصلاح alias `/var/backups/boursnegar/20260829T110000Z-data-before-spaced-alias-fix.tar.gz` هستند. PRهای ۳۹ و ۴۰ merge شده‌اند.

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

### بازیابی جریان نقد عملیاتی از artifactهای browser-Codal - 2026-08-29

- علت ریشه‌ای `INSUFFICIENT_DATA` در این بخش، نبود داده خام نبود: 223 سند HTML/XLS/XLSX محلی عبارت جریان نقد عملیاتی داشتند، اما soft-hyphen و یک نام‌گذاری معتبر فارسی در parser شناسایی نمی‌شد.
- parser اکنون soft-hyphen را normalize می‌کند و دو الگوی «جریان خالص ورود (خروج) نقد ... فعالیت‌های عملیاتی» را می‌شناسد. تست‌های data-service: 75 مورد، همگی پاس.
- 48 بسته به‌صورت batch پردازش شد: 1,429 رکورد مالی، شامل 149 رکورد operating_cash_flow برای 44 نماد و 112 ترکیب نماد/دوره/دامنه/حسابرسی؛ 148 مورد IRR_million و 1 مورد IRR_billion. خطاهای 120 سند parse/document در manifest نگه‌داری شده و رکورد مبهم وارد نشده است.
- Production با backup `/var/backups/boursnegar/20260829T130000Z-cashflow-parser-fix-before-import.dump`، manifest/checksum و advisory lock به‌روزرسانی شد: 1,414 رکورد جدید، اجرای تکراری 0، خطای validation صفر. سپس 43 نماد از 44 نماد دوباره با `latest_codal` تحلیل شدند؛ نماد آرمان به‌علت نبود گزارش واردشده با پاسخ `برای نماد ... گزارش واردشده‌ای موجود نیست` باقی ماند.
- artifactهای ممیزی: `artifacts/cashflow-batches-20260829T121500Z/` و `artifacts/cashflow-parser-fix-20260829T124500Z/`. این بازیابی coverage را بهتر می‌کند اما به‌تنهایی ادعای تحلیل کامل همه نمادها نیست.

### لینک مستقیم اطلاعیه‌های رسمی - 2026-08-29

- parser و importer اکنون فقط URLهای `https://codal.ir/Reports/Decision.aspx...` و `https://excel.codal.ir/...` قابل‌اثبات را در provenance نگه می‌دارند؛ URLهای ناشناخته/غیر HTTPS رد می‌شوند.
- برای artifactهای browser-Codal، 1,429 رکورد مالی با URL اطلاعیه و 1,429 رکورد با URL فایل مالی نرمال شد؛ در Production پس از import، 302 لینک مستقیم اطلاعیه و 302 لینک مستقیم فایل مالی در metadata معتبر ثبت شد.
- `data-service` روی release `/var/www/boursnegar-data-releases/20260829T140000Z-codal-links` و web روی `/var/www/boursnegar-releases/20260829T140000Z-codal-links` فعال است. backupهای قبل از rollout در `/var/backups/boursnegar/20260829T140000Z-codal-links-data-before.tar.gz` و `/var/backups/boursnegar/20260829T140000Z-codal-links-web-before.tar.gz` نگهداری می‌شوند.
- صفحه سهم اکنون لینک مستقیم را در صورت وجود نشان می‌دهد و فقط در نبود شواهد به فهرست رسمی نماد fallback می‌کند؛ در viewport موبایل 390×844، 6 لینک مستقیم برای «آ س پ»، بدون خطای console و بدون overflow، مشاهده شد.

### هشدارهای مبتنی بر محدوده ارزش‌گذاری - 2026-08-29

- هشدارهای `buy_zone` و `sell_zone` به schema و UI اضافه شدند. این دو نوع target دستی ندارند و فقط از `fairValueBase * 0.80` و `fairValueHigh * 1.15` همان snapshot معتبر استفاده می‌کنند.
- worker اکنون snapshot نسخه v2 را می‌خواند و همچنان opt-in، محدودشده، دارای advisory lock، deduplication و سقف ارسال در هر اجراست. در Production اجرای safety با هر دو پرچم SMS خاموش، بدون ارسال پیامک و با خروج موفق انجام شد.
- migration `021_valuation_alerts` روی دیتابیس با backup `/var/backups/boursnegar/20260829T160000Z-valuation-alerts-before-migration.dump` اعمال شد؛ constraintهای `alerts_kind_check` و `alerts_target_check` موجودند.
- release فعال web: `/var/www/boursnegar-releases/20260829T160000Z-valuation-alerts`. health عمومی و screener عمومی پس از rollout موفق بودند.
- ناسازگاری `schema_migrations` نیز رفع شد: migrationهای موجود 012، 013، 014، 015 مالی، 017 و 020 پس از بررسی idempotency با مالک دیتابیس ثبت شدند؛ `scripts/migrate.ts` روی همان release بعد از اصلاح بدون خطا و بدون migration جدید اجرا شد.

### مقایسه هم‌صنعت با داده واقعی - 2026-08-29

- endpoint `/api/stocks/:symbol` اکنون peerهای همان صنعت را از قیمت معتبر و آخرین snapshot می‌سازد؛ فقط نماد فعال با پوشش حداقل ۷۰٪ وارد جدول می‌شود و حداکثر ۵ ردیف نمایش داده می‌شود.
- صفحه سهم جدول «مقایسه با شواهد هم‌صنعت» را با سلامت بنیادی، پوشش، P/E، ROE و نتیجه فعلی نشان می‌دهد و صریحاً آن را رتبه‌بندی/توصیه مستقل معرفی نمی‌کند.
- Production release `/var/www/boursnegar-releases/20260829T173000Z-peer-comparison` فعال است. برای «شپنا» دو peer واقعی (`شتران` و `شبندر`) در desktop و mobile دیده شد؛ console error صفر و overflow موبایل صفر بود.

### پوشش fallback اسکرینر - 2026-08-29

- برای نمادهایی که snapshot تحلیلی ندارند، اسکرینر اکنون آخرین دوره مالی و هفت fact اصلی معتبر را از Production محاسبه می‌کند؛ این مقدار فقط پوشش evidence را نشان می‌دهد و بدون snapshot تصمیم BUY/HOLD/SELL تولید نمی‌کند.
- یک خطای cast و سپس یک خطای نام ستون در rollout شناسایی و اصلاح شد. release فعال `/var/www/boursnegar-releases/20260829T183000Z-fact-coverage` با backupهای فایل build در `/var/backups/boursnegar/20260829T193000Z-fact-coverage-hotfix-server.cjs` و `/var/backups/boursnegar/20260829T194500Z-fact-coverage-join-fix-server.cjs` قابل بازگشت است.
- پاسخ زنده `GET /api/market/screener?sort=health` با موفقیت ۵۰ ردیف از مجموع ۶۹۵ ردیف را برگرداند. صفحه اصلی در مرورگر واقعی ۱۰ ردیف، پوشش ۴۳٪ تا ۸۶٪، بنیاد و وضعیت اقدام را نشان داد و خطای console ثبت نشد.
- ممیزی فعلی Production: snapshotها شامل ۸ خرید، ۳۱ نگهداری، ۹۶ فروش و ۳٬۳۵۱ مورد `INSUFFICIENT_DATA` هستند؛ fact معتبر جریان نقد عملیاتی هنوز ۱۴۹ رکورد است. این اعداد نشان می‌دهند fallback نمایش بهتر شده، اما پوشش تحلیلی کامل نشده است.
- آزمون بدون نشست معتبر، `POST /api/comments` و `POST /api/alerts` و `GET /api/admin/comments` را به‌ترتیب با ۴۰۱ رد کرد. احراز هویت‌شدهٔ moderator/reward همچنان تنها گیت بیرونی باقی‌مانده است.
- برای چهار نماد ناقص صفحه اصلی (`میدکو، کچاد، کگل، ومعادن`) در جمع‌آوری local-only کدال ۴ فایل و ۱۱۸ سند رسمی دریافت شد؛ نرمال‌سازی ۲۰۵ رکورد و ۱۸ خطای parse/سندِ غیرقابل استفاده ثبت کرد و import با ۸۹ رکورد جدید، ۸۵ fact معتبر و خطای validation صفر انجام شد. backup پیش از import در `/var/backups/boursnegar/20260829T210000Z-homepage-core-import-before.dump` است.
- پس از refresh با `latest_codal`، هر چهار نماد در اسکرینر پوشش ۵۷٫۱۴٪، محدوده ارزش‌گذاری و وضعیت `DATA_REVIEW`/`INCOMPLETE_EVIDENCE` دارند. cash flow عملیاتی برای گزارش‌های واردشده ثبت شده، ولی ترازنامه/دوره مقایسه‌ای کامل هنوز برای تصمیم قطعی کافی نیست.
- انتخاب‌گر گزارش اصلاح شد تا income statement و balance sheet جداگانه اما هم‌دوره را بر اساس تاریخ، طول دوره، scope و audit با هم merge کند؛ شرط revenue/net profit دیگر period ترازنامه را حذف نمی‌کند. پس از deploy، هر چهار نماد ۱۰/۱۰ سنجه اصلی، پوشش ۱۰۰٪ و تحلیل تازه دریافت کردند: میدکو و کچاد `SELL` مبتنی بر ارزش‌گذاری، کگل و ومعادن `CONDITIONAL_REVIEW`.
- `report_used.detail_url` نیز به snapshot منتقل شد؛ برای میدکو، کچاد، کگل و ومعادن `sourceLineage.codalDocument` اکنون لینک مستقیم واقعی `codal.ir/Reports/Decision.aspx` است. backup سرویس قبل از این اصلاح `/var/backups/boursnegar/20260829T230000Z-provenance-report-used-main.py` است.
- batch دوم برای `همراه، خساپا، خبهمن، رمپنا` چهار فایل و ۱۲۲ سند رسمی دریافت کرد؛ نرمال‌سازی ۳۰۶ رکورد با ۳۱ خطای retained انجام شد و import Production با backup `/var/backups/boursnegar/20260830T003000Z-homepage-core-2-import-before.dump`، ۳۳ رکورد جدید/۳۳ fact و validation صفر داشت؛ اجرای تکراری `inserted=0` بود.
- پس از refresh، هر چهار نماد پوشش ۱۰۰٪ دارند و لینک مستقیم کدال در source lineage ثبت شده است. خروجی تحلیلی فعلی: همراه و خبهمن `INSUFFICIENT_DATA` با هشدار واگرایی بازار/بنیاد، خساپا و رمپنا `SELL`؛ اسکرینر نیز پوشش ۱۰۰٪ را نشان می‌دهد، اما نبود مدل ارزش‌گذاری صنعت برای برخی نمادها صریحاً حفظ شده است.
- برای گیت چنددوره‌ای، batch سال ۱۴۰۳ برای `شبندر، شستا، میدکو، ومعادن، کچاد، کگل` شامل ۱۶۷ سند و ۱۹۶ رکورد استاندارد بود؛ import با backup `/var/backups/boursnegar/20260830T033000Z-homepage-history-1403-import-before.dump` تعداد ۱۹۶ fact استاندارد و validation صفر داشت. به‌دلیل تفاوت واقعی scope/طول دوره، فقط تاریخچهٔ هم‌طول قابل مقایسه فعال می‌شود؛ مقایسهٔ نامعتبر ساخته نشد.
- مدل صنعت `holding` برای شرکت‌های چندرشته‌ای اضافه شد: P/B فقط به‌عنوان proxy حقوق صاحبان سهام حسابداری، نه NAV، با بازهٔ سناریویی محافظه‌کارانه و محدودیت صریح. پس از deploy و refresh، شستا مدل `price_to_book` با پوشش ۸۵٫۷۱٪ و لینک مستقیم کدال دارد؛ به‌دلیل نبود جریان نقد عملیاتی همچنان `INSUFFICIENT_DATA` است و تصمیم قطعی صادر نمی‌شود. backupهای این rollout در `/var/backups/boursnegar/20260830T053000Z-holding-model-*` نگهداری می‌شوند.
- فضای دیسک Production با حفظ release فعال `20260829T183000Z-fact-coverage` و rollbackهای نزدیک، فقط با حذف ۶ release قدیمی و دارای سابقه rollout از ۱۰۰٪ به ۹۲٪ رسید؛ health وب و data service پس از cleanup سبز ماند. کنترل اجرایی حافظه در `scripts/project-memory-check.sh` اضافه شد و در هر handoff قابل اجراست.
- safety run واقعی `dist/alert-worker.cjs` با `ALERT_WORKER_ENABLED=false` و `SMS_ENABLED=false` با خروجی `alert-worker disabled` پایان یافت؛ در محیط Production `KAVENEGAR_API_KEY` وجود دارد اما sender خالی است و `DATABASE_URL` در web.env تنظیم نیست، بنابراین ارسال پیامک عمداً اجرا نشد. listing عمومی comment با ۲۰۰ و endpointهای alerts/admin با ۴۰۱ بدون نشست پاسخ دادند.
- ابزار `scripts/project-memory-note.sh <slug>` به پروتکل اضافه شد؛ با timestamp یکتا فقط قالب یک یادداشت جدید را می‌سازد و بازنویسی حافظه قبلی را ممکن نمی‌کند. در محیط موقت ساخت فایل و کنترل `project-memory-check.sh` با موفقیت آزموده شد.
- batch سوم برای partialهای نمای اصلی (`شپنا، وبملت، خودرو، شبندر، فولاد، شستا`) شامل ۱۷۴ سند، ۳۶۶ رکورد استاندارد و ۳۰ خطای retained بود؛ import با backup `/var/backups/boursnegar/20260830T120000Z-homepage-partial-import-before.dump` تعداد ۳۴۳ رکورد و ۳۵۲ fact جدید، validation صفر و replay بعدی inserted=0 داشت.
- پس از refresh، وبملت، خودرو، شبندر و فولاد به پوشش ۱۰۰٪ رسیدند؛ شپنا و شستا به‌ترتیب با missing `operating_cash_flow` در coverage ۸۵٫۷۱٪ باقی ماندند. هر ۱۰ ردیف نمای پیش‌فرض coverage غیرخالی دارند؛ شستا مدل P/B proxy و لینک مستقیم کدال دارد و تصمیم قطعی آن همچنان مسدود است.

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

## اصلاح طول دوره و recovery کم پوشش - 2026-08-30

- علت ریشه‌ای بخشی از خطای مقایسه چنددوره‌ای پیدا شد: importer طول دوره را از پنجره جست‌وجو محاسبه می‌کرد، نه از عنوان رسمی گزارش. parser اکنون الگوی «N ماهه» و عنوان سالانه را استخراج می‌کند و normalizer/importer همین مقدار را حمل می‌کنند؛ برای artifactهای قدیمی fallback قبلی حفظ شده است.
- ابزار `data-service/scripts/repair_financial_period_lengths.py` با backup `/var/backups/boursnegar/20260830T190000Z-period-length-repair-v4-before.dump` اجرا شد. ۶۱۳۲ ردیف اصلاح یا ادغام شدند؛ اجرای audit بعدی `mismatches=0` بود. شمارش نهایی پس از repair: ۱۵۴۳۵ دوره، ۵۶۶۹۲ fact و ۲۸۷۸۹ fact معتبر.
- یک bug اجرایی در `auto_local_to_production.py` نیز رفع شد: پوشه run قبل از checkpoint lookup ساخته می‌شود. تست‌های data-service پس از اصلاح: ۷۹ مورد، همگی پاس.
- recovery کم‌پوشش برای ۵۰ نماد با local browser/Codal و checkpoint اجرا شد. خروجی Production با backup `/var/backups/boursnegar/20260830T102900Z-auto-local-to-production.dump` شامل ۳ manifest و ۱۰۲۶۸۴ رکورد بود؛ import اول ۵۰۰۸ fact استاندارد و بدون validation error داشت و replay idempotent نیز عبور کرد. health/ready هر دو سبز هستند.
- پس از انتقال و refresh هر ۵۰ نماد بدون خطای endpoint تحلیل شدند. وضعیت فعلی ۵۰ ردیف: ۱۳ مورد coverage=100، ۳۰ مورد 85.71، سه مورد 71.43، یک مورد 42.86 و سه مورد 28.57؛ تصمیم‌ها ۶ SELL، یک HOLD و ۴۳ INSUFFICIENT_DATA هستند. شستا پس از داده تازه به 100٪ رسید.
- این اعداد نشان می‌دهند pipeline و provenance سالم‌اند، اما کمبود شواهد بنیادی برای ۴۳ نماد هنوز واقعی است؛ پوشش ظاهری نباید به توصیه قطعی تبدیل شود. timeoutهای Codal در manifest همان نماد retained شده‌اند.

## recovery دقیق نمادهای ناقص نمای اصلی - 2026-08-30

- فهرست زنده نمای اصلی به ۳۷ نماد با پوشش کمتر از ۱۰۰٪ محدود شد و در `artifacts/homepage-partial-symbols-20260830.txt` ثبت شد. گزینه `--symbols-file` به `auto_local_to_production.py` اضافه شد تا انتخاب هدف صریح و با alias فعال Production اعتبارسنجی شود.
- اجرای اول به‌علت timeout یک نماد متوقف می‌شد؛ pipeline اکنون خطای هر نماد را retained می‌کند و به نماد بعدی ادامه می‌دهد. همچنین reuse checkpoint مسیر دوبل نماد اصلاح شد.
- اجرای دقیق ۳۷ نماد با backup `/var/backups/boursnegar/20260830T120829Z-auto-local-to-production.dump` تکمیل شد: ۳ manifest، ۲۳۱۳۱۱ رکورد، بدون validation error و بدون symbol failure. audit طول دوره پس از انتقال `mismatches=0` بود.
- پس از refresh واقعی `latest_codal`، از ۵۰ ردیف نمای اصلی ۴۱ نماد coverage=100، هفت نماد coverage=85.71 و دو نماد coverage=28.57 دارند؛ همه ۵۰ endpoint بدون خطا پاسخ دادند. تصمیم‌ها ۶ SELL، یک HOLD و ۴۳ INSUFFICIENT_DATA است.
- ۹ نماد ناقص باقی‌مانده عبارت‌اند از `شپنا، احیا، فزر، شبریز، سیسکو، ددانا، انرژی، فاراک، ونوین`. این موارد به‌دلیل کمبود fact/سند معتبر در مبنای تحلیل مسدودند، نه به‌دلیل مشکل صفحه یا API. باید فقط با سند معتبر بعدی یا artifact قابل‌اثبات تکمیل شوند.

## انتخاب تازه‌ترین گزارش و audit نهایی نمای اصلی - 2026-08-30

- در `data-service/app/main.py` ترتیب انتخاب گروه گزارش اصلاح شد: ابتدا جدیدترین تاریخ پایان دوره، سپس برای همان دوره scope تلفیقی، و بعد وضعیت حسابرسی ترجیح داده می‌شود. این مانع انتخاب صورت مالی تلفیقی قدیمی‌تر به‌جای گزارش جدیدتر می‌شود.
- rollout سرویس با backup `/var/backups/boursnegar/20260830T131500Z-homepage-selection-fix-before.py` انجام شد؛ سرویس active است و health پاسخ `ok` دارد.
- پس از refresh هر ۵۰ تحلیل `latest_codal` بدون خطای endpoint بازتولید شدند. پوشش: ۴۴ ردیف ۱۰۰٪، چهار ردیف ۸۵٫۷۱٪ و دو ردیف ۲۸٫۵۷٪. موارد ناقص فعلی: `شبریز، ددانا، وگردش، انرژی، فاراک، ونوین`.
- تصمیم‌های صفحه اصلی: ۶ `SELL`، یک `HOLD` و ۴۳ `INSUFFICIENT_DATA`. در ۴۳ مورد، واگرایی بازار/بنیاد یا نبود cash-flow هم‌دوره مانع نتیجه قطعی است؛ این رفتار مورد انتظار سیاست evidence-only است.
- تست‌ها پس از اصلاح: data-service تعداد ۸۱ و web تعداد ۶۴ موفق؛ build وب موفق؛ `project-memory-check.sh` و `git diff --check` موفق و worktree clean است. رندر زنده قبلی desktop/mobile بدون console error و overflow ثبت شده و تغییر فعلی فقط سرویس داده است.
