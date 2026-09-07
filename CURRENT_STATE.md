# وضعیت فعلی بورس‌نگار

## کارت اجرای سریع — نقطهٔ شروع هر نوبت

- ابتدا [BOURSNEGAR_EXECUTION_CARD.md](BOURSNEGAR_EXECUTION_CARD.md) را بخوان؛ سپس فقط آخرین entry و جدیدترین report را بررسی کن.
- برای ممیزی پایان هدف، [GOAL_COMPLETION_MATRIX.md](GOAL_COMPLETION_MATRIX.md) را نیز بخوان؛ این ماتریس جایگزین artifact یا report فنی نیست.
- بدون delta واقعی، batch، audit یا backup تکرار نکن. upstream نامعتبر یعنی checkpoint + backoff + بدون import.
- promotion فقط با manifest/SHA-256، یک backup، replay با `inserted=0`، refresh و health/ready مجاز است.
- وضعیت مرجع: ۱۵۲۴ نماد فعال؛ `721 CORE_READY`، `419 FUND_MODEL_REQUIRED`، `384 MISSING_COMPARABLE_PERIODS`.
- blocker فعلی: پاسخ `search.codal.ir` غیرJSON و Chrome مستقلِ متصل در دسترس نیست؛ داده‌سازی یا تفسیر absence ممنوع.

## 2026-09-07 - بازبینی زمان‌بندی collector محلی

- unit و timer کاربر `boursnegar-local-codal-monitor.timer` هر دو `enabled/active` هستند و برای امروز اجرای monitor با وضعیت `already-ran-today` گزارش شد؛ بنابراین schedule دوباره ساخته یا تکرار نشد.
- اجرای dry-run با `batch-size=3` و `--no-import` هیچ artifact یا import جدیدی ایجاد نکرد. گیت واقعی همچنان دسترسی Chrome/session معتبر و پاسخ JSON معتبر از upstream است؛ تا بسته‌شدن آن، freshness یا نبود اطلاعیه ادعا نمی‌شود.

## 2026-09-07 - گیت اجرای ممیزی NAV

- اجرای read-only ابزار `audit_nav_consistency.py` با `PYTHONPATH=.` به کد رسید، اما PostgreSQL محلی روی `localhost:5432` در دسترس نیست.
- ابزار ممیزی در مسیر Production فعلی وجود ندارد (`TOOL_ABSENT`)؛ به همین دلیل برای اجرای آن انتقال یا تغییر Production انجام نشد. صف NAV تا دسترسی به DB معتبر یا انتشار کنترل‌شدهٔ ابزار، متوقف و بدون import باقی ماند.

## 2026-09-07 - ممیزی read-only گیت ارزش‌گذاری Production

- ابزار موجود `audit_valuation_input_gates.py` روی Production بدون write اجرا شد: ۱۵۲۴ نماد، `PASS=473` و `REVIEW=1051`.
- وضعیت `REVIEW` به‌عنوان کمبود evidence یا عبور نکردن یکی از گیت‌های shares/OCF/equity/sustainable-profit/unit حفظ شد؛ هیچ promotion یا اصلاح داده انجام نشد.
- گزارش موقت در مسیر `/tmp/boursnegar-nav-gate-20260907.json` روی Production تولید شد و اقدام بعدی فقط پس از انتخاب evidence مشخص است.

## 2026-09-07 - اجرای واقعی collector محلی با Chrome

- با Chrome متصل، اجرای محدود و بدون import برای `آ س پ`، `آبادا` و `آبادا3` انجام شد؛ browser capture، normalize مالی و notice و ساخت local DB همگی با خطای صفر پایان یافتند.
- برای هر سه نماد checkpoint وضعیت `NO_NOTICES` و صفر فایل ثبت کرد. این نتیجه نبود اطلاعیه را اثبات نمی‌کند و به Production منتقل نشد.
- artifact و manifest در `data-service/artifacts/daily-codal-live-20260907/14050616/` نگهداری شد؛ مسیر collector محلی اکنون عملیاتی و قابل ادامه با batch بعدی است.

## 2026-09-07 - اولویت‌بندی صف صندوق‌ها

- از ۴۱۹ صندوق فعال، توزیع گیت‌ها چنین است: `passed_gates=0: 12`، `1: 176`، `2: 30` و `3: 201`.
- ۱۲ مورد با صفر گیت عبوری (`آرمانی، بزرگ2، تدبیریکم، ثنا2، دیوان، زرگر2، سافرون2، ستاره4، صایند2، طعام2، نوآور، پالایش2`) برای بررسی evidence اولیه اولویت گرفتند؛ این فهرست candidate است و به‌معنی فقدان تاریخی داده نیست.
- به‌دلیل نبود Chrome/session معتبر و نبود ابزار NAV در Production، جمع‌آوری یا promotion این فهرست انجام نشد.

## 2026-09-07 - recovery هدفمند NAV، batch001 و batch002

- batch001 برای `آرمانی`، `بزرگ2` و `تدبیریکم` و batch002 برای `ثنا2`، `دیوان` و `زرگر2` با بازهٔ `1404/01/01` تا `1405/06/16` اجرا شدند.
- هر دو batch با capture/normalize بدون خطا پایان یافتند، اما هر شش نماد `NO_NOTICES` و صفر evidence برگشتند؛ هیچ‌کدام به‌عنوان نبود تاریخی داده علامت‌گذاری یا promote نشدند.
- artifactها در `data-service/artifacts/fund-nav-live-20260907/batch-001/` و `batch-002/` حفظ شدند و ادامه از صف بعدی فقط با همان گیت‌های provenance مجاز است.

## 2026-09-07 - recovery هدفمند NAV، batch003 و batch004

- batch003 برای `سافرون2`، `ستاره4` و `صایند2` و batch004 برای `طعام2`، `نوآور` و `پالایش2` با همان بازهٔ تاریخی اجرا شدند.
- هر دو batch با صفر خطا و صفر رکورد normalize پایان یافتند؛ هر شش نماد `NO_NOTICES` ماندند و هیچ promotion یا importی انجام نشد.
- artifactها در `data-service/artifacts/fund-nav-live-20260907/batch-003/` و `batch-004/` حفظ شدند؛ زیرصف ۱۲ نماد اولویت‌دار اکنون کامل بررسی شده و برای evidence معتبر نتیجه‌ای تولید نکرده است.

## 2026-09-07 - بازبینی backtest بیست‌جلسه‌ای Production

- backtest با روش `forward_valid_sessions` و گیت `quality_status=VALID AND volume>0` روی ۴۱۶۸ snapshot اجرا شد.
- افق ۵ جلسه‌ای `2652` و افق ۱۰ جلسه‌ای `73` نمونهٔ قابل‌مقایسه و از نظر حداقل ۳۰ نمونه `READY` هستند.
- افق ۲۰ جلسه‌ای فقط `13` نمونهٔ قابل‌مقایسه دارد و `INSUFFICIENT_SAMPLE` باقی ماند؛ snapshot تاریخی مصنوعی ساخته نشد. نتیجه در `/tmp/boursnegar-backtest-20260907.json` روی Production ثبت شد.

## 2026-09-06 - smoke مسیر daily_local_ingestion

- `daily_local_ingestion.py` با `--codalpy-first --dry-run` برای `فولاد` اجرا شد؛ برنامه‌ی Codalpy، browser fallback، normalize مالی، normalize notice و build local DB معتبر تولید شد.
- `--precheck` برای همین نماد به‌دلیل وضعیت complete آن را از صف حذف کرد؛ این نشان می‌دهد precheck با registry فعلی کار می‌کند، اما schedule روزانه‌ی session-aware هنوز در لایه‌ی سیستم‌عامل تعریف نشده است.

## 2026-09-06 - audit معماری collector روزانه کدال

- روی سیستم محلی `google-chrome` و `browser_codal_fetch.py` موجود است، اما unit روزانه‌ای برای اجرای collector مرورگر وجود ندارد.
- `boursnegar-codal-backfill.service` عمداً retired و `ExecStart=/usr/bin/true` است؛ unit Production فقط artifactهای محلی را import می‌کند. collector بدون Chrome profile/session واقعی یا روی Production اضافه نشد، چون با provenance و محدودیت no-direct-Codal سازگار نیست.
- گیت freshness اطلاعیه‌ها تا ایجاد یک job محلیِ session-aware و انتقال manifest/checksum به Production باز می‌ماند.

## 2026-09-06 - گیت freshness اطلاعیه‌های کدال

- `codal_notice_events` در Production آخرین `retrieved_at=2026-08-31 03:05 UTC` را دارد و در ۴۸ ساعت اخیر رکوردی ثبت نشده است.
- timer مالی روزانه فقط artifactهای محلی موجود را import می‌کند و به‌تنهایی پایش روزانه‌ی Codal را انجام نمی‌دهد؛ بنابراین گیت freshness اطلاعیه‌ها باز است. این کمبود به‌عنوان «نبود اطلاعیه» تفسیر نشد و تا اتصال collector مرورگر محلی به schedule، ادعای پایش روزانه صادر نمی‌شود.

## 2026-09-06 - audit قابل‌تکرار سازگاری NAV

- ابزار `data-service/scripts/audit_nav_consistency.py` اضافه و روی Production اجرا شد. نتیجه: `promoted_total=5`، `non_irr_promotions=5`، `raw_total=24`، `raw_symbols=14`، `raw_non_per_share_units=5` و `exact_source_matches=5`.
- این ابزار تأیید کرد هر پنج promotion قدیمیِ NAV با واحد ناسازگار در وضعیت `REVIEW` هستند و هیچ promotion `VALID` با واحد غیر `IRR` باقی نمانده است؛ raw evidence حذف نشده است.
- خطای bind پارامتر SQLAlchemy در اجرای اول با escape امن literal اصلاح شد و اجرای دوم موفق بود.

## 2026-09-06 - quarantine پنج NAV با واحد ناسازگار

- audit تطبیقی پنج رکورد `valuation_inputs.nav_per_share` با `normalized_unit=IRR_million` و `quality_status=VALID` را پیدا کرد (`امین شهر` دو گزارش، `آتیه ملت`، `امتیاز` و `آتیمس`). NAV per unit بدون سند واحدی معتبر نیست؛ داده حذف نشد و هر پنج مورد به `REVIEW` منتقل شدند.
- backup پیش از update: `/var/backups/boursnegar/20260906T121456Z-nav-unit-quarantine-before-update.dump`، SHA-256=`3b5bd0214e71c3db402f8954d7db6a9bca5204d3617925a4ac77d87723a2d01b`.
- Production با `UPDATE 5` و `/readyz=ready` تأیید شد. raw records و provenance دست‌نخورده باقی ماندند؛ promotion بعدی فقط با واحد `IRR` و تعداد واحد معتبر مجاز است.

## 2026-09-06 - گیت تطبیق raw NAV با promotion

- audit مستقیم نشان داد raw `codalpy_records` شامل duplicateهای چند گزارش و واحدهای ناسازگار (`IRR`/`IRR_million`) است؛ join ساده بر اساس symbol با aliasهای تاریخی تطبیق کاذب تولید می‌کند.
- اختلاف ۱۴ نماد raw و ۴ issuer دارای `valuation_inputs` تا زمان تطبیق یکتای `issuer_id`، period، source disclosure و checksum قابل نتیجه‌گیری نیست. promotion جدید متوقف ماند تا این audit با mapping درست انجام شود.

## 2026-09-06 - ممیزی پوشش واقعی NAV صندوق‌ها

- گزارش مستقیم Production: ۴۱۹ صندوق فعال شناسایی شد؛ فقط ۴ issuer در `valuation_inputs` دارای NAV معتبر هستند و ۴۱۵ مورد هنوز فاقد NAV معتبرِ promotion‌شده‌اند.
- در raw `codalpy_records`، ۱۴ نماد و ۲۴ رکورد با `fact_key=nav_per_share` وجود دارد؛ این با ۴ promotion نهایی یکی نیست و باید در ادامه با provenance/period/واحد audit شود.
- نتیجه: صف NAV هنوز واقعی است، اما روش offset ترتیبی مناسب نیست. ادامه باید از registry یکتای صندوق‌ها و اولویت اسناد دارای NAV/تعداد واحد استخراج‌شده استفاده کند.

## 2026-09-06 - regression test برای NAV صندوق

- دو تست regression برای ردیف رسمی پایان دوره صندوق و قرارداد `units_outstanding` اضافه شد؛ suite محلی اکنون `121/121` موفق است و `git diff --check` نیز موفق ماند.

## 2026-09-06 - verification تغییرات اخیر

- `git diff --check` موفق شد و suite محلی `unittest` با `119/119` موفق اجرا شد.
- تغییرات اخیر محدود به parser/normalize NAV، migration registry policy و handoffهای وضعیت است؛ فایل migration جدید هنوز untracked است و باید در commit/deploy بعدی همراه rollback نگهداری شود.

## 2026-09-06 - بررسی evidence ورودی FCFE/DCF برای فولاد

- در artifactهای رسمی فولاد، مانده‌ی `تسهیلات مالی` در جداول ترازنامه/یادداشت‌ها دیده شد، اما capex و net borrowing به‌صورت جریان نقدی استاندارد و قابل‌اتکا برای period مورد نظر استخراج نشد.
- مانده‌ی بدهی به‌عنوان net borrowing جایگزین نشد؛ این کار از نظر معنایی و provenance نادرست است. برای فولاد و مشابه آن، FCFE/DCF تا زمان وجود هر دو جریان واقعی و نرخ‌های مستند در وضعیت gate باقی می‌ماند.

## 2026-09-06 - registry نسخه‌دار policyهای صنعت

- migration `028_industry_model_policies` اضافه و روی Production اعمال شد؛ ۴۷ policy فعال از familyهای صریح موجود در `industry_valuation.py` ثبت شد: `normalized_pe=39`، `price_to_book=7` و `nav=1`.
- backup قبل از migration: `/var/backups/boursnegar/20260906T120743Z-industry-policy-before-migration.dump`، SHA-256=`4e1d860faa40b7b78a2ef003794b28a9f093fdf9dfb82d64cfef42f6f06d87ca`.
- schema migration و `/readyz=ready` تأیید شدند. rollback متناظر در `web/migrations/028_industry_model_policies.rollback.sql` ثبت است. این policyها سناریوهای داخلی‌اند، نه ادعای consensus بازار.

## 2026-09-06 - audit عمیق مدل‌های صنعت

- در Production برای issuerهای فعال، `industry_id` و `model_family` کامل است؛ اما جدول `industry_model_policies` policy فعال ندارد و یک رکورد عمومی `market:نامشخص` با `model_family=unclassified` باقی است که به issuer فعال وصل نیست.
- مدل‌های اجرایی در `data-service/app/analytics/industry_valuation.py` برای familyهای موجود تعریف شده‌اند. رکورد عمومی نامشخص حذف یا به صنعت خاصی نگاشت نشد، چون evidence رسمی برای آن وجود ندارد؛ گیت policy registry همچنان باز است.

## 2026-09-06 - علت ریشه‌ای کمبود backtest بیست‌جلسه‌ای

- ممیزی Production نشان داد `daily_prices` معتبر از `2025-03-25` تا `2026-09-06` موجود است، اما `analytical_snapshots` از `2026-08-14` شروع می‌شوند.
- بنابراین کمبود افق ۲۰ جلسه‌ای ناشی از کمبود قیمت آینده نیست؛ snapshot تاریخیِ دارای زمان و evidence مالی هم‌زمان وجود ندارد. بازسازی snapshot قدیمی با داده‌های امروز provenance را مخدوش می‌کند و انجام نشد.

## 2026-09-06 - audit backtest جاری Production

- backtest با ۴۱۱۶ snapshot اجرا شد؛ افق ۵ جلسه‌ای `2446/READY` و افق ۱۰ جلسه‌ای `55/READY` است.
- افق ۲۰ جلسه‌ای فقط `9` مورد قابل‌مقایسه دارد و همچنان `INSUFFICIENT_SAMPLE` (حداقل ۳۰) است؛ مشکل کمبود تاریخچه‌ی snapshot است، نه شکست اجرای موتور. هیچ داده یا روز تعطیل به‌صورت مصنوعی اضافه نمی‌شود.

## 2026-09-06 - audit نهایی صنعت و دوره‌های مالی

- ممیزی مستقیم Production: ۱۵۲۴ issuer فعال، `industry_id` خالی=`0` و `model_family` خالی=`0`. گیت نمادهای unclassified بسته است؛ فهرست ۳۷تایی قدیمی دیگر مبنای کار نیست.
- `financial_periods` فقط طول‌های ۱ تا ۱۲ ماه دارد؛ طول‌های غیرواقعی ۱۵/۲۴/۲۷ پس از repair برابر صفر تأیید شد. دوره‌های نامتعارف قبلی دوباره‌کاری نمی‌شوند.

## 2026-09-06 - توقف صف ترتیبی NAV و تغییر راهبرد

- batch149 برای `دجابر`، `دجابر4` و `دحاوی` اجرا شد؛ ۱۳ سند رسمی و ۵۰ رکورد normalized ثبت شد و یک خطای `child_entity_financial_statement` داشت؛ NAV/تعداد واحد قابل promotion پیدا نشد.
- صف ترتیبی بر مبنای offset به‌دلیل تکرار aliasها و بازده پایین متوقف شد. ادامه فقط باید با registry یکتای صندوق‌ها، حذف موارد قبلاً بررسی‌شده، و اولویت‌دهی به اسناد دارای نشانه NAV انجام شود.
- ممیزی سرویس‌های روزانه: importer کدال آخرین بار با exit code صفر و `inserted=0` اجرا شد؛ snapshot refresh با `processed=1, ok=1, errors=0` پایان یافت. هر دو timer فعال‌اند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch148

- batch148 برای `دتوزیع`، `دتوزیع3` و `دتولید` اجرا و normalize شد؛ ۱۲ سند رسمی و ۴۰ رکورد normalized با خطای صفر ثبت شد.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch148/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch147

- batch147 برای `داوه`، `دتماد` و `دتماد3` اجرا و normalize شد؛ ۱۰ سند رسمی و ۲۵ رکورد normalized ثبت شد و یک خطای `child_entity_financial_statement` باقی ماند.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد؛ خطای child-entity به‌عنوان فقدان داده تفسیر نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch147/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch146 و تأیید NAV دانیک

- batch146 برای `دانا`، `دانا3` و `دانیک` اجرا و normalize شد؛ ۸ سند رسمی و ۳۹ رکورد normalized با خطای صفر ثبت شد.
- برای `دانیک` سه جفت NAV/تعداد واحد رسمی استخراج شد: NAVهای `12595` برای `1405/03/31` و `12166` برای `1404/12/29`، با تعداد واحد `150` و provenance/checksum مستقل. این مقادیر از قبل در Production موجود بودند، بنابراین import جدید انجام نشد.
- artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch146/` حفظ شدند.

## 2026-09-06 - promotion کنترل‌شده NAV و تعداد واحد دامون

- batch145 سه جفت NAV/تعداد واحد رسمی برای `دامون` استخراج کرد؛ دوره جدید `1405/02/31` و دو گزارش هم‌دوره `1404/11/30` با وضعیت حسابرسی متفاوت ثبت شدند.
- backup پیش از Production: `/var/backups/boursnegar/20260906T075425Z-nav-damoon-before-import.dump`، SHA-256=`b52f18183009c4ad8bd62cc435702cc1072028e6f0a26cc8e211f33f49888b45`.
- import اول `inserted=6` و replay `inserted=0` بود؛ رکوردها در `codalpy_records` با واحدهای `IRR` و `units` و `/readyz=ready` تأیید شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch144

- batch144 برای `داسوه`، `دالبر` و `دالبر3` اجرا و normalize شد؛ ۱۶ سند رسمی و ۴۰ رکورد normalized با خطای صفر ثبت شد.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch144/` حفظ شدند.

## 2026-09-06 - اصلاح قرارداد normalize تعداد واحد صندوق

- `units_outstanding` اکنون با `output_type=balance_sheet` و `unit=units` normalize می‌شود؛ مقدارهای شمارشی دیگر با واحد پولی اشتباه برچسب نمی‌خورند.
- normalize مجدد batch135، هر سه جفت NAV/تعداد واحد `خورشید` را با قرارداد جدید تولید کرد؛ ۱۱۹ تست موفق ماند و هیچ داده‌ای تغییر عددی نکرد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch143

- batch143 برای `دارو`، `دارو3` و `دارونو` اجرا و normalize شد؛ ۵ سند رسمی و ۲۰ رکورد normalized با خطای صفر ثبت شد.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch143/` حفظ شدند.

## 2026-09-06 - ممیزی گیت ارزش‌گذاری Production

- در `valuation_inputs` فقط `nav_per_share` با وضعیت `VALID` وجود دارد (۵ رکورد). برای `fcfe`، `fcff`، `capital_expenditure`، `net_borrowing`، `cost_of_equity`، `wacc` و `terminal_growth` هیچ ورودی معتبر ثبت نشده است.
- در `valuation_results` فقط مدل‌های `nav` (۵)، `normalized_pe` (۳۲۴۳) و `price_to_book` (۹۰۷) دیده شد؛ بنابراین خروجی DCF/FCFE/Residual Income عددی بدون evidence تولید نمی‌شود و گیت فعلی درست عمل می‌کند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch142

- batch142 برای `داتام`، `داتام3` و `داترا` اجرا و normalize شد؛ ۹ سند رسمی و ۲۷ رکورد normalized ثبت شد و پنج خطای `child_entity_financial_statement` باقی ماند.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد؛ خطاهای child-entity به‌عنوان فقدان داده تفسیر نشدند. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch142/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch141

- batch141 برای `خیمن3`، `دابور` و `دابور3` اجرا و normalize شد؛ ۷ سند رسمی و ۳۰ رکورد normalized با خطای صفر ثبت شد.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch141/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch140

- batch140 برای `خگستر`، `خگستر3` و `خیمن` اجرا و normalize شد؛ ۱۱ سند رسمی و ۳۷ رکورد normalized ثبت شد و سه خطای `child_entity_financial_statement` باقی ماند.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد؛ خطاهای child-entity به‌عنوان فقدان داده تفسیر نشدند. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch140/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch139

- batch139 برای `خکرمان`، `خکمک` و `خکمک3` اجرا و normalize شد؛ ۸ سند رسمی و ۴۰ رکورد normalized ثبت شد و دو خطای `child_entity_financial_statement` باقی ماند.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد؛ خطاهای child-entity به‌عنوان فقدان داده تفسیر نشدند. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch139/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch138

- batch138 برای `خکار`، `خکار3` و `خکاوه` اجرا و normalize شد؛ ۱۱ سند رسمی و ۳۴ رکورد normalized ثبت شد و یک خطای `child_entity_financial_statement` باقی ماند.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد؛ خطای child-entity به‌عنوان فقدان داده تفسیر نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch138/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch137

- batch137 برای `خپویش`، `خچرخش` و `خچرخش3` اجرا و normalize شد؛ ۱۰ سند رسمی و ۴۰ رکورد normalized با خطای صفر ثبت شد.
- NAV یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch137/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch136 پس از اصلاح parser

- batch136 برای `خوشه`، `خوشه2` و `خپارس` اجرا و normalize شد؛ ۸ سند رسمی و ۲۰ رکورد normalized ثبت شد.
- چهار خطا باقی ماند: سه `parse:هیچ جدولی در فایل پیدا نشد` و یک `child_entity_financial_statement`. این خطاها به‌عنوان نبود داده تفسیر نشدند؛ NAV/تعداد واحد عددی معتبر برای promotion به دست نیامد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch136/` حفظ شدند.

## 2026-09-06 - promotion کنترل‌شده NAV و تعداد واحد خورشید

- اصلاح parser و normalize batch135 سه جفت داده رسمی برای `خورشید` استخراج کرد: NAV/تعداد واحد برای پایان دوره‌های `1404/09/30`، `1404/12/29` و `1405/03/31`.
- backup پیش از Production: `/var/backups/boursnegar/20260906T073629Z-nav-khorshid-before-import.dump`، SHA-256=`6de69f47ce25f131918a1e6de1a497ba5aecb50a965cd00c85c618c72654a412`.
- import اول `inserted=6` و import replay `inserted=0` بود؛ رکوردها در `codalpy_records` با مقادیر رسمی و `/readyz` با وضعیت `ready` تأیید شدند.

## 2026-09-06 - اصلاح parser NAV صندوق‌ها

- parser برای ردیف رسمی `خالص دارایی‌ها (واحدهای سرمایه‌گذاری) پایان دوره` اصلاح شد: NAV از ستون قیمت و تعداد واحد از ستون تعداد استخراج می‌شوند؛ صفرهای کاذب NAV قبل از ردیف رسمی نادیده گرفته می‌شوند.
- آزمون‌های واحد `119/119` موفق شد و normalize مجدد batch135 سه NAV رسمی برای `خورشید` استخراج کرد: `22735476`، `21685022` و `24345607` ریال، با provenance و checksum موجود. تعداد واحدها هنوز در خروجی normalized این batch تولید نشده و نیازمند اصلاح مرحله normalize/انتخاب period است؛ promotion فعلاً انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch135 و گیت استخراج NAV

- batch135 برای `خورشید`، `خوساز` و `خوساز3` اجرا و normalize شد؛ ۹ سند رسمی و ۲۹ رکورد normalized با خطای صفر ثبت شد.
- در metadata سند `خورشید`، parser وجود `nav_per_share` را گزارش کرده اما fact عددی NAV در خروجی normalized تولید نشده است؛ این مورد «نبود داده» تلقی نشد و برای اصلاح/بررسی parser و Excel در صف ماند. هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch135/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch134

- batch134 برای `خودرو`، `خودرو3` و `خودکفا` اجرا و normalize شد؛ ۱۰ سند رسمی و ۳۷ رکورد normalized ثبت شد و ۲ خطای `child_entity_financial_statement` در manifest باقی ماند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. خطای child-entity به‌عنوان فقدان داده تفسیر نشده است؛ artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch134/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch133

- batch133 برای `خنور`، `خنور3` و `خودران` اجرا و normalize شد؛ ۶ سند رسمی و ۲۰ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch133/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch132

- batch132 برای `خموتور`، `خموتور3` و `خنصیر` اجرا و normalize شد؛ ۱۴ سند رسمی و ۶۰ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch132/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch131

- batch131 برای `پیشگام`، `چاشنی` و `چاشنی2` اجرا و normalize شد؛ ۱ سند رسمی و ۳ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch131/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch130

- batch130 برای `پیروز`، `پیشران` و `پیشرفت` اجرا و normalize شد؛ ۸ سند رسمی و ۲۴ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch130/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch129

- batch129 برای `پناه2`، `پولاد` و `پویا` اجرا و normalize شد؛ ۲ سند رسمی و ۶ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch129/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch128

- batch128 برای `پرتوسا`، `پلاتا` و `پناه` اجرا و normalize شد؛ ۴ سند رسمی و ۱۲ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch128/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch127

- batch127 برای `پتروپاداش2`، `پرتو` و `پرتو2` اجرا و normalize شد؛ ۳ سند رسمی و ۶ رکورد normalized ثبت شد و یک خطای parser در manifest باقی ماند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. خطای parser به‌عنوان فقدان داده تفسیر نشده است؛ artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch127/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch126

- batch126 برای `پتروفارس`، `پتروما` و `پتروپاداش` اجرا و normalize شد؛ ۳ سند رسمی و ۶ رکورد normalized ثبت شد و یک خطای parser در manifest باقی ماند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. خطای parser به‌عنوان فقدان داده تفسیر نشده است؛ artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch126/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - promotion کنترل‌شدهٔ NAV پتروصبا، batch125

- batch125 برای `پتروسورین`، `پتروصبا` و `پتروصبا2` اجرا شد؛ ۶ سند رسمی و ۲۰ رکورد normalized با خطای صفر ثبت شد.
- دو NAV رسمی برای `پتروصبا` کشف شد: `13367 IRR`، period-end=`1404/12/29`، tracingهای `1512151` (حسابرسی‌شده) و `1510857` (حسابرسی‌نشده)، با checksumهای سند به‌ترتیب `ba550c216c11979b48a8f2a6487e04eb9596ca96b0a1e015b8c1b07ec065bd79` و `4d0d1949caa972e96b61b26ad224f520f8f2d6a4ad0c3fc3ee86c627a20586a8`.
- backup معتبر پیش از import در `/var/backups/boursnegar/20260906T071801Z-nav-petrosaba-before-import.dump` با SHA-256=`af39bcb98f97884ac0e1935c6e141f2f76188156a6975b799fdb581428842d9e` ثبت شد. import اول `inserted=2` و `standard_facts=2`؛ replay با `inserted=0` و خطای صفر انجام شد.
- Production verification هر دو رکورد را تأیید کرد و `/readyz` برابر `{"status":"ready"}` بود. هیچ `units_outstanding` معتبر در batch پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch125/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch124

- batch124 برای `پتروآگاه2`، `پتروداریوش` و `پتروداریوش2` اجرا شد؛ در بازهٔ capture هیچ سند رسمی دریافت نشد (`files=0`) و normalize نیز صفر رکورد و صفر خطا داشت.
- این نتیجه فقط `NO_NOTICES` در بازهٔ جست‌وجوی capture است و به‌عنوان نبود تاریخی NAV یا تعداد واحد تفسیر نشده است. checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch124/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch123

- batch123 برای `پایش`، `پتروآبان` و `پتروآگاه` اجرا و normalize شد؛ ۹ سند رسمی و ۲۷ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch123/` حفظ شدند.

## 2026-09-06 - promotion کنترل‌شدهٔ NAV پایدار، batch122

- batch122 برای `پایا2`، `پایدار` و `پایدار2` اجرا شد؛ ۱ سند رسمی و ۴ رکورد normalized با خطای صفر ثبت شد.
- یک NAV رسمی برای `پایدار` کشف شد: `10000 IRR`، period-end=`1404/09/30`، tracing=`1584793` و سند Excel با checksum=`24f189b3bd1040d3de60cb73cb777f1f5466b5371d635d7b167db4d6aa4ab30c`.
- backup معتبر پیش از import در `/var/backups/boursnegar/20260906T071218Z-nav-paidar-before-import.dump` با SHA-256=`7e510dc385fd9b4b22f3e68cd4a6f8a8dda7a21fdd47dc998336b772481bf115` ثبت شد. import اول `inserted=1` و `standard_facts=1`؛ replay با `inserted=0` و خطای صفر انجام شد.
- Production verification رکورد NAV را تأیید کرد و `/readyz` برابر `{"status":"ready"}` بود. هیچ `units_outstanding` معتبر در batch پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch122/` حفظ شدند.

## 2026-09-06 - candidate رسمی NAV پالایش، batch121

- batch121 برای `پالایش`، `پالایش2` و `پایا` اجرا و normalize شد؛ ۶ سند رسمی و ۱۹ رکورد normalized با خطای صفر ثبت شد.
- یک fact رسمی `nav_per_share` برای `پالایش` با مقدار استخراج‌شدهٔ `1 IRR` و tracing=`1568582` پیدا شد. به‌دلیل ابهام مقیاس/واحد، بدون تصحیح یا حدس promotion نشد و candidate با provenance کامل حفظ شد.
- هیچ `units_outstanding` معتبر پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch121/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch120

- batch120 برای `پارند`، `پارند2` و `پاسارگاد` اجرا و normalize شد؛ ۱ سند رسمی و ۳ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch120/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch119

- batch119 برای `پاداش`، `پاداش2` و `پارتین` اجرا و normalize شد؛ ۴ سند رسمی و ۱۲ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch119/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch118

- batch118 برای `ویستا2`، `ویسرو` و `پادا` اجرا و normalize شد؛ ۴ سند رسمی و ۱۲ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch118/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch117

- batch117 برای `ولتاژ`، `ونچر` و `ویستا` اجرا و normalize شد؛ ۱۱ سند رسمی و ۳۳ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch117/` حفظ شدند؛ یک فایل موقت دانلودی (`.crdownload`) نیز برای پیگیری فنی باقی مانده است.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch116

- batch116 برای `هیبرید`، `هیوا` و `وبازار` اجرا و normalize شد؛ ۵ سند رسمی و ۱۵ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch116/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch115

- batch115 برای `هوشیار`، `هوشیار2` و `هومان` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch115/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch114

- batch114 برای `همگام2`، `همیان` و `هوشمند` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch114/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch113

- batch113 برای `همتا`، `همسنگ` و `همگام` اجرا و normalize شد؛ ۱۰ سند رسمی و ۳۰ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch113/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch112

- batch112 برای `هم وزن`، `هم وزن2` و `همای` اجرا و normalize شد؛ ۷ سند رسمی و ۲۱ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch112/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch111

- batch111 برای `هم ارز2`، `هم تراز` و `هم تراز2` اجرا و normalize شد؛ ۲ سند رسمی و ۶ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch111/` حفظ شدند.

## 2026-09-06 - promotion کنترل‌شدهٔ NAV هم ارز، batch110

- batch110 برای `هامون`، `هدف` و `هم ارز` اجرا شد؛ ۱۱ سند رسمی و ۳۵ رکورد normalized با خطای صفر ثبت شد.
- دو fact رسمی `nav_per_share` برای `هم ارز` با مقدار `9829 IRR`، period-end=`1404/12/29` و tracingهای `1526060` و `1526117` کشف شد.
- backup معتبر پیش از import در `/var/backups/boursnegar/20260905T205909Z-nav-hamarz-before-import.dump` با SHA-256=`56ae3c9e679204578db4593f6041f98511239e45105052d3f1f56e43728671d2` ثبت شد. import اول `inserted=2` و `standard_facts=2`؛ replay با `inserted=0` و خطای صفر انجام شد.
- Production verification هر دو رکورد را تأیید کرد و `/readyz` برابر `{"status":"ready"}` بود. هیچ `units_outstanding` معتبر در batch پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch110/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch109

- batch109 برای `نیلی`، `نیک گستر` و `هامرز` اجرا و normalize شد؛ ۱۰ سند رسمی و ۳۰ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch109/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch108

- batch108 برای `نوآور`، `نگین فارس` و `نیروانا` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch108/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch107

- batch107 برای `نمک`، `نهال` و `نهال2` اجرا و normalize شد؛ ۱ سند رسمی و ۳ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch107/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch106

- batch106 برای `نقرسا`، `نقرفام` و `نقرین` اجرا شد؛ در بازهٔ capture هیچ فایل/سند رسمی دریافت نشد (`files=0`) و normalize نیز صفر رکورد و صفر خطا داشت.
- این نتیجه فقط `NO_NOTICES` در بازهٔ جست‌وجوی capture است و به‌عنوان نبود تاریخی NAV یا تعداد واحد تفسیر نشده است. checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch106/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch105

- batch105 برای `نفیس`، `نقرابی` و `نقران` اجرا و normalize شد؛ ۲ سند رسمی و ۶ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch105/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch104

- batch104 برای `نخل`، `نشان` و `نفتوداریوش` اجرا و normalize شد؛ ۸ سند رسمی و ۲۴ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch104/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch103

- batch103 برای `ناوگان`، `ناوگان2` و `نبات` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch103/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch102

- batch102 برای `ناب2`، `نارنج اهرم` و `نارین` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch102/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch101

- batch101 برای `موج`، `میراث` و `ناب` اجرا و normalize شد؛ ۸ سند رسمی و ۲۴ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch101/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch100

- batch100 برای `مسگون`، `معدن` و `مهرگلد` اجرا شد؛ در بازهٔ capture هیچ فایل/سند رسمی دریافت نشد (`files=0`) و normalize نیز صفر رکورد و صفر خطا داشت.
- این نتیجه فقط `NO_NOTICES` در بازهٔ جست‌وجوی capture است و به‌عنوان نبود تاریخی NAV یا تعداد واحد تفسیر نشده است. checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch100/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch99

- batch99 برای `مدیر`، `مروارید` و `مزه` اجرا و normalize شد؛ ۵ سند رسمی و ۱۵ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch99/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch98

- batch98 برای `مثقال`، `مختلط` و `مختلط2` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch98/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch97

- batch97 برای `ماکان`، `ماکان2` و `متال` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch97/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch96

- batch96 برای `مانی`، `ماهور` و `ماهور4` اجرا و normalize شد؛ ۷ سند رسمی و ۲۱ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch96/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch95

- batch95 برای `لیان`، `مالک آتیه` و `مانا` اجرا و normalize شد؛ ۷ سند رسمی و ۱۵ رکورد normalized ثبت شد و ۲ خطای parser در manifest باقی ماند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. خطاهای parser به‌عنوان فقدان داده تفسیر نشده‌اند؛ artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch95/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch94

- batch94 برای `لبخند`، `لذیذ` و `لذیذ2` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch94/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch93

- batch93 برای `فیروزه`، `قلک گلد` و `قیراط` اجرا و normalize شد؛ ۸ سند رسمی و ۲۴ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch93/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch92

- batch92 برای `فلزفارابی`، `فیروزا` و `فیروزا4` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch92/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch91

- batch91 برای `فرصت`، `فلزا` و `فلزا2` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch91/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch90

- batch90 برای `فرا الگوریتم`، `فراز` و `فردا` اجرا و normalize شد؛ ۸ سند رسمی و ۲۴ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch90/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch89

- batch89 برای `فارما کیان`، `فارما کیان2` و `فارمانی` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch89/` حفظ شدند.

## 2026-09-06 - candidate رسمی NAV عیار، batch88

- batch88 برای `عیار`، `فاخر` و `فاخر2` اجرا و normalize شد؛ ۵ سند رسمی و ۱۷ رکورد normalized با خطای صفر ثبت شد.
- دو fact رسمی `nav_per_share` برای `عیار` با مقدار استخراج‌شدهٔ `1 IRR` و tracingهای `1593671` و `1550213` پیدا شد. به‌دلیل ابهام مقیاس/واحد، بدون تصحیح یا حدس promotion نشد و candidate با provenance کامل حفظ شد.
- هیچ `units_outstanding` معتبر پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch88/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch87

- batch87 برای `عرش`، `عقیق` و `عمارت دی` اجرا شد؛ ۱ سند رسمی دریافت شد اما normalize با ۱ خطای parser و صفر رکورد normalized پایان یافت.
- هیچ `nav_per_share` یا `units_outstanding` عددی قابل‌اعتبارسنجی برای promotion پیدا نشد. خطای parser به‌عنوان فقدان داده تفسیر نشده است؛ artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch87/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - candidate رسمی NAV طلا، batch86

- batch86 برای `طلا`، `طلوع` و `طلوع2` اجرا و normalize شد؛ ۲ سند رسمی و ۸ رکورد normalized با خطای صفر ثبت شد.
- دو fact رسمی `nav_per_share` برای `طلا` با مقدار استخراج‌شدهٔ `1 IRR` در tracingهای `1575312` و `1529307` پیدا شد. به‌دلیل ابهام مقیاس/واحد، بدون تصحیح یا حدس promotion نشد و candidate با provenance کامل حفظ شد.
- هیچ `units_outstanding` معتبر پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch86/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch85

- batch85 برای `ضمان`، `طعام` و `طعام2` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch85/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch84

- batch84 برای `صنهال`، `صنهال2` و `صنوین` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch84/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch83

- batch83 برای `صدف`، `صدف2` و `صنم` اجرا و normalize شد؛ ۶ سند رسمی و ۹ رکورد normalized ثبت شد و ۳ خطای parser در manifest باقی ماند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. خطاهای parser به‌عنوان فقدان داده تفسیر نشده‌اند؛ artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch83/` حفظ شدند و هیچ importی انجام نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch82

- batch82 برای `شیلد`، `صایند` و `صایند2` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch82/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch81

- batch81 برای `سیگلو`، `شتاب` و `شمیم` اجرا و normalize شد؛ ۶ سند رسمی و ۱۵ رکورد normalized ثبت شد و یک خطای parser در manifest باقی ماند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. خطای parser به‌عنوان فقدان داده تفسیر نشده است. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch81/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch80

- batch80 برای `سیمانیا`، `سیمین` و `سیناد` اجرا و normalize شد؛ ۸ سند رسمی و ۲۴ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch80/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch79

- batch79 برای `سیلور`، `سیمانا` و `سیمانو` اجرا و normalize شد؛ ۲ سند رسمی و ۶ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch79/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch78

- batch78 برای `سپیدما2`، `سپینود` و `سیان` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch78/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch77

- batch77 برای `سپنتارود`، `سپهر` و `سپیدما` اجرا و normalize شد؛ ۷ سند رسمی و ۲۱ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch77/` حفظ شدند.

## 2026-09-06 - promotion کنترل‌شدهٔ NAV سپر، batch76

- batch76 برای `سپر`، `سپر2` و `سپر4` اجرا شد؛ ۲ سند رسمی و ۸ رکورد normalized با خطای صفر ثبت شد.
- دو NAV رسمی برای `سپر` کشف شد: `43172 IRR` برای period-end=`1405/03/31` با tracing=`1572207` و `39924 IRR` برای period-end=`1404/12/29` با tracing=`1532904`.
- backup معتبر پیش از import در `/var/backups/boursnegar/20260905T202759Z-nav-separ-before-import.dump` با SHA-256=`95ee61f1779e3a29325bf94bc9305113eab1af49dcd8473f067de2572a1916a2` ثبت شد. import اول `inserted=2` و `standard_facts=2`؛ replay با `inserted=0` و خطای صفر انجام شد.
- Production verification هر دو رکورد را تأیید کرد و `/readyz` برابر `{"status":"ready"}` بود. هیچ `units_outstanding` معتبر در batch پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch76/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch75

- batch75 برای `سهامدار`، `سورنافود` و `سولار` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch75/` حفظ شدند.

## 2026-09-06 - candidate رسمی NAV سها، batch74

- batch74 برای `سلام`، `سمان` و `سها` اجرا و normalize شد؛ ۱۰ سند رسمی و ۳۴ رکورد normalized با خطای صفر ثبت شد.
- چهار fact رسمی `nav_per_share` برای `سها` با مقدار استخراج‌شدهٔ `1 IRR` در tracingهای `1573847`، `1556930`، `1550148` و `1512848` پیدا شد. به‌دلیل مقدار غیرعادی و نبود اثبات مستقلِ مقیاس واحد در این خروجی، promotion جدید انجام نشد و candidate با provenance کامل حفظ شد.
- هیچ `units_outstanding` معتبر پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch74/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch73

- batch73 برای `سخند`، `سرو` و `سرو2` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch73/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch72

- batch72 برای `سبزآبنوس`، `ستاره` و `ستاره4` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch72/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch71

- batch71 برای `سافرون`، `سافرون2` و `سام` اجرا و normalize شد؛ ۷ سند رسمی و ۲۱ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch71/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch70

- batch70 برای `زیتون2`، `ساحل` و `ساحل2` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch70/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch69

- batch69 برای `زمرد کوروش`، `زمرد2` و `زیتون` اجرا و normalize شد؛ ۵ سند رسمی و ۱۵ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch69/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch68

- batch68 برای `زرین`، `زرین2` و `زمرد` اجرا و normalize شد؛ ۶ سند رسمی و ۱۶ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch68/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch67

- batch67 برای `زرگر`، `زرگر2` و `زریران` اجرا و normalize شد؛ ۲ سند رسمی و ۶ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch67/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch66

- batch66 برای `زرفام`، `زرفام2` و `زروان` اجرا و normalize شد؛ ۴ سند رسمی و ۱۲ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch66/` حفظ شدند.

## 2026-09-06 - candidate رسمی NAV زر، batch65

- batch65 برای `ریتون`، `ریتون2` و `زر` اجرا شد؛ ۷ سند رسمی و ۲۵ رکورد normalized با خطای صفر ثبت شد.
- چهار fact رسمی `nav_per_share` برای `زر` با مقدار استخراج‌شدهٔ `1 IRR` و tracingهای `1593369`، `1580406`، `1519853` و `1482678` پیدا شد. مقدار غیرعادی است اما از سند رسمی آمده؛ بدون بررسی واحد/مقیاس در منبع، promotion جدید انجام نشد و candidate با provenance کامل نگه‌داری شد.
- هیچ `units_outstanding` معتبر پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch65/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch64

- batch64 برای `رویش`، `رویش همراه` و `رویین` اجرا و normalize شد؛ ۵ سند رسمی و ۱۵ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch64/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch63

- batch63 برای `رشدی کیان`، `رشدی کیان2` و `رونق` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch63/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch62

- batch62 برای `رزگلد`، `رسانا` و `رشد` اجرا و normalize شد؛ ۱۰ سند رسمی و ۳۰ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch62/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch61

- batch61 برای `رایکا`، `رخش` و `رز ترنج` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch61/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch60

- batch60 برای `رابین2`، `رادان` و `رایبد` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch60/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch59

- batch59 برای `دیتا`، `دیوان` و `رابین` اجرا و normalize شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch59/` حفظ شدند.

## 2026-09-06 - promotion کنترل‌شدهٔ NAV دیبا، batch58

- batch58 برای `دی سهام`، `دیار` و `دیبا` اجرا شد؛ ۹ سند رسمی و ۲۸ رکورد normalized با خطای صفر ثبت شد.
- یک NAV رسمی برای `دیبا` کشف شد: `22203 IRR`، period-end=`1404/12/29`، tracing=`1510903` و سند Excel با checksum=`8d5d2043eb7f9e97128ed8ba7099d6134734ebd7129b0cc684d661b0b685b0ae`.
- backup معتبر قبل از import در `/var/backups/boursnegar/20260906T-nav-diba-before-import.dump` با SHA-256=`1ddc28cb600b3fe4c8ffe621e69d46c2096c85ad1ba5b5df5a2bb755ac977b5a` ثبت شد. import اول `inserted=10` و `standard_facts=6` بود؛ replay با `inserted=0` و خطای صفر انجام شد.
- Production verification رکورد NAV را با مقدار `22203.0` تأیید کرد و `/readyz` برابر `{"status":"ready"}` بود. هیچ `units_outstanding` معتبر در این batch پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch58/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch57

- batch57 برای `دفینه`، `دلتا` و `دوایکس` اجرا و normalize شد؛ ۵ سند رسمی و ۱۵ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch57/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch56

- batch56 برای `دریا`، `درین` و `درین2` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch56/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch55

- batch55 برای `درخشان`، `درسا` و `درنا` اجرا و normalize شد؛ ۹ سند رسمی و ۲۷ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch55/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch54

- batch54 برای `داریک2`، `دامون` و `دانیک` اجرا و normalize شد؛ ۵ سند رسمی و ۱۷ رکورد normalized با خطای صفر ثبت شد.
- دو fact رسمی `nav_per_share` برای `دانیک` با مقدار `12595 IRR` و tracingهای `1582208` و `1563947` کشف شد؛ هر دو source_action پیش‌تر در Production وجود داشتند، بنابراین import تکراری لازم نبود و write جدید انجام نشد. هیچ `units_outstanding` معتبر پیدا نشد.
- artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch54/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch53

- batch53 برای `دارونو`، `داریوش` و `داریک` اجرا و normalize شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch53/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch52

- batch52 برای `خوشه2`، `دارا` و `دارا یکم` اجرا و normalize شد؛ ۶ سند رسمی و ۹ رکورد normalized ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد.
- سه خطای parser مربوط به فایل‌های `دارا یکم` با پیام نبود جدول در Excel در manifest حفظ شد؛ این موارد به‌عنوان فقدان داده تفسیر نشده‌اند. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch52/` قرار دارند.

## 2026-09-06 - ممیزی سلامت Production پس از batch51

- اتصال SSH و مسیر canonical Production بررسی شد؛ `boursnegar-data-service.service` و timerهای importer و snapshot همگی `active` هستند.
- endpointهای داخلی `/health` و `/readyz` به‌ترتیب `{"status":"ok"}` و `{"status":"ready"}` پاسخ دادند.
- فضای دیسک ریشه ۲۵G کل، ۱۶G مصرف، ۸.۱G آزاد و ۶۷٪ مصرف است؛ در این نوبت هیچ write یا promotion جدیدی انجام نشد و گیت‌های دادهٔ باقی‌مانده همچنان باز هستند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch51

- batch51 برای `خودران`، `خورشید` و `خوشه` اجرا شد؛ ۶ سند رسمی و ۹ رکورد normalized تولید شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر در خروجی پیدا نشد و هیچ importی انجام نشد.
- سه خطای parser برای فایل‌های `خوشه` به‌دلیل نبود جدول در فایل Excel ثبت شد؛ این خطاها به‌عنوان فقدان تاریخی داده تفسیر نشده‌اند. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch51/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch50

- batch50 برای `جواهر2` و `خاتم` تکمیل شد؛ ۳ سند رسمی و ۹ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch50/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch49

- batch49 برای `جهش`، `جوانه کوچک` و `جواهر` تکمیل شد؛ ۱۱ سند رسمی و ۳۳ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch49/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch48

- batch48 برای `ثهام`، `جام سهند` و `جام طلا` تکمیل شد؛ ۷ سند رسمی و ۲۱ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch48/` حفظ شدند.

## 2026-09-06 - promotion کنترل‌شدهٔ NAV ثروین

- batch47 یک NAV رسمی برای `ثروین` کشف کرد: `10372 IRR`، period-end=`1404/12/29`، tracing=`1518869` و سند Excel رسمی با checksum=`e893df03d4abf1e4ba4496409bb2a92bf570eb2107b88678ccffed641c8ed6da`.
- backup تازهٔ قبل از import در `/var/backups/boursnegar/20260905T195437Z-nav-thervin-before-import.dump` با SHA-256=`d6e318008ede8a66d260c4546853a48dbf09a733e77d7981898ca8574139ab76` تهیه شد. import اول رکورد را ثبت کرد؛ replay با `inserted=0` و خطای صفر idempotent بود.
- Production verification رکورد `codalpy_records` و `financial_facts` را با مقدار `10372.0` و `quality_status='VALID'` تأیید کرد؛ `/readyz` برابر `ready` است. هیچ تعداد واحدی برای این نماد به‌صورت معتبر استخراج نشد.

## 2026-09-06 - ممیزی صف NAV بر اساس checkpoint

- تطبیق خودکار registry رسمی صندوق‌ها با همهٔ checkpointهای artifact نشان داد از ۴۱۹ نماد فعال صندوق، ۱۳۸ نماد سابقهٔ تلاش در corpus محلی دارند و ۳۵۶ نماد هنوز checkpoint ندارند. این شمارش «تلاش‌شده» است و به‌معنی وجود یا نبود NAV نیست.
- این تفکیک برای ادامهٔ batchها ثبت شد تا نمادهای تکراری دوباره بررسی نشوند و `NO_NOTICES` فقط به بازهٔ جست‌وجوی همان capture محدود بماند.

## 2026-09-06 - اعمال retention دو backup در Production

- retention script پس از dry-run و حذف تنها فایل صفر‌بایتِ backup ناموفق اجرا شد؛ همهٔ dumpهای معتبر اعتبارسنجی شدند و policy دو dump آخر با `--apply` اعمال شد. فقط `20260905T190658Z-nav-danik-before-import.dump` و `20260905T192005Z-period-length-before-repair.dump` باقی ماندند.
- report retention در `/var/backups/boursnegar/20260905T195037Z-retention-report.tsv` ثبت شد. فضای `/` از ۷۹٪ به ۶۶٪ رسید (۲۵G کل، ۱۶G مصرف، ۸.۲G آزاد). `/health=ok` و `/readyz=ready` پس از عملیات تأیید شدند؛ raw evidence و rollbackهای غیر dump حذف نشدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch46

- batch46 برای `ارزش مسکن`، `استیل` و `اطلس` تکمیل شد؛ ۳ bundle، ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch46/` حفظ شدند.

## 2026-09-06 - پایش زندهٔ Production

- `boursnegar-data-service.service` و timerهای Codal/snapshot هر سه active هستند؛ endpointهای داخلی `/health` و `/readyz` به‌ترتیب `ok` و `ready` پاسخ دادند.
- آخرین importer در journal با `files=6`، `inserted=0`، `standard_facts=0` و `validation_errors=[]` موفق تمام شد؛ آخرین refresh ثبت‌شده `no_recent_evidence` است. دیسک ریشه ۲۵G، مصرف ۱۹G و فضای آزاد ۵.۱G (۷۹٪) دارد.

## 2026-09-06 - regression test پس از repair دوره‌ها

- `pytest` در virtualenv موجود نبود؛ تست با `unittest discover -s tests -q` اجرا شد: `119/119` موفق و `git diff --check` بدون خطا بود.
- تست‌ها parser، قراردادها، snapshot و market history را پوشش دادند؛ این نتیجه صحت کامل Production را به‌تنهایی اثبات نمی‌کند و health/ready و auditهای Production جداگانه باقی می‌مانند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch45

- batch45 برای `اهرم`، `اوج` و `اوصتا2` تکمیل شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch45/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch44

- batch44 برای `امگا`، `امین یکم` و `اندوخته داریوش` تکمیل شد؛ ۵ سند رسمی و ۱۵ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ importی انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch44/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch43

- batch43 برای `اعتماد4`، `افران` و `امرالد` تکمیل شد؛ ۴ سند رسمی و ۱۲ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch43/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch42

- batch42 برای `اطلس4`، `اطمینان` و `اعتماد2` تکمیل شد؛ `اطمینان` یک bundle با ۳ سند و ۹ رکورد normalized داشت و دو نماد دیگر در بازهٔ بررسی `NO_NOTICES` بودند. خطای normalize صفر بود.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch42/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch41

- batch41 برای `ارکیده`، `ارکیده2` و `ارزش` تکمیل شد؛ ۵ سند رسمی و ۱۵ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch41/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch40

- batch40 برای `آکورد2`، `آگاس` و `اتوداریوش` تکمیل شد؛ `آگاس` یک bundle با ۳ سند و ۹ رکورد normalized داشت و دو نماد دیگر در بازهٔ `1405/01/01` تا `1405/06/14` `NO_NOTICES` بودند. خطای normalize صفر بود.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد؛ artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch40/` حفظ شدند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch39

- batch39 برای `آوان`، `آوان2` و `آکورد` تکمیل شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch39/` حفظ شدند.

## 2026-09-06 - بررسی ورودی FCFE برای فولاد

- capture رسمی `فولاد` در بازهٔ `1404/01/01` تا `1405/06/14` شامل ۷ سند، ۴۰ fact normalized و ۲ خطای ثبت‌شده در manifest بود. OCF، درآمد، سود، دارایی، بدهی و حقوق صاحبان سهام استخراج شدند.
- هیچ `capital_expenditure` یا `net_borrowing` عددی معتبر در خروجی وجود نداشت؛ بنابراین FCFE/DCF عددی ساخته نشد و artifact محلی در `data-service/artifacts/fcfe-followup-foolad-20260906/` با provenance حفظ شد.

## 2026-09-06 - تفکیک گلوگاه parser از کمبود evidence در DCF/FCFE

- جست‌وجوی artifactهای normalized و raw موجود برای ردیف‌های خرید دارایی ثابت، capex، تسهیلات/استقراض و net borrowing نتیجه‌ای نداشت؛ aliases لازم در parser وجود دارند، اما سند cash-flow دارای این ردیف‌ها در corpus فعلی دیده نشد.
- بنابراین کمبود DCF/FCFE فعلاً ناشی از نبود evidence ورودی است، نه صرفاً حذف ردیف توسط parser. هیچ alias حدسی، مقدار استخراج‌شده از متن نامطمئن یا نرخ تنزیل پیش‌فرض اضافه نشد و گیت عدم صدور ارزش ذاتی عددی حفظ شد.

## 2026-09-06 - ممیزی ورودی‌های واقعی DCF/FCFE/Residual Income

- ممیزی مستقیم Production نشان داد تنها `operating_cash_flow` با ۲۰۵۹ رکورد عددی موجود است؛ برای `capital_expenditure`، `net_borrowing`، `fcfe`، `fcff`، `cost_of_equity`، `terminal_growth`، `wacc` و `net_income/book_equity` هیچ رکورد عددی در جدول facts وجود ندارد.
- در نتیجه هیچ DCF، FCFE یا Residual Income عددی صادر نشد و گیت فعلی درست عمل می‌کند. تکمیل این ورودی‌ها نیازمند اسناد رسمی صورت جریان وجوه نقد/یادداشت‌ها و منبع نرخ‌های تنزیل است؛ مقدار پیش‌فرض یا برآورد بدون provenance وارد نشد.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch38

- batch38 برای `آلا2`، `آلتون` و `آلکان` تکمیل شد؛ ۶ سند رسمی و ۱۸ رکورد normalized با خطای صفر ثبت شد.
- برچسب NAV در metadata parser دیده شد، اما هیچ `nav_per_share` یا `units_outstanding` با مقدار عددی معتبر تولید نشد و هیچ promotion انجام نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch38/` حفظ شدند.

## 2026-09-06 - verification coverage پس از repair

- coverage audit کامل روی Production پس از repair اجرا شد: `CORE_READY=721`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=384`؛ global نیز `active_instruments=1524`، `financial_periods=18135`، `valid_facts=38210` و `valid_prices=495634` گزارش کرد.
- ثابت ماندن ۳۸۴ نماد نشان می‌دهد repair دوره‌های duplicate صحت metadata و provenance را اصلاح کرده، اما کمبود دوره‌های معتبرِ هم‌قابل‌مقایسه را پر نکرده است. هیچ داده‌ای برای بهبود مصنوعی coverage ساخته نشد.

## 2026-09-06 - repair کنترل‌شدهٔ دوره‌های هم‌قابل‌مقایسه

- پس از dry-run و backup، اسکریپت `repair_financial_period_lengths.py` از stdin روی interpreter همان release canonical Production با `--apply` اجرا شد. هر ۶۸ candidate بر اساس عنوان رسمی کدال repair شد؛ facts به canonical period همان `disclosure_version` منتقل شدند و periodهای duplicate حذف شدند.
- verification پس از عملیات: تعداد periodهای browser با طول ناسازگار `15/24/27` برابر صفر و `/readyz` برابر `{"status":"ready"}` است. اجرای write روی مسیر اشتباه انجام نشد.
- backup پیش از عملیات: `/var/backups/boursnegar/20260905T192005Z-period-length-before-repair.dump`، SHA-256=`21e6faafe47ff393f73b4c77f055741479a55f591eab96261eb3c2d37db57c92`. provenance منبع خام و checksumهای disclosure حفظ شدند.

## 2026-09-06 - کشف ناسازگاری release در repair دوره‌ها

- اجرای dry-run اسکریپت `repair_financial_period_lengths.py` روی `/var/www/boursnegar-data-current` نشان داد symlink فعلی به release `20260831T203700Z-audited-interim-selection` اشاره می‌کند، اما این release اسکریپت جدید repair را ندارد (`can't open file`). هیچ write یا repair انجام نشد.
- بنابراین پیش از حل duplicate-period باید release canonical و artifact deploy هم‌راستا شوند؛ اجرای اسکریپت از مسیر اشتباه ممنوع است. این finding به‌عنوان blocker عملیاتی مسیر ثبت شد و نیازمند deploy/release کنترل‌شده با backup قبلی است.

## 2026-09-06 - ممیزی industry unclassified

- ممیزی زندهٔ Production تعداد نمادهای فعال با industry تهی/`unclassified` را ۳۷ مورد تأیید کرد: `آ س پ`، `آواک`، `ارفع`، `اپرداز3`، `بتک`، `تمحرکه`، `ثعتما`، `خریخت`، `خفولا`، `درپاد`، `ذرت`، `سیتا`، `سیدکو`، `شگستر`، `غبهنوش`، `غپاک`، `فالوم`، `فرآور`، `فپنتا3`، `قیستو`، `مارون`، `مهرمام`، `نطرین`، `های وب`، `وبملت2`، `ورازی`، `وسدید`، `وشمال`، `ومهان`، `ونیکی`، `وپارس3`، `وپترو3`، `کاریز`، `کایزد`، `کرومیت`، `کساوه` و `کمینا`.
- legal_name در این query به‌تنهایی منبع رسمی صنعت محسوب نشد؛ هیچ mapping حدسی یا تغییر Production انجام نشد. این ۳۷ مورد همچنان باید از مرجع رسمی صنعت/بورس یا evidence شرکتی معتبر تکمیل شوند.

## 2026-09-06 - صف هدفمند صندوق‌ها، batch37

- صف جمع‌آوری با فیلتر `industries.model_family='fund'` ممیزی شد و ۴۱۹ نماد فعال صندوق شناسایی شد؛ این فیلتر از بررسی نمادهای غیرصندوق جلوگیری می‌کند.
- batch37 برای `آسان`، `آسود` و `آسود2` با ۴ سند رسمی، ۱۲ رکورد normalized و خطای صفر تکمیل شد. برچسب NAV در parser دیده شد، اما هیچ مقدار عددی معتبر `nav_per_share` یا `units_outstanding` برای promotion تولید نشد؛ هیچ importی انجام نشد.
- artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch37/` حفظ شدند.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch36

- batch36 برای `تاتمس`، `تادیکو` و `تادیکو3` تکمیل شد؛ ۱۶ سند رسمی و ۴۴ رکورد normalized ثبت شد و دو خطای parser در manifest حفظ شدند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifactها در `data-service/artifacts/fund-nav-followup-20260906-batch36/` حفظ شدند.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch35

- batch35 برای `بکهنوج`، `بگیلان` و `بگیلان3` تکمیل شد؛ ۲۱ سند رسمی و ۵۰ رکورد normalized تولید شد و یک خطای parser در manifest حفظ شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch35/` نگه‌داری شدند.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch34

- batch34 برای `بکابل`، `بکام` و `بکام3` تکمیل شد؛ ۱۵ سند رسمی و ۴۵ رکورد normalized تولید شد و یک گزارش شرکت تابعه در manifest به‌صورت gated ثبت شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch34/` حفظ شدند.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch33

- batch33 برای `بپیوند3`، `بکاب` و `بکاب3` تکمیل شد؛ `بکاب` از ۸ سند رسمی و ۳۰ رکورد normalized با خطای صفر برخوردار بود و دو نماد دیگر در بازهٔ `1405/01/01` تا `1405/06/14` `NO_NOTICES` بودند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد؛ artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch33/` حفظ شدند.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch32

- batch32 برای `بپویا`، `بپویا3` و `بپیوند` تکمیل شد؛ ۱۵ سند رسمی و ۵۰ رکورد normalized تولید شد. یک مورد `child_entity_financial_statement` برای شرکت مفتول‌سازان اورامان جدا و gated شد.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد. artifactها، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch32/` حفظ شدند.

## 2026-09-06 - پایش jobهای روزانه پس از ممیزی دوره‌ها

- journal Production تأیید کرد importer محلی Codal با `inserted=0`، `standard_facts=0` و `validation_errors=[]` موفق اجرا شده و refresh snapshot با `no_recent_evidence` خاتمه یافته است؛ این پیام نبود artifact جدید را نشان می‌دهد، نه خرابی job.
- اجرای coverage audit کامل در این نوبت به‌دلیل زمان طولانی خروجی قابل‌اتکا برنگرداند؛ آن را evidence ناقص محسوب کردم و هیچ ادعای کاهش گیت‌های coverage یا تغییر Production بر اساس آن ثبت نشد.

## 2026-09-06 - provenance duplicate-period و قرنطینه

- schema واقعی Production مشخص شد: کلید provenance سند در `disclosures.source_disclosure_id` و checksum در `disclosure_versions.content_checksum` است. برای نمونهٔ `رایا` هر دو period دقیقاً به `1570348:balance_sheet` و checksum یکسان اشاره دارند؛ fact اضافی در period نادرست از قبل `DATA_REVIEW` بود و canonical facts `VALID` هستند.
- اجرای کنترل‌شده با `--quarantine-conflicting-period-facts` انجام شد؛ ۶۸ conflict شناسایی شد، `changed=0` و `quarantined_conflicting_facts=0` چون fact معتبر اضافی باقی نمانده بود. بنابراین هیچ دادهٔ معتبر قرنطینه یا حذف نشد و گیت‌های تحلیل بدون افت حفظ شدند.

## 2026-09-06 - بررسی نمونهٔ duplicate-period

- نمونهٔ `رایا` نشان داد یک دورهٔ browser با `length_months=15` و همان عنوان رسمی دورهٔ ۳ماهه، فقط ۱ fact دارد، در حالی‌که canonical period با `length_months=3` سه fact دارد. بنابراین مشکل صرفاً نمایش نیست و ادغام facts باید با مقایسهٔ شناسهٔ اطلاعیه، نسخه و parser انجام شود.
- تلاش read-only برای مقایسهٔ tracing با نام ستونی نادرست متوقف شد؛ هیچ write یا قرنطینه‌ای انجام نشد. پیش از ادامه باید schema واقعی `disclosures` خوانده و مسیر ادغام دقیقاً بر اساس provenance طراحی شود.

## 2026-09-06 - ممیزی repair دوره‌های هم‌قابل‌مقایسه

- dry-run `repair_browser_period_lengths.py` روی Production، ۶۸ candidate را نشان داد که طول دوره‌ی ذخیره‌شده با عنوان رسمی کدال اختلاف دارد؛ اما اجرای کنترل‌شده با backup قبلی، در هر ۶۸ مورد به‌علت وجود canonical period هم‌پوشان با constraint دیتابیس مواجه شد (`conflicts=68`, `changed=0`).
- هیچ fact یا دوره‌ای تغییر نکرد. مسئله اکنون duplicate-period/ادغام دوره‌هاست و باید با قرنطینه و replay دقیق facts حل شود؛ اصلاح مستقیم بدون بررسی هم‌ارزی provenance مجاز نیست.
- backup قبل از این تلاش در Production با SHA-256=`21e6faafe47ff393f73b4c77f055741479a55f591eab96261eb3c2d37db57c92` در `/var/backups/boursnegar/20260905T192005Z-period-length-before-repair.dump` حفظ شد. یک فایل صفر بایتِ تلاش ناموفق قبلی نیز باقی است و به‌عنوان backup معتبر محسوب نمی‌شود.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch31

- batch31 برای `بوعلی`، `بوعلی3` و `بپاس` تکمیل شد؛ ۲ bundle، ۱۰ سند رسمی و ۲۸ رکورد normalized ثبت شد و normalize دو خطای صریح داشت که در manifest نگه‌داری شدند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion پیدا نشد و هیچ داده‌ای به Production وارد نشد. artifactها در `data-service/artifacts/fund-nav-followup-20260906-batch31/` حفظ شدند.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch30

- batch30 برای `بهپاک`، `بهپاک3` و `بهیر` تکمیل شد؛ `بهپاک` از یک bundle شامل ۸ سند رسمی، ۲۰ رکورد normalized و خطای صفر برخوردار بود و دو نماد دیگر در بازهٔ `1405/01/01` تا `1405/06/14` وضعیت `NO_NOTICES` داشتند.
- هیچ `nav_per_share` یا `units_outstanding` عددی معتبر برای promotion به دست نیامد. artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch30/` حفظ شدند و نتیجهٔ `NO_NOTICES` به کل تاریخ تعمیم داده نشد.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch29

- batch29 برای `بنیرو`، `بنیرو3` و `بهامرز` تکمیل شد: `بنیرو3` در بازهٔ جست‌وجو `NO_NOTICES` بود؛ دو نماد دیگر ۳۶ رکورد از ۱۱ سند رسمی تولید کردند و checksumها در manifest ثبت شد.
- normalize سه مورد `child_entity_financial_statement` را برای گزارش‌های شرکت‌های تابعه جدا نگه داشت؛ هیچ NAV یا `units_outstanding` عددی معتبر برای promotion به دست نیامد و هیچ import تولیدی انجام نشد.
- artifactهای batch در `data-service/artifacts/fund-nav-followup-20260906-batch29/` حفظ شدند؛ نتیجهٔ `NO_NOTICES` فقط محدود به بازهٔ جست‌وجو است.

## 2026-09-06 - ممیزی بک‌تست و سرویس Production

- بک‌تست read-only روی دیتابیس فعال Production اجرا شد: ۲۷۱۴ snapshot؛ افق‌های ۵ و ۱۰ جلسه به‌ترتیب ۱۸۹۲ و ۳۲ نمونهٔ قابل‌مقایسه دارند، اما افق ۲۰ جلسه فقط ۹ نمونه و همچنان `INSUFFICIENT_SAMPLE` با حداقل ۳۰ است. افزایش نمونه با حذف/پرکردن مصنوعی روزهای تعطیل انجام نشد؛ snapshotهای جدید پس از گذشت ۲۰ جلسهٔ معتبر باید این گیت را طبیعی تکمیل کنند.
- پایش عملیاتی Production تأیید کرد `boursnegar-data-service.service` فعال است و روی `127.0.0.1:8001` گوش می‌دهد؛ پورت ۸۰۰۰ در معماری فعلی پورت سرویس نیست. timerهای Codal و snapshot نیز active هستند. DNS دامنه در این بررسی resolve نشد، بنابراین دسترسی عمومی را از این خروجی ادعا نمی‌کنیم.
- اجرای ممیزی مشابه در Local به‌دلیل نبود PostgreSQL روی localhost انجام نشد؛ این محدودیت محیط ثبت شد و به‌جای آن از دادهٔ Production استفاده شد. هیچ تغییر دیتابیسی در این ممیزی انجام نشد.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch28

- batch28 برای `بمولد3`، `بمپنا` و `بمیلا` با browser fallback و Excel-only تکمیل شد: `بمولد3` در بازهٔ جست‌وجو `NO_NOTICES` بود؛ دو نماد دیگر در مجموع ۴۰ رکورد از ۱۶ سند رسمی تولید کردند.
- normalize با ۴ خطای صریح `child_entity_financial_statement` تمام شد؛ این خطاها به‌عنوان گزارش شرکت تابعه حفظ شدند و به دادهٔ شرکت اصلی تبدیل نشدند. هیچ NAV یا `units_outstanding` عددی معتبر وجود نداشت و هیچ promotion تولیدی انجام نشد.
- artifact، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch28/` نگه داشته شدند؛ provenance و گیت عدم جعل رعایت شد.

## 2026-09-06 - ادامهٔ غربالگری NAV صندوق‌ها، batch27

- batch27 برای `رابین2`، `رادان` و `رایبد` با browser fallback، Excel-only و بازهٔ `1405/01/01` تا `1405/06/14` تکمیل شد. `رابین2` با وضعیت `NO_NOTICES` ثبت شد؛ برای `رادان` و `رایبد` به‌ترتیب ۹ و ۲۰ رکورد normalized از اسناد رسمی تولید شد، خطای normalize صفر بود، و checksumهای اسناد در manifest حفظ شدند.
- در این batch هیچ `nav_per_share` یا `units_outstanding` با مقدار عددی معتبر تولید نشد؛ `parser_found_items` شامل برچسب NAV بود اما مقدار قابل‌استفاده برای promotion وجود نداشت. هیچ داده‌ای به Production وارد نشد و نتیجهٔ `NO_NOTICES` فقط به همین بازه محدود است.
- artifactهای خام، checkpoint و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch27/` نگه داشته شدند. این batch نیز گیت provenance و محدودیت «عدم جعل داده» را پاس کرد.

## 2026-09-06 - ممیزی زندهٔ پوشش، گیت ارزش‌گذاری و بک‌تست

- Production audit زنده با دیتابیس فعال اجرا شد: ۱۵۲۴ نماد فعال، ۷۲۱ `CORE_READY`، ۴۱۹ `FUND_MODEL_REQUIRED` و ۳۸۴ `MISSING_COMPARABLE_PERIODS`.
- گیت ورودی ارزش‌گذاری: ۴۶۱ نماد `pass` و ۱۰۶۳ نماد `review`. این عدد readiness ورودی‌های موجود است و به‌معنی وجود DCF/FCFE/Residual Income کامل برای همهٔ نمادها نیست.
- بک‌تست forward بر مبنای `quality_status='VALID' AND volume>0`: افق ۵ جلسه‌ای ۱۸۹۲ نمونه و افق ۱۰ جلسه‌ای ۳۲ نمونه (`READY`)؛ افق ۲۰ جلسه‌ای ۹ نمونه (`INSUFFICIENT_SAMPLE`, حداقل ۳۰). هیچ داده یا بازدهی برای پرکردن کمبود جعل نشد.
- `health` و `readyz` Production سبز، سرویس داده active و timerهای کدال و refresh فعال/enabled هستند. تست local: ۱۱۹/۱۱۹ موفق و `git diff --check` بدون خطا.
- ledger محلی برای artifactهای مرجع با ۲ manifest و ۹۲ رکورد اعلام‌شده اجرا شد: `missing_files=0` و ۱۲ فایل `VERIFIED`؛ ۵ خطای اعلام‌شدهٔ manifest حفظ و به‌عنوان دادهٔ سالم تلقی نشدند. dry-run نگاشت قطعی صنایع روی Production نیز ۴۸ صنعت و `updated=0` نشان داد؛ برای نمادهای نامشخص mapping حدسی انجام نشد.
- پایش عملیاتی Production در 2026-09-06: importer کدال با `Result=success` و `ExecMainStatus=0` اجرا شد، `inserted=0` و `standard_facts=0` گزارش کرد؛ snapshot refresh نیز `no_recent_evidence` از 2026-09-03T17:30:26Z داد. این وضعیت نبود artifact محلی جدید را نشان می‌دهد، نه نبود اطلاعیه در خود کدال. دیسک `/` با ظرفیت ۲۵G، مصرف ۱۹G و فضای آزاد ۵.۶G (۷۷٪) است.
- بازیابی محدود مرورگر برای `امین شهر` در 2026-09-06 با profile جدا انجام شد؛ capture در `data-service/artifacts/fund-nav-followup-20260906/` و normalize با ۱۴ fact و ۱۴ source document، خطای صفر، ثبت شد. سند رسمی کدال با tracingهای `1573540` و `1573834`، period-end=`1405/03/31` و NAV=`14038 IRR` دارد و checksumها در payload/manifest نگهداری شده‌اند. چون همین period قبلاً در Production promotion شده، import تکراری انجام نشد؛ تعداد واحد عدد period-end معتبر نداشت. timeout بیرونی با checkpoint/manifest ثبت شد و دادهٔ ناقص به‌عنوان نبود تاریخی تلقی نشد.
- بازیابی محدود `آبنوس` نیز capture رسمی با tracing=`1574667` و checksumدار ایجاد کرد؛ normalize با خطای صفر ۵ fact تولید کرد، اما ردیف NAV در payload به‌عنوان مورد پیدا‌شده دیده شد و مقدار عددی معتبر برای promotion تولید نکرد (در خروجی normalized فقط total_assets/total_liabilities/net_profit باقی ماند). تعداد واحد نیز عدد period-end معتبر نداشت؛ بنابراین import انجام نشد و capture در `data-service/artifacts/fund-nav-followup-20260906-abnos/` نگه داشته شد.
- مسیر `browser_codal_fetch.py` harden شد: checkpoint اکنون در ابتدای capture و پس از هر صفحه با `progress[ symbol|range ]={page,records,updated_at}` نوشته می‌شود؛ timeout یا توقف کنترل‌شده دیگر progress را تا پایان نماد معطل نمی‌کند. `py_compile` و تست‌های مرتبط ۴/۴ موفق شدند. این تغییر فقط metadata پیشرفت را ثبت می‌کند و هیچ دادهٔ مالی تولید یا جعل نمی‌کند.
- capture محدود `آتش` با Excel رسمی و checkpoint کامل انجام شد؛ normalize با خطای صفر ۳ fact معتبر برای سند حسابرسی‌شدهٔ period-end=`1405/02/31` تولید کرد (net_profit، total_assets، total_liabilities)، اما NAV و تعداد واحد عددی معتبر نداشتند. manifest/checksum در `data-service/artifacts/fund-nav-followup-20260906-atash/` حفظ شد و هیچ promotion انجام نشد.
- capture محدود `آتی1` در بازهٔ `1405/01/01` تا `1405/06/14` با پاسخ بدون اطلاعیه تمام شد؛ checkpoint با `NO_NOTICES` و خطای صفر، و فایل JSONL صفررکورد در `data-service/artifacts/fund-nav-followup-20260906-ati1/` نگهداری شد. این فقط نبود اطلاعیه در بازهٔ جست‌وجو است و به‌عنوان نبود تاریخی NAV تفسیر نشد.
- پس از hardening checkpoint، تست کامل data-service دوباره اجرا شد: `119/119` موفق، `git diff --check` بدون خطا و `py_compile` مسیر browser موفق بود.
- اسکن بدون دانلود همهٔ `normalized.jsonl`های artifact فعلی انجام شد: ۴ NAV مثبت در ۱ نماد (`امین شهر`) و ۰ fact معتبر `units_outstanding` پیدا شد. این اسکن فقط artifactهای موجود را پوشش می‌دهد و نبود داده در کدال را اثبات نمی‌کند.
- capture محدود `آرمان` با Excel رسمی در بازهٔ `1405/01/01` تا `1405/06/14` انجام شد؛ normalize با خطای صفر ۱۶ fact از ۴ سند تولید کرد، اما NAV و تعداد واحد عددی معتبر نداشت. manifest/checksum در `data-service/artifacts/fund-nav-followup-20260906-arman/` حفظ شد و promotion انجام نشد.
- capture محدود `آذرین` با Excel رسمی در همان بازه انجام شد؛ normalize با خطای صفر ۹ fact از ۳ سند تولید کرد، شامل صورت‌های مالی حسابرسی‌شدهٔ ۶ماهه تا `1405/03/31` و گزارش قبلی ۳ماهه، اما NAV و تعداد واحد عددی معتبر نداشت. manifest/checksum در `data-service/artifacts/fund-nav-followup-20260906-azarin/` حفظ شد و promotion انجام نشد.
- batch غربالگری `آرام`، `آرامش` و `آرمانی` با browser fallback و Excel-only انجام شد؛ ۲ bundle، ۶ سند، ۱۸ fact و خطای صفر ثبت شد، اما هیچ NAV یا تعداد واحد عددی معتبر به دست نیامد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch2/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `آس`، `آسا` و `آسا2` با Excel-only انجام شد؛ ۳ سند رسمی، ۹ fact و خطای صفر ثبت شد، اما هیچ NAV یا تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch3/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `آساس`، `آسال` و `آسام` با Excel-only انجام شد؛ ۵ سند رسمی، ۱۵ fact و خطای صفر ثبت شد، اما هیچ NAV یا تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch4/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `آفاق`، `آفرین` و `آلا` با Excel-only انجام شد؛ ۹ سند رسمی، ۲۷ fact و خطای صفر ثبت شد، اما هیچ NAV یا تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch5/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `آلیاژ`، `آمیتیس` و `آوا` با Excel-only انجام شد؛ ۶ سند رسمی، ۱۸ fact و خطای صفر ثبت شد، اما هیچ NAV یا تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch6/` حفظ شدند و promotion انجام نشد.
- summary تجمیعی captureهای follow-up ساخته شد: ۱۰ capture و ۱۵ نماد یکتا بررسی شده‌اند؛ مجموع NAV مثبت ۴ fact در همان ۴ نماد ثبت‌شدهٔ قبلی و مجموع `units_outstanding` مثبت صفر است. summary در `data-service/artifacts/fund-nav-followup-summary-20260906.json` قرار دارد.
- batch غربالگری `آوند4`، `آوید` و `آکام` با Excel-only انجام شد؛ ۳ سند رسمی، ۹ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch7/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `ابتکار`، `ابتکار2` و `اتوآگاه` با Excel-only انجام شد؛ ۳ سند رسمی، ۹ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch8/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `ارزش2`، `ارمغان` و `ارمغان2` در بازهٔ `1405/01/01` تا `1405/06/14` بدون سند/اطلاعیه به پایان رسید؛ checkpoint و manifest با خطای صفر و normalize صفررکورد ثبت شدند. این فقط نتیجهٔ همین بازه است و به‌عنوان نبود تاریخی NAV تفسیر نشد؛ artifact در `data-service/artifacts/fund-nav-followup-20260906-batch9/` حفظ شد.
- summary follow-up پس از batchهای اخیر به‌روزرسانی شد: ۱۳ capture، ۱۷ نماد یکتا، ۶۳ سند، ۱۵۲ fact و خطای normalize صفر؛ NAV مثبت ۴ fact و `units_outstanding` مثبت صفر باقی ماند. checksum هر ۱۳ فایل normalized بررسی شد و failure صفر بود. summary در `data-service/artifacts/fund-nav-followup-summary-20260906.json` حفظ شد.
- summary follow-up پس از batch10 به‌روزرسانی شد: ۱۴ capture، ۱۹ نماد یکتا، ۶۷ سند، ۱۶۴ fact و خطای normalize صفر؛ NAV مثبت ۴ fact و `units_outstanding` مثبت صفر باقی ماند. batch `اصیل`، `اصیل2` و `اطلس` نیز ۱۲ fact از ۴ سند تولید کرد و promotion انجام نشد.
- ممیزی محتوای normalized follow-up نشان داد ۱۵۴ رکورد دارای `parser_found_items` شامل برچسب NAV بوده‌اند، اما فقط ۴ fact NAV مثبت emit شده‌اند و ۰ رکورد تعداد واحد معتبر وجود دارد؛ بنابراین گلوگاه اصلی، مقدار عددی قابل‌استفاده/گیت مقدار است، نه فقط کشف ردیف. این تفکیک در تفسیر کمبود داده حفظ شد.
- summary follow-up به schema v2 ارتقا یافت تا checkpointهای `NO_NOTICES` نیز شمرده شوند: ۱۶ capture، ۳۴ نماد تلاش‌شده، ۳۲ نماد دارای fact normalizeشده، ۴ NAV مثبت و ۰ تعداد واحد معتبر. تفاوت «تلاش‌شده» و «دارای fact» عمداً جدا نگه داشته شد.
- batch14 یک candidate جدید و قابل‌promotion کشف کرد: `اوصتا`، NAV=`59887 IRR` برای period-end=`1404/12/29`، سند حسابرسی‌شده با tracing=`1511275`، URL رسمی Codal و checksum=`8e11aeec6ef54c53d1585abffcf36da8dcaed5705fca6adb1c185cf027940f88`. normalize با خطای صفر انجام شد؛ تا اجرای backup و promotion قفل‌شده، عمداً وارد Production نشده است.
- promotion کنترل‌شدهٔ NAV اوصتا در 2026-09-06 انجام شد: backup فشردهٔ Production در `/var/backups/boursnegar/20260905T185257Z-nav-oshta-before-import.dump` با SHA-256=`d56b166dccc6974d3c334807a9a4ede78101a2d23ca6cf2bf755524018183128` ساخته شد؛ import اول `inserted=1, standard_facts=1`، replay idempotent `inserted=0` و validation error صفر بود. API واقعی اوصتا اکنون period=`1404/12/29`، `nav_per_share=59887 IRR` و valuation input همان مقدار را نشان می‌دهد؛ health سبز است.
- batch غربالگری `اکسیژن`، `بازبیمه` و `بازده` با Excel-only انجام شد؛ ۱۰ سند رسمی، ۳۰ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch15/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `بانکو`، `بانکیا` و `بذر` با Excel-only انجام شد؛ ۴ سند رسمی، ۱۲ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch16/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `بزرگ2`، `بلد` و `بلد2` در بازهٔ `1405/01/01` تا `1405/06/14` بدون سند/اطلاعیه تمام شد؛ checkpoint و manifest با خطای صفر و normalize صفررکورد ثبت شدند. این نتیجه فقط همین بازه را پوشش می‌دهد و نبود تاریخی NAV تلقی نشد؛ artifact در `data-service/artifacts/fund-nav-followup-20260906-batch17/` حفظ شد.
- batch غربالگری `بنکر`، `بنکوداریوش` و `بهین رو` با Excel-only انجام شد؛ ۳ سند رسمی، ۹ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch18/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `تخت گاز`، `تداوم` و `تداوم4` با Excel-only انجام شد؛ ۵ سند رسمی، ۱۵ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch19/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `ترنج ثابت2`، `تصمیم` و `تصمیم2` با Excel-only انجام شد؛ ۳ سند رسمی، ۹ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch20/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `ثبات2`، `ثروت` و `ثروت ساز` با Excel-only انجام شد؛ ۲ سند رسمی، ۶ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch21/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `ثمین`، `ثنا` و `ثنا2` با Excel-only انجام شد؛ ۶ سند رسمی، ۱۸ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch22/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `خبرگان`، `خزانه ملت` و `خلیج` با Excel-only انجام شد؛ ۹ سند رسمی، ۲۷ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch23/` حفظ شدند و promotion انجام نشد.
- batch `دارا`، `دارا یکم` و `دارونو` بررسی شد؛ capture دارای ۶ سند، normalize دارای ۹ fact و ۳ خطای صریح `No tables found` برای سه فایل Excel دارا یکم بود، و NAV معتبر جدید تولید نشد. دارونو در این بازه `NO_NOTICES` بود. به‌دلیل خطاهای parser هیچ promotion انجام نشد؛ manifest/checksum در `data-service/artifacts/fund-nav-followup-20260906-batch24/` حفظ شد.
- batch25 سه NAV مربوط به `دانیک` را پیدا کرد؛ رکورد حسابرسی‌شدهٔ اصلی period-end=`1405/03/31` و NAV=`12595 IRR` با tracing=`1582208` و checksum=`d17439206a1f7624e2b7a6793e1e3562fd8747e4107eac07620ab1a0d7a878df` بود. backup قبل از promotion در `/var/backups/boursnegar/20260905T190658Z-nav-danik-before-import.dump` با SHA-256=`5ba93e494b29769e9322eafb69a4ca5326e258bd0aa444cc491962a0baaef918` ساخته شد؛ import اول `inserted=3, standard_facts=3`، replay `inserted=0` و validation error صفر. API Production اکنون period=`1405/03/31` و `nav_per_share=12595 IRR` را نشان می‌دهد؛ health سبز است.
- batch غربالگری `دریا`، `درین` و `درین2` با Excel-only انجام شد؛ ۶ سند رسمی، ۱۸ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch26/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `افق ملت`، `افق نگر` و `الماس` با Excel-only انجام شد؛ ۹ سند رسمی، ۲۷ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch12/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `امین یکم`، `انار` و `انار2` با Excel-only انجام شد؛ ۵ سند رسمی، ۱۵ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch13/` حفظ شدند و promotion انجام نشد.
- batch غربالگری `اعتبار2`، `اعتبارسهام` و `اعتماد` با Excel-only انجام شد؛ ۲ سند رسمی، ۶ fact و خطای صفر ثبت شد، اما NAV و تعداد واحد عددی معتبر پیدا نشد. artifact و manifest در `data-service/artifacts/fund-nav-followup-20260906-batch11/` حفظ شدند و promotion انجام نشد.

## 2026-09-06 - hardening parser برای NAV صندوق

- parser کدال اکنون ردیف رسمی `خالص دارایی‌های هر واحد سرمایه‌گذاری` را به fact کلیددار `nav_per_share` نگاشت می‌کند و در مسیر داده‌ی صورت وضعیت مالی قرار می‌دهد.
- روی batch14، parser این ردیف را در ۱۴ سند پیدا کرد، اما مقدار منتشرشده در اسناد بررسی‌شده صفر بود؛ normalizer آن را عمداً promotion نکرد تا NAV نامعتبر وارد ارزش‌گذاری نشود. سند، checksum و provenance حفظ شده‌اند.
- `py_compile` موفق و تست کامل local: `117/117` موفق.
- ممیزی مجدد همه batchهای موجود با parser جدید، ۱۰ رکورد NAV غیرصفر برای ۴ نماد (`آتیمس`، `آتیه ملت`، `امتیاز`، `امین شهر`) پیدا کرد؛ گزارش provenance در `artifacts/fund-nav-positive-audit.json` ثبت شد. این رکوردها هنوز قبل از backup و import کنترل‌شده به Production منتقل نشده‌اند.
- برای NAV به‌ازای واحد، واحد داخلی به `IRR` اصلاح شد؛ واحد `میلیون ریال` سند فقط برای جمع‌های صورت مالی است و نباید به قیمت هر واحد تعمیم داده شود. تلاش audit مستقیم دیتابیس local به‌دلیل نبود PostgreSQL روی `localhost:5432` اجرا نشد؛ Production همچنان از مسیر SSH قابل‌دسترسی و نگاشت هر چهار نماد در آن تأیید شده است.
- پیش از promotion، backup کامل Production با موفقیت ساخته و checksum شد: `/var/backups/boursnegar/20260905T172640Z-fund-nav-before-import.dump`، حجم ۱۵۶٬۳۳۵٬۸۸۳ بایت، SHA-256=`51bbb0372bd395ce33f932e16393f0dbfb36b326607f74c4cb254e29c5e315f1`.
- پنج رکورد NAV غیرصفر پس از انتقال checksum-دار، با advisory lock وارد Production شدند (`inserted=5`, `standard_facts=5`, خطا=۰). بازبینی DB: آتیمس ۱، آتیه ملت ۱، امتیاز ۱، امین شهر ۲ رکورد معتبر؛ `/health` نیز `status=ok` است.
- artifactهای موجود صندوق‌ها برای تعداد واحد نیز بررسی شدند؛ موارد پیدا‌شده عمدتاً متن الزامات/حدنصاب بودند، نه مقدار عددی period-end، بنابراین تعداد واحد هنوز وارد نشده است. در عوض یک backtest جدید Production با ۲۷۱۴ snapshot اجرا شد: افق ۲۰ جلسه‌ای ۹ نمونه دارد و همچنان `INSUFFICIENT_SAMPLE` (حداقل ۳۰) است؛ نتیجه در `artifacts/valuation-backtest-current.json` ثبت شد.
- پایش عملیاتی Production بررسی شد: `boursnegar-codal-financials.timer` فعال و آخرین اجرای importer موفق با `inserted=0` و خطای صفر بود؛ `boursnegar-snapshot-refresh.timer` نیز فعال است. اجرای دستی refresh با خروج موفق انجام شد و پیام `no_recent_evidence` برای بازه ۴۸ ساعت ثبت شد؛ یعنی در آن بازه اطلاعیه‌ی مالی جدید قابل refresh وجود نداشت، نه اینکه job خراب باشد.
- ممیزی فعلی ورودی‌های ارزش‌گذاری Production در `artifacts/valuation-input-gates-current.json` ذخیره شد: ۱۵۲۴ نماد، ۴۶۱ عبور و ۱۰۶۳ مورد review. این audit فقط readiness داده‌های پایه را پوشش می‌دهد؛ برای DCF/FCFE/Residual Income هنوز ورودی‌های دارای provenance در schema فعلی ثبت نشده‌اند و مدل به‌درستی عدد intrinsic صادر نمی‌کند.
- ممیزی schema نشان داد جدول `instruments` صنعت رسمی ندارد و endpoint دسته‌بندی ۳۷ نماد نامشخص نیز قبلاً 404 داده بود؛ بنابراین هیچ industry mapping حدسی اعمال نشد. در عوض برای جلوگیری از regression، تست مستقل تشخیص fact NAV اضافه شد؛ تست کامل local اکنون `118/118` موفق است.
- ممیزی مستقیم raw payloadهای Production برای چهار نماد NAV-promoted، ۵ رکورد `nav_per_share` را تأیید کرد و هیچ رکوردی با مقدار عددی تعداد واحد پیدا نشد؛ موارد قبلیِ «تعداد واحد» صرفاً متن الزامات بودند. بنابراین تعداد واحد هنوز به‌درستی gated است.
- اتصال `nav_per_share` به `valuation_inputs` در لایه API اصلاح شد؛ برای جلوگیری از مخلوط‌کردن دوره‌ها، NAV فقط وقتی مصرف می‌شود که با period، طول دوره، scope و وضعیت حسابرسی گزارش انتخاب‌شده منطبق باشد. backup قبل از deploy: `/var/backups/boursnegar/20260905T173508Z-nav-period-join/main.py.before` با SHA-256=`9ba285a375b634c7ce6fc2731427425a07569ae5b2d49f3468d2641e6ea525b9`. تست local `118/118` و Production `/readyz` موفق؛ `امین شهر` فعلاً به‌دلیل عدم تطبیق دوره همچنان NAV را مصرف نمی‌کند.
- انتخاب‌گر گزارش برای ترجیح دوره‌ی جدید صندوق deploy شد؛ با این حال smoke واقعی `امین شهر` هنوز گزارش سالانه ۱۴۰۴/۱۲/۲۹ را انتخاب کرد و NAV را مصرف نکرد. این نشان می‌دهد تشخیص `model_family` در این مسیر هنوز با انتخاب‌گر هم‌راستا نیست و باید قبل از هر promotion بعدی اصلاح شود. backup: `/var/backups/boursnegar/20260905T173555Z-fund-period-priority/main.py.before`، SHA-256=`b4fce2cb4e99eaac706589d15766c3e4e60271c9db9f2cb8e2307fc92a263498`.
- اولویت‌بندی جدید با `has_nav` نیز deploy و smoke شد؛ با وجود NAV معتبر در period سه‌ماهه ۱۴۰۵/۰۳/۳۱، API هنوز گزارش سالانه را برمی‌گزیند. backup: `/var/backups/boursnegar/20260905T173658Z-nav-has-nav-priority/main.py.before`، SHA-256=`b834c15c37f51064377df0c34ccbb43d0dea12a686e12ab6c2401d5969ebbd91`. تست local `118/118` و `/readyz` موفق؛ این mismatch انتخاب‌گر همچنان کار بازِ اصلی است.
- علت نهایی مشخص شد: smoke قبلی با `report_mode=audited` اجرا شده بود و NAV رسمی موجود برای امین شهر حسابرسی‌نشده است؛ در `latest_codal` همان API دوره ۱۴۰۵/۰۳/۳۱ و `valuation_inputs.nav_per_share=14038` را برمی‌گرداند. بنابراین رفتار audited صحیح است و mismatch ناشی از mode بوده، نه خطای انتخاب‌گر.
- smoke نهایی `/api/v2/analyze` برای `امین شهر` با `latest_codal` موفق شد: `valuationGate=READY`, method=`nav`, basis=`14038`, fair value=`11230/14038/16846` و `fundModel=NOT_APPLICABLE`. وضعیت تحلیلی به‌علت رژیم تعطیلی بازار `MARKET_CLOSURE_REGIME` و داده `PARTIAL_DATA` باقی ماند؛ این محدودیت عمداً ارزش‌گذاری رسمی NAV را حذف نکرد.
- بازیابی NAV batch15 برای `اونیکس`، `اکتان`، `اکستریم`، `اکسیژن` و `بازبیمه` انجام شد؛ ۴ گروه سند، ۳۶ رکورد normalize‌شده، ۱۶ سند و صفر خطا. NAV غیرصفر یا تعداد واحد قابل promotion در این batch وجود نداشت؛ artifacts خام و manifest حفظ شدند.
- بازیابی NAV batch16 برای `بازده`، `بانکا`، `بانکا2`، `بانکدار` و `بانکو` انجام شد؛ ۳ گروه سند، ۴۴ رکورد normalize‌شده، ۲۰ سند و صفر خطا. NAV غیرصفر یا تعداد واحد قابل promotion پیدا نشد و هیچ import عددی انجام نشد.
- بازیابی NAV batch17 برای `بانکیا`، `بذر`، `برلیان`، `برلیان2` و `بزرگ` انجام شد؛ ۳ گروه سند، ۲۵ رکورد normalize‌شده، ۱۰ سند و صفر خطا. NAV غیرصفر یا تعداد واحد معتبر پیدا نشد و هیچ import عددی انجام نشد.
- بازیابی NAV batch18 برای `بزرگ2`، `بلد`، `بلد2`، `بلوط` و `بلوط2` انجام شد؛ یک اجرای کدال بدون سند قابل دانلود نتیجه داد و normalize شامل صفر رکورد، صفر سند و صفر خطا بود. این نتیجه به‌عنوان نبود evidence در بازه ثبت شد، نه نبود تاریخی داده؛ checkpoint حفظ شد.
- مسیر FCFE مبتنی بر داده واقعی اضافه شد: parser اکنون `capital_expenditure` و `net_borrowing` را جداگانه استخراج می‌کند و API فقط در صورت وجود هر دو به‌همراه OCF هم‌دوره، FCFE را می‌سازد؛ نرخ تنزیل/رشد بدون منبع همچنان gate است. تست local `118/118` موفق. Production با backup `/var/backups/boursnegar/20260905T174322Z-fcfe-input-gate` deploy شد؛ checksum قبل از deploy برای parser=`5eb5ab58276244fbcce0848c451c8d0a395b98458580eb404cf69ba24a38595b` و main=`57b28d284ed84040e86e623b17f114f90581adadf3821bc38da040d689b2835a`. `/readyz` پس از restart `ready` است.
- smoke پس از deploy موفق بود: `امین شهر` با latest_codal مقدار NAV=14038 و `fcfe=null` (به‌دلیل نبود ورودی‌های کامل FCFE)، `فولاد` نیز HTTP 200 و بدون خطای تحلیل. هر دو timer پایش کدال و refresh snapshot `enabled/active` و `/health` برابر `ok` هستند.
- ممیزی مصرف FCFE در Production روی `فولاد` و `شوینده` انجام شد: OCF برای فولاد موجود بود، اما `capital_expenditure` و `net_borrowing` در period انتخاب‌شده وجود نداشتند؛ برای شوینده نیز هر سه ورودی کامل نبودند. بنابراین هیچ FCFE/DCF عددی تولید نشد و گیت داده صحیح باقی ماند.
- ممیزی journal روزانه Production: ingest کدال، refresh snapshot، market daily و market intraday همگی `Result=success` و `ExecMainStatus=0` هستند؛ refresh پیام `no_recent_evidence` دارد و با خطا اشتباه گرفته نمی‌شود. Data Service نیز `ready` است.
- بازیابی NAV batch19 برای `بمان`، `بنکر`، `بنکوداریوش`، `بهین رو` و `بیدار` انجام شد؛ ۳ گروه سند، ۴۹ رکورد normalize‌شده، ۲۲ سند و صفر خطا. NAV غیرصفر یا تعداد واحد معتبر پیدا نشد؛ هیچ import انجام نشد.
- بازیابی NAV batch20 برای `تابش`، `تاراز`، `تخت گاز`، `تداوم` و `تداوم4` انجام شد؛ ۳ گروه سند، ۳۶ رکورد normalize‌شده، ۱۶ سند و صفر خطا. NAV غیرصفر یا تعداد واحد معتبر پیدا نشد؛ هیچ import انجام نشد.
- بازیابی NAV batch21 برای `تدبیریکم`، `ترمه`، `ترنج ثابت`، `ترنج ثابت2` و `تصمیم` انجام شد؛ ۳ گروه سند، ۳۸ رکورد normalize‌شده، ۱۷ سند و صفر خطا. NAV غیرصفر یا تعداد واحد معتبر پیدا نشد. پس از این batch، بازیابی عمومی صورت‌های مالی برای صف صندوق‌ها بازده پایینی نشان داده و ادامه باید به اسناد تخصصی NAV/واحد یا منبع رسمی دیگر محدود شود.
- تلاش برای جمع‌آوری اسناد تخصصی صندوق `امین شهر` با `download-all-documents` و `professional-documents` به‌علت صف طولانی اسناد متوقف شد؛ checkpoint و manifest در `artifacts/fund-specialized-amin-shahr` حفظ شدند. هیچ سند یا عددی بدون تکمیل retrieval و provenance وارد نشد.
- بازیابی NAV batch23 برای `تیام`، `تیام2`، `ثابت اکسیژن`، `ثابت اکسیژن2` و `ثبات` انجام شد؛ ۳ گروه سند، ۳۹ رکورد normalize‌شده، ۱۸ سند و صفر خطا. NAV غیرصفر یا تعداد واحد معتبر پیدا نشد؛ این آخرین batch عمومی این مرحله است و ادامه باید با اسناد تخصصی NAV/واحد انجام شود.
- بازیابی NAV batch24 برای `ثبات2`، `ثروت`، `ثروت ساز`، `ثروتم` و `ثروین` با timeout کنترل‌شده انجام شد؛ ۳ گروه سند، ۳۶ رکورد normalize‌شده، ۱۶ سند و صفر خطا. NAV غیرصفر یا تعداد واحد معتبر پیدا نشد و import انجام نشد.
- بازیابی NAV batch25 برای `ثمر`، `ثمین`، `ثنا`، `ثنا2` و `ثهام` انجام شد؛ ۴ گروه سند، ۵۴ رکورد normalize‌شده، ۲۴ سند و صفر خطا. NAV غیرصفر یا تعداد واحد معتبر پیدا نشد و import انجام نشد.
- برای پوشش تعداد واحد، fact مستقل `units_outstanding` با نگاشت‌های محدود و دقیق به parser local اضافه شد؛ روی دو سند دارای متن واحدهای صادر/ابطال، ردیف عددی period-end پیدا نشد و parser آن‌ها را استخراج نکرد. تست کامل local `119/119` موفق است؛ این تغییر هنوز به Production deploy نشده تا پیش از آن روی سند عددی واقعی تأیید شود.
- migrationهای `027_valuation_inputs.sql` و rollback آن اضافه شدند تا ورودی‌های FCFF/FCFE، نرخ‌ها، NAV و تعداد واحد به issuer/period/source/checksum و quality gate متصل شوند. migration فقط schema است و تا زمان داشتن evidence معتبر هیچ seed یا مقدار مالی ایجاد نمی‌کند؛ `git diff --check` موفق است.
- schema `valuation_inputs` با همان SQL migration به‌صورت idempotent روی Production اعمال و با `information_schema` تأیید شد (`1` جدول، بدون seed). `/readyz` پس از اعمال `ready` است؛ فایل migration نیز برای تاریخچه در release source نگه داشته شد.
- پنج NAV fact معتبر موجود با همان issuer/period/source/disclosure/checksum به جدول `valuation_inputs` backfill شدند (`upserted=5`, `total=5`). این backfill seed یا مقدار جدید نیست و صرفاً provenance factهای موجود را به schema intrinsic متصل می‌کند.
- ممیزی schema Production موفق بود: ۵ رکورد `VALID`، صفر رکورد با provenance ناقص، index دوره/کلید و unique constraint فعال، و foreign keyهای issuer/period برقرار هستند.
- اجرای محدودتر `professional-documents` برای `امین شهر` نیز با وجود timeout کوتاه پاسخ نداد و متوقف شد؛ هیچ process باقی نماند و داده‌ای وارد نشد. مسیر اسناد تخصصی فعلاً نیازمند روش جمع‌آوری تعاملی/منبع رسمی جایگزین است.
- اجرای آزمایشی فقط-HTML اسناد حرفه‌ای برای `امین شهر` نیز پس از ۶۰ ثانیه بدون artifact متوقف شد؛ checkpoint/manifest در `artifacts/fund-specialized-amin-shahr-html` ساخته شد و هیچ داده‌ای وارد نشد. این مسیر باید با تعامل مرورگر/منبع رسمی جایگزین انجام شود.
- بازیابی NAV batch22 برای `تصمیم2`، `تمشک`، `توان`، `توسکا` و `تکپاد` با timeout ۹۰ ثانیه انجام شد؛ ۴ گروه سند، ۳۷ رکورد normalize‌شده، ۲۲ سند و ۴ خطای parser برای فایل‌های Excel `تمشک` که واقعاً جدول قابل‌خواندن نداشتند. NAV غیرصفر یا تعداد واحد معتبر پیدا نشد؛ خطاها در manifest حفظ شدند.
- ممیزی دوره‌های قابل‌مقایسه در Production: فقط ۲۸۷ issuer از ۲۲۹۴ issuer دارای حداقل دو تاریخ متمایز با factهای معتبر درآمد/سود در یک طول دوره هستند؛ بیشینه دوره‌های هم‌طول ۵ است. بنابراین گیت `MISSING_COMPARABLE_PERIODS` برای بخش بزرگی از universe همچنان واقعی است و با forward-fill یا ترکیب دوره‌های ناهم‌طول دور زده نمی‌شود.
- ممیزی تجمیعی Production: ۴ instrument صندوق دارای NAV معتبر غیرصفر و ۵ fact NAV هستند؛ ۴۱۹ issuer در صنعت fund قرار دارند؛ اما هیچ periodی هنوز هر سه fact OCF، capital expenditure و net borrowing معتبر را هم‌زمان ندارد (`periods_with_cash_inputs=0`). بنابراین FCFE عددی در وضعیت فعلی به‌درستی gated است.
- ممیزی میانی snapshotهای Production: وضعیت‌ها در جدول فعلی شامل `BUY=26`، `HOLD=109`، `SELL=921` و `INSUFFICIENT_DATA=7487` است. جدول snapshot فقط checksum/quality را نگه می‌دارد و روش ارزش‌گذاری را به‌صورت قابل query ذخیره نمی‌کند؛ برای ادعای پوشش روش‌ها باید از payload/API و artifactهای تحلیلی استفاده شود، نه این شمارش خام.
- smoke گروهی v2 برای هر چهار صندوق NAVدار موفق شد: `آتیمس` (NAV=1)، `آتیه ملت` (15017)، `امتیاز` (12762) و `امین شهر` (14038) همگی HTTP 200، `valuationGate=READY` و method=`nav` دارند. state تحلیلی هر چهار مورد `MARKET_CLOSURE_REGIME` است و از صدور سیگنال قطعی جلوگیری می‌کند.
- کد backtest افق ۲۰ جلسه‌ای ممیزی شد: فقط `daily_prices` با `quality_status='VALID' AND volume>0` و offset دقیق ۱۹ جلسه بعد مصرف می‌شود؛ کمبود ۹ نمونه ناشی از نبود قیمت آینده کافی است، نه حذف closure-day یا خطای forward-fill. gate `INSUFFICIENT_SAMPLE` حفظ شد.
- تست contract برای FCFE به suite اضافه شد: با ورودی‌های کامل، روش `fcfe` و provenance basis صحیح باید انتخاب شود؛ suite کامل local اکنون `119/119` موفق است.
## 2026-09-06 - بازیابی NAV صندوق‌ها batch14

- پنج صندوق (`اندوخته داریوش`، `اهرم`، `اوج`، `اوصتا`، `اوصتا2`) با workflow مرورگر محلی کدال بررسی شدند؛ ۴ گروه سند دانلود شد.
- artifactهای `artifacts/fund-nav-recovery-batch14` و `artifacts/fund-nav-normalized-batch14` تولید شدند؛ normalize شامل ۳۶ رکورد، ۱۶ سند و صفر خطاست.
- در سند رسمی `اوصتا` ردیف `خالص دارايي هاي هر واحد سرمايه گذاري` وجود دارد؛ parser فعلی هنوز آن را به `nav_per_share` نگاشت نمی‌کند. بنابراین این مورد نقص parser است، نه نبود داده، و هیچ NAV عددی بدون نگاشت/واحد معتبر وارد نشد.
- برای تعداد واحد نیز evidence قابل‌اعتماد برای promotion به دیتابیس به‌دست نیامد؛ provenance و گیت‌های داده حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch13

- پنج صندوق (`امگا`، `امین شهر`، `امین یکم`، `انار`، `انار2`) بررسی شدند؛ ۳ فایل evidence و ۳۳ رکورد normalize‌شده با خطای صفر تولید شد.
- فقط دارایی/بدهی/سود استخراج شد و NAV رسمی به‌ازای واحد یا تعداد واحد معتبر پیدا نشد؛ import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch13` و `artifacts/fund-nav-normalized-batch13` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch12

- پنج صندوق (`افق ملت`، `افق نگر`، `الماس`، `امتیاز`، `امرالد`) بررسی شدند؛ ۵ فایل evidence و ۵۱ رکورد normalize‌شده با خطای صفر تولید شد.
- فقط دارایی/بدهی/سود استخراج شد و NAV رسمی به‌ازای واحد یا تعداد واحد معتبر پیدا نشد؛ import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch12` و `artifacts/fund-nav-normalized-batch12` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch11

- پنج صندوق (`اعتبارسهام`، `اعتماد`، `اعتماد2`، `اعتماد4`، `افران`) بررسی شدند؛ ۲ فایل evidence و ۲۶ رکورد normalize‌شده با خطای صفر تولید شد.
- factهای موجود فقط دارایی/بدهی/سود بودند؛ NAV رسمی به‌ازای واحد یا تعداد واحد معتبر پیدا نشد، بنابراین import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch11` و `artifacts/fund-nav-normalized-batch11` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch10

- پنج صندوق (`اطلس`، `اطلس4`، `اطمینان`، `اعتبار`، `اعتبار2`) بررسی شدند؛ ۳ فایل evidence و ۴۱ رکورد normalize‌شده با خطای صفر تولید شد.
- فقط دارایی/بدهی/سود استخراج شد و NAV رسمی به‌ازای واحد یا تعداد واحد معتبر پیدا نشد؛ import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch10` و `artifacts/fund-nav-normalized-batch10` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch9

- پنج صندوق (`ارکیده`، `ارکیده2`، `استیل`، `اصیل`، `اصیل2`) بررسی شدند؛ ۳ فایل evidence و ۲۸ رکورد normalize‌شده با خطای صفر تولید شد.
- فقط دارایی/بدهی/سود استخراج شد و NAV رسمی به‌ازای واحد یا تعداد واحد معتبر پیدا نشد؛ import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch9` و `artifacts/fund-nav-normalized-batch9` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch8

- پنج صندوق (`ارزش`، `ارزش مسکن`، `ارزش2`، `ارمغان`، `ارمغان2`) بررسی شدند؛ ۲ فایل evidence و ۱۴ رکورد normalize‌شده با خطای صفر تولید شد.
- factهای استخراج‌شده فقط دارایی/بدهی/سود بودند و NAV رسمی به‌ازای واحد یا تعداد واحد معتبر وجود نداشت؛ import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch8` و `artifacts/fund-nav-normalized-batch8` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch7

- پنج صندوق (`آگاس`، `ابتکار`، `ابتکار2`، `اتوآگاه`، `اتوداریوش`) بررسی شدند؛ ۲ فایل evidence و ۱۸ رکورد normalize‌شده با خطای صفر تولید شد.
- فقط دارایی/بدهی/سود استخراج شد و NAV رسمی به‌ازای واحد یا تعداد واحد معتبر وجود نداشت؛ import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch7` و `artifacts/fund-nav-normalized-batch7` حفظ شدند.

## 2026-09-06 - هدف جدید، بازیابی NAV صندوق‌ها batch6

- پنج صندوق (`آوند4`، `آوید`، `آکام`، `آکورد`، `آکورد2`) بررسی شدند؛ ۲ فایل evidence و ۲۳ رکورد normalize‌شده با خطای صفر تولید شد.
- داده‌ها فقط `total_assets`، `total_liabilities` و `net_profit` بودند؛ NAV رسمی به‌ازای واحد و تعداد واحد معتبر پیدا نشد، بنابراین import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch6` و `artifacts/fund-nav-normalized-batch6` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch5

- پنج صندوق (`آمیتیس`، `آوا`، `آوان`، `آوان2`، `آوند`) بررسی شدند؛ ۴ فایل قابل‌پردازش و ۳۳ رکورد معتبر normalize شد.
- یک فایل `آوا` به‌دلیل نبود جدول با خطای parser ثبت شد. رکوردهای موفق فقط دارایی/بدهی/سود بودند و NAV رسمی یا تعداد واحد معتبر نداشتند؛ import عددی انجام نشد. artifacts در `artifacts/fund-nav-recovery-batch5` و `artifacts/fund-nav-normalized-batch5` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch4

- پنج صندوق (`آلا`، `آلا2`، `آلتون`، `آلکان`، `آلیاژ`) بررسی شدند؛ ۳ فایل evidence و ۴۱ رکورد normalize‌شده با خطای صفر تولید شد.
- فقط `total_assets`، `total_liabilities` و `net_profit` استخراج شد؛ NAV رسمی به‌ازای واحد و تعداد واحد معتبر پیدا نشد. import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch4` و `artifacts/fund-nav-normalized-batch4` حفظ شدند.

## 2026-09-06 - بازیابی NAV صندوق‌ها batch3

- پنج صندوق (`آسان`، `آسود`، `آسود2`، `آفاق`، `آفرین`) بررسی شدند؛ ۴ فایل evidence واقعی و ۴۰ رکورد normalize‌شده با خطای صفر به‌دست آمد.
- factهای موجود فقط `total_assets`، `total_liabilities` و `net_profit` بودند؛ NAV رسمی به‌ازای واحد و تعداد واحد معتبر پیدا نشد، بنابراین import عددی انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch3` و `artifacts/fund-nav-normalized-batch3` حفظ شدند.

## 2026-09-06 - هدف جدید، بازیابی NAV صندوق‌ها batch2

- هدف جدید برای تکمیل موارد باقی‌مانده ثبت شد. بازیابی مرورگری پنج صندوق (`آبنوس`، `آتش`، `آتی1`، `آتیمس`، `آتیه ملت`) با quoting صحیح انجام شد؛ ۴ فایل evidence دریافت و normalize تعداد ۴۱ رکورد معتبر با خطای صفر تولید کرد.
- factهای استخراج‌شده دارایی/بدهی/سود برای آبنوس، آتیه ملت و آتیمس هستند؛ NAV رسمی به‌ازای واحد و تعداد واحد معتبر استخراج نشد. بنابراین هیچ import عددی NAV انجام نشد و artifacts در `artifacts/fund-nav-recovery-batch2` و `artifacts/fund-nav-normalized-batch2` حفظ شدند.

## 2026-09-06 - candidate category برای نمادهای unclassified

- برای ۳۷ نماد `unclassified` endpoint زنده‌ی Production بررسی شد و همه پاسخ 404/بدون category دادند؛ بنابراین هیچ mapping حدسی یا mutation در جدول صنایع انجام نشد.
- خروجی evidence و وضعیت دریافت در `artifacts/unclassified-live-category-candidates.json` ثبت شد. این صف تا دریافت category رسمی از منبع بازار/کدال باز می‌ماند.

## 2026-09-06 - صف نگاشت صنایع نامشخص

- صف ۳۷ نماد بدون صنعت معتبر از coverage audit جدا و در `artifacts/unclassified-industry-review.csv` ذخیره شد؛ برای هر مورد نام/نماد و پوشش دوره و fact موجود است.
- این صف باید با منبع رسمی issuer/کد صنعت تکمیل شود؛ تا آن زمان موتور برای آن‌ها ارزش‌گذاری عددی صادر نمی‌کند.

## 2026-09-06 - ممیزی روش‌های فعال در snapshot

- شمارش روش‌های آخرین snapshot هر نماد در Production: `normalized_pe` برای metals=95، petrochemical=85، general=164، pharmaceutical=47، food=41، cement=37 و ceramics=7؛ `price_to_book` برای financial=118، bank=13، real_estate=26 و holding=6.
- `NO_VALUATION=894` شامل صندوق‌ها، داده‌های ناقص و گیت‌های باز است. مدل‌های intrinsic (`nav`/`fcfe`/`dcf`/`residual_income`) در کد evidence-gated هستند اما در snapshot فعلی نمونه‌ی فعال ندارند؛ این موضوع به‌عنوان نبود ورودی، نه موفقیت جعلی مدل، ثبت شد.

## 2026-09-06 - اصلاح 404 گزارش صندوق

- `_stored_financial_report` برای همه صنایع وجود `revenue` را اجباری می‌کرد و صندوق‌هایی مثل `آبنوس` را با وجود دارایی/بدهی/سود معتبر 404 می‌کردند. شرط برای خانواده `fund` اصلاح شد: دارایی و سود معتبر برای نمایش گزارش کافی است، اما NAV همچنان شرط ارزش‌گذاری عددی است.
- تست کامل data-service `117/117` موفق شد. backup پیش از rollout در `/var/backups/boursnegar/20260906T110000Z-fund-report-gate/main.py.before` با SHA-256 `3ed9d4d9259bff051c07cdc10127688b4facbbd17971446534a4c03460d6b207` ثبت شد.
- Production smoke برای `آبنوس` اکنون HTTP 200، `analysisState=FUND_MODEL_REQUIRED` و `valuationGate=REVIEW` با evidenceهای لازم NAV را برمی‌گرداند؛ دیگر 404 کاذب رخ نمی‌دهد. healthz/readyz سبز هستند.

## 2026-09-06 - اصلاح نتیجه تشخیص صندوق‌ها

- query تشخیصی قبلی به‌دلیل quoting نادرست، نبود دوره مالی برای `آبنوس` و `آرامش` را گزارش کرده بود. بررسی مستقیم صحیح نشان داد برای هر دو نماد alias فعال، دوره مالی و fact معتبر دارایی/بدهی/سود وجود دارد و رکوردهای browser نیز متصل‌اند.
- شکاف واقعی همچنان NAV رسمی به‌ازای هر واحد و تعداد واحد معتبر است؛ بنابراین فقط فعال‌سازی ارزش‌گذاری NAV gate می‌ماند و هیچ اصلاح عددی حدسی انجام نمی‌شود.

## 2026-09-06 - کنترل import evidence صندوق

- manifest normalize صندوق‌های `آبنوس` و `آرامش` با checksum به staging Production منتقل شد و importer با advisory lock اجرا شد؛ نتیجه `inserted=0`، `standard_facts=0` و خطای اعتبارسنجی صفر بود. هیچ mutation جدیدی رخ نداد.
- بررسی ۳۶ رکورد نشان داد داده‌ها فقط دارایی/بدهی/سود هستند و fact استاندارد NAV یا تعداد واحد وجود ندارد؛ بنابراین gate مدل صندوق عمداً باز نشد و evidence خام در artifacts محلی حفظ شد.

## 2026-09-06 - اصلاح gate صندوق پس از NAV معتبر

- یک باگ منطقی اصلاح شد: حتی اگر صندوق NAV رسمی معتبر داشت، `fund_model_required` همچنان true می‌ماند و تصمیم را بی‌دلیل `INSUFFICIENT_DATA` می‌کرد. اکنون پس از valuation موفق با روش `nav`، صندوق `READY` مدل خودش محسوب می‌شود؛ نبود NAV همچنان `REVIEW` است.
- تست کامل data-service `117/117` موفق شد. پیش از rollout backup در `/var/backups/boursnegar/20260906T100000Z-fund-gate-fix/snapshot_v2.py.before` با SHA-256 `d66bf5a1bfcd52ddc52d0d47594564d39441cb763daf28074bd09eaafd001a3a` ثبت شد؛ restart و `/healthz`/`/readyz` سبز هستند.

## 2026-09-06 - ممیزی evidence صندوق‌ها

- جست‌وجوی مستقیم رکوردهای واقعی Codal در Production برای NAV/ارزش خالص دارایی/ارزش هر واحد نتیجه قابل‌استفاده‌ای نداشت؛ outputهای موجود عمدتاً `monthly_activity`، `balance_sheet` و `income_statement` هستند و فقط ۳ رکورد `cash_flow` ثبت شده است.
- بنابراین مدل `fund-nav-v1.0.0` از نظر کد و gate آماده است، اما فعال‌سازی عددی صندوق‌ها تا ورود evidence رسمی NAV، ارزش پرتفوی، بدهی/وجه نقد و تعداد واحدها عمداً انجام نمی‌شود.

## 2026-09-06 - مدل NAV صندوق‌ها

- مدل اختصاصی `fund-nav-v1.0.0` اضافه شد. صندوق‌ها فقط با `official_nav_per_share` رسمی ارزش‌گذاری می‌شوند؛ در نبود NAV، EPS یا P/B fallback نمی‌گیرد و خروجی عددی `None/REVIEW` باقی می‌ماند.
- دو تست جدید برای NAV صندوق و جلوگیری از fallback اضافه شد؛ تست خانواده ارزش‌گذاری `14/14` موفق است و py_compile و diff check نیز موفق شدند.
- پیش از rollout backup کد در `/var/backups/boursnegar/20260906T090000Z-fund-nav-model/industry_valuation.py.before` با SHA-256 `b7ff53dc104c3b782ede6b4b4ccb4c041426f4b0163c7637ab22c8d34384cb95` ثبت شد. data-service restart و `/healthz` و `/readyz` سبز تأیید شدند.

## 2026-09-06 - coverage audit نهایی

- coverage audit کامل Production در `artifacts/analysis-coverage-final.json` و `artifacts/analysis-coverage-final.csv` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۲۰۳ دوره مالی، ۷۱۹۸۵ fact و ۳۸۲۰۱ fact معتبر؛ ۱٬۸۲۶٬۷۲۳ رکورد Codal متصل و ۴۵٬۰۹۴ رکورد بدون اتصال باقی است.
- طبقه‌بندی پوشش: `CORE_READY=721`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=384`. این تفکیک با صف snapshot یکی نیست و برای تصمیم‌گیری داده‌ای باید هر دو گیت حفظ شوند.
- نمادهای ETF/صندوق با ۴۱۹ مورد به مدل اختصاصی صندوق نیاز دارند؛ مدل‌های شرکتی برای آن‌ها نباید اعمال شوند. ۳۸۴ نماد نیز دوره هم‌قابل‌مقایسه کافی ندارند.

## 2026-09-06 - smoke نهایی runtime

- درخواست واقعی `POST /api/v2/analyze` برای نماد مرجع `شستا` در Production موفق بود و `valuationGate=READY` با روش `price_to_book` و شناسه تحلیل `791b26d2-91d3-4463-8aeb-490980883175` برگشت.
- این smoke همراه با health/readiness سبز است؛ با این حال هدف کلی هنوز complete نیست چون ۸۱۰ نماد فاقد evidence مالی قابل‌تحلیل و backtest افق ۲۰ جلسه‌ای فاقد نمونه آماری کافی است.

## 2026-09-06 - پایان صف refresh قابل‌تحلیل

- ممیزی پس از batch18 نشان داد تعداد نمادهای `LEGACY` دارای هم‌زمان دوره مالی و factهای معتبر `revenue` و `net_profit` برابر صفر است؛ بنابراین ادامه refresh برای ۸۱۰ نماد باقی‌مانده بدون بازیابی evidence جدید بی‌اثر و خلاف گیت provenance است.
- وضعیت snapshotها: `READY=639`، `REVIEW=84` و `LEGACY=810`. نمادهای `REVIEW` باید با علت کمبود داده نمایش داده شوند، نه با ارزش عددی ساختگی.
- backtest چندافقی و ممیزی ورودی‌ها پیش‌تر ثبت شده‌اند؛ افق ۵/۱۰ جلسه‌ای gate آماری دارد و افق ۲۰ جلسه‌ای هنوز `INSUFFICIENT_SAMPLE` است.

## 2026-09-06 - اصلاح نگاشت issuer و batch18

- ممیزی نشان داد `REVIEW ∩ LEGACY` شامل aliasهایی مانند `آبادا3` است که issuer مستقل و بدون دوره مالی دارند؛ شرط انتخاب به وجود `financial_periods` و هر دو fact معتبر `revenue`/`net_profit` در همان issuer اصلاح شد.
- batch18 با این نگاشت صحیح ۱۴ نماد را انتخاب کرد؛ هر ۱۴ مورد موفق و بدون خطا refresh شدند. فهرست و checkpoint در `artifacts/legacy-model-batch18.txt` و `artifacts/legacy-model-batch18-checkpoint.json` ثبت شدند.
- شمارش آخرین snapshotهای Production: `READY=639`، `REVIEW=84` و `LEGACY=810`. بدون backup تکراری؛ backup پایه کمپین batch10 حفظ است.

## 2026-09-06 - batch16/17 و تفکیک scope ممیزی

- batch16 از صف `PASS` ممیزی انتخاب شد و ۱۰۰ نماد با موفقیت refresh شدند، اما شمارش تغییر نکرد؛ این نمادها پیش‌تر snapshot غیرLegacy داشتند.
- تقاطع واقعی `PASS` با `LEGACY` صفر است. صف `REVIEW ∩ LEGACY` برابر ۸۱۵ بود، اما batch17 با انتخاب ۱۰۰ مورد از این صف ۰ موفق و ۱۰۰ خطای 404 داشت؛ نمونه خطا `آبادا3` است. هیچ snapshotی تغییر نکرد و checkpoint در `artifacts/legacy-model-batch17-checkpoint.json` ثبت شد.
- این نتیجه نشان داد audit گیت‌ها در سطح issuer/گزارش مالی و refresh در سطح symbol/endpoint الزاماً یک scope ندارند؛ پیش از batch بعدی باید نگاشت symbol به company/issuer و معیار وجود گزارش endpoint اصلاح شود، نه اینکه صف 404 تکرار شود.

## 2026-09-06 - اصلاح health/readiness مسیر داده

- ممیزی runtime نشان داد سرویس data-service فقط `/health` داشت، درحالی‌که استقرار و QA مسیرهای `/healthz` و `/readyz` را صدا می‌زدند و 404 می‌گرفتند. دو endpoint اضافه شد؛ `/readyz` اتصال واقعی دیتابیس را با `SELECT 1` بررسی می‌کند.
- پیش از rollout، نسخه فعلی کد در `/var/backups/boursnegar/20260906T080000Z-health-aliases/main.py.before` با SHA-256 `8de2f4044008031395f18c6efe89d2ff4409d8fa2e01a0a3a3fafa23c40ce9b8` ذخیره شد. data-service restart شد.
- پس از صبر برای startup، هر پنج smoke مسیر `/health`، `/healthz`، `/readyz` و health/ready وب با پاسخ موفق تأیید شدند. تست نحوی محلی و `git diff --check` موفق بود؛ pytest محلی به‌دلیل نبودن پکیج نصب‌شده اجرا نشد.

## 2026-09-06 - refresh batch15

- batch15 با گیت وجود هر دو fact استاندارد `revenue` و `net_profit` اجرا شد: ۱۰ نماد باقی‌مانده در این scope، هر ۱۰ موفق و بدون خطا؛ checkpoint و فهرست در `artifacts/legacy-model-batch15-checkpoint.json` و `artifacts/legacy-model-batch15.txt` ثبت شدند.
- بدون backup تکراری؛ backup پایه کمپین batch10 حفظ شد.
- شمارش آخرین snapshotهای Production: `READY=630`، `REVIEW=79` و `LEGACY=824`. این scope واجد fact استاندارد اکنون تخلیه شده و ادامه کار باید بر اساس گیت‌های واحد، OCF، سهام و دوره‌های قابل‌مقایسه اولویت‌بندی شود.

## 2026-09-06 - refresh batch14

- batch14 با گیت وجود هم‌زمان `revenue` و `net_profit` استاندارد در صورت‌های مالی اجرا شد: ۱۰۰ نماد، ۱۰۰ موفق و بدون خطا؛ checkpoint در `artifacts/legacy-model-batch14-checkpoint.json` و فهرست در `artifacts/legacy-model-batch14.txt` ثبت شد.
- backup تکراری ساخته نشد؛ backup پایه کمپین batch10 حفظ است.
- شمارش آخرین snapshotهای Production: `READY=623`، `REVIEW=76` و `LEGACY=834`.

## 2026-09-06 - batch13 و گیت صورت‌های مالی استاندارد

- معیار انتخاب refresh اصلاح شد: فقط نمادهای `LEGACY` دارای هر دو fact استاندارد `revenue` و `net_profit` در `income_statement`/`balance_sheet` انتخاب شدند. batch13 با ۱۰۰ نماد اجرا شد و هر ۱۰۰ مورد موفق بود؛ checkpoint در `artifacts/legacy-model-batch13-checkpoint.json` و فهرست در `artifacts/legacy-model-batch13.txt` ثبت شد.
- هیچ backup تکراری ساخته نشد؛ rollback پایه کمپین `/var/backups/boursnegar/20260906T060000Z-legacy-refresh10/before.dump` باقی است.
- شمارش آخرین snapshotهای Production: `READY=543`، `REVIEW=56` و `LEGACY=934`. این نتیجه تأیید می‌کند گیت revenue+net_profit نرخ refresh را از batchهای قبلی به ۱۰۰٪ رساند.

## 2026-09-06 - refresh batch12 با فیلتر گزارش خام

- batch12 فقط از نمادهای `LEGACY` دارای رکورد در `codalpy_records` انتخاب شد: ۱۰۰ نماد، ۷ موفق و ۹۳ خطای مستند؛ فهرست و checkpoint در `artifacts/legacy-model-batch12.txt` و `artifacts/legacy-model-batch12-checkpoint.json` ثبت شدند.
- هیچ backup تکراری ساخته نشد و rollback پایه کمپین همچنان `/var/backups/boursnegar/20260906T060000Z-legacy-refresh10/before.dump` است.
- شمارش آخرین snapshotهای Production: `READY=455`، `REVIEW=44` و `LEGACY=1034`. فیلتر گزارش خام نرخ موفقیت را اندکی بهتر کرد، اما نشان داد صرف وجود رکورد خام برای refresh تحلیلی کافی نیست و گیت‌های parser/period/unit همچنان تعیین‌کننده‌اند.

## 2026-09-06 - batch11 و اصلاح معیار انتخاب refresh

- batch11 با استفاده از backup پایه batch10 و بدون dump تکراری اجرا شد: ۱۰۰ نماد، ۰ موفق و ۱۰۰ خطای `404` با پیام نبود گزارش واردشده؛ checkpoint در `artifacts/legacy-model-batch11-checkpoint.json` ثبت شد و هیچ snapshotی تغییر نکرد.
- backup پایه کمپین همچنان `/var/backups/boursnegar/20260906T060000Z-legacy-refresh10/before.dump` است. backup ناقص batch11 حذف شد.
- نتیجه ممیزی: انتخاب صرفاً بر اساس `LEGACY` برای نمادهای فاقد گزارش داخلی، refresh بی‌اثر ایجاد می‌کند. batchهای بعدی باید با وجود هم‌زمان گزارش/فکت مالی خام محدود شوند تا سهمیه و زمان صرف 404های قابل‌پیش‌بینی نشود.

## 2026-09-06 - refresh batch10 و پاکسازی پردازش‌های orphan

- batch دهم با انتخاب پویا از نمادهای `LEGACY` اجرا شد: ۱۰۰ نماد، ۴ موفق و ۹۶ خطای مستند؛ فهرست و checkpoint در `artifacts/legacy-model-batch10.txt` و `artifacts/legacy-model-batch10-checkpoint.json` ثبت شدند.
- backup معتبر پیش از mutation در `/var/backups/boursnegar/20260906T060000Z-legacy-refresh10/before.dump` با حجم حدود ۱۶MB ایجاد شد. فایل صفر بایتی اولیه حذف و جایگزین شد.
- چند `pg_dump` قدیمیِ orphan شده از batchهای قبلی متوقف شدند؛ پردازش‌های مربوط به batch10 حفظ شدند. load سرور از حدود ۸ به حدود ۵.۷ کاهش یافت و مصرف دیسک حدود ۷۶٪ است.
- شمارش آخرین snapshotهای Production: `READY=453`، `REVIEW=39` و `LEGACY=1041`. خطاهای refresh همچنان صریح و بدون درج داده حدسی باقی مانده‌اند.

## 2026-09-06 - ادامه refresh مرحله‌ای گیت ارزش‌گذاری

- batch نهم refresh نمادهای `LEGACY` اجرا شد: ۱۰۰ نماد، ۷ موفق و ۹۳ خطای مستند در `artifacts/legacy-model-batch9-checkpoint.json`. فهرست واقعی نمادها در `artifacts/legacy-model-batch9.txt` نگهداری شده است.
- backup PostgreSQL پیش از mutation در `/var/backups/boursnegar/20260906T050000Z-legacy-refresh9/before.dump` با حجم حدود ۱۶MB ثبت شد.
- شمارش آخرین snapshotهای Production پس از batch: `READY=453`، `REVIEW=35` و `LEGACY=1045`. گیت‌ها همچنان فقط با داده و provenance معتبر فعال می‌شوند؛ ۹۳ خطای batch به‌عنوان کمبود/خطای واقعی باقی مانده‌اند.

## 2026-09-05 - انتشار سیاست محدوده‌های بنیادی و سناریوهای P/E

- مدل‌های `normalized_pe` اکنون سناریوهای شفاف P/E=4 برای کف محافظه‌کارانه و P/E=8 برای سقف خوش‌بینانه دارند؛ ضریب پایه هر خانواده همچنان به‌عنوان سناریوی داخلی نمایش داده می‌شود و این اعداد ادعای اجماع بازار یا ارزش ذاتی قطعی نیستند.
- محدوده‌های خرید و فروش در screener فقط از ارزش‌گذاری بنیادی مشتق می‌شوند: خرید تا `80%` ارزش پایه و فروش از `115%` ارزش بالای سناریو؛ MA20/MA50/ATR فقط برای وضعیت تکنیکال و فیلترها باقی مانده‌اند و محدوده بنیادی را جابه‌جا نمی‌کنند. `zone_basis=VALUATION_ONLY` است.
- قبل از انتشار backup PostgreSQL در `/var/backups/boursnegar/20260905T110000Z-valuation-zones/before.dump` با SHA-256 `14c8cb638c5aa3a09c2d07c91cf214a3066311466ceace06644aecf7f8c10dcb` ثبت شد. release وب canonical اکنون `/var/www/boursnegar-releases/20260905T110000Z-valuation-zones` است و data-service از همان مسیر استاندارد فعال است.
- پس از rollout: data-service و PM2 فعال، `/healthz` و `/readyz` سبز، دیسک Production حدود `66.32%` مصرف دارد. endpoint شوینده مدل `petrochemical-v1.0.0`، مبنای EPS بازار `1772`، ضریب `6.5`، fair value پایه `11518` و وضعیت `INSUFFICIENT_DATA`/`MARKET_CLOSURE_REGIME` را برمی‌گرداند.
- ممیزی مدل‌ها نشان داد ۱۳ خانواده مدل وجود دارد، اما `general` fallback و `unclassified` بدون مدل معتبر هستند؛ بانک/مالی/هلدینگ هنوز به‌ترتیب به مدل‌های P/B/NAV مبتنی بر داده معتبر نیاز دارند. پیاده‌سازی DCF/FCFE/NAV اختصاصی برای هر صنعت بدون OCF، NAV، دوره و واحد قابل تطبیق، عمداً gate شده و نباید با عدد ساختگی تکمیل شود.
- تست‌های این مرحله: data-service `112/112`، وب `75/75`، typecheck و build Production موفق. گیت QA مرورگر احراز هویت‌شده همچنان فقط با نشست واقعی مجاز قابل PASS است.
- در ادامه، سناریوهای P/B نیز مانند P/E به بازه سیاستی ۴ تا ۸ مجهز شدند؛ تست واحد اختصاصی بانک این قرارداد را تأیید می‌کند. backup جدید پیش از تغییر در `/var/backups/boursnegar/20260905T120000Z-pb-scenarios/before.dump` ساخته شد و data-service با health سبز restart شد. snapshotهای قبلی بدون refresh مجدد عمداً بازنویسی نشدند.
- مدل‌های intrinsic gate‌شده اضافه شدند: `nav` با `official_nav_per_share` برای هلدینگ/املاک، `residual_income` با حقوق صاحبان سهام/سود/هزینه سرمایه/رشد پایدار برای بانک و مالی، و `fcfe` با FCFE/هزینه سرمایه/رشد پایدار برای ورودی‌های کامل. تست‌ها `114/114` و rollout data-service پس از restart و health موفق است.
- نماد مرجع ممیزی‌شده برای هر خانواده در Production: bank=دی، cement=اردستان، ceramics=کترام، financial=آرمان، food=آردینه، fund=آبنوس، general=آبین، holding=شستا، metals=آلومینا، petrochemical=آبادا، pharmaceutical=برکت، real_estate=ثاخت، unclassified=آ س پ. این انتخاب صرفاً نمونه پوشش مدل است و توصیه سرمایه‌گذاری نیست.
- اولین refresh مرجع چهار خطای واقعی آشکار کرد: تغییر P/B با ضریب پایه قدیمی ترتیب ارزش‌ها را می‌شکست و برای آرمان/شستا/ثاخت 500 می‌داد؛ ضریب پایه P/B اکنون در بازه ۴ تا ۸ clamp می‌شود. پس از اصلاح، refresh مجدد آرمان، شستا و ثاخت با HTTP 200 موفق شد؛ آبنوس با HTTP 404 و پیام نبود گزارش واردشده باقی ماند. checkpointها در `artifacts/model-reference-checkpoint.json` و `artifacts/model-reference-retry-checkpoint.json` حفظ شده‌اند.
- ابزار `data-service/scripts/backtest_valuation_models.py` اضافه و روی Production اجرا شد. روش آن forward-20-valid-sessions با گیت `quality_status='VALID' AND volume>0` است. گزارش `artifacts/valuation-backtest-20260905.json` شامل ۲۷۱۳ snapshot، فقط ۵ مورد قابل‌مقایسه و ۲۷۰۸ مورد فاقد افق ۲۰ جلسه‌ای است؛ میانگین فاصله ارزش پایه تا قیمت ورود `-40.93%` و بازده آینده `6.86%` است. این نمونه برای نتیجه‌گیری آماری کافی نیست و به‌عنوان محدودیت، نه موفقیت مدل، ثبت می‌شود.
- ممیزی evidence-gate با `data-service/scripts/audit_valuation_input_gates.py` روی کل `۱۵۲۴` نماد اجرا شد. گیت‌های تعداد سهام معتبر، OCF، حقوق صاحبان سهام مثبت، سود مثبت دو دوره و واحد مالی بررسی شدند؛ نتیجه فعلی `PASS=0` و `REVIEW=1524` است. این نتیجه نشان می‌دهد داده‌های واردشده هنوز برای ادعای ارزش ذاتی کامل کافی نیستند؛ خروجی خام در `artifacts/valuation-input-gates-20260905.json` حفظ شده است. شواهد سود تقسیمی و افزایش سرمایه نیز جداگانه شمارش شده‌اند و جایگزین گیت‌های بنیادی نشده‌اند.
- تفکیک گیت‌ها نشان داد کمبودها یکسان نیستند: سهام معتبر ۱۴۳۹ نماد، OCF معتبر ۱۴۹، حقوق صاحبان سهام مثبت ۲۷۱، سود مثبت دو دوره ۸۳ و واحد معتبر ۱۰۲ نماد است. در جدول `corporate_actions` فعلاً ۵۹ اقدام از نوع `capital_increase_registered` وجود دارد و هیچ رکورد سود تقسیمی ثبت نشده؛ بنابراین گیت سود تقسیمی هنوز قابل PASS نیست و به معنی نبود سود تقسیمی در واقعیت بازار نیست.
- برای بازیابی هدفمند، Chrome محلی سه نماد دی، آرمان و شستا را از کدال گرفت؛ normalize تعداد ۳۲ fact معتبر با ۳ OCF و واحد `IRR_million` تولید کرد و ۵ خطای دی را به‌دلیل شرکت تابعه بودن سند رد کرد. پس از manifest/checksum و backup `/var/backups/boursnegar/20260905T140000Z-reference-codal-import/before.dump`، import Production با `inserted=3` و `validation_errors=0` انجام شد و refresh مجدد هر سه نماد HTTP 200 بود. با این حال گیت کلی هنوز `PASS=0` است چون factهای جدید با دوره منتخب کامل تحلیل هم‌دوره نشده‌اند؛ خروجی‌های `artifacts/reference-recheck.json` و `artifacts/valuation-input-gates-after-reference.json` حفظ شدند.
- انتخاب گزارش اصلاح شد تا factهای درآمدی و ترازنامه‌ای از اطلاعیه‌های جدا، فقط در صورت تطابق دقیق دوره، طول دوره، دامنه و حسابرسی، کنار هم قرار گیرند؛ provenance هر fact و tracing جدا باقی می‌ماند. backup قبل از انتشار در `/var/backups/boursnegar/20260905T150000Z-period-merge/before.dump` ساخته شد، data-service health سبز دارد و refresh checkpointed آرمان و شستا هر دو HTTP 200 شدند.
- ممیزی گیت نیز با همین period-merge هم‌راستا شد؛ در اجرای Production، `PASS=461` و `REVIEW=1063` از ۱۵۲۴ نماد به‌دست آمد. آرمان و شستا هر پنج گیت سهام، OCF، equity، سود مثبت دو دوره و واحد را PASS کردند؛ دی فقط گیت سهام را PASS کرد. گزارش کامل در `artifacts/valuation-input-gates-final-audit.json` ثبت شد.
- ممیزی سود تقسیمی اصلاح شد تا علاوه بر `corporate_actions`، عنوان اطلاعیه‌های `تقسیم سود` و `تصمیمات مجمع` در `disclosures` را هم بشمارد. اجرای Production اکنون ۴۹۲ نماد دارای شواهد سود تقسیمی/مجمع و ۴۹ نماد دارای اقدام افزایش سرمایه نشان می‌دهد؛ گیت اصلی ارزش‌گذاری همچنان فقط بر factهای مالی معتبر تکیه دارد. گزارش `artifacts/valuation-input-gates-dividend-audit.json` حفظ شد.
- ممیزی runtime نشان داد از آخرین snapshot هر instrument، ۱۵۳۱ مورد هنوز `valuationGate=LEGACY`، فقط ۱ مورد `REVIEW` و ۱ مورد `READY` هستند؛ با این حال ۴۷۳ snapshot مدل `normalized_pe` و ۱۶۴ snapshot مدل `price_to_book` دارند. این اختلاف ناشی از refresh نشدن snapshotهای قدیمی است، نه نبود مدل؛ refresh مرحله‌ای باید برای یکدست‌سازی persisted UI ادامه یابد.
- اولین batch refresh مرحله‌ای برای ۱۰۰ نماد legacy شرکت‌محور اجرا شد: ۶۶ موفق و ۳۴ خطای مستند در checkpoint `artifacts/legacy-model-batch-checkpoint.json`. backup قبل از mutation در `/var/backups/boursnegar/20260905T210000Z-legacy-refresh/before.dump` ساخته شد. پس از batch، وضعیت آخرین snapshotها `READY=65`، `REVIEW=3` و `LEGACY=1465` است؛ این batch پوشش گیت جدید را از ۲ به ۶۸ رساند.
- batch دوم refresh legacy نیز اجرا شد: ۱۰۰ نماد، ۶۵ موفق و ۳۵ خطای مستند در `artifacts/legacy-model-batch2-checkpoint.json`. backup قبل از mutation در `/var/backups/boursnegar/20260905T220000Z-legacy-refresh2/before.dump` ثبت شد. شمارش آخرین snapshotها پس از batch `READY=124`، `REVIEW=9` و `LEGACY=1400` است.
- batch سوم refresh legacy اجرا شد: ۱۰۰ نماد، ۶۴ موفق و ۳۶ خطای مستند در `artifacts/legacy-model-batch3-checkpoint.json`. backup قبل از mutation در `/var/backups/boursnegar/20260905T230000Z-legacy-refresh3/before.dump` ثبت شد. شمارش آخرین snapshotها `READY=183`، `REVIEW=14` و `LEGACY=1336` است؛ مجموع snapshotهای دارای گیت جدید به ۲۴۱ رسید.
- batch چهارم refresh legacy اجرا شد: ۱۰۰ نماد، ۶۱ موفق و ۳۹ خطای مستند در `artifacts/legacy-model-batch4-checkpoint.json`. backup قبل از mutation در `/var/backups/boursnegar/20260906T000000Z-legacy-refresh4/before.dump` ثبت شد. شمارش آخرین snapshotها `READY=241`، `REVIEW=17` و `LEGACY=1275` است؛ مجموع snapshotهای دارای گیت جدید به ۲۵۸ رسید.
- batch پنجم refresh legacy اجرا شد: ۱۰۰ نماد، ۶۰ موفق و ۴۰ خطای مستند در `artifacts/legacy-model-batch5-checkpoint.json`. backup قبل از mutation در `/var/backups/boursnegar/20260906T010000Z-legacy-refresh5/before.dump` ثبت شد. شمارش آخرین snapshotها `READY=296`، `REVIEW=22` و `LEGACY=1215` است؛ مجموع snapshotهای دارای گیت جدید به ۳۱۸ رسید.
- batch ششم refresh legacy اجرا شد: ۱۰۰ نماد، ۶۹ موفق و ۳۱ خطای مستند در `artifacts/legacy-model-batch6-checkpoint.json`. backup قبل از mutation در `/var/backups/boursnegar/20260906T020000Z-legacy-refresh6/before.dump` ثبت شد. شمارش آخرین snapshotها `READY=360`، `REVIEW=27` و `LEGACY=1146` است؛ مجموع snapshotهای دارای گیت جدید به ۳۸۷ رسید.
- batch هفتم refresh legacy شامل ۷۶ نماد باقی‌مانده از محدوده انتخابی بود: ۴۷ موفق و ۲۹ خطای مستند در `artifacts/legacy-model-batch7-checkpoint.json`. backup قبل از mutation در `/var/backups/boursnegar/20260906T030000Z-legacy-refresh7/before.dump` ثبت شد. شمارش آخرین snapshotها `READY=403`، `REVIEW=31` و `LEGACY=1099` است؛ مجموع snapshotهای دارای گیت جدید به ۴۳۴ رسید.
- انتخاب اولیه batch هشتم با offset ثابت خالی شد و هیچ mutation نکرد؛ سپس scope بر اساس وضعیت لحظه‌ای بازسازی شد و ۱۰۰ نماد پردازش شدند: ۴۷ موفق و ۵۳ خطای مستند در `artifacts/legacy-model-batch8-checkpoint.json`. backup batch در `/var/backups/boursnegar/20260906T040000Z-legacy-refresh8/before.dump` ثبت شد. شمارش آخرین snapshotها `READY=446`، `REVIEW=35` و `LEGACY=1052` است.
- backtest پس از refreshهای مرجع دوباره اجرا شد؛ هنوز ۲۷۱۳ snapshot و فقط ۵ افق ۲۰جلسه‌ای قابل‌مقایسه وجود دارد، با میانگین فاصله ارزش پایه `-40.93%` و بازده آینده `6.80%`. تغییر جزئی نسبت به اجرای قبلی ناشی از داده‌های تازه است، اما نمونه همچنان برای نتیجه‌گیری آماری کافی نیست. خروجی جدید در `artifacts/valuation-backtest-latest.json` ثبت شد.
- مسیر DCF/FCFF نیز به‌صورت evidence-gated اضافه شد: فقط با FCFF به‌ازای سهم، WACC و رشد پایدار معتبر فعال می‌شود؛ برای شرکت‌های فاقد این ورودی‌ها خروجی قبلی تغییر نمی‌کند. تست‌ها `115/115` موفق شدند و قبل از rollout backup `/var/backups/boursnegar/20260905T160000Z-dcf-model/before.dump` ساخته شد؛ data-service پس از انتشار health سبز دارد.
- گیت واحد از ممیزی به موتور تحلیل منتقل شد: وقتی `financial_metrics_units` حاضر باشد، P/B بدون واحد شناخته‌شده equity و P/E بدون واحد شناخته‌شده EPS محاسبه نمی‌شود. backup انتشار در `/var/backups/boursnegar/20260905T170000Z-unit-gate/before.dump` ساخته شد؛ پس از rollout health سبز بود. smoke معتبر آرمان HTTP 200 با valuation و دی HTTP 200 بدون valuation/با missing OCF و EPS بود.
- payload تحلیل اکنون `valuationGate` دارد و وضعیت `READY/REVIEW`، روش مدل و علت نبود ارزش‌گذاری عددی را صریح به UI/API می‌دهد. backup انتشار در `/var/backups/boursnegar/20260905T180000Z-valuation-gate/before.dump` ساخته شد و data-service پس از rollout health سبز دارد؛ تست data-service `115/115` موفق است.
- فرانت گزارش تحلیل اکنون `valuationGate=REVIEW` را با پیام قابل‌مشاهده نشان می‌دهد. build Production موفق شد و release canonical وب به `/var/www/boursnegar-releases/20260905T190000Z-valuation-gate-ui` منتقل شد؛ backup پیش از rollout در `/var/backups/boursnegar/20260905T190000Z-valuation-gate-ui/web-before.tar.gz` با SHA-256 `99a0af587d8945fa2e4b9d16311a47edd91f5e49bfef3d1f174d0d28969f3217` ثبت است. PM2، healthz، readyz و صفحه اصلی HTTP 200 تأیید شدند.
- endpoint صفحه نماد نیز فیلدهای `valuation_gate_status` و `valuation_gate_reason` را از snapshot ذخیره‌شده برمی‌گرداند تا گیت در مسیر persisted UI هم قابل ممیزی باشد. release وب جدید `/var/www/boursnegar-releases/20260905T200000Z-valuation-gate-api` فعال شد؛ backup در `/var/backups/boursnegar/20260905T200000Z-valuation-gate-api/web-before.tar.gz` با SHA-256 `526fec6a3ffc1fbcc5b043e5878689c627cf262b0d3528da0336486f20566626` ثبت و PM2/healthz/readyz تأیید شدند.
- smoke اولیه null بودن گیت را به snapshot قدیمی نسبت داد؛ refresh کنترل‌شده آرمان با checkpoint `artifacts/gate-refresh.json` انجام شد و endpoint عمومی `/api/stocks/آرمان` اکنون `valuation_gate_status=READY` و `decision=INSUFFICIENT_DATA` (به‌دلیل گیت‌های دیگر مثل توقف بازار) برمی‌گرداند. این تفکیک نشان می‌دهد READY بودن valuation به‌تنهایی تصمیم قطعی نیست.
- runtime نهایی endpoint تحلیل تأیید کرد: آرمان HTTP 200 با `valuationGate=READY` و مدل P/B دارد اما به‌دلیل رژیم توقف `INSUFFICIENT_DATA` است؛ دی HTTP 200 با `valuationGate=REVIEW` و بدون ارزش‌گذاری عددی به‌دلیل واحد/ورودی نامعتبر دارد. release canonical وب همان `20260905T200000Z-valuation-gate-api` است و data-service، healthz و readyz سبز هستند.
- backtest از تک‌افق ۲۰ جلسه‌ای به افق‌های ۵/۱۰/۲۰ جلسه‌ای گسترش یافت. اجرای Production: افق ۵ دارای ۱۸۹۲ مشاهده (P/E=1685، P/B=207)، افق ۱۰ دارای ۳۲ مشاهده (P/E=27، P/B=5)، و افق ۲۰ دارای ۵ مشاهده (همگی P/E) است. گزارش `artifacts/valuation-backtest-multihorizon.json` ذخیره شد؛ بازده‌ها توصیفی‌اند و به‌علت تفاوت اندازه نمونه، نتیجه‌گیری آماری قطعی نیست.
- برای جلوگیری از تفسیر بیش‌ازحد، گیت آماری backtest اضافه شد: حداقل ۳۰ مشاهده برای هر افق لازم است. گزارش `artifacts/valuation-backtest-gated.json` افق‌های ۵ و ۱۰ را `READY` و افق ۲۰ را با ۵ مشاهده `INSUFFICIENT_SAMPLE` علامت‌گذاری می‌کند.
- خلاصه PASS به تفکیک خانواده از audit معتبر: bank `7/23`، cement `24/70`، ceramics `4/14`، financial `85/170`، food `28/73`، fund `0/419`، general `116/281`، holding `7/14`، metals `71/158`، petrochemical `52/140`، pharmaceutical `32/77`، real_estate `18/43` و unclassified `17/42`. صندوق‌ها طبق طراحی مدل NAV مستقل می‌خواهند و unclassified نباید ارزش‌گذاری عددی بگیرد.
- audit سراسری coverage دوباره اجرا شد و با وجود زمان اجرای طولانی، artifactهای `artifacts/analysis-coverage-final.json` و `artifacts/analysis-coverage-symbols-final.csv` تولید شدند: ۱۵۲۴ instrument فعال، ۱۸۲۰۳ دوره مالی، ۷۱۹۸۵ fact خام، ۳۸۲۰۱ fact معتبر و ۴۹۴۲۹۷ قیمت معتبر. آخرین تصمیم‌ها `INSUFFICIENT_DATA=1418`، `SELL=101` و `HOLD=5` هستند؛ هیچ نماد BUY در این snapshot صادر نشده است. این آمار وضعیت فعلی است و جایگزین بررسی provenance نمادبه‌نماد نیست.
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

## بازاجرای جمع‌بندی جامع و ممیزی نهایی - 2026-08-30

- حافظهٔ ثبت‌شده، پروتکل پروژه، اسناد وضعیت، Git، تست‌های اخیر و وضعیت Release/health دوباره تطبیق داده شدند. فایل‌های حافظهٔ خام گفتگو در workspace به‌صورت مستقل وجود ندارند؛ این جمع‌بندی بر مبنای حافظهٔ ثبت‌شده، rollout noteها، اسناد پروژه و ممیزی زنده است.
- آخرین ممیزی ثبت‌شده نشان می‌دهد هر ۵۰ نماد نمای اصلی به پوشش ۱۰۰٪ رسیده‌اند؛ ددانا با بازیابی گزارش رسمی ۱۴۰۴/۰۹/۳۰ تکمیل شد و لینک واقعی Codal نیز دارد. صفحه اصلی اکنون وضعیت اقدام قابل‌فهم، مبنای محدوده‌های خرید/فروش، بنیاد، روند، هم‌صنعت، تاریخچه، جریان نقد، هشدار و lineage اطلاعیه را نمایش می‌دهد.
- Production در ممیزی اخیر سالم بود: وب و data-service health/ready سبز، دسترسی alerts نیازمند احراز هویت، importها checksum-validated و replay آن‌ها idempotent است. Releaseهای فعالِ ممیزی جاری وب `/var/www/boursnegar-releases/20260830T050000Z-account-admin-polish` و داده `/var/www/boursnegar-data-releases/20260829T140000Z-ratio-quality` هستند؛ PM2 آنلاین است و backupهای timestamped قبل از rolloutها حفظ شده‌اند.
- کیفیت داده همچنان evidence-first است: دادهٔ ناقص یا نسبت مشکوک حذف یا جعل نمی‌شود؛ در تحلیل کنار گذاشته و با `INSUFFICIENT_DATA`/`DATA_REVIEW`/`ratio_anomalies` شفاف می‌شود. محدوده‌ها valuation/trend evidence-backed هستند و توصیهٔ قطعی سرمایه‌گذاری محسوب نمی‌شوند.
- اعتبارسنجی ثبت‌شده: ۸۲ تست data-service، ۷۲ تست وب، lint/typecheck/build و `project-memory-check.sh` موفق؛ audit سراسری قبلی نیز ۶۹۵ ردیف اسکرینر را بدون ROE/P-E نامعقول ثبت کرده است. تغییرات فعلی frontend/data در worktree هنوز uncommitted هستند و نباید بدون بازبینی کاربر commit یا rollback شوند.

### گیت‌های واقعی باقی‌مانده

1. E2E واقعی مدیریت دیدگاه و پاداش با نشست moderator مجاز هنوز اجرا نشده؛ بدون هویت و نشست واقعی نباید شبیه‌سازی شود.
2. اجرای اسکریپت جامع remote final gate در ممیزی اخیر به درخواست خارجی timeout شد؛ health و کنترل‌های مستقل موفق‌اند، اما timeout را PASS کامل تلقی نکن.
3. برای releaseهای بعدی، QA تعاملی frontend با مرورگر متصل در viewportهای 1440، 768 و 375، شامل focus و overflow جدول، هنوز باید با شواهد تصویری انجام شود.
4. هر recovery دادهٔ جدید باید local-browser/Codal، manifest/checksum، backup، advisory lock، replay idempotent و audit پس از refresh داشته باشد؛ عددسازی برای پوشش یا تصمیم ممنوع است.
- تصمیم‌های صفحه اصلی: ۶ `SELL`، یک `HOLD` و ۴۳ `INSUFFICIENT_DATA`. در ۴۳ مورد، واگرایی بازار/بنیاد یا نبود cash-flow هم‌دوره مانع نتیجه قطعی است؛ این رفتار مورد انتظار سیاست evidence-only است.
- تست‌ها پس از اصلاح: data-service تعداد ۸۱ و web تعداد ۶۴ موفق؛ build وب موفق؛ `project-memory-check.sh` و `git diff --check` موفق و worktree clean است. رندر زنده قبلی desktop/mobile بدون console error و overflow ثبت شده و تغییر فعلی فقط سرویس داده است.

## محدوده ترکیبی ارزش‌گذاری و روند - 2026-08-30

- screener اکنون علاوه بر محدوده بنیادی، ATR ساده‌شده از دامنه high-low بیست روز اخیر را محاسبه می‌کند. در روند صعودی، `buy_zone_high` از کمینه حاشیه امن ارزش‌گذاری و حمایت `MA20-ATR20` و `sell_zone_low` از بیشینه سناریوی فروش و `MA20+ATR20` ساخته می‌شود؛ در نبود روند کافی، مبنای ارزش‌گذاری حفظ می‌شود.
- API فیلدهای `valuation_buy_zone_high`، `valuation_sell_zone_low` و `zone_basis` را نیز نگه می‌دارد تا عدد ترکیبی قابل audit باشد. UI صفحه اصلی عنوان و tooltip فارسی دارد و برداشت سریع صریحاً ترکیب ارزش‌گذاری و حمایت روند را توضیح می‌دهد.
- build وب در release فعال با backup `/var/backups/boursnegar/20260830T170000Z-combined-zones-before-dist.tgz` rollout شد. health/ready هر دو سبز و پاسخ زنده screener دارای `zone_basis` و محدوده‌های جدید است؛ صفحه اصلی HTML زنده نیز عنوان جدید را برمی‌گرداند.
- تست وب: ۶۴ تست، typecheck و build موفق. این تغییر محدوده‌های هشدار SMS را عمداً تغییر نمی‌دهد؛ worker همچنان از snapshot ارزش‌گذاری معتبر، opt-in و deduplication استفاده می‌کند.

## یادداشت برتری آخرین ممیزی - 2026-08-30T12:42:23Z

یادداشت‌های قدیمی‌تر همین فایل، از جمله اعداد ۴۳ مورد `INSUFFICIENT_DATA` و coverageهای ناقص، مربوط به قبل از recovery نهایی هستند. برای وضعیت جاری، آخرین ممیزی ثبت‌شده در حافظه مرجع است: هر ۵۰ نماد نمای اصلی coverage=100٪ دارند و ددانا نیز با گزارش رسمی ۱۴۰۴/۰۹/۳۰ تکمیل شده است. گیت‌های باقی‌مانده فقط E2E احراز هویت‌شدهٔ moderator/reward، اجرای مجدد remote final gate پس از timeout خارجی، و QA تعاملی frontend با مرورگر متصل هستند.

## بهبود پوشش نمادهای خارج از صفحه اصلی - batch 1 - 2026-08-30

- فهرست زندهٔ خارج از صفحهٔ اصلی دقیقاً ۶۴۵ نماد بود؛ اجرای عمومی pipeline به‌دلیل دربرداشتن ۱۵۲۴ نماد شامل صندوق‌ها متوقف و batch صریح از اسکرینر عمومی ساخته شد.
- batch اول ۱۰ نماد (`شگویا، وپارس، شسپا، بجهرم، پخش، والبر، فسبزوار، رانیز، دعبید، خگستر`) بود. برای ۹ نماد refresh تحلیل انجام شد؛ خگستر به‌دلیل `AbortError` کدال retained شد.
- Production import با backup `/var/backups/boursnegar/20260830T132324Z-auto-local-to-production.dump` انجام شد: ۶۱۱۷ رکورد codalpy، ۱۰۷ رکورد normalized و ۸۲ رویداد، validation error صفر، و replay idempotent موفق. health/ready هر سه سبز بودند.
- نتیجهٔ زنده پس از refresh: پوشش خارج از صفحه اصلی از ۵۰ به ۵۸ نماد با coverage=100٪ رسید؛ ۳۹۵ نماد در ۴۲٫۸۶٪، ۱۳۶ در ۸۵٫۷۱٪، ۴۲ در ۲۸٫۵۷٪، ۴ در ۵۷٫۱۴٪، ۲ در ۷۱٫۴۳٪ و ۵۸ نماد بدون coverage باقی مانده‌اند. هنوز تصمیم‌ها برای این batch به‌دلیل confidence/شواهد کافی قطعی نشده‌اند.
- checkpointها و manifestهای run در `artifacts/auto-sync/20260830T131225Z/` نگهداری شدند؛ timeout و سند غیرقابل‌خواندن retained شد و هیچ مقدار حدسی وارد نشد. batch بعدی باید از فهرست عمومی ۶۴۵تایی و با همین کنترل‌ها ادامه یابد.

## بهبود پوشش نمادهای خارج از صفحه اصلی - batch 2 - 2026-08-30

- batch دوم از همان فهرست عمومی شامل `ثفارس، غپینو، دزاگرس، فرابورس، شغدیر، بترانس، غنوش، آریان، حتاید، پکویر` اجرا شد.
- Production import با backup `/var/backups/boursnegar/20260830T134051Z-auto-local-to-production.dump` انجام شد: ۷۲۸۹ رکورد codalpy، ۲۰۱ رکورد normalized و ۱۰۵ رویداد، validation error صفر، replay idempotent موفق و health/ready سبز.
- refresh هر ۱۰ نماد با `latest_codal` موفق بود. ۹ نماد به coverage=100٪ و حتاید به 85.71٪ رسید؛ همه به‌دلیل سیاست confidence/evidence هنوز `INSUFFICIENT_DATA`/`DATA_REVIEW` هستند.
- ممیزی live خارج از صفحه اصلی اکنون ۶۴۵ نماد را با ۱۷ نماد coverage=100٪، ۱۳۶ نماد 85.71٪، ۳۸۷ نماد 42.86٪، ۴۱ نماد 28.57٪، چهار نماد 57.14٪، دو نماد 71.43٪ و ۵۸ نماد صفر ثبت می‌کند. صف عمومی بعدی باید از نماد ۲۱ فهرست batchها ادامه پیدا کند.
## 2026-08-30 - Public non-homepage coverage batch 3

- Target: the next 10 symbols from live public pages 2-14 with incomplete coverage: کالا، بازرگام، خزامیا، افرا، کویر، شبهرن، شرانل، دامین، اسیـاتک، فاذر.
- Evidence: local Codal artifacts were collected through codalpy first and browser/Codal fallback where required; manifests were produced and local SQLite was updated idempotently. Production backup: `/var/backups/boursnegar/20260830T135847Z-auto-local-to-production.dump`.
- Production import: codalpy inserted 6854 records, normalized inserted 105, notice events inserted 43; validation errors 0; replay was idempotent; `data-service`, `healthz`, and `readyz` were green; symbol failures 0.
- Refresh: all 10 `latest_codal` refresh calls succeeded. 8 reached 100.0% coverage; کالا and اسیـاتک reached 85.71%. All remain `INSUFFICIENT_DATA` because evidence/confidence/model gates still block a decision.
- Live remainder audit after refresh: 645 rows; coverage `100.0=25`, `85.71=137`, `71.43=2`, `57.14=3`, `42.86=380`, `28.57=40`, `0=58`; action states `DATA_REVIEW=472`, `CONDITIONAL_REVIEW=75`, `SELL=30`, `HOLD=8`, `BUY=2`, `NOT_EVALUABLE=58`.
- Next queue prepared: غدانه، پترول، جم، سفارس، دتوزیع، فولاژ، وخارزم، حفاری، دقاضی، کوچین. Remaining incomplete-coverage public symbols: 615.
## 2026-08-30 - Public non-homepage coverage batch 4

- Target: غدانه، پترول، جم، سفارس، دتوزیع، فولاژ، وخارزم، حفاری، دقاضی، کوچین.
- Evidence/import: Codal artifacts were checkpointed locally; the first orchestration stopped after artifacts were retained, then the batch was safely resumed. Production backup: `/var/backups/boursnegar/20260830T142521Z-auto-local-to-production.dump`. Three manifests imported with validation errors 0, idempotent replay, and no symbol failures; health/ready green.
- Refresh: all ten `latest_codal` calls succeeded and reached 100.0% coverage. حفاری produced a valid `SELL`; the other nine remain `INSUFFICIENT_DATA` under the confidence/evidence gates.
- Live remainder audit: 645 rows; coverage `100.0=35`, `85.71=135`, `71.43=2`, `57.14=2`, `42.86=374`, `28.57=39`, `0=58`; action states `DATA_REVIEW=473`, `CONDITIONAL_REVIEW=74`, `SELL=30`, `HOLD=8`, `BUY=2`, `NOT_EVALUABLE=58`.
- Next queue remains to be selected from the 610 incomplete-coverage public symbols; no synthetic coverage or decision was created.
## 2026-08-30 - Public non-homepage coverage batch 5

- Target: داترا، غگز، وفیروزه، سصفها، وسنا، آلومینا، ددام، شاراک، درهآور، سباقر.
- Evidence/import: checkpointed Codal artifacts were normalized locally and imported through the artifact-only Production path. Backup: `/var/backups/boursnegar/20260830T144326Z-auto-local-to-production.dump`; validation errors 0, replay idempotent, health/ready green.
- Refresh: all ten `latest_codal` calls succeeded at 100.0% coverage. وفیروزه returned `SELL`; the other nine remain `INSUFFICIENT_DATA` under evidence/confidence gates.
- Live remainder audit: 645 rows; coverage `100.0=45`, `85.71=131`, `71.43=2`, `57.14=2`, `42.86=369`, `28.57=38`, `0=58`; action states `DATA_REVIEW=476`, `CONDITIONAL_REVIEW=70`, `SELL=31`, `HOLD=8`, `BUY=2`, `NOT_EVALUABLE=58`.
- Remaining incomplete-coverage symbols: 600. No synthetic facts or decisions were added.
## 2026-08-30 - Public non-homepage coverage batch 6

- Target: دکیمی، اخابر، چدن، غزر، هجرت، شیران، سخوز، سرود، پتایر، بمولد.
- Evidence/import: checkpointed Codal artifacts were recovered, normalized and imported through the artifact-only Production path. Backup: `/var/backups/boursnegar/20260830T150110Z-auto-local-to-production.dump`; three manifests, validation errors 0, idempotent replay, health/ready green, symbol failures 0.
- Refresh: all ten `latest_codal` calls succeeded at 100.0% coverage. All remain `INSUFFICIENT_DATA` under the evidence/confidence gates; no decision was fabricated.
- Live remainder audit: 645 rows; coverage `100.0=55`, `85.71=129`, `71.43=2`, `57.14=2`, `42.86=361`, `28.57=38`, `0=58`; action states `DATA_REVIEW=478`, `CONDITIONAL_REVIEW=69`, `SELL=31`, `HOLD=7`, `BUY=2`, `NOT_EVALUABLE=58`.
- Remaining incomplete-coverage symbols: 590.
## 2026-08-30 - Public non-homepage coverage batch 7

- Target: کاوه، کی بی سی، واتی، غشان، شملی، شبصیر، سجام، دکوثر، زدشت، فسپا.
- Evidence/import: checkpointed official Codal artifacts were imported through the artifact-only Production path; health/ready green and replay idempotent. No symbol failure was reported. The run backup was created before import.
- Refresh: all ten `latest_codal` calls succeeded at 100.0% coverage. واتی returned valid `SELL`; the other nine remained `INSUFFICIENT_DATA` under evidence/confidence gates.
- Live remainder audit: 645 rows; coverage `100.0=65`, `85.71=124`, `71.43=2`, `57.14=2`, `42.86=356`, `28.57=38`, `0=58`; action states `DATA_REVIEW=482`, `CONDITIONAL_REVIEW=65`, `SELL=31`, `HOLD=7`, `BUY=2`, `NOT_EVALUABLE=58`.
- Remaining incomplete-coverage symbols: 580.
## 2026-08-30 - Public non-homepage coverage batch 8

- Target: قچار، جم پیلن، بوعلی، هرمز، شاوان، ثشاهد، شمواد، وتجارت، های وب، ساینا.
- Evidence/import: official Codal artifacts were checkpointed and imported through the artifact-only Production path; 28,883 Codal records and 185 normalized records were accepted, validation errors 0, replay idempotent, health/ready green. Backup was taken before import.
- Refresh: all ten `latest_codal` calls succeeded. Eight reached 100.0%; وتجارت and های وب reached 85.71% and both returned `SELL`. The remaining symbols stayed under evidence gates.
- Live remainder audit: 645 rows; coverage `100.0=73`, `85.71=120`, `71.43=2`, `57.14=2`, `42.86=352`, `28.57=38`, `0=58`; action states `DATA_REVIEW=486`, `CONDITIONAL_REVIEW=60`, `SELL=32`, `HOLD=7`, `BUY=2`, `NOT_EVALUABLE=58`.
- Remaining incomplete-coverage symbols: 572.
## 2026-08-30 - Public non-homepage coverage batch 9

- Target: کاسپین، دلر، فافق، فایرا، بهپاک، غصینو، ذوب، نان، وکغدیر، کحافظ.
- Evidence/import: official Codal artifacts were checkpointed and imported through the artifact-only Production path. Import accepted 11,049 Codal records, 234 normalized records and 143 notice events; validation errors 0, idempotent replay, health/ready green, symbol failures 0. Backup: `/var/backups/boursnegar/20260830T155442Z-auto-local-to-production.dump`.
- Refresh: all ten `latest_codal` calls succeeded at 100.0%. وکغدیر returned `SELL`; ذوب was classified `TURNAROUND_CANDIDATE` but remained `INSUFFICIENT_DATA`; the other eight remained evidence-gated.
- Live remainder audit: 645 rows; coverage `100.0=83`, `85.71=119`, `71.43=2`, `57.14=2`, `42.86=346`, `28.57=36`, `0=57`; action states `DATA_REVIEW=487`, `CONDITIONAL_REVIEW=60`, `SELL=32`, `HOLD=7`, `BUY=2`, `NOT_EVALUABLE=57`.
- Remaining incomplete-coverage symbols: 562.
## 2026-08-30 - Public non-homepage coverage batch 10

- Target: بالاس، زکوثر، وخاور، بیوتیک، کسرا، فپنتا، زفجر، شیراز، زاگرس، قاسم.
- Evidence/import: official checkpointed Codal artifacts imported through the artifact-only Production path; validation errors 0, idempotent replay, health/ready green, symbol failures 0. Backup: `/var/backups/boursnegar/20260830T161349Z-auto-local-to-production.dump`.
- Refresh: all ten `latest_codal` calls succeeded. Nine reached 100.0%; وخاور remained 85.71%. قاسم stayed `INSUFFICIENT_DATA` with `CAPITAL_ACTION_DATA_GAP`, not a fabricated decision.
- Live remainder audit: 645 rows; coverage `100.0=92`, `85.71=119`, `71.43=2`, `57.14=2`, `42.86=337`, `28.57=36`, `0=57`; action states `DATA_REVIEW=488`, `CONDITIONAL_REVIEW=59`, `SELL=32`, `HOLD=7`, `BUY=2`, `NOT_EVALUABLE=57`.
- Remaining incomplete-coverage symbols: 553.
## 2026-08-30 - Public non-homepage coverage batch 11

- Target: فخاس، سصوفی، آریا، پارس، بپاس، کلر، زملارد، برکت، کگهر، وبانک.
- Evidence/import: official checkpointed Codal artifacts imported through the artifact-only Production path; validation errors 0, replay idempotent, health/ready green, symbol failures 0. Backup: `/var/backups/boursnegar/20260830T163228Z-auto-local-to-production.dump`.
- Refresh: all ten calls succeeded; nine reached 100.0% coverage and one remained below full coverage. بپاس returned valid `SELL`; other symbols stayed evidence-gated.
- Batch evidence is complete; the next full live audit will establish the updated 645-row distribution.

## 2026-08-30 - Public non-homepage coverage batch 12

- Target: ومپنا، وسپهر، خیمن، وپاسار، فولای، دسبحا، شپارس، مادیرا، شکلر، کطبس.
- Evidence/import: official Codal artifacts were checkpointed locally; codalpy and browser fallback artifacts were normalized and promoted through the artifact-only Production path. Production accepted 28,208 Codal records, 172 normalized records and 86 notice events; validation errors 0, replay idempotent, health/ready green, and symbol failures empty. Backup: `/var/backups/boursnegar/20260830T164803Z-auto-local-to-production.dump`.
- Refresh: all ten `latest_codal` calls succeeded. 9 reached 100.0% coverage; وپاسار reached 85.71%. All ten remained `INSUFFICIENT_DATA` because evidence/confidence/model gates still prevent a defensible BUY/HOLD/SELL; no decision was fabricated.
- Live audit of pages 2-14: exactly 645 rows; coverage `100.0=111`, `85.71=114`, `71.43=2`, `57.14=2`, `42.86=323`, `28.57=36`, `0=57`; action states `DATA_REVIEW=493`, `CONDITIONAL_REVIEW=57`, `SELL=32`, `HOLD=4`, `BUY=2`, `NOT_EVALUABLE=57`; decisions `INSUFFICIENT_DATA=607`, `SELL=32`, `HOLD=4`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=513`, `WORTH_REVIEW=75`, `WAIT_FOR_DATA=57`.
- Remaining work is still substantial: 534 rows are below 100.0% coverage. Continue with the next explicit 10-symbol queue after selecting only from the current live pages and excluding completed batches; preserve all checkpoints, manifests and backups.

## 2026-08-30 - Public non-homepage coverage batch 13

- Target: شپاس، شصدف، زشگزا، وسپه، تادیکو، تایرا، نماد، فباهنر، سشرق، کپارس.
- Evidence/import: official Codal artifacts were checkpointed locally and promoted through the artifact-only Production path. Production accepted 15,402 Codal records, 162 normalized records and 102 notice events; validation errors 0, replay idempotent, health/ready green, and symbol failures empty. Backup: `/var/backups/boursnegar/20260830T170654Z-auto-local-to-production.dump`.
- Refresh: all ten `latest_codal` calls succeeded; all ten reached 100.0% coverage. `نماد` returned a defensible `SELL`; the other nine remained `INSUFFICIENT_DATA` under evidence/confidence/model gates.
- Live audit of pages 2-14: exactly 645 rows; coverage `100.0=121`, `85.71=111`, `71.43=2`, `57.14=2`, `42.86=317`, `28.57=36`, `0=56`; action states `DATA_REVIEW=497`, `CONDITIONAL_REVIEW=54`, `SELL=33`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=56`; decisions `INSUFFICIENT_DATA=607`, `SELL=33`, `HOLD=3`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=518`, `WORTH_REVIEW=71`, `WAIT_FOR_DATA=56`.
- Remaining below-full-coverage rows: 524. Continue with explicit live-queue batches and preserve the evidence, especially for symbols whose full fact coverage still cannot clear the decision gates.

## 2026-08-30 - Public non-homepage coverage batch 14

- Target: کیسون، کرماشا، خموتور، بورس، وپترو، فسازان، وتوسم، غپونه، وپست، کهمدا.
- Recovery/import: the first Production backup attempt hit a full filesystem and was discarded as an incomplete dump. The orchestrator was then hardened with local streamed rollback backups and atomic same-filesystem artifact moves. After limited cleanup of archived journals and failed-run staging only, the batch was promoted successfully. Local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260830T181500Z-batch14.dump`. Production accepted 23,930 Codal records, 55 normalized records and 21 notice events; validation errors 0, replay idempotent, health/ready green, and symbol failures empty.
- Refresh: 9 `latest_codal` calls succeeded. کیسون returned valid `SELL`; کرماشا، خموتور، وپترو، فسازان، غپونه و کهمدا remained `INSUFFICIENT_DATA` at 100.0%; بورس and وپست remained `INSUFFICIENT_DATA` at 85.71%; وتوسم returned HTTP 404 and is retained as an explicit refresh failure, not counted as success.
- Live audit of pages 2-14: exactly 645 rows; coverage `100.0=128`, `85.71=112`, `71.43=2`, `57.14=2`, `42.86=309`, `28.57=36`, `0=56`; action states `DATA_REVIEW=497`, `CONDITIONAL_REVIEW=53`, `SELL=34`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=56`; decisions `INSUFFICIENT_DATA=606`, `SELL=34`, `HOLD=3`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=519`, `WORTH_REVIEW=70`, `WAIT_FOR_DATA=56`.
- Remaining below-full-coverage rows: 517. The next queue must be selected from the current live pages, with the exact `وتوسم` 404 and any alias/identity mismatch retained for parser/API investigation.

## 2026-08-30 - Public non-homepage coverage batch 15-16

- Batch 15 target: ثمسکن، مفاخر، کوثر، وصندوق، سیلام، ثبهساز، دسانکو، شراز، حتوکا، زفکا. Production accepted 37,508 records through three artifact manifests; local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260830T190000Z-batch15.dump`; validation errors 0, replay idempotent, health/ready green, symbol failures empty.
- Batch 15 refresh: 9 calls succeeded. ثمسکن، مفاخر، سیلام، ثبهساز، دسانکو، شراز و زفکا reached 100.0% but remained `INSUFFICIENT_DATA`; وصندوق reached 100.0% with `SELL`; حتوکا reached 85.71% and remained `INSUFFICIENT_DATA`; کوثر returned HTTP 404 and remains an explicit refresh failure.
- Batch 16 target: آرمان، اتکاسا، اتکام، اعتلا، البرز، باران، بتیس، بزندگی، بنو، بهامرز. Production accepted 15,789 records through three artifact manifests; local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260830T200000Z-batch16.dump`; validation errors 0, replay idempotent, health/ready green, symbol failures empty.
- Batch 16 refresh: all ten returned HTTP 404 with `برای نماد ... گزارش واردشده‌ای موجود نیست`; no fabricated coverage or decision was created. This indicates a remaining report-identity/accepted-financial-report gap after official Codal artifacts were captured, requiring parser/alias/model investigation.
- Live audit of pages 2-14 after batch 16: exactly 645 rows; coverage `100.0=136`, `85.71=111`, `71.43=2`, `57.14=2`, `42.86=302`, `28.57=36`, `0=56`; action states `DATA_REVIEW=497`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=56`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=520`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=56`.
- Remaining below-full-coverage rows: 509. Continue selecting from the live lowest-coverage queue, while separately investigating why imported official artifacts for batch 16 are not recognized as accepted reports by `/api/v2/analyze`.

## 2026-08-30 - Sector label parser correction

- Root cause found for part of the report-not-found/insufficient evidence cluster: insurance financial statements use the exact total label `درآمدهای بیمه‌ای`, while the parser only accepted generic operating-revenue labels. The normalized form is also covered, and the CodalPy mapping now recognizes both Persian spacing variants.
- Added a focused parser regression test; 29 relevant unittest cases pass, Python compilation passes, and `git diff --check` passes. No broad or ambiguous revenue inference was added.
- Next recovery should re-import/refresh affected insurance symbols and measure whether the accepted same-period report gate clears; unresolved symbols remain explicit review gaps.
- Re-running آرمان، اتکاسا، اتکام و اعتلا after the fix showed a real effect: آرمان، اتکاسا و اتکام moved from HTTP 404 to persisted `latest_codal` analysis at 71.43% / `PARTIAL_DATA`; اعتلا still returns HTTP 404 because no usable report with both revenue and net profit was accepted. All remain `INSUFFICIENT_DATA`; no decision was fabricated.
- Live audit after the parser recovery: 645 rows; coverage `100.0=136`, `85.71=111`, `71.43=5`, `57.14=2`, `42.86=302`, `28.57=36`, `0=53`; actions `DATA_REVIEW=500`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=53`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`. The zero-coverage count dropped from 56 to 53, with no synthetic values.
- Batch 17 target: خودکفا، نوین، رایا، نیروترانسفو، مهر، والماس، وحافظ، ما، میهن، ثزاگرس. Official checkpointed artifacts were imported through three manifests with local rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260830T220000Z-batch17.dump`; 8,105 records, validation errors 0, idempotent replay, health/ready green, symbol failures empty.
- Batch 17 refresh: نوین، رایا، وحافظ، ما و میهن reached 71.43% `PARTIAL_DATA`; ثزاگرس reached 100.0% `READY`; خودکفا، نیروترانسفو، مهر و والماس returned explicit HTTP 404. All successful analyses remained `INSUFFICIENT_DATA` under evidence/confidence gates.
- Live audit after batch 17: exactly 645 rows; coverage `100.0=137`, `85.71=111`, `71.43=10`, `57.14=2`, `42.86=302`, `28.57=36`, `0=47`; actions `DATA_REVIEW=506`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=47`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=529`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=47`.
- Remaining below-full-coverage rows: 508. Continue the lowest-coverage queue and retain the four explicit 404s as unresolved report/identity gaps.
- Batch 18 target: ومشان، وسبحان، وصنا، گوهران، کمرجانح، معین، وحکمت، وثوق، پردیس، دانا. Production accepted 12,881 checkpointed records through three manifests with backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260830T230000Z-batch18.dump`; validation errors 0, idempotent replay, health/ready green, and no symbol failures.
- Batch 18 refresh: معین، وحکمت و دانا reached 71.43% `PARTIAL_DATA`; the other seven returned explicit HTTP 404. No decision was fabricated.
- Batch 19 target: وثنو، وفردا، وهامون، وبوعلی، وسالت، وآتوس، سنوین، ومعلم، وجامی. Production accepted 2,479 records through three manifests with backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T000000Z-batch19.dump`; validation errors 0, idempotent replay, health/ready green. `وهامون` is retained as an explicit ingestion symbol failure (`exit=1`).
- Batch 19 refresh: وفردا and ومعلم reached 71.43% `PARTIAL_DATA`; وسالت reached 28.57% `PARTIAL_DATA`; وثنو، وهامون، وبوعلی، وآتوس، سنوین و وجامی returned explicit HTTP 404. These are not counted as successful full analyses.
- Live audit after batches 18-19: exactly 645 rows; coverage `100.0=137`, `85.71=111`, `71.43=15`, `57.14=2`, `42.86=302`, `28.57=37`, `0=41`; actions `DATA_REVIEW=512`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=41`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=535`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=41`.
- Remaining below-full-coverage rows: 508. The zero-coverage count has fallen from 56 to 41; explicit report/identity failures must remain visible for later alias/parser investigation.
- Batch 18-19 industry audit: active data service reports 1,524 active instruments across 47 authoritative industry groups. ETF funds (419 symbols) remain separated from operational-company core-fact scoring; insurance has 34 symbols with sector-specific revenue handling. Global ledger facts: 64,415 rows, 32,176 valid, 1,688,726 linked raw Codal records; these totals include the full active universe and are not substituted for the public 645-row audit.
- Parser production proof: `codal_excel_parser.py` and `codalpy_pipeline.py` were backed up in the active data release with timestamp `20260830T185720Z`, copied with matching SHA-256 to `/var/www/boursnegar-data-current`, and the data service restarted. It is currently `active` with `/health` returning `{"status":"ok"}`. New release creation was avoided because remote root had only 15M free; file-level rollback copies and the existing database dump backups are retained.
- Batch 20 target: واعتبار، حیات، مدیریت، فن افزار، وتعاون، سفارود، وسین، ودی، وسرمد. Production accepted 1,592 checkpointed records through three manifests with backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T010000Z-batch20.dump`; validation errors 0, idempotent replay, health/ready green, and symbol failures empty.
- Batch 20 refresh: حیات، وتعاون، وسین، ودی و وسرمد reached 71.43% `PARTIAL_DATA`; واعتبار، مدیریت، فن افزار و سفارود returned explicit HTTP 404. All successful analyses remained `INSUFFICIENT_DATA` under evidence/confidence gates.
- Live audit after batch 20: exactly 645 rows; coverage `100.0=137`, `85.71=111`, `71.43=20`, `57.14=2`, `42.86=302`, `28.57=37`, `0=36`; actions `DATA_REVIEW=517`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=36`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=540`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=36`.
- Remaining below-full-coverage rows: 508. Zero-coverage fell from 56 to 36 across the recovery batches; remaining 404s and 28.57%-42.86% groups require continued evidence recovery, alias/period inspection, and sector-specific parser coverage.
- Batch 21 target: ثقزویح، گنگین، وطوبی، فاهواز، ولاناح، وآفری. The local run reached staged manifests and had a 142MB rollback backup at `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T020000Z-batch21.dump`; staged manifests were safely replayed idempotently after cleanup, with validation errors 0 and no data loss. Final health/ready checks were green and staging was removed.
- Batch 21 refresh: وآفری reached 71.43% `PARTIAL_DATA`; ثقزویح، گنگین، وطوبی، فاهواز و ولاناح returned explicit HTTP 404. No synthetic decision or coverage was created.
- Slowdown incident: the batch left a local `.chrome-codal-profile` Chrome process group with 20+ renderer processes. The ingestion session had already stopped; the exact process group was terminated, no Chrome/Codal ingestion process remains, local memory is 3.6Gi/15Gi used with 11Gi available, local disk is 27% used, and the remote data service remains active/healthy. The staged batch was completed before cleanup.
- Live audit after batch 21: exactly 645 rows; coverage `100.0=137`, `85.71=111`, `71.43=21`, `57.14=2`, `42.86=302`, `28.57=37`, `0=35`; actions `DATA_REVIEW=518`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=35`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=541`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=35`.
- Remaining below-full-coverage rows: 508. Zero-coverage is now 35; the next work remains explicit 404/alias recovery plus the 28.57%-42.86% period/core-fact gaps.
- Parser total-label correction: added exact `جمع درآمدهای عملیاتی` mapping for investment/fund statements in both Excel and CodalPy parsers. The focused suite now has 30 passing unittest cases; production deployment backup timestamp was `20260830T192536Z`, checksums matched, service restarted and health stayed green.
- Targeted parser recovery for واعتبار، مدیریت و کوثر used backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T030000Z-parser-total-recovery.dump`; 2,111 records imported via three manifests with validation errors 0, idempotent replay and no symbol failures. Refresh moved واعتبار and مدیریت to 85.71% `PARTIAL_DATA`, and کوثر to 71.43% `PARTIAL_DATA`; all remained `INSUFFICIENT_DATA`.
- Live audit after targeted parser recovery: exactly 645 rows; coverage `100.0=137`, `85.71=113`, `71.43=22`, `57.14=2`, `42.86=302`, `28.57=37`, `0=32`; actions `DATA_REVIEW=521`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=32`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`. Review signals: `INCOMPLETE_EVIDENCE=544`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=32`.
- Remaining below-full-coverage rows: 508. Zero-coverage is now 32; unresolved 404s are increasingly concentrated in symbols with no usable report or unresolved identity/period mapping, while 28.57%-42.86% rows need more comparable/core facts.

## 2026-08-30 - Slowdown recovery and public batch 22

- Slowdown remediation: the orphaned local Codal/Chrome process group was terminated; local resources are normal. On Production, archived journals were vacuumed from 72MB to the configured 20MB ceiling, freeing 56MB. Two inactive legacy web releases from 2026-08-25 were removed after confirming they were not the active release; current and recent rollback releases remain. Production root moved from 100% with 22MB free to 98% with 616MB free. No data release, database, or evidence backup was removed.
- Batch 22 target: بموتو، بنیرو، حآفرین، حسیر، سمازن، عالیس، غسالم، فبیرا، وسینا، کیمازی. Existing checkpointed official artifacts were transferred in bounded one-manifest stages after a local streamed rollback backup at `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T040000Z-batch22.dump`; 48,353 CodalPy records, 472 normalized records and 180 notice events were present. SHA-256 was checked before each import; validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz remained green.
- The original all-at-once batch22 transfer failed before import because Production root was full; it was not counted as a successful run. The staged retry completed without re-downloading or deleting local evidence.
- Live audit after batch22: exactly 645 rows; coverage `100.0=137`, `85.71=113`, `71.43=22`, `57.14=2`, `42.86=302`, `28.57=37`, `0=32`; actions `DATA_REVIEW=521`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=32`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`; review signals `INCOMPLETE_EVIDENCE=544`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=32`.
- Remaining below-full-coverage rows: 508. The next recovery batch is still gated by evidence quality and by preserving at least several hundred MB of Production free space; do not start another bulk browser ingestion while disk is below the operational floor.

## 2026-08-30 - Public non-homepage coverage batch 23

- Target: وبوعلی، وصنا، اکتان، خودران، دارونو، سیمانو، معدن، صنم، تمشک، خوشه. Checkpointed official artifacts were processed with the bounded browser fallback; local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260830T195937Z-batch23.dump`.
- Production accepted 10,279 records through three manifests; CodalPy supplied 688 standard facts and normalized data supplied 13 additional standard facts. Validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- Recovery evidence was not equivalent for every symbol: وبوعلی and وصنا returned HTTP 200 from `latest_codal`; اکتان، خودران، دارونو، سیمانو، معدن، صنم، تمشک و خوشه returned explicit HTTP 404 after the available CodalPy/browser attempts. These remain unresolved evidence/identity gaps, not successful analyses.
- Live audit after refreshing batch23: exactly 645 rows; coverage `100.0=137`, `85.71=115`, `71.43=22`, `57.14=2`, `42.86=302`, `28.57=37`, `0=30`; actions `DATA_REVIEW=523`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`; review signals `INCOMPLETE_EVIDENCE=546`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=30`. وبوعلی and وصنا now have 85.71% snapshots; the other eight explicit 404s remain unresolved.
- Remaining below-full-coverage rows: 508. Zero-coverage is now 30; the next queue continues from the live lowest-coverage rows with bounded browser work and preserved checkpoints.

## 2026-08-30 - Public non-homepage coverage batch 24

- Target: اکتان، خودران، دارونو، سیمانو، معدن، صنم، تمشک، خوشه، امرالد، اوصتا. Existing checkpoints were retried through the bounded CodalPy/browser path; local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260830T210000Z-batch24.dump`.
- Production accepted 3,727 records through three manifests; validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz were green. The batch had no orchestrator-level symbol failure, while individual source retries and parser normalization errors remain visible in their checkpoints/manifests.
- Refresh returned explicit HTTP 404 for all ten symbols. No new public snapshots, coverage, or decisions were fabricated; the existing 30 zero-coverage rows remain unchanged.
- Live audit after batch24: exactly 645 rows; coverage `100.0=137`, `85.71=115`, `71.43=22`, `57.14=2`, `42.86=302`, `28.57=37`, `0=30`; actions `DATA_REVIEW=523`, `CONDITIONAL_REVIEW=52`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`; review signals `INCOMPLETE_EVIDENCE=546`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=30`.

## 2026-08-30 - Explicit fund model boundary

- Root cause audit: 419 of the 1,524 active instruments are authoritative ETF/fund instruments. They have no company-style core financial facts by design and were previously mixed into the generic incomplete queue, causing repeated 404 attempts.
- Added an explicit `fund` model family for ETF industry labels, excluded funds from the operating-company turnaround logic, and changed the coverage audit tier to `FUND_MODEL_REQUIRED`. Production audit now reports `CORE_READY=528`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=445`, `MISSING_CORE_FACTS=132`.
- Automatic recovery selection now defers ETF/fund rows; explicit symbol files can still target them when a sourced NAV/holdings model is implemented. Production file-level backups were created before deployment, SHA-256 was checked, the service restarted, and health returned `ok`.
- This is a model-boundary correction, not a claim that funds are fully analyzed. A separate sourced NAV/holdings/discount-premium model remains required before issuing fund valuation decisions.

## 2026-08-30 - Public non-homepage coverage batch 25

- Target: فافزا، وامیر، ولانا، کشرق، افرا، بمپنا، تکاردان، ثباغ، خکاوه، ساوه. Existing official checkpoints were recovered with bounded CodalPy/browser fallback; local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260830T220000Z-batch25.dump`.
- Production accepted 5,056 records through three manifests: 2,220 CodalPy records, 5 normalized records and 1 notice event were new at import, with 120 and 23 standard facts respectively. Validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten requested analyses returned HTTP 200 from `latest_codal`; nine were visible in the current public 645-row pages and reached 100.0% coverage. They remained `INSUFFICIENT_DATA`/`DATA_REVIEW` because evidence/confidence/model gates do not support a defensible recommendation; no BUY/HOLD/SELL was forced.
- Live audit after batch25: exactly 645 rows; coverage `100.0=145`, `85.71=113`, `71.43=22`, `57.14=2`, `42.86=296`, `28.57=37`, `0=30`; actions `DATA_REVIEW=524`, `CONDITIONAL_REVIEW=51`, `SELL=35`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=605`, `SELL=35`, `HOLD=3`, `BUY=2`; review signals `INCOMPLETE_EVIDENCE=547`, `WORTH_REVIEW=68`, `WAIT_FOR_DATA=30`.
- Remaining below-full-coverage rows: 500. Zero-coverage remains 30, now explicitly split between `FUND_MODEL_REQUIRED` ETF rows and unresolved non-fund report/period/identity gaps.

## 2026-08-31 - Public non-homepage coverage batch 26

- Target: اوانح، ثامید، کرمان، وشهر، آرمانح، آواپارس، کاریز، حآسا، خفنر، توسن. Checkpointed official artifacts were processed with bounded CodalPy/browser fallback; local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T230000Z-batch26.dump`.
- Production accepted 27,895 records through three manifests: 19,875 CodalPy records, 10 normalized records and 2 notice events were new at import; standard facts added were 888 and 15 respectively. Validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- Refresh returned HTTP 200 for ثامید، کرمان، آواپارس، کاریز، حآسا، خفنر و توسن; ثامید، کرمان، توسن، خفنر reached 100.0% and حآسا produced a defensible `SELL`. اوانح، وشهر و آرمانح remained explicit HTTP 404 gaps. No decision was fabricated for the unresolved symbols.
- Live audit after batch26: exactly 645 rows; coverage `100.0=150`, `85.71=112`, `71.43=22`, `57.14=2`, `42.86=292`, `28.57=37`, `0=30`; actions `DATA_REVIEW=522`, `CONDITIONAL_REVIEW=52`, `SELL=36`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=604`, `SELL=36`, `HOLD=3`, `BUY=2`; review signals `INCOMPLETE_EVIDENCE=546`, `WORTH_REVIEW=69`, `WAIT_FOR_DATA=30`.
- Remaining below-full-coverage rows: 495. The next queue must exclude the completed batch26 symbols and ETF/fund instruments, and continue investigating unresolved identity/period gaps.

## 2026-08-31 - Public non-homepage coverage batch 27

- Target: پاریز، ورازی، حشکوه، حپارسا، حپترو، حپرتو، رنیک، خزر، خعمرا، خلنت. Checkpointed official artifacts were recovered via bounded CodalPy/browser fallback; local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T010000Z-batch27.dump`.
- Production accepted 22,696 records through three manifests: 4,744 CodalPy records, 255 normalized records and 180 notice events were new at import; standard facts added were 1,178 and 230 respectively. Validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. Eight of the ten reached 100.0% public coverage; the remaining two have persisted snapshots but remain below full coverage. No decision was forced by the import.
- Live audit after batch27: exactly 645 rows; coverage `100.0=158`, `85.71=112`, `71.43=22`, `57.14=2`, `42.86=286`, `28.57=35`, `0=30`; actions `DATA_REVIEW=519`, `CONDITIONAL_REVIEW=53`, `SELL=38`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=602`, `SELL=38`, `HOLD=3`, `BUY=2`; review signals `INCOMPLETE_EVIDENCE=545`, `WORTH_REVIEW=70`, `WAIT_FOR_DATA=30`.
- Remaining below-full-coverage rows: 487. The zero-coverage count remains 30 because it is dominated by explicit fund-model and unresolved identity gates; continue with nonfund rows and do not reinterpret missing evidence as a recommendation.

## 2026-08-31 - Recovery queue deduplication

- Fixed the Local->Production orchestrator so automatic selection excludes any symbol that already has a checkpointed attempt under the artifact root, while explicit `--symbols-file` queues can intentionally retry symbols after parser or alias changes.
- Automatic selection continues to exclude ETF/fund instruments until the sourced fund model exists. Focused regression coverage now has 30 passing tests; `git diff --check` and project memory checks pass.

## 2026-08-31 - Public non-homepage coverage batch 28

- Target: غدیس، وتوس، کمرجان، انتخاب، حگهر، غمایه، غویتا، غگیلا، فبستم، نطرین. The deduplicated automatic queue selected these ten nonfund symbols after excluding prior checkpoint attempts and fund-model rows.
- Checkpointed official artifacts were processed with CodalPy/browser fallback; local rollback backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T030000Z-batch28.dump`. Production accepted 2,072 records through three manifests: 1,468 CodalPy records, 14 normalized records and 2 notice events were new at import; validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz remained green. Symbol failures were empty.
- All ten `latest_codal` refreshes returned HTTP 200. The public 645-row audit remains exactly 645 unique rows; coverage is `100.0=167`, `85.71=108`, `71.43=22`, `57.14=2`, `42.86=281`, `28.57=35`, `0=30`; actions are `DATA_REVIEW=515`, `CONDITIONAL_REVIEW=54`, `SELL=41`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=30`; decisions are `INSUFFICIENT_DATA=599`, `SELL=41`, `HOLD=3`, `BUY=2`; review signals are `INCOMPLETE_EVIDENCE=541`, `WORTH_REVIEW=74`, `WAIT_FOR_DATA=30`.
- Batch 28 improved full coverage by 9 rows and reduced `INSUFFICIENT_DATA` by 3, but it did not make every symbol evaluable. The remaining 30 zero-coverage rows are still explicit fund-model or unresolved identity/evidence gates; no recommendation was fabricated.
- Slowdown gate after batch 28: remote root remains at 98% usage with approximately 542MB free. `bourse-app` is online, data health is green, local RAM has approximately 11GiB available, and no orphaned Codal/Chrome ingestion process remains. Further bulk browser recovery should remain paused until reversible disk headroom is restored while retaining the active release, rollback releases, and evidence backups.

## 2026-08-31 - Staging cleanup and public non-homepage coverage batch 29

- Slowdown root cause was confirmed: completed `staging/auto-sync` transfer directories occupied approximately 1.56GB inside the active data release. No Codal/import process was active and the newest staging directory belonged to completed batch 28. Only these temporary replicated artifacts were removed; the database, active release, rollback releases, local evidence and production backups were retained. Production root improved from 98%/542MB free to 94%/1.6GB free.
- Batch 29 target: اتکای، بساما، تکیمیا، فجوش، کفرآور، زفارس، زگلدشت، الکترومادح، شگلح، مدارانح. Official checkpointed CodalPy/browser artifacts were processed with local rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T040000Z-batch29.dump`; two manifests imported 353 records with validation errors 0, idempotent replay, staging cleanup, green health/healthz/readyz, and no orchestrator-level symbol failures.
- Refresh returned HTTP 200 for اتکای، بساما، تکیمیا، فجوش، کفرآور، زفارس و زگلدشت. الکترومادح، شگلح و مدارانح returned explicit HTTP 404 and remain unresolved evidence/identity gaps; no decision was fabricated.
- Live audit after batch29: exactly 645 unique rows; coverage is `100.0=173`, `85.71=108`, `71.43=22`, `57.14=2`, `42.86=275`, `28.57=35`, `0=30`; actions are `DATA_REVIEW=512`, `CONDITIONAL_REVIEW=56`, `SELL=42`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=30`; decisions are `INSUFFICIENT_DATA=598`, `SELL=42`, `HOLD=3`, `BUY=2`; review signals are `INCOMPLETE_EVIDENCE=538`, `WORTH_REVIEW=77`, `WAIT_FOR_DATA=30`.
- Batch29 improved full coverage by 6 rows and reduced `INSUFFICIENT_DATA` by 1. The remaining 30 zero-coverage rows are still explicit fund-model or unresolved identity/evidence gates; 472 rows remain below full coverage. Production root is now 94% used with about 1.6GB free, and further batches must continue to remove temporary staging after each import.

## 2026-08-31 - Public non-homepage coverage batch 30

- Target: وآتوسح، ولنوینح، وپترو3، حکشتی3، آبادا3، آریا3، آسیا3، اتکام2، اتکام3، اردستان3. These suffix-bearing instruments were intentionally kept as independent identities; no base-symbol merge was assumed without official evidence.
- Official CodalPy/browser checkpoints were processed with local rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T060000Z-batch30.dump`. Two manifests imported 18 records with validation errors 0, idempotent replay, staging cleanup, green health/healthz/readyz, and no orchestrator-level symbol failures.
- Refresh returned HTTP 200 only for وپترو3; the other nine returned explicit HTTP 404. The result is retained as an identity/evidence gate, not converted into a recommendation or a base-symbol alias.
- Live audit after batch30 is unchanged from batch29: exactly 645 unique rows; coverage `100.0=173`, `85.71=108`, `71.43=22`, `57.14=2`, `42.86=275`, `28.57=35`, `0=30`; actions `DATA_REVIEW=512`, `CONDITIONAL_REVIEW=56`, `SELL=42`, `HOLD=3`, `BUY=2`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=598`, `SELL=42`, `HOLD=3`, `BUY=2`; review signals `INCOMPLETE_EVIDENCE=538`, `WORTH_REVIEW=77`, `WAIT_FOR_DATA=30`.
- No public coverage improvement was claimed from batch30. Production root remains 94% used with about 1.6GB free after staging cleanup. The next queue must prioritize symbols where official identity/period evidence can add facts, while keeping independent suffix instruments and fund-model rows behind explicit gates.
- Identity verification for batch30 suffix symbols: the live catalog contains distinct market instrument IDs and ISINs for آبادا3 (`IRO1NBAB0003`), آریا3 (`IRO3APOZ0003`), آسیا3 (`IRO1ASIA0003`), اتکام2 (`IRO1ETKA0002`), اتکام3 (`IRO1ETKA0003`), اردستان3 (`IRO1ARDS0003`) and حکشتی3 (`IRO1KSHJ0003`). Their issuer links are explicit, so merging them into base symbols would be incorrect without a separate official disclosure mapping.
- Latest all-active industry audit after batch30: 1,524 active instruments, 979 issuers with periods, 17,130 financial periods, 65,566 financial facts (32,956 valid), 1,770,316 raw Codal records (1,722,546 linked), and coverage tiers `CORE_READY=537`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=443`, `MISSING_CORE_FACTS=125`. Latest active decisions are `INSUFFICIENT_DATA=1462`, `SELL=56`, `HOLD=4`, `BUY=2`; this broad audit is separate from the public 645-row audit.
- Automatic recovery queue after batch30 is empty for nonfund, non-derived symbols (`selected_symbols=[]`, `attempted_symbols=284`). Derived suffix instruments are now explicitly deferred from automatic retries and can only be retried through `--symbols-file` after identity/parser evidence changes; ETF/fund rows remain behind the separate fund-model gate.
- Final slowdown cleanup: no local or Production ingestion process is active; the stale local `.chrome-codal-profile` (626MB) was removed after process verification. Production staging contains only the retained `ddana-history-20260829` artifact and an empty `auto-sync` directory. Data health, web health and readiness remain green; Production root is 94% used with about 1.6GB free.
- Created and refreshed the symbol-level public evidence audit at `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json`, built from live screener pages 2-14 and the latest all-active authoritative coverage CSV. It verifies 645 unique rows and records current gate counts: `SNAPSHOT_COVERAGE_GAP=280`, `ANALYTICAL_CONFIDENCE_GATE=163`, `MISSING_CORE_FACTS=119`, `MISSING_COMPARABLE_PERIODS=65`, `NO_KNOWN_DATA_GATE=18`. The 322-row snapshot refresh returned HTTP 200 for 321 symbols; `باران` remained HTTP 404. Public coverage is now `100.0=215`, `85.71=276`, `71.43=26`, `57.14=1`, `42.86=77`, `28.57=20`, `0=30`. Latest all-active decisions after refresh: `INSUFFICIENT_DATA=1394`, `SELL=117`, `HOLD=10`, `BUY=3`. SHA-256: `d9508de1276a78a4396e90fd7d82c6bd49cd42a6c9620e92f4fa5422bcc26ea9`.
- Rechecked all 30 public zero-coverage symbols directly through `latest_codal`; every one returned explicit HTTP 404, including باران. They are therefore retained as official report/identity or period/core-fact gates, not as stale snapshots or aliases.
- Explicit parser-recovery retry31 targeted امین، تفیرو، خچرخش، سکرد، غشهد، قنقش، قیستو، لازما، لخانه و ممسنی. The Production backup was `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T110000Z-explicit-retry31.dump`; three manifests imported 31,683 records, including 1,769 standard facts and 200 notice events, with validation errors 0, idempotent replay and green health/healthz/readyz. All ten refreshes returned HTTP 200.
- Live public audit after retry31: exactly 645 unique rows; coverage `100.0=225`, `85.71=276`, `71.43=26`, `57.14=1`, `42.86=77`, `28.57=10`, `0=30`; actions `DATA_REVIEW=357`, `CONDITIONAL_REVIEW=137`, `SELL=108`, `HOLD=9`, `BUY=4`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=524`, `SELL=108`, `HOLD=9`, `BUY=4`; review signals `INCOMPLETE_EVIDENCE=418`, `WORTH_REVIEW=197`, `WAIT_FOR_DATA=30`.
- Latest all-active audit after retry31: `CORE_READY=547`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=443`, `MISSING_CORE_FACTS=115`; decisions `INSUFFICIENT_DATA=1389`, `SELL=121`, `HOLD=10`, `BUY=4`.
- The evidence audit artifact was refreshed at `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json`; current SHA-256 is `ecf271dfccbc23e55cf8a316bc0177cf7b536dfdb575a42e590f149c616dbbf8`. It records the 322-row snapshot refresh, retry31 symbols/import counts, all 645 rows and their current gates.
- Explicit parser-recovery retry32 targeted کلوند، کساوه، وسالت، وشمال، کازرو، نمرینو، کابگن، کهرام، پشاهن و وملت. Production backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T130000Z-explicit-retry32.dump`; three manifests imported 25,647 records, including 1,320 standard facts and 180 notice events, with validation errors 0, idempotent replay, green health/healthz/readyz, and all ten refreshes HTTP 200.
- Live public audit after retry32: exactly 645 unique rows; coverage `100.0=234`, `85.71=276`, `71.43=26`, `57.14=1`, `42.86=77`, `28.57=1`, `0=30`; actions `DATA_REVIEW=349`, `CONDITIONAL_REVIEW=140`, `SELL=113`, `HOLD=9`, `BUY=4`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=519`, `SELL=113`, `HOLD=9`, `BUY=4`; review signals `INCOMPLETE_EVIDENCE=412`, `WORTH_REVIEW=203`, `WAIT_FOR_DATA=30`.
- Latest all-active audit after retry32: `CORE_READY=556`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=443`, `MISSING_CORE_FACTS=106`; decisions `INSUFFICIENT_DATA=1384`, `SELL=126`, `HOLD=10`, `BUY=4`. The public audit artifact was updated with these values; SHA-256: `848e64011ce8b9a7cc303f1095bf6e60b7132062df5b81f16b5a9529e56d2900`.
- Final cleanup after retry32 removed the temporary local Chrome profile and Production auto-sync staging; health/ready remained green and Production root remained 94% used with about 1.5GB free.

## 2026-08-31 - Explicit parser-recovery retry 33

- Target: تنوین، ساروج، ساروم، سفانو، سکرما، سیمرغ، فاما، وبهمن، ولکار و ومدیر. Official CodalPy/browser artifacts were processed with local rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T150000Z-explicit-retry33.dump`.
- Production accepted 50,531 records through three manifests: 12,318 CodalPy rows, 17 normalized facts and 1 notice event were new at import; validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz remained green. No symbol-level orchestrator failure was reported.
- All ten `latest_codal` refreshes returned HTTP 200. Nine symbols reached 100.0% public coverage; ولکار reached 85.71%. ساروج produced the fifth public `BUY`; سکرما remained `HOLD`; وبهمن و ومدیر remained `SELL`; the remaining rows stayed `INSUFFICIENT_DATA`/review-gated where confidence or comparable-period evidence is still insufficient.
- Live public audit remains exactly 645 unique rows: coverage `100.0=243`, `85.71=277`, `71.43=26`, `57.14=1`, `42.86=67`, `28.57=1`, `0=30`; actions `DATA_REVIEW=342`, `CONDITIONAL_REVIEW=143`, `SELL=115`, `HOLD=10`, `BUY=5`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=515`, `SELL=115`, `HOLD=10`, `BUY=5`; review signals `INCOMPLETE_EVIDENCE=405`, `WORTH_REVIEW=210`, `WAIT_FOR_DATA=30`.
- Latest all-active audit: `CORE_READY=561`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=106`; latest decisions `INSUFFICIENT_DATA=1380`, `SELL=128`, `HOLD=11`, `BUY=5`.
- Refreshed evidence artifact: `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json`, SHA-256 `a050283504f7e5b8822a3a1aff249d9cbeb513baf4e532da73326df007e95aa8`. Current public gates are `SNAPSHOT_COVERAGE_GAP=281`, `ANALYTICAL_CONFIDENCE_GATE=175`, `MISSING_CORE_FACTS=100`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=29`.
- Remaining work is evidence/model work, not a silent fallback: 30 public zero-coverage rows still require official report/identity/period evidence, 419 active fund instruments require a sourced NAV/holdings model, and 438 active instruments lack comparable periods. Production root remains 95% used with about 1.5GB free, so each future recovery must remain bounded, backup-first and followed by staging cleanup.

## 2026-08-31 - Explicit parser-recovery retry 34

- Target: حپترو، دزهراوی، آرمان، قرن، لسرما، مهرگان، کایتا، کمینا، کیمیاتک و گکیش. Official CodalPy/browser artifacts were processed with local rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T170000Z-explicit-retry34.dump`.
- Production accepted 42,692 records through three manifests: 6,558 CodalPy rows, 230 normalized records and 140 notice events were inserted; standard facts added were 2,206 and 202 respectively. Validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz remained green.
- All ten `latest_codal` refreshes returned HTTP 200. Eight symbols reached 100.0% public coverage, آرمان reached 71.43%, and حپترو remained 42.86% because its available CodalPy balance-sheet values are `UNIT_UNKNOWN` and its browser recovery did not yield accepted facts. کایتا produced a public `SELL`; no unsupported decision was forced for the other incomplete rows.
- Live public audit remains exactly 645 unique rows: coverage `100.0=251`, `85.71=277`, `71.43=26`, `57.14=1`, `42.86=59`, `28.57=1`, `0=30`; actions `DATA_REVIEW=336`, `CONDITIONAL_REVIEW=148`, `SELL=116`, `HOLD=10`, `BUY=5`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=514`, `SELL=116`, `HOLD=10`, `BUY=5`; review signals `INCOMPLETE_EVIDENCE=400`, `WORTH_REVIEW=215`, `WAIT_FOR_DATA=30`.
- Latest all-active audit: `CORE_READY=569`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=98`; latest decisions `INSUFFICIENT_DATA=1379`, `SELL=129`, `HOLD=11`, `BUY=5`.
- Refreshed evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` has SHA-256 `c335978cd02c865f8c8f9e5d72b4ac51d1f08396b21e0cf62b43f5810361c558`; gates are `SNAPSHOT_COVERAGE_GAP=281`, `ANALYTICAL_CONFIDENCE_GATE=182`, `MISSING_CORE_FACTS=92`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=30`.

## 2026-08-31 - Explicit parser-recovery retry 35

- Target: پکرمان، چاپ، شگستر، دابور، وگستر، غمهرا، شجم، کصدف، غگل و پدرخش. Official CodalPy/browser artifacts were processed with local rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T190000Z-explicit-retry35.dump`.
- Production accepted 46,729 records through three manifests: 138 CodalPy rows and 286 normalized records were inserted, with 2,079 and 270 standard facts respectively plus 200 notice events. Validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz remained green.
- All ten refreshes returned HTTP 200. All ten left the 42.86% public gate and reached 100.0%; پکرمان، وگستر و کصدف produced `SELL`, شجم produced `BUY`, and the remaining symbols stayed evidence-gated without fabricated recommendations.
- Live public audit remains exactly 645 unique rows: coverage `100.0=261`, `85.71=277`, `71.43=26`, `57.14=1`, `42.86=49`, `28.57=1`, `0=30`; actions `DATA_REVIEW=327`, `CONDITIONAL_REVIEW=153`, `SELL=119`, `HOLD=10`, `BUY=6`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=510`, `SELL=119`, `HOLD=10`, `BUY=6`; review signals `INCOMPLETE_EVIDENCE=391`, `WORTH_REVIEW=224`, `WAIT_FOR_DATA=30`.
- Latest all-active audit: `CORE_READY=579`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=88`; latest decisions `INSUFFICIENT_DATA=1375`, `SELL=132`, `HOLD=11`, `BUY=6`.
- Refreshed evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` has SHA-256 `80dc8b364a938463143fc4c376a6b64bc2863880f0d89e219f1522d468d6168f`; gates are `SNAPSHOT_COVERAGE_GAP=281`, `ANALYTICAL_CONFIDENCE_GATE=188`, `MISSING_CORE_FACTS=82`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=34`.

## 2026-08-31 - Explicit parser-recovery retry 36 and current-universe audit

- Target: وتوکا، دماوند، کولان، غانیزان، بگیلان، سپاها، ولتجار، کیمیا، زکشت و سلیم. Official CodalPy/browser artifacts were processed with local rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T210000Z-explicit-retry36.dump`.
- Production synchronized 30,053 records through three manifests: 1,314 CodalPy standard facts, 231 normalized standard facts and 200 notice events were accepted; validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz were green. Symbol failures were empty.
- All ten `latest_codal` refreshes returned HTTP 200. The current public screener universe contains 695 unique rows; all ten retry36 symbols reached 100.0% coverage.
- Current public audit: coverage `100.0=321`, `85.71=277`, `71.43=26`, `57.14=1`, `42.86=39`, `28.57=1`, `0=30`; actions `DATA_REVIEW=332`, `CONDITIONAL_REVIEW=187`, `SELL=128`, `HOLD=12`, `BUY=6`, `NOT_EVALUABLE=30`; decisions `INSUFFICIENT_DATA=549`, `SELL=128`, `HOLD=12`, `BUY=6`; review signals `INCOMPLETE_EVIDENCE=399`, `WORTH_REVIEW=266`, `WAIT_FOR_DATA=30`.
- Latest all-active audit: `CORE_READY=589`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=78`; latest decisions `INSUFFICIENT_DATA=1373`, `SELL=133`, `HOLD=12`, `BUY=6`.
- Refreshed evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records the live 695-row universe; SHA-256 is `d561a890a17a741806b286c11a642a257d21c882071d3c54c674fddeff82c936`. Current gates are `SNAPSHOT_COVERAGE_GAP=281`, `ANALYTICAL_CONFIDENCE_GATE=236`, `MISSING_CORE_FACTS=72`, `MISSING_COMPARABLE_PERIODS=61`, `NO_KNOWN_DATA_GATE=45`.
- Slowdown check: no ingestion process is active; Production remains disk-bound at 95% usage with about 1.5GB free. Further recovery must stay bounded and followed by staging cleanup; active and rollback releases remain retained.

## 2026-08-31 - Deterministic industry-family backfill

- Added `data-service/scripts/backfill_industry_model_families.py`, an idempotent evidence-only backfill that updates an industry row only when the existing official Persian title maps deterministically to an already-supported family; unknown industries remain `unclassified` and receive no invented valuation model.
- Created rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T230000Z-industry-model-families.dump` before the Production database mutation. The dry run found one safe update, and the apply run updated exactly one of 48 industry rows.
- The post-change all-active audit remains `CORE_READY=589`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=78`; decisions remain `INSUFFICIENT_DATA=1373`, `SELL=133`, `HOLD=12`, `BUY=6`. No recommendation was changed by the backfill.
- The public evidence artifact was synchronized with the authoritative post-backfill CSV; its SHA-256 is `5c25e30aada4ed4b61de30cc53c4138075b81262555360692dff0d82fc337bf8`.

## 2026-08-31 - General operating-industry family activation

- Extended the finite deterministic industry map for official operating labels including automotive, agriculture, computing, transport, machinery, utilities, paper, textiles and sugar. These labels use the existing transparent `general-v1` policy scenario; funds, financial industries, unknown labels and malformed identities remain separately gated.
- Promoted the mapping to the active Production data release and restarted `boursnegar-data-service` under systemd. The service recovered successfully; `/health`, `/healthz` and `/readyz` are green. The database backup from `20260831T230000Z-industry-model-families.dump` predates the mutation.
- The authoritative all-active audit remains `CORE_READY=589`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=78`; decisions remain `INSUFFICIENT_DATA=1373`, `SELL=133`, `HOLD=12`, `BUY=6`. No recommendation changed.
- Public evidence artifact synchronized with the post-activation industry CSV; SHA-256 is `d70943b202df4827ebb6853985849215d74110fd5540e7eaf0d3cf7f61e9faa7`.

## 2026-09-01 - Targeted period-evidence recovery retry 37

- Targeted امید، تکاردان، وصنا، ثبهساز، وسپه، وبوعلی، ثامید، لوتوس و انتخاب because their raw Codal ledger contained multiple reports but only one valid comparable period. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T010000Z-explicit-retry37.dump`.
- Production import synchronized 27,941 records through three manifests with 1,106 CodalPy standard facts and 42 normalized standard facts; validation errors were 0, replay was idempotent, staging was removed, and health/healthz/readyz were green. The orchestrator recorded one symbol failure: browser capture for ثبهساز terminated with `AbortError`; it was not counted as a clean recovery.
- Eight successful latest_codal refreshes returned HTTP 200. Public coverage improved to `100.0=323`, `85.71=275`, `71.43=26`, `57.14=1`, `42.86=39`, `28.57=1`, `0=30`; actions are `DATA_REVIEW=328`, `CONDITIONAL_REVIEW=191`, `SELL=128`, `HOLD=12`, `BUY=6`, `NOT_EVALUABLE=30`.
- The authoritative all-active audit remains `CORE_READY=589`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=78`; decisions remain `INSUFFICIENT_DATA=1373`, `SELL=133`, `HOLD=12`, `BUY=6`.
- Refreshed evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` records retry37 and SHA-256 `9b07529812b87ebff034bf4dc988c294bd49b02c97fe896f92b3e4ac4a08f7f2`.

## 2026-09-01 - Browser retry hardening and explicit retry 38

- Hardened `data-service/scripts/browser_codal_fetch.py`: page-side `AbortError`/Runtime evaluation failures now retry twice in a fresh Codal search page, then checkpoint a symbol/page error and continue the batch instead of aborting the whole run.
- Hardened `data-service/scripts/auto_local_to_production.py`: successful symbols can still be imported, but any symbol failure now produces exit code 2, including runs with no new manifests. Added regression coverage for this contract; focused suite is now 30 passing tests.
- Retry38 reprocessed ثبهساز using the hardened browser path with backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260901T030000Z-explicit-retry38.dump`. It synchronized 3,234 records through three manifests, validation errors were 0, replay was idempotent, staging was removed, health/healthz/readyz were green, and the refresh returned HTTP 200. The prior AbortError was not reproduced.
- Retry38 did not change the all-active tier counts or public coverage: public remains `100.0=323`, `85.71=275`, `71.43=26`, `57.14=1`, `42.86=39`, `28.57=1`, `0=30`; all-active remains `CORE_READY=589`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=78`.
- Evidence artifact was refreshed at `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json`; SHA-256 is `ea183694638771951db5cf597ab81a2ab2b96fcee45736afc0116c45057bab22`.

## 2026-09-01 - Core-fact recovery retry 39

- Targeted پاکشو، بکام، پلاسک، لبوتان، قهکمت، لابسا، تکمبا، تکشا، فلامی و قنیشا because the authoritative audit showed missing balance-sheet/core facts despite official raw evidence. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260901T050000Z-explicit-retry39.dump`.
- Production synchronized 125,457 aggregate records through three manifests: 4,325 CodalPy standard facts, 253 normalized standard facts and 200 notice events were accepted; validation errors were 0, replay was idempotent, all ten symbol failures were empty, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. Each targeted symbol reached 100.0% public coverage; public coverage is now `100.0=333`, `85.71=275`, `71.43=26`, `57.14=1`, `42.86=29`, `28.57=1`, `0=30`; decisions are `INSUFFICIENT_DATA=544`, `SELL=133`, `HOLD=12`, `BUY=6`.
- The authoritative all-active audit improved to `CORE_READY=599`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=438`, `MISSING_CORE_FACTS=68`; latest decisions are `INSUFFICIENT_DATA=1368`, `SELL=138`, `HOLD=12`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry39 and SHA-256 `5d239f78b70ae56e37f623353a61328508ab5630009586aa3c28cadf106ed934`. Current public gates are `SNAPSHOT_COVERAGE_GAP=281`, `ANALYTICAL_CONFIDENCE_GATE=241`, `MISSING_CORE_FACTS=62`, `MISSING_COMPARABLE_PERIODS=61`, `NO_KNOWN_DATA_GATE=50`.
- Slowdown check: no recovery process remains active; remote Production is still disk-bound at 95% usage with about 1.4GB free. Keep future recovery batches bounded and retain active/recent rollback releases and backups.

## 2026-09-01 - Comparable-period recovery retry 40

- Targeted ثامید، وتوس، کرمان، اتکای، حآسا، حگهر، توسن، رانفور، زفارس و زگلدشت because they had one valid period while retaining official raw evidence. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260901T070000Z-explicit-retry40.dump`.
- Production synchronized 8,219 records through three manifests: 666 CodalPy standard facts, 6 normalized standard facts and no new notice events; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. One symbol advanced out of the comparable-period gate: the authoritative all-active audit is now `CORE_READY=600`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=68`; latest decisions remain `INSUFFICIENT_DATA=1368`, `SELL=138`, `HOLD=12`, `BUY=6`.
- The live public universe remains 695 rows. Coverage is `100.0=333`, `85.71=275`, `71.43=26`, `57.14=1`, `42.86=29`, `28.57=1`, `0=30`; decisions are `INSUFFICIENT_DATA=544`, `SELL=133`, `HOLD=12`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry40 and SHA-256 `b5c77aef8bd762116c3a093b1017df6b67c5cbdb31d440a7425b88c0dcd1d073`. Current public gates are `SNAPSHOT_COVERAGE_GAP=282`, `ANALYTICAL_CONFIDENCE_GATE=241`, `MISSING_CORE_FACTS=62`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=50`.
- Slowdown check: no recovery process remains active; remote Production remains at 95% disk usage with about 1.4GB free. Future batches must remain bounded and keep rollback releases/backups.

## 2026-09-01 - Comparable-period recovery retry 41

- Targeted وبهمن، ومدیر، تنوین، غویتا، سیمرغ، کگهر، بمپنا، ساینا، مفاخر و ثزاگرس because they had one valid period with official raw evidence. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260901T090000Z-explicit-retry41.dump`.
- Production synchronized 17,041 records through three manifests: 501 CodalPy standard facts; normalized and notice imports were replay-safe with validation errors 0; symbol failures were empty, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. The authoritative all-active tier counts did not change: `CORE_READY=600`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=68`; latest decisions are `INSUFFICIENT_DATA=1366`, `SELL=140`, `HOLD=12`, `BUY=6`.
- The public universe remains 695 rows with coverage `100.0=333`, `85.71=275`, `71.43=26`, `57.14=1`, `42.86=29`, `28.57=1`, `0=30`; decisions are `INSUFFICIENT_DATA=544`, `SELL=133`, `HOLD=12`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry41 and SHA-256 `1cee6d69ed69ef74691ca6c64f59da83a8309d9c2d62150ec82ccded27528d24`. Current public gates are `SNAPSHOT_COVERAGE_GAP=282`, `ANALYTICAL_CONFIDENCE_GATE=241`, `MISSING_CORE_FACTS=62`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=50`.
- Retry41 proves that repeated recovery alone cannot resolve these rows; next work should inspect period identity/quality rejection reasons before another download batch. Remote disk remains at 95% usage with about 1.4GB free.

## 2026-09-01 - Core-fact recovery retry 42

- Targeted بکاب، دفرا، غاذر، قزوین، کگاز، قپیرا، حپترو، غچین، اتکام و ما because each had at least two periods but fewer than seven valid core facts. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260901T110000Z-explicit-retry42.dump`.
- Production synchronized 83,429 records through three manifests: 3,618 CodalPy standard facts, 143 normalized standard facts and 140 notice events; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. Seven symbols advanced out of the core-facts gate. The authoritative all-active audit is now `CORE_READY=607`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=61`; latest decisions are `INSUFFICIENT_DATA=1365`, `SELL=141`, `HOLD=12`, `BUY=6`.
- The public universe remains 695 rows. Coverage is `100.0=339`, `85.71=275`, `71.43=26`, `57.14=1`, `42.86=23`, `28.57=1`, `0=30`; decisions are `INSUFFICIENT_DATA=544`, `SELL=139`, `HOLD=12`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry42 and SHA-256 `7cce5dd1ce8b608140229064d02d2fd7964110ba29e6b54b1c63f1e7898b9ba9`. Current public gates are `SNAPSHOT_COVERAGE_GAP=282`, `ANALYTICAL_CONFIDENCE_GATE=246`, `MISSING_CORE_FACTS=56`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=51`.
- Slowdown check: no recovery process remains active; remote Production remains at 95% disk usage with about 1.4GB free. Future batches must remain bounded and retain rollback releases/backups.

## 2026-09-01 - Core-fact recovery retry 43

- Targeted وشهر، البرز، دانا، شرنگی، پردیس، وامین، وکبهمن، وآفری، وتعاون و کوثر using official CodalPy/browser artifacts. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260901T130000Z-explicit-retry43.dump`.
- Production synchronized 50,203 records through three manifests: 1,004 CodalPy standard facts, 92 normalized standard facts and 60 notice events; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- Nine latest_codal refreshes returned HTTP 200. `وشهر` returned HTTP 404 and is retained as an explicit unresolved symbol gate, not counted as a successful refresh. The authoritative all-active audit improved to `CORE_READY=611`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=57`; latest decisions are `INSUFFICIENT_DATA=1364`, `SELL=141`, `HOLD=13`, `BUY=6`.
- The public universe remains 695 rows. Coverage is `100.0=342`, `85.71=276`, `71.43=27`, `57.14=1`, `42.86=20`, `28.57=1`, `0=28`; decisions are `INSUFFICIENT_DATA=540`, `SELL=136`, `HOLD=13`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry43 and SHA-256 `8457e22bb7f185f41653ae43ae28d35713116cf915be76e2315b7de502b6a929`. Current public gates are `SNAPSHOT_COVERAGE_GAP=283`, `ANALYTICAL_CONFIDENCE_GATE=249`, `MISSING_CORE_FACTS=52`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=51`.
- Slowdown check: no recovery process remains active, staging is empty, and remote Production remains disk-bound at 95% usage with about 1.4GB free. Further batches must remain bounded; `وشهر`, 57 missing-core symbols, 437 comparable-period gaps and 419 fund-model gaps remain open and require distinct evidence/model work.

## 2026-09-01 - Core-fact recovery retry 44

- Targeted وجامی، وسبحان، وآتوس، والماس، وتوسم، وثنو، گوهران، اتکاسا، رایا و معین because official evidence existed but their valid core-fact count was incomplete. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260901T150000Z-explicit-retry44.dump`.
- Production synchronized 3,502 records through three manifests: 144 CodalPy standard facts and 21 normalized standard facts; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. Seven symbols advanced out of the core-facts gate. The authoritative all-active audit is now `CORE_READY=618`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=50`; latest decisions are `INSUFFICIENT_DATA=1364`, `SELL=141`, `HOLD=13`, `BUY=6`.
- The public universe remains 695 rows. Coverage is `100.0=342`, `85.71=283`, `71.43=27`, `57.14=1`, `42.86=20`, `28.57=1`, `0=21`; decisions are `INSUFFICIENT_DATA=540`, `SELL=136`, `HOLD=13`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry44 and SHA-256 `97e3894aeb138fd353fae3374873967a46dd5628e71a648d0a739922bdff4ab8`. Current public gates are `SNAPSHOT_COVERAGE_GAP=290`, `ANALYTICAL_CONFIDENCE_GATE=249`, `MISSING_CORE_FACTS=45`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=51`.
- Slowdown check: no recovery process remains active, staging is empty, and remote Production remains disk-bound at 95% usage with about 1.4GB free. Further batches must remain bounded; 50 missing-core symbols, 437 comparable-period gaps, 419 fund-model gaps and the unresolved `وشهر` 404 remain open.

## 2026-09-01 - Core-fact recovery retry 45

- Targeted میهن، وحافظ، وحکمت، ودی، ورازی، وسرمد، وسین، وفردا، ومعلم و بتیس using official browser/Codal artifacts. The first attempt used two mistyped aliases and was rejected before any server mutation; the corrected run used the active Production symbols. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260901T170000Z-explicit-retry45.dump`.
- Production synchronized 780 records through two manifests: 14 normalized standard facts were accepted; no new CodalPy standard facts or notice events were accepted. Validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. The authoritative all-active audit remained `CORE_READY=618`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=50`; latest decisions remained `INSUFFICIENT_DATA=1364`, `SELL=141`, `HOLD=13`, `BUY=6`. This confirms that raw official documents alone did not provide additional model-eligible facts for this batch.
- The public universe remains 695 rows. Coverage is `100.0=342`, `85.71=283`, `71.43=28`, `57.14=1`, `42.86=20`, `28.57=1`, `0=20`; decisions remain `INSUFFICIENT_DATA=540`, `SELL=136`, `HOLD=13`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry45 and SHA-256 `8e3344ad781d758812cc0fac50883d757d540fbb0821421d5dc5acacc030bbbb`. Current public gates are `SNAPSHOT_COVERAGE_GAP=290`, `ANALYTICAL_CONFIDENCE_GATE=249`, `MISSING_CORE_FACTS=45`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=51`.
- Slowdown check: no recovery process remains active, staging is empty, and remote Production remains disk-bound at 95% usage with about 1.4GB free. Next work should focus on parser rejection reasons/period identity for these unchanged rows before repeating downloads; fund-model and comparable-period gates remain distinct.

## 2026-08-31 - Parser reparse 47

- After the resilient HTML parser fix, 96 existing browser captures belonging to public data-gated symbols were rescanned locally without downloading new documents. Ten symbols produced additional valid normalized facts: بنو، باران، بهامرز، بزندگی، اعتلا، نوین، خودکفا، مهر، سنوین و ومشان.
- The corrected artifacts were promoted with rollback backup `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T023000Z-parser-reparse47.dump`. The import used two manifests and synchronized 392 records, including 21 newly accepted normalized standard facts; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. The all-active tiers remained `CORE_READY=618`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=50`; latest decisions changed to `INSUFFICIENT_DATA=1362`, `SELL=143`, `HOLD=13`, `BUY=6`. This confirms parser recovery without overstating analytical readiness.
- The public universe remains 695 rows. Coverage is `100.0=342`, `85.71=290`, `71.43=30`, `57.14=1`, `42.86=20`, `28.57=1`, `0=11`; decisions are `INSUFFICIENT_DATA=538`, `SELL=138`, `HOLD=13`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records parser reparse47 and SHA-256 `34472786fa6ff6142da18f61e46e851c374c4501d8750b1621d2b4d6b5b5b428`. Current public gates are `SNAPSHOT_COVERAGE_GAP=290`, `ANALYTICAL_CONFIDENCE_GATE=249`, `MISSING_CORE_FACTS=45`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=51`.
- Slowdown check: no recovery process remains active, staging is empty, and remote Production remains disk-bound at 95% usage with about 1.4GB free. Remaining gates require period identity/comparable evidence, proper fund NAV/holdings modeling, and careful review of the 45 public core-fact gaps.

## 2026-08-31 - Core-fact recovery retry 48

- Targeted خلیبل، خمحور، خپارس، کورز، ولراز، واحصا، وطوبی، وفتخار، ویسا و بپیوند because each had two valid periods but fewer than seven valid core facts. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T040000Z-explicit-retry48.dump`.
- Production synchronized 8,211 records through three manifests: 383 CodalPy standard facts, 234 normalized standard facts and 163 notice events; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. Ten symbols advanced out of the core-facts gate. The authoritative all-active audit is now `CORE_READY=628`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=40`; latest decisions are `INSUFFICIENT_DATA=1356`, `SELL=149`, `HOLD=13`, `BUY=6`.
- The public universe remains 695 rows. Coverage is `100.0=350`, `85.71=291`, `71.43=30`, `57.14=1`, `42.86=12`, `28.57=1`, `0=10`; decisions are `INSUFFICIENT_DATA=532`, `SELL=144`, `HOLD=13`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry48 and SHA-256 `7ac77ae229f9d0c003790f3266284d4038121c17fb8c822bb7f71de774c1f0fe`. Current public gates are `SNAPSHOT_COVERAGE_GAP=291`, `ANALYTICAL_CONFIDENCE_GATE=251`, `MISSING_CORE_FACTS=36`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=57`.
- Slowdown check: no recovery process remains active, staging is empty, and remote Production remains disk-bound at 95% usage with about 1.4GB free. Remaining work is distinct model/period evidence work, not a reason to fabricate BUY/HOLD/SELL decisions.

## 2026-08-31 - Core-fact recovery retry 49

- Targeted تماوند، قتربت، پتوسعه، پیزد، بکابل، غنیلی، نبابک، دحاوی، دشیری و چنوپا because each had two valid periods but fewer than seven valid core facts. A typo in the first symbol file was rejected before mutation; the corrected run used active Production symbols. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T060000Z-explicit-retry49.dump`.
- Production synchronized 595 records through two manifests: 200 normalized standard facts and 200 notice events were accepted; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All ten latest_codal refreshes returned HTTP 200. Ten symbols advanced out of the core-facts gate. The authoritative all-active audit is now `CORE_READY=638`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=30`; latest decisions are `INSUFFICIENT_DATA=1353`, `SELL=152`, `HOLD=13`, `BUY=6`.
- The public universe remains 695 rows. Coverage is `100.0=359`, `85.71=291`, `71.43=30`, `57.14=1`, `42.86=3`, `28.57=1`, `0=10`; decisions are `INSUFFICIENT_DATA=529`, `SELL=147`, `HOLD=13`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry49 and SHA-256 `bc1a4c1a89f51f0a5f4a4895b402167b1dc7c8677c915d7e28b52b94df7f96f9`. Current public gates are `SNAPSHOT_COVERAGE_GAP=291`, `ANALYTICAL_CONFIDENCE_GATE=257`, `MISSING_CORE_FACTS=27`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=60`.
- Slowdown check: no recovery process remains active, staging is empty, and remote Production remains disk-bound at 95% usage with about 1.4GB free. Remaining work is 30 core-fact gaps, 437 comparable-period gaps and 419 fund-model gaps, with public coverage gaps kept separate.

## 2026-08-31 - Core-fact recovery retry 50

- Targeted کسعدی، گپارس و گکوثر, the remaining three public non-derived core-fact candidates. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T080000Z-explicit-retry50.dump`.
- Production synchronized 7,402 records through three manifests: 392 CodalPy standard facts, 61 normalized standard facts and 60 notice events; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green.
- All three latest_codal refreshes returned HTTP 200. All three symbols advanced out of the public core-facts gate. The authoritative all-active audit is now `CORE_READY=641`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=27`; latest decisions are `INSUFFICIENT_DATA=1352`, `SELL=153`, `HOLD=13`, `BUY=6`.
- The public universe remains 695 rows. Coverage is `100.0=361`, `85.71=291`, `71.43=30`, `57.14=1`, `42.86=1`, `28.57=1`, `0=10`; decisions are `INSUFFICIENT_DATA=528`, `SELL=148`, `HOLD=13`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry50 and SHA-256 `56826d25dfd2b67b1d8f5ebea58e07af93ced1a4309444dd6c4856f1907b9365`. Current public gates are `SNAPSHOT_COVERAGE_GAP=291`, `ANALYTICAL_CONFIDENCE_GATE=258`, `MISSING_CORE_FACTS=25`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=61`.
- Slowdown check: no recovery process remains active, staging is empty, and remote Production remains disk-bound at 95% usage with about 1.4GB free. The public core-fact queue is now materially reduced; remaining work is comparable-period evidence, 27 all-active core gaps, fund-model support and snapshot coverage.

## 2026-08-31 - Comparable-period recovery retry 51

- Targeted خکاوه، ساوه، فافزا، فجوش، قاسم، ولانا و کی بی سی because each had ten valid facts but only one valid comparable period. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T100000Z-explicit-retry51.dump`.
- Production synchronized 392 records through two manifests; validation errors were 0, symbol failures were empty, replay was idempotent, staging was removed, and health/healthz/readyz were green. The batch did not add a model-eligible comparable period.
- All seven latest_codal refreshes returned HTTP 200, including the exact internal-space symbol `کی بی سی` after a separate refresh. The authoritative all-active audit remained `CORE_READY=641`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=27`; latest decisions are `INSUFFICIENT_DATA=1350`, `SELL=154`, `HOLD=14`, `BUY=6`.
- The public universe remains 695 rows. Coverage is `100.0=361`, `85.71=291`, `71.43=30`, `57.14=1`, `42.86=1`, `28.57=1`, `0=10`; decisions are `INSUFFICIENT_DATA=526`, `SELL=149`, `HOLD=14`, `BUY=6`.
- Evidence artifact `/home/king/Projects/boursnegar/artifacts/audits/public-645-evidence-audit-20260831.json` now records retry51 and SHA-256 `46c07492fc25f8cc0180d7131a1e35d52ed165e69186b0e2e235e05151dfbd6d`. Current public gates are `SNAPSHOT_COVERAGE_GAP=291`, `ANALYTICAL_CONFIDENCE_GATE=258`, `MISSING_CORE_FACTS=25`, `MISSING_COMPARABLE_PERIODS=60`, `NO_KNOWN_DATA_GATE=61`.
- Slowdown check: no recovery process remains active, staging is empty, and remote Production remains disk-bound at 95% usage with about 1.4GB free. Repeating these seven downloads is not useful without new period evidence; remaining work should prioritize the other public gates and distinct fund-model support.

## 2026-08-31 - Side-by-side parser and browser recovery retry 52

- The Codal Excel parser now scans adjacent label/value pairs across the full row. This fixes side-by-side balance-sheet layouts used by insurance and financial issuers without changing the exact label normalization or first-valid-number policy. Focused regression and integration tests passed: 55 tests, 0 failures.
- A local browser reparse processed 936 normalized records across 24 targeted symbols. Production import was backed up at `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T032500Z-side-by-side-balance-reparse52.dump`; the manifest SHA-256 was `f0f68d4411b4a3acfd79f99827e4e2f7b62595ffa04cf774a218f1316fa491ac`. The replay was idempotent and staging was removed.
- A separate official browser recovery for حپترو، ورازی، وسالت و وشهر produced 76 normalized rows and inserted 64 standard facts. Backup: `/home/king/Projects/boursnegar/artifacts/production-backups/20260831T034500Z-hpatro-browser-recovery52.dump`; manifest SHA-256: `eb7fbd0f4dcb28b000d7d9811671b902fa3f6dc2ebf2c5537d37a32ae518ad8`. The second import inserted 0 rows, health/healthz/readyz stayed green, and temporary staging was removed.
- Latest authoritative all-active audit: `CORE_READY=666`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=2`; decisions: `INSUFFICIENT_DATA=1347`, `SELL=157`, `HOLD=14`, `BUY=6`. The two remaining core gaps are وسالت and وشهر; no formal eligible statement evidence was found for them in the bounded browser attempt.
- Comparable-period gaps remain distinct: 382 symbols have zero valid comparable periods and 55 have one; 353 are derived/suffixed symbols. فجوش yielded only one period, while bounded checks for فن افزار، وثوق و گنگین yielded no formal statement rows. No values, decisions, or fund NAV data were fabricated.
- The public audit artifact was refreshed for the 25 retry52 symbols and records SHA-256 `42378375e83438c240cffabdb3d3341feed9c32cff9c2261e0cc73fd0bb1e564`. The local recovery browser profiles were removed; no recovery process remains active. Production still has about 1.4GB free at 95% disk usage, so future batches must remain bounded and clean staging immediately.

## 2026-08-31 - Industry model-family verification

- The active Production release was checked with `backfill_industry_model_families.py --dry-run`: 48 industry rows were inspected and 0 changes were pending. Active symbols are classified across bank, cement, ceramics, financial, food, fund, general, holding, metals, petrochemical, pharmaceutical and real-estate families; 259 active symbols remain `unclassified` and must not receive an invented valuation model.
- The 419 ETF/fund symbols remain explicitly `fund` and `FUND_MODEL_REQUIRED`. The database has no NAV or holdings fields, so they remain outside company valuation until official NAV/holdings evidence is imported. This is a deliberate evidence gate, not a parser failure.
- Production deployment proof: the active parser file now matches local SHA-256 `71add47677f6c3155c46f7799660923dcf337e25e7bcb734036e0495e5e9f6ba`. The pre-change file backup is `/var/backups/boursnegar/20260831T034307Z-codal-excel-parser-before-recovery52.py`; `boursnegar-data-service` was restarted successfully and `/health` plus `/readyz` returned HTTP 200. Completed staging directories were removed; no ingestion process remains active.
- After the family expansion and refresh audit, the authoritative all-active result is unchanged on readiness (`CORE_READY=666`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=2`) and decisions remain `INSUFFICIENT_DATA=1347`, `SELL=157`, `HOLD=14`, `BUY=6`. Industry mapping now covers 265 `general`, 160 `financial`, 137 `metals`, 172 `unclassified` and the already-supported families. Audit artifacts: `/home/king/Projects/boursnegar/artifacts/audits/coverage-all-active-20260831-recovery52.json` (SHA-256 `92d87a4baa07257ec38ff29cf19198901f4b6532dda2618f37f1f2588faa2a6c`) and its symbol CSV (SHA-256 `87e2599b67fd99e2f4e4663e303715c852fcde300b82f75772e9618eabd0e324`).
- Family-refresh proof: snapshot tables were backed up at `/var/backups/boursnegar/20260831T035125Z-snapshots-before-family-refresh.dump` (SHA-256 `7c686064bb5fa3f6fcd2dc9db7503e0e8b022d3710848d4dd24c37e13d13e716`). A bounded refresh attempted 87 newly classified symbols: 57 returned HTTP 200 and persisted refreshed snapshots; 30 returned the expected 404 no-imported-report gate. Post-refresh audit decisions are `INSUFFICIENT_DATA=1335`, `SELL=167`, `HOLD=16`, `BUY=6`, while readiness tiers remain unchanged. Final artifacts: `/home/king/Projects/boursnegar/artifacts/audits/coverage-all-active-20260831-recovery52-refresh.json` (SHA-256 `585534795d61bb65aa6d7cf63bb1e18494d3b03a700ebac60b1e9c54608fe8d7`) and symbol CSV (SHA-256 `92879e898f02fbce50fb37b97dfddd340c3c3b2c1c76aa7f51b82cf973719e96`).
- Comparable recovery retry53: official browser capture/checkpoint completed for خودکفا، مهر، ومشان، سنوین، اعتلا، حیات و وهامون. Normalization produced 78 records with 0 parser errors, but all seven records represented only 1405/03/31; no new comparable period was present, so no import was performed. Capture manifest SHA-256: `2ea36ba260377781e2b245de19791b868b3151f1eb4c0f998014cfb2d6121815`; normalized manifest SHA-256: `177dc2c74fd7062955a8bb3de812c61feac4a8c71a9f658c284e3325d0b56d0c`. The browser profile was removed and the checkpoint retained for evidence.
- The public audit artifact now also records retry53 with zero imported rows and SHA-256 `5b7852907f5c42948fd915ab8cf958c06735d95288414902d69da4d65a55b0b4`; no coverage or decision was promoted from the duplicate-period capture.
- Formal-evidence retry54 for وشهر and وسالت found official ن-۱۰ statements in the local browser result, but both official Excel endpoints timed out even with a 60-second browser download timeout. HTML normalization added no new balance-sheet facts (0 normalized records in the long retry), so no import or coverage promotion was performed. The public audit records retry54 with SHA-256 `19d53538791a8d919c2186f128c43ed7521c9d8afb3890fbf5a9936c199b84b8`; the remaining gate is evidence-access/quality, not an alias mismatch. Temporary Chrome profiles were removed.

## 2026-08-31 - Official hidden-sheet recovery retry 55

- The local browser fetcher now captures Codal's official `ddlTable=0` balance-sheet view as an additional `html-sheet` artifact when Excel download is unavailable. The parser reads the embedded official `datasource` JSON before falling back to HTML tables; the normalizer processes all captured sheets and excludes explicit subsidiary/group statements from symbol attribution.
- For وشهر, the official 1405/03/31 interim report yielded 7 normalized facts: four income-statement facts and three balance-sheet facts. A nearby Codal result for شرکت گروه توسعه صنایع و معادن شهر, شرکت اب و برق کیش and شرکت مسکن و عمران تجارت آتیه کیش was correctly excluded as subsidiary data.
- Production import used artifact `artifacts/recovery55-sheet-normalized/manifest.json`, inserted 7 `codalpy_records` and 7 model facts, then replayed with `inserted=0` and no validation errors. Rollback backup: `/var/backups/boursnegar/20260831T041440Z-وشهر-recovery55-before-import.dump`, SHA-256 `c15b4cc5d7e862758233b430d5db0a2dd447339a831553919a019ae367e7f773`.
- A fresh `latest_codal` snapshot was persisted for وشهر, but its decision remains `INSUFFICIENT_DATA` because the comparable-period gate is still open. Production health, web health and readiness were all green; staging was removed after import.
- Authoritative all-active audit artifact: `artifacts/audits/coverage-all-active-20260831-recovery55.json` (SHA-256 `7b61f7e7bb398aa87602808049d5db53a144da15c5882626b76fe34e3eb16ccb`) and symbol CSV (SHA-256 `f4beb658de3a46d7daf34cd6d3d74bcb51e6b52d322de15dee44bb414dc55b01`). Tiers improved to `CORE_READY=667`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=1`; latest decisions are `INSUFFICIENT_DATA=1335`, `SELL=167`, `HOLD=16`, `BUY=6`.
- Local verification passed: 72 unit tests, Python syntax compilation and `git diff --check`. Two stale recovery Chrome profiles were removed; the persistent Codal profile and all database backups were retained. The workspace remains large (`artifacts` about 15GB), while the local dev page responds in 8-10ms; no recovery process remains active. Production disk remains the main operational constraint at about 95% usage with about 1.3GB free.

## 2026-08-31 - Core-fact recovery retry 56

- A bounded official-browser attempt targeted وسالت, the only remaining all-active `MISSING_CORE_FACTS` symbol. The fetcher captured the official HTML and attempted the hidden `ddlTable=0` sheet for the available formal notices; the run was stopped after an extended Codal navigation wait once the captured artifacts were sufficient for a bounded conclusion.
- Normalization initially saw 16 rows because the hidden-sheet page repeated the income statement. A deduplication guard now keeps one row per source action, yielding 8 unique facts with 0 parser errors; no new model-eligible balance facts were promoted, avoiding unsupported bank ratios. Artifact manifest: `artifacts/recovery56-وسالت-normalized/manifest.json`, SHA-256 `7cdf6246c0e4830898b9e817036b1624247e84703af7b8280511d4cc8e988d26`.
- No Production mutation was performed for retry56. The temporary Chrome profile and the stuck recovery process were removed; Production health/readiness and staging state from retry55 remain the last verified green state. وسالت therefore remains an explicit evidence/quality gate with `valid_periods=2`, `valid_fact_keys=4`, and no fabricated core facts.
- Follow-up hardening added two guards: the browser fetcher records a hidden sheet only when the returned document contains actual balance-sheet labels, and the normalizer deduplicates repeated source actions across HTML/sheet views. The 72-test suite and `git diff --check` remain green after these changes.

## 2026-08-31 - Browser period-identity repair retry 57

- Audit confirmed 6,707 `browser/codal.ir` financial periods; 76 had a `length_months` inconsistent with the official disclosure title. A repair script was added with a dry-run gate, advisory lock and per-row savepoints.
- Production backup: `/var/backups/boursnegar/20260831T042848Z-browser-period-lengths-before-repair.dump`, SHA-256 `a73a70d2940e70c6ed8900b62884f2f357af0043829f7fc275aa74e1f8f21774`.
- The repair changed 8 safe rows. 68 rows conflicted with an existing unique period identity and were skipped without deletion or merge; they remain explicit duplicate-period review gates. Health/readiness stayed green.
- Future browser normalization now carries `period_length_months` directly from the official title, preventing the search window from becoming the accounting period length. The post-repair audit remained `CORE_READY=667`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=1`; no decision was fabricated.
- Audit artifacts: `artifacts/audits/coverage-all-active-20260831-recovery57.json` SHA-256 `a4275460139cb7fdde1b4a2a9fcbcb15cf097be79c3d54cd37b2c92d807ed058` and CSV SHA-256 `f4beb658de3a46d7daf34cd6d3d74bcb51e6b52d322de15dee44bb414dc55b01`.

## 2026-08-31 - Duplicate-period quarantine retry 58

- The 68 remaining period-length conflicts were compared with their canonical same-issuer, same-end-date, same-scope and same-disclosure-version periods. All 68 had overlapping facts, so no facts were moved and no period was deleted.
- Where the duplicate fact sets were exactly identical, 155 duplicate `VALID` facts were downgraded to `DATA_REVIEW`; 37 non-identical duplicate sets remain untouched for manual evidence review. The operation was protected by the prior rollback dump `/var/backups/boursnegar/20260831T043514Z-browser-period-merge-before.dump` (SHA-256 `a73a70d2940e70c6ed8900b62884f2f357af0043829f7fc275aa74e1f8f21774`).
- Post-quarantine audit artifact `artifacts/audits/coverage-all-active-20260831-recovery58.json` has SHA-256 `43a0d813d48b7644bf0bd094ae54b8fe24f879debe3fbdd3649d211c0d7e6965`; CSV SHA-256 `36d956a85f616e57ec24ca139eea02f1b5d0b082d59ed34105b27da6ff150293`. Readiness and decisions were unchanged: `CORE_READY=667`, `MISSING_CORE_FACTS=1`, `MISSING_COMPARABLE_PERIODS=437`, `FUND_MODEL_REQUIRED=419`, with `INSUFFICIENT_DATA=1335`, `SELL=167`, `HOLD=16`, `BUY=6`.
- The 75-test suite and diff checks remain green. The 37 non-identical duplicate sets, one missing-core bank symbol, 437 comparable-period gates, 419 fund-model gates and 185 unclassified industries remain explicit; no values or decisions were fabricated.

## 2026-08-31 - Period-quality quarantine and snapshot refresh retry 60

- The 25 symbols affected by invalid browser period identities were refreshed through the internal `latest_codal` analysis endpoint after quarantine. All 25 returned successful snapshot IDs; no Codal HTTP fetch was performed in Production.
- The refresh changed only persisted analytical snapshots. Decisions moved to the evidence-backed current results: `INSUFFICIENT_DATA=1323`, `SELL=177`, `HOLD=18`, `BUY=6`; no BUY/HOLD/SELL was created from missing evidence.

## 2026-08-31 - Non-overlapping period-fact reconciliation retry 62

- The period-conflict repair moved 68 fact rows from invalid-length duplicate periods to their canonical same-disclosure periods, only when the fact key/parser identity was absent in canonical. Values and official browser provenance were preserved; no period or fact row was deleted.
- The prior `DATA_REVIEW` quarantine remained in place for overlapping keys. This recovered the four temporarily exposed core gaps: the authoritative audit returned to `CORE_READY=667`, `MISSING_CORE_FACTS=1`, `MISSING_COMPARABLE_PERIODS=437`, `FUND_MODEL_REQUIRED=419`.
- All 25 affected symbols were refreshed again through the internal analysis endpoint; `refresh_ok=25`, `refresh_fail=0`. Latest decisions remain evidence-backed at `INSUFFICIENT_DATA=1323`, `SELL=177`, `HOLD=18`, `BUY=6`.
- Audit artifacts: `artifacts/audits/coverage-all-active-20260831-recovery62.json` SHA-256 `3766060d483a107d4ac673747b90bc5cc36c064b5400a73e799d8f3b5aa38328` and CSV SHA-256 `4d0be97bf8d75db291ded9ae79e7b9dfac7a542d71c310959ee6e96807f0fb46`. Production health/readiness remained green and staging is empty.
- Post-refresh audit: `CORE_READY=663`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=437`, `MISSING_CORE_FACTS=5`. The four newly exposed core gaps are the expected consequence of removing invalid-period facts from the analytical basis.
- Audit artifacts: `artifacts/audits/coverage-all-active-20260831-recovery60.json` SHA-256 `b6f9e6c8b091bf6571a988b91f4d1b57a882cf1ed673fcf090287bf45f3a94d3` and CSV SHA-256 `c3aa623b15f877987a6e3400ddf625039df0af00f8fa2fbab4c86d45b99ce695`. Production health/readiness remained green and staging is empty.

## 2026-08-31 - Period-conflict diagnosis retry 61

- The remaining 68 period conflicts were diagnosed by canonical period and parser version. They affect 25 symbols; the non-identical differences are concentrated in balance-sheet `total_equity`/`total_liabilities`, with a smaller `total_assets`, `cogs` and operating-cash-flow subset for حپترو.
- The repair report now records canonical period IDs, symbols, fact counts and differing fact keys. No additional database mutation occurred in retry61; the prior `DATA_REVIEW` quarantine remains the only treatment for invalid-period facts.
- This confirms the remaining conflicts are parser/provenance review cases rather than safe period-length updates. They must not be merged by value or used to manufacture comparable periods.

## 2026-08-31 - Comparable-period discovery and multi-sheet fetch hardening retry 63

- A bounded browser discovery checked ten of the 54 non-derived symbols with only one valid period. The first 20 official notices per symbol were inspected; several symbols had prior-period financial disclosures, but the initial capture was dominated by monthly notices and subsidiary disclosures, so no data was promoted from discovery alone.
- A focused official capture for اتکای confirmed that the annual audited notice contains separate Codal tabs for balance sheet, income statement and cash flow. The previous fetcher persisted only a partially rendered selected tab, which could make a complete notice appear analytically incomplete.
- The browser fetcher now waits for a stable rendered document and captures tabs 0 (balance sheet), 1 (income statement) and 9 (cash flow) as separate provenance-preserving HTML artifacts. The normalizer already accepts these `html-sheet-*` documents and deduplicates by tracing number and fact identity.
- The recovered اتکای artifact normalized to the already represented ۱۴۰۴/۰۹/۳۰ annual period; no new comparable period was found and no Production import or snapshot mutation was performed. The remaining 437 comparable-period gates therefore remain unchanged and explicit.
- Validation: Python compilation and the focused 75-test suite passed. Temporary recovery browser processes/profiles were removed; no Production Codal HTTP request was made.

## 2026-08-31 - Comparable-period recovery retry 65

- The official discovery artifacts for 44 remaining one-period symbols were completed. Thirty-one symbols exposed independent 6- or 9-month financial notices in the bounded result set; subsidiary/group disclosures were excluded by title policy.
- A direct browser-only recovery used saved official Codal URLs for nine symbols: افرا، توسن، تکاردان، تکیمیا، حیات، خودکفا، خکاوه، زگلدشت و ساروج. It captured 23 official statement tabs and normalized 67 facts with 0 parser errors. Periods were 1404/06/31 or 1404/09/30 with a title-derived length of 9 months.
- Production preflight showed each target had one valid period. Artifact-only import inserted 67 `codalpy_records` and 67 standard facts under the advisory lock; replay inserted 0 records and reported 0 validation errors. A first backup command was attempted with the wrong PostgreSQL role and produced a zero-byte file; it was not used for rollback and was removed. A valid rollback dump was then created at `/var/backups/boursnegar/20260831T-recovery65-after-import.dump`, size 107,745,280 bytes, SHA-256 `49b1eb59d96e7d2bce72f5cba3c591af9264bbf6285461352b713dd330a4c8ea`.
- Post-import preflight confirmed all nine targets now have two valid periods. All nine were refreshed through the internal `latest_codal` endpoint; results were successful and no direct Codal HTTP request was made from Production. `ساروج` produced an evidence-backed `BUY` snapshot; the other refreshed decisions remained `INSUFFICIENT_DATA` because their remaining analytical gates are still explicit.
- Authoritative all-active audit improved to `CORE_READY=676`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=428`, `MISSING_CORE_FACTS=1`. Latest decisions remain `INSUFFICIENT_DATA=1335`, `SELL=167`, `HOLD=16`, `BUY=6`. Artifacts: `artifacts/audits/coverage-all-active-20260831-recovery65.json` SHA-256 `871629934fed168e5ba034db99bd41872fb9e55528fe67f58777372749026a3a`, CSV SHA-256 `04b2b9fc1ef34fba4e9db625b343f2e34abf1a7a074f9b1f7b8410f3b8bda44e`.
- Production `boursnegar-data-service`, `/health`, web `/healthz` and `/readyz` were verified green. Temporary staging and Chrome profiles were removed. Remaining work is 428 comparable-period gates, 419 fund-model/NAV gates, one core-fact gate and 185 unclassified industries; no value or identity was fabricated.

## 2026-08-31 - Comparable-period re-audit and duplicate-safe recovery retry 66

- A second bounded direct-browser batch captured 23 official tabs for ten symbols: آواپارس، اعتلا، انتخاب، بمپنا، تنوین، ساوه، سنوین، سیمرغ، غدیس و غمایه. Normalization produced 78 facts; two non-readable tab payloads were recorded as parser errors and excluded from promotion.
- The source-action preflight found all ten notices already present in `codalpy_records`; the advisory-lock import therefore inserted 0 records and 0 standard facts on both attempts, with 0 validation errors. This confirms duplicate-safe behavior and avoided rewriting existing provenance.
- A fresh audit after the snapshot refresh corrected the prior stale artifact: all ten symbols have two valid periods. Current all-active tiers are `CORE_READY=686`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=418`, `MISSING_CORE_FACTS=1`; latest decisions are `INSUFFICIENT_DATA=1335`, `SELL=167`, `HOLD=16`, `BUY=6`.
- Audit artifacts: `artifacts/audits/coverage-all-active-20260831-recovery66.json` SHA-256 `66714c8beb9296742ed6e871dd6af2ecc68aee6b0f0cbfdc94a3eddff459e32f` and CSV SHA-256 `b758cb00beeb1958467d31e9739229c89682ffdc44ca0b5f3f67cceac773b5bd`. The normalized manifest SHA-256 is `c0c9bd140d682a73da74d21d01780b78301c8f6d79cc917bf73ad0b4a06e633e`.
- The ten symbols were refreshed through the internal `latest_codal` endpoint. Production `/health`, web `/healthz` and `/readyz` remained green; temporary staging and browser profiles were removed. No Production Codal HTTP request, fabricated value or identity was used.

## 2026-08-31 - Comparable-period recovery retry 67

- A direct browser-only recovery used previously discovered official Codal URLs for 11 symbols: غویتا، فافزا، فبستم، قاسم، مفاخر، نطرین، وبوعلی، ولانا، وهامون، کاریز و کی بی سی. It captured 30 official statement tabs and normalized 90 facts with 0 parser errors.
- The source-action preflight showed these notices were not present in Production. The existing verified rollback dump `/var/backups/boursnegar/20260831T-recovery66-before-import.dump` was reused because no financial mutation occurred after it was created; SHA-256 `5d39201672b836028b414c388b3cd620402fea99707ccbf5f73f87416d451197`.
- Artifact-only import under the advisory lock inserted 90 `codalpy_records` and 90 standard facts with 0 validation errors. Replay inserted 0 and changed 0, confirming idempotency. All 11 targets now have two valid periods.
- All 11 symbols were refreshed through the internal `latest_codal` endpoint. Their results were evidence-backed; five returned `SELL`, six remained `INSUFFICIENT_DATA` because separate analytical gates remain open.
- Fresh all-active audit: `CORE_READY=697`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=407`, `MISSING_CORE_FACTS=1`; latest decisions `INSUFFICIENT_DATA=1334`, `SELL=168`, `HOLD=16`, `BUY=6`. Artifacts: `artifacts/audits/coverage-all-active-20260831-recovery67.json` SHA-256 `7526843008c355c0e85cf575fb8aea4725d4de01fbddb33efbe2c92e912f33ec`, CSV SHA-256 `0fddbc0ab8b1ac385083e6b23c9a37715a8e8c2c886e678b09b6aee93c443289`; normalized manifest SHA-256 `fe6a847b60ea4d3cde95507c4fc27ccb97cea7509bc5716d8839aa414908391d`.
- Production health, web health/readiness and the 75-test focused suite were green; `git diff --check` passed. Temporary staging/browser profiles were removed. Production disk remains at 99% with about 367MB free, so further imports require the same backup-retention gate; remaining gates are 407 comparable periods, 419 fund models, one core-fact gap and unclassified industries.

## 2026-08-31 - Comparable-period recovery retry 68 and Production retention repair

- The official browser-only recovery for زفارس captured the 1404/03/31 six-month income statement from Codal and normalized/imported 4 facts with 0 replay changes. No balance-sheet sheet was available in the captured payload, so the symbol remains outside core-ready analysis; its comparable-period gate is closed with 2 valid periods.
- Fresh all-active audit after retry68: `CORE_READY=698`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=406`, `MISSING_CORE_FACTS=1`. The audit contains 1,524 active symbols, 69,988 financial facts, 36,070 valid facts, 485,783 valid prices and 1,816,851 linked raw Codal records. Audit artifacts: `artifacts/audits/coverage-all-active-20260831-recovery68.json` SHA-256 `a488de21a3fc8e06a1e3fc41ac9073c74b466cccd223a51a80f7ff210fadf42e`; CSV SHA-256 `39d1957e30fc5d3599511b5b4405c6a39cddd6c2a430b0aa6e7176b60d9fc2b8`.
- Production cleanup approved by the user removed temporary recovery directories, old web/data releases and old auto-local dumps while retaining the active release, recent rollback releases, the latest three auto-local backups, database data and recovery backups. Disk improved from 99%/367MB free to 75%/6.1GB free. Active symlinks remained unchanged.
- Cleanup exposed a stale virtualenv link in the active data release. Before any further audit, the link was repaired to the retained complete environment at `/var/www/boursnegar-data-service.broken/venv`; the incomplete environment was preserved as `/var/www/boursnegar-data-service/venv-incomplete-20260831`. The data service was restarted and `/health` returned `{"status":"ok"}`. Do not remove either environment without a separate rollback plan.
- Current remaining work is evidence-bound: 406 comparable-period gates (550 symbols have zero valid periods and 37 have one), 419 official NAV/holdings model gates for funds, 1 core-fact gate (`وسالت`), and 187 symbols with industry `نامشخص`. No value, decision, coverage or identity was fabricated.

## 2026-08-31 - Historical comparable recovery retries 69-70

- The browser fetcher period filter had a missing `re` import; the failure was caught before any import, patched, and syntax/runtime validation passed. Local orphan linkage was also hardened to skip cleaned/missing artifacts with explicit evidence instead of aborting the entire audit.
- Retry69 searched eight non-fund symbols for current 1405 statements. It completed seven symbols before the bounded timeout and found only current-period notices; no import was promoted from this batch.
- Retry70 repeated the historical window through 1404/12/29 using the official local browser session. It normalized 38 facts with 2 non-readable payloads excluded. Artifact-only import retained 31 official facts for کگهر، کرمان، وتوس و ثزاگرس; کرمان was restricted to its audited consolidated report to avoid counting separate/consolidated views as two comparable periods. Replay inserted 0 changes.
- A valid post-import rollback dump is `/var/backups/boursnegar/20260831T-recovery70-after-import.dump`, 61MB, SHA-256 `686e8edbd9319011007c08ddd04d15886b053b39a23f251a8aeb88875262460f`. The earlier zero-byte `20260831T-recovery70-before-import.dump` was not used as a backup and must not be treated as rollback evidence.
- All four targets now have `valid_periods=2`, `valid_fact_keys=10`, and `CORE_READY`. `وتوس` refreshed to `SELL`; the other three remain `INSUFFICIENT_DATA` for separate evidence gates. Fresh audit: `CORE_READY=702`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=402`, `MISSING_CORE_FACTS=1`. Decisions: `INSUFFICIENT_DATA=1336`, `SELL=166`, `HOLD=16`, `BUY=6`. Artifacts: `artifacts/audits/coverage-all-active-20260831-recovery70.json` SHA-256 `ff8e0d2c1f5741be8e519e0af09cf38792137db70486f82746d3bb5da7c3353e`; CSV SHA-256 `89235f090ae1059b5b8b3937f9d27e5564a5bc5598fad54a71f01a2e85b3989b`.
- Production data service, web health/readiness, disk at 75% usage with 6.2GB free, focused 75-test suite and `git diff --check` remain green. No Production Codal HTTP request, fabricated value, or identity was used.

## 2026-08-31 - Historical comparable recovery retries 71-72

- Retry71 imported 30 official browser facts for حآسا (audited 6- and 9-month reports) and حگهر (audited 9-month report); duplicate-safe replay inserted 0. Both symbols were refreshed and now have comparable evidence, while `اتکای` had no extractable historical financial statement in the bounded window.
- Retry71 backup: `/var/backups/boursnegar/20260831T-recovery71-before-import.dump`, SHA-256 `bd321af062fe415be820e4dd848e5bd372b7821b9df3bd5ca41651f1f78569bd`. Audit: `artifacts/audits/coverage-all-active-20260831-recovery71.json` SHA-256 `955553ca3b0770b1ea42c4585dcb1e564b146c04b1247a4786ded82da2233feb`; CSV SHA-256 `1290b5f147b8ea269ddfc59c74942b5ab2534a1a665a6ddaba190f3560d7871b`. Tiers were `CORE_READY=704`, `MISSING_COMPARABLE_PERIODS=400`, `FUND_MODEL_REQUIRED=419`, `MISSING_CORE_FACTS=1`.
- Retry72 historical fetch was bounded to seven symbols. Only کفرآور completed before the timeout; its official 1404/08/30 three-month report normalized to 10 facts, imported under the lock with replay 0, and refreshed without issuing a decision from incomplete evidence. The other six symbols remain checkpointed and were not partially promoted.
- Retry72 backup: `/var/backups/boursnegar/20260831T-recovery72-before-import.dump`, SHA-256 `a72b3d90378bd24448bb44ea08c8e8550a7e332ac9fec7d5a2d3beab76af19a8`. Fresh audit: `artifacts/audits/coverage-all-active-20260831-recovery72.json` SHA-256 `bfaed953a09502a684a12ea4e04952fdb829be3b01f8dfcceb4837808ef71f63`; CSV SHA-256 `e05ef4e16b46003cfed57a4743b6ee98e445c1b6e5e88df24a252eddbdd4de3d`. Tiers are `CORE_READY=705`, `MISSING_COMPARABLE_PERIODS=399`, `FUND_MODEL_REQUIRED=419`, `MISSING_CORE_FACTS=1`; latest decisions are `INSUFFICIENT_DATA=1337`, `SELL=165`, `HOLD=16`, `BUY=6`.
- The 399 comparable-period gaps, 419 fund NAV/holdings gates, one core-fact gate (`وسالت`) and 194 `نامشخص` industry rows remain explicit. Recovery artifacts retain official provenance and search checkpoints; no Production Codal HTTP request, fabricated value, coverage or identity was used.

## 2026-08-31 - Comparable recovery retry 72 continuation

- The historical checkpoint was continued for کمرجان and مهر. کمرجان completed search with no extractable eligible statement facts; مهر reached the bounded browser timeout before a completed record and produced no import candidate. Both remain explicit recovery gates in `artifacts/recovery72-period-browser/checkpoint.json` and no Production mutation was performed.
- Final local verification after the continuation: no recovery Chrome/fetch process remains; the 77-test focused suite and `git diff --check` pass. Production data health, web health and readiness are green. Disk is 77% used with 5.7GB free after retaining the new rollback backup.

## 2026-08-31 - Period-aware normalizer hardening and retry 74

- The central parser now exposes `derive_period_start_jalali(end,length)` and both browser normalizers use it. The Chrome search range is retained under `payload.capture_range`; it is no longer passed as the accounting start date. This prevents a search-window date from corrupting financial-period identity for 3-, 6-, 9- and 12-month reports.
- Production deployment proof: active parser SHA-256 `5eb5ab58276244fbcce0848c451c8d0a395b98458580eb404cf69ba24a38595b`; rollback file `/var/backups/boursnegar/20260831T-parser-period-aware-before-deploy.py` SHA-256 `71add47677f6c3155c46f7799660923dcf337e25e7bcb734036e0495e5e9f6ba`. The data service restarted successfully and parser import plus `/health` passed.
- Retry74 searched `وصنا` in the historical window. It completed with no extractable eligible financial statement facts, so no import or snapshot mutation occurred. Its checkpoint is retained at `artifacts/recovery74-period-browser/checkpoint.json`.
- Focused validation now passes 83 tests, Python compilation and `git diff --check`. The latest authoritative data audit remains recovery72: `CORE_READY=705`, `MISSING_COMPARABLE_PERIODS=399`, `FUND_MODEL_REQUIRED=419`, `MISSING_CORE_FACTS=1`; the next recovery must continue from the saved browser checkpoints.

## 2026-08-31 - Comparable recovery retries 75-76

- Historical browser recovery for ومشان and امید completed without an eligible financial-statement document or normalized fact. Both runs were kept as explicit zero-evidence gates; no Production import, snapshot mutation or inferred value was made.
- Their checkpoints are `artifacts/recovery75-period-browser/checkpoint.json` and `artifacts/recovery76-period-browser/checkpoint.json`. No recovery browser process remains active.
- Production data service, web health/readiness, parser deployment and the 83-test suite remain green. The authoritative coverage audit is still recovery72 because retries 75-76 produced no data: `CORE_READY=705`, `MISSING_COMPARABLE_PERIODS=399`, `FUND_MODEL_REQUIRED=419`, `MISSING_CORE_FACTS=1`.

## 2026-08-31 - Comparable recovery retries 77-78

- Historical official-browser recovery for ساینا and غگیلا completed with search checkpoints but no extractable eligible financial-statement documents. Both remain explicit no-evidence gates; no values, periods, snapshots or decisions were promoted.
- Checkpoints: `artifacts/recovery77-period-browser/checkpoint.json` and `artifacts/recovery78-period-browser/checkpoint.json`. No recovery process remains active.
- Production health/readiness and parser deployment remain green; 83 focused tests and `git diff --check` pass. Latest authoritative audit remains recovery72: `CORE_READY=705`, `MISSING_COMPARABLE_PERIODS=399`, `FUND_MODEL_REQUIRED=419`, `MISSING_CORE_FACTS=1`.

## 2026-08-31 - Artifact-based comparable recovery retry 79

- A previously captured official Codal artifact for اتکای was reprocessed after the browser batch had missed its completed document. The audited/linked annual statement ending 1404/09/30 normalized to 7 model facts; its search-range date was replaced by the derived 12-month start 1403/10/01 while the original capture range remained in provenance.
- Production preflight backup: `/var/backups/boursnegar/20260831T-recovery79-before-import.dump`, SHA-256 `21c555596e274665ba02d5cad7ed854cf528788cff8d60a3976dcf53deb08664`. Artifact-only import inserted 7 records/facts, replay inserted 0, and the internal latest-codal snapshot refresh completed with `INSUFFICIENT_DATA` because other analytical gates remain explicit.
- Fresh audit: `artifacts/audits/coverage-all-active-20260831-recovery79.json` SHA-256 `31db2e7f681cbe2ef2eff8f12ec7bd37af8ae8e07cf4e63f04b9b3c47a172804`; CSV SHA-256 `ada7847f705ae608bd28906dda3b76a8d423141336f114189a62096f15345e01`. Tiers improved to `CORE_READY=706`, `MISSING_COMPARABLE_PERIODS=398`, `FUND_MODEL_REQUIRED=419`, `MISSING_CORE_FACTS=1`; latest decisions are `INSUFFICIENT_DATA=1337`, `SELL=165`, `HOLD=16`, `BUY=6`.
- The 398 comparable-period gates, 419 fund NAV/holdings gates, one core-fact gate (`وسالت`) and 195 `نامشخص` industry rows remain explicit. Production health/readiness and the 83-test suite remain green; no direct Production Codal request or fabricated value/identity was used.
## 2026-08-31 - گیت مستقل مدل صندوق‌ها

- بررسی artifactهای رسمی صندوق‌ها نشان داد گزارش‌های موجود عمدتاً «صورت وضعیت پورتفو» و گزارش فعالیت ماهانه‌اند و به‌تنهایی NAV رسمی، ارزش روز کامل دارایی‌ها، بدهی/وجه نقد و تعداد واحدهای هم‌دوره را به‌صورت قابل اتکا فراهم نمی‌کنند.
- در `snapshot_v2` برای خانواده `fund` خروجی مستقل `FUND_MODEL_REQUIRED` اضافه شد: ارزش‌گذاری شرکتی روی صندوق اعمال نمی‌شود، تصمیم همیشه `INSUFFICIENT_DATA` می‌ماند و چهار شواهد لازم برای مدل NAV در payload ثبت می‌شود.
- تست محلی snapshot و مدل صنعت: ۲۹ تست موفق؛ فایل فعال Production با backup `/var/backups/boursnegar/20260831T-fund-model-before-deploy.py` منتشر شد. checksum فایل local و Production برابر `d51a1bab4ef28de27ac154f8b6aac27efcd043521ca88ff81539de9eb90d05a9` و health سرویس `ok` است.
- گیت باقی‌مانده صندوق‌ها اکنون صریح و قابل ممیزی است: استخراج NAV و holdings رسمی، سپس migration/import idempotent و refresh snapshot. تا آن زمان عدد، محدوده خرید/فروش یا سیگنال ساختگی تولید نمی‌شود.

## 2026-08-31 - Production audit مستقل پس از انتشار مدل صندوق

- ممیزی مستقیماً روی دیتابیس Production اجرا و CSV آن در `artifacts/audits/coverage-all-active-20260831-production-current.csv` ذخیره شد؛ ۱۵۲۴ ابزار فعال، ۱۷۸۲۶ دوره مالی، ۷۰۰۶۶ fact خام، ۳۶۱۴۸ fact معتبر و ۴۸۵۷۸۳ قیمت معتبر ثبت شد.
- tierهای فعلی بدون تغییر نسبت به recovery79 تأیید شدند: `CORE_READY=706`، `FUND_MODEL_REQUIRED=419`، `MISSING_COMPARABLE_PERIODS=398` و `MISSING_CORE_FACTS=1`. تصمیم‌های ذخیره‌شده: `INSUFFICIENT_DATA=1337`، `SELL=165`، `HOLD=16` و `BUY=6`.
- checksum ممیزی Production برابر `ada7847f705ae608bd28906dda3b76a8d423141336f114189a62096f15345e01` است. health سرویس `ok`، وضعیت systemd `active` و فضای آزاد دیسک حدود ۵٫۶GB است.
- این ممیزی ثابت می‌کند وضعیت قبلی stale نیست، اما هدف هنوز کامل نشده: ۳۹۹ گیت غیرصندوق باید با recovery رسمی یا ثبت دلیل ناتوانی تعیین تکلیف شوند و ۴۱۹ صندوق به شواهد NAV/پورتفو و مدل مستقل نیاز دارند.

## 2026-08-31 - Refresh snapshotهای ناقصِ public 645

- برای هر ۲۹۶ نماد دارای `SNAPSHOT_COVERAGE_GAP`، قبل از mutation از جداول snapshot/valuation/recommendation پشتیبان custom گرفته شد: `/var/backups/boursnegar/20260831T-public645-snapshot-refresh-before.dump` با SHA-256 `6389eb39f439a5816611425bfae6087fcaef86d5486a9a6fa284385c413d87da`.
- refresh فقط از endpoint داخلی data-service و facts واردشده استفاده کرد؛ هیچ درخواست Codal از Production انجام نشد. هر ۲۹۶ نماد موفق شدند؛ دو timeout اولیه (`شگل` و `خکار`) در retry جداگانه موفق شدند. checkpoint نهایی `artifacts/audits/public-645-snapshot-refresh-20260831.json` با SHA-256 `f3d74949f68d5eb55125ee6c8d7e52d450ae595c0f23d3a471cf4eb999745f91` است.
- پوشش پس از refresh همچنان `100%=336`، `85.71%=292`، `71.43%=6`، `57.14%=1`، `28.57%=1` و `0%=9` ماند؛ بنابراین گیت پوشش برای این batch stale نبود و کمبود evidence واقعی است.
- refresh با بازبینی تصمیم‌ها، تعداد فروش را در universe از ۱۵۲ به ۸۸ کاهش داد و `INSUFFICIENT_DATA` را به ۵۴۹ رساند؛ audit عمومی جدید JSON با SHA-256 `4754520441d249fc65addebab06823e5e662f91fe1956e9d3659126781616062` و CSV با SHA-256 `4274945020e45faf6c488a9e2215586b77bdf494a349fd2acb096226abdc9119` ثبت شد.

## 2026-08-31 - بازسازی دقیق audit عمومی 645 نماد

- صفحات ۲ تا ۱۴ API عمومی با ۱۳ درخواست موفق و بدون تکرار، دقیقاً ۶۴۵ نماد خارج از صفحه اصلی را برگرداندند؛ فیلد total سرویس همچنان ۶۹۵ است و به‌تنهایی نباید برای هدف خارج از صفحه استفاده شود.
- audit جدید با تطبیق هر نماد با ممیزی all-active ساخته شد: `artifacts/audits/public-645-evidence-audit-20260831-current.json` با SHA-256 `de2e5d3fd93ff426bedfa8f06235e9145e0cd6ef7f7fce61c5e2b4313021afed` و CSV متناظر با SHA-256 `cf03c60a0c85d100432c23b5cf18f3524fe295a41fba19c5225a960133193daa`.
- گیت‌های فعلی همین ۶۴۵ نماد: `SNAPSHOT_COVERAGE_GAP=296`، `ANALYTICAL_CONFIDENCE_GATE=258`، `MISSING_COMPARABLE_PERIODS=23`، `MISSING_CORE_FACTS=1` و `NO_KNOWN_DATA_GATE=67`. پوشش: ۳۳۶ ردیف ۱۰۰٪، ۲۹۲ ردیف ۸۵٫۷۱٪، ۶ ردیف ۷۱٫۴۳٪، یک ردیف ۵۷٫۱۴٪، یک ردیف ۲۸٫۵۷٪ و ۹ ردیف صفر.
- تصمیم‌های فعلی این universe: `SELL=152`، `HOLD=15`، `BUY=6` و `INSUFFICIENT_DATA=472`. این اعداد snapshot فعلی را گزارش می‌کنند و به‌معنای توصیه شخصی سرمایه‌گذاری نیستند.

## 2026-08-31 - نمایش عمومی گیت مدل صندوق

- `DecisionReport` اکنون `FUND_MODEL_REQUIRED` و چهار نیازمندی NAV/پورتفو را به‌صورت خوانا در گزارش نماد نمایش می‌دهد؛ مدل شرکت و محدوده خرید/فروش برای صندوق‌ها همچنان عمداً نمایش داده نمی‌شود.
- typecheck و ۷۲ تست وب موفق شدند. bundle تولیدی با SHA-256 `c001229652549fe55713022f5319554baf21113f24b004f0c3b3fd249b3842a0` در release `/var/www/boursnegar-releases/20260831T-fund-model-ui` منتشر شد.
- release قبلی حفظ شد، PM2 آنلاین است و `/healthz`، `/readyz` و data-service `/health` همگی سالم هستند. هیچ mutation داده‌ای در این rollout انجام نشد.

## 2026-08-31 - بازیابی رسمی وسالت و ثبت گیت‌های public 645

- در نشست مرورگر محلی، ترازنامه رسمی `وسالت` از اطلاعیه ۹ماهه منتهی به `1404/09/30` استخراج شد. parser سه fact معتبر `total_assets`، `total_liabilities` و `total_equity` تولید کرد؛ خطای normalization صفر بود. شواهد خام در `artifacts/auto-sync/20260831T-vasalat-official-browser.html` و manifest نسخه هم‌تراز در `artifacts/normalized/20260831T-vasalat-official-browser-v2/manifest.json` نگه‌داری شد.
- import artifact-only با backup `/var/backups/boursnegar/20260831T-vasalat-official-before-import.dump` انجام شد: ۳ رکورد و ۳ fact جدید پذیرفته شد، replay دوم `inserted=0` و validation error صفر بود. شناسه منبع ترازنامه با اطلاعیه صورت سود و زیان `1552415` هم‌تراز شد تا موتور گزارش‌های دو اطلاعیه را ترکیب نکند.
- snapshot وسالت بعد از import refresh شد و اکنون پوشش `71.43%` و confidence `36` دارد؛ تصمیم همچنان عمداً `INSUFFICIENT_DATA` است، چون EPS و جریان نقد عملیاتی موجود نیست و مدل صنعت پشتیبانی‌شده ندارد. این recovery گیت را حذف نکرد، بلکه آن را از `MISSING_CORE_FACTS` به `ANALYTICAL_CONFIDENCE_GATE` با دلیل قابل ممیزی تبدیل کرد.
- registry دقیق هر ۶۴۵ نماد در `artifacts/audits/public-645-gate-registry-20260831.json` با SHA-256 `1a5b6282a54adba34cf0e80dcbb1514e9e0bcc40cf8657c2c064b32d3379ddf0` ثبت شد. ۲۳ نماد دارای گیت دوره هم‌قابل‌مقایسه همچنان مشخصاً فهرست شده‌اند؛ برای آن‌ها در artifactهای محلی فعلی دوره رسمی دومِ قابل اتکا پیدا نشد و هیچ داده‌ای جعل یا import نشد.
- وضعیت هدف هنوز کامل نیست: باید recovery رسمیِ ۲۳ گیت دوره‌ای و ۶۷ گیت بدون داده/باقی‌مانده‌های snapshot ادامه یابد و سپس ممیزی all-active و public 645 دوباره از Production تولید و با صحت‌سنجی نهایی ثبت شود.

## 2026-08-31 - ممیزی all-active پس از هم‌ترازی وسالت

- ممیزی مستقیم Production پس از import و refresh نشان داد `وسالت` اکنون `CORE_READY` است: ۲ دوره معتبر، ۷ fact معتبر و پوشش snapshot `71.43%` با confidence `36`. تصمیم همچنان `INSUFFICIENT_DATA` باقی مانده و این دو مفهوم نباید با هم قاطی شوند.
- tierهای all-active به `CORE_READY=707`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=398` رسیدند؛ گیت `MISSING_CORE_FACTS` دیگر وجود ندارد. global audit شامل ۱۵۲۴ ابزار فعال، ۱۷۸۲۸ دوره مالی، ۷۰۰۷۲ fact و ۳۶۱۵۴ fact معتبر است.
- artifactهای ممیزی: `artifacts/audits/coverage-all-active-20260831-after-vasalat.json` با SHA-256 `c1dfe3bf1d3f09047199825ce3a03e4f88faa394edf2dfd3697ba595f0497a24` و CSV با SHA-256 `57b5e38c6ce44a922902a2400fa4f7bc49d2c599c870c0c83db26d0cb2c5f9f5`.
- هنوز ممیزی public 645 باید از داده تازه all-active بازتولید شود؛ سپس recovery نمادهای دارای گیت دوره‌ای و نمادهای بدون شواهد ادامه خواهد یافت.
- نسخه reconciled public 645 پس از این ممیزی در `artifacts/audits/public-645-evidence-audit-20260831-post-vasalat.json` با SHA-256 `88b2d66cbf83eb3f1a9f87b0b16831c27c8f14307be99e3cb77b1a63e74ed94c` ثبت شد: `SNAPSHOT_COVERAGE_GAP=296`، `ANALYTICAL_CONFIDENCE_GATE=259`، `MISSING_COMPARABLE_PERIODS=23`، `NO_KNOWN_DATA_GATE=67` و `MISSING_CORE_FACTS=0`.

## 2026-08-31 - بازیابی artifactهای 53 نماد بدون داده شناخته‌شده

- از manifestهای رسمی browser/codal.ir موجود در Local، برای ۵۳ نماد از ۶۷ نماد، ۱۹۰۷ رکورد normalized معتبر با checksum صحیح جمع‌آوری و بر اساس `(source, source_action_id)` deduplicate شد. ۱۴ نماد artifact معتبر محلی نداشتند و بدون mutation باقی ماندند.
- manifest batch در `artifacts/normalized/no-known-data-recovery-20260831/manifest.json` ثبت شد. import artifact-only با backup `/var/backups/boursnegar/20260831T-no-known-data-recovery-before-import.dump` با حجم ۱۵۲۲۲۶۷۱۲ بایت انجام شد؛ رکورد خام جدید `0` بود، اما ۲۳ fact استاندارد جدید/اصلاح‌شده پذیرفته شد. replay دوم `0` و validation error صفر بود.
- snapshot هر ۵۳ نماد با endpoint داخلی refresh شد؛ checkpoint با ۵۳ موفق و صفر خطا تکمیل شد. هیچ درخواست Codal از Production انجام نشد.
- ممیزی all-active جدید در `artifacts/audits/coverage-all-active-20260831-after-no-known-data.json` با SHA-256 `be13a6f6c2bd7a6b821b751d8562a5c2cbc7fef295063674102c68356f17e8fe` و CSV با SHA-256 `88b629792bd90837ab5914d3e6db4933a23b64a57960edcaaa77be5d068992f9` ثبت شد. tierها همچنان `CORE_READY=707`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=398` هستند؛ تصمیم‌های refreshed: `INSUFFICIENT_DATA=1456`، `SELL=65`، `BUY=1` و `HOLD=2`.
- ۱۴ نماد بدون artifact معتبر محلی: `آواک، اردستان، استقلال، بالبر، بمیلا، تشتاد، تپولا، حفاری، حپترو، ساذری، سمگا، وملی، پارسیان، کانسار`. این‌ها در گیت باقی می‌مانند تا شواهد رسمی از نشست مرورگر محلی به‌دست آید.

## 2026-08-31 - تأیید گیت نمادهای فاقد artifact

- recovery مستقیم و bounded با نشست مرورگر محلی برای `پارسیان، اردستان، استقلال، حپترو` اجرا شد؛ هر چهار manifest صفر رکورد معتبر داشتند و checkpointها در `artifacts/recovery-no-artifact-20260831/` نگه‌داری شدند. هیچ import یا snapshot mutation انجام نشد.
- این نتیجه فقط نبودِ سند قابل‌استخراج در بازه و نشست فعلی را ثابت می‌کند، نه نبود تاریخی اطلاعیه در کدال؛ بنابراین این چهار نماد همچنان نیازمند retry رسمی بعدی هستند و نباید به‌صورت خودکار تصمیم‌پذیر اعلام شوند.
- همین recovery برای ۱۰ نماد دیگر (`آواک، بالبر، بمیلا، تشتاد، تپولا، حفاری، ساذری، سمگا، وملی، کانسار`) نیز اجرا شد؛ هر ۱۰ manifest صفر رکورد معتبر داشتند. اکنون هر ۱۴ نماد فاقد artifact، checkpoint مستقل و قابل ممیزی دارند.
- registry به‌روزشده در `artifacts/audits/public-645-gate-registry-20260831-post-direct-recovery.json` با SHA-256 `0a258bc4d164ed6a8cfb3aeffb20dc73f019d18f1147801b9269421a9ad7f10c` ثبت شد. این ۱۴ مورد همچنان گیت‌اند و فقط با retry رسمیِ بازه/نشست متفاوت یا سند واقعی بعدی قابل ارتقا هستند.

## 2026-08-31 - بازپردازش دوره‌محور و recovery چهار گیت مقایسه‌ای

- normalizedهای قدیمی ۲۳ نماد دارای تاریخ جست‌وجو به‌جای تاریخ شروع دوره بودند؛ import آن‌ها متوقف و ۲۳ capture خام با parser دوره‌محور فعلی دوباره پردازش شد. batch جدید ۳۳۰ رکورد معتبر برای ۱۴ نماد و ۸ خطای غیرمسدودکننده document-level داشت؛ هیچ مقدار ساخته یا اصلاح حدسی نشد.
- artifact batch در `artifacts/normalized/comparable-recovery-20260831/manifest.json` ثبت شد. import با backup `/var/backups/boursnegar/20260831T-comparable-recovery-before-import.dump` انجام شد: ۸ رکورد خام جدید و ۲۸ fact استاندارد پذیرفته شد؛ replay دوم `0` و validation error صفر بود. refresh snapshot هر ۱۴ نماد با ۱۴ موفق و صفر خطا انجام شد.
- ممیزی all-active جدید در `artifacts/audits/coverage-all-active-20260831-after-comparable.json` با SHA-256 `b096779f2beabc7f736bc0752f4617d91fb5401c4bc26203773243056b76ee93` و CSV با SHA-256 `ac46033f227f1cfaaab5d69d316d4647f0835fda3c040cb04fd1844519dc2d83` ثبت شد. tierها به `CORE_READY=711`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=394` رسیدند؛ تصمیم‌های refreshed: `INSUFFICIENT_DATA=1460`، `SELL=61`، `BUY=1` و `HOLD=2`.
- از ۲۳ گیت عمومی، ۴ نماد (`امید، ثباغ، ومدیر، ومشان`) به `CORE_READY` رسیدند. ۱۹ نماد هنوز گیت دوره‌ای دارند: ۹ نماد بدون period معتبر (`وثوق، فن افزار، سفارود، ثقزویح، گنگین، فاهواز، ولاناح، نیروترانسفو، کمرجانح`) و ۱۰ نماد با فقط یک period معتبر (`غگیلا، ثامید، ثبهساز، ساینا، لوتوس، مهر، وبهمن، وسپه، وصنا، کمرجان`).

## 2026-08-31 - recovery دوره تاریخی ثامید و ثبهساز

- بازه تاریخی قبل از `1404/10/01` با فیلتر گزارش ۶ماهه برای `ثامید` و `ثبهساز` بررسی شد. به‌ترتیب ۶ و ۱۲ fact رسمی با دوره صحیح `1403/10/01 تا 1404/03/31` استخراج شد؛ اجرای فیلتر ۱۲ماهه قبلی صفر رکورد داشت و کنار گذاشته شد.
- import artifact-only شامل ۱۸ رکورد با backup `/var/backups/boursnegar/20260831T-comparable-historical-before-import.dump` انجام شد: ۱۸ رکورد و ۱۸ fact جدید، replay دوم `0` و validation error صفر. snapshot هر دو نماد با موفقیت refresh شد.
- ممیزی all-active در `artifacts/audits/coverage-all-active-20260831-after-historical.json` با SHA-256 `a81df231732181d5e9a438f56d0abad33ee7f3a07878acdc8c1b56b99a951d25` و CSV با SHA-256 `a223d80568234dd4225b2a004c2c0c05c2f4c2deee02004106f3cdcbfe44f115` ثبت شد. tierها به `CORE_READY=713`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=392` رسیدند.
- تصمیم‌های فعلی all-active: `INSUFFICIENT_DATA=1460`، `SELL=61`، `BUY=1` و `HOLD=2`. گیت دوره‌ای هنوز برای همه نمادها به‌طور کامل بسته نشده و recovery تاریخی سایر موارد باید ادامه یابد.

## 2026-08-31 - recovery تاریخی batch دوم برای 9 نماد

- بازه تاریخی ۶ماهه برای ۱۰ نماد دارای فقط یک period اجرا شد. برای ۹ نماد (`غگیلا، لوتوس، مهر، وسپه، وصنا، کمرجان، ساینا، ثامید، ثبهساز`) در مجموع ۵۴ fact رسمی با دوره واقعی `1403/10/01 تا 1404/03/31` یا دوره مالی متناظر استخراج شد؛ `وبهمن` سند قابل‌استخراج معتبر نداشت و import نشد.
- import با backup `/var/backups/boursnegar/20260831T-comparable-historical-v2-before-import.dump` انجام شد: ۳۶ رکورد خام و ۳۶ fact استاندارد جدید، replay دوم `0` و validation error صفر. snapshot هر ۹ نماد با موفقیت refresh شد.
- ممیزی all-active جدید در `artifacts/audits/coverage-all-active-20260831-after-historical-v2.json` با SHA-256 `954fb3fc8a7d27a93fb8c238d6722f53944036c410eb7d97ae5598dbb6208e50` و CSV با SHA-256 `75482d5d67a37e02b99b0bc061527735df186323ed477622d1eee73a46ad4a10` ثبت شد. tierها به `CORE_READY=720`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=385` رسیدند.
- تصمیم‌ها تغییری در این ممیزی نداشتند: `INSUFFICIENT_DATA=1460`، `SELL=61`، `BUY=1` و `HOLD=2`. گیت‌های دوره‌ای همچنان باید برای موارد بعدی recovery شوند.

## 2026-08-31 - بررسی نهایی بازه تاریخی 10 گیت باقی‌مانده

- بازه تاریخی ۶ماهه با فیلتر گزارش‌های رسمی برای `وثوق، فن افزار، سفارود، ثقزویح، گنگین، فاهواز، ولاناح، نیروترانسفو، کمرجانح، وبهمن` اجرا شد. برای هر ۱۰ نماد manifest و checkpoint مستقل ثبت شد؛ normalization دوره‌محور برای همه صفر رکورد معتبر تولید کرد و هیچ import یا snapshot mutation انجام نشد.
- اجرای `فن افزار` ابتدا به‌علت فاصله نام نماد به دو ورودی شکسته شد؛ اجرای صحیح با نام کامل بلافاصله تکرار و با صفر رکورد پایان یافت. این خطای اجرایی اثری روی Production نداشت.
- این batch گیت‌ها را حذف نکرد؛ شواهد فعلی کافی نیست و تصمیم درست، نگه‌داشتن `MISSING_COMPARABLE_PERIODS` و retry با نشست/بازه متفاوت است، نه پر کردن دوره با داده تخمینی.

## 2026-08-31 - refresh کامل public 645 پس از recoveryهای نهایی

- refresh داخلی هر ۶۴۵ نماد خارج از صفحه اصلی اجرا شد: ۶۳۶ موفق و ۹ پاسخ صریح `404 / گزارش واردشده‌ای موجود نیست` (`وثوق، فن افزار، سفارود، ثقزویح، گنگین، فاهواز، ولاناح، نیروترانسفو، کمرجانح`). checkpoint در `artifacts/audits/public-645-final-refresh.json` با SHA-256 `65bbac9b616939af4191eee06d9063c97b45a9b4e1db7fad2e6542745dddf656` ثبت شد.
- registry نهایی هر ۶۴۵ نماد در `artifacts/audits/public-645-gate-registry-20260831-final-refresh.json` با SHA-256 `41d636d1f413b63fbdfbb7297167c7ca371cd71ad91eaeb23b96da036d502902` ثبت شد؛ شامل وضعیت refresh، tier all-active، دوره‌های معتبر و اقدام بعدی است.
- ۹ پاسخ 404 گیت داده باقی ماندند؛ هیچ fallback، identity جعلی یا درخواست مستقیم Codal از Production استفاده نشد. سایت و data-service باید فقط بر اساس همین وضعیت evidence-first تصمیم‌پذیری را محدود کنند.

## 2026-08-31 - صحت‌سنجی ساختاری registry عمومی

- registry public 645 از نظر count، یکتایی نماد، وجود gate، وضعیت refresh، tier و next action کامل است: ۶۴۵ نماد یکتا، ۶۳۶ refresh موفق، ۹ `no_stored_report_404`، و بدون فیلد ضروری مفقود.
- در این universe، tier all-active برای ۶۳۵ نماد `CORE_READY` و برای ۱۰ نماد `MISSING_COMPARABLE_PERIODS` است؛ `FUND_MODEL_REQUIRED` در مجموعه خارج از صفحه اصلی وجود ندارد. این audit صرفاً کامل بودن ثبت و وضعیت evidence را ثابت می‌کند و به‌تنهایی مجوز صدور BUY/SELL نیست.

## 2026-08-31 - اصلاح registry عملیاتی public 645 و بررسی گیت‌های باز

- ممیزی read-only زنده در 2026-08-31T09:11Z نشان داد Production سالم است: `/healthz` و `/readyz` وب و `/health` سرویس داده سبز هستند، observer با `disk=83% rows=50 coverage=100%` پاس شده، و DB زنده شامل 1,524 ابزار فعال، 17,847 دوره مالی، 70,134 fact مالی و 36,216 fact معتبر است.
- tier زنده Production با آخرین artifact هم‌خوان است: `CORE_READY=720`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=385`. همه ابزارهای فعال snapshot دارند؛ تصمیم‌های latest روی ابزار فعال `INSUFFICIENT_DATA=1472`، `SELL=51` و `HOLD=1` است. این اعداد توصیه شخصی سرمایه‌گذاری نیستند.
- symlink وب روی `/var/www/boursnegar-releases/20260831T-fund-model-ui` است، اما PM2 هنوز cwd/script release قدیمی‌تر `/var/www/boursnegar-releases/20260830T050000Z-account-admin-polish` را نشان می‌دهد. checksum `dist/server.cjs` در هر دو release برابر است، اما برای ادعای UI باید asset/DOM واقعی مرورگر مبنا باشد.
- اسکریپت `data-service/scripts/reconcile_public_gate_registry.py` اضافه شد تا `gate` عملیاتی را از `all_active_coverage_tier` و وضعیت refresh بازسازی کند و مقدار قبلی را در `source_gate` نگه دارد. تست جدید آن در `data-service/tests/test_reconcile_public_gate_registry.py` ثبت شد.
- registry عملیاتی جدید در `artifacts/audits/public-645-gate-registry-20260831-operator-v2.json` با SHA-256 `47d0ed0b7f140df4de49d32c54122ac914f4225ad0b29ab2e1096823cd79d245` و CSV متناظر با SHA-256 `587e0314e177c79113a67086df0d968b9cfe120101fe811e7bd4a11013b2a33a` ساخته شد. شمارش gate عملیاتی: `SNAPSHOT_COVERAGE_GAP=300`، `ANALYTICAL_CONFIDENCE_GATE=264`، `RECOVERY_CLOSED=71`، `NO_KNOWN_DATA_GATE=9` و `MISSING_COMPARABLE_PERIODS=1`.
- ۹ گیت واقعی بدون گزارش ذخیره‌شده باقی هستند: `وثوق، فن افزار، سفارود، ثقزویح، گنگین، فاهواز، ولاناح، نیروترانسفو، کمرجانح`. تنها گیت واقعی دوره دوم در public 645 اکنون `وبهمن` است؛ دوره معتبر آن 1 و fact معتبر آن 10 است.
- بررسی artifactهای `وبهمن` نشان داد در بازه تاریخی فایل خام وجود دارد، اما normalizedهای تاریخی صفر هستند. نمونه اطلاعیه‌های ن-۱۰ قابل مشاهده مربوط به شرکت‌های زیرمجموعه/عنوان‌های غیرقابل‌قبول برای دوره مقایسه‌ای والد هستند، پس import یا تصمیم جدید ساخته نشد. گزارش بررسی در `artifacts/audits/public-645-open-recovery-investigation-20260831.json` با SHA-256 `6e21b325cbfdb85938115656154203026d3571ab2ac4615105caab0f480df864` ثبت شد.
- اعتبارسنجی لوکال پس از این اصلاح: 101 تست Python با venv پروژه پاس، typecheck وب پاس، 72 تست وب پاس، build production پاس و `git diff --check` بدون خطا. هیچ request مستقیم Codal از Production، import، snapshot mutation، داده ساختگی یا هویت ساختگی انجام نشد.

## 2026-08-31 - جلوگیری از ورود گزارش‌های زیرمجموعه به recovery والد

- در بازبینی artifactهای تاریخی `وبهمن` مشخص شد ۷ اطلاعیه `ن-۱۰` قابل‌استخراج، در عنوان خود نام شرکت زیرمجموعه داشتند: اوین، بافکار، اعتبار آفرین، توسعه ساختمانی بهمن، گنجینه ایرانیان، دادوستداریا و گروه صنعتی ایرانیان. نام issuer در metadata «سرمایه گذاری بهمن» بود، اما این اسناد شواهد صورت مالی والد محسوب نمی‌شوند.
- تابع `has_child_entity_qualifier` در parser مشترک اضافه شد و هم normalizer مرورگر و هم انتخاب‌گر گزارش API اکنون عنوان‌های صریحاً متعلق به زیرمجموعه را کنار می‌گذارند. عنوان تلفیقی والد بدون qualifier همچنان مجاز است.
- تست حفاظتی اضافه و موفق شد. بازپردازش محدود capture تاریخی `وبهمن` در `artifacts/normalized/comparable-historical-6m-remaining-20260831/وبهمن-v2/manifest.json` با SHA-256 `dfa1728e7bb02b0db9f10f66f18e8fd8d7f477639d5a101b54674d4c0f098a08` نتیجه `records=0`, `source_documents=0`, `errors=7` داد؛ هر ۷ خطا از نوع `child_entity_financial_statement` هستند.
- این تغییر هیچ import، snapshot mutation یا درخواست Codal از Production ایجاد نکرد. گیت `وبهمن` به‌درستی باز می‌ماند تا صورت مالی رسمی والد با دوره قابل‌مقایسه در artifact مستقل به‌دست آید.

## برنامه آینده - صفحه مستقل نماد و هویت بصری معتبر

- برای هر نماد صفحه مستقل با URL پایدار و قابل ایندکس ایجاد شود؛ صفحه باید گزارش تحلیلی، وضعیت گیت داده و provenance را حفظ کند.
- لینک وب‌سایت رسمی شرکت در صورت وجود منبع معتبر اضافه شود.
- لوگو یا تصویر کوچک شرکت فقط با منبع رسمی/قابل‌تأیید و در سربرگ استفاده شود؛ پس‌زمینه بزرگ پشت داده‌های مالی در برنامه نیست، چون خوانایی و تمرکز کاربر را کاهش می‌دهد.
- این کار بعد از تثبیت گیت‌های داده و با بررسی SEO، Schema، responsive UI و منبع هر تصویر انجام شود؛ هیچ URL یا تصویری حدسی ساخته نشود.

## 2026-08-31 - ممیزی دوباره دسترسی SSH و سرویس‌های Production

- نام مدیریتی ثبت‌شده `srv6626362878` در SSH config تعریف نشده بود؛ alias صحیح محلی `boursnegar` است و به `194.5.175.239` وصل می‌شود. مشکل از قطع SSH نبود.
- ممیزی read-only با alias صحیح: وب روی `/var/www/boursnegar-releases/20260831T-fund-model-ui`، داده روی `/var/www/boursnegar-data-releases/20260830T022500Z-ratio-quality`، PM2 `bourse-app` آنلاین و listenerهای localhost روی 3000 و 8001 فعال هستند. healthz، readyz و data health همگی سبز هستند.
- observer فعال و آخرین اجرا `BOURSNEGAR_OBSERVER=PASS disk=83% rows=50 coverage=100%` بود. فضای آزاد `/var/www` حدود 4.3GB است.
- واحد صحیح داده `boursnegar-data-service.service` فعال است؛ بررسی قبلی `boursnegar-data.service` نام نادرست داشت. با این حال `boursnegar-market-daily.service` در auto-restart، `boursnegar-market-intraday.service` failed و `boursnegar-rahavard-quarantine.service` failed هستند؛ لاگ هر سه علت `Failed to load environment files: No such file or directory` را نشان می‌دهد. `boursnegar-post-backfill-audit-v2.service` نیز با exit code 1 failed است.
- این ممیزی هیچ restart، deploy، import یا تغییر داده‌ای انجام نداد. رسیدگی به فایل‌های environment و jobها نیازمند بررسی مسیر/backup و اقدام جداگانه است.

## 2026-08-31 - رفع توقف به‌روزرسانی قیمت‌های صفحه اصلی

- علت توقف jobهای بازار پیدا شد: `EnvironmentFile=/var/www/boursnegar-data-current/.env` به release فعال اشاره می‌کرد، اما فایل وجود نداشت. فایل معتبر قبلی با DB hashهای همسان، اتصال PostgreSQL موفق و dry-run منبع بازار معتبر شناسایی شد.
- پیش از اصلاح، backup کامل PostgreSQL در `/var/backups/boursnegar/20260831T-market-refresh-before-env-fix.dump` با حجم ۱۵۲۶۶۴۸۲۵ بایت و SHA-256 `276fecc9892f298b9788a383500d54d13760a699f2c29abcdc88a88bc5b173ea` ثبت شد. `.env` با mode `600` در release فعال قرار گرفت و checksum آن با منبع برابر است.
- gate catalog در کد به حداقل ۱۰۰۰ قیمت و mapping حداقل ۸۰٪ تغییر کرد و `mapping_coverage` در metrics ثبت شد؛ داده‌های unmapped همچنان وارد نمی‌شوند. فایل Production با checksum `115bea7ddb7df1a1e1e2df5551ca21c032b417314bf7de814b8f0a1ab353bff2` منتشر و نسخه قبلی با checksum `c790cdc87bc25dd6dbf159a35eebe4dce7cf25331a7e1cedf52ddceedb9ed76a` backup شد.
- اجرای روزانه موفق شد: ۱۶۱۳ quote معتبر، ۱۵۲۵ نماد معامله‌شده، ۱۳۴۶ قیمت mapped و ۲۶۷ مورد unmapped؛ mapping coverage برابر `0.8345`. اجرای intraday نیز موفق شد. dashboard عمومی تاریخ `2026-08-31` و ۶۹۳ نماد دارای قیمت را نشان داد.
- مصرف دیسک Production پس از backup حدود `83%` است: `/var/backups=5.4G`، PostgreSQL حدود `3.0G`، `/var/lib/boursnegar/codalpy/daily=2.0G`، Rahavard quarantine حدود `1.2G` و releaseهای وب/داده حدود `1.2G`. backupها و quarantineها شواهد rollback/provenance هستند و بدون تصمیم retention حذف نشدند.
- علت ریشه‌ای serviceهای market روزانه و intraday رفع شد؛ jobهای Rahavard و audit نیز environment را می‌بینند، اما اجرای سنگین آن‌ها عمداً در این اصلاح شروع نشد. هیچ داده ساختگی، Codal مستقیم از Production یا حذف evidence انجام نشد.

## 2026-08-31 - پاک‌سازی محدود فضای سرور و طرح fallback دریافت Codal

- با تأیید کاربر، فقط virtualenv ناقص و بلااستفاده `/var/www/boursnegar-data-service/venv-incomplete-20260831` حذف شد؛ حدود ۲۳۷MB آزاد شد. فایل موقت انتقال اسکریپت نیز حذف شد.
- backupهای PostgreSQL، release فعال و rollback، artifactهای Codal، داده‌های روزانه و PDFهای Rahavard quarantine حذف نشدند. پس از پاک‌سازی فضای آزاد حدود ۴.۴GB و مصرف دیسک ۸۲٪ شد؛ health وب و data-service سبز باقی ماند.
- معماری دریافت آتی: ابتدا API Codal با quota روزانه، سپس در quota/429/timeout/خطای provider، fallback به مرورگر Local یا ingestion worker. هر دو مسیر باید artifact خام، manifest، checksum، parser status و timestamp یکسان تولید کنند؛ در شکست هر دو مسیر، داده قدیمی تازه فرض نمی‌شود.
- Local Debian برای backfill بزرگ لازم نیست همیشه فعال باشد؛ فقط worker دریافت و اعتبارسنجی Codal است. BRSAPI برای refresh روزانه قیمت روی Production مستقل می‌ماند.

## 2026-08-31 - یکدست‌سازی نهایی مسیرهای Production

- مسیرهای استاندارد تثبیت شدند: وب `/var/www/boursnegar-current`، داده `/var/www/boursnegar-data-current` و runtime ثابت Python `/var/www/boursnegar-runtimes/data-venv`. releaseها فقط از طریق symlinkهای `current` انتخاب می‌شوند.
- PM2 با backup `/var/backups/boursnegar/20260831T-path-unification/pm2.dump.before` و نقشه مسیر قبل از تغییر دوباره ساخته شد؛ اکنون `bourse-app` با `pm_cwd=/var/www/boursnegar-current` و `pm_exec_path=/var/www/boursnegar-current/dist/server.cjs` آنلاین است و `pm2 save` شده تا بعد از reboot همین مسیر بازگردد.
- runtime قبلی در `boursnegar-data-service.broken/venv` به `/var/www/boursnegar-runtimes/data-venv` منتقل شد. shebangهای ۱۵ فایل runtime و واحد `boursnegar-data-service.service` به مسیر ثابت اصلاح شدند؛ process فعلی با `/var/www/boursnegar-runtimes/data-venv/bin/python3` اجرا می‌شود.
- audit process پس از تغییر هیچ process فعالی از release قدیمی وب، `bourse-analyzer` یا مسیر `data-service.broken` نشان نداد. Nginx همچنان فقط به `127.0.0.1:3000` proxy می‌کند و systemd jobهای بازار از `boursnegar-data-current` اجرا می‌شوند.
- timer مربوط به `boursnegar-rahavard-quarantine` با تأیید کاربر disabled شد؛ artifactهای Rahavard حذف نشده‌اند. timerهای market daily، market intraday، observer و alert worker فعال باقی ماندند.
- پس از restart کنترل‌شده data-service، وب و data health/readiness سبز هستند و فضای آزاد دیسک حدود `4.4GB` با مصرف `82%` باقی است. هیچ داده، backup یا provenance حذف نشد.

## 2026-08-31 - تکمیل گیت observer و QA صفحه مستقل نماد

- observer به‌صورت evidence-first اصلاح شد: سلامت وب، data-service، تعداد ردیف‌های screener و موجودبودن coverage بررسی می‌شوند، اما coverage کمتر از ۱۰۰٪ به‌تنهایی سرویس را failed نمی‌کند؛ گیت‌های تحلیلی همچنان در audit و پاسخ نماد باقی می‌مانند.
- نسخهٔ اصلاح‌شده پس از backup در `/var/backups/boursnegar/20260831T143412Z-observer-coverage-gate-fix.sh` روی `/usr/local/sbin/boursnegar-observer` نصب شد. اجرای واقعی Production موفق بود: `BOURSNEGAR_OBSERVER=PASS disk=82% rows=50 coverage_min=42.86 coverage_max=100 coverage_100=43`.
- گیت نهایی Production با نسخهٔ مخزن اجرا و `REMOTE_FINAL_GATE=PASS` ثبت شد؛ اجرای قبلی از مسیر اشتباه release به‌دلیل نبودن اسکریپت در آن release timeout/ناموفق تلقی شده بود و دیگر به‌عنوان شواهد معتبر استفاده نمی‌شود.
- QA مرورگری صفحهٔ `/s/فولاد` در Production موفق بود: عنوان، دادهٔ قیمت، نمودار، snapshot تحلیل، اطلاعیه‌های رسمی، لینک Codal، canonical و structured data حاضر بودند؛ در viewport موبایل ۳۷۵×۸۱۲ نیز متن کامل و بدون overflow افقی رندر شد و خطای کنسول مشاهده نشد.
- اعتبارسنجی Local: ۱۰۲ تست Python، ۷۲ تست وب، typecheck و build موفق شدند. صفحه مستقل نماد از قبل پیاده و اکنون با QA زنده تأیید شد؛ لینک سایت رسمی و تصویر شرکت هنوز فقط پس از وجود منبع معتبر قابل اضافه‌کردن هستند.
- گیت‌های باز واقعی باقی ماندند: ۹ نماد بدون گزارش ذخیره‌شده و ۱۰ نماد با گیت دورهٔ مقایسه‌ای که در recovery فعلی سند معتبر نداشتند؛ E2E moderator/reward نیازمند نشست مجاز واقعی است و بدون هویت ساختگی بسته نمی‌شود. پوشش ناقص به تصمیم قطعی تبدیل نشده است.

## 2026-08-31 - recovery80 و حذف ارجاع‌های Production به runtime قدیمی

- recovery رسمی browser/Codal برای `وبهمن، وسپه، وصنا` در بازهٔ `1403/01/01 تا 1404/09/30` اجرا شد. manifest خام ۳ فایل و ۶۰ رکورد جست‌وجو داشت؛ normalization دوره‌محور ۳۷ رکورد/سند معتبر و ۶ خطای retained تولید کرد. خطاهای وبهمن مربوط به صورت وضعیت پورتفوی شرکت‌های زیرمجموعه بود و وارد facts نشد.
- سه سند والد با دورهٔ قطعی `1403/10/01 تا 1404/03/31` شناسایی شدند: وبهمن ۱۰ fact، وسپه ۲۰ fact و وصنا ۷ fact. manifest نرمال‌شده در `artifacts/recovery80-period-normalized/manifest.json` با SHA-256 `ab5474050e12bced0f1a0b76c3897c322cbbaf8ae4e073c79500947e4afa8545` ثبت شد.
- قبل از import backup `/var/backups/boursnegar/20260831T-recovery80-before-import.dump` با حجم ۱۵۲۸۵۸۷۶۵ بایت ساخته شد. import با checksum و advisory lock انجام شد: `inserted=37` و `standard_facts=37`؛ replay دوم `inserted=0` و بدون validation error بود. refresh داخلی هر سه نماد موفق شد.
- ممیزی all-active تازه در `artifacts/audits/coverage-all-active-20260831-recovery80.json` با SHA-256 `5fe52f404e249e7f1a169edd36b7940c82f2957fff768f6fee3fa84e1c10704b` و CSV با SHA-256 `abfd414cf080eba9b0b13136a338a350ea4b0fcc255656e8bd39ecaa9c302677` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۸۵۵ دوره، ۷۰۱۷۱ fact و ۳۶۲۵۳ fact معتبر. وبهمن `CORE_READY` و `RECOVERY_CLOSED` شد؛ وسپه `CORE_READY` با گیت اطمینان و وصنا `CORE_READY` با پوشش ۸۵٫۷۱٪ باقی ماند.
- registry عمومی ۶۴۵ نماد با ممیزی recovery80 هم‌تراز شد و در `artifacts/audits/public-645-gate-registry-20260831-recovery80.json` ثبت گردید؛ شمارش گیت‌ها: `RECOVERY_CLOSED=14`، `ANALYTICAL_CONFIDENCE_GATE=322`، `SNAPSHOT_COVERAGE_GAP=300` و `NO_KNOWN_DATA_GATE=9`.
- اسکریپت‌های انتقال و واحدهای systemd مخزن از `/var/www/boursnegar-data-current/venv/bin/python` به runtime ثابت `/var/www/boursnegar-runtimes/data-venv/bin/python3` اصلاح شدند؛ مسیر قدیمی دیگر در فایل‌های اجرایی Production مخزن استفاده نمی‌شود. تست Python پس از اصلاح ۱۰۲ مورد موفق بود.
- ممیزی Production نشان داد unitهای نصب‌شده هنوز نسخهٔ قدیمی را داشتند؛ با backup در `/var/backups/boursnegar/runtime-path-unification-20260831T144406Z` هر چهار unit (`market-daily`، `market-intraday`، `codal-financials` و `rahavard-quarantine`) فقط از نظر interpreter اصلاح و `daemon-reload` شدند. `ExecStart` هر چهار مورد اکنون runtime ثابت را نشان می‌دهد؛ هیچ اجرای سنگین یا import جدیدی در این اصلاح شروع نشد.
- پس از یکسان‌سازی، بررسی داخلی وب، data-service و observer سبز ماند. بررسی عمومی از سیستم Local با HTTP 200 انجام شد؛ درخواست عمومی از خود سرور در چند تلاش به‌صورت intermittent در Cloudflare timeout شد (hairpin)، بنابراین این timeout به‌عنوان نقص داخلی یا PASS کامل ثبت نمی‌شود. `remote-final-gate.sh` نیز timeout شبکهٔ صریح ۱۵ ثانیه‌ای گرفت تا probe بی‌نهایت معطل نماند.

## 2026-08-31 - recovery81 برای سه گیت دوره‌ای

- بازهٔ رسمی `1403/01/01 تا 1404/09/30` برای `کمرجانح، نیروترانسفو، فاهواز` با نشست مرورگر Local بررسی شد. کمرجانح و نیروترانسفو با وضعیت `NO_NOTICES` و صفر رکورد پایان یافتند؛ فاهواز ۱۲ رکورد جست‌وجو داشت اما هیچ سند مالی قابل‌استخراج برای normalization تولید نکرد.
- checkpoint و manifest در `artifacts/recovery81-period-browser/` و `artifacts/recovery81-period-normalized/` نگه‌داری شدند؛ normalization خروجی `records=0`, `source_documents=0`, `errors=0` داشت. هیچ import، snapshot mutation یا مقدار حدسی انجام نشد؛ این سه گیت برای retry رسمی با بازه/نشست متفاوت باقی ماندند.

## 2026-08-31 - recovery82 برای سه گیت دوره‌ای با بازهٔ گسترده‌تر

- بازهٔ `1402/01/01 تا 1404/09/30` برای `غگیلا، ساینا، مهر` با browser/Codal محلی بررسی شد. normalization دوره‌محور ۵۶ رکورد و ۱۲ سند رسمی تولید کرد؛ یک فایل غیرقابل‌خواندن مهر با خطای `No tables found` retained شد و وارد داده نشد.
- import artifact-only با backup `/var/backups/boursnegar/20260831T-recovery82-before-import.dump` انجام شد: ۴۱ رکورد و fact جدید پذیرفته شد، ۱۵ مورد تکراری بود، validation error صفر و replay دوم `inserted=0` بود. refresh هر سه snapshot با checkpoint `artifacts/recovery82-refresh.json` موفق شد.
- ممیزی all-active در `artifacts/audits/coverage-all-active-20260831-recovery82.json` با SHA-256 `a921515bf913112f6c937d5da675178a779083498416f2db74e9b53d0b70c030` و CSV با SHA-256 `3890862e0aabef1229f1977ea12712858dad4c4a91c0b979952445a1393a6378` ثبت شد. tierها `CORE_READY=721`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=384` هستند؛ این batch رکورد معتبر اضافه کرد اما tier کلی را تغییر نداد.
- registry به‌روز در `artifacts/audits/public-645-gate-registry-20260831-recovery82.json` با SHA-256 `d5d99aef856b5f7667d8c86c0014ae4f03c99aa4a80ee95eb64f55b4010c058d` ثبت شد. هیچ دادهٔ حدسی یا هویت نامعتبر وارد نشد.

## 2026-08-31 - بررسی گیت‌های بدون گزارش و شواهد ناقص وثوق

- recovery83 برای `وثوق، سفارود، ثقزویح` با بازهٔ `1402/01/01 تا 1404/09/30` انجام شد. وثوق ۲۰ اطلاعیه و سفارود یک مکاتبه داشتند و ثقزویح بدون اطلاعیه بود؛ هیچ سند کامل قابل normalization پیدا نشد و import انجام نشد.
- recovery84 برای وثوق با فیلتر رسمی دورهٔ ۱۲ماهه اجرا شد. سه رکورد `net_profit` از اطلاعیه‌های مجمع استخراج شد، اما چون صورت مالی کامل نیستند و دوره را با هستهٔ fact قابل‌اتکا ثابت نمی‌کنند، وارد facts canonical نشدند. manifest و شواهد خام در `artifacts/recovery83-period-browser/` و `artifacts/recovery84-annual-browser/` نگه‌داری شدند.
- گیت وثوق، سفارود و ثقزویح همچنان باز و evidence-first است؛ هیچ period، تصمیم یا identity حدسی ساخته نشد.

## 2026-08-31 - ممیزی نهایی پس از یکسان‌سازی مسیرها

- بررسی زندهٔ Production با alias `boursnegar` موفق بود: وب `healthz` و `readyz`، سرویس داده و observer همگی سبز هستند. observer مقدار `disk=84%`، `rows=50`، `coverage_min=42.86`، `coverage_max=100` و `coverage_100=43` را گزارش کرد؛ این کاهش پوشش به‌عنوان شکست سرویس یا مجوز تصمیم قطعی تفسیر نمی‌شود.
- releaseهای فعال همان مسیرهای استاندارد هستند: وب `/var/www/boursnegar-current` و داده `/var/www/boursnegar-data-current`؛ هر چهار unit بررسی‌شده از `/var/www/boursnegar-runtimes/data-venv/bin/python3` استفاده می‌کنند و هیچ unit شکست‌خوردهٔ `boursnegar` باقی نمانده است.
- یک پردازش موقتِ رهاشده از ۲۲ اوت که با interpreter قدیمی برای بررسی دستی Codal اجرا شده بود، پس از احراز مستقل‌بودن از سرویس‌ها خاتمه یافت. سرویس فعال data-service همچنان برقرار است؛ پردازش‌های `bourse-analyzer` و `data-service.broken` دیده نشدند.
- timerهای بازار روزانه، بازار intraday، observer و alert worker فعال هستند. هیچ import، restart اضافی، حذف backup یا حذف artifact انجام نشد.
- اعتبارسنجی نهایی Local: `python unittest` با ۱۰۲ تست، تست وب با ۷۲ تست، typecheck، build production، `project-memory-check` و `git diff --check` همگی موفق شدند.
- گیت‌های شواهد ناقص و نبود گزارش هنوز باز هستند؛ recovery83/84 به‌درستی بدون import پایان یافتند. صفحهٔ مستقل نماد قبلاً با QA زنده تأیید شده است، اما لینک وب‌سایت رسمی و تصویر شرکت تا زمان وجود منبع معتبر اضافه نمی‌شوند.

## 2026-08-31 - حذف آخرین ارجاع اجرایی به venv قدیمی data-service

- ممیزی process نشان داد data-service با interpreter ثابت اجرا می‌شد، اما command آن هنوز به `.../boursnegar-data-current/venv/bin/uvicorn` اشاره داشت. این ارجاع با unit هم‌راستا نبود و برای جلوگیری از ابهام مسیر اصلاح شد.
- فایل مرجع `ops/systemd/boursnegar-data-service.service` اضافه شد: `PATH` و `ExecStart` اکنون مستقیماً از `/var/www/boursnegar-runtimes/data-venv/bin/python3 -m uvicorn` استفاده می‌کنند. پیش از نصب، unit قبلی در backup `/var/backups/boursnegar/20260831T150051Z-data-service-unit-runtime-fix/boursnegar-data-service.service.before` نگه‌داری شد.
- پس از `daemon-reload` و restart کنترل‌شده، data-service active است و `healthz`، `readyz`، data health و observer همگی موفق‌اند؛ observer `disk=83%`, `rows=50`, `coverage_min=42.86`, `coverage_max=100`, `coverage_100=43` گزارش کرد. هیچ import یا mutation داده انجام نشد.
- ممیزی process پس از تغییر، هیچ `bourse-analyzer`، `data-service.broken` یا `/var/www/boursnegar-data-current/venv` فعال نشان نداد و `systemctl --failed` برای unitهای بورس‌نگار خالی بود.

## 2026-08-31 - recovery85 برای اتکای، افرا و انتخاب

- دریافت browser/Codal محلی برای `اتکای، افرا، انتخاب` در بازهٔ `1402/01/01 تا 1404/09/30` با فیلتر رسمی دورهٔ ۶ماهه انجام شد. manifest خام با SHA-256 `1d915b8a13a14be086b2f1ea873b5ece9c0c249800080efe606a6d187e365c64` سه فایل و ۶۰ رکورد جست‌وجو را ثبت کرد.
- normalization با manifest در `artifacts/recovery85-period-normalized/manifest.json` و SHA-256 `4e66648cdecf9469e91bffba64c84418cea87046efc89db2ff3ea22f2f5928fc`، ۶۴ رکورد و ۱۲ سند رسمی تولید کرد. چهار عنوان صریحاً متعلق به شرکت‌های زیرمجموعه بودند و به‌عنوان `child_entity_financial_statement` retained شدند؛ هیچ‌کدام وارد facts نشدند.
- سه سند والد قابل‌قبول شناسایی شد: اتکای ۲۸ fact در دورهٔ `1403/10/01 تا 1404/03/31`، افرا ۲۶ fact در دورهٔ `1404/01/01 تا 1404/06/31` و انتخاب ۱۰ fact تلفیقی در دورهٔ `1403/10/01 تا 1404/03/31`. پیش از import، backup معتبر Production در `/var/backups/boursnegar/20260831T150300Z-recovery85-before-import.dump` با SHA-256 `0a5e871615dd4c393b62a370325b3e1fc4c7d05a73efc6b596006748788016d1` ثبت شد.
- import artifact-only با checksum و advisory lock موفق شد: `inserted=54`, `standard_facts=57`, خطای validation صفر؛ replay درج خام جدیدی نداشت (`inserted=0`) و فقط ۶ fact هم‌کلید را با همان شواهد به‌روزرسانی کرد. refresh داخلی هر سه نماد با HTTP 200 موفق شد و checkpoint در `artifacts/recovery85-refresh.json` با SHA-256 `2993de5bd3bb0eb2db55d72d4e96460ab48628f84ac568764519a0ae61c62261` ثبت شد.
- audit زندهٔ all-active در `artifacts/audits/coverage-all-active-20260831-recovery85.json` با SHA-256 `f0f3ca162fbbd8fb5df5e4a5b9fc8cd83a0394b7cf5eca19e79ce13ebf38649f` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۸۷۶ دوره، ۷۰۲۶۶ fact و ۳۶۳۴۸ fact معتبر؛ tierها `CORE_READY=721`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=384` و تصمیم‌های latest برابر `INSUFFICIENT_DATA=1471`, `SELL=51`, `HOLD=2` هستند.
- registry عملیاتی در `artifacts/audits/public-645-gate-registry-20260831-recovery85.json` با SHA-256 `ead688b0812f5fe27a030a8495b4a83ee8cd04339e2a9882a2d888bfd1a6f5e4` و CSV با SHA-256 `074e06ca442d9db2c5c1282a635decfc3bb4cbe6832d9f9f5b8f939ead85c144` ساخته شد. شمارش gate تغییری نکرد؛ اتکای و افرا اکنون در all-active سه دورهٔ معتبر دارند، اما گیت اطمینان/پوشش مطابق policy باز مانده است.
- هیچ دادهٔ حدسی، هویت ساختگی، import مستقیم Codal از Production یا حذف backup/artifact انجام نشد.

## 2026-08-31 - recovery86 برای بساما، بمپنا و توسن

- دریافت browser/Codal محلی برای `بساما، بمپنا، توسن` در بازهٔ `1402/01/01 تا 1404/09/30` با فیلتر رسمی دورهٔ ۶ماهه انجام شد. normalization، ۷۶ رکورد و ۱۴ سند رسمی تولید کرد؛ دو عنوان بساما مربوط به شرکت زیرمجموعهٔ هلدینگ سرآمد بود و با وضعیت `child_entity_financial_statement` retained شد.
- شواهد قابل‌قبول شامل بساما ۴۰ fact در دورهٔ `1404/01/01 تا 1404/06/31`، بمپنا ۲۶ fact در دورهٔ `1403/10/01 تا 1404/03/31` و توسن ۱۰ fact در دورهٔ `1403/10/01 تا 1404/03/31` بود. manifest نرمال‌شده در `artifacts/recovery86-period-normalized/manifest.json` با SHA-256 `5afae15cd1725e393b2b4c3d385799f8a1744befdc6997fe34e4bda28448ff87` ثبت شد.
- پیش از import، backup Production در `/var/backups/boursnegar/20260831T151500Z-recovery86-before-import.dump` با SHA-256 `d0e34138de481ec9d3e73f044e686d9773229864777b53fa9e9fac6fed4e4908` ثبت شد. import artifact-only با checksum و advisory lock موفق شد: `inserted=62`, `standard_facts=62`, validation error صفر؛ replay دوم `inserted=0`, `standard_facts=0` بود.
- refresh داخلی هر سه نماد با HTTP 200 موفق شد و checkpoint `artifacts/recovery86-refresh.json` ثبت گردید. audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery86.json` با SHA-256 `4aebf691a0b85349b7ae808deebb5aa641bc0c0b8881576a111bf21b5eb8b0f0` و CSV با SHA-256 `23ef183d5f7ddf0adbb926ac901cc60e9dc8949bdb928ce01dd0838d8762b5e6` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۸۹۰ دوره، ۷۰۳۲۸ fact و ۳۶۴۱۰ fact معتبر.
- registry عملیاتی recovery86 در `artifacts/audits/public-645-gate-registry-20260831-recovery86.json` با SHA-256 `13916256f068db6edae82cdcd6e4794c35a5abe0f3a292f18bb2c0575a79c392` و CSV با SHA-256 `bcf0bb7cfe83eef0568ed0f1c49f745de070d7cb41987e1d930a3c9aa5955675` ثبت شد. شمارش gateها همچنان `ANALYTICAL_CONFIDENCE_GATE=322`, `SNAPSHOT_COVERAGE_GAP=300`, `NO_KNOWN_DATA_GATE=9`, `RECOVERY_CLOSED=14` است.
- هیچ داده یا هویت حدسی وارد نشد و backup/artifact حذف نشد. گیت‌های مقایسه‌ای، پوشش و مدل صندوق همچنان طبق evidence-first policy باز هستند.

## 2026-08-31 - recovery87 برای تکیمیا، ثباغ و ثزاگرس

- دریافت browser/Codal محلی برای `تکیمیا، ثباغ، ثزاگرس` در بازهٔ `1402/01/01 تا 1404/09/30` با فیلتر رسمی ۶ماهه انجام شد. normalization، ۵۸ رکورد و ۹ سند تولید کرد؛ دو عنوان retained مربوط به شرکت‌های زیرمجموعه بودند و به والد نسبت داده نشدند.
- شواهد والد معتبر شامل تکیمیا ۲۶ fact در دورهٔ `1404/01/01 تا 1404/06/31` و ثباغ ۳۲ fact در دورهٔ `1403/10/01 تا 1404/03/31` بود. برای ثزاگرس فقط شواهد شرکت زیرمجموعه پیدا شد و import انجام نشد. manifest نرمال‌شده در `artifacts/recovery87-period-normalized/manifest.json` با SHA-256 `d4adaed22bb0d2463571746bedb7f6a5e1f7381427160638f150acda930fb365` ثبت شد.
- backup Production پیش از import در `/var/backups/boursnegar/20260831T153000Z-recovery87-before-import.dump` با SHA-256 `65dc963fa2df8727e47502946bd9c647363d46af42df0eba0f0d5a194f158994` ثبت شد. import artifact-only با checksum و advisory lock موفق شد: `inserted=40`, `standard_facts=40`, validation error صفر؛ replay دوم `inserted=0`, `standard_facts=0` بود.
- refresh داخلی تکیمیا و ثباغ با HTTP 200 موفق شد؛ ثزاگرس به دلیل نبود evidence والد refresh نشد. audit زنده در `artifacts/audits/coverage-all-active-20260831-recovery87.json` با SHA-256 `637af678efd28a3b3bacb8b247a5668e5e46c1b63105d7b5b8395599a9f7677f` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۸۹۸ دوره، ۷۰۳۶۸ fact و ۳۶۴۵۰ fact معتبر.
- registry recovery87 در `artifacts/audits/public-645-gate-registry-20260831-recovery87.json` با SHA-256 `3c76b1b0b896155ba89e44eeb44f77608c701f0b1efa8fd111ed2fc10f45eeef` و CSV با SHA-256 `c76fd944748323d619d98ee3de0255050faff47c0f205535e2eefd448beb3858` ثبت شد. شمارش gateها همچنان `ANALYTICAL_CONFIDENCE_GATE=322`, `SNAPSHOT_COVERAGE_GAP=300`, `NO_KNOWN_DATA_GATE=9`, `RECOVERY_CLOSED=14` است.
- هیچ داده یا هویت حدسی، import مستقیم Codal از Production یا حذف backup/artifact انجام نشد؛ گیت‌های شواهد ناکافی همچنان باز هستند.

## 2026-08-31 - recovery88 برای حگهر، خکاوه و زاگرس

- دریافت browser/Codal محلی برای `حگهر، خکاوه، زاگرس` در بازهٔ `1402/01/01 تا 1404/09/30` با فیلتر رسمی ۶ماهه انجام شد. normalization، ۹۴ رکورد و ۱۴ سند تولید کرد؛ دو عنوان خکاوه مربوط به شرکت‌های زیرمجموعه بود و retained شد.
- شواهد والد معتبر شامل حگهر ۲۶ fact، خکاوه ۲۶ fact و زاگرس ۴۲ fact، همگی در دورهٔ `1404/01/01 تا 1404/06/31`، بود. manifest نرمال‌شده در `artifacts/recovery88-period-normalized/manifest.json` با SHA-256 `3bd0b1b060b15b3c030d290b45717fe0ef018bd9198bbc34cdc48b2c8e3a013d` ثبت شد.
- backup Production پیش از import در `/var/backups/boursnegar/20260831T160000Z-recovery88-before-import.dump` با SHA-256 `724886f85699a72e38c584474e310b6c501c8e91125346752d5225c4a129517f` ثبت شد. import artifact-only با checksum و advisory lock موفق شد: `inserted=70`, `standard_facts=80`, validation error صفر؛ replay درج خام جدیدی نداشت (`inserted=0`) و ۲۰ fact هم‌کلید را با همان شواهد همگام کرد.
- refresh داخلی هر سه نماد با HTTP 200 موفق شد و checkpoint در `artifacts/recovery88-refresh.json` ثبت گردید. audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery88.json` با SHA-256 `6d14a70a0e6915ea4515cfb2d9bba3fb72caf861cd7faf51bb4bd0270b676818` و CSV با SHA-256 `965d6652e37c269062df72cc9a22f30a0d942b1528108fe00092d24c8267d67a` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۱۲ دوره، ۷۰۴۳۸ fact و ۳۶۵۲۰ fact معتبر.
- registry recovery88 در `artifacts/audits/public-645-gate-registry-20260831-recovery88.json` با SHA-256 `1b48052eaf6edfd1e53c21ed4f7777f079308c7b2c80373770d6b56d20a8c7a5` و CSV با SHA-256 `982d2c466f3b310aa44cb03fa00d551ea37c03437f5f16b59ef91c66be19eb6f` ثبت شد. شمارش gateها همچنان `ANALYTICAL_CONFIDENCE_GATE=322`, `SNAPSHOT_COVERAGE_GAP=300`, `NO_KNOWN_DATA_GATE=9`, `RECOVERY_CLOSED=14` است.
- هیچ دادهٔ ساختگی یا هویت حدسی وارد نشد؛ گیت‌های کیفیت و پوشش همچنان طبق provenance باز هستند.

## 2026-08-31 - recovery89 برای ساوه، غدیس و غمایه

- دریافت browser/Codal محلی برای `ساوه، غدیس، غمایه` در بازهٔ `1402/01/01 تا 1404/09/30` با فیلتر رسمی ۶ماهه انجام شد. normalization، ۵۸ رکورد و ۱۰ سند رسمی تولید کرد؛ یک فایل غدیس با خطای `No tables found` retained شد و وارد داده نشد.
- هر سه نماد شواهد والد معتبر شش‌ماهه داشتند و برای هرکدام ۱۶ تا ۲۶ fact استخراج شد. manifest نرمال‌شده در `artifacts/recovery89-period-normalized/manifest.json` با SHA-256 `3b48e614ea77c23c8c82fd0f645bab6a01473df7024c5648f70da9fb45eb266a` ثبت شد.
- backup Production پیش از import در `/var/backups/boursnegar/20260831T170000Z-recovery89-before-import.dump` با SHA-256 `0e64d0e9f9bff81db5f2e6cd3b9ecbfa8884c6d657c431f27a0eadd27550db4a` ثبت شد. import artifact-only با checksum و advisory lock موفق شد: `inserted=46`, `standard_facts=46`, validation error صفر؛ replay دوم `inserted=0`, `standard_facts=0` بود.
- refresh داخلی هر سه نماد با HTTP 200 موفق شد. audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery89.json` با SHA-256 `72c42c5bf147cd5be97017dcab40e04dffd6f50dd17d9b6f6f59e6efdc801dfd` و CSV با SHA-256 `bc75b929f9a6d839acab35a0435abe04f3fb86fa5b1bcd2b7f8630c2670ff92b` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۲۱ دوره، ۷۰۴۸۴ fact و ۳۶۵۶۶ fact معتبر.
- registry recovery89 در `artifacts/audits/public-645-gate-registry-20260831-recovery89.json` با SHA-256 `7eda00d6e748d1b09fafded7d21c22e16feaf8b151150f9b1d1d062ecd2f6094` و CSV با SHA-256 `7cf68bf30709859c7c5a6d5068f7cf8fbba13996fde8c2e1ff583a4d89e2c6c3` ثبت شد. شمارش gateها همچنان `ANALYTICAL_CONFIDENCE_GATE=322`, `SNAPSHOT_COVERAGE_GAP=300`, `NO_KNOWN_DATA_GATE=9`, `RECOVERY_CLOSED=14` است.
- هیچ دادهٔ ساختگی، هویت حدسی، import مستقیم Codal از Production یا حذف backup/artifact انجام نشد.

## 2026-08-31 - recovery90 برای فافزا، فبستم و فجوش

- دریافت browser/Codal محلی برای `فافزا، فبستم، فجوش` در بازهٔ `1402/01/01 تا 1404/09/30` با فیلتر رسمی ۶ماهه انجام شد. normalization، ۵۸ رکورد و ۱۰ سند تولید کرد؛ دو خطای فافزا شامل یک سند زیرمجموعه و یک فایل بدون جدول retained شد. فجوش evidence قابل‌استخراج نداشت.
- شواهد والد معتبر شامل فافزا ۳۲ fact در دورهٔ `1404/01/01 تا 1404/06/31` و فبستم ۲۶ fact در دورهٔ `1403/10/01 تا 1404/03/31` بود. manifest نرمال‌شده در `artifacts/recovery90-period-normalized/manifest.json` با SHA-256 `14be1e71b27b6736f08fb8a9ac84a784f08b48d68bbfba58f439ca68528115c2` ثبت شد.
- backup Production پیش از import در `/var/backups/boursnegar/20260831T180000Z-recovery90-before-import.dump` با SHA-256 `a485aa7742587dc3ca5f1d213bb440d853fad00c1efa138a3cb908a47aaaffd9` ثبت شد. import artifact-only با checksum و advisory lock موفق شد: `inserted=46`, `standard_facts=46`, validation error صفر؛ replay دوم `inserted=0`, `standard_facts=0` بود.
- refresh داخلی فافزا و فبستم با HTTP 200 موفق شد؛ فجوش به‌دلیل نبود evidence والد refresh نشد. audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery90.json` با SHA-256 `bfdc7de8221323e1305659c77039d0f775c9f810329f825e50b462bd06e61286` و CSV با SHA-256 `6a8c5ebc114319fcf306585b4f8bc04d38d6bf53a66fb3208a3529b886c03b58` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۳۰ دوره، ۷۰۵۳۰ fact و ۳۶۶۱۲ fact معتبر.
- registry recovery90 در `artifacts/audits/public-645-gate-registry-20260831-recovery90.json` با SHA-256 `492e1bca3dc28afb8a2d7f4f6d8fd16248b1a110937c0912b8e170e6b5a44e7d` و CSV با SHA-256 `be167be956564b8c78bfa49d1e6a3abbaf93ab085867ae577432a0f7536a1582` ثبت شد. شمارش gateها همچنان `ANALYTICAL_CONFIDENCE_GATE=322`, `SNAPSHOT_COVERAGE_GAP=300`, `NO_KNOWN_DATA_GATE=9`, `RECOVERY_CLOSED=14` است.
- فضای Production هنگام شروع batch حدود ۳٫۵ گیگ آزاد بود و پس از backup حدود ۸۶٪ مصرف گزارش شد. برای جلوگیری از فشار دیسک، batch بعدی تا بررسی retention متوقف شد؛ هیچ backup یا artifact موجودی حذف نشد.

## 2026-08-31 - recovery91 برای فزر، قاسم و مفاخر

- دریافت browser/Codal محلی برای `فزر، قاسم، مفاخر` در بازهٔ `1402/01/01 تا 1404/09/30` با فیلتر رسمی ۶ماهه انجام شد. normalization، ۴۶ رکورد و ۸ سند تولید کرد؛ سه عنوان متعلق به شرکت‌های زیرمجموعه retained شد و به والد نسبت داده نشد.
- شواهد والد معتبر شامل فزر ۱۰ fact در دورهٔ `1403/10/01 تا 1404/03/31`، قاسم ۱۰ fact در دورهٔ `1404/01/01 تا 1404/06/31` و مفاخر ۲۶ fact در دورهٔ `1403/10/01 تا 1404/03/31` بود. manifest نرمال‌شده در `artifacts/recovery91-period-normalized/manifest.json` با SHA-256 `8c8568f0d9f2fdebeb1ff1bb8ef9d78df70c13e1bf08dbf27020981ccf4e26b7` ثبت شد.
- backup Production پیش از import در `/var/backups/boursnegar/20260831T190000Z-recovery91-before-import.dump` با SHA-256 `aba7f3b0d63ef25d858cb271b7dadd854b9da49f3a5207ab0566b4896dd1c730` ثبت شد. import artifact-only با checksum و advisory lock موفق شد: `inserted=40`, `standard_facts=40`, validation error صفر؛ replay دوم `inserted=0`, `standard_facts=0` بود.
- refresh داخلی هر سه نماد با HTTP 200 موفق شد. audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery91.json` با SHA-256 `668a5a56f3f47d9663376cd65c5d725e43113e7bb34597235f49886c1cec4508` و CSV با SHA-256 `ceaee6dc9602a13d613bde867fab23cb3d49e71c1d52ec75a497c7cc63f5119a` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۳۸ دوره، ۷۰۵۷۰ fact و ۳۶۶۵۲ fact معتبر.
- registry recovery91 در `artifacts/audits/public-645-gate-registry-20260831-recovery91.json` با SHA-256 `40e43c5bb9287f6c3613fa7f591cea38ee063eb7aa1fa2d67d69bf3c762006d6` و CSV با SHA-256 `ea0f9067964003b7c3bcf5e2e9671f91b88c589285cd739b534975649792e368` ثبت شد. شمارش gateها همچنان `ANALYTICAL_CONFIDENCE_GATE=322`, `SNAPSHOT_COVERAGE_GAP=300`, `NO_KNOWN_DATA_GATE=9`, `RECOVERY_CLOSED=14` است.
- فضای Production پس از این backup به محدودهٔ ۸۷٪ رسید؛ برای جلوگیری از پرشدن دیسک، batch بعدی تا بررسی retention امن متوقف است. هیچ backup یا artifact حذف نشد.

## 2026-08-31 - ممیزی retention پس از recovery91

- فضای واقعی Production در ممیزی retention حدود ۳٫۲ گیگ آزاد و ۸۸٪ مصرف بود. مصرف اصلی شامل `/var/backups/boursnegar` حدود ۶٫۷ گیگ، PostgreSQL حدود ۳ گیگ و `/var/lib/boursnegar/codalpy` حدود ۲٫۲ گیگ است؛ releaseهای فعال عامل اصلی فشار نیستند.
- backupهای recovery80 تا recovery91، dumpهای قبل از rollout و آرشیو Codal روزانه به‌عنوان rollback/provenance حفاظت شدند. حذف یا فشرده‌سازی آن‌ها بدون سیاست retention و مسیر بازیابی تأییدشده انجام نشد.
- در `/tmp` فایل‌های قدیمی build، audit و coverage شناسایی شدند، اما چون برخی ممکن است تنها نسخهٔ شواهد یک اجرای قبلی باشند، بدون تطبیق manifest/backup حذف نشدند. فایل‌های transient شناخته‌شدهٔ اجرای جاری قبلاً پاک شده‌اند.
- recovery داده‌ای پس از recovery91 موقتاً متوقف است تا retention ایمن مشخص شود؛ سرویس‌ها و داده‌های موجود دست‌نخورده و قابل‌بازگشت باقی مانده‌اند. هیچ دادهٔ ساختگی یا هویت حدسی وارد نشد.
- در ممیزی بعدی یک فایل backup صفر‌بایتی و نامعتبر `/var/backups/boursnegar/20260831T-recovery70-before-import.dump` شناسایی و فقط همان فایل حذف شد؛ backupهای معتبر، آرشیو Codal و releaseهای rollback دست‌نخورده ماندند. پس از این cleanup فضای آزاد همچنان حدود ۳٫۲ گیگ و observer/health سبز است.

## 2026-08-31 - اعمال سیاست نگهداری دو dump کامل Production

- با تأیید کاربر، همهٔ ۴۶ dump کامل و معتبر PostgreSQL موجود در `/var/backups/boursnegar` با `pg_restore -l` بررسی شدند. دو dump جدیدتر نگه داشته شدند: `20260831T190000Z-recovery91-before-import.dump` با SHA-256 `aba7f3b0d63ef25d858cb271b7dadd854b9da49f3a5207ab0566b4896dd1c730` و `20260831T180000Z-recovery90-before-import.dump` با SHA-256 `a485aa7742587dc3ca5f1d213bb440d853fad00c1efa138a3cb908a47aaaffd9`.
- ۴۴ dump قدیمی‌تر، پس از ثبت اندازه و SHA-256 هر مورد در گزارش `/var/backups/boursnegar/20260831T180519Z-retention-two-full-dumps.tsv` حذف شدند. نسخهٔ ممیزی لوکال در `artifacts/audits/production-backup-retention-20260831.tsv` با SHA-256 `26500fd0a56070eb90e96f486e83e966060986a122daa68787a606ae511cb6b3` ثبت است. backupهای تنظیمات/rollback، لاگ‌های provenance، releaseها و artifactهای خام Codal حذف نشدند.
- اندازهٔ `/var/backups/boursnegar` از حدود ۶٫۹ گیگ به ۱٫۶ گیگ رسید؛ فضای آزاد `/` از ۳٫۲ گیگ و ۸۸٪ مصرف به ۸٫۵ گیگ و ۶۵٪ مصرف رسید. health وب، ready، data-service و observer موفق‌اند و `systemctl --failed` برای سرویس‌های بورس‌نگار خروجی ندارد.
- سیاست ادامه: در هر اجرای backup کامل جدید، دو dump معتبر جدیدتر نگه داشته شوند؛ backupهای غیر dump فقط طبق دستهٔ rollback/config و provenance مستقل نگه‌داری شوند. هیچ artifact خام یا مدرک منبع به‌دلیل این سیاست حذف نشود.

## 2026-08-31 - خودکارسازی retention Production

- ابزار قابل‌تکرار `scripts/production-backup-retention.sh` اضافه و روی `/usr/local/sbin/boursnegar-backup-retention` نصب شد. اجرای پیش‌فرض dry-run است؛ اجرای `--apply` فقط dumpهای custom PostgreSQL معتبر را بررسی، checksum می‌کند و طبق سیاست دو مورد آخر حذف می‌کند. قفل همزمانی، بررسی `pg_dump/pg_restore` و توقف هنگام فعال‌بودن unitهای ingest دارد.
- دو dump قدیمی داخل rollbackهای recovery قبلی نیز در اجرای recursive شناسایی و حذف شدند. گزارش اجرای نهایی Production در `/var/backups/boursnegar/20260831T184731Z-retention-report.tsv` و نسخهٔ لوکال در `artifacts/audits/production-backup-retention-20260831-final.tsv` با SHA-256 `7c901f59b2d4c2d05312c9d1a7e5347306c67d211b21ada8a1fd76e8be1ecc20` ثبت است؛ گزارش شامل checksum و مسیر هر چهار dump بررسی‌شده است.
- واحدهای `boursnegar-backup-retention.service` و `boursnegar-backup-retention.timer` به مخزن اضافه و timer روزانه با تأخیر تصادفی حداکثر ۱۵ دقیقه فعال شد. اجرای دستی service موفق بود و در پایان فقط recovery91 و recovery90 باقی ماندند.
- وضعیت زنده پس از نصب: `/var/backups/boursnegar` حدود ۱٫۳ گیگ، فضای آزاد `/` حدود ۸٫۷ گیگ و مصرف ۶۵٪؛ `readyz` وب و `health` سرویس داده موفق، timer فعال و `systemctl --failed` برای بورس‌نگار خالی است. این ابزار به raw Codal، provenance، release و backupهای config/rollback غیر dump دست نمی‌زند.

## 2026-08-31 - recovery92 برای گیت‌های بدون گزارش

- retry مرورگری محلی برای ۹ نماد `وثوق، فن افزار، سفارود، ثقزویح، گنگین، فاهواز، ولاناح، نیروترانسفو، کمرجانح` در بازهٔ `1402/01/01 تا 1404/09/30` با فیلتر رسمی ۶ماهه انجام شد. هر ۹ manifest با منبع `browser/codal.ir` و `files=0`, `errors=0` پایان یافتند؛ هیچ سند مالی والد جدیدی برای normalization وجود نداشت.
- audit مستقل در `artifacts/audits/recovery92-no-known-data-20260831.json` با SHA-256 `326f09b39a5985dbb9759f8b933c3e85be0f14b68bb08c1bbda061a725be478e` ثبت شد. هیچ import، backup جدید، snapshot mutation یا تصمیم بنیادی انجام نشد؛ گیت `NO_KNOWN_DATA_GATE` برای هر ۹ نماد طبق policy باز ماند.
- هر ۹ capture، checkpoint و manifest خام در `artifacts/recovery92-period-browser/` حفظ شدند. نبود فایل، نتیجهٔ واقعی جست‌وجوی امروز است و به‌عنوان پوشش یا دادهٔ قدیمی تفسیر نشد.
- پس از این بررسی، تست Python با ۱۰۲ مورد و تست وب با ۷۲ مورد موفق شدند؛ `git diff --check` نیز بدون خطا بود. گیت‌های باز شامل نبود evidence والد برای این ۹ نماد، گیت‌های پوشش/اطمینان تحلیلی، و E2E moderator/reward با نشست مجاز واقعی است.

## 2026-08-31 - recovery93 با بازهٔ گسترده‌تر برای سه گیت بدون گزارش

- برای `فن افزار، وثوق، فاهواز` بازهٔ مرورگری از `1403/01/01` تا `1405/06/09` بدون فیلتر دوره‌ای اجرا شد تا اطلاعیه‌های رسمی خارج از بازهٔ قبلی هم بررسی شوند. هر سه manifest با منبع `browser/codal.ir`، `files=0` و `errors=0` پایان یافتند.
- normalizer با staging تختِ artifact-only اجرا شد و `records=0`, `source_documents=0`, `errors=0` تولید کرد. probe خواندنی API رسمی کدال برای فن‌افزار نیز `Total=0` و `Letters=[]` برگرداند. گزارش در `artifacts/audits/recovery93-broad-no-notices-20260831.json` با SHA-256 `e5dee82360f684a4e37b50838cfc2b32e12354dc1a8d0084a0f071a0ed41f3f9` ثبت است؛ manifest نرمال‌شده در `artifacts/recovery93-broad-normalized-20260831/manifest.json` با SHA-256 `51e5756c14728670dc7347a6872262accf8031652a202ab573106ceed7d7f5fd` ثبت شد.
- هیچ import، backup، snapshot mutation یا تصمیم بنیادی انجام نشد. این نتیجه evidence نبود گزارش رسمی قابل‌استخراج در جست‌وجوی گسترده‌تر امروز است؛ گیت هر سه نماد همچنان `NO_KNOWN_DATA_GATE` باقی ماند.

## 2026-08-31 - حذف مسیر Local با دادهٔ ثابت از entry اجرایی

- ممیزی نشان داد `web/src/main.tsx` در اجرای `npm run dev`، اپ قدیمی `App.tsx` را mount می‌کرد؛ آن اپ و `stocksData.ts` شامل مقادیر ثابتِ بدون provenance برای چند نماد بودند. این مسیر با سیاست عدم جعل ناسازگار بود، هرچند entry Production جدا بود.
- entry Local اکنون همان `AppProduction` evidence-gated را mount می‌کند و `web/vite.config.ts` مسیر `/api` را از طریق proxy قابل‌تنظیم `BOURSNEGAR_API_PROXY` به backend می‌فرستد. نبود backend اکنون خطای شفاف/داده‌نیامده می‌دهد، نه دادهٔ ثابت.
- فایل‌های legacy برای تاریخچه حذف نشدند، اما دیگر از entry اجرایی Local یا Production قابل‌دسترسی نیستند. Production همچنان از `main.production.tsx` استفاده می‌کند.
- smoke واقعی dev server در `127.0.0.1:5180` نشان داد HTML از `main.tsx` و module ارائه‌شده از `AppProduction` استفاده می‌کند. تست وب ۷۳ مورد، typecheck، build و `git diff --check` موفق شدند؛ هیچ Production data mutation انجام نشد.

## 2026-08-31 - ممیزی اجرای روزانه پس از recovery92

- ممیزی زندهٔ timerها نشان داد آخرین اجرای موفق `boursnegar-market-daily.service` در `13:09:19 UTC` با `status=passed`, تعداد `prices=1346` و `missing=267` ثبت شده است؛ `boursnegar-market-intraday.service` نیز در `13:09:45 UTC` موفق شد. `missing` به‌عنوان دادهٔ unmapped واقعی باقی می‌ماند و به عددسازی یا حذف گیت کیفیت تبدیل نشده است.
- خطاهای قدیمی‌تر همان روز شامل نبود موقت `.env` در زمان تلاش‌های قبل از اصلاح و یک اجرای قدیمی با گیت سخت‌گیرانهٔ mapping بود؛ آخرین اجرای هر دو job موفق است و `Result=success`, `ExecMainStatus=0` دارد. این سابقه برای جلوگیری از ادعای «بدون هیچ خطای تاریخی» حفظ شد.
- checksum واحدهای retention نصب‌شده با فایل‌های مخزن یکسان است؛ timer retention فعال است. health وب، ready، data health و observer موفق‌اند و `systemctl --failed` برای unitهای بورس‌نگار خالی است.
- این ممیزی هیچ import، restart، تغییر داده یا حذف artifact انجام نداد. گیت‌های داده و E2E نشست مجاز همچنان طبق evidence-first policy باز هستند.

## 2026-08-31 - ممیزی نهایی مسیرهای اجرایی Production

- process واقعی تنها data-service فعال را با `/var/www/boursnegar-runtimes/data-venv/bin/python3 -m uvicorn` نشان داد. PM2 فقط `/var/www/boursnegar-current` و `dist/server.cjs` را اجرا می‌کند؛ market daily، market intraday و Codal importer نیز از runtime ثابت و `boursnegar-data-current` استفاده می‌کنند.
- هیچ process یا unit فعال از `/var/www/bourse-analyzer`، `data-service.broken`، `boursnegar-data-current/venv` یا `/var/www/boursnegar-data-service/venv` پیدا نشد. timerهای Codal backfill، Codal financials و Rahavard disabled/inactive هستند و Production مستقیماً Codal را فراخوانی نمی‌کند.
- دو فایل قدیمی `.bak/.backup` در `/etc/systemd/system` صرفاً backup تاریخی unit هستند و executable یا unit فعال نیستند؛ برای حفظ rollback نگه داشته شدند. این موارد نباید در ممیزی process به‌عنوان مسیر اجرایی شمرده شوند.
- این ممیزی بدون restart، import یا mutation انجام شد. health/readiness و وضعیت سرویس‌ها سبز باقی ماندند؛ گیت‌های evidence داده و نشست مجاز همچنان باز هستند.

## 2026-08-31 - اصلاح fallback روزانهٔ Codalpy به مرورگر

- ممیزی `data-service/scripts/daily_local_ingestion.py` نشان داد Codalpy-first در صورت exit غیرصفرِ API/شبکه، پیش از رسیدن به browser fallback متوقف می‌شد؛ timeout قبلاً fallback می‌داد، اما خطای process به‌درستی مدیریت نمی‌شد.
- تابع `symbols_requiring_browser_fallback` اضافه شد. شکست یا timeout مسیر Codalpy اکنون با event JSON ثبت می‌شود و همهٔ نمادهای همان batch به browser fallback بازمی‌گردند؛ در موفقیت Codalpy فقط rangeهای فاقد رکورد به مرورگر می‌روند. هیچ مقدار یا هویت جایگزین ساخته نمی‌شود.
- این تغییر فقط orchestration محلی را اصلاح کرد؛ Production مستقیماً Codal/Codalpy را فراخوانی نمی‌کند و هیچ import یا mutation Production در این مرحله انجام نشد. مسیر importer همچنان از runtime ثابت Production استفاده می‌کند.
- آزمون‌های هدفمند supervisor و auto-sync با ۱۶ تست، dry-run واقعی daily ingestion و `py_compile`/`git diff --check` همگی موفق شدند. این اصلاح باید برای اجرای روزانهٔ محلی به‌عنوان fallback رسمی استفاده شود.

## 2026-08-31 - زیرساخت هویت رسمی صفحهٔ مستقل نماد

- ممیزی schema و دادهٔ زندهٔ Production نشان داد `issuers` و metadata اطلاعیه‌ها هیچ وب‌سایت رسمی یا تصویر شرکتِ قابل‌اثباتی ندارند؛ بنابراین هیچ URL یا تصویر حدسی برای نمادها ساخته نشد.
- migration `web/migrations/025_issuer_profiles.sql` جدول اختیاری `issuer_profiles` را با یک رکورد برای هر ناشر، URLهای فقط HTTPS، نوع منبع، مرجع شواهد، checksum شواهد، وضعیت `VERIFIED/PENDING/REJECTED` و زمان تأیید اضافه کرد. فقط رکورد `VERIFIED` از API خوانده می‌شود.
- API صفحهٔ نماد اکنون `issuerProfile` را فقط برای پروفایل تأییدشده برمی‌گرداند. UI صفحهٔ مستقل نماد در نبود شواهد، صریحاً «وب‌سایت رسمی ثبت نشده» و جایگاه بدون تصویر رسمی نشان می‌دهد؛ با ورود رکورد معتبر، لینک وب‌سایت و تصویر کوچک با منبع نمایش داده می‌شود.
- backup پیش از migration در `/var/backups/boursnegar/20260831T190622Z-issuer-profile-before-migration.dump` با SHA-256 `899b258d2752ff9e2f53ee13cb7b22e9fc1c8bdbcce21e1b1d479f35dd708ddc` و اندازهٔ ۱۵۳۰۲۳۹۷۰ بایت ثبت و مستقل بررسی شد. release فعال `/var/www/boursnegar-releases/20260831T190622Z-issuer-profile` است؛ PM2، health، ready، endpoint نماد و observer موفق‌اند.
- سیاست retention دو dump اجرا شد و فقط backupهای `20260831T190622Z-issuer-profile-before-migration.dump` و `20260831T190000Z-recovery91-before-import.dump` باقی ماندند. هیچ دادهٔ مالی، artifact خام یا هویت ساختگی وارد نشد.
- تست وب ۷۴ مورد، typecheck، build، smoke روی release و observer Production موفق شدند. migration runner نیز اصلاح شد تا نسخهٔ اعمال‌شده را در `schema_migrations` ثبت کند.
- گیت باقی‌مانده: جمع‌آوری و تأیید واقعی وب‌سایت/لوگوی هر ناشر با manifest و checksum مستقل؛ تا آن زمان نمایش خالی عمداً حفظ می‌شود. گیت‌های داده و نشست مجاز moderator/reward همچنان جداگانه باز هستند.

## 2026-08-31 - نخستین پروفایل هویتی رسمی: فولاد

- صفحهٔ رسمی `https://msc.ir/` و فایل لوگوی همان دامنه در `artifacts/issuer-profiles-20260831/` دریافت شدند. HTML با نام فولاد مبارکه و PNG معتبر ۵۱×۸۱ ذخیره شد؛ checksumها در manifest ثبت‌اند. دامنهٔ `msc.ir` نیز در کانال رسمی گروه فولاد مبارکه به‌عنوان تارنمای گروه معرفی شده است.
- manifest `artifacts/issuer-profiles-20260831/manifest.json` با schema `boursnegar-issuer-profile-v1` شامل URL وب‌سایت، URL لوگو، منبع، مرجع و checksum است؛ SHA-256 manifest برابر `cf3210a6615a29494e546716e3294560b6409b9de71a44fff8032dae74ff7a1f` است.
- importer جدید `web/scripts/import-issuer-profiles.ts` فقط manifest دارای HTTPS، فایل موجود با checksum صحیح، تطبیق نماد/نام، advisory lock و `--apply` صریح را می‌پذیرد. اجرای dry-run و apply برای `فولاد` موفق شد؛ یک رکورد `VERIFIED` در Production ثبت شد و endpoint صفحهٔ نماد همان URLها و checksum را برگرداند.
- گزینهٔ بانک ملت به‌دلیل ناسازگاری hostname گواهی TLS در دریافت مستقیم رد شد و در manifest با دلیل نگه داشته شد؛ هیچ URL آن وارد دیتابیس نشد.
- backup پیش از import در `/var/backups/boursnegar/20260831T191605Z-issuer-profile-before-import.dump` با SHA-256 `c7e0dbc8f9d2d6ebf52464cc62002a0eb108c634d5c57f9134451c70fdf3edd3` و اندازهٔ ۱۵۳۰۲۶۸۰۹ بایت ثبت شد. retention دو dump را حفظ کرد: همین backup و backup پیش از migration `20260831T190622Z-issuer-profile-before-migration.dump`.
- observer Production با دیسک ۶۵٪ و پوشش ۴۲٫۸۶٪ تا ۱۰۰٪ موفق ماند؛ هیچ دادهٔ مالی، هویت یا URL ساختگی وارد نشد. گیت بعدی، جمع‌آوری batchهای بعدی با همین پروتکل و بررسی مجدد گزینه‌های ردشده پس از رفع TLS است.

## 2026-08-31 - batch دوم پروفایل‌های هویت رسمی: شستا و خودرو

- صفحات HTTPS رسمی `https://www.ssic.ir/` و `https://www.ikco.ir/fa/` با نام شستا و ایران‌خودرو دریافت شدند؛ HTML خام و لوگوی همان دامنه‌ها در `artifacts/issuer-profiles-20260831-batch2/` نگه‌داری شد.
- manifest مستقل `artifacts/issuer-profiles-20260831-batch2/manifest.json` با SHA-256 `5380e3a4cb67b6cbbf78d441cdac0bc31ca3dffbc5e066e2ecafa6240e36940a` شامل دو رکورد `VERIFIED`، URLهای HTTPS و checksum شواهد است. checksum HTML شستا `6db4da10406c98be4a2446144ad41c6802605c4bcb8ce8f01635469bfdb16c13` و HTML خودرو `c1522947b4be9b5314aec7bf0a9d6478df7fe72e7a9de20980c9f52bf401cf36` است؛ checksum لوگوها نیز در manifest ثبت شده‌اند.
- backup کامل پیش از import در `/var/backups/boursnegar/20260831T192205Z-issuer-profile-batch2-before-import.dump` با اندازهٔ ۱۵۳۰۲۷۰۰۸ بایت و SHA-256 `b763919987169969a138d4c4ab7a6eb8c26aad08b920617ea66360010d1895e3` ساخته و مستقل بررسی شد. پس از import و retention، فقط دو dump معتبر اخیر `20260831T191605Z-issuer-profile-before-import.dump` و همین backup باقی ماندند.
- dry-run، apply و replay دوم importer موفق شدند؛ رکوردهای `VERIFIED` برای شستا و خودرو در Production و endpointهای نماد با URL و checksum درست مشاهده شدند. advisory lock و تطبیق نماد/نام فعال بود.
- health/ready وب و observer موفق ماندند؛ observer مقدار `disk=65% rows=50 coverage_min=42.86 coverage_max=100 coverage_100=43` را ثبت کرد. بررسی پالایش اصفهان به‌دلیل timeout پاسخ/TLS در بازهٔ محدود، بدون import متوقف شد.
- هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد. گیت بعدی، ادامهٔ batchهای رسمی با همین manifest/checksum و نگه‌داشتن دو dump آخر است؛ گیت‌های پوشش داده، اطمینان تحلیلی و E2E نشست مجاز همچنان جداگانه باز هستند.

## 2026-08-31 - batch سوم پروفایل هویت رسمی: کچاد

- سایت رسمی `https://chadormalu.com/` با نام شرکت معدنی و صنعتی چادرملو و لوگوی PNG همان دامنه دریافت شد؛ HTML و تصویر خام در `artifacts/issuer-profiles-20260831-batch3/` نگه‌داری شدند. کانال روابط عمومی شرکت نیز همین دامنه را به‌عنوان وب‌سایت شرکت معرفی می‌کند.
- manifest مستقل `artifacts/issuer-profiles-20260831-batch3/manifest.json` با SHA-256 `b9b96b9d2c054f2683920f9de22ae72de4d32468df39b299d198955ad30c61a` شامل رکورد `VERIFIED` است. checksum HTML کچاد `2814997ae905784fc273c9a3e9058623becc85251cfe03a7a2b2161641f833ea` و checksum لوگو `16a6fa7ef242f24df445e6051cf3871815add1f355bd4ffce2750efcc7e71c00` است.
- backup کامل پیش از import در `/var/backups/boursnegar/20260831T192756Z-issuer-profile-batch3-before-import.dump` با اندازهٔ ۱۵۳۰۲۷۲۳۲ بایت و SHA-256 `60043e464c182a2286de4b7d0b457372ea54d0c1d12aa705d86a2c70fcfea1e5` ساخته و بررسی شد. پس از retention فقط backupهای batch2 و همین batch3 باقی ماندند.
- dry-run، apply و replay دوم importer موفق شدند؛ رکورد `VERIFIED` کچاد در Production و endpoint نماد با URL و checksum درست مشاهده شد. health/ready وب و observer موفق ماندند و مصرف دیسک ۶۵٪ ثبت شد.
- هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد. گیت بعدی، ادامهٔ جمع‌آوری رسمی با checksum مستقل است؛ گیت‌های پوشش داده، اطمینان تحلیلی و E2E نشست مجاز همچنان باز هستند.

## 2026-08-31 - batch چهارم پروفایل هویت رسمی: فملی و شتران

- صفحات HTTPS رسمی `https://www.nicico.com/` و `https://www.torc.ir/` نام شرکت ملی صنایع مس ایران/فملی و پالایش نفت تهران/شتران را نشان دادند؛ HTML خام و لوگوی همان دامنه‌ها در `artifacts/issuer-profiles-20260831-batch4/` ذخیره شد.
- manifest مستقل `artifacts/issuer-profiles-20260831-batch4/manifest.json` با SHA-256 `f98eb2c741d62d9679ceab676f9a1cc3744e16fbd0040002f06133b5694c5f26` شامل دو رکورد `VERIFIED` است. checksum HTML فملی `f84e14fb174f53834f38f4a2f6d21603c12ce852c80543b59c863e273a3862de` و شتران `9af4531d43e7aab35362d3f3ca930368cbb1dacbc1c5beab3c03e6db5087d752` است؛ checksum لوگوها نیز در manifest ثبت شده‌اند.
- backup کامل پیش از import در `/var/backups/boursnegar/20260831T193220Z-issuer-profile-batch4-before-import.dump` با اندازهٔ ۱۵۳۰۲۷۳۵۹ بایت و SHA-256 `249db86a161f7f1ca7c60bf3f7d432a6c02a68f4ddfbd0964c84fcc75cd31fd5` ساخته و بررسی شد. پس از retention فقط backupهای batch3 و همین batch4 باقی ماندند.
- dry-run، apply و replay دوم importer موفق شدند؛ رکوردهای `VERIFIED` فملی و شتران در Production و endpointهای نماد با URL و checksum درست مشاهده شدند. health/ready وب، observer و retention موفق ماندند و مصرف دیسک ۶۵٪ ثبت شد.
- هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد. گیت بعدی ادامهٔ جمع‌آوری رسمی با checksum مستقل است؛ گیت‌های پوشش داده، اطمینان تحلیلی و E2E نشست مجاز همچنان باز هستند.

## 2026-08-31 - batch پنجم پروفایل هویت رسمی: شبندر و رمپنا؛ رد گیت فارس

- صفحات HTTPS رسمی `https://www.baorco.ir/fa`، `https://pgpic.ir/` و `https://mapnagroup.com/` با شواهد HTML و لوگوی هم‌دامنه جمع‌آوری شدند. شواهد فارس عمداً حفظ شده‌اند، اما به‌دلیل نبود alias/ناشر فعال قابل‌تطبیق در catalog Production، وارد manifest اعمالی نشدند؛ درخواست API نماد فارس نیز 404 بود.
- manifest جمع‌آوری کامل در `artifacts/issuer-profiles-20260831-batch5/manifest.json` و manifest قابل‌اعمال دو نماد در `artifacts/issuer-profiles-20260831-batch5/manifest-importable.json` با SHA-256 `f9325194a705c050ef141689e1a0611dd4ec6a64eef09146438f1d33fab39803` ثبت شد. checksum شواهد هر سه مورد در manifestهاست.
- backup کامل پیش از تلاش import در `/var/backups/boursnegar/20260831T193704Z-issuer-profile-batch5-before-import.dump` با اندازهٔ ۱۵۳۰۲۷۵۶۳ بایت و SHA-256 `453b8dccee1133288bafa866ec8dc117a3b2f1d616aeaec2196b5b0387a570e5` ساخته و بررسی شد. تلاش اولیه با فارس به‌صورت تراکنشی rollback شد؛ سپس import دو نماد شبندر و رمپنا با همین backup معتبر انجام گرفت. retention فقط backupهای batch4 و همین batch5 را نگه داشت.
- dry-run، apply و replay دوم برای شبندر و رمپنا موفق شدند؛ رکوردهای `VERIFIED` و endpointهای زندهٔ هر دو نماد URL و checksum درست را برگرداندند. health/ready وب، observer و retention موفق ماندند و مصرف دیسک ۶۵٪ ثبت شد.
- فارس به‌عنوان `REJECTED_FOR_MAPPING` باقی می‌ماند، نه پروفایل تأییدشده؛ تا ایجاد alias/ناشر واقعی در catalog هیچ URL یا هویتی برای آن نمایش داده نمی‌شود. هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد.

## 2026-08-31 - batch ششم پروفایل هویت رسمی: شپنا

- صفحهٔ HTTPS رسمی `https://eorc.ir/` عنوان «شرکت پالایش نفت اصفهان»، نام نماد `شپنا` و لوگوی هم‌دامنه را نشان داد. HTML و PNG خام در `artifacts/issuer-profiles-20260831-batch6/` حفظ شدند. دامنهٔ قدیمی `esfahanoil.ir` در این بررسی پایدار نبود و منبعی برای import نشد.
- manifest مستقل `artifacts/issuer-profiles-20260831-batch6/manifest.json` با SHA-256 `bcca700f8c27d3601447861d1d2060b6b39ee6f9d4bcaa69669cbcf832fcc211` شامل رکورد `VERIFIED` است؛ checksum HTML `7458ebf0508c9782204856e60f56966489ee8171afd2bd9f82e0b1c232ea81e1` و checksum لوگو `141a651b1e63511533dbd628e35c7eccda8ad1154d1c1ff6feaeaff7dcbf8913` است.
- backup کامل پیش از import در `/var/backups/boursnegar/20260831T194139Z-issuer-profile-batch6-before-import.dump` با اندازهٔ ۱۵۳۰۲۷۸۳۲ بایت و SHA-256 `0248150d232d29865caa5768566b58ff490efed423a6c0f02e38a25e3cace3ad` ساخته و بررسی شد. پس از retention فقط backupهای batch5 و همین batch6 باقی ماندند.
- dry-run، apply و replay دوم importer موفق شدند؛ رکورد `VERIFIED` شپنا و endpoint زنده با URL و checksum درست مشاهده شد. health/ready وب، observer و retention موفق ماندند و مصرف دیسک ۶۵٪ ثبت شد.
- کگل به‌دلیل ناسازگاری hostname گواهی TLS در `golgohar.com` و `www.golgohar.com` وارد نشد؛ فارس همچنان پشت گیت mapping است. هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد.

## 2026-08-31 - batch هفتم پروفایل هویت رسمی: وپارس و وبصادر

- صفحهٔ رسمی بانک پارسیان در `https://parsian-bank.ir/` با canonical همان دامنه و redirect به زیرساخت رسمی خدمات، نام بانک پارسیان و لوگوی همان مقصد را نشان داد. صفحهٔ رسمی بانک صادرات در `https://www.bsi.ir/Pages/Home.aspx` نام بانک صادرات ایران و لوگوی هم‌دامنه را نشان داد.
- manifest مستقل `artifacts/issuer-profiles-20260831-batch7/manifest.json` با SHA-256 `a3e24230b8a71dae9f803bcf10bba37addd71d58aa8aabfb83a0ed6008857cae` شامل دو رکورد `VERIFIED` است؛ checksum شواهد هر دو در manifest ثبت شده‌اند.
- backup کامل پیش از import در `/var/backups/boursnegar/20260831T194710Z-issuer-profile-batch7-before-import.dump` با اندازهٔ ۱۵۳۰۲۷۹۵۲ بایت و SHA-256 `77baec2097b1ffc5496436419c989e80c944f629416402749f8d25f3bfb11d0d` ساخته و بررسی شد. پس از retention فقط backupهای batch6 و همین batch7 باقی ماندند.
- dry-run، apply و replay دوم importer موفق شدند؛ رکوردهای `VERIFIED` و endpointهای زندهٔ وپارس و وبصادر URL و checksum درست را برگرداندند. health/ready وب، observer و retention موفق ماندند و مصرف دیسک ۶۵٪ ثبت شد.
- هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد. گیت‌های mapping فارس، TLS کگل، پوشش/اطمینان داده و E2E نشست مجاز همچنان باز هستند.

## 2026-08-31 - batch هشتم پروفایل هویت رسمی: ومعادن و تاپیکو

- صفحات HTTPS رسمی `https://mmdic.ir/` و `https://www.tappico.com/` نام شرکت و نمادهای ومعادن و تاپیکو و لوگوی هم‌دامنه را نشان دادند؛ HTML و PNG خام در `artifacts/issuer-profiles-20260831-batch8/` نگه‌داری شد.
- manifest مستقل `artifacts/issuer-profiles-20260831-batch8/manifest.json` با SHA-256 `6c513fb01080d3a4e3b9a6a0a13fc1bfa4fe2e29f5191c514eb1e81857e90c25` شامل دو رکورد `VERIFIED` است؛ checksum همهٔ شواهد در manifest ثبت شده‌اند.
- backup کامل پیش از import در `/var/backups/boursnegar/20260831T195203Z-issuer-profile-batch8-before-import.dump` با اندازهٔ ۱۵۳۰۲۸۱۹۷ بایت و SHA-256 `a9d9f559a8ec692f8791df0552884050205bdd3752385bfcf565002ef1610a64` ساخته و بررسی شد. پس از retention فقط backupهای batch7 و همین batch8 باقی ماندند.
- dry-run، apply و replay دوم importer موفق شدند؛ رکوردهای `VERIFIED` ومعادن و تاپیکو و endpointهای زنده با URL و checksum درست مشاهده شدند. health/ready وب، observer و retention موفق ماندند و مصرف دیسک ۶۵٪ ثبت شد.
- `وامید` به‌دلیل اینکه دامنهٔ محتمل `omid.com` صفحهٔ فروش دامنه بود وارد نشد. هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد؛ گیت‌های mapping فارس و TLS کگل و گیت‌های داده/احراز هویت همچنان باز هستند.

## 2026-08-31 - batch نهم پروفایل هویت رسمی: وامید

- صفحهٔ HTTPS رسمی `https://omidinvestment.ir/` عنوان شرکت سرمایه‌گذاری امید، نام نماد `وامید` و لوگوی هم‌دامنه را نشان داد. این دامنه پس از بررسی مستقل جایگزین گزینهٔ قبلی `omid.com` شد که صفحهٔ فروش دامنه بود؛ آن گزینه هرگز وارد Production نشده بود.
- manifest مستقل `artifacts/issuer-profiles-20260831-batch9/manifest.json` با SHA-256 `8c336ce4ea79847703a2ad97b34e18ec01bccc6e083be15ec0b1da8ad51117fd` شامل رکورد `VERIFIED` است؛ checksum HTML `d90847058d6b3efa942e9357fbf6d39e4c92b1ff1c19e0281a8faf4d4fd4507c` و checksum لوگو `bcccd2331de3ea2c7c4f071193a4837edfc201a12a6a7719a2ab9f7f88ac711b` است.
- backup کامل پیش از import در `/var/backups/boursnegar/20260831T195645Z-issuer-profile-batch9-before-import.dump` با اندازهٔ ۱۵۳۰۲۸۴۴۶ بایت و SHA-256 `990586b401ab35951b1f99f80b5cd904706a7db1ed43ea6dca2aaca1350a0e28` ساخته و بررسی شد. پس از retention فقط backupهای batch8 و همین batch9 باقی ماندند.
- dry-run، apply و replay دوم importer موفق شدند؛ رکورد `VERIFIED` وامید در Production و endpoint زنده با URL و checksum درست مشاهده شد. health/ready وب، observer و retention موفق ماندند و مصرف دیسک ۶۵٪ ثبت شد.
- سایپا و بانک تجارت در این نوبت پاسخ پایدار/قابل‌اثبات ندادند و وارد نشدند. هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد؛ گیت‌های mapping فارس، TLS کگل، پوشش/اطمینان داده و E2E نشست مجاز همچنان باز هستند.

## 2026-08-31 - اصلاح شمارش پروفایل‌های VERIFIED و گیت mapping فارس

- ممیزی read-only زندهٔ `issuer_profiles` تعداد واقعی `VERIFIED=14` را نشان داد. فهرست یکتای فعلی: `فولاد، شستا، خودرو، کچاد، فملی، شتران، شبندر، رمپنا، وپارس، وبصادر، ومعادن، تاپیکو، وامید، شپنا`. گزارش‌های مکالمه‌ای قبلی که عدد ۱۵ را اعلام کرده بودند یک خطای شمارش داشتند؛ این اصلاحیه مرجع عدد جاری است.
- برای `فارس` در جداول `symbol_aliases/instruments/issuers` هیچ alias فعال یا ناشر قابل‌تطبیقی وجود ندارد؛ بنابراین صفحهٔ رسمی `pgpic.ir` فقط به‌عنوان evidence جمع‌آوری‌شده باقی می‌ماند و هیچ profile برای فارس ساخته نمی‌شود. این گیت mapping مستقل از گیت TLS کگل است.
- این ممیزی هیچ mutation، import، restart یا حذف artifact انجام نداد. هیچ دادهٔ مالی، URL، تصویر یا هویت حدسی وارد نشد.

## 2026-08-31 - recovery94: ممیزی گستردهٔ شش گیت داده‌ای با مرورگر محلی

- جست‌وجوی محلیِ browser/Codal برای `سفارود، ثقزویح، گنگین، ولاناح، نیروترانسفو، کمرجانح` در بازهٔ `1403/01/01` تا `1405/06/09` با profile و checkpoint مستقل اجرا شد؛ capture manifest در `artifacts/recovery94-broad-browser/manifest.json` با SHA-256 `cfece11dc19212a6ffafe7f0fe386879b87d2a3cd63089933c13fc7fc8f24cca` ثبت است.
- پنج نماد `ثقزویح، گنگین، ولاناح، نیروترانسفو، کمرجانح` با وضعیت `NO_NOTICES` برگشتند. `سفارود` سه notice رسمی داشت، اما عناوین فقط مکاتبه/تعلیق/رأی ورشکستگی بودند و هیچ صورت مالی یا رکورد تحلیلی قابل‌قبول ارائه نکردند؛ بنابراین طبقه‌بندی آن `NOTICE_ONLY` است، نه پوشش مالی.
- normalizer با صفر `records`، صفر `source_documents` و صفر `errors` تمام شد. manifest نرمال‌سازی `artifacts/recovery94-broad-normalized/manifest.json` با SHA-256 `51e5756c14728670dc7347a6872262accf8031652a202ab573106ceed7d7f5fd` و گزارش ممیزی `artifacts/audits/recovery94-broad-no-financial-statements-20260831.json` ثبت شدند.
- هیچ import، backup، restart، snapshot mutation یا تغییر Production انجام نشد. گیت `NO_KNOWN_DATA_GATE` برای پنج نماد و گیت `NOTICE_ONLY` برای سفارود همچنان باز هستند؛ هیچ داده یا coverage ساختگی از این recovery نتیجه‌گیری نمی‌شود.

## 2026-08-31 - reconciliation و کنترل نهایی پس از recovery94

- registry عملیاتی recovery91 با `reconcile_public_gate_registry.py` بازتولید شد و هیچ اختلافی با گیت‌های ثبت‌شده نداشت: `ANALYTICAL_CONFIDENCE_GATE=322`، `SNAPSHOT_COVERAGE_GAP=300`، `NO_KNOWN_DATA_GATE=9` و `RECOVERY_CLOSED=14`. خروجی JSON در `artifacts/audits/public-645-gate-registry-20260831-recovery94-reconciled.json` با SHA-256 `005df21516d485b2d1a2bae05610da4c47385567070a8b6f5fb9462e25898dda` و CSV با SHA-256 `ea0f9067964003b7c3bcf5e2e9671f91b88c589285cd739b534975649792e368` ثبت شد.
- آزمون‌های data-service با ۱۰۴ تست موفق شدند. تست وب با ۸ فایل و ۷۵ تست، typecheck و build Production نیز موفق شدند. خطای نخست فقط به‌دلیل ارسال گزینهٔ ناسازگار `--runInBand` به Vitest بود و با دستور استاندارد پروژه تکرار شد.
- وضعیت زندهٔ Production در کنترل نهایی: `bourse-app` آنلاین با cwd `/var/www/boursnegar-current`، سرویس data فعال، API health با HTTP 200، timer روزانه enabled و دیسک ۶۵٪. فقط دو dump معتبر اخیر در `/var/backups/boursnegar` باقی است: batch8 و batch9.
- هیچ import، restart، حذف backup یا mutation داده انجام نشد. recovery داده‌ای تا زمان وجود evidence والد/دورهٔ معتبر ادامه دارد؛ گیت‌های اطمینان و پوشش عمداً به تصمیم قطعی تبدیل نشده‌اند.

## 2026-08-31 - تفکیک self-check عمومی از سلامت واقعی Production

- کنترل نهایی روی origin موفق بود: Nginx روی پورت‌های ۸۰/۴۴۳ فعال است، `nginx -t` موفق شد، `/healthz` روی origin با HTTPS و `/readyz` روی Node وضعیت آماده برگرداند، data-service روی `127.0.0.1:8001` با `{"status":"ok"}` پاسخ داد و observer نصب‌شدهٔ Production مقدار `BOURSNEGAR_OBSERVER=PASS disk=65% rows=50 coverage_min=42.86 coverage_max=100 coverage_100=43` ثبت کرد.
- self-check از داخل خود سرور به `https://boursnegar.ir/healthz` در ۲۰ ثانیه timeout شد، اما درخواست همان دامنه از سیستم فعلی HTTP 200 و پاسخ Cloudflare/برنامه گرفت. بنابراین این مورد به‌عنوان محدودیت مسیر loopback سرور به Cloudflare ثبت شد، نه خرابی عمومی سایت؛ هیچ تغییر، restart یا تغییر DNS انجام نشد.
- این distinction برای ممیزی‌های بعدی الزامی است: سلامت origin و observer جدا از اثبات دسترسی عمومی سنجیده شوند و timeout self-check به‌تنهایی مبنای rollback یا ادعای قطعی سایت نباشد.

## 2026-08-31 - ممیزی کامل ledger اسناد orphan و ثبت فایل‌های حذف‌شده

- ابزار `audit_orphan_financial_documents.py` اصلاح شد تا ارجاع ledger به فایل حذف‌شده را به‌عنوان `MISSING_ARTIFACT` ثبت کند و ممیزی سایر اسناد را متوقف نکند. این رفتار با یک تست مستقل در `data-service/tests/test_audit_orphan_documents.py` پوشش داده شد.
- ممیزی کامل query `--only-with-facts` روی ledger محلی ۱۲۰۸ ردیف را بررسی کرد: ۱۲۰۲ مورد `MISSING_ARTIFACT`، ۶ مورد `PARSED_WITH_FACTS`، و هیچ candidate جدید آمادهٔ promotion نبود. در کل جدول parse پس از ممیزی، وضعیت‌ها `MISSING_ARTIFACT=1282`، `PARSED_NO_CORE_FACTS=1304`، `PARSED_WITH_FACTS=578` و `PARSE_FAILED=121` هستند؛ orphan candidateها `DUPLICATE_EXISTING=8292` و `NEEDS_DISAMBIGUATION=618` هستند.
- گزارش ممیزی در `artifacts/audits/local-parser-orphan-audit-20260831.json` با SHA-256 `1537ec9e6df016e564fa37e2b400ca921bb21df8d285c6fd832432e12a038d56` ثبت شد. نبود فایل به‌عنوان نبود evidence حفظ شده و هیچ fact حدسی یا candidate مبهم وارد Production نشد.
- این تغییر و ممیزی فقط روی ledger/فایل‌های Local بود؛ هیچ import، backup، restart یا mutation Production انجام نشد. گیت promotion تا فراهم‌شدن فایل و linkage مستقل باز می‌ماند.

- پس از اصلاح، کل مجموعهٔ تست data-service با ۱۰۵ تست موفق شد؛ JSON ممیزی معتبر و `git diff --check` نیز بدون خطا بودند و `project-memory-check.sh` وضعیت `CURRENT_STATE: OK` و `PROJECT_MEMORY_PROTOCOL: OK` داد.

## 2026-08-31 - بازبینی linkage اسناد قابل‌parse و جلوگیری از promotion مبهم

- `link_orphan_candidates.py` اصلاح شد تا برای فایل‌های filename-linked، اگر JSONL هم‌جوار title نداشت، title رسمیِ داخل HTML workbook را بخواند و scope را فقط در صورت وجود evidence تعیین کند. اجرای قابل‌بازتولید روی ledger، ۵۷۵ فایل parse‌شده را دید: ۴ لینک موجود، ۵۷۱ مسیر بدون artifact؛ هیچ مورد ambiguous باقی‌مانده برای لینک‌دهی جدید تولید نشد.
- پس از linkage، ۳۷ ردیف fact در وضعیت `READY_FOR_NORMALIZATION` باقی ماندند، اما فقط ۷ ردیف از نظر scope eligible بودند و promotion dry-run برای آن‌ها `inserted=0` داد؛ یعنی همه با fact موجود duplicate بودند. سه سند filename-linked فاقد title/scope قابل‌اثبات باقی ماندند و عمداً promote نشدند.
- review queue در `artifacts/audits/local-candidate-review-20260831.csv` با SHA-256 `4b47368bc80a06792c38b0fec5eaed1f5565d610d84019dcc22afb570b420ad5` به‌روزرسانی شد. هیچ fact جدید، import Production، backup deletion یا mutation Production انجام نشد.

## 2026-08-31 - ممیزی زندهٔ all-active و تفکیک scope گیت‌ها

- ممیزی مستقیم دیتابیس Production با runtime canonical در `/var/www/boursnegar-data-current` انجام شد و خروجی در `artifacts/audits/coverage-all-active-20260831-live.json` با SHA-256 `0bd63d32191381f3ba9609e2e68019f51e1bb12674a5b5cea5be8b908bbe7f31` و CSV در همان شاخه با SHA-256 `ceaee6dc9602a13d613bde867fab23cb3d49e71c1d52ec75a497c7cc63f5119a` ذخیره شد.
- وضعیت زندهٔ all-active شامل ۱۵۲۴ ابزار فعال، ۱۷۹۳۸ دوره، ۷۰۵۷۰ fact خام و ۳۶۶۵۲ fact معتبر است؛ tierهای معتبر فعلی `CORE_READY=721`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=384` هستند و تصمیم‌های آخر `INSUFFICIENT_DATA=1471`، `SELL=51` و `HOLD=2` ثبت شده‌اند.
- registry عمومی ۶۴۵ نماد با CSV زندهٔ all-active به‌صورت exact-symbol merge بازتولید شد. خروجی `artifacts/audits/public-645-gate-registry-20260831-live-reconciled.json` با SHA-256 `bc496b2fff971b6bbf185db86e3a94b5eaf8d66357975597b67123165965803a` و CSV با SHA-256 `cba5694e749f890dfcf8e961966c0d6a8c5d94b62c7428bf787b215ad9194693` همان شمارش عمومی را تأیید کرد: `ANALYTICAL_CONFIDENCE_GATE=322`، `SNAPSHOT_COVERAGE_GAP=300`، `NO_KNOWN_DATA_GATE=9` و `RECOVERY_CLOSED=14`.
- این دو شمارش متناقض نیستند: all-active کل ۱۵۲۴ ابزار را پوشش می‌دهد، registry عمومی فقط universe عمومی ۶۴۵ نماد را. از این پس این دو scope و artifact نباید به‌جای یکدیگر استفاده شوند. هیچ import، restart، backup deletion یا mutation انجام نشد.

## 2026-08-31 - promotion اسناد orphan و پشتیبانی cash flow در Production

- ممیزی و linkage محلی با حفظ گیت‌های evidence انجام شد. از ۳۷ ردیف قابل‌نرمال‌سازی، فقط facts دارای period، scope و title قابل‌اثبات وارد manifest شدند؛ خروجی `artifacts/promoted-remote-20260831-v2/normalized.jsonl` با SHA-256 `48c79687ab59b5c0fdef543e9c9bd6bd44f66606a5ec9481e9a075eb23a0babb` و manifest با SHA-256 `898f1cf4360771987aabf4502497a235a7778d17163360dc6889bd3b66be81f6` ثبت شد. سه سند operating cash flow برای کپرور، ثبهساز و ثنظام با واحد مستند `IRR_million` و checksum سند در payload نگه‌داری شدند؛ هیچ مقدار یا هویتی جعل نشد.
- migration `026_codalpy_cash_flow.sql` برای پذیرش `cash_flow` در constraint جدول `codalpy_records` ساخته شد. اجرای runner عادی به‌دلیل owner بودن `web.env` و سپس خطای `must be owner of table codalpy_records` انجام نشد؛ SQL با کاربر مالک `postgres` در transaction اجرا و migration در `schema_migrations` ثبت شد. این مسیر و علت آن باید در deployهای بعدی صریحاً حفظ شود.
- import اول با constraint قبلی rollback شد. پس از migration، checksum روی سرور برای manifest و JSONL با مقادیر بالا تطبیق داشت؛ import/replay بدون validation error اجرا شد. importer سپس اصلاح شد تا `ON CONFLICT(source,source_action_id)` فقط insert نباشد و payload، واحد و مقدار همان رکورد رسمی را idempotently همگام کند. replay اصلاح‌شده ۳۷ رکورد را reconcile کرد و facts استاندارد operating cash flow با وضعیت `VALID` برای هر سه سند در DB دیده شدند.
- یک گیت واقعی باقی است: تحلیل کپرور و زبینا هنوز operating cash flow را در گزارش منتخب audited/هم‌دوره وارد نمی‌کند و برای ثبهساز و ثنظام API تحلیل گزارش resolve نمی‌کند؛ پاسخ‌ها به‌عنوان `INSUFFICIENT_DATA` یا نبود گزارش ثبت شدند و هیچ تصمیمی با دورزدن گیت داده صادر نشد. این موضوع کار بعدیِ انتخاب گزارش و mapping است، نه کمبود provenance سند.
- ممیزی زندهٔ all-active پس از import در `artifacts/audits/coverage-all-active-20260831-post-orphan-cashflow.json` با SHA-256 `663a90869dc46864a809f2248e1cf8fda0ae896a2c8231b9a31d96fd66d7f765` و CSV با SHA-256 `303ef59a24ab272ee94767337311d512616734051fa87471b1d8d312c67773ab` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۴۳ دوره، ۷۰۵۸۲ fact خام، ۳۶۶۶۴ fact معتبر، tierها `CORE_READY=721`، `FUND_MODEL_REQUIRED=419` و `MISSING_COMPARABLE_PERIODS=384` و تصمیم‌ها `INSUFFICIENT_DATA=1471`، `SELL=51` و `HOLD=2`.
- observer برابر `PASS` با disk `66%`، سرویس data فعال و `bourse-app` آنلاین بود. retention با policy `keep_2_newest_valid_custom_postgresql_dumps` اجرا شد؛ دو backup باقی‌مانده: `/var/backups/boursnegar/20260831T202557Z-orphan-cashflow-before-retry.dump` با SHA-256 `c5f8172443492e4ec89edee4f77f9f756f2979ffd85cf108cce50bef14fca6c2` و `/var/backups/boursnegar/20260831T202018Z-orphan-candidates-before-import.dump` با SHA-256 `5e1a52ac12535b20790c3b68f16c4d6faf7e09ba8196b3e3efc68a0844292555`.

## 2026-08-31 - اصلاح انتخاب گزارش حسابرسی‌شده و انتشار release پایدار

- بررسی زنده نشان داد `audited` در `_stored_financial_report` علاوه بر `fp.audited` شرط نادرست `fp.length_months = 12` داشت. این شرط برای نمادهایی که آخرین گزارش حسابرسی‌شدهٔ معتبرشان میان‌دوره‌ای است، پاسخ ۴۰۴ می‌ساخت. شرط سالانه حذف شد؛ حالت `audited` همچنان فقط facts با `fp.audited=true` و انتخاب کامل‌ترین گروه هم‌دوره را می‌پذیرد و `latest_codal` مستقل باقی ماند.
- اصلاح در release `/var/www/boursnegar-data-releases/20260831T203700Z-audited-interim-selection` منتشر و symlink `/var/www/boursnegar-data-current` به‌صورت اتمیک به آن منتقل شد. backup معتبر پیش از deploy در `/var/backups/boursnegar/20260831T203639Z-audited-interim-selection-before-deploy.dump` با اندازهٔ ۱۵۳۰۳۶۰۱۰ بایت و SHA-256 `25276c338c87856a13e814617249fde98d4bb3eb4ef51298cb3818549735c20a` ثبت و با `pg_restore -l` بررسی شد.
- آزمون زنده پس از انتشار: ثبهساز در `audited` با پوشش `100.0` و بدون missing metric پاسخ داد؛ ثنظام در `latest_codal` با پوشش `100.0` و بدون missing metric پاسخ داد؛ کپرور در `latest_codal` با پوشش `100.0` و بدون missing metric پاسخ داد. حالت audited برای کپرور به‌درستی نبود cash-flow در گزارش سالانهٔ حسابرسی‌شده را به‌صورت `INSUFFICIENT_DATA` نگه داشت.
- health data-service (`/health`)، readiness وب (`http://127.0.0.1:3000/readyz`)، observer و PM2 موفق بودند. `/readyz` روی پورت ۸۰۰۱ عمداً endpoint نیست و ۴۰۴ آن خرابی سرویس داده محسوب نمی‌شود.
- retention ابتدا هنگام وجود پردازش backup محافظه‌کارانه متوقف شد؛ پس از نبودن `pg_dump/pg_restore` فعال، با policy دو dump اجرا شد. گزارش در `artifacts/audits/production-backup-retention-20260831T203820Z.tsv` با SHA-256 `57c141b1dc11cee1cf09d67e5ffb8a1f331774f1e5cd4e1706ecb840786ee999` ثبت است. دو dump فعلی: backup جدید بالا و `/var/backups/boursnegar/20260831T202557Z-orphan-cashflow-before-retry.dump` با SHA-256 `c5f8172443492e4ec89edee4f77f9f756f2979ffd85cf108cce50bef14fca6c2`.

## 2026-08-31 - recovery95 برای گیت NO_KNOWN_DATA

- جست‌وجوی رسمی browser/Codal در Local برای ۹ نماد `وثوق، فن افزار، سفارود، ثقزویح، گنگین، فاهواز، ولاناح، نیروترانسفو، کمرجانح` در بازهٔ `1403/01/01` تا `1405/06/09` با checkpoint و manifest مستقل اجرا شد. manifest capture در `artifacts/recovery95-no-known-browser/manifest.json` با SHA-256 `0db729703476d48552c81729793331beb173eb1dd3f3cd2e05479bf10202a9df` و checkpoint با SHA-256 `8ee069baeef7a6fce934d055749a085ee379c120607c5cf6ff8dc4ba20a2511d` ثبت است؛ خطای browser صفر بود.
- `وثوق` ۲۰ notice و `فاهواز` ۲۰ notice داشتند، اما هیچ‌کدام صورت مالی رسمی قابل‌استخراج در این جست‌وجو نبودند؛ `سفارود` ۳ notice غیرمالی داشت. شش نماد `فن افزار، ثقزویح، گنگین، ولاناح، نیروترانسفو، کمرجانح` بدون notice برگشتند. نتیجهٔ نرمال‌سازی صفر record، صفر source document و صفر error بود؛ manifest نرمال‌سازی همان artifact معتبر قبلی با SHA-256 `51e5756c14728670dc7347a6872262accf8031652a202ab573106ceed7d7f5fd` است.
- گزارش audit در `artifacts/audits/recovery95-no-known-data-20260831.json` با SHA-256 `27de604d076239de55c5bd4f987772437026e7611396aae602050a3a9c4f97aa` نگه‌داری شد. classification گیت‌ها صادقانه باقی ماند: دو نماد `NOTICE_ONLY` و شش نماد `NO_NOTICES`; هیچ import، backup، refresh snapshot یا mutation Production انجام نشد. `وثوق` و `فاهواز` از نظر evidence دیگر صرفاً «بدون دادهٔ شناخته‌شده» نیستند، اما تا صورت مالی رسمی همچنان وارد تحلیل نمی‌شوند.

## 2026-08-31 - recovery96، refresh snapshot از facts موجود

- فهرست دقیق ۳۰۰ نماد گیت `SNAPSHOT_COVERAGE_GAP` از registry استخراج و در `artifacts/recovery96-snapshot-refresh-symbols.txt` ثبت شد. پیش از هر mutation، backup کامل Production در `/var/backups/boursnegar/20260831T204155Z-snapshot-refresh-before.dump` با اندازهٔ ۱۵۳۰۳۹۷۷۱ بایت و SHA-256 `6abeabc3bd52d797e8450beb3903cd8ea057bf1f9283392a76a2c0c821bfb060` ساخته و با `pg_restore -l` بررسی شد.
- اسکریپت `refresh_internal_snapshots.py` ابتدا در release نبود و اجرای آن بدون mutation با خطای فایل گمشده متوقف شد؛ اسکریپت Local با SHA-256 `4ca12bf173fc1a7a6c89fb9b71dc983097cf1944d99edf79f1465c09a5ab98a9` به release فعال افزوده شد. اجرای checkpoint‌دار پس از آن برای هر ۳۰۰ نماد موفق شد (`ok=300`, `errors=0`) و فقط از endpoint داخلی data-service و facts واردشده استفاده کرد؛ هیچ تماس یا دانلود Codal انجام نشد.
- audit all-active پس از refresh در `artifacts/audits/coverage-all-active-20260831-recovery96.json` با SHA-256 `972c8274bb4d221756bb828345e8c419d24924a8e50d276547cf9bacf8c7b347` و CSV با SHA-256 `7d7ed0d04a64bcd63e141c40c75974639a67d2ca743519e45b494a3f2b623526` ثبت شد. tierها ثابت ماندند (`CORE_READY=721`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=384`) اما تصمیم‌های latest از `INSUFFICIENT_DATA=1471, SELL=51, HOLD=2` به `INSUFFICIENT_DATA=1383, SELL=125, HOLD=13, BUY=3` تغییر کردند؛ این تغییر فقط نتیجهٔ refresh snapshotهای مشتق‌شده است.
- registry عمومی exact-symbol با audit جدید بازتولید شد. source با SHA-256 `095c2d94ea770ba3bc036be80ca6e1974f7329aca16d1b553a709d86aed41f4c`، reconciled JSON با SHA-256 `343f8995e1b789968371cd32f9467ff3861ccd9ed9561413e9bb0e658b9115ba` و CSV با SHA-256 `5e9500abe6d0a7c80455b2132fcd21cd01d20eb3adaf6b101122be516130d7ac` ثبت شدند. شمارش گیت‌ها از `SNAPSHOT_COVERAGE_GAP=300` به `298` رسید؛ کپرور به `ANALYTICAL_CONFIDENCE_GATE` با پوشش ۱۰۰٪ و ثنظام به `RECOVERY_CLOSED` با پوشش ۱۰۰٪ و تصمیم `SELL` منتقل شد.
- retention با سیاست دو dump اجرا شد؛ دو backup فعلی `/var/backups/boursnegar/20260831T204155Z-snapshot-refresh-before.dump` با SHA-256 بالا و `/var/backups/boursnegar/20260831T203639Z-audited-interim-selection-before-deploy.dump` با SHA-256 `4f3fde6fdfc39c7b0e28cf6e26ac725ee499b915c7c0e37aceb4f5d8231a3cc0` هستند. گزارش retention در `artifacts/audits/production-backup-retention-20260831T204743Z.tsv` با SHA-256 `08eda9e2e8898036f6a94a479fecc97de2f78e0726f7cffb5e54d3fd6e93def8` ثبت شد. observer، data-service health و وب readiness سبز باقی ماندند.

## 2026-08-31 - recovery97، بازیابی cash-flow رسمی برای پنج نماد

- برای `شارپیلن، وپاسار، غالبر، غدام، دیران` جست‌وجوی browser/Codal محلی در بازهٔ `1404/01/01` تا `1405/06/09` انجام شد. capture با ۱۰۰ notice و ۳۶ سند رسمی در `artifacts/recovery97-cashflow-browser/manifest.json` با SHA-256 `6c11a66f951f0fdf8e6081546e9a2d923afb7c0bf4207bc942f8af9369897cf6` و checkpoint با SHA-256 `05d7aa9cb2c075731261cbc736023656a72a3ea786028b6f29f0aedb3a45ef19` ثبت است.
- نرمال‌سازی با parser رسمی ۱۱۲ fact و ۶ خطای retained تولید کرد. هر ۶ خطا child-entity واقعی بودند و عمداً وارد نشدند. manifest نرمال‌سازی `artifacts/recovery97-cashflow-normalized/manifest.json` با SHA-256 `455fce31721a4ad5eeab51040678128a7fc7d7b49747b401f08a864c99e50ab0` و JSONL با SHA-256 `1570c996ce342142283f5264cc3ef39717cbac608df2e06e10719dca6bf03a44` ثبت شد. شش operating cash flow رسمی با unit، title، period و document checksum در artifact وجود داشتند؛ هیچ مقدار حدسی ساخته نشد.
- backup پیش از import در `/var/backups/boursnegar/20260831T205353Z-recovery97-before-import.dump` با اندازهٔ ۱۵۳۲۶۰۷۴۵ بایت و SHA-256 `c1e4751bc20d4eb23d74d3ca0c28cd62ffebd71cef47737ea2a97361ab85c7df` ساخته و با `pg_restore -l` بررسی شد. import artifact-only با checksum/advisory lock موفق شد: `inserted=112`, `standard_facts=26`, validation error صفر؛ replay اصلاح‌شده `inserted=0`, `standard_facts=0` بود.
- refresh snapshot پنج نماد با `ok=5`, `errors=0` موفق شد. audit all-active پس از import در `artifacts/audits/coverage-all-active-20260831-recovery97.json` با SHA-256 `66857aa64fa937a04009216b0706a2bb76296dc5fc22583bac682a5bb971b0fa` و CSV با SHA-256 `63b6ec7cfcde9b0b4829802ba82a600ff0195bdb453a0a068a6d7b9d8e9f740e` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۵۵ دوره، ۷۰۶۰۸ fact خام و ۳۶۶۹۰ fact معتبر؛ tierها ثابت ماندند.
- registry exact-symbol با audit جدید به‌روزرسانی شد: source با SHA-256 `defcee554793d842bb11e60902268693cdb3c824441f7f4695e3eee14828f1cb`، reconciled JSON با SHA-256 `891e6c4237963db4fc2d7ad5458289d001bb9f640fd818ff50928384d6cafee7` و CSV با SHA-256 `1e83768fddae5d5c01bead766f2ddd2fb77963affa32f4e8d5be540d7031376a` ثبت شدند. گیت‌ها اکنون `SNAPSHOT_COVERAGE_GAP=294`، `ANALYTICAL_CONFIDENCE_GATE=325`، `RECOVERY_CLOSED=17` و `NO_KNOWN_DATA_GATE=9` هستند. غالبر و غدام بسته شدند؛ شارپیلن و دیران با پوشش ۱۰۰٪ در گیت اطمینان ماندند؛ وپاسار به‌دلیل `eps_basic` ناقص همچنان gated است.
- importer اصلاح شد تا در conflict هم provenance/واحد را reconcile کند اما شمارندهٔ `inserted` را با `RETURNING (xmax = 0)` فقط برای insert واقعی افزایش دهد. تست‌های data-service با ۱۱۱ تست موفق شدند. retention گزارش `artifacts/audits/production-backup-retention-20260831T205812Z.tsv` با SHA-256 `628ffaad32eb11763d7edb0ff40cd205de5c047d32296d83d214c39d2d72893e` را ثبت کرد؛ دو backup فعلی recovery97 و snapshot-refresh هستند. observer، health و readiness سبز باقی ماندند.

## 2026-08-31 - recovery98، cash-flow رسمی و اصلاح هویت نمادها

- batch اولیه با دو نام تایپی فارسی اجرا شد و فقط روی Local ماند؛ هیچ artifact آن وارد زنجیرهٔ import نشد. سپس نام‌های دقیق `اسیاتک` و `حتاید` مستقیماً از registry استخراج و capture تکمیل شد. این خطا به‌عنوان تجربهٔ عملیاتی ثبت شد: نام نمادهای فارسی در command دستی ممنوع؛ همیشه از registry/فایل ماشینی استفاده شود.
- capture نهایی `وخاور، وسینا، وپست، حتوکا، حتاید، اسیاتک` در `artifacts/recovery98-cashflow-browser/manifest.json` با SHA-256 `36224cda686c866e3084966719a3841c5e928bd4ebb09c94e0fe2e00d1b1517d` و checkpoint با SHA-256 `16fdc3950cc60959ad52372d4d5574487767c26e1601dc17e3e4acc5621704af` ثبت شد. نام دقیق registry برای اسیآتک در artifact به شکل `اسیاتک` ذخیره شده است؛ هویت دیگری ساخته نشد.
- نرمال‌سازی ۷۹ fact و ۴۷ سند رسمی داشت و ۸ خطای retained تولید کرد: child-entityهای واقعی و یک workbook فاقد جدول. manifest نرمال‌سازی `artifacts/recovery98-cashflow-normalized/manifest.json` با SHA-256 `259019d66d255a4a1d6fa227ec5cd7bb535ea56d46337a5b9be54620dcfa0df9` و JSONL با SHA-256 `f193c27d68b97406b7c6aee715ef1c876f8fa5b6589ec1e0c1dd2cd5786056a2` ثبت شد؛ دادهٔ ردشده وارد نشد.
- backup پیش از import در `/var/backups/boursnegar/20260831T210726Z-recovery98-before-import.dump` با اندازهٔ ۱۵۳۲۸۶۴۰۵ بایت و SHA-256 `1c5d36d69ff1bde2ecc3b1cee511e07cfdbec4079ae700ca089b8e31bd9a29a8` ساخته و با `pg_restore -l` بررسی شد. import artifact-only با checksum/advisory lock موفق شد: `inserted=21`, `standard_facts=18`, validation error صفر؛ replay `inserted=0`, `standard_facts=0` بود.
- refresh شش نماد موفق شد (`ok=6`, `errors=0`). audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery98.json` با SHA-256 `36cc70e9696d59f5ba8f9537f907b1dfea1cc7ab67f42523e64766edebc85413` و CSV با SHA-256 `b1acbb5d7e36353b103a768f388f4779988700d0946315ac638f247f31a740ad` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۶۸ دوره، ۷۰۶۲۶ fact خام و ۳۶۷۰۸ fact معتبر. اسیآتک به پوشش ۱۰۰٪ و گیت اطمینان رسید؛ حتوکا به `RECOVERY_CLOSED` با پوشش ۱۰۰٪ رسید.
- registry exact-symbol با source SHA-256 `1ccc1cf67729095c1bb8cab20cb66b47a3954c7fefd07e522dc894e3768015e9`، JSON نهایی SHA-256 `d5de5e656920cd2f0a0b91dd2955516b23047d573390e855e12bac434ac71c01` و CSV SHA-256 `bf78b7dece336032e31879f13815aa3bb39f574c9f7485387a3813a3a0956a96` ثبت شد. گیت‌ها به `SNAPSHOT_COVERAGE_GAP=292`، `ANALYTICAL_CONFIDENCE_GATE=326`، `RECOVERY_CLOSED=18` و `NO_KNOWN_DATA_GATE=9` رسیدند. حتاید، وخاور، وپست و وسینا به‌دلیل کمبود واقعی cash-flow/EPS همچنان gated هستند.
- retention با policy دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260831T211135Z.tsv` با SHA-256 `deacf1473b06c7926db0b94d28d54eb4aa09c167bf39bd9a6fc5dc0de8fd8195` ثبت است. دو backup فعلی recovery98 و recovery97 هستند. observer، data-service health، وب readiness و ۱۱۱ تست سبز باقی ماندند.

## 2026-08-31 - recovery99، پنج نماد بعدی با evidence رسمی

- پنج نماد `خکمک، داسوه، سهگمت، غبشهر، پی پاد` به‌صورت ماشینی از registry انتخاب شدند و نام‌ها در `artifacts/recovery99-symbols.txt` با SHA-256 `3f1da8f4dfc9f07b671ea6ac4eb970b52ad76ee84dec1525304a3539eab84a87` ثبت شد. capture browser/Codal بدون خطای browser انجام شد؛ manifest با SHA-256 `fc2d91d074948372a2dd5643ef43ca31a3e0a129ba0c761d14351d284fab7537` و checkpoint با SHA-256 `18532583d67acfa2d45e8575657f31bb7951b5d13f5dc7e94e53920a960521e5` ثبت است.
- نرمال‌سازی ۱۲۹ fact از ۴۴ سند رسمی تولید کرد؛ ۴ خطای child-entity واقعی retained و خارج از import ماندند. JSONL نرمال‌شده با SHA-256 `9bced85b6f6420cf6ace2ca6dd3cd3a8dc13c59721a08c1dcfb8b4c54ff16334` و manifest آن با SHA-256 `260f0488fd863be9ffdaaa1f50591e84f6374973a23b15bc4b4897499c6ded20` ثبت شد. هشت رکورد operating cash flow رسمی با unit/title/period/checksum استخراج شدند؛ هیچ مقدار حدسی ساخته نشد.
- backup پیش از import در `/var/backups/boursnegar/20260831T211834Z-recovery99-before-import.dump` با اندازهٔ ۱۵۳۳۰۸۶۷۷ بایت و SHA-256 `0ab80e2c0525a463904eb9eab26e015734a32d38ed51df55d8df34a472904213` ساخته و با `pg_restore -l` بررسی شد. import artifact-only با checksum/advisory lock موفق شد: `inserted=24`, `standard_facts=25`, validation error صفر؛ replay واقعی `inserted=0`, `standard_facts=0` بود.
- refresh snapshot پنج نماد با `ok=5`, `errors=0` موفق شد. audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery99.json` با SHA-256 `3af4ef0d84420fccfb853c345c193ba6fe32636b871de2e60c535ff7e90835d9` و CSV با SHA-256 `7e102eb40eede3428d01b9c6db96fc06af87a9c8ca203ef14dc9974d32217207` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۷۷ دوره، ۷۰۶۵۰ fact خام و ۳۶۷۳۳ fact معتبر. registry exact-symbol source با SHA-256 `1b5294b89a03387caddd10f6e085de58c7094a106e32a93b1d84f4a0d1e2c666`، JSON reconciled با SHA-256 `5be76157260ecc993f808434fe65a824e45e7461755de0b3333ba293823b658b` و CSV با SHA-256 `a6b265f90f44d9664d080b0e1669d36f60c833a8fcca709de31d744690419bb4` ثبت شدند.
- گیت‌های عمومی اکنون `SNAPSHOT_COVERAGE_GAP=287`، `ANALYTICAL_CONFIDENCE_GATE=329`، `RECOVERY_CLOSED=20` و `NO_KNOWN_DATA_GATE=9` هستند. خکمک و سهگمت به `RECOVERY_CLOSED` رسیدند؛ داسوه، غبشهر و پی پاد پوشش ۱۰۰٪ گرفتند اما گیت اطمینانشان طبق policy حفظ شد.
- retention با policy دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260831T212241Z.tsv` با SHA-256 `c16a6f09202cdf024178d9bbbf69c8a088f65bc6e38358dce5775a1c7718c4cc` ثبت است. دو backup فعلی recovery99 و recovery98 هستند. observer، data-service health، وب readiness و ۱۱۱ تست سبز باقی ماندند.

## 2026-08-31 - recovery100، پنج نماد بعدی و رفع نوسان replay

- پنج نماد `بسویچ، بورس، دروز، سبزوا، سدشت` به‌صورت ماشینی از registry انتخاب شدند و فهرست در `artifacts/recovery100-refresh-symbols.txt` ثبت شد. capture رسمی browser/Codal بدون خطای browser انجام شد؛ manifest در `artifacts/recovery100-cashflow-browser/manifest.json` با SHA-256 `2d6c831062b9aa20e374ec7f3b6f8c4db0393c72f41ff8f08ad4634f015c9847` ثبت است. نرمال‌سازی ۱۵۶ رکورد از ۴۷ سند رسمی تولید کرد و ۷ خطای child-entity واقعی را خارج از import نگه داشت؛ manifest نرمال‌سازی با SHA-256 `27d6cb7e4a5f45352eeede4b0a4b6c82435643016898267915c0a5fc0b052715` و JSONL با SHA-256 `0953ec429ebd058da5ebfeca02a21a80b955d0d6a3795d8feb5cbebdeaa63cc0` ثبت شد.
- در artifact مشخص شد بعضی cellهای یک source action هم از HTML و هم از Excel آمده‌اند و واحد parser آن‌ها متفاوت است. importer در `data-service/scripts/codalpy_remote_import.py` اصلاح شد: برای fact استاندارد، تکرار یک `source_action_id` با انتخاب deterministic و ترجیح workbook حل می‌شود؛ artifactهای خام و مدارک رسمی حذف نشدند. backup پیش از import در `/var/backups/boursnegar/20260831T213108Z-recovery100-before-import.dump` با اندازهٔ ۱۵۳۳۳۸۶۷۶ بایت، SHA-256 `3509cf9d82f4fda33c0a38f3f26a9815997ca2ec4750300e341c617dbcdbeb46` و `pg_restore -l` موفق ثبت شد.
- import artifact-only با checksum/advisory lock انجام شد: اجرای اولیهٔ همان batch `inserted=81`, `standard_facts=107`, validation error صفر داشت. پس از اصلاح importer، replayهای تکراری واقعی `inserted=0`, `standard_facts=0` و validation error صفر دادند؛ این batch اکنون idempotent است.
- refresh داخلی snapshot برای هر پنج نماد موفق شد (`ok=5`, `errors=0`) و checkpoint در `artifacts/recovery100-refresh.json` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery100.json` با SHA-256 `1a07e86e3ddc66785d9cc4f41dc5c55aa23b1f8c1ee55263bda10db6a111c72d` و CSV با SHA-256 `c3023e775c6e879a18e8699f5b29f50a6e9bb7d7e148d080c1b3d7f021f2f61f` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۷۹۹۹ دوره، ۷۰۷۳۱ fact خام و ۳۶۸۱۵ fact معتبر. tierها `CORE_READY=721`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=384` و latest decisionها `INSUFFICIENT_DATA=1383`, `SELL=124`, `HOLD=14`, `BUY=3` هستند.
- registry exact-symbol با source SHA-256 `df26d171264265452f042dd896739b53f33b1d2cfc75df9aea87f4b52bdd149b`، JSON reconciled با SHA-256 `358d7aa82e164c634fba6d50bbca34da93ba51e0b63bc40c942e2f7664dd0ef0` و CSV با SHA-256 `39be768404883f7327f525179d2ad80a8cdd1703419616fb23f057bf15ef60f7` ساخته شد. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=282`, `ANALYTICAL_CONFIDENCE_GATE=332`, `RECOVERY_CLOSED=22` و `NO_KNOWN_DATA_GATE=9` هستند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260831T214232Z.tsv` با SHA-256 `3b72f9bdc8c355c7c127d460b644c86a559e454434c1a96ac01a6b7f4ab5e671` ثبت است. دو backup فعلی recovery100 و recovery99 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}`، وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` و ۱۱۱ تست سبز باقی ماندند.

## 2026-08-31 - recovery101، cash-flow رسمی برای چهار نماد و توقف صادقانهٔ بهیر

- پنج نماد `اپال، بایکا، بزاگرس، بهیر، تاتمس` از registry فعلی انتخاب و با endpoint زنده تأیید شدند؛ فهرست در `artifacts/recovery101-symbols.txt` با SHA-256 `ba12d645ad31b782af7e1595e332d0dbb633c32e738c183ee1c11bdaa496e522` ثبت است. capture browser/Codal محلی با manifest `artifacts/recovery101-cashflow-browser/manifest.json`، SHA-256 `b1e2fe692d8fdfa15c4f5fb9eca91498b711286069784231398b0ae837ea7469` و checkpoint با SHA-256 `d7344da060fb66a6a6b02334b620934c8ddce2368976be951370d1b0bf9f141c` بدون خطا کامل شد.
- نرمال‌سازی ۱۸۰ fact از ۱۱۲ سند رسمی تولید کرد و ۴ خطای child-entity واقعی را خارج از import نگه داشت. چهار نماد اپال، بایکا، بزاگرس و تاتمس cash-flow رسمی قابل‌قبول داشتند؛ برای بهیر چنین evidenceی به‌دست نیامد و مقدار حدسی ساخته نشد. manifest نرمال‌سازی با SHA-256 `399e074c2ff78312c50eccf7680b59959acf70344ec03d1660207468f5b89ccb` و JSONL با SHA-256 `1e7093e393e02753b10719c47d7e79555e4fdba544f14fd51981313b110fc237` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260831T221601Z-recovery101-before-import.dump` با اندازهٔ ۱۵۳۳۸۵۵۳۴ بایت، SHA-256 `fc6ebbb2bfa7a3513607903f45bcef1864db5d7b9d01e5801b2ec3b30c400896` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=60`, `standard_facts=60`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot برای پنج نماد با `ok=5`, `errors=0` انجام شد. audit all-active در `artifacts/audits/coverage-all-active-20260831-recovery101.json` با SHA-256 `a564345185f017949b228ec40baa07dee0bebd317a3e77382e04b24530376e95` و CSV با SHA-256 `e4e766b520630e9cde63ab2490a3b435a66f47dc7fb282c7ee54044741ef2de2` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۱۸ دوره، ۷۰۷۹۱ fact خام و ۳۶۸۷۵ fact معتبر. اپال، بایکا، بزاگرس و تاتمس به پوشش ۱۰۰٪ رسیدند؛ بهیر با پوشش ۸۵٫۷۱٪ و کمبود واقعی `operating_cash_flow` gated باقی ماند.
- registry exact-symbol با source SHA-256 `f469f93093fcab3eb9170e83d215b9c1c94d945cc235d2a8e6f7132de7dac8d5`، JSON reconciled با SHA-256 `a89ab87b2363945b335589a1425380e26ae6c6c1ae3bbadaa9464e272d707c66` و CSV با SHA-256 `9f8807da74a2f5837bcc13bcb6f69bb32efe08112b807bffebe408f43ba4fea4` ثبت شد. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=278`, `ANALYTICAL_CONFIDENCE_GATE=332`, `RECOVERY_CLOSED=26` و `NO_KNOWN_DATA_GATE=9` هستند.
- retention با policy دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260831T222022Z.tsv` با SHA-256 `c1704bb9c1dd9f491832f3cb56d27b7b1c1a729cf41feb2b5141b21985f5a8fd` ثبت است. دو backup فعلی recovery101 و recovery100 هستند. observer `PASS` با disk `65%`، data-service health، وب readiness و ۱۱۱ تست سبز باقی ماندند.

## 2026-09-01 - recovery102، cash-flow رسمی برای پنج نماد

- پنج نماد `آبین، آسیا، اوان، اپرداز، بانیان` بر اساس registry و تحلیل زنده انتخاب شدند؛ هر پنج نماد در شروع recovery کمبود `operating_cash_flow` داشتند. فهرست در `artifacts/recovery102-symbols.txt` با SHA-256 `c00f348c19b54f6f0f179b8b1a67dccca40fc33aa85e8a0eb265f7fb519f7bb5` ثبت است. capture browser/Codal محلی با manifest `artifacts/recovery102-cashflow-browser/manifest.json` و SHA-256 `d5a45779a3181d2b633518c46ae13569fb725486c2b2c86c7cff7cfeeca1aa6f` و checkpoint با SHA-256 `d5dca1dc29a2e531aef430d37ab8b1e9390a9839b00f498ec55f1016a5768258` بدون خطای browser کامل شد.
- نرمال‌سازی ۱۵۲ fact از ۱۲۵ سند رسمی تولید کرد و ۹ مورد را خارج از import نگه داشت: چهار workbook آبین فاقد جدول و پنج اطلاعیه child-entity بودند. برای هر پنج نماد cash-flow رسمی در artifactهای قابل‌قبول وجود داشت؛ هیچ مقدار حدسی ساخته نشد. manifest نرمال‌سازی با SHA-256 `216a50b2245400bab319bd5201ef07498ee9c39eabfbf464ebaefd1435e05c1c` و JSONL با SHA-256 `b4c0531e206ed0a7bfcbc4e3a8b95434128780cd5b186800492e65218977ea56` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260831T225337Z-recovery102-before-import.dump` با اندازهٔ ۱۵۳۴۴۳۱۱۰ بایت، SHA-256 `ff3467628a637d9f8b8638e2a9e7c3a5b17e80912d646bbb970c90f8a6e0503e` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=28`, `standard_facts=32`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot هر پنج نماد با `ok=5`, `errors=0` انجام شد. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery102.json` با SHA-256 `2cc9906518f4c47d85482e084ecd9e715a95c6497ca0334e0375912f8188984c` و CSV با SHA-256 `eac97c8710ca58a5ce4f3b0d93f5296ba008cce7c247aa1971b721ebaa571372` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۲۸ دوره، ۷۰۸۱۹ fact خام و ۳۶۹۰۷ fact معتبر. هر پنج نماد پوشش ۱۰۰٪ گرفتند؛ آبین به‌دلیل ۸ fact معتبر همچنان در گیت اطمینان باقی ماند.
- registry exact-symbol با source SHA-256 `2321bfea9f184703d1ccaee48630ce7802c4e1b3292bbde72f41e54a35ceb08b`، JSON reconciled با SHA-256 `16202707a43aad02bbf42190477507512f44748e052d6a4845c8a1a4ca473923` و CSV با SHA-256 `d7702d1dc41f3a158bf968479efcb4e06f611cbf5a6731a03fbacb40dc1f8b1c` ثبت شد. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=273`, `ANALYTICAL_CONFIDENCE_GATE=336`, `RECOVERY_CLOSED=27` و `NO_KNOWN_DATA_GATE=9` هستند.
- retention با policy دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T041858Z.tsv` با SHA-256 `d2db2b68f03e224e1db664bae4a7d8416a07e36f4a46a483f8917fdd5f4caa8d` ثبت است. دو backup فعلی recovery102 و recovery101 هستند. observer `PASS` با disk `65%`، data-service health، وب readiness و ۱۱۱ تست سبز باقی ماندند.

## 2026-09-01 - recovery103، cash-flow رسمی برای پنج نماد

- پنج نماد `بشهاب، بپویا، بکهنوج، تجلی، تلیسه` از registry زنده انتخاب شدند؛ فهرست در `artifacts/recovery103-symbols.txt` با SHA-256 `57bdd23e84e1c3aa058dfc2e7a60caa1e5c14e46cf3e98e6c027e7df87cded70` ثبت است. capture محلی browser/Codal در بازهٔ `1404/01/01` تا `1405/06/09` برای هر پنج نماد کامل شد؛ manifest با SHA-256 `dbcebe0a15bf6644da4f7de5804f3b20247fab6f73c04174c0ddbc520423c14f` و checkpoint با SHA-256 `311412e2945498beb6d9e952b2fa7eae19e291e3ae25fb9595d96a7837bd8f82` و خطای browser صفر ثبت شدند.
- نرمال‌سازی ۱۸۶ fact از ۱۳۵ سند رسمی تولید کرد و ۶ مورد را خارج از import نگه داشت: یک child-entity واقعی برای بپویا و پنج workbook تلیسه فاقد جدول معتبر. برای هر پنج نماد cash-flow رسمی قابل‌قبول در artifactها وجود داشت؛ هیچ مقدار حدسی یا هویت جعلی ساخته نشد. manifest نرمال‌سازی با SHA-256 `a6e6d10240dcdfa48d1af62ae1edd6521e8751e714031e325fa298ebe883dea2` و JSONL با SHA-256 `896853290a6fb2b92a46bd57f9e7754c9c96e76243b3d4db8b9bbfa41f9c5d66` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T045814Z-recovery103-before-import.dump` با اندازهٔ ۱۵۳۴۸۵۲۴۲ بایت و SHA-256 `45e963ff1b94ca65a7012bd4c5464c37eff82289b804e86f121e1eb3641ef196` ساخته و با `pg_restore -l` بررسی شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=27`, `standard_facts=24`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot برای پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery103-refresh.json` با SHA-256 `a7f8be5731dee0e81ba17c45dc5643993190bf254cb447b6275f6e77729fe42c` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery103.json` با SHA-256 `dd1f8d17af4491c9ab2fcac0997713bfba8993deeaf5b06557e74d1babc782a8` و CSV با SHA-256 `b7197642f0bea30c290328a98859645029e18d1fb2283371918f475772f79cc2` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۳۶ دوره، ۷۰۸۴۳ fact خام و ۳۶۹۳۱ fact معتبر. tierها ثابت ماندند (`CORE_READY=721`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=384`) و تصمیم‌ها `INSUFFICIENT_DATA=1383`, `SELL=124`, `HOLD=14`, `BUY=3` هستند. هر پنج نماد پوشش ۱۰۰٪ گرفتند؛ بشهاب و تلیسه به‌دلیل کمبود facts معتبر کافی همچنان `INSUFFICIENT_DATA` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `b83f76f3a7159a5f0cf361bd5753b964970eb7fc106ccde225c2a318f17e1eff`، JSON reconciled با SHA-256 `61a45a5afa3ae6c47620dcb2c58a4f36fd4db3300ea08be996aab0cd50ec3af4` و CSV با SHA-256 `97976dcdf6199b84f8646da2a3157f64fad8265741814ba885f2743d81a60fe9` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=268`, `ANALYTICAL_CONFIDENCE_GATE=338`, `RECOVERY_CLOSED=30` و `NO_KNOWN_DATA_GATE=9` هستند؛ policy رجیستری مقدار source قبلی را نیز جداگانه حفظ کرده است.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T050331Z.tsv` با SHA-256 `78e2bd6d1d86fc834edfd5e595fcb0e0708533d64142ae84caeb7bcabf889c5a` ثبت شد. دو backup فعلی recovery103 و recovery102 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery104، cash-flow رسمی برای پنج نماد

- پنج نماد `تپسی، ثرود، حریل، خپویش، سفار` بر اساس گیت زندهٔ `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery104-symbols.txt` و فهرست refresh با SHA-256 مشترک `b91af5f8968be147d8c5526f1f7348bf1cd0e3efb87ee78a98ca348458ce66dc` ثبت است. دو تلاش اولیهٔ browser روی دانلود نیمه‌تمام متوقف شدند و هیچ checkpoint معتبر یا importی از آن‌ها انجام نشد؛ artifactهای ناقص حذف نشدند. تلاش موفق فقط‌ـExcel با منبع `browser/codal.ir`، ۵ فایل JSONL و ۱۰۰ notice در `artifacts/recovery104-cashflow-browser-retry2/` ثبت شد؛ manifest با SHA-256 `891d0b71bdabeed84813df28541c5ffbe7b6c8aea02e7d06537357d36da77ae6` و checkpoint با SHA-256 `6010e112f48183902f6f355b92ff15bcc946b6eeea67595643089dc797c93468` و خطای browser صفر هستند.
- نرمال‌سازی ۱۷۰ fact از ۴۲ سند رسمی تولید کرد و یک مورد child-entity واقعی تپسی (`1548911`، شرکت نوآفرینان بهراد پارس) را خارج از import نگه داشت. هر پنج نماد fact استاندارد `operating_cash_flow` دارند؛ manifest نرمال‌سازی با SHA-256 `422e485447213b46bb6aa31942f68c4eefc1eccd050b399598672451b30a8281` و JSONL با SHA-256 `69f2e5e97dbff69d257032a20528238dd0ea2a5badc5d4098bc89931f3895a1e` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery104-before-import.dump` با اندازهٔ ۱۵۳۵۰۸۰۷۴ بایت، SHA-256 `1c9dc2ad6dbcbc99634dd3b280fba4ddbd43817ede4d1c4bc7f6332ad3530d69` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=44`, `standard_facts=52`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot برای پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery104-refresh.json` با SHA-256 `2b42864281ed7e98f908bac9ee83bcc56959ce105d3e5d57dd2489344b5adf91` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery104.json` با SHA-256 `57fc5b71796241449e41bf6986fcbcaee16683805146913ec7f176b07a957a39` و CSV با SHA-256 `cf9e80c8d688978d5a70017f1208adc92bf10c20b20fc2e430497f16877b38e0` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۴۲ دوره، ۷۰۸۸۷ fact خام و ۳۶۹۸۳ fact معتبر. tierها `CORE_READY=721`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=384` و تصمیم‌ها `INSUFFICIENT_DATA=1383`, `SELL=124`, `HOLD=14`, `BUY=3` باقی ماندند. هر پنج نماد پوشش ۱۰۰٪ و ۱۰ fact معتبر گرفتند؛ ثرود همچنان به‌دلیل گیت اطمینان `INSUFFICIENT_DATA` است.
- registry عمومی exact-symbol با source SHA-256 `28a3c6d8759c9746eba279aa93148904be968c642b42108e798fd03190ce3d38`، JSON reconciled با SHA-256 `2d19e21fe2984a594fcdc62d017dc4a71ed13489d8dc3b0d2e96da69057fe69f` و CSV با SHA-256 `7efdb9328cfec58d7feeab0f8bd1c6ae3965e289a476d432bb7f14ad767b2614` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=263`, `ANALYTICAL_CONFIDENCE_GATE=339`, `RECOVERY_CLOSED=34` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T052106Z.tsv` با SHA-256 `bbc3e0013f5af69a763bd2231baeb5c6d70d5ea8d1654920bdd7370a180e1583` ثبت شد. دو backup فعلی recovery104 و recovery103 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery105، cash-flow رسمی برای پنج نماد

- پنج نماد `ولصنم، ولیز، فزرین، وساخت، وپایا` بر اساس کمبود واقعی `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery105-symbols.txt` با SHA-256 `48707589d993000ea8728f87d1d1990f5e5a4b447b28d78d2500e65b20265156` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` کامل شد؛ manifest با SHA-256 `862930284350e2e9e19ed13bf2cc5d02cd6abb054298814b4f5fd1ec5d7f375e` و checkpoint با SHA-256 `558de9ee3d3712f1afaae362816b68e831c25aca5d2725e952705dcbbba44e8f` و خطای browser صفر هستند.
- نرمال‌سازی ۱۳۵ fact از ۵۰ سند رسمی تولید کرد و ۵ مورد child-entity واقعی را خارج از import نگه داشت: یک مورد فزرین و چهار مورد وساخت. برای هر پنج نماد ۱۵ رکورد `operating_cash_flow` رسمی قابل‌قبول استخراج شد؛ manifest نرمال‌سازی با SHA-256 `208696d930b112676ee32fae44c9133fb21f9d465ef5cc7d0052124b5408499b` و JSONL با SHA-256 `ef2df75724ef7f0d0b628b383b928fd084b81f820af53ad951de2f444ea0c7aa` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery105-before-import.dump` با اندازهٔ ۱۵۳۵۳۵۰۱۹ بایت، SHA-256 `84cf75f8656778a7549cd577d19c490fa7d580ac911b8130af03d490bd373d76` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=47`, `standard_facts=50`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot برای پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery105-refresh.json` با SHA-256 `fbc63b4be0960cc3cda50fb7ca7c12c9885b5e6f8800a32f09c127c5aaf12f16` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery105.json` با SHA-256 `6abb1aa8525361792666f51023c063e1c110f2e4633e45b5018bbb4071da3401` و CSV با SHA-256 `019d3891e7c929860af64aa4512b106b05ae2ca8854acbf6ed0dbb21db60ee7b` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۴۸ دوره، ۷۰۹۳۴ fact خام و ۳۷۰۳۳ fact معتبر. tierها `CORE_READY=721`, `FUND_MODEL_REQUIRED=419`, `MISSING_COMPARABLE_PERIODS=384` و تصمیم‌ها `INSUFFICIENT_DATA=1383`, `SELL=124`, `HOLD=14`, `BUY=3` باقی ماندند. هر پنج نماد پوشش ۱۰۰٪ و ۱۰ fact معتبر گرفتند؛ فزرین و وساخت همچنان به‌دلیل `INSUFFICIENT_DATA` در گیت اطمینان هستند.
- registry عمومی exact-symbol با source SHA-256 `5eedc32b6636a3780dbf8a8a4a09f1380d20c6f12cd998bc4ca9136809286186`، JSON reconciled با SHA-256 `a3b85e5850cd34daf7434b8325cfd9d65b8b6fb51212da3a1f98e358c7a5397e` و CSV با SHA-256 `3c7b8fe761935a5be28a58e6750037b2e5d8692113a46080dac95fa3f3057c71` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=258`, `ANALYTICAL_CONFIDENCE_GATE=341`, `RECOVERY_CLOSED=37` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T052946Z.tsv` با SHA-256 `06fceaf575a345c2c33858116d4045acd031c15e58d0fa3b7922bb6bc647edb5` ثبت شد. دو backup فعلی recovery105 و recovery104 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery106، cash-flow رسمی برای پنج نماد

- پنج نماد `غمارگ، وکار، فرود، ولکار، غگرجی` با snapshot زنده و کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery106-symbols.txt` با SHA-256 `d5732bb44ebbc939ae5d6c7b8bf58d05199d92ff9a2f95cbd512b30d26cb8496` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` بدون خطای browser کامل شد؛ manifest با SHA-256 `3e38b511c7d72ad30ae734afe5b88789ffb45da1be59140ba7d6efee526061b9` و checkpoint با SHA-256 `06e51e7ab9e047a7b3449672f8f0e8ba15e843039f9bfa716925caa32b76e9f0` ثبت شدند.
- نرمال‌سازی ۷۲ fact از ۳۰ سند رسمی تولید کرد و دو گزارش child-entity واقعی وکار (`1589719` و `1586477`) را خارج از import نگه داشت. ۹ رکورد `operating_cash_flow` معتبر باقی ماند؛ manifest نرمال‌سازی با SHA-256 `a760a52227fc01be4caf09db016e743bb40ecd3522ce7b5cfc451b558892a457` و JSONL با SHA-256 `fee6cbf42f06ee1bd17ec6249642abe28c0f8b0d80f669bfed10b6bab097f17` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery106-before-import.dump` با اندازهٔ ۱۵۳۵۷۱۲۴۸ بایت، SHA-256 `2dfd522e1ae5bb2dd9761c18ef96e01c386da6a6c4e52f195e9bd37f5ccae4b0` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=22`, `standard_facts=26`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery106-refresh.json` با SHA-256 `1b35019e00901b0e5bf99eace5136b5c1df2f84ed71d02b4ffe80d0cb4fa402f` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery106.json` با SHA-256 `8e3cfbb0ddfecd7aa2da0e1470eda520e352296cc4889fa80af57fec6e4432b2` و CSV با SHA-256 `13a216fc5d1468fdecaf90dfdcfd860af2729f394769b33c378ae9abc6702b31` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۵۳ دوره، ۷۰۹۵۶ fact خام و ۳۷۰۵۹ fact معتبر. هر پنج نماد ۱۰ fact معتبر گرفتند؛ غمارگ، فرود، ولکار و غگرجی پوشش ۱۰۰٪ گرفتند اما به‌دلیل `INSUFFICIENT_DATA` در گیت اطمینان ماندند؛ وکار با پوشش ۸۵٫۷۱٪ و کمبود `operating_cash_flow` همچنان در گیت پوشش باقی ماند.
- registry عمومی exact-symbol با source SHA-256 `4e6618d8da0621ef15aeeffd7c0236d4bb3a3f956a8a0f6ac8f02dfa8d66196d`، JSON reconciled با SHA-256 `f8392564f5a2ff6e2c1b3df655e895b94f5bd8111fce831a7e4de45d5e0506ab` و CSV با SHA-256 `f431a76242f356a44da8c94049d248e3c4c0a0ad7a4028586421db87b21c8cf6` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=254`, `ANALYTICAL_CONFIDENCE_GATE=345`, `RECOVERY_CLOSED=37` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T053805Z.tsv` با SHA-256 `f6b2597b0ed1307db14ca97f5f90ad09a904517f57ed9aa8b512f7fef7cdba1b` ثبت شد. دو backup فعلی recovery106 و recovery105 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery107، cash-flow رسمی برای پنج نماد

- پنج نماد `کفرا، کخاک، حگردش، خاذین، کسرام` با snapshot زنده و کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery107-symbols.txt` با SHA-256 `62bc4ed38311f43c576d307df13b51294afa30448950c14fc1f8fb9f2657d5ab` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` و خطای browser صفر کامل شد؛ manifest با SHA-256 `a09d8e8ba9d9bf171dae4a84f7f483445a6c9a9c0ae8b0e988c200216590cc6d` و checkpoint با SHA-256 `900d6cb24d365dab558273f54bdf5d036b402adf87ecdb201fea61f5425a6621` ثبت شدند.
- نرمال‌سازی ۱۳۰ fact از ۳۴ سند رسمی تولید کرد و سه گزارش child-entity واقعی را خارج از import نگه داشت: دو مورد حگردش و یک مورد کسرام. برای هر پنج نماد ۱۳ رکورد `operating_cash_flow` معتبر باقی ماند؛ manifest نرمال‌سازی با SHA-256 `5f690ba0c69b691a966797113889ee584045eb9e3af08fd7714d7f4a5ae6f581` و JSONL با SHA-256 `b76736e4f6036e6ea1e97b328906f7113a06dbca4ded4b9e782ef77ce1fb35f4` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery107-before-import.dump` با اندازهٔ ۱۵۳۵۹۲۸۰۲ بایت، SHA-256 `92149cd50fefa964cb3477bd0c148e1a7af1d1bce7f971022387d078a37f747c` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=58`, `standard_facts=59`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery107-refresh.json` با SHA-256 `5dc7c211eb3846ce62ccbe020db12a80643a6a50bed97faf3fabd3d6638a027c` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery107.json` با SHA-256 `a5a9130e569a1f015a2afaa2119c690d6bf373dbd0f8c16fdf27c3f057b1f27e` و CSV با SHA-256 `e725f9c539bb45b403955406e7aa6f365767efa63273d9729ac8d8a8c332c525` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۶۲ دوره، ۷۱۰۰۷ fact خام و ۳۷۱۱۸ fact معتبر. هر پنج نماد پوشش ۱۰۰٪ و ۱۰ fact معتبر گرفتند؛ حگردش و کسرام با تصمیم SELL بسته شدند و کفرا، کخاک و خاذین به‌دلیل `INSUFFICIENT_DATA` در گیت اطمینان ماندند.
- registry عمومی exact-symbol با source SHA-256 `8edfb063cf3d2f58717a70413bd231ef407ecd0d22218aadad8e68eaa6ce4f16`، JSON reconciled با SHA-256 `39b29282ef35d0185b805cb0b6583c2f93f479d3b1189bf4f2f5caeddcae6ebe` و CSV با SHA-256 `1a4e5e09ab619efb9d7e9f03cd76b51581542a90bd314f6efb4aa11b1705aab2` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=249`, `ANALYTICAL_CONFIDENCE_GATE=348`, `RECOVERY_CLOSED=39` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T054725Z.tsv` با SHA-256 `7cc330e6968cb697ebd6c69d762d5200d594bb50257157ca35a73688ed0f9763` ثبت شد. دو backup فعلی recovery107 و recovery106 هستند. observer `PASS` با disk `65%` و `coverage_100=45`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery108، cash-flow رسمی برای پنج نماد

- پنج نماد `فمراد، ولنوین، نخریس، رانفور، خوساز` با snapshot زنده و کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery108-symbols.txt` با SHA-256 `1bf04a1fa8ed1715151965f55bc43bc7fe450aa49434bd3f92a56aa98539f9ff` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` و خطای browser صفر کامل شد؛ manifest با SHA-256 `94349fad8001c676c863d45e774ef2629c99acc06ab231bf03d8b5be0f6f0506` و checkpoint با SHA-256 `5a5591ad0c5dd7fed442921d52810d550fba7057ddb232b7a8ab4014918a593a` ثبت شدند.
- نرمال‌سازی ۹۰ fact از ۳۰ سند رسمی تولید کرد و دو گزارش child-entity واقعی رانفور (`1586697` و `1586480`) را خارج از import نگه داشت. برای هر پنج نماد ۹ رکورد `operating_cash_flow` معتبر باقی ماند؛ manifest نرمال‌سازی با SHA-256 `636e568b33532881717bcbacdd3a52728b5b44d88af19657345c4ff169739070` و JSONL با SHA-256 `f9cde0eafceb4971631965f55bc43bc7fe450aa49434bd3f92a56aa98539f9ff` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery108-before-import.dump` با اندازهٔ ۱۵۳۶۹۱۸۹۰ بایت، SHA-256 `38581f2859058e5f8387e784cca3dfe3416f7e029bf64bb28fbaa66e75475bcc` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=45`, `standard_facts=53`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery108-refresh.json` با SHA-256 `2e0f3fbd0593eff425c03104e25a2cb26ab13a479a7da4c104d7166d2f6d9e93` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery108.json` با SHA-256 `66a92ff82f0fc276c368ab4679da270dbeea1477760ece2bc394279a7f6180a7` و CSV با SHA-256 `116a10a0aef07d226b61e00424117020b1a2f58983a9186efe8751b661e22217` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۷۰ دوره، ۷۱۰۵۲ fact خام و ۳۷۱۷۱ fact معتبر. هر پنج نماد پوشش ۱۰۰٪ و ۱۰ fact معتبر گرفتند؛ خوساز با تصمیم SELL بسته شد و فمراد، ولنوین، نخریس و رانفور به‌دلیل `INSUFFICIENT_DATA` در گیت اطمینان ماندند.
- registry عمومی exact-symbol با source SHA-256 `07bb6a196d6ee9deae836821d67f6eddfd6322b66d8cdd04b68cae91825ce19a`، JSON reconciled با SHA-256 `84ef06eb908104428b37d135816713dbdc69b1bb6c0a894f2ee934a8d7b5146b` و CSV با SHA-256 `c0d24f390810c340e34c295b4051d6fa49011c1b9de96b9eb8f22f35a47adc83` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=244`, `ANALYTICAL_CONFIDENCE_GATE=352`, `RECOVERY_CLOSED=40` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T055454Z.tsv` با SHA-256 `b921e4e08fc88bd5dcced3122a69f1948ec3c0a1518259790c1d74495eb7a458` ثبت شد. دو backup فعلی recovery108 و recovery107 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery109، cash-flow رسمی برای پنج نماد

- پنج نماد `خفولا، وتوشه، غشوکو، ثعمرا، چفیبر` با snapshot زنده و کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery109-symbols.txt` با SHA-256 `638dcfa189f82adda0c5966d860e4a6bd6617095de393da22636e52207bb33e1` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` و خطای browser صفر کامل شد؛ manifest با SHA-256 `8d838dcdb3c62b3adcbf8a5dd5682b88f79ae090b44c0ef830b11055fd29c7b6` و checkpoint با SHA-256 `f6a252229c8e28682e48f606dc4a315eccaf22c1c05da6d684370b2f27ede376` ثبت شدند.
- نرمال‌سازی ۱۳۷ fact از ۳۱ سند رسمی تولید کرد و ۷ گزارش child-entity واقعی وتوشه را خارج از import نگه داشت. برای پنج نماد ۱۴ رکورد `operating_cash_flow` معتبر باقی ماند؛ manifest نرمال‌سازی با SHA-256 `ca7a0c1dfe2756f4f92d7d32b004a8e03c87fc39e8e367eb8b81834433a21ad9` و JSONL با SHA-256 `28d1b1aafbe4acdec56b315d8b45705fc89d1af8c61dd7ca7de6233885b3192f` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery109-before-import.dump` با اندازهٔ ۱۵۳۷۲۴۶۸۵ بایت، SHA-256 `aeb11b46bced2f9b6921ece31d28df664746c23ae26c7131a5122303a4049d35` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=15`, `standard_facts=15`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery109-refresh.json` با SHA-256 `4b0e750f56d0dc4a28a1672265502e892a5f8a76c4784052756932014a57769c` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery109.json` با SHA-256 `6f89917fa8f2b6ab8f1ccc9a25ba53a34aaafe070a284de6a441417e98a6521d` و CSV با SHA-256 `0aa96cd82537c95e1cef81d346e46d12ec24fbab0ddef05521cd57531c198fa9` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۷۰ دوره، ۷۱۰۶۷ fact خام و ۳۷۱۸۶ fact معتبر. هر پنج نماد پوشش ۱۰۰٪ و ۱۰ fact معتبر گرفتند؛ ثعمرا و توشه با تصمیم‌های SELL/HOLD بسته شدند و خفولا، غشوکو و چفیبر به‌دلیل `INSUFFICIENT_DATA` در گیت اطمینان ماندند.
- registry عمومی exact-symbol با source SHA-256 `15160a609e44c5d723984e82acb4670960101295151cb5feecdbcb5d9433ac6d`، JSON reconciled با SHA-256 `776ba4abce161ee26b79d7b54a1e53053d677d3c5a9bab9c7da7e65be0877b9d` و CSV با SHA-256 `39e47a17546665ee204d87ca551956b747ff91db0d03ad8a5c3b3e028788657a` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=239`, `ANALYTICAL_CONFIDENCE_GATE=355`, `RECOVERY_CLOSED=42` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T060248Z.tsv` با SHA-256 `ca3353abf9a9c3374f3d59668a8226d6489e6cac76ebf96359511d4003ac3ec0` ثبت شد. دو backup فعلی recovery109 و recovery108 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery110، cash-flow رسمی برای پنج نماد

- پنج نماد `کساپا، قشیر، قشرین، وثخوز، نیشکر` با snapshot زنده و کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery110-symbols.txt` با SHA-256 `bfde98ae6c5be107f990230a286b4371f2c8dde4c6df40f91e9bad4956266dea` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` و خطای browser صفر کامل شد؛ manifest با SHA-256 `3488b2ece87671f4188a0f6f294c3ca2789db8c3ab1d99696346821edaffc638` و checkpoint با SHA-256 `cfa0b3f269685fbc695081ee8e26f3765d9bc44f69fa839152dac07f33558abc` ثبت شدند.
- نرمال‌سازی ۹۶ fact از ۳۸ سند رسمی تولید کرد و ۴ گزارش child-entity واقعی و یک workbook وثخوز فاقد جدول معتبر را خارج از import نگه داشت. برای پنج نماد ۱۱ رکورد `operating_cash_flow` معتبر باقی ماند؛ manifest نرمال‌سازی با SHA-256 `46788fb336399bd23d052e7116f47a88951cb8cf30830aab24feb65cfad029a5` و JSONL با SHA-256 `78ad03fb36fbd4a8cc61ea419edf2b5de39dcd2815a752448906cc89187a9aa7` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery110-before-import.dump` با اندازهٔ ۱۵۳۷۶۵۱۷۰ بایت، SHA-256 `75435a61f8c5d18da3bda6a40daebc3ceb698fe159df81dc2ba3f88d3b8bd383` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=14`, `standard_facts=16`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery110-refresh.json` با SHA-256 `42e32c9e45c8fba110ad9b35a67ac1d7ee420b3d9f87d455065475411ffb8315` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery110.json` با SHA-256 `1c43400d548340bc533c6bfc4fdc99d901c8e4b4597cb4a00d65b291a107d87b` و CSV با SHA-256 `fb4b07daa5a28c2f63524bf0cf8e7ad7bd0804a6400587b5108acf7fc3cf27fc` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۷۰ دوره، ۷۱۰۸۱ fact خام و ۳۷۲۰۱ fact معتبر. کساپا، قشیر و قشرین با تصمیم SELL بسته شدند؛ وثخوز با `INSUFFICIENT_DATA` در گیت اطمینان ماند و نیشکر با پوشش ۸۵٫۷۱٪ همچنان در گیت پوشش باقی ماند.
- registry عمومی exact-symbol با source SHA-256 `f3e7f13b85098eac49f4d67223e59c100eac07366412d1400be582895d56dd69`، JSON reconciled با SHA-256 `a523c39c8fe1368765d0d4c625a461b5d2dd580540313adde6126e2684eb5129` و CSV با SHA-256 `34704ef2438307121113d763e303c5cb4be0f33caaa63cb495045cde8c89b0ca` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=235`, `ANALYTICAL_CONFIDENCE_GATE=356`, `RECOVERY_CLOSED=45` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T061010Z.tsv` با SHA-256 `a6c9b3da7b2f94071e5f6aaf8c930eeb908157862574cd54d6e6cb55d1dcf492` ثبت شد. دو backup فعلی recovery110 و recovery109 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery111، cash-flow رسمی برای پنج نماد

- پنج نماد `ثجوان، سیستم، ثقزوی، پلوله، خبنیان` با snapshot زنده و کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery111-symbols.txt` با SHA-256 `52632a1706988dd62c63e63810a511581d44394a549fac6e52dc01323729d8c3` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` و خطای browser صفر کامل شد؛ manifest با SHA-256 `691cd7dfc9fe34aaa589b2d76b358fe8e961a2f9c1bef5b3852e4e33f61046ef` و checkpoint با SHA-256 `625730b987a4703c47c4322a73699bbbb3974544f77596c85e22d26f0d8170b6` ثبت شدند.
- نرمال‌سازی ۱۱۰ fact از ۲۹ سند رسمی تولید کرد و سه گزارش child-entity واقعی خبنیان و دو workbook فاقد جدول معتبر را خارج از import نگه داشت. برای هر پنج نماد ۱۱ رکورد `operating_cash_flow` معتبر باقی ماند؛ manifest نرمال‌سازی با SHA-256 `5de3f541577c782684ec9a6ad66282b78deb4a8e44b05d82e0f978ec79c8d694` و JSONL با SHA-256 `5f903f7eea30ebfa1d84ffc7bf937a494844d1382cc9ba4e5c23764955245b98` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery111-before-import.dump` با اندازهٔ ۱۵۳۷۸۳۴۶۴ بایت، SHA-256 `1975926572ea72a07e98d728172ffddbea439398fdf01a00ae346a717e15d26f` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=11`, `standard_facts=11`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery111-refresh.json` با SHA-256 `135d07f8537bd8865fc39393490bd3aa2cf84fddefa363dbce2843ef9a409b5e` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery111.json` با SHA-256 `8dede149dfa1d7d590a5d84d4da3ee39da44437ce6423343d05f63778cbef2de` و CSV با SHA-256 `f35ca86c1f88c17acc34f7dcc643f3ace1dbd75400a7ebef75366812d66914a0` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۷۰ دوره، ۷۱۰۹۲ fact خام و ۳۷۲۱۲ fact معتبر. ثجوان، ثقزوی و خبنیان با تصمیم SELL بسته شدند؛ سیستم و پلوله با `INSUFFICIENT_DATA` در گیت اطمینان ماندند.
- registry عمومی exact-symbol با source SHA-256 `f89a7791bf2d7c117423c6d52fde49e6e33562dd2bfc54bc02b71bc94aad684d`، JSON reconciled با SHA-256 `fecbd160a505620b8e8924266a922e5243a5fd7d95f8db14532bddb62f44a2aa` و CSV با SHA-256 `a1702150363bf3fe6801a7c72b2ae80b7992114bc3efbd1941e6978c92540243` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=230`, `ANALYTICAL_CONFIDENCE_GATE=358`, `RECOVERY_CLOSED=48` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T061720Z.tsv` با SHA-256 `8c38f8ee77392e9e8be15dbdbcb8a394ec253f63bdaf916e45549ab5dac6b0de` ثبت شد. دو backup فعلی recovery111 و recovery110 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery112، cash-flow رسمی برای پنج نماد

- پنج نماد `ولبهمن، ولشرق، داوه، غپاک، شهر` با snapshot زنده و کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery112-symbols.txt` با SHA-256 `bf0863b3746fc387aceba1506cd69524da5a8cb9ce370ea1778c39c399bd09f5` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` و خطای browser صفر کامل شد؛ manifest با SHA-256 `de7c4b89fffdb80f6b8220f62172374e7faf947c58627e4257e8bc77c1fb5624` و checkpoint با SHA-256 `e916ca353977e1c19b68e3cf838628a836a69d654a3d158538716acee53bdf8d` ثبت شدند.
- نرمال‌سازی ۸۲ fact از ۲۹ سند رسمی تولید کرد و سه گزارش child-entity واقعی داوه، شهر و غپاک را خارج از import نگه داشت؛ غپاک fact والد قابل‌استخراج جدیدی نداشت. ۹ رکورد `operating_cash_flow` معتبر از چهار نماد باقی ماند؛ manifest نرمال‌سازی با SHA-256 `b42153939edce51b90ca356e24effc4c0582e749025f9530a2d413d99c6a8082` و JSONL با SHA-256 `bc785085420febc77c12a53bcb962495b9ef733d51842a3ca3f264317b71d763` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery112-before-import.dump` با اندازهٔ ۱۵۳۸۳۱۶۹۲ بایت، SHA-256 `f34770f4a25615330a8e50d6acab7c58e603cd6df5d99fcb75b9b8ca376dd2fe` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=10`, `standard_facts=14`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot هر پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery112-refresh.json` با SHA-256 `8b736558f92c899c4661f79e1731c8ea5faa97d5703d00bf1fe62e46304c112c` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery112.json` با SHA-256 `7bf95284d8f623299328148d12cb52cba076382446aff34e041e99129cf67ecc` و CSV با SHA-256 `182780de118ee7d08c5f658edfb0ab2ea01bb78b6e16c677d4cd99d1809726a5` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۷۰ دوره، ۷۱۱۰۲ fact خام و ۳۷۲۲۶ fact معتبر. ولبهمن، ولشرق و داوه با پوشش ۱۰۰٪ به گیت اطمینان رفتند؛ شهر با پوشش ۸۵٫۷۱٪ و غپاک با پوشش ۸۵٫۷۱٪ و ۹ fact معتبر همچنان در گیت پوشش باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `67bc8a297675253dfe18d0fdc91ecb9d0a1ef0bfea78d2cee5ee56e14990179a`، JSON reconciled با SHA-256 `ce805e1a5c9ca66578ff9741c3389ac0aa52b9c73285279c23ded003cd885c27` و CSV با SHA-256 `c808f94d4cacb6813a15f590f5c4c3c4f3007bcf1dc133748c49e9792e728d74` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=227`, `ANALYTICAL_CONFIDENCE_GATE=361`, `RECOVERY_CLOSED=48` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T062524Z.tsv` با SHA-256 `85797534d059630adfcadbda2c7a245f2c648def9b9239600314024db400381b` ثبت شد. دو backup فعلی recovery112 و recovery111 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery113، cash-flow رسمی برای پنج نماد

- پنج نماد `ساربیل، غدشت، ولپارس، تملت، مداران` با snapshot زنده و کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست در `artifacts/recovery113-symbols.txt` با SHA-256 `417c164bdac9a52851b550c29083f570b82c51c2c75c6a802d1ada3ad37519b2` ثبت است. capture محلی browser/Codal با منبع `browser/codal.ir` و خطای browser صفر کامل شد؛ manifest با SHA-256 `f32c20435bb3590d0c757ee95d49a04e1f6fa8ee98d09967a7296aadd7b8ad88` و checkpoint با SHA-256 `abede0d8cc53b038cab46f194f0b41acc58e169b8d4f487e7f93af9988fe7c4b` ثبت شدند.
- نرمال‌سازی ۹۰ fact از ۳۰ سند رسمی تولید کرد و چهار workbook تملت فاقد جدول معتبر و یک child-entity غدشت را خارج از import نگه داشت. برای هر پنج نماد ۹ رکورد `operating_cash_flow` معتبر باقی ماند؛ manifest نرمال‌سازی با SHA-256 `ce5139c1aa01b4234a755de015d61794c548d60c4f9bd9e0a76d98c462ccba3c` و JSONL با SHA-256 `d1a8d12a0aabb0338f316bfa9bfd8fff7460969b249ed5db0f259048a27f536a` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery113-before-import.dump` با اندازهٔ ۱۵۳۸۵۹۷۶۶ بایت، SHA-256 `28af2b370741c8803ed13343908f77a8d6d366b528858acfa9b01fb532925dbf` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=27`, `standard_facts=20`, validation error صفر؛ دو replay واقعی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery113-refresh.json` با SHA-256 `72b67c33417bd17eda1fffe4d0d54bdd9ad8a4b91706b11fdb977e9e38b69ee1` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery113.json` با SHA-256 `41aed1d046587bee2d643b354119e447c48e61ef2a14bc65969d62a53b0a539a` و CSV با SHA-256 `d6f4dac2290cdbb4bb1d5c6384d224cf692221434b291247aea1a1eea9243544` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۷۳ دوره، ۷۱۱۲۲ fact خام و ۳۷۲۴۶ fact معتبر. ساربیل، ولپارس و مداران با تصمیم‌های HOLD/SELL بسته شدند؛ تملت و غدشت با `INSUFFICIENT_DATA` در گیت اطمینان ماندند.
- registry عمومی exact-symbol با source SHA-256 `8236f7611df5c83234a9d6e4d36c8345f0cdb8b01e968f92872752847fd5c59b`، JSON reconciled با SHA-256 `06e189727ae08d812cb250dcf0a7c90cfdc946462a1f31fa440a52c1767bd8d3` و CSV با SHA-256 `a598c2f6ac254593011cec8927797fd7f741082cd95a9899c614bb98dc79e8ba` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=222`, `ANALYTICAL_CONFIDENCE_GATE=363`, `RECOVERY_CLOSED=51` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T063327Z.tsv` با SHA-256 `e9fa10583d3e12e5f77e5625506a0d606727ef4ac6e1e2d5deb1119adce8bfa9` ثبت شد. دو backup فعلی recovery113 و recovery112 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery114، cash-flow رسمی برای پنج نماد

- پنج نماد `کزغال، کتوسعه، تکنار، ثاصفا، ثتران` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ `سنوین` به‌دلیل کمبود متفاوت `eps_basic` وارد این چرخه نشد. فهرست‌های انتخاب و refresh در `artifacts/recovery114-symbols.txt` و `artifacts/recovery114-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد، ۵ فایل و بدون خطا کامل شد. checkpoint با SHA-256 `25e8378520e98d8744bed301a1ddcfdc23fdaa1884b35c1eb0e86390a8f971ad` و manifest خام با SHA-256 `3c047d0b25d5646cc3a4686c9b8d4ad7e4783b101364e7f83608a80ce34c9138` ثبت شدند.
- نرمال‌سازی ۱۵۰ رکورد از ۳۱ سند رسمی تولید کرد و خطای نرمال‌سازی صفر بود. manifest نرمال‌سازی با SHA-256 `2228e6925a892a8521410a6500e9cfa63d529ee1a2cd3c9c15a82409562430a7` و JSONL با SHA-256 `51ed7e3739c48e1103a1e4fe91463e7aecd4f215768ddd03f0ad3a706c90a0f1` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery114-before-import.dump` با اندازهٔ ۱۵۳۸۸۳۵۱۵ بایت، SHA-256 `f329b280bc279592bc96431892d54192a317eb16cde837e4aa34e320c5b9306f` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=24`, `standard_facts=17`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery114-refresh.json` با SHA-256 `226cbb671a9ea0a2b0d384c93edcc08dad8384b6ffc84bc06acb87072f783c90` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery114.json` با SHA-256 `c2036e911fb1a7992c2c38a191947b2c4ef9a8d4a9ec5c3d777d15a3f0ff2a8b` و CSV با SHA-256 `ce47ff53a6787725598bf1ebf5726eb0b7ff4c32257f30d33513b4c56dcb7ccf` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۷۴ دوره، ۷۱۱۳۹ fact خام و ۳۷۲۶۳ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ تصمیم‌های نهایی کزغال/کتوسعه `INSUFFICIENT_DATA` و تکنار/ثاصفا/ثتران `SELL` است.
- registry عمومی exact-symbol با source SHA-256 `f1d04ad931269a3cbe1c4060d5e14cd340d539a6ed0e7643139e434ff3006218`، JSON reconciled با SHA-256 `40b607021bed69c3d5fc8243008d8482b7c3a7c7430a00b2ee40b843dab4f556` و CSV با SHA-256 `29afff684508ae79d7dd6b80e7636239f7f9553276f7fd46e80cafa2b257f372` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=217`, `ANALYTICAL_CONFIDENCE_GATE=365`, `RECOVERY_CLOSED=54` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T064300Z.tsv` با SHA-256 `00f2c751db66f2c487b0ad211a87ef3013a04267ac7a4577f30ae10a67a5728b` ثبت شد. دو backup فعلی recovery114 و recovery113 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery115، cash-flow رسمی برای پنج نماد

- پنج نماد `کماسه، کبافق، کدما، کرومیت، کمنگنز` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery115-symbols.txt` و `artifacts/recovery115-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `806375ca0d632533a74ada8a50451a6a55606e3f5e0c6e6542b5355fc47dbf6b` و manifest خام با SHA-256 `75af2a726b70fede443a0232bb8a69d005bb1589476844006fbf7652808bb117` ثبت شدند.
- نرمال‌سازی ۱۱۰ رکورد از ۳۵ سند رسمی تولید کرد. ۴ سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ کرومیت و کماسه و کمنگنز رد و خارج از import نگه داشته شدند؛ خطای جعل یا حدس وجود نداشت. manifest نرمال‌سازی با SHA-256 `c7b67fb2bb97827c9cb70aea00d89c45278856a0b51c7121a3947d7c29a6ebf5` و JSONL با SHA-256 `6cf0651981e22478e7a29795ecf2a2c7a45d3dd20ffa0d75e438379bdaabff7a` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery115-before-import.dump` با اندازهٔ ۱۵۳۹۲۲۹۱۰ بایت، SHA-256 `8322ff6d4e8b68f93310406abe540a13c4e8a1475acd7d21853e0e37391899d1` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=65`, `standard_facts=65`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery115-refresh.json` با SHA-256 `00994a728ad39fe98a50299066673d7c8c6852d3fbdcc00afcb33ed4f154a97c` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery115.json` با SHA-256 `c525ad789e87404801079bcfd18219b3987e3492aec859a7ca35282eaaba3ecb` و CSV با SHA-256 `6592c7467c86570c3a541e3e470e361e3c9357980b532416fe582283cfb55c3e` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۸۶ دوره، ۷۱۲۰۴ fact خام و ۳۷۳۲۸ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ کماسه/کبافق/کدما/کمنگنز در `INSUFFICIENT_DATA` و کرومیت با `SELL` در `RECOVERY_CLOSED` قرار گرفت.
- registry عمومی exact-symbol با source SHA-256 `d8b1f809f2cc1935572c95d3dc362be749646472cb644aa08eb9af907b48f65e`، JSON reconciled با SHA-256 `7b869a42a48b1ade760aac45a97d99f0a28596f883f88c3c674407f903bd8a47` و CSV با SHA-256 `9a7f8cb7215c045303933055d18d27169af8bbeb6de3586967307a3ed29236f2` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=212`, `ANALYTICAL_CONFIDENCE_GATE=369`, `RECOVERY_CLOSED=55` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T065149Z.tsv` با SHA-256 `63ee2e669ad794020be49cfed35abe9472dc9861e5a1d48b667da60b2517e885` ثبت شد. دو backup فعلی recovery115 و recovery114 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery116، cash-flow رسمی برای پنج نماد

- پنج نماد `کنور، ثاخت، ثتوسا، ثجنوب، ثعتما` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery116-symbols.txt` و `artifacts/recovery116-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `ad27b0d05bda0e74de14b1e787dc26d2762e0d3d8c8760f8b2ff84b8ef34bb90` و manifest خام با SHA-256 `17e7d49875dd74a1d6229718d61bdb23664a4a10db2881f21b65fa9fdf20a799` ثبت شدند.
- نرمال‌سازی ۱۴۷ رکورد از ۳۷ سند رسمی تولید کرد. ۵ سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ ثاخت رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `1d1d32f77c9b5e3b5e91dcc2ab4c7eb4927eef2f2138f0390ce789ae5952322d` و JSONL با SHA-256 `d0558e0d276f92769a85d194eba500fb8e6116267cde82fc7d64dfac80f9858b` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery116-before-import.dump` با اندازهٔ ۱۵۳۹۵۳۴۳۵ بایت، SHA-256 `2bc663c92a793609b0cbedcccac1b9dab42586f83211e8e96c15bc364d3322db` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=16`, `standard_facts=16`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery116-refresh.json` با SHA-256 `4b62702d9c865eac7ae942f17ed34e9329b970b8f81071aa7647f44b9aff9044` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery116.json` با SHA-256 `6ea4d33a9709543abc4eb7971431d030af76e4ff93bbf0c667a696981183233a` و CSV با SHA-256 `12f35f70dbdb8dcf2b9de8386eb881d70ac48c7d34db655c614ee31c0b59725d` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۸۶ دوره، ۷۱۲۲۰ fact خام و ۳۷۳۴۴ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ کنور/ثاخت/ثجنوب در `INSUFFICIENT_DATA` و ثتوسا/ثعتما با `SELL` در `RECOVERY_CLOSED` قرار گرفتند.
- registry عمومی exact-symbol با source SHA-256 `5664fa3d884008e18699ed76d33f698af3b6f4f43aef7f839278df9720536338`، JSON reconciled با SHA-256 `e670d456304d01bff5e283d71904fe17aa790aa3802080e14bca5919cdcc5bc2` و CSV با SHA-256 `ff5859eaaf31825e61d351f9628b4db4cd6b2bb06318f70614e2e4aaf17f4543` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=207`, `ANALYTICAL_CONFIDENCE_GATE=372`, `RECOVERY_CLOSED=57` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T065924Z.tsv` با SHA-256 `21966c71bd020b6b544f531a3d7846fb1cea226a05f8719100fe2189a75098bc` ثبت شد. دو backup فعلی recovery116 و recovery115 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery117، cash-flow رسمی برای پنج نماد

- پنج نماد `ثغرب، ثنام، ثنوسا، ثپردیس، ثپهران` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery117-symbols.txt` و `artifacts/recovery117-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `a76fb86833a2d3393fa5a509ebfb750df1c65c55130be5572b505163eec0eb88` و manifest خام با SHA-256 `79cd3e36c93b50b34eed43645bc800b4d15116341bd44eaa3a129b7a8091ee7c` ثبت شدند.
- نرمال‌سازی ۱۸۰ رکورد از ۴۶ سند رسمی تولید کرد. یک فایل ثنوسا با خطای `parse:هیچ جدولی در فایل پیدا نشد: No tables found` رد و خارج از import نگه داشته شد؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `06cf10399eade9d6a0abf9b1eda01855d0a7b9111a81ac84ea85423830fc2896` و JSONL با SHA-256 `807349344ea81c7af63a81a95dfe8d48192c6b4eff38d35f22cad82e6b7ff976` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery117-before-import.dump` با اندازهٔ ۱۵۳۹۷۵۹۳۵ بایت، SHA-256 `e68286c9e1f36fdb78a02e9204fcc6f7fec11da2d34872f456cdd41cd720fac2` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=27`, `standard_facts=27`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery117-refresh.json` با SHA-256 `7c9cb6df8fc5ac8a5646666544d64b363941c27a86045f6b7dfe9971e08e1761` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery117.json` با SHA-256 `2757a4dd1d7a5d671c18c4a714b28f4b9223d07b452f1ea39c08f426e4200d5c` و CSV با SHA-256 `e497d1e64e567806f776e38b7831f728b413cb38104a0f70d71ae973d88c4c67` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۸۸ دوره، ۷۱۲۴۷ fact خام و ۳۷۳۷۱ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ ثغرب/ثپهران در `INSUFFICIENT_DATA` و ثنام/ثنوسا/ثپردیس با `SELL` در `RECOVERY_CLOSED` قرار گرفتند.
- registry عمومی exact-symbol با source SHA-256 `68ac6d463a18489ab4cffb2246a56809ef9020c5e56bf6d8f4c5f35b069fb19e`، JSON reconciled با SHA-256 `7b96cf469effcb4f3bfa8e6f8981dd571211decece5977f248a17085d69f0c09` و CSV با SHA-256 `08fadaaf6501eb90d31c7b1b70b5ca1b3f3d7b4e4ae609ca93af5cf44b377415` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=202`, `ANALYTICAL_CONFIDENCE_GATE=374`, `RECOVERY_CLOSED=60` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T070728Z.tsv` با SHA-256 `0ab6841418dfefcb122599728fa74a14201fbeeed1637c9a15a5aa0eacf288b8` ثبت شد. دو backup فعلی recovery117 و recovery116 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery118، cash-flow رسمی برای پنج نماد بانکی

- پنج نماد `وتجارت، وخاور، وپارس، وپست، ملت` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery118-symbols.txt` و `artifacts/recovery118-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `063d180d53902df5d45a0c2497cb2ca893edc464f8de0e807b369062ca8522bd` و manifest خام با SHA-256 `f213dd1b0ffa3feb89a92bc48f12fafa3036504232d8945ba36ad145800eee7a` ثبت شدند.
- نرمال‌سازی ۵۱ رکورد از ۲۰ سند رسمی تولید کرد. ۲۶ مورد رد شد: ۲۴ مورد با `child_entity_financial_statement` برای شرکت‌های زیرمجموعه و ۲ مورد با `parse:هیچ جدولی در فایل پیدا نشد: No tables found`. همهٔ این موارد خارج از import نگه داشته شدند و مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `d6edff7c8dddd57a7b321b26e43f77a0b728d8cdf01caec7c52dd80e9b2298b4` و JSONL با SHA-256 `aade13e2733efd978c484754bc3665958f23da171eeaff23ec2fb6cbf2665a5c` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery118-before-import.dump` با اندازهٔ ۱۵۳۹۹۸۸۶۹ بایت، SHA-256 `2c93cd4759a9dcd81d4c715bc49cb8bc023fdcf80609a3fe60e0188653c29a87` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=11`, `standard_facts=11`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery118-refresh.json` با SHA-256 `75e85c9747bef91e2a09a6b8e3fa32547b6af6a5981e13664322305cd5b9dd3c` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery118.json` با SHA-256 `9e74cdfcaa902eb932da9b5391ba96c010bc18d5160e3d3a276ce979143d2b0f` و CSV با SHA-256 `7c0ca44299754a1d084a1eca94f135342a3c24f7cb775d0d12bec277470e5f07` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۸۸ دوره، ۷۱۲۵۸ fact خام و ۳۷۳۸۲ fact معتبر. تجارت و ملت به پوشش `100.0%` رسیدند؛ خاور/وپارس/وپست در `85.71%` باقی ماندند و همهٔ پنج نماد همچنان `INSUFFICIENT_DATA` هستند.
- registry عمومی exact-symbol با source SHA-256 `ab1c73407fc7ded5fa1222dfb72290678264977754773b5442204f89df2a9e62`، JSON reconciled با SHA-256 `6ab665dae335f5067471a93e9ee45ac0b5e31947bfe75688df1e4771705660c7` و CSV با SHA-256 `e7c80d69b6d6189800207beb3fc16cfb564ca26cc802443cb1a873bcbcf905d4` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=200`, `ANALYTICAL_CONFIDENCE_GATE=376`, `RECOVERY_CLOSED=60` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T071529Z.tsv` با SHA-256 `c764fc016ec1fbb443332dde1db660dad0634efe67c42c6eb397d7efb6368868` ثبت شد. دو backup فعلی recovery118 و recovery117 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery119، cash-flow رسمی برای پنج نماد

- پنج نماد `حبندر، حتاید، حرهشا، حسینا، رتکو` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery119-symbols.txt` و `artifacts/recovery119-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `1c52d897a8b2c6030c63db9bfccd8574bf4ad419b1211c40ea4626ca511873ce` و manifest خام با SHA-256 `fb76e64cc54f2fdc17654f815ba2843b370d585b24ac3aeecd115b12ae7fd375` ثبت شدند.
- نرمال‌سازی ۱۸۰ رکورد از ۳۷ سند رسمی تولید کرد. دو سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ حتاید رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `045d4bfafe8c47c81dc73b37dd5d09f81d834406e30616b2333daec917ef1850` و JSONL با SHA-256 `59b1c3ecabab18e3e52e19a30dec33044bd76297f61ee6635f224298bbbd73d8` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery119-before-import.dump` با اندازهٔ ۱۵۴۰۱۵۸۶۰ بایت، SHA-256 `eece3337f6ce1c00b780c5df54b2aaf9208cca0125fbbd2748ea3a3c9f4a0d63` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=18`, `standard_facts=46`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery119-refresh.json` با SHA-256 `162f39831b2b5993b4e4c993ef008c0fa9d1fa38a30e2cb9973d51f32ae824fd` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery119.json` با SHA-256 `2b85bcc6ccc4478d0953f28872c80f73c79e696998ae25300be3217ffc7ae9eb` و CSV با SHA-256 `53d7c095146109b396675e8b80a71729a6278cb3c4d982347ab2b8a4c8da689b` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۸۸ دوره، ۷۱۲۷۶ fact خام و ۳۷۴۰۴ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ حتاید `HOLD`، حرهشا/حسینا/رتکو `SELL` و حبندر `INSUFFICIENT_DATA` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `8cae44a86e55d5a1a9f1c0b4c9b08c37c33604c15b6679398424229a4065f7f9`، JSON reconciled با SHA-256 `509269f75125367429ec2654228b625be092b3997c4e193595223b3186d58aa3` و CSV با SHA-256 `fa325643f7066f6a0bc8a0cb7ed107d80fa33e9459f11764c9e943f049bff4ab` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=195`, `ANALYTICAL_CONFIDENCE_GATE=377`, `RECOVERY_CLOSED=64` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T072356Z.tsv` با SHA-256 `2610611754267d70032dd833e14c61383469ccd6a235f02f1eaafdff3cd88b6a` ثبت شد. دو backup فعلی recovery119 و recovery118 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery120، cash-flow رسمی برای پنج نماد خودرویی

- پنج نماد `خبرنا، ختراک، ختور، ختوقا، خدیزل` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery120-symbols.txt` و `artifacts/recovery120-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `17141dbe39a5e6f788f6cb3fbb5a66f06a81a2a931ce5a1957f840045088ad9e` و manifest خام با SHA-256 `bc1c65a59fb16b562681db475f1aa91074fcf2d5cb0246bfe864212e70feeb55` ثبت شدند.
- نرمال‌سازی ۱۱۲ رکورد از ۲۹ سند رسمی تولید کرد. ۵ سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ خبرنا، ختوقا و خدیزل رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `8ed2871b5278a70255c1ee7b30c3f89130f308658640d0a532494a2da0cd9fa4` و JSONL با SHA-256 `fc253645d892407176c29eca7a9f1c296c5414569d00632c896024eebc2bc06b` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery120-before-import.dump` با اندازهٔ ۱۵۴۰۵۴۱۲۷ بایت، SHA-256 `00972b9db43453deb52e5e88c6821f51a2f520322a28fd1f06285facc83763e9` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=22`, `standard_facts=36`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery120-refresh.json` با SHA-256 `7d0f49655286ad3ee99d4aee3c3148d9a91fce324f0abf5a4d4ff9e7ad1f4771` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery120.json` با SHA-256 `3f241129b02398e3f41b1e9190b83f5813115dc51fd121d1d0995e051dd2bef9` و CSV با SHA-256 `91d73972ac425485c4d68b1c6b665d946195f67778e3e3597cd51ac46d437d4d` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۸۹ دوره، ۷۱۲۹۱ fact خام و ۳۷۴۳۱ fact معتبر. خبرنا/ختراک با `SELL` در `RECOVERY_CLOSED` قرار گرفتند؛ ختور/خدیزل در `INSUFFICIENT_DATA` و ختوقا در `SNAPSHOT_COVERAGE_GAP` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `d4697cbedd4d11f1cced057382bde9929801449b72f115d1d5d5a14ccb0206a3`، JSON reconciled با SHA-256 `c8918336312ff74eee863810dc6da8e1316e6c744306bf979073be104828cda6` و CSV با SHA-256 `0c3408d7581ed3a10829b3456816884c1be560dd4d0fa163d627b62d6e8a484f` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=191`, `ANALYTICAL_CONFIDENCE_GATE=379`, `RECOVERY_CLOSED=66` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T073137Z.tsv` با SHA-256 `65c70b3818f364d466288bbc55b66b9740a73eb7b03173581dbdfc8fb08a5fc3` ثبت شد. دو backup فعلی recovery120 و recovery119 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery121، cash-flow رسمی برای پنج نماد خودرویی

- پنج نماد `خمحرکه، خمهر، خنصیر، خکار، خکرمان` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery121-symbols.txt` و `artifacts/recovery121-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `f7f670c6ba687372f105af694f12e7e0c1285a813c69b3a642671364ed1a4840` و manifest خام با SHA-256 `85b60eb5d682f7b03cc974bef008b9470ef97b3400319fca621de93073189d77` ثبت شدند.
- نرمال‌سازی ۱۰۴ رکورد از ۳۰ سند رسمی تولید کرد. ۴ سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ خمحرکه، خکار و خکرمان رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `4f6b0f9444a4d85c82a4144139c527520020d2c32dcc4455a9283c0597790865` و JSONL با SHA-256 `b8fd363e650e4ca6bd97f6ff8868118f30db3d06febcdf7c2ed31fe55689c550` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery121-before-import.dump` با اندازهٔ ۱۵۴۰۹۶۰۳۵ بایت، SHA-256 `4c7855b33f100d8984afa3991cc28c60f51f9b427697dc2f66f603462ce9bfc8` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=11`, `standard_facts=27`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery121-refresh.json` با SHA-256 `a0d3fbf63042fedb124f8bb8722eacd269bd69e2c6b12a799d24adbb8d723597` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery121.json` با SHA-256 `30cb956be091658c149ac25550d43b6f90edfad2140d94644ceec5da50aff565` و CSV با SHA-256 `284e8db0a806a493a7c82c8ba775ec22f95cac5b10f557548718b73ff7a7b186` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۹۰ دوره، ۷۱۳۰۲ fact خام و ۳۷۴۵۸ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ خمحرکه/خمهر/خنصیر با `SELL` در `RECOVERY_CLOSED` و خکار/خکرمان در `INSUFFICIENT_DATA` قرار گرفتند.
- registry عمومی exact-symbol با source SHA-256 `91b3a2af7af6b6f571eb8378a52515417238159130f70ec07d35d436f7c6f631`، JSON reconciled با SHA-256 `c7952ec31dbc412f06c6140804cf87d7b18526f5981f994998430b9f5223b5f1` و CSV با SHA-256 `344a2c48f948c2bfe7a84cae1660d0439b70ec981b538eabf0888439cdece78f` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=186`, `ANALYTICAL_CONFIDENCE_GATE=381`, `RECOVERY_CLOSED=69` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T073914Z.tsv` با SHA-256 `29eb05a35e754119518c47f2094ab7d39b8dbd8d32007c8ad1eebd87e7423848` ثبت شد. دو backup فعلی recovery121 و recovery120 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery122، cash-flow رسمی برای پنج نماد

- پنج نماد `خگستر، فنر، ناما، رافزا، رپویا` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery122-symbols.txt` و `artifacts/recovery122-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `f3eed6cb4e992f1968db7ffc73fe7999d26e6e0dc117a0d1177d08ba53f44633` و manifest خام با SHA-256 `6b7a6c6c90bff0333157eda37fd3946e9301a46cc21c0911b6486ae6810184d7` ثبت شدند.
- نرمال‌سازی ۱۱۲ رکورد از ۳۰ سند رسمی تولید کرد. ۴ سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ خگستر و فنر رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `546a4cfe9efe74253d7a45571aab13f3df204950d5a8232fa62748af165907f6` و JSONL با SHA-256 `52853651eb4114aa8e0288e07dfcfaf78bdbfdc9311ebc0576011373d40c976b` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery122-before-import.dump` با اندازهٔ ۱۵۴۱۲۵۰۹۷ بایت، SHA-256 `940310ab425652de9c2ec96267669bbb27281a4680cd4c6e59ea3917a77e90a9` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=13`, `standard_facts=21`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery122-refresh.json` با SHA-256 `edfc90827a1dbeafed2c3bc9fc399fce5e08af4c3f28e0f71addd09e43b3a5c9` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery122.json` با SHA-256 `1142e6582e232d4b64f8444389ee1c6b5c07a2682cc8148491bf29a97d3d9118` و CSV با SHA-256 `66cdb3e66b5bcd40ae05fea795eab7454b941100061ff5190163a7c225c402aa` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۹۰ دوره، ۷۱۳۱۵ fact خام و ۳۷۴۷۹ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ خگستر/رپویا با `SELL` در `RECOVERY_CLOSED` و فنر/ناما/رافزا در `INSUFFICIENT_DATA` قرار گرفتند.
- registry عمومی exact-symbol با source SHA-256 `cf358af8066244a0e685b8d805d1bbe81d8f1e4465be7473c0866a626769da92`، JSON reconciled با SHA-256 `0104a087fbb0d4e118e6ec4c3813a9f3cf986158a5d8f2110089491b6b34e9f7` و CSV با SHA-256 `a17accba9716cd93388bcd7ce1dad0a2e1d6ad4a513cd4434c43751a40ae4015` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=181`, `ANALYTICAL_CONFIDENCE_GATE=384`, `RECOVERY_CLOSED=71` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T074640Z.tsv` با SHA-256 `9ed70b39993e530b5709d12c343b14ff4d37477de624e9c6b713c69f51d7b213` ثبت شد. دو backup فعلی recovery122 و recovery121 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery123، cash-flow رسمی برای پنج نماد

- پنج نماد `لکما، فجام، فکمند، هانیکو، کیا` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery123-symbols.txt` و `artifacts/recovery123-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `9fbafa89c5e15cf7f47e4eefdd1db6c93c17cbd8894aafa12d71412323351811` و manifest خام با SHA-256 `782ad49c889ebb3579c138e69d839c8d51ae78c073b616c05a655a28bd4a39a9` ثبت شدند.
- نرمال‌سازی ۱۴۰ رکورد از ۳۴ سند رسمی تولید کرد. ۳ سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ هانیکو رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `be55159282682dc919c0ca195926a47276ed0f69f279988610c1e5a323d0af31` و JSONL با SHA-256 `f854ff9b16f8962e976cb130e7b7c6f315ce8c0bfd1766c5850e9afa88cbc0a8` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery123-before-import.dump` با اندازهٔ ۱۵۴۱۴۷۲۱۴ بایت، SHA-256 `f350bcf378a7e7dd38c017fcba19d7e85df6637ae4d8d8e6b36d73b262fdeceb` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=14`, `standard_facts=24`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery123-refresh.json` با SHA-256 `5537ffc19a4a6d1bde7ed949e90dec2a3e413608619fb1e1b0754cb76e961031` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery123.json` با SHA-256 `6ce73029849b69eb0cef52a1f66b0680f8c8147615c541b49a42e986cab873a1` و CSV با SHA-256 `8b0c60d1f7871198bf749c5e1d6429d8f83a85b6896b3bcd60b8c809a2d9adf5` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۹۰ دوره، ۷۱۳۲۹ fact خام و ۳۷۵۰۲ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ لکما/فکمند/کیا با `SELL` در `RECOVERY_CLOSED` و فجام/هانیکو در `INSUFFICIENT_DATA` قرار گرفتند.
- registry عمومی exact-symbol با source SHA-256 `ccbb8acd53d36f762783ab39621773a7aff53eb46e486636a52b5bcc105edcdb`، JSON reconciled با SHA-256 `ac456f508f85013ef569ad9a1270fc75838a734775aa435dc6ec810798cdfe14` و CSV با SHA-256 `6c4054cdd73ef721ce4419a7c410d351c3386074399aadaf127bbf3c39ba77c5` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=176`, `ANALYTICAL_CONFIDENCE_GATE=386`, `RECOVERY_CLOSED=74` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T075406Z.tsv` با SHA-256 `f34d6f45d5e96124a9a3e6cb3404c26d8a20dc5093f06842d5230fc7827a1dd3` ثبت شد. دو backup فعلی recovery123 و recovery122 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery124، cash-flow رسمی برای پنج نماد

- پنج نماد `سفاسی، شلیا، کاذر، کایزد، کباده` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery124-symbols.txt` و `artifacts/recovery124-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `bd6cd6b4f79fc2c56bd5e8d9ca880b594868e2567888170a2051b7b8314f7eca` و manifest خام با SHA-256 `d99a95b7e4a884f4b53b93d9343ba7fa93e824b9a35eecefd73dfc55c2c072f3` ثبت شدند.
- نرمال‌سازی ۱۱۰ رکورد از ۳۱ سند رسمی تولید کرد. یک فایل سفاسی با خطای `parse:هیچ جدولی در فایل پیدا نشد: No tables found` و دو سند کباده با خطای `child_entity_financial_statement` رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `2a2ca9a37db0b82a4051e479fe393e6980dac42bac8db155f6b7de171c6d89bd` و JSONL با SHA-256 `33f370896e94541b47fe1be21efef71f160bd9fc7d809dc3fd89252c403ba416` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery124-before-import.dump` با اندازهٔ ۱۵۴۱۸۱۴۰۹ بایت، SHA-256 `4c3e8b474f3a788854c607f00cc1bea7aed4c855c0574d2b2ffc4e8db6996d1d` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=11`, `standard_facts=19`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery124-refresh.json` با SHA-256 `29431b0867770ae81bbc3f1d8934bdb207a12624f75e109024f5a329590f1a11` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery124.json` با SHA-256 `fe45f7465d18bb4716d6848a2a0435cc47be526230062449dc258c9e2d2fc933` و CSV با SHA-256 `abdbaab56652ca632acfeb34497cd79da8c2be7410e8c9a0b29db698d1ef6950` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۹۰ دوره، ۷۱۳۴۰ fact خام و ۳۷۵۲۱ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ سفاسی با `SELL` در `RECOVERY_CLOSED` و شلیا/کاذر/کایزد/کباده در `INSUFFICIENT_DATA` قرار گرفتند.
- registry عمومی exact-symbol با source SHA-256 `15b5a1d7fdedc3d4028ebdf5d80ef562da1baa803189aa6f4a8be2a62c827bb0`، JSON reconciled با SHA-256 `1f2e9755811f674738e06d2ece6edef426026ff51f2b7b12fe4a681c7eee5e59` و CSV با SHA-256 `958edc6a3590dce2a9525518b3c395d1055c73922fce68ce60f478066d723be7` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=171`, `ANALYTICAL_CONFIDENCE_GATE=390`, `RECOVERY_CLOSED=75` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T080122Z.tsv` با SHA-256 `50c23bc0a0df528cc946230f325ad01e4eabf9b58f826ab022501bb8a3e6b83b` ثبت شد. دو backup فعلی recovery124 و recovery123 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery125، cash-flow رسمی برای پنج نماد

- پنج نماد `کرازی، کقزوی، ولساپا، ولغدر، بهیر` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery125-symbols.txt` و `artifacts/recovery125-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `415213889525af87fe8c039b655ba0c60486466394c2cd05571ee63553f45212` و manifest خام با SHA-256 `8dcb1853c8d13ec4d0f02d902d157083b6cc6242b942009db24b2773b7e7e2c3` ثبت شدند.
- نرمال‌سازی ۱۰۴ رکورد از ۲۱ سند رسمی تولید کرد. دو سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ بهیر و کرازی رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `7df01ca613bd654602eed787dce4e8cce7b4fb28fc0c12b1493dc6369d9ba787` و JSONL با SHA-256 `1dfd84aaeddfe75476eeea8a24f54d7e2ebf4b55fad10cdf3668e9e3ae38ae51` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery125-before-import.dump` با اندازهٔ ۱۵۴۲۱۱۴۳۷ بایت، SHA-256 `2577452127042e46549c3286f65e5a61d35eee1a5f50d553ca1fa25db2e01aa8` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=27`, `standard_facts=28`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery125-refresh.json` با SHA-256 `6021a2ade0cc7e8d7a37a7d78292b60e594d3a747ba3301b31af5029d61c9a45` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery125.json` با SHA-256 `7a0ce9e39a600cb5ede30acc4fc585bca42151a6588e7c3b55cce8008cbf76a3` و CSV با SHA-256 `5c647da2ff37b32c2745f5c7792e717b3fc3623acf9fffa2a147b3f5dd10e2b6` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۹۴ دوره، ۷۱۳۶۷ fact خام و ۳۷۵۴۹ fact معتبر. کرازی/کقزوی/ولساپا/ولغدر به پوشش `100.0%` رسیدند؛ هر چهار مورد در `INSUFFICIENT_DATA` هستند. بهیر با پوشش `85.71%` و تصمیم `SELL` در `SNAPSHOT_COVERAGE_GAP` باقی ماند.
- registry عمومی exact-symbol با source SHA-256 `9863255fa2e62b8c2d4404e7fa3b390f9471363a163eaa453bc44849592bcd2b`، JSON reconciled با SHA-256 `4548b00299cd0b146ad1051a916d4d3974b25b96e2c8b75887c0b2c5bd6a260c` و CSV با SHA-256 `1e631ca36d38148ec44f2262fe14e311de362b1d2148c438715005df1fd933ac` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=167`, `ANALYTICAL_CONFIDENCE_GATE=394`, `RECOVERY_CLOSED=75` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T080911Z.tsv` با SHA-256 `720e523edb839f43aff5a770e7c3cb0fc295754db9b6ac6994a5673aa4023a37` ثبت شد. دو backup فعلی recovery125 و recovery124 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-01 - recovery126، cash-flow رسمی برای پنج نماد

- پنج نماد `داتام، سدبیر، فلات، وآرین، وآوا` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery126-symbols.txt` و `artifacts/recovery126-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `ec33f86f632df695499daf72370dbdecd86d041435bc54d9285aa843637e627c` و manifest خام با SHA-256 `f1411db850ab5dd7dfea088d2c68e1cca0745c028f7d85c8fc03a4e8c9a74d0f` ثبت شدند.
- نرمال‌سازی ۸۵ رکورد از ۲۶ سند رسمی تولید کرد. ۸ سند با خطای `child_entity_financial_statement` برای شرکت‌های زیرمجموعهٔ داتام، سدبیر، وآرین و وآوا رد و خارج از import نگه داشته شدند؛ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `8e5a9b4f1dc10f1e750990cf1e99139fc5bfa70df9fdfe61f214d9f1f383d756` و JSONL با SHA-256 `95811907f9148054f91ac2cfd10674692d43f69ed3c975c9bb57c7ad739bad15` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260901T-recovery126-before-import.dump` با اندازهٔ ۱۵۴۲۳۵۱۲۴ بایت، SHA-256 `188e045b0535112c400b22aa4d945e89c43afa12c9ad8f682a7188b0039a3572` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=15`, `standard_facts=15`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery126-refresh.json` با SHA-256 `31c67a0e93c65c29848541e4434f59e488ced1cee65083df79bc3fbbbfca6b4d` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260901-recovery126.json` با SHA-256 `2724694d06d9ac360693d1a2668ab2ac1d055674037a833fb9d3d2a0076e6758` و CSV با SHA-256 `a7f46fd8d0311609c20968549f555da1da86feb80846b0e3d9556e2f246fb5a4` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۰۹۴ دوره، ۷۱۳۸۲ fact خام و ۳۷۵۶۴ fact معتبر. سدبیر/فلات/وآرین/وآوا به پوشش `100.0%` رسیدند؛ فلات با `SELL` در `RECOVERY_CLOSED` و سدبیر/وآرین/وآوا در `INSUFFICIENT_DATA` قرار گرفتند. داتام با پوشش `85.71%` در `SNAPSHOT_COVERAGE_GAP` باقی ماند.
- registry عمومی exact-symbol با source SHA-256 `0ea5af48488ac7e65e9a338d72885b360f1adf9364f8b6395d165a5a3261c937`، JSON reconciled با SHA-256 `70f24a312b5303ca1eabcd6c0c58981d236e46dd3a4be29e56d69642d7d31014` و CSV با SHA-256 `ba6220194ec122380ee69a32bea816fc1246a457d10e092d0713c5f103130526` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=163`, `ANALYTICAL_CONFIDENCE_GATE=397`, `RECOVERY_CLOSED=76` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T081704Z.tsv` با SHA-256 `6132c3c7ee387adccbe4184b3882afbdc5a9cbdef2af819685d1f8c4961ff6a8` ثبت شد. دو backup فعلی recovery126 و recovery125 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery127، cash-flow رسمی برای پنج نماد سیمانی

- پنج نماد `سبهان، ستران، سخاش، سخزر، سخواف` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery127-symbols.txt` و `artifacts/recovery127-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `642a22f6244f724abdd04a54cc87e6189daa83a645efdc41af48f38518f2085f` و manifest خام با SHA-256 `66879416e1808beb2194ca4bf0a968be108cb04d1d4bca16bb58bb2a5037400e2` ثبت شدند.
- نرمال‌سازی ۸۰ رکورد از ۲۴ سند رسمی تولید کرد و خطای نرمال‌سازی صفر بود. manifest نرمال‌سازی با SHA-256 `8ad6ba1e1eef82b2cee0f92c3d6049280a9c374f013a7028a61177b72662cf90` و JSONL با SHA-256 `88c13914b807f6aa70bc4c21e87ff025a88ccd405796d6358f9ba8bb2472131d` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery127-before-import.dump` با اندازهٔ ۱۵۴۲۵۰۰۴۰ بایت، SHA-256 `d0985ffe525e667406c9e9396a74b7a7f3f974191877ff7094e79dcf3a206b29` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=80`, `standard_facts=66`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery127-refresh.json` با SHA-256 `a9657aa3f3a03825c597f5c34760850afacf830ffa4cdbd87b605d0bbff83a2d` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery127.json` با SHA-256 `41e2358f136b52725f09653a8be4140626fafdd6872fbd8802c44b72741994d8` و CSV با SHA-256 `dceac3373a1858fe9b8d5d56fe456a3d41adaa4fac0cd2ec4ad55f1b7a917253` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۰۸ دوره، ۷۱۴۴۸ fact خام و ۳۷۶۳۰ fact معتبر. ستران/سخزر/سخواف به پوشش `100.0%` رسیدند؛ سخزر `HOLD` و سخواف `SELL` در `RECOVERY_CLOSED` قرار گرفتند. سبهان و سخاش با پوشش `85.71%` در `SNAPSHOT_COVERAGE_GAP` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `732accefabcbf0d472f2b99b23ea73baf3c9345986dd5c38e653aacffd743aaf`، JSON reconciled با SHA-256 `f857aa659d87d9ab247b0e3d72629e57d6b5f5bbe35d4b6d1d4b09b15479e85c` و CSV با SHA-256 `86bdf0a554bbdd2accdee8021a0e512bf761943e19e474b4430302789ad5ddb9` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=160`, `ANALYTICAL_CONFIDENCE_GATE=398`, `RECOVERY_CLOSED=78` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T082533Z.tsv` با SHA-256 `215ec2e4f1f8aa43708f81be35059295f3a7acd198ae7bfb05d78e28804e2242` ثبت شد. دو backup فعلی recovery127 و recovery126 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery128، cash-flow رسمی برای پنج نماد سیمانی

- پنج نماد `سشمال، سغدیر، سغرب، سلار، سمتاز` پس از بررسی زنده و تأیید کمبود دقیق `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery128-symbols.txt` و `artifacts/recovery128-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `fdb0e0a3e222ba2f8366c30be46109507621f1ca77c1aa5d1c5c30abe86bcc6d` و manifest خام با SHA-256 `6380283311cfbb0dbedb8af9b17a6568b044e8bc066dccac7da229c1c4d873f7` ثبت شدند.
- نرمال‌سازی ۱۱۸ رکورد از ۳۸ سند رسمی تولید کرد. دو سند رد شدند: یک `child_entity_financial_statement` برای زیرمجموعهٔ سغدیر و یک خطای parse با پیام `No tables found` برای سمتاز؛ هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `908ce8074c77018d7fc7afab82010a54c86e96e2a89ccf24a71a84fc34ea894b` و JSONL با SHA-256 `6f5843b77d328b90076f045ff9a25b2a928c7a0dc7531f4276935d7c18b8ad19` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery128-before-import.dump` با اندازهٔ ۱۵۴۲۸۰۱۶۸ بایت، SHA-256 `7e0f90e95683d2d91bf267f3bb612e9eba0a9a3010744ac3b4d2f96d49e2dff6` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=118`, `standard_facts=111`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery128-refresh.json` با SHA-256 `1f2e37494881b935f28161e425338d88ebf8164dd2e7dc71dcb4d42822531108` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery128.json` با SHA-256 `e81111037cf1398f3d1e52a3abbe2eb33cf7aa5481a769a18aef3fb8a05b2318` و CSV با SHA-256 `1ec0927b1a1b937ee1a4e14d43a99980d59b421d7458906081ea3d4a182df69c` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۳۳ دوره، ۷۱۵۵۹ fact خام و ۳۷۷۴۱ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند؛ سغرب با `HOLD` در `RECOVERY_CLOSED` قرار گرفت و سشمال/سغدیر/سلار/سمتاز به‌دلیل گیت اعتماد تحلیلی در `INSUFFICIENT_DATA` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `1f7b3d139fe4e2537a16551edf0bbdc7f0ac09752bd808f9b6015e2b05196f8f`، JSON reconciled با SHA-256 `b5209100db256cb99d0acd9403a7cf04cc9802be8186f11bdbbab815d0260fd1` و CSV با SHA-256 `fcfd53aee6f16f476995caf27ebbf919ea32e0525287a2f512bcccbb8a40225e` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=155`, `ANALYTICAL_CONFIDENCE_GATE=402`, `RECOVERY_CLOSED=79` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T083514Z.tsv` با SHA-256 `084da92f9dfc7e404e5c018e4ee68ebfd7db2527d9dc5a9a0e0659a7f5109c26` ثبت شد. دو backup فعلی recovery128 و recovery127 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery129، cash-flow رسمی برای پنج نماد بانکی و کشاورزی

- پنج نماد `دی، سمایه، وسالت، جوین، زبینا` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery129-symbols.txt` و `artifacts/recovery129-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `6fc4c448d753d377ad6978eb0e7f9a1e97b79c3bc0e501cd19ae5accf1927651` و manifest خام با SHA-256 `70beba07c9213b44a65e28a6ac9cc837d633c589e6eeb2141d409aec20aba0fa` ثبت شدند.
- نرمال‌سازی ۳۶ رکورد از ۳۷ سند رسمی تولید کرد. ۱۲ سند رد شدند: ۷ سند `child_entity_financial_statement` برای زیرمجموعه‌های دی، سمایه و جوین و ۵ فایل زبینا با خطای `No tables found`؛ هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `51aca943a2e70495080bbcc79c43634894e37c7da27a63d4cccc1e7f292a2795` و JSONL با SHA-256 `1c820103820d31a53ca5d2caf75a7fbe8ebb4263543b999308dd2cb8f4ccdc10` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery129-before-import.dump` با اندازهٔ ۱۵۴۳۲۴۸۱۵ بایت، SHA-256 `000ce806ce1f160e0557aae17abe80cd9720567bd0afefad78a3ab368ca1e90e` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=4`, `standard_facts=4`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery129-refresh.json` با SHA-256 `251c67b4e30037510ea701412769833929c12563250905e98767fba9d02d4fc2` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery129.json` با SHA-256 `b1ec853c0be1f3870e8e81bdad29805334692562c8deff30052523e6388ff3d3` و CSV با SHA-256 `f1e0787f97be94e135ef6fed6783a716670d7c306e25f0179f55b76b8a48e9b1` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۳۳ دوره، ۷۱۵۶۳ fact خام و ۳۷۷۴۵ fact معتبر. جوین و زبینا به پوشش `100.0%` رسیدند اما در `ANALYTICAL_CONFIDENCE_GATE` ماندند؛ دی، سمایه و وسالت با پوشش `71.43%` در `SNAPSHOT_COVERAGE_GAP` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `1bad1982d2ed7607127930b38b1432ded8f3912df23751e44cf89ab4ffd20fff`، JSON reconciled با SHA-256 `5567f6c1033657383c387c0485c8d463bd22c68e75130657ec512302541b173f` و CSV با SHA-256 `250e43c18fcdab06ff30c96e9bfcbc15f0adbce83dd615a1fcf277c29f7cdfdc` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=153`, `ANALYTICAL_CONFIDENCE_GATE=404`, `RECOVERY_CLOSED=79` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T084438Z.tsv` با SHA-256 `88d5c7222f992f0834479e1a52ab8f5134f2025738aa401010201b42f4e80d3d` ثبت شد. دو backup فعلی recovery129 و recovery128 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery130، cash-flow رسمی برای پنج نماد فناوری و کشاورزی

- پنج نماد `رکیش، سپ، زشریف، زقیام، سپیدار` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery130-symbols.txt` و `artifacts/recovery130-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `013ada584ae4443e684cfee0f0c146870dc90e33ce173f784fb5f8532c177960` و manifest خام با SHA-256 `54e6547fb0cc6f7bdbe1713c73a8c9dde681b8b9ce0e40ada1730d994c02efe7` ثبت شدند.
- نرمال‌سازی ۹۰ رکورد از ۳۵ سند رسمی تولید کرد. ۱۴ سند رد شدند: ۵ سند `child_entity_financial_statement` برای زیرمجموعه‌های رکیش و سپ و ۹ فایل زشریف/زقیام با خطای `No tables found`؛ هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `3859d037c80ed1c4157ccf97f75f48e829a65268e2791b07a12a468c3e332138` و JSONL با SHA-256 `d461fe9850bff0900e48a97de270cf00715573984e4e77467de1dbfc7411fa25` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery130-before-import.dump` با اندازهٔ ۱۵۴۳۳۴۶۶۱ بایت، SHA-256 `e18887c3a99fa61e67adc1c58f54718538efa38363925a81e63215d78f20c698` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=10`, `standard_facts=33`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery130-refresh.json` با SHA-256 `cf4b17cdb3c69cc4daa50c507bfe5c9dc2bb439a11d241102bf19a9d7c1f6112` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery130.json` با SHA-256 `3dfab44fd6a009d6689d1b03030105fc43365802ccc7fd08c4b1b474d367f646` و CSV با SHA-256 `fea365a0a6c6a39ba688eb4bcd99cfc797a83db932ea9c3ce852130e461e567a` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۳۳ دوره، ۷۱۵۷۳ fact خام و ۳۷۷۵۸ fact معتبر. سپ و سپیدار با تصمیم `SELL` در `RECOVERY_CLOSED` قرار گرفتند؛ رکیش، زشریف و زقیام با پوشش `100.0%` در `ANALYTICAL_CONFIDENCE_GATE` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `2ef4f6819cc7c9b5e837452b49d206e91e10b1a491e338033c81c731de3461ff`، JSON reconciled با SHA-256 `34cda5d530bf5369914c18e32b12239147e979ddcb91d1680bce4d96f5660eb5` و CSV با SHA-256 `fb47b2496336d9c1df6028df523a29b755461237d70974c3ba2dfc8ca45a9515` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=148`, `ANALYTICAL_CONFIDENCE_GATE=407`, `RECOVERY_CLOSED=81` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T085254Z.tsv` با SHA-256 `9f5e7da2c65768f6dd6faa14d83fa5bb3f66911fec80b5d681a35d74256e7954` ثبت شد. دو backup فعلی recovery130 و recovery129 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery131، cash-flow رسمی برای پنج نماد کشاورزی و سرمایه‌گذاری

- پنج نماد `خاور، زماهان، زمگسا، زهلال، وارس` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery131-symbols.txt` و `artifacts/recovery131-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `9219e392d615d8b8a11a30d73efdad1f91af2e13274472a0cbcb608e0e17f692` و manifest خام با SHA-256 `e87d0807096116aeed1404f9caf900e02182574b6858cd52576554d4ec664c9f` ثبت شدند.
- نرمال‌سازی ۸۲ رکورد از ۳۰ سند رسمی تولید کرد. ۱۷ سند رد شدند: ۵ سند `child_entity_financial_statement` برای زیرمجموعه‌های خاور و وارس و ۱۲ فایل بدون جدول برای زماهان، زمگسا، زهلال و وارس؛ هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `bed3b72a61617ba5f12a802b716bde198a27fb32c031f539c66b05c929f9a9d9` و JSONL با SHA-256 `6558eacbd16463e2c255379e4b489a91890eff62cbf8105571f2705976e44bf5` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery131-before-import.dump` با اندازهٔ ۱۵۴۳۵۶۹۱۹ بایت، SHA-256 `dee230e7eaba9886b36433e6e8b1e914f544f01dad48f8e78d5800db8a5d4fbd` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=17`, `standard_facts=27`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery131-refresh.json` با SHA-256 `35c5e4f7428dd47210f4d5d3d5378967849c6a397292bd451015758d48106b92` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery131.json` با SHA-256 `fce02bf86422bb9dbc7345d4db778304f8befe653c66f03955249c28f5f8f213` و CSV با SHA-256 `dbab79c4bb8396fcc719aeb6b06fa16d653f717dd331fc036c636e485539a39a` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۳۵ دوره، ۷۱۵۹۰ fact خام و ۳۷۷۷۸ fact معتبر. خاور، زماهان، زمگسا و زهلال به پوشش `100.0%` رسیدند اما در `ANALYTICAL_CONFIDENCE_GATE` ماندند؛ وارس با پوشش `85.71%` در `SNAPSHOT_COVERAGE_GAP` باقی ماند.
- registry عمومی exact-symbol با source SHA-256 `9c716eeb5a306cd3710a7dc0d95240c64ec77094f24de775953d544b3fa026dd`، JSON reconciled با SHA-256 `941597c2e5984c8a0ce2c1efab026746f15106e8e96ced7b15c4837d2fc29d71` و CSV با SHA-256 `b3999c463c789aa0c7b866f762dcee4d137b751676bf4777f01ea727839e3ca1` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=144`, `ANALYTICAL_CONFIDENCE_GATE=411`, `RECOVERY_CLOSED=81` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T090026Z.tsv` با SHA-256 `46bf0636784274b12ae3aa0c5022e045e936ec2eba84a94c36b0df086e0bd41d` ثبت شد. دو backup فعلی recovery131 و recovery130 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery132، cash-flow رسمی برای پنج نماد سرمایه‌گذاری

- پنج نماد `واعتبار، والماس، وتوسم، وثنو، وجامی` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery132-symbols.txt` و `artifacts/recovery132-refresh-symbols.txt` ثبت شدند.
- دو تلاش اولیهٔ دریافت به‌دلیل خطای تایپی در نام نماد متوقف شدند؛ خروجی صفر‌فایلی حاصل از آن‌ها وارد pipeline نشد. دریافت معتبر با نام‌ها از فایل batch و در پوشهٔ `artifacts/recovery132-cashflow-browser-rerun` انجام شد: ۵ فایل و منبع `browser/codal.ir`. checkpoint با SHA-256 `cc5c98e3a3a1771b9628a0a6a82c25fd9027ceb7b120c1bb63975215929a5775` و manifest خام با SHA-256 `3f7a03778a21cb11a9ba820c360b11057013d894d90cde1f02ad2c10fbda8321` ثبت شدند.
- نرمال‌سازی معتبر ۹۱ رکورد از ۴۱ سند رسمی تولید کرد. سه فایل والماس، وتوسم و وجامی با خطای `No tables found` رد شدند؛ هیچ مقدار یا هویت حدسی وارد نشد. خروجی معتبر در `artifacts/recovery132-cashflow-normalized-rerun`، manifest با SHA-256 `ed9265664c32e01c9d0a86f4aa286368f832166f34ef6c8adc3b929e752cb6a8` و JSONL با SHA-256 `656567343f213d230212b44f10022c4c4232c04757a6c38aa3568b1a03082db4` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery132-before-import.dump` با اندازهٔ ۱۵۴۳۷۶۱۸۵ بایت، SHA-256 `8dd67f6ad30b22aaf042a56ccf2f0889776965871ca27a7def051b8c80592fa9` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=7`, `standard_facts=10`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery132-refresh.json` با SHA-256 `a3bdd0d0b85e4a4beaa4844a8d3c0d14f08401fd7c3eadff14f1ef2a0d93fc0c` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery132.json` با SHA-256 `e615bd3dd7726a92ef93ccd3cea8b1f39891caef5384ab6a62f66f67f062d49a` و CSV با SHA-256 `a86c151fb82ea224d111ba8b7d36226bc17c4cfd33f02f4e78a4140ad9d09c73` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۳۶ دوره، ۷۱۵۹۳ fact خام و ۳۷۷۸۱ fact معتبر. هر پنج نماد با پوشش `85.71%` در `SNAPSHOT_COVERAGE_GAP` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `e1d60c08a0c66fde3d49ec71549451dc041f3808b75c23bcc81dd546f8930f6d`، JSON reconciled با SHA-256 `d56cf4229d746fef9a17f8c0fe645b22a1b98a22e5dab0281f320d263ef631f5` و CSV با SHA-256 `3ede0803da89bc4bc7de37cbf32d67ed92d64cf70c1572501acc6681ebc5c81a` ثبت شدند. gateهای عمومی بدون تغییر در `SNAPSHOT_COVERAGE_GAP=144`, `ANALYTICAL_CONFIDENCE_GATE=411`, `RECOVERY_CLOSED=81` و `NO_KNOWN_DATA_GATE=9` باقی ماندند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T090942Z.tsv` با SHA-256 `b27f40c1f60d4f4cabc0d11ca2b5138bc136e1e91a96457983e4addc4319aa28` ثبت شد. دو backup فعلی recovery132 و recovery131 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery133، cash-flow رسمی برای پنج نماد مالی و فلزی

- پنج نماد `وایرا، وبرق، زنگان، فتوسا، فجر` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery133-symbols.txt` و `artifacts/recovery133-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `e0367441dedbc3f52a144c3517879e4f17698600a68511139dd0c99f80284800` و manifest خام با SHA-256 `06ccbe357b9902553d73ae504d46907983db333b24717adca302c3fa43e63d53` ثبت شدند.
- نرمال‌سازی ۱۳۷ رکورد از ۳۸ سند رسمی تولید کرد. ۴ سند `child_entity_financial_statement` برای زیرمجموعه‌های وایرا و وبرق رد شدند؛ هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `b40ef381db7a6c5a637fc52b1a81bc421290a904bd7b369b7c19e4d43c594585` و JSONL با SHA-256 `980dc512a7215cff456768761bd487f62f3cf81b1950083421359e9c44ab594c` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery133-before-import.dump` با اندازهٔ ۱۵۴۳۹۳۶۳۰ بایت، SHA-256 `2e97638c020132e1bca18e0feffdadcdc2f3c7d2ced66aad313f474add17631b` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=105`, `standard_facts=109`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery133-refresh.json` با SHA-256 `05a73fdfad2c38b75594c00ab39c889042478be374565c1ea1bcf9f4104f8b85` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery133.json` با SHA-256 `d276f0650e710dc1053a7ed380df377aa0449bd74226920d3b15d3a8f821aff6` و CSV با SHA-256 `d3a5e453f0a0c939bf117d1de5f3c134d9e5d46edf42c7e17cbd65afd111bbf6` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۵۵ دوره، ۷۱۶۹۱ fact خام و ۳۷۸۸۲ fact معتبر. وبرق و زنگان با تصمیم `SELL` در `RECOVERY_CLOSED` قرار گرفتند؛ وایرا، فتوسا و فجر با پوشش `100.0%` در `ANALYTICAL_CONFIDENCE_GATE` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `1793f963d09bb65afc5c30af259a132c890f5761e46bf5fcb6c8ebda6d301ed7`، JSON reconciled با SHA-256 `1a1807d51d5baf4025f6acafc324bfd20d0109a54cafab4fa59f6968cf0a9666` و CSV با SHA-256 `c3735021b02dbbe51296116398d4e81179e6011fc1b93455cf71b150a0d865a3` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=139`, `ANALYTICAL_CONFIDENCE_GATE=414`, `RECOVERY_CLOSED=83` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T091924Z.tsv` با SHA-256 `0117e3ca53072f408f90a58856b3e591ab5a5fd443cc32a3fc2cfba523fc6b58` ثبت شد. دو backup فعلی recovery133 و recovery132 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery134، cash-flow رسمی برای پنج نماد فلزی

- پنج نماد `فروس، فروسیل، فروژ، فروی، فسدید` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery134-symbols.txt` و `artifacts/recovery134-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `d8822aa3ad72920d0a26de15569cadca26877c773249056f472645ea5978f6f2` و manifest خام با SHA-256 `d6f135fa84be2b2585e11253355f2f5c82786af474dc8f2012d1a0e6d44816d8` ثبت شدند.
- نرمال‌سازی ۹۱ رکورد از ۲۶ سند رسمی تولید کرد و خطای نرمال‌سازی صفر بود. manifest نرمال‌سازی با SHA-256 `4165cda0aa22c610f82f107804c99e9f78c4540ff6289fb862de8160fd722945` و JSONL با SHA-256 `dc1f88277d77f3babc538c6144f79dee29773f0c28091e11794d0ab534cb5316` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery134-before-import.dump` با اندازهٔ ۱۵۴۴۵۰۰۵۶ بایت، SHA-256 `ccbc91db707ebe6bc280b30e79f7f7dfcf5bbbc7b6a54aee63df83e9dcba4a7d` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=91`, `standard_facts=91`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery134-refresh.json` با SHA-256 `dece394486e99dfa5d3d9dbe2b4a98d9771f0a35355f8e28f0750afbc83bec0b` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery134.json` با SHA-256 `ddd8657437d58a0dc1c85a56f29e28b64de944eb4a0ba60e86a8f9d9c27e1b1d` و CSV با SHA-256 `d0d13ee6416465f93c6ec6b1ca3435f2d8420f04c75ca0486851d1c36904424d` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۷۴ دوره، ۷۱۷۸۲ fact خام و ۳۷۹۷۳ fact معتبر. فسدید با تصمیم `SELL` در `RECOVERY_CLOSED` قرار گرفت؛ فروسیل، فروژ و فروی در `ANALYTICAL_CONFIDENCE_GATE` و فروس با پوشش `85.71%` در `SNAPSHOT_COVERAGE_GAP` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `3ee29c8d0122bcf0e2260e9a6cc4e9d77022b929553e7b1107652616818e6b85`، JSON reconciled با SHA-256 `cc89e5b2db67bbec467a26bb1aec8fda4e0e04222f2e3ac9fd3e5347ba4bce64` و CSV با SHA-256 `9d16ec35c89cb4e445ac0bc98d35416d9eed539d58d05b902667d9775f8094fb` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=135`, `ANALYTICAL_CONFIDENCE_GATE=417`, `RECOVERY_CLOSED=84` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T092710Z.tsv` با SHA-256 `c1981b3c8b9dbb53d624a7130ecda8895ed8ac0e6e46e58b0876ab683678deba` ثبت شد. دو backup فعلی recovery134 و recovery133 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery135، cash-flow رسمی برای پنج نماد قندی

- پنج نماد `قثابت، قجام، قشکر، قصفها، قمرو` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery135-symbols.txt` و `artifacts/recovery135-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `4ea43fd7e17fa1f77a7b683499dac1a1f57d67fc930e32f6f89eb3033ba4c8cf` و manifest خام با SHA-256 `c3c71807d6b1781ea6744e6299b29e65b052fcd947f59e62484853540f118933` ثبت شدند.
- نرمال‌سازی ۱۱۰ رکورد از ۳۸ سند رسمی تولید کرد و خطای نرمال‌سازی صفر بود. manifest نرمال‌سازی با SHA-256 `1ea70049ebe32b5deb4ef16e226536c898cce553c8fe6aa4f1d4959f6530501c` و JSONL با SHA-256 `7e61cabe6f79cb9dc389ae6a1613cbdd806bbe0ce37f2ca911f798e4cd661895` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery135-before-import.dump` با اندازهٔ ۱۵۴۴۷۷۰۶۹ بایت، SHA-256 `641728c480231d96a9bb1680d228c1fd46bac2a7e2978e98803d337e2044fb3d` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=20`, `standard_facts=15`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery135-refresh.json` با SHA-256 `cb66d4e7eff02ba1ca17b2accd2f3cf29df7230f1fe6e0a0418584ec89aa1c35` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery135.json` با SHA-256 `10a88927cbe775a409c5f828b2c6b2112058240ddac71b31ecfa2f7da8bd21bd` و CSV با SHA-256 `4369b3e7a9e1e64fbb49af838c3b897ea14aae277ae5e2fcce80e1cb95751ce1` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۷۵ دوره، ۷۱۷۹۵ fact خام و ۳۷۹۸۸ fact معتبر. قشکر با تصمیم `SELL` در `RECOVERY_CLOSED` قرار گرفت؛ قجام، قصفها و قمرو در `ANALYTICAL_CONFIDENCE_GATE` و قثابت با پوشش `85.71%` در `SNAPSHOT_COVERAGE_GAP` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `2e0b844c5d57844e66fe3d5830b5158a17f78e85429a62c6aa94a78649383f61`، JSON reconciled با SHA-256 `a73b10ab009949995670eb7301e7a24d6ea6ac2afd938de37a13085f71d90b24` و CSV با SHA-256 `f5a2a4e7b5819bfc0a5c76a534685692f7344ae298c14219e68d71aa41ef9aa6` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=131`, `ANALYTICAL_CONFIDENCE_GATE=420`, `RECOVERY_CLOSED=85` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T093446Z.tsv` با SHA-256 `de9b7e6cad20aabf779c00a2ae1f111f85d6839fdb7fca235a51dbd1638b683c` ثبت شد. دو backup فعلی recovery135 و recovery134 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery136، cash-flow رسمی برای پنج نماد فلزی

- پنج نماد `فسرب، فصبا، فطلوع، فلوله، فماک` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ فهرست‌های انتخاب و refresh در `artifacts/recovery136-symbols.txt` و `artifacts/recovery136-refresh-symbols.txt` ثبت شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `ce63fed11af9802163c09a68e4bb0a27b3d77a54e33d1e7f4b8f9775bcb60399` و manifest خام با SHA-256 `242f4e53a1c4db75f8cb8cefcc89ddbc6f067135d2f0c9aeb01bce7861f57253` ثبت شدند.
- نرمال‌سازی ۱۱۰ رکورد از ۳۳ سند رسمی تولید کرد. دو فایل فسرب و فطلوع با خطای `No tables found` رد شدند؛ هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `2bb939ec4cd1c51ea1bb5abce986a0e43fc63171a39ac2f8ff96ed495e09662e` و JSONL با SHA-256 `b0444f6a523b70ca0605b37109a91ef8c2e0374f932bb808290806591ea2dffd` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery136-before-import.dump` با اندازهٔ ۱۵۴۵۰۴۳۲۴ بایت، SHA-256 `40b1955be82e3c7a1d9973c393d196616e1de4344ab49f4b90d244610ff69890` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=65`, `standard_facts=65`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery136-refresh.json` با SHA-256 `81ddb8271d6f7043d6b27d703be2df59dae8d6a41bdf3416cd2f755e31c7edd8` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery136.json` با SHA-256 `0adefb704ec166ceee0c28335921fb4a7e1b249f46cd6d5ec5f9f6a29653422a` و CSV با SHA-256 `00be8a5352d5dc7952a5ea370af1e2e109acf8e1c25fadb4aec14b0d1a72e9e1` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۸۷ دوره، ۷۱۸۶۰ fact خام و ۳۸۰۵۳ fact معتبر. فصبا، فطلوع و فلوله با تصمیم `SELL` در `RECOVERY_CLOSED` قرار گرفتند؛ فسرب و فماک در `ANALYTICAL_CONFIDENCE_GATE` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `5e180035a49a449fac42b3f51ac76b8ba1b514d580f9895d88a68d9c130f5fdd`، JSON reconciled با SHA-256 `bdd2761c8a54d4287a40dd84291eed4cf92e4015e7f2a331fee585ab5b9abc8c` و CSV با SHA-256 `4dc2fea2989a1f1339b3e6bde3139d680d299dc487d834f9036a7699e6dc0d10` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=126`, `ANALYTICAL_CONFIDENCE_GATE=422`, `RECOVERY_CLOSED=88` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T094208Z.tsv` با SHA-256 `dd36694ed6757c7600a19553726a68c4b118e07682eb27528fe37d942d5ced9f` ثبت شد. دو backup فعلی recovery136 و recovery135 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery137، cash-flow رسمی برای پنج نماد فلزی و قندی

- پنج نماد `فنوال، فهامون، فوکا، فگستر، قثابت` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شدند؛ قثابت برای تلاش تکمیلی پس از باقی‌ماندن در گیت پوشش دوباره بررسی شد.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۵ نماد و بدون خطای دریافت کامل شد. checkpoint با SHA-256 `d105b5f94d834f08511e433b99122568b1dcb1287e6aa0b094044f78489268bc` و manifest خام با SHA-256 `51cd83042d381f63083b8256d3f5ab8c50a4d1f9bd7d49318b0700d2f0d7351f` ثبت شدند.
- نرمال‌سازی ۷۰ رکورد از ۲۵ سند رسمی تولید کرد. یک فایل فنوال با خطای `No tables found` و یک سند زیرمجموعهٔ فهامون رد شدند؛ هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `7b8c886e90bcc47bb0e7684aae3d92ef8e1598d9f4aa264836940daca6343a2d` و JSONL با SHA-256 `2459afa3bb7f0f77ce321e605ee06c9d5182edaf9d4e46786ee5def6b5161b5d` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery137-before-import.dump` با اندازهٔ ۱۵۴۵۳۸۷۳۹ بایت، SHA-256 `6289c65dd17cf78ca49fb4b71a4c17f1fc266d5ca45f61ce161e418ec7f2f7ed` و `pg_restore -l` موفق ثبت شد. import artifact-only با checksum/advisory lock موفق بود: `inserted=7`, `standard_facts=24`, validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh داخلی snapshot پنج نماد با `ok=5`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery137-refresh.json` با SHA-256 `26bb3b653b2af0085f74e7748d596e5015f5fee496f6c1c9bc1d25939683f279` ثبت است. audit all-active در `artifacts/audits/coverage-all-active-20260902-recovery137.json` با SHA-256 `b1fe85eb778135a3041e28053b096767b6bd89693f4bedd15687995c2d1e8854` و CSV با SHA-256 `e75ad051df54537127398a9630fd91e97c2b58827b3d002c1b7419476f225e6a` ثبت شد: ۱۵۲۴ ابزار فعال، ۱۸۱۸۷ دوره، ۷۱۸۶۷ fact خام و ۳۸۰۶۸ fact معتبر. هر پنج نماد به پوشش `100.0%` رسیدند اما در `ANALYTICAL_CONFIDENCE_GATE` باقی ماندند.
- registry عمومی exact-symbol با source SHA-256 `bd7f776de1e88c1c477464a95b668918b0f9bf777e9cb67930c139a643b7245a`، JSON reconciled با SHA-256 `e96cda7c5247134202ed69ec89691154b95d5eab44eec0ed76d060c48887b687` و CSV با SHA-256 `5d5a9ae337c90c3e705a4db1dffa527e5faeae6e96d074bf0ee21ad4238184c6` ثبت شدند. gateهای عمومی اکنون `SNAPSHOT_COVERAGE_GAP=121`, `ANALYTICAL_CONFIDENCE_GATE=427`, `RECOVERY_CLOSED=88` و `NO_KNOWN_DATA_GATE=9` هستند؛ source gateهای قبلی جداگانه حفظ شده‌اند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T094956Z.tsv` با SHA-256 `8cc902f9a0c5c60b2bffd629cab9a09d63b677f03d7a272be4e3ceab8644789a` ثبت شد. دو backup فعلی recovery137 و recovery136 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery138، cash-flow رسمی برای موج ۹ نمادی

- موج بزرگ‌تر و هدفمند شامل `فن آوا، معیار، وآفر، وبیمه، وتوسکا، وتوصا، ودانا، وسکاب، پرداخت` پس از بررسی زندهٔ Production و تأیید کمبود `operating_cash_flow` انتخاب شد؛ نمادهایی که OCF معتبر داشتند عمداً وارد موج نشدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برای هر ۹ نماد با ۹ فایل موفق شد؛ checkpoint و manifest خام در `artifacts/recovery138-cashflow-browser` ثبت شدند.
- نرمال‌سازی `206` رکورد از `57` سند رسمی انجام شد. ۹ سند `child_entity_financial_statement` رد شدند؛ هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `f64984b2e341bc678a23d4f22e6714a1a521493d8e9abc7e8ce6bbb77f0af85` و JSONL با SHA-256 `3be73b3fa16377effd98accbdaaac3f81677b9aad3180fb1db03fbccd105169a` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery138-before-import.dump` با اندازهٔ `154550971` بایت، SHA-256 `f93c6cf3bad3fe4536e7f840d46e659595136639ddee2b87daf2d4e1b271f740` و `pg_restore -l` موفق ثبت شد. import artifact-only با `inserted=45`, `standard_facts=43` و validation error صفر؛ دو replay بعدی هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh Production برای هر ۹ نماد با `ok=9`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery138-refresh.json` با SHA-256 `8f85ab5b3bd67f460f6cacf8017f4993857956cbf05e2e852ba024e88987db7c` ثبت است. audit نهایی با SHA-256 JSON `c59b4e5fb37e97b1c1359153981d1b66095aea3804c0624282a8493dbad6960f` و CSV `331fa3d892fc4e441e41d9e729ca36b86cd57e55b9d791936bccbb0944ccbd6e` ثبت شد: `1524` ابزار فعال، `18189` دوره، `71901` fact خام و `38106` fact معتبر. فن آوا، معیار، وآفر، وبیمه، وتوسکا، وتوصا و ودانا و پرداخت به پوشش `100.0%` رسیدند؛ وسکاب با پوشش `85.71%` در `SNAPSHOT_COVERAGE_GAP` باقی ماند و نمادهای دارای تصمیم `INSUFFICIENT_DATA` همچنان گیت اعتماد تحلیلی دارند.
- registry عمومی recovery138 با source در `artifacts/audits/public-645-gate-registry-20260902-recovery138-source.json`، reconciled JSON با SHA-256 `e6db450e87a4bd8959e6e19b145caf0694cf40f93bc018b37631bad85e8bd3eb` و CSV با SHA-256 `cf1d33f0cc227e6e4ee11b07917efedb88421af81708ad76345ba51b1c5a8889` ثبت شد؛ gateها `SNAPSHOT_COVERAGE_GAP=121`, `ANALYTICAL_CONFIDENCE_GATE=427`, `RECOVERY_CLOSED=88` و `NO_KNOWN_DATA_GATE=9` هستند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T100343Z.tsv` با SHA-256 `0dcbac0c6f43d3fede9a71f0f064688a058620e381339d1325dc03c714143b62` ثبت شد. دو backup فعلی recovery138 و recovery137 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery139، cash-flow رسمی برای موج ۱۹ نمادی

- موج شتاب‌یافته شامل `ارفع، اپرداز3، بتک، تاصیکو، تفارس، خریخت، خرینگ، خزامیا3، خنور، ذرت، سیدکو، شپلی، غبهنوش، فالوم، فرآور، فپنتا3، مارون، وآذر، وبملت2` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شد؛ نمادهای دارای OCF معتبر کنار گذاشته شدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برابر ۱۹ فایل موفق شد. نرمال‌سازی `224` رکورد از `75` سند رسمی تولید کرد؛ `26` سند child-entity/غیرقابل‌استخراج رد شدند و هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `50e0690a7849f55f02c129939d9955a9d791aa51b39b336333d7b796572725aa` و JSONL با SHA-256 `f75b1f8c60272cdb5b79eeee20a6b739a4d057f57439eaf54f89f4fbb68d62be` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery139-before-import.dump` با اندازهٔ `154591309` بایت، SHA-256 `f021b0aa9777d2e8a7621bebc6ea108c3baf912c1a14f238bf798f712fbade27` و `pg_restore -l` موفق ثبت شد. import artifact-only با `inserted=92`, `standard_facts=95` و validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh Production برای هر ۱۹ نماد با `ok=19`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery139-refresh.json` با SHA-256 `e87b5ebd76cfaaf5e04f017732c2ef78114ee65018d92dd30cfa326e33a8c428` ثبت است. audit نهایی با SHA-256 JSON `7161232a85965c4ecd16d294eb5f4f7f03b4fc4bf677a5778b0da2ae89ec8ebe` و CSV `149beec904fb0d0e233629643a1a2c24c685c2515c59a93f283613327340791a` ثبت شد: `1524` ابزار فعال، `18203` دوره، `71979` fact خام و `38195` fact معتبر. دوازده نماد به پوشش `100.0%` رسیدند؛ ارفع، اپرداز3، تاصیکو، خزامیا3، فپنتا3 و وبملت2 با پوشش `85.71%` در `SNAPSHOT_COVERAGE_GAP` باقی ماندند و نمادهای دارای `INSUFFICIENT_DATA` گیت اعتماد تحلیلی را حفظ کردند.
- registry عمومی recovery139 با source در `artifacts/audits/public-645-gate-registry-20260902-recovery139-source.json`، reconciled JSON با SHA-256 `22129f2abb619baac472a0b6a0d395981657968fce7e431a15e4fc4052b79225` و CSV با SHA-256 `cf1d33f0cc227e6e4ee11b07917efedb88421af81708ad76345ba51b1c5a8889` ثبت شد؛ gateها `SNAPSHOT_COVERAGE_GAP=121`, `ANALYTICAL_CONFIDENCE_GATE=427`, `RECOVERY_CLOSED=88` و `NO_KNOWN_DATA_GATE=9` هستند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T101613Z.tsv` با SHA-256 `c6e61e505215aa5fc800108c383f0507cbbb267106e41171b29881bc1bf7ff72` ثبت شد. دو backup فعلی recovery139 و recovery138 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - recovery140، cash-flow رسمی برای موج ۷ نمادی

- موج هدفمند شامل `وبملت3، وسدید، وشهر، وصندوق3، ونفت3، ونیکی، وپارس3` پس از بررسی مستقیم Production و تأیید کمبود `operating_cash_flow` انتخاب شد؛ نمادهای `آ س پ` و `وفتخار` به‌دلیل داشتن OCF معتبر وارد نشدند.
- capture محلی browser/Codal با منبع `browser/codal.ir` برابر ۷ فایل موفق شد. نرمال‌سازی `37` رکورد از `12` سند رسمی تولید کرد؛ `24` سند child-entity/غیرقابل‌استخراج رد شدند و هیچ مقدار یا هویت حدسی وارد نشد. manifest نرمال‌سازی با SHA-256 `59aa8df7408c6b233fed9830046726d13ee49f81d22eb11a8d3012f92a8ad94f` و JSONL با SHA-256 `74a0dfa825b259951e511ec42222e174928802dfa405765a2029859b18869c5f` ثبت شد.
- backup پیش از import در `/var/backups/boursnegar/20260902T-recovery140-before-import.dump` با اندازهٔ `154659246` بایت، SHA-256 `27dda5b6acbbc105f420ba49c9510eeb2b8eda70b2a00c4fd92b8956a82a1eda` و `pg_restore -l` موفق ثبت شد. import artifact-only با `inserted=5`, `standard_facts=5` و validation error صفر؛ دو replay هر دو `inserted=0`, `standard_facts=0` و validation error صفر دادند.
- refresh Production برای هر ۷ نماد با `ok=7`, `errors=0` انجام شد؛ checkpoint در `artifacts/recovery140-refresh.json` با SHA-256 `43b8112edfac073658824531cc2c2a86c6cc40013aefa71b90aa7e78661833b7` ثبت است. audit نهایی با SHA-256 JSON `b4ec29468a4aceccda573272d5b3008c37a346e17bb9e92d316fb995f1d47431` و CSV `9a61e050b141ccd5f47461db0d4a45eb3433789cd2e38a1fd6bfddca62d0f99f` ثبت شد: `1524` ابزار فعال، `18203` دوره، `71984` fact خام و `38200` fact معتبر. نتیجهٔ این موج در snapshotها ثبت شد و گیت‌های پوشش/اعتماد دست‌نخورده باقی ماندند.
- retention با policy تأییدشدهٔ دو dump اجرا شد؛ گزارش `artifacts/audits/production-backup-retention-20260901T102351Z.tsv` با SHA-256 `bba42d528ad4369b85e0a27cb328c9060eb3d8561f598d9ffe91359083d6ec6e` ثبت شد. دو backup فعلی recovery140 و recovery139 هستند. observer `PASS` با disk `65%`، data-service health `{"status":"ok"}` و وب readiness `{"status":"ready","auth":"email_password","mail":"ready"}` باقی ماندند.

## 2026-09-02 - بازبینی گیت‌های باقی‌مانده پس از recovery140

- اجرای مجدد `scripts/remote-final-gate.sh` روی Production با خروجی `REMOTE_FINAL_GATE=PASS` انجام شد؛ readiness وب، health سرویس داده، PM2، systemd، مجوز فایل‌های محیط و کنترل artifactهای موقت همگی تأیید شدند.
- صف recovery نمادهای دارای کمبود واقعی `operating_cash_flow` پس از موج‌های recovery138 تا recovery140 به پایان رسید؛ دو کاندید باقی‌مانده (`آ س پ` و `وفتخار`) OCF معتبر دارند و recovery جدید برایشان مجاز یا لازم نیست.
- گیت احراز هویت‌شدهٔ moderator/comment/reward همچنان عمداً باز است؛ بدون نشست و هویت مجاز واقعی نباید شبیه‌سازی شود. QA تعاملی تصویری مرورگر نیز تا اجرای مرورگر متصل با شواهد DOM/console/network در viewportهای لازم، بسته اعلام نمی‌شود.

## 2026-09-02 - QA مرورگر زنده پس از recovery140

- صفحهٔ اصلی Production با Google Chrome واقعی در viewportهای `1440x1200`، `768x1024` و `375x812` رندر شد؛ هر سه screenshot غیرخالی و چیدمان responsive قابل مشاهده بود. artifactها در `artifacts/qa-live-20260902/` ثبت شدند.
- SHA-256 screenshotها: desktop=`b30569eb292798b2be893b6be08bbd2862e1cbd3eabff030b4ce51fcb8dbae26`، tablet=`508f9f70af27dd9775db8cc2e096e79e3b640471d1679f5252577376753f7d29`، mobile=`e9cdfeca590ff424abc2ee6d134c6eddfa3093eeddbae875addae26995da9ae6`. DOM dump هر سه viewport نیز نگهداری شد.
- این QA برای رندر عمومی و non-auth معتبر است؛ E2E واقعی moderator/comment/reward هنوز بدون نشست مجاز انجام نشده و endpointهای عمومی در یک تلاش جداگانه به‌دلیل timeout شبکه شواهد قطعی ندادند؛ هیچ‌کدام PASS فرض نشد.
- در کنترل تعاملی Chrome، عنوان صفحه و کنترل‌های اصلی شناسایی شدند و ورودی نماد مقدار `فولاد` را پذیرفت؛ DOM dump با SHA-256 `cbb2b94e1b88a315610cd262c1178675e7caa220549ba4ade26a545ce6f007d2` در `artifacts/qa-live-20260902/interactive.json` ثبت است. کلیک تا صفحهٔ نماد به‌دلیل جابه‌جایی target در headless شواهد پایدار نداد و عمداً PASS اعلام نشد.
- صفحهٔ نماد واقعی `/s/فولاد` در Chrome با H1 و title درست، canonical `https://boursnegar.ir/s/%D9%81%D9%88%D9%84%D8%A7%D8%AF` و ۱۶ لینک مستقیم کدال بررسی شد؛ DOM desktop با SHA-256 `301bb20839fd33b4b401112cceb387ee7766b3f90ec78bc26ff36c19030e6c0e` در `artifacts/qa-live-20260902/stock-page.json` ثبت است.
- همان صفحه در viewport دقیق `375x812` بدون overflow افقی (`scrollWidth=360`, `clientWidth=360`) و با H1 فولاد و ۱۶ لینک کدال بررسی شد؛ artifact با SHA-256 `8103b62d02f795cde6aa8f9f891c4ed8609184cf1c210cbcf3e757cb0dd20b73` در `artifacts/qa-live-20260902/stock-page-mobile-exact.json` ثبت است.

## 2026-09-02 - تصمیم تحلیلی: رژیم توقف بازار 1404/12 تا 1405/02

- پیشنهاد کاربر دربارهٔ اثر توقف طولانی بازار تأیید شد و به‌عنوان یک گیت تحلیلی ثبت می‌شود. تاریخ‌ها باید بر اساس شواهد تقویمی نگهداری شوند: آخرین روز کاری عادی پیش از بحران 1404/12/06 گزارش شده، جلسهٔ 1404/12/09 ابطال/متوقف شد و بازگشایی عمومی بازار سهام برای 1405/02/29 اعلام شد؛ 1405/02/18 هنوز پایان توقف قطعی نبود. منابع ثبت‌شده: گزارش توقف اولیه و اطلاعیهٔ سازمان در `https://www.chn.ir/stock-exchange-and-forex/235403/`، گزارش تعویق تا 1405/02/21 در `https://digiato.com/finance-investment/seventy-day-uncertainty-for-shareholders` و اعلام بازگشایی 1405/02/29 به نقل از سازمان بورس در `https://www.tasnimnews.ir/fa/news/1405/02/26/3592525/بازار-سهام-از-روز-سه-شنبه-بازگشایی-می-شود`.
- در طراحی بعدی، این بازه به‌صورت `MARKET_CLOSURE_REGIME` و با `closure_start=1404/12/09`، `reopen_date=1405/02/29`، `last_normal_session=1404/12/06` و `reopen_discovery_window=20 trading sessions` ثبت می‌شود؛ روزهای بسته نباید با قیمت صفر، حجم صفر، forward-fill یا بازده ساختگی پر شوند.
- بازده و شاخص‌های تکنیکال باید بر مبنای جلسهٔ معاملاتی محاسبه شوند. فاصلهٔ قیمت آخرین جلسهٔ عادی تا نخستین جلسهٔ بازگشایی باید به‌عنوان `closure_gap_return` و جدا از بازده عادی پس از بازگشایی گزارش شود؛ برای ۵، ۱۰ و ۲۰ جلسهٔ نخست، regime flag و کاهش اعتماد/`DATA_REVIEW` اعمال شود.
- برای صورت‌های مالی، `period_end`، `published_at` و `available_at` از هم جدا می‌مانند. تأخیر انتشار به‌تنهایی نباید به‌عنوان افت عملکرد یا missing evidence تعبیر شود؛ گزارش‌های دیررس باید با برچسب `REPORTING_DELAY_AROUND_CLOSURE` وارد تحلیل point-in-time شوند و مقایسه فقط با دورهٔ هم‌طول، هم‌دامنه و هم‌واحد انجام شود.
- رشد ناگهانی قیمت پس از بازگشایی نباید مستقیماً رشد بنیادی تلقی شود. در تحلیل باید بازده بازار/صنعت، بازده ویژهٔ سهم، نقدشوندگی و پنجرهٔ کشف قیمت جدا شوند؛ تا تکمیل پنجرهٔ کشف قیمت، نتیجهٔ قطعی فقط با evidence بنیادی مستقل مجاز است.

## 2026-09-02 - ممیزی و اصلاح نخستین مصرف قیمت‌ها در رژیم توقف

- ممیزی زندهٔ Production برای `daily_prices` در بازهٔ میلادی `2026-02-28` تا `2026-05-18`، معادل بازهٔ توقف تا روز پیش از بازگشایی اعلام‌شده، `72900` ردیف از `1503` ابزار فعال نشان داد؛ `66070` ردیف حجم صفر داشتند و همه از منبع `tsetmc-closing-price-api` بودند. نمونهٔ فولاد نیز قیمت ثابت با `volume=0` داشت؛ این ردیف‌ها سابقهٔ دریافتی خام هستند، نه جلسهٔ معاملاتی اثبات‌شده.
- بدون حذف یا تغییر دادهٔ خام، CTE قیمت در `_stored_analysis_context` اکنون فقط `quality_status='VALID' AND volume>0` را وارد محاسبهٔ مشاهدهٔ قیمت، سهام و قیمت‌های ۹۰/۳۶۵ روزه می‌کند. بنابراین روزهای بسته یا placeholderهای حجم‌صفر وارد بازده و شاخص‌های روند نمی‌شوند؛ فیلترهای تکمیلی پنجرهٔ کشف قیمت باید در مرحلهٔ بعد به خروجی عمومی اضافه شوند.
- این اصلاح کوچک و قابل بازگشت است و هنوز به‌تنهایی به معنی حل کامل تحلیل توقف نیست؛ گیت‌های `MARKET_CLOSURE_REGIME`، تفکیک `closure_gap_return`، برچسب `REPORTING_DELAY_AROUND_CLOSURE` و پنجرهٔ ۵/۱۰/۲۰ جلسه‌ای همچنان الزام‌های فعال‌اند.

## 2026-09-02 - سیاست تحلیل بنیادی پس از توقف طولانی بازار

- چارچوب پیشنهادی کاربر پذیرفته شد: توقف بازار باید به‌عنوان پنهان‌شدن ریسک و اختلال در کشف قیمت مدل شود، نه حذف ریسک. مقایسهٔ قیمت با بازارهای موازی، تورم و ارز فقط با منبع و تاریخ مشاهدهٔ مستقل مجاز است.
- برای هر نماد، اثر عملیاتی باید از افشای رسمی شرکت استخراج شود: تولید، فروش، صادرات، زنجیرهٔ تأمین، خسارت، هزینهٔ مالی و نقدشوندگی؛ ادعاهای کلی دربارهٔ تعداد شرکت‌های آسیب‌دیده یا افت ارزش بازار بدون منبع رسمی وارد داده یا تصمیم نمی‌شوند.
- قیمت پس از بازگشایی باید با برچسب مداخله/محدودیت بازار، نقدشوندگی و پنجرهٔ کشف قیمت تفسیر شود. رشد قیمت به‌تنهایی نشانهٔ بهبود بنیادی نیست و بازده بازار، صنعت و ویژهٔ سهم باید جدا گزارش شوند.
- گزارش‌های پیش از توقف برای تصمیم جاری «قدیمی بالقوه» محسوب می‌شوند، اما حذف نمی‌شوند. گزارش جدید بر اساس `period_end`، `published_at` و `available_at`، هم‌طول و هم‌واحد با دورهٔ مقایسه سنجیده می‌شود؛ تأخیر ناشی از توقف با `REPORTING_DELAY_AROUND_CLOSURE` مشخص خواهد شد.
- خروجی محافظه‌کارانهٔ مورد انتظار در نبود شواهد کافی `DATA_REVIEW` یا `INSUFFICIENT_DATA` است؛ هیچ تعدیل تورمی، ارزی، خسارت جنگی یا ارزش جایگزینی به‌صورت حدسی تولید نمی‌شود.

## 2026-09-02 - هم‌راستاسازی قالب صفحهٔ اول با مرجع سولی‌تریدر

- قالب صفحهٔ اول با حفظ معماری موجود به سمت پایانهٔ تحلیلی حرفه‌ای‌تر رفت: پیام روشن محصول، جست‌وجوی نماد به‌عنوان اقدام اصلی، داشبورد زنده، اعتماد داده‌ای و مسیر منابع در همان viewportهای اصلی حفظ شدند.
- نوار جدید `market-context` وضعیت فعال بودن پایگاه داده، زمینهٔ توقف بازار و دو اقدام سریع برای اسکرینر و منابع داده را نمایش می‌دهد؛ متن آن وعدهٔ سود یا سیگنال نیست و با provenance محصول سازگار است.
- فایل‌های تغییرکرده `web/src/AppProduction.tsx` و `web/src/production.css` هستند. `npm run lint` و `npm run build` موفق شدند؛ QA مرورگر نهایی این نسخه هنوز باید روی Production پس از انتشار انجام شود.

## 2026-09-02 - انتشار نسخهٔ قالب جدید روی Production

- backup قبل از انتشار وب در `/var/backups/boursnegar/20260901T145554Z-ui-solitrader-inspired-web-before-deploy.tar.gz` ایجاد شد؛ release مستقل در `/var/www/boursnegar-releases/20260901T145554Z-ui-solitrader-inspired` قرار گرفت و `/var/www/boursnegar-current` به‌صورت اتمیک به آن اشاره می‌کند.
- در اولین راه‌اندازی، نبودن symlink فایل محیط مشترک شناسایی شد؛ بدون تغییر در secrets، `.env` release به `/var/www/boursnegar-shared/web.env` متصل و PM2 دوباره راه‌اندازی شد.
- پس از اصلاح، PM2 آنلاین، `healthz` برابر `{"status":"ok"}`، `readyz` برابر `{"status":"ready","auth":"email_password","mail":"ready"}` و پاسخ صفحهٔ اصلی HTTP 200 تأیید شدند. QA مرورگر متصل در این نوبت در دسترس نبود و ادعای visual PASS برای این release ثبت نمی‌شود.

## 2026-09-02 - ممیزی کنتراست همهٔ سطوح فرانت و انتشار اصلاح

- ممیزی importها و selectorهای فرانت نشان داد صفحهٔ اصلی، صفحهٔ نماد، اسکرینر، گزارش تحلیل، پنل حساب/مدیریت، مودال‌ها و بخش پرداخت همگی در bundle Production حضور دارند؛ `redesign.css` tokenهای مشترک را روی سطوح تیره اعمال می‌کند.
- دو ناحیهٔ با قواعد قدیمی روشن شناسایی و اصلاح شد: `comments-section`/فرم نظر و `payment-form`. اکنون پس‌زمینه، متن، placeholder، textarea و پیام‌های این بخش‌ها با tokenهای پوستهٔ فعلی جدا و خوانا هستند.
- نسخهٔ اصلاح‌شده در `/var/www/boursnegar-releases/20260901T161647Z-ui-contrast-fix` منتشر شد؛ backup قبل از انتشار ایجاد شد. PM2، `healthz` و `readyz` پس از انتشار موفق‌اند.
- مرورگر متصل در این نوبت در دسترس نبود؛ بنابراین ادعای بررسی بصری تک‌تک stateها و viewportها ثبت نمی‌شود. بررسی source/CSS انجام شده و QA مرورگر برای نوبت اتصال مرورگر باقی است.

## 2026-09-05 - تکمیل گیت قیمت و تست‌ها

- ممیزی مصرف‌های backend نشان داد dashboard، screener، MA20/MA50، بازده یک‌ماهه، history نماد و peerها باید از ردیف‌های `volume=0` جدا شوند؛ همهٔ این مسیرها اکنون `quality_status='VALID' AND volume>0` دارند و شمارش خام overview/provenance دست‌نخورده است.
- نسخهٔ backend در release `/var/www/boursnegar-releases/20260905T062644Z-market-closure-analytics` با backup قبل از انتشار مستقر شد؛ `healthz` و `readyz` پس از rollout سبز هستند.
- تست وابسته به artifact پاک‌شده در `test_link_orphan_candidates.py` به fixture موقت deterministic تبدیل شد؛ مجموعهٔ کامل `111` تست با `OK` تمام شد و `project-memory-check` و `git diff --check` موفق‌اند.
- تلاش QA مرورگر برای `https://boursnegar.ir` با `ERR_QUIC_PROTOCOL_ERROR` متوقف شد؛ visual PASS جدید ثبت نمی‌شود و گیت مرورگر و E2E احراز هویت‌شده همچنان باز است.

## 2026-09-05 - QA مرورگر محلی و تکرار گیت Production

- صفحهٔ اصلی release فعلی در Browser محلی رندر شد؛ screenshot دسکتاپ و `375x812` گرفته شد. navigation، hero، پنل پایگاه داده، جست‌وجو و `market-context` بدون overlap یا خطای console دیده شدند.
- تلاش route نماد در محیط محلی به‌دلیل نبود API محلی به state خطا رسید و PASS نشد. تلاش مستقیم Production و مسیر `www` نیز با `ERR_QUIC_PROTOCOL_ERROR` در Browser شکست خورد؛ این گیت هنوز معتبر است و با health/readiness جایگزین نشده است.

## 2026-09-05 - QA محلی viewport صفحهٔ اصلی

- نسخهٔ build‌شده در Vite محلی با Browser بررسی شد؛ DOM صفحهٔ اصلی شامل banner، navigation، heading، جست‌وجوی نماد و `market-context` سالم بود و خطای console ثبت نشد.
- screenshot دسکتاپ و موبایل `375x812` ثبت و به‌صورت بصری بررسی شدند؛ هدر، hero، پنل پایگاه داده و فرم جست‌وجو بدون overlap دیده شدند و layout موبایل یک‌ستونه و قابل استفاده بود.
- route نماد در محیط محلی به API دادهٔ محلی متصل نیست و با state خطا نمایش داده شد؛ این route در این نوبت PASS نشد. شواهد قبلی Production برای صفحهٔ فولاد جداگانه حفظ است.

## 2026-09-05 - ادامهٔ QA قالب Production

- وضعیت زنده دوباره تأیید شد: release فعال `20260901T161647Z-ui-contrast-fix`، PM2 آنلاین، `healthz` و `readyz` سبز، مصرف دیسک `65%`.
- تلاش مجدد برای QA بصری مرورگر به‌دلیل timeout اتصال مرورگر کامل نشد؛ این مورد همچنان باز است و visual PASS برای همهٔ viewportها ادعا نمی‌شود.
-
## 2026-09-05 - بستن QA بصری با تونل داخلی Production

- برای جلوگیری از وابستگی به خطای Cloudflare/QUIC، تونل موقت SSH به listener داخلی Production برقرار شد؛ هیچ تنظیم عمومی یا احراز هویتی تغییر نکرد.
- صفحهٔ اصلی در Production با دادهٔ زنده در viewport دسکتاپ و `375x812` بررسی شد؛ navigation، hero، جست‌وجو، پنل داده و نوار زمینهٔ بازار بدون overlap دیده شدند.
- صفحهٔ واقعی `/s/فولاد` در Production در موبایل و دسکتاپ بررسی شد؛ H1 یکتا، title صحیح، لینک وب‌سایت رسمی شرکت، تصویر لوگو، ۱۶ لینک مستقیم کدال و نمودار دیده شدند و console error صفر بود. کارت مقایسهٔ هم‌صنعت اصلاح و در release `/var/www/boursnegar-releases/20260905T063054Z-peer-contrast-fix` منتشر شد؛ پس از rollout دوباره با `peer=1` و error صفر تأیید شد.
- گیت احراز هویت‌شدهٔ moderator/comment/reward بررسی شد: endpointها و مرز دسترسی تعریف‌شده‌اند، اما اجرای E2E نیازمند نشست واقعی مجاز است و عمداً شبیه‌سازی نشد.

## 2026-09-05 - ممیزی کامل شوینده و شفاف‌سازی ارزش‌گذاری

- ممیزی زندهٔ Production برای شوینده نشان داد آخرین قیمت تعدیل‌شده `39,582.72` ریال در `2026-09-05` است؛ آخرین مشاهدهٔ معاملاتی پیش از توقف `20,560` ریال و نخستین مشاهدهٔ پس از بازگشایی `22,710` ریال بود، یعنی شکاف بازگشایی حدود `10.46%` تعدیل‌شده. این شکاف از بازده عادی پس از بازگشایی جداست و به‌تنهایی رشد بنیادی محسوب نمی‌شود.
- snapshot آخر شوینده با وضعیت داخلی `INSUFFICIENT_DATA`، پوشش `85.71%` و اطمینان `60%` ثبت شده است؛ `analysisState=MARKET_FUNDAMENTAL_DIVERGENCE` و بازده ۹۰روزه/۳۶۵روزهٔ ذخیره‌شده به‌ترتیب `58.33%` و `150.52%` هستند. بنابراین نتیجهٔ درست فعلاً «بررسی مشروط» است، نه خرید/فروش قطعی.
- ارزش‌گذاری فعلی یک سناریوی P/E داخلی برای خانوادهٔ محصولات شیمیایی است: مبنا `1,772` ریال به‌ازای سهم، ضریب `6.5`، ارزش پایه `11,518` و بازهٔ `9,214` تا `13,822` ریال. EPS گزارش‌شدهٔ صورت مالی حسابرسی‌شده `6,663` ریال است و با مبنای بازار/TTM یکی نیست؛ این اختلاف اکنون در کارت نماد با منبع مبنا و ضریب نمایش داده می‌شود تا فاصلهٔ قیمت و ارزش منصفانه قابل ممیزی باشد.
- برای شوینده در `financial_facts` هیچ fact معتبر `operating_cash_flow` پیدا نشد؛ این کمبود قطعیِ دادهٔ واردشده است، نه اثبات نبودن در همهٔ اسناد کدال. تا بازیابی سند رسمی و تطبیق دوره/واحد، مقدار OCF خالی و گیت `INSUFFICIENT_DATA` باقی می‌ماند و هیچ داده‌ای جعل نشد.
- backend صفحهٔ نماد برای نمایش `valuation_basis_per_share`، `valuation_basis_source` و `valuation_multiple` تکمیل شد. تست‌های وب `75/75`، تست‌های data-service `111/111` و build تولیدی موفق شدند؛ انتشار Production این تغییر شفاف‌سازی هنوز انجام نشده و قبل از آن backup و release gate لازم است.
- تلاش انتشار release آزمایشی `20260905T065700Z-shoyande-valuation-label` با backup `/var/backups/boursnegar/20260905T065700Z-shoyande-valuation-label-before.tar.gz` به‌دلیل ناقص‌بودن بستهٔ release و نبود dependencyهای external مانند `express` متوقف شد؛ rollback به release پایدار `/var/www/boursnegar-releases/20260905T063054Z-peer-contrast-fix` انجام شد و پس از retry، `healthz` و `readyz` سبز هستند. release آزمایشی حذف نشد تا برای بررسی/بازگشت باقی بماند.
- پس از تکمیل ساختار release با `package.json`، `.env` و symlink `node_modules`، همان release با موفقیت فعال شد: `/var/www/boursnegar-current -> /var/www/boursnegar-releases/20260905T065700Z-shoyande-valuation-label`. پس از restart، health/ready سبز و endpoint زندهٔ `/api/stocks/شوینده` مقدارهای شفاف‌سازی‌شدهٔ `market_ttm_eps`, `1772`, `6.5` را برمی‌گرداند؛ وضعیت همچنان `INSUFFICIENT_DATA` و OCF غایب است.

## 2026-09-05 - ممیزی چندنمادی و گیت رژیم توقف

- نمونهٔ طبقه‌بندی‌شدهٔ ۱۵ نماد استخراج شد. تاریخ نخستین معامله معتبر پس از توقف عمومی برای خودرو، شستا، شپنا، فملی، وبملت و چند نماد دیگر `2026-05-19` بود؛ برای شوینده `2026-05-23`، آریا `2026-06-17`، شتران `2026-05-25`، کچاد/کگل `2026-05-26` و فولاد `2026-08-08` بود. این اختلاف نشان می‌دهد گیت باید نمادمحور باشد و بازده واحد تقویمی برای همه نمادها کافی نیست.
- در `_stored_analysis_context` گیت `market_closure_regime`، تاریخ شروع/بازگشایی، `closure_gap_return_percent` و بازده ۵/۱۰/۲۰ جلسه پس از بازگشایی اضافه شد؛ روزهای بدون معامله حذف یا forward-fill نشدند. در `snapshot_v2`، این رژیم confidence را حداکثر ۶۰ می‌کند و تصمیم قطعی را تا عبور از گیت مسدود نگه می‌دارد.
- تست اختصاصی گیت اضافه شد؛ تست data-service `111/111` و تست وب `75/75` موفق، build تولیدی موفق و `git diff --check` موفق است.
- data-service با backup فایل‌محور در `/var/backups/boursnegar/20260905T073000Z-closure-regime/` منتشر شد. سپس web release با backup `/var/backups/boursnegar/20260905T074000Z-closure-regime-ui-before.tar.gz` فعال شد: `/var/www/boursnegar-current -> /var/www/boursnegar-releases/20260905T074000Z-closure-regime-ui`. پس از تأخیر کوتاه startup، PM2، `healthz`، `readyz` و endpoint شوینده تأیید شدند؛ endpoint همچنان OCF غایب و `INSUFFICIENT_DATA` را برمی‌گرداند.

## 2026-09-05 - refresh سراسری رژیم توقف

- scope refresh از audit معتبر شامل `1524` alias جاری انتخاب شد و فایل نمادها در `artifacts/closure-refresh-all-symbols.txt` و checkpoint در `artifacts/closure-refresh-all-checkpoint.json` نگهداری شد.
- قبل از refresh، backup کامل PostgreSQL در `/var/backups/boursnegar/20260905T081500Z-all-snapshot-refresh.dump` با SHA-256 `9d169f586b2b8e39b79ce7407f0997d7a578bb741aae662641d212100e5805e2` ساخته شد؛ فضای آزاد پس از backup حدود `8.3G` باقی ماند.
- refresh مرحله‌ای با endpoint داخلی data-service انجام شد: `723` نماد موفق و `801` نماد با `404` مستند برگشتند؛ تمام 404ها پیام «گزارش واردشده‌ای موجود نیست» داشتند و به‌عنوان نبود گزارش واردشده، نه نبود تاریخی مطلق، ثبت شدند.
- smoke مستقیم برای فولاد نشان داد خروجی جدید `analysisState=MARKET_CLOSURE_REGIME`، `market_closure_regime=true`، شکاف `-8.51%`، confidence `55%` و decision `INSUFFICIENT_DATA` است؛ گیت برای داده واقعی اعمال شده و تصمیم قطعی را مسدود می‌کند.
- تست نهایی data-service `112/112`، وب `75/75` و typecheck موفق است؛ Production data-service فعال، PM2 آنلاین، release canonical `/var/www/boursnegar-releases/20260905T074000Z-closure-regime-ui` و health/ready سبز هستند.

## 2026-09-05 - تفکیک پوشش و refresh هدفمند روزانه

- endpoint `/api/market/overview` اکنون scopeها را جدا برمی‌گرداند: `instruments=1524` کل نمادهای فعال، `core_ready=721` آماده تحلیل بنیادی و `needs_recovery=803` نیازمند تکمیل داده. داشبورد Production همین سه عدد را با برچسب روشن نمایش می‌دهد.
- به‌جای refresh روزانهٔ پرهزینه برای همهٔ نمادها، `refresh_recent_snapshots.py` اضافه و با timer روزانهٔ `boursnegar-snapshot-refresh.timer` فعال شد؛ فقط نمادهایی را که در ۴۸ ساعت گذشته evidence کدال گرفته‌اند refresh می‌کند. در زمان نصب، query بررسی کرد که evidence جدیدی برای پردازش وجود ندارد (`0` نماد)، پس پردازش بی‌مورد اجرا نشد.
- backup تنظیمات پیش از نصب در `/var/backups/boursnegar/20260905T091500Z-targeted-refresh/` نگهداری شد. timer فعال و enabled است و زمان اجرای بعدی ثبت شده است.
- تست‌ها پس از تغییرات: data-service `112/112`، وب `75/75`، typecheck و `git diff --check` موفق؛ data-service، PM2، `healthz` و `readyz` سبز هستند. موارد باز آگاهانه: backlog `803` نماد کم‌داده، تکمیل OCFهای فاقد سند، و E2E مرورگر عمومی/نشست احراز هویت‌شده.

## 2026-09-05 - ممیزی تازگی کدال، مدل صنایع و ارزش‌گذاری

- آخرین `disclosure_versions.retrieved_at` در Production برابر `2026-09-01 10:12:41 UTC` است؛ در هفت روز اخیر دریافت‌ها فقط در روزهای ۲۹ اوت تا ۱ سپتامبر ثبت شده‌اند. job کدال روی Production نصب بود اما timer غیرفعال بود و unit واقعی فقط نماد `دکوثر` را اجرا می‌کرد؛ timer فعال شد و unit با backup `/var/backups/boursnegar/20260905T100000Z-codal-unit-fix/service.before` به manifest کامل `--symbol *` اصلاح شد. اجرای دستی پس از آن با `inserted=0` تمام شد؛ این فقط نشان می‌دهد artifact جدید محلی برای import موجود نبود، نه اینکه کدال قطعاً اطلاعیه جدیدی نداشته است.
- توزیع مدل خانواده‌ها در ۱۳ گروه: `fund=419`, `general=281`, `metals=158`, `petrochemical=140`, `financial=170`, `pharmaceutical=77`, `food=73`, `cement=70`, `real_estate=43`, `bank=23`, `ceramics=14`, `holding=14`, `unclassified=42`. بنابراین همه صنایع مدل اختصاصی ندارند؛ `general` سناریوی محافظه‌کارانه عمومی است و `unclassified` بدون ارزش‌گذاری می‌ماند.
- ممیزی کد نشان داد محدوده خرید ارزش‌گذاری از `fairValueBase*0.80` و محدوده فروش از `fairValueHigh*1.15` ساخته می‌شود؛ در روند صعودی، محدوده خرید با حمایت/ATR به‌صورت `LEAST` و محدوده فروش با `GREATEST` ترکیب می‌شود. این محاسبه از نظر ریاضی سازگار است، اما صحت اقتصادی آن به اعتبار EPS، واحد، دوره، مدل خانواده و شواهد بنیادی وابسته است؛ بنابراین ارزش‌های مدل عمومی همچنان «سناریویی» هستند، نه ارزش ذاتی قطعی.
- endpoint `/api/market/overview` اکنون تفکیک scope را نمایش می‌دهد و refresh هدفمند روزانه فعال است. وضعیت Production پس از اصلاح unit و timer: سرویس داده active، PM2 online، health/ready سبز.

## 2026-09-06 - مسیر canonical پایش روزانهٔ کدال

- به‌دلیل نبودن collector محلی زمان‌بندی‌شده، `data-service/scripts/daily_codal_monitor.py` اضافه شد. این supervisor رجیستری فعال را از Production می‌خواند، با cursor پایدار هر اجرا فقط یک batch محدود انتخاب می‌کند، برای اجرای هم‌زمان advisory lock دارد، و فقط به `daily_local_ingestion.py` موجود با مسیر Codalpy-first و fallback مرورگر واگذار می‌کند.
- unit و timer متناظر در `ops/systemd/boursnegar-local-codal-monitor.service` و `ops/systemd/boursnegar-local-codal-monitor.timer` ثبت شدند. اجرای واقعی عمداً در این نوبت انجام نشد؛ dry-run روی رجیستری واقعی با batch دو نماد موفق بود و هیچ artifact یا داده‌ای به Production وارد نشد.
- regression test برای state اتمیک و شروع cursor اضافه شد؛ کل data-service اکنون `123/123` تست موفق و `git diff --check` موفق دارد. این تغییر جایگزین batchهای ترتیبی NAV یا recovery نمی‌شود و آن صف‌ها عمداً متوقف باقی می‌مانند.
- گیت‌های باز همچنان واقعی‌اند: تازگی اطلاعیهٔ Production تا دریافت artifact محلی جدید اثبات نمی‌شود، ورودی‌های DCF/FCFE/Residual کافی نیست، NAV صندوق‌های فاقد سند رسمی تکمیل نشده، و backtest افق ۲۰ جلسه‌ای نمونهٔ کافی ندارد.
- supervisor روزانه idempotent شد: state اکنون `last_date` را نگه می‌دارد و اجرای تکراری همان تاریخ بدون `--force` فقط `already-ran-today` برمی‌گرداند؛ تست‌ها پس از این اصلاح `124/124` موفق‌اند و dry-run رجیستری واقعی همچنان موفق است.
- unit محلی در `/home/king/.config/systemd/user/` نصب و timer با `systemctl --user enable` و `start` فعال شد؛ وضعیت `active (waiting)` و نخستین trigger برای 2026-09-07 ساعت 06:32:58 EDT ثبت شد. اجرای فوری انجام نشد تا سهمیهٔ کدال مصرف نشود؛ این نخستین اجرای زمان‌بندی‌شده باید با evidence واقعی Chrome و manifest بررسی شود.
- برای کنترل سهمیه و امکان بررسی evidence، اندازهٔ batch پیش‌فرض پایش روزانه از ۵۰ به ۱۰ نماد کاهش یافت؛ unit نصب‌شدهٔ کاربر نیز با daemon-reload به همین مقدار به‌روزرسانی شد.
- نخستین اجرای واقعی `boursnegar-local-codal-monitor.service` در 2026-09-06 موفق شد. precheck از ۱۰ نماد فقط `آبادا3، آتش، آتی1` را واجد refresh دانست؛ Codalpy برای ۱۸ درخواست failure ثبت کرد و fallback واقعی Chrome یک اطلاعیه/Excel برای `آتش` تولید کرد. پس از normalize، ۵ fact و ۱ notice با manifest وارد Production شدند؛ importerها به‌ترتیب `inserted=5` و `inserted=1` و خطای اعتبارسنجی صفر گزارش کردند. backup پیش از write در `/var/backups/boursnegar/20260906T122825Z-daily-monitor-before.dump` با SHA-256 `ee58d54aef5e90e10da233305ae234aded0e91557bd97d6512e9e138f5a55151` ثبت است.
- aliasهای جریان نقدی بازبینی شد: «دریافت تسهیلات» و «بازپرداخت تسهیلات» به‌تنهایی دیگر به‌عنوان `net_borrowing` پذیرفته نمی‌شوند؛ فقط برچسب صریح جریان خالص مجاز است. این اصلاح از تولید FCFE/DCF بر مبنای یک جزء ناخالص جلوگیری می‌کند و برای انتشار بعدی نیازمند backup و release gate است.
- برای قرارداد فوق regression test اضافه شد؛ تست صراحتاً هر دو برچسب تک‌جزئی را رد و برچسب صریح `دریافت(پرداخت)تسهیلات` را قبول می‌کند.
- بلافاصله پس از import، `boursnegar-snapshot-refresh.service` دستی و هدفمند اجرا شد؛ `total=2، ok=2، errors=0` و `/readyz` برابر `ready` بود. این شواهد چرخهٔ کامل محلی تا refresh Production را تأیید می‌کند؛ نبود اطلاعیه برای نمادهای دیگر به‌عنوان absence قطعی اعلام نمی‌شود.
- ممیزی تازهٔ `audit_valuation_input_gates.py` روی Production برای ۱۵۲۴ نماد فعال، `461 PASS` و `1063 REVIEW` گزارش کرد. این ۴۶۱ نماد هر پنج گیت پایهٔ سهام، OCF، حقوق مالکانه، سود مثبت دو دوره و واحد سود را دارند و باید منبع انتخاب recovery بعدی جریان‌های نقدی باشند؛ این نتیجه جایگزین شواهد موردی CapEx/Net Borrowing نیست.
- backtest read-only پس از refresh جدید دوباره اجرا شد: `total_model_snapshots=4116`، افق ۵ جلسه‌ای `2446 READY`، افق ۱۰ جلسه‌ای `55 READY` و افق ۲۰ جلسه‌ای `9 INSUFFICIENT_SAMPLE` باقی ماند. snapshotهای تازهٔ امروز عمداً برای افق ۲۰ جلسه‌ای استفاده نشدند، چون هنوز forward window معتبر ندارند.
- پایش روزانه پس از اجرای موفق، فقط profile موقت Chrome را پاک می‌کند و manifest، checkpoint، اسناد خام و normalized را نگه می‌دارد؛ regression test تضمین می‌کند `manifest.json` باقی بماند. این کار از رشد بی‌دلیل فضای دیسک در اجرای روزانه جلوگیری می‌کند.
- مسیر پایش روزانه به رجیستری کامل SQLite محلی (`artifacts/local-ingestion.sqlite3`, تعداد ۱۵۲۴ نماد) منتقل شد؛ دیگر برای انتخاب نماد به Production query یا `--precheck` وابسته نیست و نمادهای `complete` نیز برای noticeهای همان روز بررسی می‌شوند. این تغییر منبع انتخاب را با معماری Local-first هم‌راستا می‌کند.
- اجرای force دوم برای batch بعدی (`آرام، آرامش، آردینه، آرمان، آرمانح، آرمانی، آریا، آریا3، آریان، آس`) با fallback Chrome موفق شد؛ Codalpy برای ۷۸ درخواست failure و browser یک notice با ۷ رکورد normalized تولید کرد، اما importها `inserted=0` و بدون validation error بودند. برای جلوگیری از overwrite manifest در retry همان روز، مسیر خروجی از این پس در صورت force به زیرپوشهٔ `cursor-XXXX` می‌رود؛ artifact خام اجرای قبلی حفظ شده است.
- اجرای force سوم نشان داد Codalpy در monitor روزانه ناخواسته بازه‌های تاریخی را نیز می‌خواند: ۶ فایل و `342` ردیف وارد شد، هرچند validation error صفر بود. این رفتار برای daily notice monitoring نامناسب است؛ monitor اصلاح شد تا Codalpy را کنار بگذارد و فقط `html-only` و بازهٔ همان روز را با Chrome اجرا کند. backfill تاریخی همچنان جدا و صریح باقی می‌ماند.
- نمونهٔ recovery بنیادی برای `آبین` از بین نمادهای دارای پنج گیت پایه انجام شد. هشت سند رسمی و ۱۳ رکورد normalized به‌دست آمد؛ فقط OCF، سود و ترازنامه استخراج شد و CapEx/Net Borrowing صریح و هم‌دوره پیدا نشد. importer با `inserted=0` و خطای اعتبارسنجی صفر پایان یافت؛ artifact در `data-service/artifacts/fcfe-target-آبین-20260906/` حفظ شد و گیت DCF/FCFE عمداً باز ماند.
- در همان نمونه مشخص شد OCF به‌دلیل عنوان گزارش، نوع خروجی `income_statement` گرفته است. `fact_output_type` اصلاح شد تا `operating_cash_flow` نیز همیشه `cash_flow` باشد؛ regression test برای این قرارداد اضافه شد و هیچ fact Production با این patch بازنویسی نشد.
- بازپردازش artifact واقعی آبین پس از اصلاح، `13` رکورد و `8` سند را با همان `2` خطای مستند تولید کرد و OCF را با `output_type=cash_flow` تأیید کرد؛ CapEx/Net Borrowing هنوز رکوردی ندارند و import مجدد انجام نشد.
- ممیزی فضای checkout نشان داد `235` پروفایل disposable با نام `.chrome-codal-profile-*` از recoveryهای قبلی باقی مانده‌اند؛ پس از اطمینان از جدا بودن آن‌ها از artifact، manifest، سند خام و backup، فقط همین پروفایل‌ها حذف شدند و حدود `20G` فضا آزاد شد. monitor روزانهٔ جدید در اجرای موفق profile موقت خود را پاک می‌کند و نباید این انباشت تکرار شود.
- monitor روزانه پس از import موفق، اجرای `boursnegar-snapshot-refresh.service` را با `ssh ... systemctl start --wait` الزام‌آور می‌کند؛ در صورت شکست refresh، cursor و `last_date` جلو نمی‌روند. بنابراین «ورود evidence» و «قابل‌مشاهده شدن snapshot تحلیلی» دیگر دو چرخهٔ جدا و فراموش‌شدنی نیستند. regression suite پس از این تغییر `129` تست موفق دارد.
- اجرای کنترل‌شدهٔ نسخهٔ جدید با batch یک‌نمادی برای `آفاق` در `1405/06/15` فقط HTML همان روز را بررسی کرد: browser `files=0` و بدون خطا، normalized/events صفر، importها idempotent (`inserted=0` و validation error صفر). سپس refresh واقعی Production اجرا شد و `total=2، ok=2، errors=0` و `/readyz=ready` ثبت شد؛ این اولین evidence کامل برای زنجیرهٔ today-only browser → import → snapshot است.
- اسکریپت `data-service/scripts/boursnegar_daily_supervisor.py` اضافه و unit روزانه به آن منتقل شد. supervisor اجرای bounded monitor را با report زمان‌دار، stdout/stderr، return code، سیاست provenance و تصریح جدایی recovery تاریخی ثبت می‌کند؛ اجرای آزمایشی report `artifacts/daily-supervisor/20260906T125657Z.json` ساخت و suite شامل `129` تست همچنان سبز است.
- بازبینی artifact رسمی `fund-nav-followup-20260906-batch135` برای `خورشید` با normalize مستقل انجام شد: `35` رکورد از `9` سند و بدون خطا؛ هم `nav_per_share` با واحد `IRR` و هم `units_outstanding` با واحد `units` برای دوره‌های `1404/09/30`، `1404/12/29` و `1405/03/31` وجود دارد. این evidence برای promote هدفمند آماده است، اما تا کنترل تطابق issuer/source و backup نهایی انجام نشود، تغییر Production اعمال نمی‌شود. ممیزی Production فعلی `25` رکورد NAV برای `15` نماد و فقط `7` رکورد units برای `3` نماد نشان می‌دهد؛ گیت تعداد واحدها هنوز باز است.
- supervisor اکنون پس از پایش روزانه، `plan_local_recovery.py` را نیز اجرا می‌کند و صف deterministic بازیابی محلی را در `artifacts/daily-supervisor/local-recovery-plan.csv` می‌سازد. اجرای `20260906T125906Z` موفق بود و هر دو مرحله return code صفر داشتند؛ این برنامه‌ریزی جایگزین promote خودکار evidence نامطمئن نمی‌شود.
- اسکریپت `data-service/scripts/promote_evidence.py` برای promote برنامه‌ریزی‌شدهٔ یک manifest رسمی اضافه شد: checksum را قبل از انتقال بررسی می‌کند، backup Production می‌گیرد، نام فایل manifest را حفظ می‌کند، import و replay idempotent را کنترل می‌کند، سپس snapshot و `/readyz` را بررسی می‌کند. اجرای واقعی artifact `خورشید` پس از اصلاح خطای نام فایل، با `validation_errors=[]`، هر دو import با `inserted=0` (داده از قبل موجود بود)، refresh موفق و `/readyz=ready` پایان یافت؛ backup در `/var/backups/boursnegar/20260906T130218Z-evidence-before.dump` ثبت است.
- همان promote برنامه‌ریزی‌شده برای `دامون` نیز اجرا شد. normalize از `3` سند رسمی، `15` رکورد شامل `3` NAV و `3` تعداد واحد با خطای صفر تولید کرد؛ backup در `/var/backups/boursnegar/20260906T130322Z-evidence-before.dump`، هر دو import با `inserted=0` و `validation_errors=[]`، refresh موفق و `/readyz=ready` ثبت شد. صفر بودن insert نشان می‌دهد دادهٔ خام قبلاً موجود بوده و از duplicate جلوگیری شده است.
- ممیزی artifactهای محلی نشان داد `602` فایل بازه‌ای NAV و `307` manifest وجود دارد، اما در JSONLهای قابل‌خواندن فقط `107` رکورد OCF و هیچ رکورد صریح CapEx یا Net Borrowing دیده نشد. بنابراین گیت DCF/FCFE با NAV بیشتر بسته نمی‌شود؛ recovery بعدی باید به‌طور مشخص اسناد جریان نقدی و برچسب‌های خالص را هدف بگیرد، نه تکرار جمع‌آوری NAV.
- artifact رسمی `fcfe-followup-foolad-20260906` با parser فعلی بازپردازش شد: چهار OCF با `output_type=cash_flow` و دو خطای مستند child-entity؛ CapEx و Net Borrowing استخراج نشدند. promote برنامه‌ریزی‌شده با backup `/var/backups/boursnegar/20260906T130526Z-evidence-before.dump` انجام شد؛ `standard_facts=4`، `validation_errors=[]`، replay با `inserted=0`، refresh موفق و `/readyz=ready` ثبت گردید.
- برای جلوگیری از تکرار recovery اشتباه، migration برنامه‌ریزی‌شدهٔ `repair_cashflow_output_types.py` اجرا شد. پس از backup `/var/backups/boursnegar/20260906T130654Z-cashflow-output-type-before.dump`، تعداد `2114` رکورد قدیمی OCF از `income_statement` به `cash_flow` اصلاح شد؛ مقدار، دوره، منبع و provenance تغییر نکرد. شمارش نهایی `2121 cash_flow` و `14 monthly_activity` است؛ refresh موفق و `/readyz=ready` ثبت شد. CapEx و Net Borrowing همچنان صفر و گیت‌شان باز است.
- ممیزی پس از migration روی Production نشان داد OCF اکنون `2135` رکورد برای `635` نماد است و هیچ CapEx یا Net Borrowing ثبت نشده؛ هر `18145` دورهٔ مالی در محدودهٔ معتبر `1..12` ماه قرار دارد و `0` issuer فعال بدون صنعت رسمی گزارش شد. تلاش برای شمارش backtest با فیلتر نادرست روی ستون numeric متوقف شد و هیچ داده‌ای تغییر نکرد؛ معیار معتبر backtest همچنان همان artifact چندافقی قبلی است و افق ۲۰ جلسه‌ای به نمونهٔ کافی نرسیده است.
- planner محلی اصلاح شد تا به‌صورت پیش‌فرض نمادهای `complete` را دوباره وارد صف نکند و اولویت را به کمبود دورهٔ مقایسه‌ای، factهای هسته و اطلاعیه بدهد؛ audit کامل فقط با `--include-complete` ممکن است. صف فعلی از `1524` به `936` نماد واقعی کاهش یافت و اولین مورد `اتکای` با کمبود دورهٔ مقایسه‌ای است. regression suite پس از اصلاح تست قرارداد `129` تست موفق دارد.
- recovery هدفمند دورهٔ مقایسه‌ای برای `اتکای` با مرورگر و بازهٔ `1404/01/01..1405/06/15` اجرا شد. فقط یک اطلاعیهٔ رسمی child-entity با `20` ردیف پیدا شد؛ normalize صفر رکورد و یک خطای صریح `child_entity_financial_statement` ثبت کرد، و هیچ دادهٔ والد یا دورهٔ جدید وارد نشد. این مورد به‌درستی به‌عنوان absence تاریخی اعلام نشد و artifact/checkpoint در `data-service/artifacts/recovery-comparable-atk-20260906/` حفظ شد.
- planner اکنون فایل exclusion پایدار `artifacts/local-recovery-exclusions.txt` را می‌خواند؛ `اتکای` تا دریافت evidence جدید از retry خودکار خارج شد و صف از `936` به `935` مورد رسید. اولین هدف واقعی بعدی `افرا` با کمبود دورهٔ مقایسه‌ای است؛ این کار مانع تکرار recovery child-entity بدون evidence جدید می‌شود.
- به درخواست کاربر در 2026-09-06، کل روند recovery و پایش خودکار متوقف و timer محلی `boursnegar-local-codal-monitor.timer` هم stop و disable شد. سرویس Production متوقف نشد؛ در لحظهٔ توقف `/readyz` برابر `ready` و health وب برابر `ok` بود. ادامهٔ کار نیازمند تصمیم/روال جدید کاربر است.
- کاربر در ادامه صریحاً اعلام کرد توقف شامل اهداف باقی‌مانده نیست؛ timer دوباره enable/active شد و supervisor در `2026-09-06T131601Z` اجرا شد. پایش روزانه در اجرای عادی همان‌روز idempotent ماند، صف recovery با exclusionهای قبلی `934` مورد دارد و هدف بعدی `انتخاب` با کمبود دورهٔ مقایسه‌ای است؛ suite شامل `129` تست موفق است.
- recovery دورهٔ مقایسه‌ای `افرا` با همان بازهٔ رسمی و browser-only انجام شد؛ یک صفحهٔ معتبر بدون سند مالی قابل‌استخراج و بدون خطا ثبت شد، normalize و import هر دو صفر بودند و دادهٔ جدیدی پیدا نشد. `افرا` نیز تا evidence جدید در exclusion پایدار قرار گرفت تا retry کور تکرار نشود.
- ممیزی freshness جدید Production در 2026-09-07: `codal_notice_events.total=30543`، آخرین `retrieved_at=2026-09-07 01:06:56 UTC` و `recent_48h=233`. دادهٔ ذخیره‌شده تازه است، اما timer collector روی Production وجود ندارد؛ freshness با پایش زمان‌بندی‌شده یکی نیست.
- defaultهای `daily_codal_monitor.py` در 2026-09-07 اصلاح شد تا state، lock، local DB و output همگی زیر `data-service/artifacts` canonical باشند؛ اجرای default قبلی که به‌دلیل مسیر اشتباه `no-active-symbols` می‌داد، اکنون dry-run معتبر تولید می‌کند. تست monitor: `6/6` موفق.
- پس از اصلاح مسیرهای default، کل suite داده اجرا شد: `136/136` تست موفق و `git diff --check` موفق؛ هیچ تغییر Production در این verification انجام نشد.
- verification وب پس از تغییرات: `npm run typecheck` موفق، `75/75` تست Vitest موفق و `npm run build` موفق؛ ناسازگاری قراردادی یا build جدید دیده نشد.
- regression مربوط به مسیرهای canonical اضافه شد؛ suite اختصاصی monitor اکنون `7/7` موفق است، timer کاربر `enabled/active` است و اجرای default امروز به‌درستی `already-ran-today` برگشت.
- verification نهایی این مرحله کل suite data-service را پس از regression جدید با `137/137` تست موفق و `git diff --check` موفق تأیید کرد؛ artifactهای مدیریتی `PROJECT_BACKLOG.md` و `GOAL_COMPLETION_MATRIX.md` نیز موجودند.
- ناسازگاری مسیر در `daily_orchestrator.py` و unit زمان‌بندی‌شده اصلاح شد: local DB و artifact root اکنون هر دو زیر `data-service/artifacts` canonical هستند. تست‌های orchestrator/monitor `11/11` موفق و dry-run orchestrator با `production_write=false` موفق شد.
- defaultهای `run-dir` و `lock-file` در orchestrator نیز canonical شدند؛ import مستقیم timer عمداً ممنوع و فقط workflow backup-gated مجاز است. تست‌های NAV/orchestrator/monitor `13/13` و dry-run با report زیر `data-service/artifacts/daily-orchestrator` موفق‌اند.
- ابزار `audit_nav_consistency.py` در checkout اصلاح شد تا تطبیق NAV را با `symbol + period_end + value + unit + source_disclosure` انجام دهد و شمارش‌های identity/value-unit/exact-source را جدا کند؛ compile و `git diff --check` موفق، و deploy Production انجام نشده است.
- نسخهٔ اصلاح‌شدهٔ همین ابزار در 2026-09-07 از مسیر `/tmp` روی DB معتبر Production اجرا شد: `promoted_total=5`، `non_irr_promotions=5`، `raw_total=287`، `raw_symbols=80`، `raw_non_per_share_units=0`، `identity_period_value_matches=5`، `identity_value_unit_matches=0` و `exact_source_matches=0`. این اجرا read-only بود و release Production تغییر نکرد.
- قرارداد query ممیزی با `test_audit_nav_consistency.py` تثبیت شد؛ تست‌های قرارداد NAV/orchestrator/monitor `13/13` موفق و `git diff --check` موفق هستند.
- queryهای تحلیلی `main.py` اصلاح شد تا `nav_per_share` فقط با `normalized_unit='IRR'` وارد valuation شود؛ واحدهای `IRR_million` یا نامعتبر حتی در صورت promotion اشتباه، ورودی تحلیلی محسوب نمی‌شوند. تست‌های تحلیل و قرارداد `55/55` موفق.
- گیت واحد در `promote_evidence.py` نیز اضافه شد؛ normalized `nav_per_share` با واحد غیر `IRR` پیش از backup/انتقال رد می‌شود. تست‌های promotion/audit/orchestrator/monitor `15/15` موفق‌اند.
- suite کامل data-service پس از گیت promotion با `141/141` تست موفق و `git diff --check` موفق تأیید شد؛ هیچ Production write یا import در این verification انجام نشد.
- verification کامل پس از این hardening: suite data-service با `139/139` تست موفق و `git diff --check` موفق؛ هیچ write یا import Production در این اجرا انجام نشد.
- runtime Production در 2026-09-07 با hostname/TLS صحیح تأیید شد: `/healthz={status:ok,auth:email_password}`، `/readyz={status:ready,auth:email_password,mail:ready}`، release فعال `/var/www/boursnegar-releases/20260905T200000Z-valuation-gate-api` و PM2 `bourse-app=online`.
- unit واقعی کاربر با repository تطبیق داده شد: batch-size=`3`، `run-dir=/home/king/Projects/boursnegar/data-service/artifacts/daily-orchestrator` و مسیرهای canonical یکسان‌اند؛ timer `active` است، آخرین اجرای service exit code صفر داشته و trigger بعدی ثبت شده است.
- اجرای دستی unit در `2026-09-07T07:14:00Z` با `ExecMainStatus=0` پایان یافت؛ report جدید، `artifact_validation.manifests=3` و `issues=[]` ثبت شد. supervisor به‌درستی همان روز را `already-ran-today` نگه داشت و recovery plan deterministic با `1515` ردیف تولید شد؛ هیچ import Production انجام نشد.

- ممیزی مستقیم NAV در Production در 2026-09-07: `valuation_inputs.nav_per_share` شامل ۵ رکورد است که همگی `REVIEW` با واحد `IRR_million` هستند؛ `VALID=0`. در raw، ۲۸۷ رکورد NAV با واحد `IRR` وجود دارد. تطبیق آن‌ها صرفاً با symbol یا مقدار مجاز نیست و تا تطبیق issuer/period/source/checksum، promotion انجام نمی‌شود.
- تطبیق دقیق‌تر همان روز با unit و source disclosure نیز انجام شد: `raw_rows=289`، `value_unit_matches=0` و `value_source_matches=0`. اختلاف تعداد raw نسبت به ممیزی قبلی ناشی از تغییر وضعیت live داده است؛ مبنای فعلی ۲۸۹ است و هیچ تطبیق قابل promotion اثبات نشده.
- تطبیق با `latest_alias + symbol + period_end_jalali` نشان داد ۷ ردیف identity/period match وجود دارد و مقدار raw با promoted برابر است، اما همه به‌علت mismatch واحد (`IRR` در raw، `IRR_million` در promoted) از unit gate رد می‌شوند؛ duplicate source برای `امین شهر` نیز دیده شد. تا تعیین قرارداد واحد و source یکتا، promotion ممنوع است.
- provenance این ۷ مورد به سندهای رسمی Excel و `detail_url`های Codal در payload وصل است؛ چهار issuer/نمونهٔ مشخص شامل `آتیمس-1516095`، `آتیه ملت-1457062`، `امتیاز-1572614` و دو disclosure برای `امین شهر` (`1573540` و اصلاحیهٔ `1573834`) هستند. برای `امین شهر` یک join کاذب duplicate بین هر دو promotion و هر دو raw source تولید می‌شود؛ قبل از هر اصلاح باید source انتخابی اصلاحیه/آخرین disclosure و checksum سند به‌صورت یکتا تعیین شود.
- بررسی filesystem Production برای این پنج action فایل Excel محلی پیدا نکرد؛ payload همچنان `excel_url`، `detail_url` و SHA-256 کامل را نگه داشته است. برای اصلاح واحد، دریافت مجدد با Chrome محلی و تطبیق SHA-256 لازم است؛ تا آن زمان همه در `REVIEW` می‌مانند.
- صفحهٔ رسمی Codal برای `آتیمس` با Chrome باز شد و جدول امضاشده قابل‌خواندن بود: سند ۹ماههٔ منتهی به `1404/11/30`، واحد «میلیون ریال»، و ردیف «خالص دارایی‌های هر واحد سرمایه‌گذاری» با مقدار `1`. این evidence معنای واحد را تأیید می‌کند، اما چون endpoint دانلود Excel توسط Chrome با `ERR_BLOCKED_BY_CLIENT` مسدود است، checksum فایل جدید استخراج نشد و promotion انجام نشد.
- چهار صفحهٔ رسمی دیگر نیز با Chrome خوانده شد: `آتیه ملت` برای `1404/08/22` مقدار هر واحد `15017`، `امتیاز` برای `1405/03/31` مقدار `12762`، و `امین شهر` برای `1405/03/31` در هر دو گزارش اصلی/اصلاحیه مقدار `14038` نشان می‌دهند. هر صفحه متن واحد «میلیون ریال» دارد؛ این مشاهدهٔ UI با مقدار raw سازگار است، اما برای تعیین قرارداد واحد normalized کافی نیست و چون دانلود checksum‌دار مسدود است، همه در `REVIEW` باقی ماندند.

- verification نهایی پس از مرور وضعیت: گیت واحد promotion به‌صورت مستقل `2/2` و suite کامل data-service با الگوی صریح `test_*.py` برابر `141/141` موفق است؛ `git diff --check` نیز موفق بود. این اجرا read-only بود و هیچ import، promotion یا تغییر Production انجام نشد.

- در بازبینی artifactهای محلی مشخص شد پنج Excel رسمی NAV قبلاً در batchهای browser/codal.ir موجود بوده‌اند و SHA-256 آن‌ها با payloadها هم‌خوان است؛ بنابراین صف curated با چهار action یکتا ساخته شد (`1516095`، `1457062`، `1572614` و اصلاحیهٔ `1573834` برای «امین شهر»). سند اصلی `1573540` به‌علت اصلاحیه کنار گذاشته شد.
- promotion curated در `2026-09-07T07:28:42Z` با backup `/var/backups/boursnegar/20260907T072842Z-evidence-before.dump` اجرا شد؛ import/replay و refresh موفق و `/readyz=ready` بود. ممیزی post به‌صورت read-only ذخیره شد. مسیر استاندارد `financial_facts` اکنون برای چهار NAV مقدار `IRR/VALID` دارد؛ پنج رکورد legacy در `valuation_inputs` همچنان `REVIEW/IRR_million` هستند و عمداً دست‌نخورده باقی مانده‌اند.
- نقص wrapper promotion پیدا و اصلاح شد: ارسال `--symbol '*'` importer استاندارد را به شاخهٔ notice-only می‌برد؛ wrapper اکنون بدون این flag اجرا می‌شود. گزارش دوم نشان داد replay استاندارد idempotent است (`inserted=0`, `validation_errors=[]`) و migration legacy هنوز نیازمند طراحی rollback و audit مستقل است.
- پس از اصلاح wrapper، regression آن اضافه شد و suite کامل data-service با `142/142` تست موفق و `git diff --check` موفق تأیید شد؛ هیچ تغییر جدیدی در Production در این verification انجام نشد.
- migration `029_reconcile_nav_valuation_inputs.sql` پس از backup در Production اجرا شد: چهار ردیف legacy با source action کامل و checksum Excel به `IRR/VALID` اصلاح شدند و `1573540` به‌عنوان superseded با وضعیت `REJECTED` باقی ماند. پس از refresh، وضعیت شمارشی `4 VALID / 0 REVIEW / 1 REJECTED` و `/readyz=ready` تأیید شد.
- ممیزی NAV با شرط source صحیح (`source_disclosure_id=source_action_id`) اصلاح شد؛ گزارش نهایی read-only برابر است با `promoted_total=5`، `non_irr_promotions=1`، `identity_period_value_matches=5`، `identity_value_unit_matches=5` و `exact_source_matches=4`. شرط قبلی که همه sourceها را به `:balance_sheet` می‌چسباند، false negative تولید می‌کرد.
- backtest پس از refresh و migration دوباره با روش `forward_valid_sessions` اجرا شد و تغییری در پوشش ایجاد نکرد: `4168` snapshot کل، افق ۲۰ جلسه `13` نمونه از حداقل `30` و گیت `INSUFFICIENT_SAMPLE`. این گیت عمداً باز مانده و هیچ بازسازی مصنوعی انجام نشده است.
- ممیزی freshness محلی در ادامهٔ همین مرحله: timer برابر `enabled/active` است، آخرین اجرای واقعی service در `2026-09-07 03:13:59 EDT` با `ExecMainStatus=0` پایان یافته، artifact validation برابر `3 manifest / issues=[]` و recovery plan برابر `1515` ردیف است؛ trigger بعدی `2026-09-08 02:31:43 EDT` ثبت شده. مسیر import همچنان عمداً backup-gated و جدا از collector زمان‌بندی‌شده است.
- resume audit در `2026-09-07T03:41:54-04:00` delta تازه‌ای در Production پیدا نکرد: backtest همچنان `4168` snapshot و افق ۲۰ جلسه `13/30` است. هر ۱۳ نمونهٔ قابل‌محاسبه از مدل‌هایی با آخرین `calculated_at=2026-08-20` می‌آیند؛ snapshotهای بعدی برای عبور از ۲۰ جلسه هنوز forward window کامل ندارند. تولید snapshot مصنوعی یا صفر/forward-fill کردن جلسات ممنوع است.
- دومین resume audit در `2026-09-07` نیز بدون delta بود: `total_model_snapshots=4168` و h20=`13/30`, فقط `normalized_pe`. هر دو فایل migration NAV از نظر `BEGIN/COMMIT` متوازن و migration اصلی فاقد `DROP TABLE` هستند؛ rollback جداگانه و backup Production موجود است.

## 2026-09-07 - تثبیت مخزن، مسیر canonical و نگهداری Production

- تغییرات انباشته با تست کامل (`142/142` داده و `75/75` وب، typecheck/build موفق) در commit `c7381705` ثبت و روی branch `agent/data-engine-v1` push شد؛ working tree پس از checkpoint تمیز بود.
- `data-service/artifacts/` و `.codex/` از Git خارج شدند و artifactها حذف نشدند. ۱۱۳ coverage cycle و ۲۰ retention report تکراری به آرشیو قابل‌بازگشت `data-service/artifacts/archive/repeated-manual-cycles-20260906/` منتقل شدند؛ آخرین cycleها در مسیر فعال باقی ماندند.
- دیتابیس canonical لوکال در همهٔ entrypointهای فعال و console برابر `data-service/artifacts/local-ingestion.sqlite3` شد. integrity آن `ok` و موجودی آن ۱۵۲۴ نماد و ۲۱۷۴ notice است. دیتابیس قدیمی `artifacts/local-ingestion.sqlite3` حفظ شد ولی دیگر default هیچ workflow فعال نیست.
- ممیزی read-only Production اندازهٔ DB را حدود `3.3 GB` نشان داد؛ `codalpy_records` حدود `2.8 GB` و دارای autovacuum و indexهای فعال است. retention یا حذف خام بدون سیاست provenance انجام نشد.
- `boursnegar-alert-worker.service` هر پنج دقیقه به‌علت نبود `dist/alert-worker.cjs` شکست می‌خورد. artifact build با SHA-256 `7576fd397470643b8190782f9b027d0b0a83a429812bb876a5d7b0d48bf2bccc` به release فعال نصب شد؛ چون `ALERT_WORKER_ENABLED=false` و `SMS_ENABLED=false` است، service اکنون با پیام `alert-worker disabled` و exit صفر پایان می‌یابد. پس از اصلاح، failed unit صفر بود.
- `VACUUM (ANALYZE)` محدود روی `daily_prices`، `financial_facts`، `codal_notice_events` و `analytical_snapshots` اجرا شد؛ آمار live به‌ترتیب `499014`، `72558`، `30543` و `8601` و dead tuple هر چهار جدول صفر شد. جدول بزرگ `codalpy_records` عمداً vacuum دستی نشد. `/readyz` و data-service health پس از maintenance سبز ماندند.
- observer Production سخت‌گیرانه شد: وجود هر unit شکست‌خوردهٔ `boursnegar-*`، نبود `dist/alert-worker.cjs` هنگام فعال‌بودن timer، یا نتیجهٔ ناموفق آخر worker اکنون observer را FAIL می‌کند. نسخهٔ قبلی پیش از نصب در `/var/backups/boursnegar/` نگه‌داری شد و اجرای واقعی نسخهٔ جدید `PASS disk=70% failed_units=0 alert_worker=ready` داد.
- Quality Gate روی pushهای `agent/**` فعال نیست و credential فعلی GitHub نیز scope لازم برای تغییر workflow ندارد؛ CI این branch باید از trigger موجود pull request اجرا شود و تغییر workflow تا تأمین مجوز مناسب انجام نشود.
- branch با ۵۲ commit جدید main بدون تعارض reconcile شد؛ PR `#53` پس از PASS رسمی web/data-service در merge commit `74d2aa3b` وارد main شد. تست non-hermetic orchestrator که به DB workstation وابسته بود اصلاح شد و CI دوم `146/146` داده و وب PASS شد.
- preflight release یک syntax error قدیمی در `export_candidate_review.py` پیدا کرد و پیش از switch متوقف شد. خطا اصلاح و compile contract همهٔ فایل‌های Python اضافه شد؛ `147/147` تست محلی و CI رسمی PR `#54` سبز و merge commit آن `9750c0ac` است.
- schema migration registry پس از اثبات postconditionهای ۰۲۷ و ۰۲۹ reconcile شد. پیش از write، backup کامل `/var/backups/boursnegar/20260907T083226Z-schema-registry-before.dump` با SHA-256 `40c8a8caa3314d90c85ab8d6d8748d5d5800f321dae3571c01943a6f4a1ea94d` و `pg_restore -l` موفق ثبت شد. دادهٔ NAV ثابت ماند: `4 VALID/IRR` و `1 REJECTED/IRR_million`.
- data-service main در release کنار دستی `20260907T0840Z-main-9750c0ac` ساخته شد؛ compile، startup روی پورت موقت، switch اتمی و health/readiness/observer همگی موفق بودند. rollback برابر release قبلی `20260831T203700Z-audited-interim-selection` حفظ شد. تحلیل واقعی `فولاد` پس از deploy نماد و lineage معتبر، پوشش `100.0` و تصمیم محافظه‌کارانهٔ `INSUFFICIENT_DATA` برگرداند؛ گیت با deploy دور زده نشد.
- warning runtime مربوط به alias بی‌اثر Pydantic برای `reportMode` با مدل‌کردن مستقیم نام عمومی camelCase رفع شد؛ regression contract اضافه و `148/148` تست محلی و CI رسمی PR `#56` سبز شد. release `20260907T0850Z-main-4a2f286e` پس از preflight بدون warning فعال شد؛ درخواست `reportMode=invalid-mode` به‌طور قطعی HTTP 400 داد و readiness/observer سبز ماند.
- نخستین اجرای timer بازار پس از deploy با exit صفر پایان یافت و شمار رکوردهای قیمت معتبر همان روز از `296589` به `296650` رسید؛ این delta واقعی timer است. اطلاعیه‌ها بدون delta در `30543` و snapshotها بدون اجرای مصنوعی اضافه در `8602` باقی ماندند.
