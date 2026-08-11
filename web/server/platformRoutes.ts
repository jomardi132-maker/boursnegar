import crypto from "crypto";
import type express from "express";
import { z } from "zod";
import { pool, withTransaction } from "./postgres";
import { requireAdmin, requireCsrf, requireUser } from "./auth";

const asyncRoute =
  (fn: express.RequestHandler): express.RequestHandler =>
  (req, res, next) =>
    Promise.resolve(fn(req, res, next)).catch(next);
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

export function installPlatformRoutes(app: express.Express) {
  app.get(
    "/api/plans",
    asyncRoute(async (_req, res) => {
      const r = await pool.query(
        `SELECT id,code,title_fa,duration_days,price_toman,analysis_credits FROM plans WHERE active ORDER BY duration_days`,
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
          `SELECT ps.*,p.analysis_credits AS plan_credits,p.duration_days,pr.credit_amount AS campaign_credits,pr.active AS campaign_active,pr.starts_at,pr.ends_at,pr.capacity,pr.rules,u.created_at AS user_created_at FROM payment_submissions ps JOIN users u ON u.id=ps.user_id LEFT JOIN plans p ON p.id=ps.plan_id LEFT JOIN promotions pr ON pr.id=ps.promotion_id WHERE ps.id=$1 FOR UPDATE OF ps`,
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
              `INSERT INTO subscriptions(user_id,plan_id,status,starts_at,ends_at) VALUES($1,$2,'active',now(),now()+($3||' days')::interval)`,
              [payment.user_id, payment.plan_id, payment.duration_days],
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
  app.patch(
    "/api/admin/plans/:id",
    requireUser,
    requireAdmin,
    requireCsrf,
    asyncRoute(async (req, res) => {
      const p = z
        .object({
          titleFa: z.string().min(2).max(80),
          durationDays: z.number().int().min(0).max(5000),
          priceToman: z.number().int().min(0),
          analysisCredits: z.number().int().min(0).max(100000),
          active: z.boolean(),
        })
        .safeParse(req.body);
      if (!p.success)
        return res
          .status(400)
          .json({ success: false, error: "تنظیمات پلن معتبر نیست." });
      const v = p.data;
      const r = await pool.query(
        `UPDATE plans SET title_fa=$2,duration_days=$3,price_toman=$4,analysis_credits=$5,active=$6,updated_at=now() WHERE id=$1 RETURNING *`,
        [
          req.params.id,
          v.titleFa,
          v.durationDays,
          v.priceToman,
          v.analysisCredits,
          v.active,
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
