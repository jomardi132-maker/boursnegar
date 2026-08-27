# Production coverage audit - 2026-08-27

Generated from Production at `2026-08-27T05:47:03Z`, `2026-08-27T05:51:05Z`, and post-cleanup at `2026-08-27T05:55:39Z` / `2026-08-27T05:56:09Z`.

## Runtime Context

- Web runtime: PM2 `bourse-app`, release `/var/www/boursnegar-releases/20260826T103100Z-mobile-screener-fix`.
- Data runtime: `boursnegar-data-service.service`, `/var/www/boursnegar-data-current` -> `/var/www/boursnegar-data-releases/20260825T173000Z-all-industry-models`.
- Health checks passed for internal web health/ready, FastAPI `/health`, internal `/api/health`, and `nginx -t`.
- The initial audit was read-only. A subsequent guarded cleanup deactivated 9 duplicate/orphan active instrument and issuer rows after dependency and collision checks; no data rows were deleted.

## Evidence Files

Raw audit outputs are intentionally kept under ignored `artifacts/production-audits/`:

- `coverage-20260827T054703Z.json`
  - SHA-256: `f4eb60db696c8c693a160b19cc8617530f334d15aae070d19c03b05befbcedcb`
- `coverage-20260827T054703Z-industries.csv`
- `symbol-coverage-20260827T055105Z.json`
  - SHA-256: `3c00804b02697e12c474af41fa9f65cd3a5eb607613fa52492a25cbd465553cd`
- `symbol-coverage-20260827T055105Z.csv`
  - SHA-256: `fd7ac9d6596b8f2f5865a9bb9fc3a0f7d998bb7c84ec75ec5269267353d27a07`

Post-cleanup evidence:

- `coverage-after-alias-cleanup-20260827T055539Z.json`
  - SHA-256: `0df714fed1ae39661603e7993d3a10eae611ba38d3e4e32a5e59ecc27e48f777`
- `symbol-coverage-after-alias-cleanup-20260827T055609Z.json`
  - SHA-256: `ef798e086608d10beb0c04ffcb5610117d720f0a2d8914a685331e93c5aed735`
- `symbol-coverage-after-alias-cleanup-20260827T055609Z.csv`
  - SHA-256: `caa92aa3ff02d07ea93ddb64b1599f9a90ea9972f93f63ebd8a71b1c5234699c`
- Production backup: `/var/backups/boursnegar/20260827T055454Z-duplicate-symbol-instruments.json`
- Production rollback SQL: `/var/backups/boursnegar/20260827T055454Z-duplicate-symbol-instruments.rollback.sql`

## Global Counts

From the industry-level audit:

- Active instruments: 1,533
- Current symbol aliases represented in industry grouping: 1,524
- Issuers with periods: 977
- Financial periods: 12,018
- Financial facts: 44,088
- Valid facts: 17,761
- Valid prices: 484,739
- Raw Codalpy records: 1,127,218
- Linked Codalpy records: 1,079,010
- Monthly Codalpy records: 761,691
- Linked monthly Codalpy records: 719,310

The industry-level query groups by current symbol aliases and therefore totals 1,524 symbols, while the symbol-level audit includes all 1,533 active instruments and exposes 9 active instruments without a current alias.

## Post-Cleanup Reconciliation

The 9 alias-less active rows were verified as duplicate/orphan records: each had no aliases, disclosures, periods, facts, prices, or corporate actions, while the same symbol already had a validated current `BrsApi` alias on another active instrument. They were deactivated together with their empty issuer rows under a transaction guard. The backup and rollback files above remain available.

Post-cleanup active identity check:

- Active instruments: 1,524
- Active instruments with current alias: 1,524
- Active instruments without current alias: 0

Post-cleanup symbol-level coverage tiers:

- `CORE_READY`: 215
- `MISSING_CORE_FACTS`: 418
- `MISSING_COMPARABLE_PERIODS`: 891
- `NO_CURRENT_ALIAS`: 0

Post-cleanup latest persisted decisions:

- `INSUFFICIENT_DATA`: 1,520
- `SELL`: 3
- `HOLD`: 1
- `BUY`: 0

The four decision counts sum to 1,524. The identity cleanup did not add analytical facts or infer decisions; the remaining gaps are data-coverage gaps.

## Symbol-Level Coverage Tiers

From the initial symbol-level audit across all 1,533 active instruments:

- `CORE_READY`: 215
- `MISSING_CORE_FACTS`: 418
- `MISSING_COMPARABLE_PERIODS`: 891
- `NO_CURRENT_ALIAS`: 9

Latest persisted decisions:

- `INSUFFICIENT_DATA`: 1,529
- `SELL`: 3
- `HOLD`: 1
- `BUY`: 0

This is not full analytical coverage. Most instruments remain either missing comparable periods or missing core fact breadth, and almost all latest decisions remain `INSUFFICIENT_DATA`.

## Active Instruments Without Current Alias

These 9 active instruments need identity reconciliation before they can be treated as normal symbol coverage:

| Instrument marker | Legal name | Industry |
|---|---|---|
| `NO_CURRENT_ALIAS:29aee440-eb4c-4422-a265-95c9b5bed4ce` | وساپا | نامشخص |
| `NO_CURRENT_ALIAS:2a9a91fc-0f17-4975-aae1-4ae4f705dd7f` | دروز | نامشخص |
| `NO_CURRENT_ALIAS:689b59dc-14c7-4348-bcd4-76c64ec5b402` | خبازرس | نامشخص |
| `NO_CURRENT_ALIAS:7a22a68f-273a-44e1-a8d5-e1f1b679e618` | وپخش | نامشخص |
| `NO_CURRENT_ALIAS:891b7037-d7d8-4904-b8be-27f170d85945` | ومهان | نامشخص |
| `NO_CURRENT_ALIAS:9f8721a9-bd44-419e-8293-ae8cdff6ab68` | داروسازی کوثر | نامشخص |
| `NO_CURRENT_ALIAS:a7ee75a8-11a3-4710-84bf-c91c8db81797` | پالایش نفت شیراز | نامشخص |
| `NO_CURRENT_ALIAS:b497f463-3e14-45f6-8db8-fb92bdbe2446` | بانک تجارت | نامشخص |
| `NO_CURRENT_ALIAS:c4117252-f99a-428c-8ec8-acc1885e3c70` | کزغال | نامشخص |

Do not create aliases by guessing. Reconcile each one from authoritative instrument identity, source disclosure identity, or an existing validated alias history.

## Largest Comparable-Period Gaps

Top industries by `MISSING_COMPARABLE_PERIODS`:

| Industry | Symbols | Core ready | Missing comparable | Missing core |
|---|---:|---:|---:|---:|
| صندوق سرمایه‌گذاری قابل معامله | 419 | 0 | 181 | 238 |
| مواد و محصولات دارویی | 75 | 5 | 58 | 12 |
| محصولات غذایی و آشامیدنی به جز قند و شکر | 76 | 3 | 56 | 17 |
| خودرو و ساخت قطعات | 68 | 6 | 54 | 8 |
| سرمایه‌گذاری‌ها | 84 | 17 | 47 | 20 |
| سیمان، آهک و گچ | 72 | 26 | 43 | 3 |
| فلزات اساسی | 76 | 28 | 42 | 6 |
| محصولات شیمیایی | 88 | 37 | 41 | 10 |
| انبوه‌سازی، املاک و مستغلات | 45 | 9 | 34 | 2 |
| رایانه و فعالیت‌های وابسته به آن | 28 | 1 | 27 | 0 |

## Largest Core-Fact Gaps

Top industries by `MISSING_CORE_FACTS`:

| Industry | Symbols | Core ready | Missing comparable | Missing core |
|---|---:|---:|---:|---:|
| صندوق سرمایه‌گذاری قابل معامله | 419 | 0 | 181 | 238 |
| بیمه و صندوق بازنشستگی به جز تامین اجتماعی | 46 | 2 | 19 | 25 |
| سرمایه‌گذاری‌ها | 84 | 17 | 47 | 20 |
| محصولات غذایی و آشامیدنی به جز قند و شکر | 76 | 3 | 56 | 17 |
| مواد و محصولات دارویی | 75 | 5 | 58 | 12 |
| محصولات شیمیایی | 88 | 37 | 41 | 10 |
| ماشین‌آلات و تجهیزات | 22 | 2 | 11 | 9 |
| خودرو و ساخت قطعات | 68 | 6 | 54 | 8 |
| قند و شکر | 26 | 2 | 17 | 7 |
| لاستیک و پلاستیک | 15 | 1 | 7 | 7 |

## Next Data Work

1. Keep ETF/fund instruments separate from operating-company coverage; `CORE_READY=0` for ETFs should not be forced through operating-company fact logic.
2. Prioritize operating industries with large comparable-period gaps before trying to improve decision counts.
3. Promote monthly Codalpy evidence to canonical monthly facts only after explicit label, period, unit, source, and row/column validation.
4. Keep `INSUFFICIENT_DATA` for any symbol below the required tier; do not infer buy/hold/sell from raw-record counts.
