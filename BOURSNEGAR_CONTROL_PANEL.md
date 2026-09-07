# بورس‌نگار — صفحهٔ کنترل واحد

این فایل نقطهٔ شروع روزانهٔ پروژه است. برای کار معمول، گزارش‌های تاریخی و کل
`CURRENT_STATE.md` را نخوان. فقط این فایل، `PROJECT_BACKLOG.md` و آخرین entry
از `CURRENT_STATE.md` مرجع هستند.

## وضعیت تثبیت‌شده در 2026-09-07

- Production در `/healthz` سالم و در `/readyz` آماده است؛ PM2 برنامهٔ وب آنلاین است.
- دیتابیس Production حدود 3.3 GB است. جدول خام `codalpy_records` حدود 2.8 GB از آن را تشکیل می‌دهد.
- دیتابیس canonical لوکال فقط `data-service/artifacts/local-ingestion.sqlite3` است و `PRAGMA quick_check=ok` دارد.
- `artifacts/local-ingestion.sqlite3` یک snapshot قدیمی و غیرcanonical است؛ حذف نشود، اما هیچ workflow پیش‌فرضی نباید از آن استفاده کند.
- artifactهای محلی evidence هستند و زیر `data-service/artifacts/` نگهداری می‌شوند؛ Git آن‌ها را track نمی‌کند.
- سه timer کاربر فعال‌اند: collector محلی، coverage audit و backup-retention check.

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

- `run_all_incomplete.py`: batch تاریخی پرهزینه؛ فقط برای مطالعه نگه‌داری شود.
- `backfill_codal_1404.py`, `backfill_market_1404.py`: backfillهای تاریخی، نه کار روزانه.
- `daily_local_ingestion.py` به‌صورت مستقیم: فقط از orchestrator یا اجرای تشخیصی محدود.
- recoveryهای نام‌دار قدیمی: بدون evidence تازه resume نشوند.

## گیت‌های باز واقعی

1. backtest بیست‌جلسه‌ای: 13 نمونهٔ واقعی از حداقل 30؛ فقط با گذشت جلسات معتبر کامل می‌شود.
2. موارد REVIEW صندوق‌ها: فقط با evidence رسمی و تطبیق issuer/period/source/unit.
3. FCFE/DCF: تا وجود OCF، CapEx، net borrowing و نرخ‌های هم‌دوره `INSUFFICIENT_DATA` بماند.
4. زنجیرهٔ collector تا promotion زمان‌بندی‌شده هنوز عمداً جدا و backup-gated است.

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
