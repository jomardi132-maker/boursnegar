# معماری پیشنهادی بورس‌نگار

```text
web/src/
├── app/                       # در مهاجرت مرحله‌ای به Next.js: routeها و layoutها
├── components/
│   ├── FundamentalDashboard.tsx
│   ├── MarketExplorer.tsx
│   └── report/                # کارت‌های تحلیل، ارزش‌گذاری و شواهد
├── data/                      # adapterهای داده و schemaهای خروجی
├── lib/
│   ├── api.ts                 # کلاینت امن سمت سرور؛ بدون secret در browser
│   ├── auth.ts                # session و نقش‌های user/admin
│   └── format.ts              # قالب‌بندی فارسی و واحدها
├── services/
│   ├── market/                # BrsApi/TSETMC adapter با interface مشترک
│   ├── codal/                 # دریافت و نرمال‌سازی اطلاعیه‌ها
│   └── fundamentals/          # P/E، بدهی، EPS، ارزش ذاتی و INSUFFICIENT_DATA
├── styles/                    # tokenها و themeهای قابل تست
└── types.ts

server/
├── routes/market.ts           # API فقط سمت سرور
├── scrapers/                  # scraperهای محدود، rate-limited و قابل ثبت
├── db/                        # PostgreSQL migrations و repositoryها
└── jobs/                      # به‌روزرسانی قیمت/کدال و پاک‌سازی cache
```

قرارداد پیشنهادی adapter:

```ts
interface MarketDataSource {
  search(query: string): Promise<SymbolRecord[]>;
  prices(symbol: string, range: DateRange): Promise<PricePoint[]>;
  fundamentals(symbol: string): Promise<FundamentalSnapshot>;
}
```

کلیدها و connection string فقط در `.env.local`/secret manager می‌مانند. PostgreSQL منبع پایدار تاریخچه است؛ scraper فقط ingestion layer است و هیچ‌وقت مستقیماً از browser صدا زده نمی‌شود. برای داده کم، محاسبات deterministic؛ با رشد داده، FLAML به‌عنوان سرویس جدا و قابل خاموش‌کردن اضافه می‌شود.
