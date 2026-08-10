# گزارش نهایی فنی بورس‌نگار

تاریخ اجرا: 2026-08-10

## وضعیت Production

- دامنه `https://boursnegar.ir` سالم و پاسخ‌گو است.
- release فعال Node: `/var/www/boursnegar-releases/20260810T151300Z-638cd8c`
- PM2: پردازش `bourse-app` آنلاین؛ restart کنترل‌شده و `pm2 save` کامل شد.
- FastAPI: سرویس `boursnegar-data-service.service` فعال و health موفق.
- PostgreSQL: readiness موفق؛ migrationهای `001_core` تا `004_analysis_attempts` فعال؛ ۸۱ رکورد legacy در جدول قرنطینه مهاجرت داده شده‌اند.
- worker هشدار: سرویس oneshot و timer پنج‌دقیقه‌ای نصب و سالم است؛ با `ALERT_WORKER_ENABLED=false` و `SMS_ENABLED=false` هیچ ارسالی انجام نمی‌دهد.
- تحلیل عمومی فعال است. نمادهای `فولاد`، `فملی` و `شپنا` هرکدام HTTP 200 و دقیقاً سه پرسش بنیادی برگرداندند.

## قابلیت‌های تکمیل‌شده

- OTP موبایل ایران، session امن، CSRF، logout، rate limit، انقضای دو دقیقه‌ای، شمارنده تلاش و قفل موقت.
- اصلاح امنیتی مهم: تلاش‌های ناموفق OTP اکنون مستقل از نتیجه verification به‌صورت transactional پایدار می‌مانند و rollback نمی‌شوند.
- PostgreSQL برای کاربران، هویت موبایل، نشست‌ها، پلن‌ها، اشتراک، اعتبار، ledger، تاریخچه، پرداخت، referral، کمپین، هشدار، پیامک، audit و settings.
- پنج اعتبار خوش‌آمدگویی؛ کسر اعتبار فقط بعد از تحلیل موفق؛ ledger append-only و idempotent.
- پرداخت دستی با تطبیق مبلغ پلن، محدودیت اندازه/نوع و بررسی magic bytes واقعی JPG/PNG/PDF؛ تأیید/رد ادمین transactional.
- مشاهده رسید فقط برای Admin، با مسیر کنترل‌شده و `Cache-Control: private, no-store` انجام می‌شود.
- referral، پاداش، کمپین‌ها، پلن‌های کاملاً قابل تنظیم، هشدار قیمت/P/E/کدال با ساخت/ویرایش/توقف/حذف و جلوگیری از ارسال تکراری.
- کمپین به پرداخت و ledger متصل است؛ بازه زمانی، ظرفیت، استفاده یک‌باره هر کاربر و جلوگیری از تأیید تکراری در دیتابیس enforce می‌شوند.
- داشبورد responsive کاربر و مدیر برای نمای کلی، تاریخچه، پرداخت، معرفی، هشدار، آمار، جست‌وجو/نقش/وضعیت کاربران، تنظیم اعتبار و ledger، اشتراک‌ها، پلن‌ها، پرداخت‌ها، کمپین‌ها، referralها، تنظیمات، SMS و audit.
- ثبت جداگانه تلاش‌های موفق/ناموفق تحلیل و آمار ۳۰روزه ثبت‌نام/کاربر فعال، درآمد تأییدشده و مصرف اعتبار.
- Rate limit برای تمام مسیرهای Admin و پاسخ امن HTTP 400 برای JSON مخدوش.
- بارگذاری `.env` پیش از ساخت Pool PostgreSQL اصلاح شد تا restartهای آینده وابسته به محیط باقی‌مانده PM2 نباشند.
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
- backup جامع پیش از release نهایی: `/var/backups/boursnegar/20260810T150159Z-admincomplete`
- backupهای جدید شامل checksum و PostgreSQL dump هستند و با permission محدود نگهداری می‌شوند.

## آزمون‌ها

- TypeScript typecheck/lint: موفق.
- Vitest: ۳۹ تست موفق.
- Python compile و unittest: ۳ تست موفق.
- build نسخه Production، نسخه Pending و worker: موفق.
- staging PostgreSQL مستقل: چهار migration، OTP mock، کد شش‌رقمی، expiry، پنج تلاش و lockout، session، پنج اعتبار، دو مصرف هم‌زمان، ledger غیرقابل‌ویرایش، authorization واقعی HTTP، upload spoofed/valid، مشاهده امن رسید، تأیید و منع تأیید مجدد پرداخت، campaign redemption/capacity، ویرایش هشدار، آمار و فعالیت Admin: موفق (`integration-smoke: PASS`).
- Worker روی PostgreSQL آزمایشی و data service ساختگیِ محدود به تست: سقف دو ارسال در اجرا، dedup در سه اجرای متوالی و ثبت `SMS_DISABLED` موفق؛ هیچ پیامکی ارسال نشد.
- authorization مسیرهای account/admin و CSRF مسیرهای تغییردهنده: موفق.
- upload validation و تطبیق مبلغ پلن: موفق.
- QA مرورگر Production: RTL، متن فارسی، جست‌وجو با صفحه‌کلید، تحلیل واقعی، سه کارت، خطای ورودی نامعتبر، نبود console error و نبود overflow افقی: موفق.
- viewport واقعی موبایل `375×812`، تبلت `768×1024` و دسکتاپ بررسی شد؛ تحلیل موبایل/تبلت سه کارت و بدون overflow افقی بود.
- health دامنه، Node، FastAPI، PM2، PostgreSQL و worker timer: موفق.

## کاوه‌نگار و مانع بیرونی

- Template: `boursnegarotp`
- Template ID: `1515159`
- آخرین وضعیت تازه خوانده‌شده از API رسمی `verify/templatelist.json`: `Rejected`
- متن قالب: `کد ورود به بورس‌نگار: %token`
- `OTP_PENDING_APPROVAL=true`، `OTP_ENABLED=false` و `OTP_GATEWAY=disabled` باقی مانده‌اند.
- هیچ پیامک واقعی ارسال نشد و هیچ Mock یا کد ثابت در Production فعال نیست.

API علت رد را برنمی‌گرداند. مسیر رسمی پیگیری: [کنسول کاوه‌نگار](https://console.kavenegar.com/) ← «اعتبارسنجی» ← «تعریف/لیست الگوی اعتبارسنجی»؛ قالب `boursnegarotp` با شناسه `1515159` باید اصلاح یا توسط پشتیبانی تأیید شود. دسترسی خودکار به کنسول از محیط مرورگر به‌علت محدودیت شبکه ممکن نشد.

کار بیرونی باقی‌مانده: رفع رد قالب، رسیدن آن به `Approved` و اعلام شماره تست توسط مالک؛ سپس یک OTP واقعی آزمایش و در صورت موفقیت OTP فعال شود. تا آن زمان ورود و داشبورد عمداً در Production غیرفعال‌اند و تحلیل عمومی در دسترس باقی می‌ماند.

## Commitهای نهایی

```text
638cd8c fix: return safe client errors for malformed JSON
c6c61c0 fix: load database environment before pool creation
d8c7b7d test: verify alert worker rate cap and deduplication
400c856 test: seed alert worker rate and dedup checks
e79402d test: add deterministic alert worker fixture
5650970 test: make staging server readiness deterministic
c728493 feat: complete alert editing and admin operations
f0f9033 feat: expose campaign offers in account payments
0b683ed feat: complete campaign and admin payment workflows
2b13ac5 fix: persist OTP failure lockouts transactionally
fbad8f8 test: add transactional integration smoke coverage
a54bc98 feat: complete account admin and sourced analysis workflows
03b2201 feat: add safe scheduled alert worker
5b15f8a feat: add transactional platform and admin APIs
```

## تصمیم خاموش‌کردن

کامپیوتر خاموش نشد، زیرا قالب کاوه‌نگار `Rejected` شده و رفع آن به پنل/پشتیبانی کاوه‌نگار نیاز دارد. طبق دستور مالک، در وجود مانع یا نیاز به تأیید shutdown مجاز نیست. Production سالم و rollback-ready است؛ OTP و SMS خاموش‌اند و تحلیل عمومی فعال مانده است.
