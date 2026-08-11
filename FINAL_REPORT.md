# تکمیل نهایی SMTP و بازیابی رمز — ۲۰ مرداد ۱۴۰۵

- دامنه فرستنده `mail.boursnegar.ir` و همه متغیرهای SMTP بدون افشای مقدار تأیید شدند.
- اتصال SMTP و ایمیل کنترل‌شده PASS؛ `EMAIL_ENABLED=true` و readiness برابر `mail=ready` است.
- لینک بازیابی ۳۰ دقیقه‌ای، hash‌شده و تک‌بارمصرف است؛ پاسخ موجود/ناموجود یکسان، نشست‌های قبلی revoked و audit بدون اطلاعات حساس ثبت می‌شود.
- E2E: generic response، single use، expiry، session revocation، ورود با رمز جدید، rate limit و audit همگی PASS.
- Backup: `/var/backups/boursnegar/20260811T100207Z-smtp` با permission 600.
- Release: `/var/www/boursnegar-releases/20260811T100232Z-emailauth`.
- ۴۳ تست Node، چهار تست Python، typecheck، build، dependency audit، PM2، FastAPI، PostgreSQL، دامنه و Auth routes همگی PASS.
- حساب، tokenها، نشست‌ها و فایل‌های موقت تست پاک شدند؛ ایمیل/رمز/token در log، Git یا گزارش ثبت نشد.

---

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
# گزارش نهایی به‌روزرسانی ایمیل، طراحی و داده — ۲۰ مرداد ۱۴۰۵

## نتیجه اجرایی

- Production در `https://boursnegar.ir` سالم و فعال است.
- احراز هویت اصلی از OTP کاوه‌نگار به ایمیل/رمز عبور منتقل شد: ثبت‌نام، ورود، نشست امن، CSRF و خروج واقعی فعال‌اند.
- بازیابی رمز با توکن یک‌بارمصرف hash‌شده، انقضای ۳۰ دقیقه، مصرف یک‌باره و ابطال نشست‌های قبلی پیاده‌سازی شد. رمز فعلی هرگز ایمیل یا قابل بازیابی نمی‌شود.
- ارسال واقعی لینک بازیابی هنوز فعال نیست: روی دامنه MX/SPF و روی سرور SMTP/MAIL credential وجود ندارد. endpoint پاسخ ضد-enumeration می‌دهد و readiness مقدار `mail=not_configured` را صادقانه گزارش می‌کند.
- Kavenegar/OTP غیرفعال باقی ماند: `OTP_ENABLED=false`، `SMS_ENABLED=false`، `OTP_GATEWAY=disabled`. هیچ SMS واقعی ارسال نشد.
- رابط با design system مهارت UI/UX Pro Max بازطراحی شد: تم dark editorial fintech، چیدمان نامتقارن، RTL، responsive، focus state، reduced motion و بدون overflow در عرض ۳۷۵px.
- فونت رایج قبلی با Estedad Variable خودمیزبان و دارای OFL جایگزین شد؛ dependency به Google Fonts حذف شد.
- همگام‌سازی گزارش‌های کدال ۱۴۰۴ و ۱۴۰۵ هنگام جست‌وجوی نماد پیاده‌سازی شد. برای «فولاد» اکنون ۲۳ گزارش دوره ۱۴۰۴ و ۱۷ گزارش دوره ۱۴۰۵ در PostgreSQL ثبت است.
- فرمول `2/(P/E + P/D)` به‌عنوان محدوده قیمت/سیگنال اضافه نشد، چون از نظر ابعادی قیمت تولید نمی‌کند. موتور فعلی فقط نسبت‌های واقعی، earnings yield، ROE/ROA، کیفیت نقدی و مضارب صنعت‌محور را با وضعیت نامشخص هنگام کمبود داده نمایش می‌دهد.

## امنیت و Secretها

```text
AUTH_SESSION_SECRET=SET
OTP_PEPPER=SET
PASSWORD_PEPPER=SET
KAVENEGAR_API_KEY=SET (مقدار نمایش یا ثبت نشد)
```

- `.env` و backup جدید آن permission برابر 600 دارند.
- hash رمز با scrypt و پارامتر `N=131072, r=8, p=1`، salt مستقل و pepper پایدار انجام می‌شود.
- rate limit ورود/ثبت‌نام/بازیابی، قفل ۱۵ دقیقه‌ای پس از تلاش ناموفق، cookie دارای HttpOnly/Secure/SameSite و پیام‌های ضد-enumeration فعال‌اند.
- `npm audit --omit=dev`: صفر آسیب‌پذیری.

## Backup، migration و release

- Backup محرمانه: `/var/backups/boursnegar/20260811T081207Z-emailauth`
- محتوا: پروژه Node، FastAPI، `db.json`، dump سفارشی PostgreSQL و backup `.env`؛ فایل‌ها mode 600.
- Backup `.env`: `/var/www/bourse-analyzer/.env.20260811T081537Z.bak` با mode 600.
- Migration ابتدا روی restore مستقل `boursnegar_migration_test` اجرا و تأیید شد، سپس روی Production اعمال شد.
- Migration فعال: `005_email_password_auth` شامل `email_identities` و `password_reset_tokens`.
- Release فعال: `/var/www/boursnegar-releases/20260811T081537Z-emailauth`
- rollback خودکار در اسکریپت deploy تعریف شد؛ به علت موفقیت health check اجرا نشد.

## آزمون‌ها

- TypeScript typecheck: PASS
- Node/Vitest: ۸ فایل، ۴۲ تست PASS
- Production build: PASS
- Python compile: PASS
- Python unittest: ۴ تست PASS
- Migration روی restore واقعی: PASS
- ثبت‌نام/ورود/خروج/Session/CSRF: PASS
- پاسخ امن forgot-password: PASS (ارسال SMTP به علت نبود زیرساخت انجام نشد)
- Authorization پنل Admin: PASS
- مسیرهای عمومی و plans: PASS
- تحلیل واقعی «فولاد»: دقیقاً سه سؤال PASS
- Ledger: اعتبار ۵ به ۴ فقط پس از تحلیل موفق PASS
- QA مرورگر محلی: desktop، modal، 375px، بدون overflow و بدون خطای console PASS
- دسترسی عمومی دامنه: HTTP 200، asset versioned و health `ok` PASS

## وضعیت سرویس‌ها

- PM2 `bourse-app`: online، restart count release جدید برابر صفر.
- `boursnegar-data-service.service`: active.
- `https://boursnegar.ir/healthz`: `status=ok`, `auth=email_password`.
- `https://boursnegar.ir/readyz`: `status=ready`, PostgreSQL آماده، `mail=not_configured`.

## Commitها

- `e82b1d9 feat: launch secure email auth and bold fintech UI`
- `e14a74d fix: persist Persian-dated financial history`

## مانع باقی‌مانده و تصمیم خاموش‌کردن

برای فعال‌سازی واقعی «فراموشی رمز»، یک سرویس ایمیل تراکنشی لازم است و باید `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM` تنظیم و رکوردهای DNS توصیه‌شده سرویس (SPF/DKIM و در صورت نیاز MX/DMARC) اضافه شوند. این کار بدون credential و دسترسی DNS قابل انجام امن نیست.

طبق دستور کاربر که در صورت مانع/Secret مفقود کامپیوتر خاموش نشود، دستور shutdown اجرا نشد. Production سالم است و فقط ارسال outbound ایمیل باقی مانده است.

---
