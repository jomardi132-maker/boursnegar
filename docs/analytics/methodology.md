# روش‌شناسی تحلیل deterministic بورس‌نگار

نسخه اولیه policy: `recommendation-v1.0.0`
نسخه engine: `fundamental-engine-v1.0.0`

## مفاهیم مستقل

- `health_score`: کیفیت بنیادی بر اساس ابعاد قابل محاسبه، ۰ تا ۱۰۰.
- `data_coverage`: نسبت ورودی‌های ضروری معتبر و تازه، ۰ تا ۱۰۰؛ missing صفر محسوب نمی‌شود.
- `confidence`: اطمینان به provenance، audit status، freshness، reconciliation و نبود تناقض، ۰ تا ۱۰۰.

حداقل coverage و confidence در policy versioned ذخیره می‌شود. زیر هر کدام decision برابر `INSUFFICIENT_DATA` است.

## سه سؤال هویتی

1. `earnings_yield = TTM_EPS / current_price × 100`؛ در صورت P/E مثبت و معتبر `100 / P_E`. نرخ سپرده باید observation رسمی با effective date منطبق باشد.
2. `cash_to_profit_ratio = operating_cash_flow / net_profit × 100`. آستانه پایه ۸۰٪ policy است؛ سود/OCF منفی مسیر تحلیلی جدا دارد.
3. `real_growth = nominal_growth - matched_inflation_rate`. فقط دوره هم‌طول مشابه سال قبل و تورم متناظر مجاز است.

## تصمیم

تصمیم تابع health، valuation، coverage، confidence، freshness و critical risks است؛ health به‌تنهایی تصمیم نیست. شرکت قوی اما گران می‌تواند HOLD/SELL و شرکت ضعیف با multiple پایین نمی‌تواند صرفاً BUY شود.

## valuation و صنعت

- فلزی/معدنی، پالایشی، پتروشیمی: DCF/EV-EBITDA فقط با cash flow و مفروضات صنعتی معتبر.
- بانک: policy سرمایه/کیفیت دارایی و مدل بانکی؛ P/E عمومی کافی نیست.
- بیمه: policy ذخایر/توانگری و مدل بیمه؛ مدل عمومی ممنوع.
- هلدینگ/سرمایه‌گذاری: NAV با ارزش دارایی‌های قابل اتکا.
- خدماتی: DCF یا relative multiple با peer set معتبر.

هر model سه سناریو، margin of safety، assumptions و version دارد. تا آماده نبودن adapter/policy صنعت، نتیجه `INSUFFICIENT_DATA` است.

## محدوده‌ها

`fair_value_low/base/high` از scenario valuation می‌آید. buy/hold/sell zones policy-based و versioned هستند و با حمایت/مقاومت تکنیکال مخلوط نمی‌شوند.

## توضیح و lineage

متن فارسی فقط template داخلی روی facts محاسبه‌شده است. مسیر هر ادعا:

`Decision → reason/risk → metric → formula → inputs → period/report flags → line item → disclosure version/raw checksum`

این سامانه تحلیل عمومی است، نه توصیه شخصی یا تضمین سود.
