# گزارش یکپارچهٔ ممیزی و آماده‌سازی Production بورس‌نگار

تاریخ آخرین به‌روزرسانی: ۱۴۰۵/۰۶/۰۴ — 2026-08-26

## نتیجهٔ اجرایی

بورس‌نگار در Production فعال و پایدار است. مسیر واقعی اجرا Nginx → PM2 `bourse-app` روی پورت 3000 و سرویس دادهٔ FastAPI روی پورت 8001 است. release وب فعال `20260826T103100Z-mobile-screener-fix`، وضعیت PM2 برابر `online`، گیت نهایی `PASS` و endpointهای اصلی health، ready، market overview، dashboard و صفحهٔ فولاد HTTP 200 هستند.

دادهٔ مالی ساختگی و fallbackهای legacy حذف یا غیرفعال شده‌اند. نبود داده اکنون به `INSUFFICIENT_DATA`/«داده ناکافی» تبدیل می‌شود. از ۱٬۱۲۱٬۸۲۳ رکورد Codalpy، تعداد ۱٬۰۷۳٬۶۱۵ رکورد به نماد متصل است و ۴۸٬۲۰۸ رکورد همچنان بدون نگاشت قطعی باقی مانده‌اند.

## ۱) چت‌ها و تصمیم‌های پروژه

چت‌های مرتبط بر اساس متن پیام‌ها و خروجی‌های واقعی بررسی شدند، نه فقط عنوان. تصمیم‌های تثبیت‌شده عبارت‌اند از:

- بورس آنالایزر/`bourse-analyzer` دیگر پروژهٔ فعال نیست و از مسیر اجرایی حذف شده است.
- دادهٔ مالی باید واقعی، دارای provenance و قابل ردگیری باشد؛ مقدار ساختگی یا fallback عددی مجاز نیست.
- Codalpy و Rahavard مکمل‌اند و پوشش آن‌ها نباید بیشتر از شواهد واقعی اعلام شود.
- نبود داده باید صریح اعلام شود و نباید به تصمیم خرید/فروش قطعی تبدیل شود.
- UI باید در وضعیت‌های BUY، HOLD، SELL و `INSUFFICIENT_DATA` خوانا باشد.
- moderation و automation کامنت‌ها باید idempotent و approval-gated باشد.

ادعاهای قدیمی چت‌ها دربارهٔ «تکمیل همهٔ نمادها» با coverage فعلی جایگزین شدند.

## ۲) وضعیت پوشهٔ لوکال

- checkout فعلی روی شاخه‌های `main` و `agent/data-engine-v1` همسان است.
- تعداد فایل‌های tracked فعلی: ۲۰۴.
- تست‌های فرانت‌اند: ۸ فایل و ۶۱ تست موفق.
- تست‌های Python با `unittest`: ۵۷ تست موفق.
- typecheck و production build موفق.
- artifactهای اصلی Codal حفظ شدند؛ فقط profileهای موقت Chrome، cacheها، لاگ‌های fallback و خروجی‌های reprocess تکراری حذف شدند.
- کد ingestion محلی اکنون `symbol` را همراه رکورد Codalpy ذخیره می‌کند.
- mirror محلی `artifacts/local-ingestion.sqlite3` از artifactهای v16/v17/v18 به‌صورت idempotent بازسازی شد: ۱۵۲۴ نماد، ۱۵۴۷۳ اطلاعیه، ۱۹۹۳۱ fact، ۱۴۴۴۵ رویداد و ۳۸۷۸ run ثبت شده است؛ state فعلی ۲۹۷ نماد complete و ۱۲۲۷ نماد incomplete دارد.
- رابط نظارتی موجود در `data-service/scripts/ingestion_console.py` به همین SQLite متصل است و وضعیت نماد/صنعت، خطا، dry-run و import کنترل‌شده را نمایش می‌دهد.
- مسیر واقعی local→Production با pilot `dekosar-normalized` اثبات شد: manifest دارای checksum معتبر، ۸ رکورد به‌صورت کنترل‌شده برای `دکوثر` منتقل و import شد، اجرای تکراری fact جدیدی تولید نکرد و پس از آن `REMOTE_FINAL_GATE=PASS` باقی ماند.
- batch معتبر v18 شمارهٔ ۰۰۴۰ نیز با checksum کامل منتقل شد: ۶ فایل، ۷۲۵۸ رکورد Codalpy و ۳۰۰ fact استاندارد، بدون validation error؛ پس از import گیت نهایی همچنان `PASS` بود.
- batch معتبر v18 شمارهٔ ۰۰۱۴ نیز منتقل شد: ۶ فایل، ۱۹۶۷ رکورد Codalpy و ۱۴۴ fact استاندارد، بدون validation error؛ پس از import `REMOTE_FINAL_GATE=PASS` باقی ماند.
- سه batch معتبر دیگر v18 (`۰۰۰۴`، `۰۰۲۶` و `۰۰۳۰`) نیز منتقل شدند: مجموعاً ۱٬۷۵۷ رکورد Codalpy و ۳۰۶ fact استاندارد، بدون validation error؛ پس از هر سه import گیت نهایی `PASS` بود.

## ۳) وضعیت سرور و Production

- release وب فعال: `20260826T103100Z-mobile-screener-fix`
- release دادهٔ فعال: `20260825T173000Z-all-industry-models`
- PM2: `online`
- FastAPI health: `200 / {"status":"ok"}`
- Web ready: `200 / {"status":"ready"}`
- envهای فعال: `root:root` با mode `600`
- موجودی فعلی: ۱۰۷ فایل غیر build وب، ۶۱ فایل غیرمحیطی داده، ۱۹ release وب، ۱۶ release داده و ۵۶ backup.
- دو release ناقص انتشارهای ناموفق حذف شدند؛ release فعال و backupهای rollback حفظ شدند.
- symlink عملیاتی با release واقعی PM2 همگام شده و symlink قدیمی `bourse-analyzer` حذف شده است.

## ۴) وضعیت GitHub

- شاخه‌های `main` و `agent/data-engine-v1` روی commit مشترک فعلی هستند.
- درخت GitHub و checkout محلی همسان و بدون secret واقعی شناخته‌شده‌اند.
- فایل‌های `.env` در ignore هستند؛ موارد secret-like باقی‌مانده false positive یا سابقهٔ تاریخی‌اند.
- branch protection و release manifest رسمی هنوز برای فرایند سازمانی پیشنهاد می‌شوند.
- secret scan روی کل محتوای tracked همان commit با `gitleaks detect --no-git` انجام شد و `no leaks found` گزارش کرد.

## ۵) اصلاحات انجام‌شده

- حذف نمایش valuation جعلی هنگام کمبود داده.
- حذف fallbackهای سود فصلی، peer، رویداد شرکتی و تحلیل سفارشی.
- حذف آمار جعلی پنل مدیریت و مقادیر پیش‌فرض SMS.
- اصلاح خوانایی جدول اسکرینر موبایل در RTL؛ live در viewportهای 390×844 و 1440×900 بررسی شد.
- حذف مسیرها و اسکریپت‌های منسوخ `bourse-analyzer`.
- اصلاح permission فایل دادهٔ Production از وضعیت ناامن به `root:root 600`.
- backfill محدود و provenance-safe برای ۹٬۷۷۸ رکورد به نمادهای `شبندر` و `دکوثر`؛ backup در `/var/backups/boursnegar/20260826T104500Z-codal-symbol-reconcile`.

## ۶) موارد باز و تصمیم لازم

۴۸٬۲۰۸ رکورد بدون نماد در payload خود هیچ `symbol`، `ins_code`، `company_id`، `national_id` یا نام شرکت ندارند و در منابع فعلی نیز نگاشت قطعی ندارند. اصلاح آن‌ها فقط پس از فراهم‌شدن artifact منبع یا فهرست رسمی قابل انجام است؛ انتساب حدسی ممنوع است.

workflow کاملاً احراز هویت‌شدهٔ ورود/بازیابی رمز/مدیریت کامنت با حساب کنترل‌شدهٔ واقعی هنوز به‌صورت end-to-end اثبات نشده است؛ مسیر عمومی `/login` سالم است و `/api/auth/me` بدون نشست HTTP 401 صحیح می‌دهد.

## جمع‌بندی نهایی

سایت از نظر کد، تست، مسیر runtime، امنیت env، UI عمومی و استقرار Production در وضعیت عملیاتی قرار دارد. ادعای «پوشش کامل داده» هنوز مجاز نیست؛ معیار تکمیل داده، provenance قطعی برای رکوردهای باقی‌مانده و آزمون authenticated end-to-end است، نه صرفاً سبز بودن build یا health check.
