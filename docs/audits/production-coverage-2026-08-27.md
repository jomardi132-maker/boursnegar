# Production coverage audit - 2026-08-27

Generated from Production at `2026-08-27T05:47:03Z`, `2026-08-27T05:51:05Z`, post-cleanup at `2026-08-27T05:55:39Z` / `2026-08-27T05:56:09Z`, post-sync at `2026-08-27T13:16:51Z`, and recovery follow-ups through `2026-08-27T18:07:30Z`.

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
- `coverage-after-sync-20260827T1316Z.json`
  - SHA-256: `14280d7202fa854360b23fcfa71890e60f16aa721bd7e676f532ef0e1dbc6e20`
- `coverage-after-supervisor-20260827T1342Z.json`
  - SHA-256: `f5f15072eec3a044290bd7be03ec1635b24dc3288d3cd793a78735f412e198b0`
- `coverage-after-supervisor-20260827T1410Z.json`
  - SHA-256: `f4d92ae4288d59d4e17deeef7d0b820cb33a2d122bd12c0b7d5a03e31540acdc`
- `coverage-after-supervisor-20260827T1438Z.json`
  - SHA-256: `aceb92161e915dfd0128f89ebfcb0f92e892e1b4091680d5fa63d55b5254dd56`
- `coverage-after-supervisor-20260827T1504Z.json`
  - SHA-256: `a937f031fda61df2e1294d5d9fb41c50b17c1370ef123d4716b11a7fd5921da6`
- `coverage-after-supervisor-20260827T1540Z.json`
  - SHA-256: `6b002d3d0fc3b3800e127d97ca0d89f4d964a15cb137e3068f129b9eae083e96`
- `coverage-after-supervisor-20260827T1610Z.json`
  - SHA-256: `2af2701028dd3ebc85758ca441976935d89e9a41ed056636a901b0b0c6881714`
- `coverage-after-supervisor-20260827T1636Z.json`
  - SHA-256: `d696e1a4df67a21dae21a4de1b9e144e6eaad1762af0a53b95222f8eb376181c`
- `coverage-after-supervisor-20260827T1703Z.json`
  - SHA-256: `9ce05a6e1966b0395ce90e0bacdd10a5fa5da11787e5dc876fb37bb2b12b3dbf`
- `coverage-after-supervisor-20260827T1734Z.json`
  - SHA-256: `d4ffa5c2b6732df12c0430d42c1cc67df29bf72dc14b23659e37df50d891f0d7`
- `coverage-after-supervisor-20260827T1807Z.json`
  - SHA-256: `681c7058f166278967016c5925644e813002e438cb407d0d2428c0b313514832`
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

## Post-Sync Import

The first bounded local-first recovery batch after the cleanup processed 3 selected symbols. It reused existing checkpoints, fetched through the local Codalpy/browser pipeline, validated manifests, and imported through the Production artifact importer.

- Backup: `/var/backups/boursnegar/20260827T131431Z-auto-local-to-production.dump`
- Manifests: Codalpy, normalized statements, and notice events
- Aggregate records transferred: 3,702
- First-pass importer results: 36 Codalpy records / 216 standardized facts, 15 normalized records / 9 standardized facts, and 21 notice events
- Repeat-import idempotency gate: passed with `inserted=0` for all three manifests
- Validation errors: 0
- Post-sync global counts: financial periods `12,026`, financial facts `44,098`, valid facts `17,770`, raw Codalpy records `1,127,269`, linked Codalpy records `1,079,061`
- Post-sync health: FastAPI `/health`, Node `/healthz`, and `/readyz` passed

The imported batch is evidence-backed but does not establish full analytical coverage. Local Codalpy timeouts and statement-normalization errors were retained in checkpoints/manifests; they were not converted into facts by inference.

## Supervisor Recovery Progress

The checkpointed all-symbol supervisor completed 5 batches of 10 symbols (50 symbols total), each with exit code 0. It imported only validated artifacts and kept symbols with missing or unusable evidence in the retry/coverage queue.

- Local recovery state after the cycle: `complete=492`, `comparable=291`, `incomplete=741`
- Supervisor pending queue after the cycle: 1,081 symbols
- The batch logs and checkpoints remain under ignored `artifacts/all-symbols/`; they are local operational evidence, not production claims.
- Production audit after the cycle: financial periods `12,104`, financial facts `44,429`, valid facts `18,101`, raw Codalpy records `1,127,600`, linked Codalpy records `1,079,392`
- Production health remained green after the cycle.

## Symbol-Level Coverage Tiers

## Recovery Follow-up

The next checkpointed supervisor cycle completed batches `0006` through `0010` (50 additional symbols), all with exit code 0. Validated normalized statements, notice events, and available Codalpy artifacts were imported through the existing artifact-only Production path; no inferred facts were created.

- Supervisor pending queue: `1,050` symbols, down from `1,081`
- Local supervisor state files: 31 no-notice symbols, 47 insufficient-fact symbols, and 32 stable-fact symbols
- Production audit: financial periods `12,225`, financial facts `44,949`, valid facts `18,588`, raw Codalpy records `1,130,358`, linked Codalpy records `1,082,150`
- Validation errors in the Production audit: none reported
- Production health remained green after the cycle

The remaining queue is still not analytical completion. Symbols with no authoritative notices, insufficient comparable periods, or unresolved normalization evidence remain explicitly queued or quarantined.

The next checkpointed cycle completed batches `0011` through `0015` (50 additional symbols), all with exit code 0. The supervisor pending queue decreased from `1,050` to `1,016`. The new Production audit reports financial periods `12,332`, financial facts `45,350`, valid facts `18,993`, raw Codalpy records `1,130,785`, and linked Codalpy records `1,082,577`. No validation errors were reported by the audit.

The following checkpointed cycle completed batches `0016` through `0020` (50 additional symbols), all with exit code 0. The supervisor pending queue decreased from `1,016` to `986`. The new Production audit reports financial periods `12,412`, financial facts `45,586`, valid facts `19,211`, raw Codalpy records `1,140,827`, linked Codalpy records `1,092,619`, monthly records `770,241`, and linked monthly records `727,860`. No validation errors were reported by the audit, and runtime health remained green.

The following checkpointed cycle completed batches `0021` through `0025` (50 additional symbols), all with exit code 0. The supervisor pending queue decreased from `986` to `944`. The new Production audit reports financial periods `12,556`, financial facts `46,245`, valid facts `19,827`, raw Codalpy records `1,149,922`, linked Codalpy records `1,101,714`, monthly records `776,533`, and linked monthly records `734,152`. No validation errors were reported by the audit, and runtime health remained green.

The following checkpointed cycle completed batches `0026` through `0030` (50 additional symbols), all with exit code 0. The supervisor pending queue decreased from `944` to `900`. The new Production audit reports financial periods `12,678`, financial facts `46,792`, valid facts `20,250`, raw Codalpy records `1,162,855`, linked Codalpy records `1,114,647`, monthly records `784,104`, and linked monthly records `741,723`. No validation errors were reported by the audit, and runtime health remained green.

The following checkpointed cycle completed batches `0031` through `0035` (50 additional symbols), all with exit code 0. The supervisor pending queue decreased from `900` to `873`. The new Production audit reports financial periods `12,742`, financial facts `47,029`, valid facts `20,493`, raw Codalpy records `1,163,102`, linked Codalpy records `1,114,894`, monthly records `784,104`, and linked monthly records `741,723`. No validation errors were reported by the audit, and runtime health remained green.

The following checkpointed cycle completed batches `0036` through `0040` (50 additional symbols), all with exit code 0. The supervisor pending queue decreased from `873` to `844`. The new Production audit reports financial periods `12,830`, financial facts `47,431`, valid facts `20,814`, raw Codalpy records `1,170,801`, linked Codalpy records `1,122,593`, monthly records `788,400`, and linked monthly records `746,019`. No validation errors were reported by the audit, and runtime health remained green.

The following checkpointed cycle completed batches `0041` through `0045` (50 additional symbols), all with exit code 0. The supervisor pending queue decreased from `844` to `802`. The new Production audit reports financial periods `12,952`, financial facts `47,935`, valid facts `21,257`, raw Codalpy records `1,177,421`, linked Codalpy records `1,129,213`, monthly records `792,226`, and linked monthly records `749,845`. No validation errors were reported by the audit, and runtime health remained green.

The following checkpointed cycle completed batches `0046` through `0050` (50 additional symbols), all with exit code 0. The supervisor pending queue decreased from `802` to `768`. The new Production audit reports financial periods `13,015`, financial facts `48,157`, valid facts `21,503`, raw Codalpy records `1,177,671`, linked Codalpy records `1,129,463`, monthly records `792,226`, and linked monthly records `749,845`. No validation errors were reported by the audit, and runtime health remained green.

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

1. Continue bounded local-first recovery batches for operating symbols, using checkpointed retries and per-batch manifests.
2. Keep ETF/fund instruments separate from operating-company coverage; `CORE_READY=0` for ETFs should not be forced through operating-company fact logic.
3. Prioritize operating industries with large comparable-period gaps before trying to improve decision counts.
4. Promote monthly Codalpy evidence to canonical monthly facts only after explicit label, period, unit, source, and row/column validation.
5. Keep `INSUFFICIENT_DATA` for any symbol below the required tier; do not infer buy/hold/sell from raw-record counts.
