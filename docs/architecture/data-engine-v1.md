# معماری Data Engine v1 بورس‌نگار

## تصمیم معماری

موتور تحلیل deterministic و مستقل از LLM است. مسیر اصلی:

`source adapter → disclosure discovery → immutable raw document → versioned parser → normalized facts → quality/lineage → analytical snapshot → policy/valuation → recommendation → API v2`

هیچ خطای upstream به mock، preset یا عدد پیش‌فرض تبدیل نمی‌شود. خروجی فاقد coverage/confidence کافی همیشه `INSUFFICIENT_DATA` است.

## مرز داده

- داده تحلیلی با کلید ناشر/ابزار و lineage نگهداری می‌شود.
- داده حساب، session، subscription، ledger و payment در جداول موجود باقی می‌ماند و migration تحلیلی آن‌ها را overwrite نمی‌کند.
- Raw document immutable است. نسخه جدید یا اصلاحیه رکورد جدید می‌سازد.
- تاریخ اصلی UTC است؛ تاریخ میلادی و شمسی مرجع نیز جدا ذخیره می‌شوند.
- PostgreSQL استاندارد مبناست. TimescaleDB در Production نصب نیست؛ migration به extension وابسته نمی‌شود.

## هویت و نسخه

- `issuers` هویت شرکت را نگه می‌دارد.
- `instruments` ابزار و ISIN/شناسه بازار را نگه می‌دارد.
- `symbol_aliases` تغییر نماد را بدون تکثیر issuer ثبت می‌کند.
- `disclosures` هویت اطلاعیه و `disclosure_versions` نسخه/اصلاحیه را جدا می‌کند.
- `parser_versions`, `recommendation_policies`, `industry_model_policies` همه محاسبات را reproducible می‌کنند.

## ingestion state machine

وضعیت‌ها: `DISCOVERED → RAW_VERIFIED → PARSED → NORMALIZED → VALIDATED → SNAPSHOT_READY`؛ وضعیت‌های خطا `RETRYABLE_FAILED`, `DEAD_LETTER`, `BLOCKED_SOURCE` هستند.

`ingestion_runs` metrics تجمیعی و watermark دارد. `ingestion_checkpoints` با `(source, pipeline, partition_key)` یکتا است. retry محدود، exponential backoff، circuit breaker و overlap window برای اصلاحیه‌ها الزامی است.

## Data quality و lineage

هر fact نرمال‌شده می‌تواند چند `source_lineage` داشته باشد. lineage شامل سند خام، نسخه disclosure، parser، locator ردیف/ستون، formula و input references است. issueهای balance mismatch، unit ambiguity، period mismatch، contradictory revision و stale source در `data_quality_issues` ثبت می‌شوند و confidence را کاهش می‌دهند.

## Snapshot و API

API ابتدا آخرین `analytical_snapshots` معتبر را برمی‌گرداند. اگر stale باشد، همان snapshot با `stale=true` و `refresh_state=QUEUED` پاسخ داده می‌شود. نبود snapshot معتبر نتیجه `INSUFFICIENT_DATA` یا خطای شفاف است.

API v1 حفظ می‌شود. API v2 additive است و response شامل decision، valuation، dimensions، سه سؤال، quality، coverage، confidence، timestamps، model/policy versions و lineage references است.

## امنیت و quota

- OTP/SMS در مسیر Product حذف و email/password تنها روش ورود است.
- password reset token فقط به‌صورت hash و تک‌مصرف ذخیره می‌شود.
- کاربر جدید دقیقاً یک ledger grant با idempotency key ثابت و ۵ اعتبار می‌گیرد.
- کسر اعتبار فقط در transaction ایجاد snapshot معتبر/analysis usage و فقط برای decision غیر `INSUFFICIENT_DATA` انجام می‌شود.
- `Idempotency-Key` روی کل analysis request یکتا است و replay همان نتیجه را برمی‌گرداند.
- Admin فقط با RBAC سروری و bootstrap CLI محدود ایجاد/ارتقا می‌یابد.

## rollout و rollback

Migration 006 فقط additive است و transaction دارد. rollback پیش از ورود داده جدید، جداول v1 را به ترتیب dependency حذف می‌کند؛ در Production پس از ingestion، rollback به معنی توقف writer و حفظ/export داده جدید است، نه حذف خودکار. deployment release-directory جدید دارد و env فقط symlink امن است.

## معیار توقف

اگر منبع رسمی/قراردادی، نرخ اقتصادی معتبر، مدل صنعت، period matching یا lineage کافی نباشد، موتور عدد یا تصمیم تولید نمی‌کند.
