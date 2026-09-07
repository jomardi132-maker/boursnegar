# ماتریس تکمیل هدف بورس‌نگار

این فایل فقط وضعیت اثبات‌شده را ثبت می‌کند. `PASS` به معنی وجود شواهد کافی برای ادعای همان ردیف است؛ گیت باز به‌عنوان شکست یا نبود تاریخی داده تفسیر نمی‌شود.

| بخش | وضعیت | شواهد فعلی | معیار پایان |
|---|---|---|---|
| سامان‌دهی چت و handoff | PASS | اتاق کنترل pinned، چت‌های تکراری آرشیو، `CURRENT_STATE.md` و backlog | یک مرجع اصلی و بدون backlog متناقض |
| روند delta/report | PASS | execution card، runbook، backlog و گزارش‌های timestamped؛ suite داده `142/142` و وب `75/75` | هر اقدام delta، معیار پایان و report داشته باشد |
| freshness اطلاعیه | PARTIAL | Production: `30543` رکورد، آخرین دریافت `2026-09-07 01:06:56 UTC`، `233` رکورد در ۴۸ ساعت؛ timer local فعال، unit/defaultهای canonical، اجرای جدید با exit code صفر و recovery plan `1515` ردیفی؛ import مستقیم عمداً به workflow backup-gated واگذار شده | زنجیره‌ی زمان‌بندی‌شده‌ی local collector → manifest/checksum → workflow backup-gated import → refresh با report موفق |
| NAV صندوق‌ها | PASS | چهار رکورد curated با artifact Excel/HTML و SHA-256 رسمی در `valuation_inputs` برابر `IRR/VALID`؛ رکورد superseded اصلی `REJECTED` و بدون حذف فیزیکی نگه داشته شد؛ backup و rollback migration موجود است | حفظ provenance و جلوگیری از ورود واحد/نسخه‌ی superseded |
| ممیزی NAV | PASS | ممیزی نهایی: `5` تطبیق issuer/period/value، `5` تطبیق unit و `4` exact-source؛ رکورد پنجم به‌درستی superseded/REJECTED است؛ refresh و `/readyz=ready` سبز | حفظ گزارش و جلوگیری از join کاذب |
| backtest پنج/ده جلسه‌ای | PASS | ۲۶۵۲ و ۷۳ نمونه، هر دو `READY` با حداقل ۳۰ | حفظ گیت `VALID AND volume>0` |
| backtest بیست جلسه‌ای | OPEN | ۱۳ نمونه از حداقل ۳۰، `INSUFFICIENT_SAMPLE` | حداقل ۳۰ snapshot تاریخی واقعی؛ بازسازی ممنوع |

## قواعد توقف

- `NO_NOTICES`، صفر نتیجه، 404 یا خطای upstream absence تاریخی نیست.
- promotion فقط با manifest، SHA-256، backup، import idempotent و refresh موفق انجام می‌شود.
- مقدار، واحد، هویت یا دوره با حدس اصلاح نمی‌شود.
