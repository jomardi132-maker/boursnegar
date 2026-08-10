# گزارش نهایی استقرار بورس‌نگار

تاریخ اجرا: 2026-08-10

## وضعیت نهایی

- Production در `https://boursnegar.ir` سالم و پاسخ‌گو است.
- پردازش PM2 با نام `bourse-app` آنلاین است.
- سرویس `boursnegar-data-service.service` فعال است.
- health و readiness برنامه، PostgreSQL و FastAPI موفق‌اند.
- تحلیل عمومی فعال مانده و خروجی تحلیل دقیقاً سه سؤال بنیادی دارد.
- ورود پیامکی تا تأیید قالب کاوه‌نگار با حالت `OTP_PENDING_APPROVAL` غیرفعال است.
- هیچ پیامک واقعی، Mock gateway یا کد OTP ثابت در Production فعال نیست.

## Secretها

مقادیر زیر با مولد رمزنگاری امن سیستم و حداقل ۶۴ بایت تصادفی، مستقیماً روی سرور ذخیره شدند. مقدار آن‌ها نمایش، log یا وارد Git نشده است.

```text
AUTH_SESSION_SECRET=SET
OTP_PEPPER=SET
KAVENEGAR_API_KEY=VERIFIED
```

- فایل `/var/www/bourse-analyzer/.env` دارای permission برابر `600` است.
- backup محرمانه: `/var/www/bourse-analyzer/.env.security-backup.20260810T132749Z`
- permission فایل backup برابر `600` است.
- Secretهای موجود در اجرای بعدی دوباره تولید نمی‌شوند.

## کاوه‌نگار

- Template: `boursnegarotp`
- Template ID: `1515159`
- وضعیت نهایی بررسی‌شده: `PendingReview`
- ارسال واقعی OTP تا وضعیت `Approved` غیرفعال است.

## Backup و Migration

- backup جامع: `/var/backups/boursnegar/20260810T130231Z`
- migrationهای فعال PostgreSQL: `001_core`, `002_legacy_imports`
- ۸۱ تحلیل legacy به‌صورت idempotent وارد PostgreSQL شدند.
- ledger append-only، trigger حفاظتی و rollback آزمایشی تأیید شدند.

## تست و استقرار

- TypeScript typecheck: موفق
- Node/Vitest: ۲۱ تست موفق
- Python compile و unittest: موفق
- Production build: موفق
- npm audit: صفر آسیب‌پذیری
- smoke test سه نماد، سه سؤال، صفحه اصلی، authorization و مسیر عمومی: موفق
- rollback خودکار در اجرای آزمایشی عملاً بررسی شد.
- release فعال: `/var/www/boursnegar-releases/20260810T131100Z-e147db0`

## Commitهای اصلی

```text
e23fda9 fix: enforce three-question analysis contract
e147db0 feat: add safe pending OTP production mode
e248dee feat: redesign RTL analysis experience
0d28e5d feat: add secure PostgreSQL auth and credit core
4e5d642 chore: capture production source baseline
```

تنها اقدام عملیاتی باقی‌مانده پس از تأیید قالب، تست واقعی OTP با شماره‌ای است که مالک سامانه اعلام می‌کند.
