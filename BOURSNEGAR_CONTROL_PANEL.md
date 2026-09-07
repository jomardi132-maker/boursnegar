# بورس‌نگار — صفحهٔ کنترل واحد

این فایل نقطهٔ شروع روزانهٔ پروژه است. برای کار معمول، گزارش‌های تاریخی و کل
`CURRENT_STATE.md` را نخوان. فقط این فایل، `PROJECT_BACKLOG.md` و آخرین entry
از `CURRENT_STATE.md` مرجع هستند.

نقش و وضعیت همهٔ CLIهای Python در `data-service/scripts/README.md` ثبت شده است.

## وضعیت تثبیت‌شده در 2026-09-07

- Production در `/healthz` سالم و در `/readyz` آماده است؛ PM2 برنامهٔ وب آنلاین است.
- data-service فعال از release `/var/www/boursnegar-data-releases/20260907T184251Z-main-fdcec7067-sync` اجرا می‌شود؛ rollback فوری `/var/www/boursnegar-data-releases/20260907T183731Z-main-fdcec7067` است.
- دیتابیس Production حدود 3.3 GB است. جدول خام `codalpy_records` حدود 2.8 GB از آن را تشکیل می‌دهد.
- دیتابیس canonical لوکال فقط `data-service/artifacts/local-ingestion.sqlite3` است و `PRAGMA quick_check=ok` دارد.
- `artifacts/local-ingestion.sqlite3` یک snapshot قدیمی و غیرcanonical است؛ حذف نشود، اما هیچ workflow پیش‌فرضی نباید از آن استفاده کند.
- artifactهای محلی evidence هستند و زیر `data-service/artifacts/` نگهداری می‌شوند؛ Git آن‌ها را track نمی‌کند.
- سه timer کاربر فعال‌اند: collector محلی، coverage audit و backup-retention check.
- timer ساعتی legacy در Production غیرفعال است؛ import همان manifest ثابت فقط از promotion صریح و backup-gated مجاز است.
- alert worker سرور artifact معتبر دارد، اما timer آن تا زمان فعال‌شدن feature/SMS و وجود alert واقعی غیرفعال است؛ service برای فعال‌سازی آینده حفظ شده است.
- migration registry با schema واقعی همگام است: `027_valuation_inputs`، `028_industry_model_policies` و `029_reconcile_nav_valuation_inputs` ثبت‌اند.
- فقط آخرین coverage/retention cycle در مسیر فعال می‌ماند؛ cycleهای دستی تکراری 2026-09-06 زیر `data-service/artifacts/archive/repeated-manual-cycles-20260906/` نگهداری می‌شوند.
- readiness صندوق‌ها: `419` فعال، `80` دارای NAV معتبر و هر `80` مورد دارای NAV+units معتبرِ هم‌دوره؛ صف NAV-only خالی است. `339` صندوق بدون NAV معتبر فقط با evidence رسمی تازه قابل پیگیری‌اند.
- طبق تصمیم فعلی کاربر، بازار، backtest و پایش/کار روی timerهای روزانه تا پایان سایر کارها خارج از محدوده‌اند؛ وضعیت ثبت‌شدهٔ آن‌ها فقط سابقه است و اقدام بعدی محسوب نمی‌شود.

## تنها workflow روزانه

`boursnegar-local-codal-monitor.timer`
→ `daily_orchestrator.py`
→ `boursnegar_daily_supervisor.py`
→ `daily_codal_monitor.py`
→ `daily_local_ingestion.py`

این زنجیره collection-only است. import به Production فقط از workflow مستقل و
backup-gated مجاز است. اجرای دستی موازی یا اجرای `run_all_incomplete.py` ممنوع است.

## طبقه‌بندی ابزارهای Python

### فعال و زمان‌بندی‌شده

- `daily_orchestrator.py`
- `boursnegar_daily_supervisor.py`
- `daily_codal_monitor.py`
- `daily_local_ingestion.py`
- `scheduled_coverage_audit.py`
- `scheduled_backup_retention.py`

### ابزارهای کنترل‌شدهٔ دستی

- collection/normalize: `browser_codal_fetch.py`, `codalpy_local_fetch.py`, `normalize_browser_statements.py`, `normalize_notice_events.py`
- promotion: `promote_evidence.py`, `auto_local_to_production.py`, `codalpy_remote_import.py`
- audit/repair: فایل‌های `audit_*`, `repair_*`, `reconcile_*`, `backtest_valuation_models.py`
- snapshot/market: `refresh_recent_snapshots.py`, `refresh_internal_snapshots.py`, `update_market_daily.py`

ابزار دستی فقط وقتی اجرا می‌شود که delta واقعی، ورودی مشخص، معیار پایان و مسیر report
داشته باشد. ابزار promotion علاوه بر این‌ها به manifest، SHA-256، backup، replay
idempotent و health/readiness نیاز دارد.

### متوقف از اجرای روزمره

- `run_all_incomplete.py`: batch تاریخی پرهزینه؛ بدون `--acknowledge-historical-batch` اجرا نمی‌شود.
- `backfill_codal_1404.py`: backfill تاریخی و database-writing؛ بدون `--acknowledge-historical-batch` اجرا نمی‌شود.
- `backfill_market_1404.py`: backfill تاریخی، نه کار روزانه؛ طبق تصمیم فعلی خارج از محدوده است.
- `daily_local_ingestion.py` به‌صورت مستقیم: فقط از orchestrator یا اجرای تشخیصی محدود.
- recoveryهای نام‌دار قدیمی: بدون evidence تازه resume نشوند.

## گیت‌های باز واقعی

1. backtest بیست‌جلسه‌ای: 13 نمونهٔ واقعی از حداقل 30؛ فعلاً به تصمیم کاربر deferred است.
2. `339` صندوق بدون NAV معتبر: فقط با evidence رسمی تازه و تطبیق issuer/period/source/unit؛ صف NAV-only بسته است.
3. FCFE/DCF: هشت نماد OCF، CapEx و net borrowing هم‌دوره دارند، اما cost of equity و terminal growth مستند کل Production صفرند؛ تا ورود نرخ رسمی `INSUFFICIENT_DATA` بماند. انتخاب بعدی باید دقیقاً به کلید دورهٔ جاری Production join شود؛ latest محلی کافی نیست.
4. زنجیرهٔ collector تا promotion زمان‌بندی‌شده هنوز عمداً جدا و backup-gated است.
5. جدول خام `codalpy_records` بزرگ است، اما تا تدوین retention مبتنی بر provenance حذف یا فشرده نمی‌شود.

## قانون توقف

- بدون delta تازه هیچ recovery، audit، backup یا report تکرار نشود.
- HTTP 200، build یا وجود artifact به‌تنهایی پایان کار نیست.
- داده، هویت، واحد، دوره یا عملکرد تاریخی ساخته یا forward-fill نشود.
- اگر Production سالم و گیت‌ها بدون delta هستند، اقدام درست «عدم اجرا» است.

## دستورات verification

از `data-service/`:

```bash
venv/bin/python -m unittest discover -s tests -p 'test_*.py'
```

از `web/`:

```bash
npm run typecheck
npm test -- --run
npm run build
```

سلامت عمومی:

```bash
curl -fsS https://boursnegar.ir/healthz
curl -fsS https://boursnegar.ir/readyz
```
