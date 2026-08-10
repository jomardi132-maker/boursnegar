# گزارش نهایی فنی بورس‌نگار

تاریخ اجرا: 2026-08-10

## وضعیت Production

- دامنه `https://boursnegar.ir` سالم و پاسخ‌گو است.
- release فعال Node: `/var/www/boursnegar-releases/20260810T143600Z-0b683ed`
- PM2: پردازش `bourse-app` آنلاین، بدون restart ناپایدار.
- FastAPI: سرویس `boursnegar-data-service.service` فعال و health موفق.
- PostgreSQL: readiness موفق؛ migrationهای `001_core`، `002_legacy_imports` و `003_campaign_redemptions` فعال؛ ۸۱ رکورد legacy مهاجرت داده شده‌اند.
- worker هشدار: سرویس oneshot و timer پنج‌دقیقه‌ای نصب و سالم است؛ با `ALERT_WORKER_ENABLED=false` و `SMS_ENABLED=false` هیچ ارسالی انجام نمی‌دهد.
- تحلیل عمومی فعال است. نمادهای `فولاد`، `فملی` و `شپنا` هرکدام HTTP 200 و دقیقاً سه پرسش بنیادی برگرداندند.

## قابلیت‌های تکمیل‌شده

- OTP موبایل ایران، session امن، CSRF، logout، rate limit، انقضای دو دقیقه‌ای، شمارنده تلاش و قفل موقت.
- اصلاح امنیتی مهم: تلاش‌های ناموفق OTP اکنون مستقل از نتیجه verification به‌صورت transactional پایدار می‌مانند و rollback نمی‌شوند.
- PostgreSQL برای کاربران، هویت موبایل، نشست‌ها، پلن‌ها، اشتراک، اعتبار، ledger، تاریخچه، پرداخت، referral، کمپین، هشدار، پیامک، audit و settings.
- پنج اعتبار خوش‌آمدگویی؛ کسر اعتبار فقط بعد از تحلیل موفق؛ ledger append-only و idempotent.
- پرداخت دستی با تطبیق مبلغ پلن، محدودیت اندازه/نوع و بررسی magic bytes واقعی JPG/PNG/PDF؛ تأیید/رد ادمین transactional.
- مشاهده رسید فقط برای Admin، با مسیر کنترل‌شده و `Cache-Control: private, no-store` انجام می‌شود.
- referral، پاداش، کمپین‌ها، پلن‌های قابل تنظیم، هشدار قیمت/P/E/کدال و جلوگیری از ارسال تکراری.
- کمپین به پرداخت و ledger متصل است؛ بازه زمانی، ظرفیت، استفاده یک‌باره هر کاربر و جلوگیری از تأیید تکراری در دیتابیس enforce می‌شوند.
- داشبورد responsive کاربر و مدیر برای نمای کلی، تاریخچه، پرداخت، معرفی، هشدار، آمار، کاربران، پرداخت‌ها، کمپین‌ها، تنظیمات، SMS و audit.
- تحلیل deterministic بر پایه BrsApi و کدال؛ سؤال سوم از گزارش هم‌طول قبلی استفاده می‌کند و در نبود داده مستند صریحاً «نامشخص» می‌ماند.
- نرخ بانکی و تورم فقط وقتی استفاده می‌شوند که مقدار، منبع و تاریخ معتبر در `system_settings` ثبت شده باشد؛ هیچ عدد ساختگی یا قدیمی hard-code نشده است.

## امنیت و Secretها

```text
AUTH_SESSION_SECRET=SET
OTP_PEPPER=SET
KAVENEGAR_API_KEY=VERIFIED
ADMIN_API_KEY=SET
```

- هیچ مقدار Secret در این گزارش، terminal log، bundle یا Git ثبت نشده است.
- permission فایل `/var/www/bourse-analyzer/.env` برابر `600` است.
- backup محرمانه env: `/var/www/bourse-analyzer/.env.security-backup.20260810T132749Z` با permission برابر `600`.
- Secretهای موجود پایدارند و در deploy دوباره تولید نمی‌شوند.
- CSP، HSTS، nosniff و SAMEORIGIN روی دامنه تأیید شدند.
- `npm audit --omit=dev`: صفر آسیب‌پذیری.

## Backupها

- backup جامع اولیه: `/var/backups/boursnegar/20260810T130231Z`
- backup پیش از release قابلیت‌ها: `/var/backups/boursnegar/20260810T140006Z`
- backup پیش از اصلاح OTP: `/var/backups/boursnegar/20260810T141657Z-otpfix`
- backup پیش از migration کمپین: `/var/backups/boursnegar/20260810T143300Z-campaigns`
- backupهای جدید شامل checksum و PostgreSQL dump هستند و با permission محدود نگهداری می‌شوند.

## آزمون‌ها

- TypeScript typecheck/lint: موفق.
- Vitest: ۳۸ تست موفق.
- Python compile و unittest: ۳ تست موفق.
- build نسخه Production، نسخه Pending و worker: موفق.
- staging PostgreSQL مستقل: سه migration، OTP mock، کد شش‌رقمی، expiry، پنج تلاش و lockout، session، پنج اعتبار، دو مصرف هم‌زمان، ledger غیرقابل‌ویرایش، authorization واقعی HTTP، upload spoofed/valid، مشاهده امن رسید، تأیید و منع تأیید مجدد پرداخت و campaign redemption/capacity: موفق (`integration-smoke: PASS`).
- authorization مسیرهای account/admin و CSRF مسیرهای تغییردهنده: موفق.
- upload validation و تطبیق مبلغ پلن: موفق.
- QA مرورگر Production: RTL، متن فارسی، جست‌وجو با صفحه‌کلید، تحلیل واقعی، سه کارت، خطای ورودی نامعتبر، نبود console error و نبود overflow افقی: موفق.
- viewport واقعی موبایل `375×812`، تبلت `768×1024` و دسکتاپ بررسی شد؛ تحلیل موبایل/تبلت سه کارت و بدون overflow افقی بود.
- health دامنه، Node، FastAPI، PM2، PostgreSQL و worker timer: موفق.

## کاوه‌نگار و مانع بیرونی

- Template: `boursnegarotp`
- Template ID: `1515159`
- آخرین وضعیت خوانده‌شده از API: `PendingReview`
- متن قالب: `کد ورود به بورس‌نگار: %token`
- `OTP_PENDING_APPROVAL=true`، `OTP_ENABLED=false` و `OTP_GATEWAY=disabled` باقی مانده‌اند.
- هیچ پیامک واقعی ارسال نشد و هیچ Mock یا کد ثابت در Production فعال نیست.

تنها کار وابسته به عامل بیرونی: پس از `Approved` شدن قالب و اعلام شماره تست توسط مالک، یک OTP واقعی آزمایش شود؛ سپس entry نسخه کامل فعال گردد. تا آن زمان ورود و داشبورد عمداً در Production غیرفعال‌اند و تحلیل عمومی در دسترس باقی می‌ماند.

## Commitهای نهایی

```text
f0f9033 feat: expose campaign offers in account payments
0b683ed feat: complete campaign and admin payment workflows
2b13ac5 fix: persist OTP failure lockouts transactionally
fbad8f8 test: add transactional integration smoke coverage
a54bc98 feat: complete account admin and sourced analysis workflows
03b2201 feat: add safe scheduled alert worker
5b15f8a feat: add transactional platform and admin APIs
```

## تصمیم خاموش‌کردن

کامپیوتر خاموش نشد، زیرا قالب کاوه‌نگار هنوز `PendingReview` است و طبق دستور مالک، در وجود مانع/وضعیت نیازمند تأیید نباید shutdown اجرا شود. Production در وضعیت سالم و rollback-ready باقی مانده است.
