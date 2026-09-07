# بورس‌نگار — صف کارهای کنترل‌شده

این فایل فهرست کوتاه کارهای باز است. جزئیات اجرایی در `BOURSNEGAR_EXECUTION_CARD.md` و شواهد در `CURRENT_STATE.md` نگهداری می‌شود.

## فعال

- [x] collector محلی Codal فعال، canonical و idempotent است؛ اجرای واقعی محدود با Chrome و manifest validation موفق بوده است.
- [ ] promotion روزانهٔ local-to-production عمداً خودکار نیست: فقط وقتی manifest غیرخالی و تازه وجود دارد باید workflow مستقل manifest/checksum/backup/import/replay/refresh اجرا شود. آخرین normalized artifact صفر بایت بود و مجوز import نداد.
- [x] مسیرهای پیش‌فرض monitor با artifact registry canonical هم‌راستا شد و dry-run default معتبر است.
- [x] defaultهای orchestrator و unit systemd نیز با همان artifact root canonical هم‌راستا شدند؛ dry-run و تست‌های مسیر موفق‌اند.
- [x] صف NAV curated شد: چهار سند یکتا با تطبیق issuer/period/source/unit و checksum رسمی؛ برای «امین شهر» اصلاحیهٔ `1573834` جایگزین `1573540` شد.
- [x] تطبیق raw NAV با جدول legacy انجام شد؛ چهار رکورد valid و رکورد superseded اصلی `REJECTED` است و backup/rollback migration نگهداری شده.
- [x] گیت واحد NAV با artifactهای موجود حل شد؛ چهار `nav_per_share` در مسیر استاندارد Production با `IRR/VALID` ثبت و با replay `inserted=0` تثبیت شدند.
- [x] پنج Excel رسمی در artifactهای محلی موجود و SHA-256 آن‌ها در manifest ثبت است؛ خطای `ERR_BLOCKED_BY_CLIENT` فقط برای دریافت مجدد endpoint فعلی باقی است، نه برای provenance این batch.
- [x] صف NAV-only بسته شد: از ۴۱۹ صندوق فعال، هر ۸۰ صندوق دارای NAV معتبر، units معتبرِ هم‌دوره نیز دارند؛ پنج رکورد صریح units از Excelهای رسمی موجود با checksum، backup و replay صفر promote شدند.
- [ ] ۳۳۹ صندوق فعال بدون NAV معتبر فقط پس از ورود evidence رسمی تازه و تطبیق یکتای issuer/period/source/unit بررسی شوند؛ شمار REVIEW کلی یا محاسبه از روی خالص دارایی مجوز promotion نیست.
- [x] اولویت evidence اولیه ۱۲ صندوق با Chrome بررسی شد؛ هر ۱۲ مورد `NO_NOTICES` و بدون evidence قابل promotion بودند و artifact/checkpoint آن‌ها حفظ شد.
- [ ] تکمیل تاریخچهٔ analytical snapshot برای ارزیابی ۲۰ جلسه‌ای؛ طبق تصمیم کاربر فعلاً بازار و timerهای روزانه deferred هستند و بازسازی تاریخی با دادهٔ امروز ممنوع است.

## گیت‌های باز

- [ ] endpoint مستقیم Excel در دریافت مجدد با `ERR_BLOCKED_BY_CLIENT` مواجه می‌شود؛ artifactهای قبلیِ browser/codal.ir و checksum آن‌ها معتبر و نگهداری شده‌اند.
- [ ] FCFE/DCF تا وجود همهٔ مؤلفه‌ها و نرخ‌های هم‌دوره و مستند، `INSUFFICIENT_DATA` بماند. baseline فعلی: از ۱۵۲۴ نماد، OCF=`567`، CapEx=`8` و net borrowing=`8`؛ هشت نماد این سه گیت را هم‌دوره PASS کرده‌اند اما cost of equity و terminal growth کل Production هر دو `0` هستند، پس FCFE-ready همچنان صفر است. ادامهٔ recovery فقط با join دقیق به دورهٔ `rn=1` Production و action تازه مجاز است.

## انجام‌شده و خارج از صف

- [x] سلامت release، سرویس‌ها و تست‌های ثبت‌شده در آخرین audit.
- [x] policyهای مدل صنعت و quarantine واحد ناسازگار NAV با backup و rollback.
- [x] حذف/اصلاح صف‌های تکراری و نگهداری artifact، checkpoint و provenance.
- [x] loader ورودی‌های intrinsic به endpoint وصل شد: فقط `VALID`، همان هویت دوره، واحد canonical، provenance کامل و یک منبع بدون تعارض پذیرفته می‌شود؛ lineage در snapshot قابل ممیزی است.

## قانون نگهداری

هر کار جدید باید یک delta واقعی، معیار پایان و report زمان‌دار داشته باشد. بدون تغییر upstream یا evidence، audit، batch، backup و import تکرار نمی‌شود.
