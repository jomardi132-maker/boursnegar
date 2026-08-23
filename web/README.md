# بورس‌نگار

وب‌اپلیکیشن تحلیل بنیادی سهام بورس تهران؛ با داده‌ی واقعی بازار، تاریخچه‌ی قیمت، اطلاعیه‌های کدال و خروجی‌های تحلیلی قابل ردیابی.

## اجرای محلی

پیش‌نیازها: Node.js 22+، PostgreSQL و سرویس Python داده.

```bash
cp .env.example .env.local
npm ci
npm run dev:full
```

`PYTHON_API_BASE` باید به سرویس FastAPI داده اشاره کند. اطلاعات اتصال PostgreSQL و secretها فقط در محیط اجرا قرار می‌گیرند و نباید commit شوند.

## کنترل کیفیت

```bash
npm run typecheck
npm run test -- --run
npm run build
```

تست‌های Python از ریشه‌ی `data-service` اجرا می‌شوند:

```bash
python -m unittest discover -s tests -v
```

جزئیات معماری، قرارداد منبع داده و مسیرهای ingestion در [ARCHITECTURE.md](./ARCHITECTURE.md) ثبت شده است. workflow گیت‌هاب نیز در هر push و pull request، تست وب، build و تست سرویس داده را اجرا می‌کند.

در Production، Nginx/HTTPS در لایه‌ی ورودی، PM2 برای وب و systemd برای FastAPI داده استفاده می‌شود. قبل از انتشار، health endpointها، interpreter فعال، PostgreSQL، assetهای `dist` و release قابل rollback باید بررسی شوند.
