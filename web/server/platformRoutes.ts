import crypto from "crypto";
import { execFile } from "node:child_process";
import { promisify } from "node:util";
import type express from "express";
import { z } from "zod";
import { pool, withTransaction } from "./postgres";
import { requireAdmin, requireCsrf, requireUser } from "./auth";

const asyncRoute =
  (fn: express.RequestHandler): express.RequestHandler =>
  (req, res, next) =>
    Promise.resolve(fn(req, res, next)).catch(next);
const execFileAsync = promisify(execFile);
const audit = async (
  adminId: string,
  action: string,
  targetType: string,
  targetId: string,
  ip: string,
  metadata: object = {},
) =>
  pool.query(
    `INSERT INTO admin_audit_logs(admin_user_id,action,target_type,target_id,metadata,ip) VALUES($1,$2,$3,$4,$5,$6::inet)`,
    [adminId, action, targetType, targetId, metadata, ip],
  );

const priceReturn = (prices: Array<Record<string, unknown>>, months: number) => {
  const latest = prices.at(-1);
  const latestValue = Number(latest?.adjusted_close ?? latest?.close);
  if (!latest || !Number.isFinite(latestValue)) return null;
  const cutoff = new Date(String(latest.trading_date));
  cutoff.setUTCMonth(cutoff.getUTCMonth() - months);
  const baseline = [...prices].reverse().find((row) =>
    new Date(String(row.trading_date)).getTime() <= cutoff.getTime(),
  );
  const baselineValue = Number(baseline?.adjusted_close ?? baseline?.close);
  return baseline && Number.isFinite(baselineValue) && baselineValue !== 0
    ? ((latestValue / baselineValue) - 1) * 100
    : null;
};

export function installPlatformRoutes(app: express.Express) {
  app.get("/robots.txt", (_req, res) => {
    res.type("text/plain").send("User-agent: *\nAllow: /\nDisallow: /api/\nSitemap: https://boursnegar.ir/sitemap.xml\n");
  });
  app.get(
    "/sitemap.xml",
    asyncRoute(async (_req, res) => {
      res.set("Cache-Control", "public, max-age=30, stale-while-revalidate=120");
      const rows = await pool.query(`SELECT sa.symbol FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id WHERE sa.valid_to IS NULL AND i.active AND sa.symbol !~ '[0-9۰-۹]$' ORDER BY sa.symbol`);
      const urls = ["<url><loc>https://boursnegar.ir/</loc><changefreq>daily</changefreq><priority>1.0</priority></url>", ...rows.rows.map(({symbol}) => `<url><loc>https://boursnegar.ir/s/${encodeURIComponent(symbol)}</loc><changefreq>daily</changefreq><priority>0.7</priority></url>`)];
      res.type("application/xml").send(`<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">${urls.join("")}</urlset>`);
    }),
  );
  app.get(
    "/api/market/overview",
    asyncRoute(async (_req, res) => {
      const [catalog, prices, disclosures, coverage] = await Promise.all([
        pool.query(`SELECT count(*)::int AS instruments FROM instruments WHERE active`),
        pool.query(`SELECT count(*)::int AS rows,count(DISTINCT instrument_id)::int AS instruments,min(trading_date) AS from_date,max(trading_date) AS to_date FROM daily_prices`),
        pool.query(`SELECT count(*)::int AS rows,count(DISTINCT d.issuer_id)::int AS issuers,max(v.retrieved_at) AS updated_at FROM disclosure_versions v JOIN disclosures d ON d.id=v.disclosure_id`),
        pool.query(`SELECT count(*)::int AS analyzed FROM analytical_snapshots`),
      ]);
      res.json({ success: true, catalog: catalog.rows[0], prices: prices.rows[0], disclosures: disclosures.rows[0], analysis: coverage.rows[0] });
    }),
  );
  app.get(
    "/api/market/dashboard",
    asyncRoute(async (_req, res) => {
      const result = await pool.query(`
        WITH latest AS (
          SELECT DISTINCT ON (p.instrument_id) p.instrument_id,p.trading_date,p.trading_date_jalali,
            coalesce(p.adjusted_close,p.close) AS price,p.volume,p.value,p.trade_count
          FROM daily_prices p WHERE p.quality_status='VALID'
          ORDER BY p.instrument_id,p.trading_date DESC
        ), market AS (
          SELECT l.*,prev.price AS previous_price,sa.symbol,ir.legal_name
          FROM latest l JOIN instruments i ON i.id=l.instrument_id AND i.active
          JOIN symbol_aliases sa ON sa.instrument_id=i.id AND sa.valid_to IS NULL
          JOIN issuers ir ON ir.id=i.issuer_id
          LEFT JOIN LATERAL (SELECT coalesce(p.adjusted_close,p.close) AS price FROM daily_prices p
            WHERE p.instrument_id=l.instrument_id AND p.trading_date<l.trading_date AND p.quality_status='VALID'
            ORDER BY p.trading_date DESC LIMIT 1) prev ON true
          WHERE sa.symbol !~ '[0-9۰-۹]$'
        )
        SELECT max(trading_date) AS latest_date,count(*)::int AS symbols,
          coalesce(sum(value),0) AS total_value,coalesce(sum(volume),0) AS total_volume,
          count(*) FILTER (WHERE price>previous_price)::int AS advancers,
          count(*) FILTER (WHERE price<previous_price)::int AS decliners,
          count(*) FILTER (WHERE price=previous_price)::int AS unchanged,
          (SELECT jsonb_agg(x ORDER BY x.change_percent DESC) FROM (SELECT symbol,legal_name,price,value,round(((price/NULLIF(previous_price,0))-1)*100,2) AS change_percent FROM market WHERE previous_price>0 ORDER BY change_percent DESC NULLS LAST LIMIT 5) x) AS top_gainers,
          (SELECT jsonb_agg(x ORDER BY x.change_percent) FROM (SELECT symbol,legal_name,price,value,round(((price/NULLIF(previous_price,0))-1)*100,2) AS change_percent FROM market WHERE previous_price>0 ORDER BY change_percent ASC NULLS LAST LIMIT 5) x) AS top_losers,
          (SELECT jsonb_agg(x ORDER BY x.value DESC NULLS LAST) FROM (SELECT symbol,legal_name,price,value,round(((price/NULLIF(previous_price,0))-1)*100,2) AS change_percent FROM market ORDER BY value DESC NULLS LAST LIMIT 8) x) AS top_value
        FROM market`);
      res.set("Cache-Control", "public, max-age=60, stale-while-revalidate=300");
      res.json({ success: true, ...result.rows[0] });
    }),
  );
  app.get(
    "/api/market/screener",
    asyncRoute(async (req, res) => {
      const parsed = z.object({ q:z.string().trim().max(40).default(""), industry:z.string().trim().max(80).default(""), decision:z.enum(["","BUY","HOLD","SELL","INSUFFICIENT_DATA"]).default(""), minReturn:z.coerce.number().min(-1000).max(10000).optional(), maxPe:z.coerce.number().min(0).max(10000).optional(), minRoe:z.coerce.number().min(-10000).max(10000).optional(), minVolume:z.coerce.number().min(0).optional(), trend:z.enum(["","above_ma20","above_ma50"]).default(""), sort:z.enum(["value","return","volume","health","pe"]).default("value"), page:z.coerce.number().int().min(1).max(1000).default(1) }).safeParse(req.query);
      if (!parsed.success) return res.status(400).json({ success:false,error:"فیلترهای اسکرینر معتبر نیستند." });
      const v=parsed.data; const orderBy:Record<string,string>={value:"value DESC NULLS LAST",return:"return_1m DESC NULLS LAST",volume:"volume DESC NULLS LAST",health:"health_score DESC NULLS LAST",pe:"pe ASC NULLS LAST"};
      const result=await pool.query(`
        WITH latest AS (SELECT DISTINCT ON (p.instrument_id) p.instrument_id,p.trading_date,p.trading_date_jalali,coalesce(p.adjusted_close,p.close) AS price,p.volume,p.value,p.trade_count FROM daily_prices p WHERE p.quality_status='VALID' ORDER BY p.instrument_id,p.trading_date DESC),
        universe AS (
          SELECT sa.symbol,ir.legal_name,coalesce(ind.title_fa,'') AS industry,l.trading_date,l.trading_date_jalali,l.price,l.volume,l.value,l.trade_count,
            round(((l.price/NULLIF(month.price,0))-1)*100,2) AS return_1m,round(moving.ma20,2) AS ma20,round(moving.ma50,2) AS ma50,
            snap.quality_summary->>'decision' AS decision,nullif(snap.quality_summary->>'healthScore','')::numeric AS health_score,
            nullif(snap.quality_summary->'keyMetrics'->>'pe','')::numeric AS pe,nullif(snap.quality_summary->'keyMetrics'->>'roe','')::numeric AS roe
          FROM latest l JOIN instruments i ON i.id=l.instrument_id AND i.active JOIN symbol_aliases sa ON sa.instrument_id=i.id AND sa.valid_to IS NULL JOIN issuers ir ON ir.id=i.issuer_id AND ir.active LEFT JOIN industries ind ON ind.id=ir.industry_id
          LEFT JOIN LATERAL (SELECT coalesce(p.adjusted_close,p.close) AS price FROM daily_prices p WHERE p.instrument_id=l.instrument_id AND p.trading_date<=l.trading_date-interval '1 month' AND p.quality_status='VALID' ORDER BY p.trading_date DESC LIMIT 1) month ON true
          LEFT JOIN LATERAL (SELECT avg(price) FILTER (WHERE rn<=20) AS ma20,avg(price) FILTER (WHERE rn<=50) AS ma50 FROM (SELECT coalesce(p.adjusted_close,p.close) AS price,row_number() OVER (ORDER BY p.trading_date DESC) AS rn FROM daily_prices p WHERE p.instrument_id=l.instrument_id AND p.trading_date<=l.trading_date AND p.quality_status='VALID' ORDER BY p.trading_date DESC LIMIT 50) prices) moving ON true
          LEFT JOIN LATERAL (SELECT s.quality_summary FROM analytical_snapshots s WHERE s.instrument_id=l.instrument_id ORDER BY s.calculated_at DESC LIMIT 1) snap ON true
          WHERE sa.symbol !~ '[0-9۰-۹]$'
        ), filtered AS (SELECT * FROM universe WHERE ($1='' OR symbol ILIKE '%'||$1||'%' OR legal_name ILIKE '%'||$1||'%') AND ($2='' OR industry=$2) AND ($3='' OR decision=$3) AND ($4::numeric IS NULL OR return_1m >= $4) AND ($5::numeric IS NULL OR pe <= $5) AND ($6::numeric IS NULL OR roe >= $6) AND ($7::numeric IS NULL OR volume >= $7) AND ($8='' OR ($8='above_ma20' AND price>ma20) OR ($8='above_ma50' AND price>ma50)))
        SELECT *,count(*) OVER()::int AS total FROM filtered ORDER BY ${orderBy[v.sort]},symbol LIMIT 50 OFFSET $9`,[v.q,v.industry,v.decision,v.minReturn??null,v.maxPe??null,v.minRoe??null,v.minVolume??null,v.trend,(v.page-1)*50]);
      const industries=await pool.query(`SELECT title_fa FROM industries ORDER BY title_fa`);
      res.set("Cache-Control","public, max-age=30, stale-while-revalidate=120");
      res.json({success:true,rows:result.rows,total:result.rows[0]?.total??0,page:v.page,industries:industries.rows.map(row=>row.title_fa)});
    }),
  );
  app.get(
    "/api/admin/data-status",
    requireUser,
    requireAdmin,
    asyncRoute(async (_req, res) => {
      const [counts, pipelines, issues, dataService] = await Promise.all([
        pool.query(`SELECT
          (SELECT count(*)::int FROM instruments WHERE active) AS instruments,
          (SELECT count(*)::int FROM daily_prices) AS daily_prices,
          (SELECT count(DISTINCT instrument_id)::int FROM daily_prices) AS price_symbols,
          (SELECT count(*)::int FROM disclosures) AS disclosures,
          (SELECT count(*)::int FROM disclosure_versions) AS disclosure_versions,
          (SELECT count(*)::int FROM analytical_snapshots) AS analyses,
          (SELECT max(trading_date) FROM daily_prices) AS latest_price_date,
          (SELECT max(retrieved_at) FROM disclosure_versions) AS latest_disclosure_at`),
        pool.query(`SELECT pipeline,status,started_at,finished_at,metrics,error_summary FROM ingestion_runs ORDER BY started_at DESC LIMIT 30`),
        pool.query(`SELECT severity,issue_code,cause,status,detected_at FROM data_quality_issues WHERE status='OPEN' ORDER BY detected_at DESC LIMIT 30`),
        fetch(`${process.env.PYTHON_API_BASE || "http://127.0.0.1:8001"}/health`, { signal: AbortSignal.timeout(4000) })
          .then(async (response) => ({ ok: response.ok, status: response.status, detail: await response.json().catch(() => null) }))
          .catch(() => ({ ok: false, status: 0, detail: null })),
      ]);
      const latestByKind = (kind: string) =>
        pipelines.rows.find((run: any) => String(run.pipeline).toLowerCase().includes(kind)) ?? null;
      res.json({
        success: true,
        counts: counts.rows[0],
        pipelines: pipelines.rows,
        issues: issues.rows,
        providers: {
          data_service: dataService,
          market: latestByKind("market"),
          codal: latestByKind("codal"),
        },
      });
    }),
  );
  app.post(
    "/api/admin/data-refresh/:pipeline",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const services: Record<string, string> = {
        market: "boursnegar-market-daily.service",
        codal: "boursnegar-codal-backfill.service",
      };
      const service = services[req.params.pipeline];
      if (!service)
        return res.status(400).json({ success: false, error: "خط داده معتبر نیست." });
      try {
        await execFileAsync("/usr/bin/systemctl", ["start", "--no-block", service], { timeout: 5000 });
      } catch (error: any) {
        const detail = String(error?.stderr || "").slice(0, 300);
        return res.status(503).json({ success: false, error: detail || "اجرای به‌روزرسانی ممکن نشد." });
      }
      await audit(req.authUser!.id, "data.refresh", "systemd_service", service, req.ip || "127.0.0.1");
      res.status(202).json({ success: true, pipeline: req.params.pipeline, service, message: "به‌روزرسانی در صف اجرا قرار گرفت." });
    }),
  );
  app.get(
    "/api/stocks/:symbol",
    asyncRoute(async (req, res) => {
      const symbol = z.string().trim().min(1).max(32).safeParse(req.params.symbol);
      if (!symbol.success) return res.status(400).json({ success: false, error: "نماد معتبر نیست." });
      const profile = await pool.query(
        `SELECT i.id AS instrument_id,sa.symbol,i.isin,i.market_instrument_id,
                ir.legal_name,ind.title_fa AS industry,ind.model_family
         FROM symbol_aliases sa JOIN instruments i ON i.id=sa.instrument_id
         JOIN issuers ir ON ir.id=i.issuer_id LEFT JOIN industries ind ON ind.id=ir.industry_id
         WHERE sa.symbol=$1 AND sa.valid_to IS NULL AND i.active LIMIT 1`,
        [symbol.data],
      );
      if (!profile.rowCount) return res.status(404).json({ success: false, error: "نماد پیدا نشد." });
      const stock = profile.rows[0];
      const [history, disclosureRows, legacyDisclosureRows, snapshot] = await Promise.all([
        pool.query(
          `SELECT trading_date,trading_date_jalali,open,high,low,close,last,adjusted_close,volume,value,trade_count,quality_status
           FROM daily_prices WHERE instrument_id=$1 ORDER BY trading_date DESC LIMIT 420`,
          [stock.instrument_id],
        ),
        pool.query(
          `SELECT d.source_disclosure_id,d.title,d.published_date_jalali,d.is_audited,d.scope,
                  v.retrieved_at,v.metadata->>'detail_url' AS detail_url,v.metadata->>'excel_url' AS excel_url
           FROM disclosures d JOIN disclosure_versions v ON v.disclosure_id=d.id AND v.is_current
           WHERE d.instrument_id=$1 ORDER BY coalesce(d.published_at,v.retrieved_at) DESC LIMIT 16`,
          [stock.instrument_id],
        ),
        pool.query(
          `SELECT fr.tracing_no AS source_disclosure_id,fr.title,
                  fr.publish_datetime AS published_date_jalali,fr.is_audited,
                  'separate' AS scope,fr.fetched_at AS retrieved_at,
                  fr.detail_url,fr.excel_url
           FROM financial_reports fr JOIN companies c ON c.id=fr.company_id
           WHERE c.symbol=$1 ORDER BY fr.fetched_at DESC LIMIT 16`,
          [stock.symbol],
        ),
        pool.query(
          `SELECT s.id,s.status,s.data_as_of,s.calculated_at,s.coverage,s.confidence,
                  r.decision,r.top_reasons,r.top_risks,r.critical_warning,
                  h.score,v.fair_value_low,v.fair_value_base,v.fair_value_high,v.model_type,v.model_version
           FROM analytical_snapshots s
           LEFT JOIN recommendation_results r ON r.snapshot_id=s.id
           LEFT JOIN health_score_results h ON h.snapshot_id=s.id
           LEFT JOIN valuation_results v ON v.snapshot_id=s.id
           WHERE s.instrument_id=$1 ORDER BY s.calculated_at DESC LIMIT 1`,
          [stock.instrument_id],
        ),
      ]);
      const prices = history.rows.reverse();
      const latest = prices.at(-1) ?? null;
      const returns = {
        oneMonth: priceReturn(prices, 1),
        sixMonths: priceReturn(prices, 6),
        oneYear: priceReturn(prices, 12),
      };
      const disclosures = [...disclosureRows.rows, ...legacyDisclosureRows.rows]
        .filter((row, index, all) => all.findIndex((item) => String(item.source_disclosure_id) === String(row.source_disclosure_id)) === index)
        .slice(0, 16);
      res.set("Cache-Control", "public, max-age=60, stale-while-revalidate=300");
      res.json({ success: true, stock: { ...stock, instrument_id: undefined }, latest, returns, prices, disclosures, snapshot: snapshot.rows[0] ?? null });
    }),
  );
  app.get(
    "/api/symbols/search",
    asyncRoute(async (req, res) => {
      const parsed = z.string().trim().min(1).max(80).safeParse(req.query.q);
      if (!parsed.success)
        return res.json({ success: true, results: [] });
      const query = parsed.data
        .replace(/[يى]/g, "ی")
        .replace(/ك/g, "ک")
        .replace(/\u200c/g, " ")
        .replace(/\s+/g, " ");
      const r = await pool.query(
        `SELECT sa.symbol,i.isin,i.market_instrument_id,
                ir.legal_name,ind.title_fa AS industry,
                greatest(similarity(sa.symbol,$1),similarity(ir.legal_name,$1)) AS score
         FROM symbol_aliases sa
         JOIN instruments i ON i.id=sa.instrument_id AND i.active
         JOIN issuers ir ON ir.id=i.issuer_id AND ir.active
         LEFT JOIN industries ind ON ind.id=ir.industry_id
         WHERE sa.valid_to IS NULL
           AND (sa.symbol !~ '[0-9۰-۹]$' OR sa.symbol=$1)
           AND (sa.symbol ILIKE '%'||$1||'%' OR ir.legal_name ILIKE '%'||$1||'%'
                OR similarity(sa.symbol,$1)>0.18 OR similarity(ir.legal_name,$1)>0.18)
         ORDER BY (sa.symbol=$1) DESC,(sa.symbol ILIKE $1||'%') DESC,
                  score DESC,length(sa.symbol),sa.symbol
         LIMIT 10`,
        [query],
      );
      res.set("Cache-Control", "public, max-age=60, stale-while-revalidate=300");
      res.json({ success: true, results: r.rows });
    }),
  );
  app.get(
    "/api/plans",
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT id,code,title_fa,description_fa,duration_days,price_toman,
                analysis_credits,unlimited_analyses,features,display_order,
                discount,sale_starts_at,sale_ends_at
         FROM plans
         WHERE active AND publicly_visible
           AND (sale_starts_at IS NULL OR sale_starts_at<=now())
           AND (sale_ends_at IS NULL OR sale_ends_at>now())
         ORDER BY display_order,duration_days`,
      );
      res.json({ success: true, plans: r.rows });
    }),
  );
  app.get(
    "/api/campaigns",
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT id,code,title_fa,starts_at,ends_at,capacity,credit_amount,price_toman,(SELECT count(*)::int FROM promotion_redemptions WHERE promotion_id=promotions.id) AS used FROM promotions WHERE active AND starts_at<=now() AND ends_at>now() AND (capacity IS NULL OR capacity>(SELECT count(*) FROM promotion_redemptions WHERE promotion_id=promotions.id)) ORDER BY ends_at`,
      );
      res.json({ success: true, campaigns: r.rows });
    }),
  );
  app.get(
    "/api/public/settings",
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT key,value FROM system_settings WHERE is_public`,
      );
      res.json({
        success: true,
        settings: Object.fromEntries(r.rows.map((x) => [x.key, x.value])),
      });
    }),
  );

  app.get(
    "/api/account/overview",
    requireUser,
    asyncRoute(async (req, res) => {
      const [credits, subscription, payments, referral] = await Promise.all([
        pool.query(`SELECT balance FROM analysis_credits WHERE user_id=$1`, [
          req.authUser!.id,
        ]),
        pool.query(
          `SELECT s.id,s.status,s.starts_at,s.ends_at,p.code,p.title_fa FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.user_id=$1 ORDER BY s.created_at DESC LIMIT 1`,
          [req.authUser!.id],
        ),
        pool.query(
          `SELECT id,amount_toman,tracking_number,status,created_at FROM payment_submissions WHERE user_id=$1 ORDER BY created_at DESC LIMIT 30`,
          [req.authUser!.id],
        ),
        pool.query(`SELECT referral_code FROM users WHERE id=$1`, [
          req.authUser!.id,
        ]),
      ]);
      res.json({
        success: true,
        credits: credits.rows[0]?.balance ?? 0,
        subscription: subscription.rows[0] ?? null,
        payments: payments.rows,
        referralCode: referral.rows[0]?.referral_code,
      });
    }),
  );
  app.get(
    "/api/account/referrals",
    requireUser,
    asyncRoute(async (req, res) => {
      const r = await pool.query(
        `SELECT rf.id,rf.status,rf.created_at,rf.rewarded_at,u.mobile_e164,e.email FROM referrals rf JOIN users u ON u.id=rf.referred_user_id LEFT JOIN email_identities e ON e.user_id=u.id WHERE rf.referrer_user_id=$1 ORDER BY rf.created_at DESC`,
        [req.authUser!.id],
      );
      res.json({
        success: true,
        referrals: r.rows.map((x) => ({
          ...x,
          mobile_e164: x.mobile_e164
            ? x.mobile_e164.replace(/(\+989\d{2})\d{4}(\d{3})/, "$1****$2")
            : x.email?.replace(/^(.{2}).*(@.*)$/, "$1***$2") ?? "—",
        })),
      });
    }),
  );

  const alertBaseSchema = z.object({
    symbol: z.string().regex(/^[\u0600-\u06FFa-zA-Z0-9‌_-]{1,32}$/),
    kind: z.enum(["price", "pe", "codal"]),
    comparator: z.enum(["gte", "lte"]).optional(),
    targetValue: z.number().positive().optional(),
  });
  const alertSchema = alertBaseSchema.superRefine((v, c) => {
    if (v.kind === "codal" && v.targetValue != null)
      c.addIssue({ code: "custom", message: "targetValue forbidden" });
    if (v.kind !== "codal" && v.targetValue == null)
      c.addIssue({ code: "custom", message: "targetValue required" });
    if (v.kind !== "codal" && v.comparator == null)
      c.addIssue({ code: "custom", message: "comparator required" });
  });
  app.get(
    "/api/alerts",
    requireUser,
    asyncRoute(async (req, res) => {
      const r = await pool.query(
        `SELECT id,symbol,kind,comparator,target_value,active,created_at FROM alerts WHERE user_id=$1 ORDER BY created_at DESC`,
        [req.authUser!.id],
      );
      res.json({ success: true, alerts: r.rows });
    }),
  );
  app.post(
    "/api/alerts",
    requireUser,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const p = alertSchema.safeParse(req.body);
      if (!p.success)
        return res
          .status(400)
          .json({ success: false, error: "اطلاعات هشدار معتبر نیست." });
      const v = p.data;
      const r = await pool.query(
        `INSERT INTO alerts(user_id,symbol,kind,comparator,target_value) VALUES($1,$2,$3,$4,$5) RETURNING *`,
        [
          req.authUser!.id,
          v.symbol,
          v.kind,
          v.kind === "codal" ? null : v.comparator,
          v.kind === "codal" ? null : v.targetValue,
        ],
      );
      res.status(201).json({ success: true, alert: r.rows[0] });
    }),
  );
  app.patch(
    "/api/alerts/:id",
    requireUser,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const p = alertBaseSchema
        .extend({ active: z.boolean() })
        .partial()
        .refine((value) => Object.keys(value).length > 0)
        .safeParse(req.body);
      if (!p.success)
        return res
          .status(400)
          .json({ success: false, error: "درخواست معتبر نیست." });
      const current = await pool.query(
        `SELECT symbol,kind,comparator,target_value,active FROM alerts WHERE id=$1 AND user_id=$2`,
        [req.params.id, req.authUser!.id],
      );
      if (!current.rowCount)
        return res
          .status(404)
          .json({ success: false, error: "هشدار پیدا نشد." });
      const merged = {
        symbol: p.data.symbol ?? current.rows[0].symbol,
        kind: p.data.kind ?? current.rows[0].kind,
        comparator:
          p.data.kind === "codal"
            ? undefined
            : (p.data.comparator ?? current.rows[0].comparator),
        targetValue:
          p.data.kind === "codal"
            ? undefined
            : (p.data.targetValue ?? current.rows[0].target_value),
      };
      const validated = alertSchema.safeParse(merged);
      if (!validated.success)
        return res
          .status(400)
          .json({ success: false, error: "اطلاعات هشدار معتبر نیست." });
      const v = validated.data;
      const criteriaChanged =
        v.symbol !== current.rows[0].symbol ||
        v.kind !== current.rows[0].kind ||
        v.comparator !== current.rows[0].comparator ||
        Number(v.targetValue ?? 0) !==
          Number(current.rows[0].target_value ?? 0);
      const r = await pool.query(
        `UPDATE alerts SET symbol=$3,kind=$4,comparator=$5,target_value=$6,active=$7,last_trigger_key=CASE WHEN $8 THEN NULL ELSE last_trigger_key END WHERE id=$1 AND user_id=$2 RETURNING id,symbol,kind,comparator,target_value,active`,
        [
          req.params.id,
          req.authUser!.id,
          v.symbol,
          v.kind,
          v.kind === "codal" ? null : v.comparator,
          v.kind === "codal" ? null : v.targetValue,
          p.data.active ?? current.rows[0].active,
          criteriaChanged,
        ],
      );
      if (!r.rowCount)
        return res
          .status(404)
          .json({ success: false, error: "هشدار پیدا نشد." });
      res.json({ success: true, alert: r.rows[0] });
    }),
  );
  app.delete(
    "/api/alerts/:id",
    requireUser,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const r = await pool.query(
        `DELETE FROM alerts WHERE id=$1 AND user_id=$2`,
        [req.params.id, req.authUser!.id],
      );
      res.status(r.rowCount ? 200 : 404).json({ success: Boolean(r.rowCount) });
    }),
  );

  app.get(
    "/api/admin/payments",
    requireUser,
    requireAdmin,
    asyncRoute(async (req, res) => {
      const status = z
        .enum(["pending", "approved", "rejected"])
        .catch("pending")
        .parse(req.query.status);
      const r = await pool.query(
        `SELECT ps.id,ps.amount_toman,ps.tracking_number,ps.paid_at,ps.status,ps.created_at,u.mobile_e164,e.email,p.code AS plan_code,pr.code AS campaign_code FROM payment_submissions ps JOIN users u ON u.id=ps.user_id LEFT JOIN email_identities e ON e.user_id=u.id LEFT JOIN plans p ON p.id=ps.plan_id LEFT JOIN promotions pr ON pr.id=ps.promotion_id WHERE ps.status=$1 ORDER BY ps.created_at`,
        [status],
      );
      res.json({ success: true, payments: r.rows });
    }),
  );
  app.post(
    "/api/admin/payments/:id/decision",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const parsed = z
        .object({
          decision: z.enum(["approved", "rejected"]),
          note: z.string().max(500).optional(),
        })
        .safeParse(req.body);
      if (!parsed.success)
        return res
          .status(400)
          .json({ success: false, error: "تصمیم معتبر نیست." });
      const result = await withTransaction(async (client) => {
        const found = await client.query(
          `SELECT ps.*,p.analysis_credits AS plan_credits,p.duration_days,
                  p.unlimited_analyses,p.title_fa AS plan_title_fa,
                  p.features AS plan_features,
                  pr.credit_amount AS campaign_credits,pr.active AS campaign_active,
                  pr.starts_at,pr.ends_at,pr.capacity,pr.rules,
                  u.created_at AS user_created_at
           FROM payment_submissions ps
           JOIN users u ON u.id=ps.user_id
           LEFT JOIN plans p ON p.id=ps.plan_id
           LEFT JOIN promotions pr ON pr.id=ps.promotion_id
           WHERE ps.id=$1 FOR UPDATE OF ps`,
          [req.params.id],
        );
        const payment = found.rows[0];
        if (!payment) throw new Error("NOT_FOUND");
        if (payment.status !== "pending") throw new Error("ALREADY_DECIDED");
        if (parsed.data.decision === "approved" && payment.promotion_id) {
          const count = await client.query(
            `SELECT count(*)::int AS used FROM promotion_redemptions WHERE promotion_id=$1`,
            [payment.promotion_id],
          );
          if (
            !payment.campaign_active ||
            new Date(payment.starts_at) > new Date() ||
            new Date(payment.ends_at) <= new Date() ||
            (payment.rules?.audience === "new_users" &&
              new Date(payment.user_created_at) <
                new Date(payment.starts_at)) ||
            (payment.rules?.audience === "existing_users" &&
              new Date(payment.user_created_at) >=
                new Date(payment.starts_at)) ||
            (payment.capacity != null && count.rows[0].used >= payment.capacity)
          )
            throw new Error("CAMPAIGN_UNAVAILABLE");
        }
        await client.query(
          `UPDATE payment_submissions SET status=$2 WHERE id=$1`,
          [payment.id, parsed.data.decision],
        );
        await client.query(
          `INSERT INTO payment_approvals(payment_id,admin_user_id,decision,note) VALUES($1,$2,$3,$4)`,
          [
            payment.id,
            req.authUser!.id,
            parsed.data.decision,
            parsed.data.note,
          ],
        );
        if (parsed.data.decision === "approved") {
          if (payment.duration_days > 0)
            await client.query(
              `INSERT INTO subscriptions(
                 user_id,plan_id,status,starts_at,ends_at,
                 entitlement_snapshot,purchased_price_toman
               ) VALUES(
                 $1,$2,'active',now(),now()+($3||' days')::interval,
                 jsonb_build_object(
                   'durationDays',$3,
                   'analysisCredits',$4,
                   'unlimitedAnalyses',$5,
                   'titleFa',$6,
                   'features',$7::jsonb
                 ),$8
               )`,
              [
                payment.user_id,
                payment.plan_id,
                payment.duration_days,
                payment.plan_credits,
                payment.unlimited_analyses,
                payment.plan_title_fa,
                JSON.stringify(payment.plan_features ?? []),
                payment.amount_toman,
              ],
            );
          const credits = Number(
            payment.plan_credits ?? payment.campaign_credits ?? 0,
          );
          if (credits > 0) {
            const c = await client.query(
              `UPDATE analysis_credits SET balance=balance+$2,updated_at=now() WHERE user_id=$1 RETURNING balance`,
              [payment.user_id, credits],
            );
            await client.query(
              `INSERT INTO credit_ledger(user_id,delta,balance_after,reason,reference_type,reference_id,idempotency_key) VALUES($1,$2,$3,$4,$5,$6,$7)`,
              [
                payment.user_id,
                credits,
                c.rows[0].balance,
                payment.promotion_id ? "campaign" : "purchase",
                payment.promotion_id ? "promotion" : "payment",
                payment.promotion_id ?? payment.id,
                `payment:${payment.id}`,
              ],
            );
          }
          if (payment.promotion_id)
            await client.query(
              `INSERT INTO promotion_redemptions(promotion_id,user_id,payment_id,credits_awarded) VALUES($1,$2,$3,$4)`,
              [
                payment.promotion_id,
                payment.user_id,
                payment.id,
                Number(payment.campaign_credits ?? 0),
              ],
            );
          const referral = await client.query(
            `SELECT id,referrer_user_id FROM referrals WHERE referred_user_id=$1 AND status='pending' FOR UPDATE`,
            [payment.user_id],
          );
          if (referral.rows[0]) {
            const reward = 5;
            const c = await client.query(
              `UPDATE analysis_credits SET balance=balance+$2,updated_at=now() WHERE user_id=$1 RETURNING balance`,
              [referral.rows[0].referrer_user_id, reward],
            );
            await client.query(
              `INSERT INTO credit_ledger(user_id,delta,balance_after,reason,reference_type,reference_id,idempotency_key) VALUES($1,$2,$3,'referral','referral',$4,$5)`,
              [
                referral.rows[0].referrer_user_id,
                reward,
                c.rows[0].balance,
                referral.rows[0].id,
                `referral:${referral.rows[0].id}`,
              ],
            );
            await client.query(
              `UPDATE referrals SET status='rewarded',rewarded_at=now() WHERE id=$1`,
              [referral.rows[0].id],
            );
          }
        }
        return { paymentId: payment.id, status: parsed.data.decision };
      });
      await audit(
        req.authUser!.id,
        "payment.decision",
        "payment",
        req.params.id,
        req.ip || "127.0.0.1",
        { decision: parsed.data.decision },
      );
      res.json({ success: true, result });
    }),
  );
  app.patch(
    "/api/admin/users/:id",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const p = z
        .object({
          status: z.enum(["active", "suspended"]).optional(),
          role: z.enum(["user", "admin"]).optional(),
        })
        .refine((v) => v.status || v.role)
        .safeParse(req.body);
      if (!p.success)
        return res
          .status(400)
          .json({ success: false, error: "تغییر معتبر نیست." });
      const r = await pool.query(
        `UPDATE users SET status=coalesce($2,status),role_id=coalesce((SELECT id FROM roles WHERE code=$3),role_id),updated_at=now() WHERE id=$1 RETURNING id,status`,
        [req.params.id, p.data.status, p.data.role],
      );
      if (!r.rowCount) return res.status(404).json({ success: false });
      await audit(
        req.authUser!.id,
        "user.update",
        "user",
        req.params.id,
        req.ip || "127.0.0.1",
        p.data,
      );
      res.json({ success: true, user: r.rows[0] });
    }),
  );
  app.post(
    "/api/admin/users/:id/credits",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const p = z
        .object({
          delta: z
            .number()
            .int()
            .min(-10000)
            .max(10000)
            .refine((x) => x !== 0),
          note: z.string().min(3).max(300),
        })
        .safeParse(req.body);
      if (!p.success)
        return res
          .status(400)
          .json({ success: false, error: "تغییر اعتبار معتبر نیست." });
      const key = `admin:${req.authUser!.id}:${crypto.randomUUID()}`;
      const balance = await withTransaction(async (c) => {
        const r = await c.query(
          `UPDATE analysis_credits SET balance=balance+$2,updated_at=now() WHERE user_id=$1 AND balance+$2>=0 RETURNING balance`,
          [req.params.id, p.data.delta],
        );
        if (!r.rowCount) throw new Error("INVALID_BALANCE");
        await c.query(
          `INSERT INTO credit_ledger(user_id,delta,balance_after,reason,reference_type,reference_id,idempotency_key) VALUES($1,$2,$3,'admin_adjustment','admin',$4,$5)`,
          [
            req.params.id,
            p.data.delta,
            r.rows[0].balance,
            req.authUser!.id,
            key,
          ],
        );
        return r.rows[0].balance;
      });
      await audit(
        req.authUser!.id,
        "credit.adjust",
        "user",
        req.params.id,
        req.ip || "127.0.0.1",
        { delta: p.data.delta, note: p.data.note },
      );
      res.json({ success: true, balance });
    }),
  );
  app.get(
    "/api/admin/users/:id/activity",
    requireUser,
    requireAdmin,
    asyncRoute(async (req, res) => {
      const [ledger, analyses, attempts, subscriptions] = await Promise.all([
        pool.query(
          `SELECT id,delta,balance_after,reason,reference_type,created_at FROM credit_ledger WHERE user_id=$1 ORDER BY created_at DESC LIMIT 50`,
          [req.params.id],
        ),
        pool.query(
          `SELECT id,symbol,report_mode,created_at FROM analysis_history WHERE user_id=$1 ORDER BY created_at DESC LIMIT 50`,
          [req.params.id],
        ),
        pool.query(
          `SELECT id,symbol,report_mode,success,error_code,created_at FROM analysis_attempts WHERE user_id=$1 ORDER BY created_at DESC LIMIT 50`,
          [req.params.id],
        ),
        pool.query(
          `SELECT s.id,s.status,s.starts_at,s.ends_at,p.code,p.title_fa FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.user_id=$1 ORDER BY s.created_at DESC LIMIT 50`,
          [req.params.id],
        ),
      ]);
      res.json({
        success: true,
        ledger: ledger.rows,
        analyses: analyses.rows,
        attempts: attempts.rows,
        subscriptions: subscriptions.rows,
      });
    }),
  );
  app.get(
    "/api/account/ledger",
    requireUser,
    asyncRoute(async (req, res) => {
      const r = await pool.query(
        `SELECT id,delta,balance_after,reason,reference_type,created_at FROM credit_ledger WHERE user_id=$1 ORDER BY created_at DESC LIMIT 100`,
        [req.authUser!.id],
      );
      res.json({ success: true, ledger: r.rows });
    }),
  );
  app.get(
    "/api/admin/plans",
    requireUser,
    requireAdmin,
    asyncRoute(async (_req, res) => {
      const r = await pool.query(`SELECT * FROM plans ORDER BY duration_days`);
      res.json({ success: true, plans: r.rows });
    }),
  );
  const planSchema = z
    .object({
      code: z.string().regex(/^[a-z0-9][a-z0-9_-]{1,47}$/),
      titleFa: z.string().min(2).max(80),
      descriptionFa: z.string().max(500).nullable().optional(),
      durationDays: z.number().int().min(0).max(5000),
      priceToman: z.number().int().min(0),
      analysisCredits: z.number().int().min(0).max(100000),
      unlimitedAnalyses: z.boolean().default(false),
      features: z.array(z.string().min(1).max(120)).max(30).default([]),
      active: z.boolean(),
      displayOrder: z.number().int().min(-10000).max(10000).default(0),
      discount: z.record(z.string(), z.unknown()).nullable().optional(),
      saleStartsAt: z.string().datetime().nullable().optional(),
      saleEndsAt: z.string().datetime().nullable().optional(),
      publiclyVisible: z.boolean().default(true),
    })
    .refine(
      (v) =>
        !v.saleStartsAt ||
        !v.saleEndsAt ||
        new Date(v.saleEndsAt) > new Date(v.saleStartsAt),
    );
  app.post(
    "/api/admin/plans",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const parsed = planSchema.safeParse(req.body);
      if (!parsed.success)
        return res
          .status(400)
          .json({ success: false, error: "تنظیمات پلن معتبر نیست." });
      const v = parsed.data;
      const r = await pool.query(
        `INSERT INTO plans(
           code,title_fa,description_fa,duration_days,price_toman,
           analysis_credits,unlimited_analyses,features,active,display_order,
           discount,sale_starts_at,sale_ends_at,publicly_visible
         ) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
         RETURNING *`,
        [
          v.code,
          v.titleFa,
          v.descriptionFa ?? null,
          v.durationDays,
          v.priceToman,
          v.analysisCredits,
          v.unlimitedAnalyses,
          v.features,
          v.active,
          v.displayOrder,
          v.discount ?? null,
          v.saleStartsAt ?? null,
          v.saleEndsAt ?? null,
          v.publiclyVisible,
        ],
      );
      await audit(
        req.authUser!.id,
        "plan.create",
        "plan",
        r.rows[0].id,
        req.ip || "127.0.0.1",
      );
      res.status(201).json({ success: true, plan: r.rows[0] });
    }),
  );
  app.patch(
    "/api/admin/plans/:id",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const p = planSchema.omit({ code: true }).safeParse(req.body);
      if (!p.success)
        return res
          .status(400)
          .json({ success: false, error: "تنظیمات پلن معتبر نیست." });
      const v = p.data;
      const r = await pool.query(
        `UPDATE plans SET
           title_fa=$2,description_fa=$3,duration_days=$4,price_toman=$5,
           analysis_credits=$6,unlimited_analyses=$7,features=$8,active=$9,
           display_order=$10,discount=$11,sale_starts_at=$12,sale_ends_at=$13,
           publicly_visible=$14,updated_at=now()
         WHERE id=$1 RETURNING *`,
        [
          req.params.id,
          v.titleFa,
          v.descriptionFa ?? null,
          v.durationDays,
          v.priceToman,
          v.analysisCredits,
          v.unlimitedAnalyses,
          v.features,
          v.active,
          v.displayOrder,
          v.discount ?? null,
          v.saleStartsAt ?? null,
          v.saleEndsAt ?? null,
          v.publiclyVisible,
        ],
      );
      if (!r.rowCount) return res.status(404).json({ success: false });
      await audit(
        req.authUser!.id,
        "plan.update",
        "plan",
        req.params.id,
        req.ip || "127.0.0.1",
      );
      res.json({ success: true, plan: r.rows[0] });
    }),
  );
  const campaignSchema = z
    .object({
      code: z.string().regex(/^[A-Z0-9_-]{3,32}$/),
      titleFa: z.string().min(2).max(120),
      startsAt: z.string().datetime(),
      endsAt: z.string().datetime(),
      capacity: z.number().int().positive().nullable().optional(),
      creditAmount: z.number().int().min(0).max(100000),
      priceToman: z.number().int().min(0).nullable().optional(),
      active: z.boolean(),
      rules: z
        .object({
          audience: z.enum(["all", "new_users", "existing_users"]),
          perUser: z.literal(1),
        })
        .default({ audience: "all", perUser: 1 }),
    })
    .refine((v) => new Date(v.endsAt) > new Date(v.startsAt));
  app.get(
    "/api/admin/campaigns",
    requireUser,
    requireAdmin,
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT * FROM promotions ORDER BY starts_at DESC`,
      );
      res.json({ success: true, campaigns: r.rows });
    }),
  );
  app.get(
    "/api/admin/referrals",
    requireUser,
    requireAdmin,
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT r.id,r.status,r.created_at,r.rewarded_at,referrer.mobile_e164 AS referrer_mobile,referred.mobile_e164 AS referred_mobile FROM referrals r JOIN users referrer ON referrer.id=r.referrer_user_id JOIN users referred ON referred.id=r.referred_user_id ORDER BY r.created_at DESC LIMIT 200`,
      );
      res.json({ success: true, referrals: r.rows });
    }),
  );
  app.post(
    "/api/admin/campaigns",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const p = campaignSchema.safeParse(req.body);
      if (!p.success)
        return res
          .status(400)
          .json({ success: false, error: "اطلاعات کمپین معتبر نیست." });
      const v = p.data;
      const r = await pool.query(
        `INSERT INTO promotions(code,title_fa,starts_at,ends_at,capacity,credit_amount,price_toman,active,rules) VALUES($1,$2,$3,$4,$5,$6,$7,$8,$9) RETURNING *`,
        [
          v.code,
          v.titleFa,
          v.startsAt,
          v.endsAt,
          v.capacity ?? null,
          v.creditAmount,
          v.priceToman ?? null,
          v.active,
          v.rules,
        ],
      );
      await audit(
        req.authUser!.id,
        "campaign.create",
        "campaign",
        r.rows[0].id,
        req.ip || "127.0.0.1",
      );
      res.status(201).json({ success: true, campaign: r.rows[0] });
    }),
  );
  app.patch(
    "/api/admin/campaigns/:id/status",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const p = z.object({ active: z.boolean() }).safeParse(req.body);
      if (!p.success) return res.status(400).json({ success: false });
      const r = await pool.query(
        `UPDATE promotions SET active=$2 WHERE id=$1 RETURNING *`,
        [req.params.id, p.data.active],
      );
      if (!r.rowCount) return res.status(404).json({ success: false });
      await audit(
        req.authUser!.id,
        "campaign.status",
        "campaign",
        req.params.id,
        req.ip || "127.0.0.1",
        { active: p.data.active },
      );
      res.json({ success: true, campaign: r.rows[0] });
    }),
  );
  app.get(
    "/api/admin/settings",
    requireUser,
    requireAdmin,
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT key,value,is_public,updated_at FROM system_settings ORDER BY key`,
      );
      res.json({ success: true, settings: r.rows });
    }),
  );
  app.put(
    "/api/admin/reference-rates",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const referenceSchema = z.object({
        percent: z.number().min(0).max(1000),
        source: z.string().url().refine((value) => value.startsWith("https://")),
        asOf: z.string().date(),
      });
      const parsed = z
        .object({
          inflation: referenceSchema,
          bankDeposit: referenceSchema.optional(),
        })
        .safeParse(req.body);
      if (!parsed.success)
        return res.status(400).json({
          success: false,
          error: "نرخ، منبع یا تاریخ مرجع معتبر نیست.",
        });
      const entries: Array<[string, unknown]> = [
        ["inflation_rate_percent", parsed.data.inflation.percent],
        ["inflation_rate_source", parsed.data.inflation.source],
        ["inflation_rate_as_of", parsed.data.inflation.asOf],
      ];
      if (parsed.data.bankDeposit)
        entries.push(
          ["bank_deposit_rate_percent", parsed.data.bankDeposit.percent],
          ["bank_deposit_rate_source", parsed.data.bankDeposit.source],
          ["bank_deposit_rate_as_of", parsed.data.bankDeposit.asOf],
        );
      await withTransaction(async (client) => {
        for (const [key, value] of entries)
          await client.query(
            `INSERT INTO system_settings(key,value,is_public,updated_by)
             VALUES($1,$2,true,$3)
             ON CONFLICT(key) DO UPDATE SET value=excluded.value,is_public=true,
               updated_by=excluded.updated_by,updated_at=now()`,
            [key, value, req.authUser!.id],
          );
      });
      await audit(
        req.authUser!.id,
        "reference_rates.update",
        "system_settings",
        "economic_references",
        req.ip || "127.0.0.1",
        { keys: entries.map(([key]) => key) },
      );
      res.json({ success: true, updated: entries.map(([key]) => key) });
    }),
  );
  app.put(
    "/api/admin/settings/:key",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const key = z
        .string()
        .regex(/^[a-z][a-z0-9_.-]{1,63}$/)
        .safeParse(req.params.key);
      const body = z
        .object({ value: z.unknown(), isPublic: z.boolean().default(false) })
        .safeParse(req.body);
      if (
        !key.success ||
        !body.success ||
        /secret|token|password|api.?key/i.test(key.data)
      )
        return res
          .status(400)
          .json({ success: false, error: "تنظیم معتبر نیست." });
      const r = await pool.query(
        `INSERT INTO system_settings(key,value,is_public,updated_by) VALUES($1,$2,$3,$4) ON CONFLICT(key) DO UPDATE SET value=excluded.value,is_public=excluded.is_public,updated_by=excluded.updated_by,updated_at=now() RETURNING key,value,is_public,updated_at`,
        [key.data, body.data.value, body.data.isPublic, req.authUser!.id],
      );
      await audit(
        req.authUser!.id,
        "setting.update",
        "setting",
        key.data,
        req.ip || "127.0.0.1",
      );
      res.json({ success: true, setting: r.rows[0] });
    }),
  );
  app.get(
    "/api/admin/sms",
    requireUser,
    requireAdmin,
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT id,purpose,status,error_code,created_at,left(mobile_e164,6)||'****'||right(mobile_e164,3) AS mobile_masked FROM sms_delivery_attempts ORDER BY created_at DESC LIMIT 200`,
      );
      res.json({
        success: true,
        otpPending: process.env.OTP_PENDING_APPROVAL === "true",
        sendingEnabled: process.env.SMS_ENABLED === "true",
        attempts: r.rows,
      });
    }),
  );
  app.get(
    "/api/admin/audit",
    requireUser,
    requireAdmin,
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT id,action,target_type,target_id,metadata,created_at FROM admin_audit_logs ORDER BY created_at DESC LIMIT 200`,
      );
      res.json({ success: true, logs: r.rows });
    }),
  );
}
