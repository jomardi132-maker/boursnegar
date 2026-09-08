# ماتریس تکمیل هدف بورس‌نگار

این فایل فقط وضعیت اثبات‌شده را ثبت می‌کند. `PASS` به معنی وجود شواهد کافی برای ادعای همان ردیف است؛ گیت باز به‌عنوان شکست یا نبود تاریخی داده تفسیر نمی‌شود.

| بخش | وضعیت | شواهد فعلی | معیار پایان |
|---|---|---|---|
| سامان‌دهی چت و handoff | PASS | اتاق کنترل pinned، چت‌های تکراری آرشیو، `CURRENT_STATE.md` و backlog | یک مرجع اصلی و بدون backlog متناقض |
| مرکز کنترل Python | PASS | GUI واقعی RTL با سه حالت plan/local/full؛ اجرای واقعی «فجوش» از Local تا backup/import/replay/refresh/health/retention موفق و report ثبت شد | حفظ مسیر canonical و گیت‌های report؛ اجرای موازی یا bypass ممنوع |
| روند delta/report | PASS | execution card، runbook، backlog و گزارش‌های timestamped؛ suite داده `149/149` و وب `75/75`؛ timerهای zero-delta بازنشسته شدند | هر اقدام delta، معیار پایان و report داشته باشد |
| freshness اطلاعیه | PARTIAL | Production: `30543` رکورد، آخرین دریافت `2026-09-07 01:06:56 UTC`، `233` رکورد در ۴۸ ساعت؛ collector local فعال و canonical است؛ آخرین normalized artifact صفر بایت بود و import نشد | نخستین manifest تازه و غیرخالی از collector → checksum → backup-gated import → replay صفر → refresh با report موفق |
| NAV صندوق‌ها | PASS | از ۴۱۹ صندوق فعال، هر ۸۰ صندوق دارای NAV معتبر، units معتبر هم‌دوره نیز دارد؛ رکورد superseded اصلی `REJECTED` و بدون حذف فیزیکی نگه داشته شد | حفظ provenance و جلوگیری از ورود واحد/نسخه‌ی superseded |
| ممیزی NAV | PASS | ممیزی نهایی: `5` تطبیق issuer/period/value، `5` تطبیق unit و `4` exact-source؛ رکورد پنجم به‌درستی superseded/REJECTED است؛ refresh و `/readyz=ready` سبز | حفظ گزارش و جلوگیری از join کاذب |
| backtest پنج/ده جلسه‌ای | PASS | ۲۶۵۲ و ۷۳ نمونه، هر دو `READY` با حداقل ۳۰ | حفظ گیت `VALID AND volume>0` |
| backtest بیست جلسه‌ای | OPEN | ۱۳ نمونه از حداقل ۳۰، `INSUFFICIENT_SAMPLE` | حداقل ۳۰ snapshot تاریخی واقعی؛ بازسازی ممنوع |
| FCFE/DCF | OPEN | ۱۲ نماد دارای OCF/CapEx/net borrowing هم‌دوره؛ نرخ‌های معتبر cost of equity و terminal growth در Production صفر و FCFE-ready صفر است | نرخ‌های issuer-period با provenance کامل و بدون inference، سپس ممیزی نه‌گیتی PASS |

## قواعد توقف

- `NO_NOTICES`، صفر نتیجه، 404 یا خطای upstream absence تاریخی نیست.
- promotion فقط با manifest، SHA-256، backup، import idempotent و refresh موفق انجام می‌شود.
- مقدار، واحد، هویت یا دوره با حدس اصلاح نمی‌شود.
