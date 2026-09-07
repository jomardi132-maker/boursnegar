# Boursnegar — دستورالعمل اجرایی کوتاه

## قبل از هر اقدام

1. فقط این فایل، سپس آخرین `CURRENT_STATE.md` entry و آخرین report را بخوان؛ تاریخچه را دوباره‌خوانی نکن.
2. منبع حقیقت: artifact/report زمان‌دار و Production runtime؛ ادعای موفقیت با HTTP 200، build یا test تنها مجاز نیست.
3. هر اقدام باید یک delta مشخص داشته باشد. اگر upstream یا شواهد تغییر نکرده، متوقف شو.

## ingestion محلی

1. منبع نماد فقط `data-service/artifacts/local-ingestion.sqlite3` است؛ Production منبع انتخاب نماد نیست.
2. فقط batch محدود و browser/local اجرا کن؛ Codal مستقیم از Production ممنوع.
3. پاسخ معتبر یعنی artifact واقعی + `manifest.json` + SHA-256؛ `non_json_response`، captcha، child-entity و zero-result را absence تاریخی ندان.
4. خطای تکراری upstream را با backoff/exclusion نگه دار؛ batch مشابه را دوباره اجرا نکن.

## promotion به Production

1. اگر manifest یا checksum ناقص است: `BLOCKED` و بدون import.
2. قبل از هر write: backup قابل‌بازگشت بگیر و مسیر/SHA-256 را در report ثبت کن.
3. import را دوبار اجرا کن؛ replay باید `inserted=0` باشد.
4. بعد از import، snapshot refresh و `/healthz` و `/readyz` را بررسی کن؛ شکست هرکدام یعنی موفقیت اعلام نشود.

## audit و زمان‌بندی

1. coverage audit، promotion audit و retention را فقط با تغییر واقعی یا موعد schedule اجرا کن؛ برای گزارش تکراری اجرا نکن.
2. سه timer کاربر: `local-codal-monitor`، `coverage-audit`، `backup-retention`; وضعیت و آخرین report را کنترل کن.
3. health/readiness، freshness اطلاعیه، analytical readiness، browser render و authenticated E2E گیت‌های جدا هستند.

## قواعد عدم جعل و توقف

- مقدار، هویت، alias، coverage یا recommendation حدس نزن.
- `INSUFFICIENT_DATA`، `REVIEW`، `DATA_REVIEW`، `UNIT_UNKNOWN` و خطاهای واقعی را حفظ کن.
- روز تعطیل را session معاملاتی ندان؛ zero-volume را از تحلیل حذف کن ولی raw evidence را نگه دار.
- در نبود Chrome/session معتبر یا پاسخ upstream معتبر، فقط checkpoint تشخیصی بساز و متوقف شو.

## وضعیت مبنا

- Production باید با health=`ok` و ready=`ready` تأیید شود.
- آخرین مبنای ثبت‌شده: ۱۵۲۴ نماد فعال؛ ۷۲۱ `CORE_READY`، ۴۱۹ `FUND_MODEL_REQUIRED`، ۳۸۴ `MISSING_COMPARABLE_PERIODS`.
- آخرین مسیرهای کاری: `data-service/scripts/`، `data-service/artifacts/`، و گزارش‌های زمان‌دار؛ قبل از هر claim آن‌ها را تازه‌خوانی کن.
