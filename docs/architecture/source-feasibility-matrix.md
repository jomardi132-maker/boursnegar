# ماتریس امکان‌سنجی منابع داده — Data Engine v1

تاریخ بررسی: ۱۴۰۵/۰۵/۲۲ (2026-08-13 UTC)

این سند نتیجه بررسی محدود و غیرتهاجمی است. دسترسی فنی به یک endpoint به معنی مجوز استفاده انبوه یا تضمین پایداری نیست. هر منبع پشت adapter مستقل قرار می‌گیرد و شکست آن snapshot معتبر قبلی را حذف نمی‌کند.

| منبع | وضعیت/رسمیت | داده و پوشش | pagination / revision | احراز هویت و هزینه | پایداری و ریسک | سیاست v1 |
|---|---|---|---|---|---|---|
| Codal public search (`search.codal.ir/api/search/v2/q`) | دامنه رسمی کدال، API عمومی ولی مستندات قراردادی عمومی پیدا نشد | metadata اطلاعیه، لینک HTML/PDF/Excel/XBRL، ناشر، نماد، تاریخ و `TracingNo`؛ پوشش تاریخی در probe وجود داشت | page-based؛ probe «فولاد» صفحه اول ۲۰ رکورد و ۴۶ صفحه اعلام کرد. اصلاحیه از عنوان/کدنامه/پیوند سند و نسخه محتوا استخراج می‌شود | بدون auth در probe؛ هزینه اعلام‌شده یافت نشد | ریسک تغییر schema و rate policy بالا چون endpoint مستندنشده است | adapter آزمایشی با rate limit، backoff، checkpoint و overlap window؛ وابستگی دائمی فقط پس از تأیید شرایط استفاده. `TracingNo` شناسه discovery است، checksum سند شناسه نسخه محتوا |
| Codal document hosts | رسمی و وابسته به کدال | PDF/HTML/Excel/XBRL خام | URL هر اطلاعیه؛ revision با disclosure version جدا | بدون auth در نمونه | MIME/URL و قالب فایل متغیر | Raw-first، checksum قبل از parse، عدم overwrite، parser versioned و dead-letter |
| My Codal | سرویس رسمی کاربری؛ برای داده عمومی ingestion طراحی نشده | خدمات شخصی‌سازی‌شده/کاربری | نامشخص | احتمالاً login | در بررسی TLS chain قابل اعتماد نبود؛ bypass ممنوع | منبع ingestion نیست؛ فقط مسیر محصول رسمی برای آینده، بدون ذخیره credential کاربر |
| Sedra رایان بورس | مسیر تجاری/رسمی آینده | داده ساختاریافته مالی و بازار، جزئیات قرارداد وابسته به سرویس | باید در قرارداد/SLA مشخص شود | احتمال auth و هزینه | ریسک فنی کمتر ولی وابسته به قرارداد | `SedraAdapter` interface رزرو می‌شود؛ خرید یا اتصال Production بدون تصمیم مالک ممنوع |
| TSETMC / CDN | مرجع رسمی بازار | قیمت، معاملات، شناسه ابزار و وضعیت نماد | endpointها عمومی ولی قرارداد API عمومی پایدار احراز نشد | بدون auth برای صفحات عمومی | امکان محدودیت IP و تغییر endpoint | adapter مستقل؛ شناسه ابزار/ISIN محور، نه متن نماد؛ در شکست upstream داده قبلی stale می‌شود |
| BrsApi (منبع فعلی قیمت) | واسط ثالث، نه مرجع رسمی | snapshot کل نمادها، قیمت و مشخصات تابلو | پاسخ bulk؛ rate limit ادعاشده در کد فعلی ۳۰۰ درخواست/۵ دقیقه | API key؛ شرایط/هزینه وابسته به provider | single-provider risk و payload بزرگ | فقط fallback موقت پشت `MarketDataAdapter`؛ Secret در env، cache و circuit breaker؛ جایگزینی آینده با منبع رسمی/قراردادی |
| بانک مرکزی (`cbi.ir`) | رسمی | نرخ‌های سود، ارز، سری‌های زمانی و آمارهای پولی | publication/revision در صفحات و انتشارات؛ API قراردادی عمومی احراز نشد | عمومی | قالب انتشار ممکن است تغییر کند | dataset seed رسمی با provenance و سپس adapter؛ هیچ نرخ hardcode نمی‌شود. هر observation دارای publication/effective date است |
| مرکز آمار ایران (`amar.org.ir`) | رسمی | CPI و تورم و سری‌های آماری | revision/base-year باید از انتشار ثبت شود | عمومی | TLS chain در probe معتبر نبود؛ bypass ممنوع | تا رفع TLS/دریافت dataset رسمی، adapter BLOCKED و تحلیل وابسته `INSUFFICIENT_DATA` است |
| fallbackهای legacy | غیرقابل اتکا | preset/mock/simulated values | ندارد | ندارد | ریسک تصمیم ساختگی | از مسیر Production حذف می‌شوند. تنها fallback مجاز snapshot معتبر قبلی با علامت stale و provenance است |

## Probe ثبت‌شده

- Codal public search: HTTP 200؛ کلیدهای سطح بالا `Letters`, `Page`, `Total`, `IsAttacker`؛ ۲۰ رکورد در صفحه اول «فولاد»؛ تعداد صفحات اعلام‌شده ۴۶.
- دامنه‌های Codal، TSETMC/CDN، CBI، Rayan Bourse و Sedra پاسخ HTTP موفق داشتند.
- My Codal و مرکز آمار در محیط بررسی زنجیره TLS قابل اعتماد ارائه نکردند؛ `verify=False` استفاده نشد.

## قرارداد adapter

هر adapter باید `discover`, `fetch`, `health`, `checkpoint` و metadata زیر را برگرداند: `source`, `source_reference`, `retrieved_at_utc`, `published_at`, `effective_at`, `content_type`, `checksum`, `revision_hint`, `stable_ids`, و `quality_status`.

Backfill کل بازار تا قبولی pagination، deduplication، resume، revision linking، checksum و rate-limit روی ۱۲ نماد مجاز نیست.
