# Registry ابزارهای Python در data-service

این فایل مرجع انتخاب ابزار است. نبودن import یا reference داخلی به معنی «بلااستفاده»
بودن یک CLI مستقل نیست. هر فایل اجرایی این پوشه باید در یکی از گروه‌های زیر ثبت
شود؛ تست repository از اضافه‌شدن اسکریپت بی‌هویت جلوگیری می‌کند.

## مسیر canonical غیر‌بازاری

- `auto_local_to_production.py` — orchestrator امن local-to-Production؛ پیش‌فرض dry-run و write فقط پس از manifest/checksum/backup/replay.
- `browser_codal_fetch.py` — جمع‌آوری محلی با Chrome و checkpoint.
- `build_local_codal_db.py` — ساخت mirror محلی از artifactهای موجود.
- `codalpy_local_fetch.py` — collector محلی artifact-only.
- `codalpy_remote_import.py` — importer استاندارد، بدون client شبکه و idempotent.
- `daily_local_ingestion.py` — pipeline محدود Codalpy و fallback مرورگر؛ اجرای انبوه نیست.
- `daily_orchestrator.py` — coordinator محدود؛ زمان‌بندی فعلاً خارج از محدوده است.
- `ingestion_console.py` — کنسول اپراتوری canonical.
- `normalize_browser_industry.py` — normalization صنعت از artifact مرورگر.
- `normalize_browser_statements.py` — normalization صورت مالی بدون مقدارسازی.
- `normalize_notice_events.py` — normalization رویدادهای رسمی.
- `plan_local_recovery.py` — برنامهٔ recovery محلی و deterministic.
- `promote_evidence.py` — promotion استاندارد با gateهای evidence و rollback.
- `promote_notice_events.py` — promotion رویداد با manifest معتبر.
- `recalculate_local_coverage.py` — محاسبهٔ coverage در mirror محلی.
- `reconcile_local_artifacts.py` — inventory محلی بدون download.
- `refresh_internal_snapshots.py` — refresh فقط از evidence واردشده.
- `refresh_recent_snapshots.py` — refresh محدود به evidence تازه.

## ممیزی و صف بررسی — read-only یا خروجی محلی

- `analysis_coverage_audit.py` — ممیزی coverage و ریسک تصمیم.
- `audit_nav_consistency.py` — تطبیق NAV خام و promoted؛ DB را تغییر نمی‌دهد.
- `audit_orphan_financial_documents.py` — parse سندهای orphan بدون promotion.
- `audit_promotion_reports.py` — ممیزی reportهای promotion.
- `audit_valuation_input_gates.py` — ممیزی گیت NAV/FCFE/DCF.
- `backtest_valuation_models.py` — ارزیابی forward؛ بازار فعلاً خارج از محدوده است.
- `curate_nav_queue.py` — ساخت صف کوچک NAV از artifactهای موجود.
- `export_candidate_review.py` — export موارد unresolved برای review.
- `reconcile_public_gate_registry.py` — تطبیق registry عمومی با evidence tierها.
- `scheduled_backup_retention.py` — validator غیرمخرب؛ زمان‌بندی فعلاً خارج از محدوده است.
- `scheduled_coverage_audit.py` — ثبت ممیزی؛ زمان‌بندی فعلاً خارج از محدوده است.

## ابزارهای محدودِ تغییر داده

این گروه بدون ورودی معتبر، backup متناسب و معیار پایان نباید اجرا شود.

- `backfill_industry_model_families.py` — backfill deterministic خانوادهٔ صنعت.
- `export_promoted_remote_manifest.py` — export checksum-backed از facts تأییدشده.
- `import_macro_seed.py` — seed منابع macro؛ فقط با provenance رسمی.
- `import_rahavard_public_reports.py` — collector عمومی به quarantine، نه financial facts.
- `import_rahavard_staging.py` — ثبت artifactهای Rahavard در staging قرنطینه.
- `ingest_codal_financials.py` — parse اسناد cacheشده؛ مسیر عمومی روزانه نیست.
- `link_orphan_candidates.py` — link فقط با tracing number یکتا.
- `promote_local_candidates.py` — promotion محلی فقط برای candidate کاملاً linked.
- `relink_existing_codal_records.py` — replay idempotent برای lineage رکوردهای موجود.
- `repair_browser_period_lengths.py` — repair فقط از عنوان رسمی disclosure.
- `repair_cashflow_output_types.py` — migration یک‌بارمصرف نوع OCF؛ مقادیر را تغییر نمی‌دهد.
- `repair_financial_period_lengths.py` — audit/repair دوره فقط از عنوان رسمی.
- `sync_corporate_action_notices.py` — ثبت رویداد سرمایه فقط با lineage کامل.

## بازار — فعلاً خارج از محدوده

این ابزارها حذف یا تغییر داده نمی‌شوند و تا تصمیم بعدی اجرا نمی‌شوند.

- `backfill_market_1404.py`
- `export_market_bundle.py`
- `export_market_catalog.py`
- `import_market_bundle.py`
- `market_local_fetch.py`
- `market_remote_import.py`
- `update_market_daily.py`

## legacy یا تشخیصی — برای اجرای عادی ممنوع

- `backfill_codal_1404.py` — backfill تاریخی DB-writing؛ نیازمند `--acknowledge-historical-batch`.
- `run_all_incomplete.py` — supervisor انبوه تاریخی؛ نیازمند `--acknowledge-historical-batch`.
- `ingest_codalpy.py` — CLI تشخیصی قدیمی؛ persistence آن opt-in و مسیر canonical نیست.
- `boursnegar_daily_supervisor.py` — wrapper گزارش‌ساز؛ coordinator canonical، `daily_orchestrator.py` است.
- `daily_codal_monitor.py` — wrapper collector؛ timer روزانه فعلاً خارج از محدوده است.

## قانون حذف

یک اسکریپت فقط وقتی حذف می‌شود که جایگزین canonical آن مشخص باشد، هیچ unit/deploy/test
یا artifact rollback به آن وابسته نباشد و بازتولید evidence به آن نیاز نداشته باشد.
«صفر reference در grep» به‌تنهایی مجوز حذف نیست.
