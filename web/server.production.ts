import crypto from "crypto";
import fs from "fs";
import path from "path";
import express from "express";
import cookieParser from "cookie-parser";
import helmet from "helmet";
import multer from "multer";
import { z } from "zod";
import dotenv from "dotenv";
import { createServer as createViteServer } from "vite";
import {
  generateRealHealthCard,
  UpstreamAnalysisError,
} from "./server/realAnalysisAdapter";
import { pool, withTransaction } from "./server/postgres";
import {
  authenticate,
  createPasswordReset,
  createOtp,
  loginWithEmail,
  normalizeEmail,
  normalizeIranMobile,
  registerWithEmail,
  requireAdmin,
  requireCsrf,
  requireUser,
  revokeSession,
  setSessionCookie,
  resetPassword,
  verifyOtp,
} from "./server/auth";
import { installPlatformRoutes } from "./server/platformRoutes";
import { mailDeliveryReady, sendPasswordResetEmail } from "./server/mailer";

dotenv.config({ quiet: true });
const app = express();
const PORT = Number(process.env.PORT || 3000);
const isProduction = process.env.NODE_ENV === "production";
app.disable("x-powered-by");
app.set("trust proxy", 1);
app.use(
  helmet({
    contentSecurityPolicy: {
      directives: {
        defaultSrc: ["'self'"],
        scriptSrc: ["'self'"],
        styleSrc: ["'self'", "'unsafe-inline'"],
        imgSrc: ["'self'", "data:"],
        connectSrc: ["'self'"],
      },
    },
    crossOriginEmbedderPolicy: false,
  }),
);
app.use(express.json({ limit: "256kb" }));
app.use(express.urlencoded({ extended: false, limit: "64kb" }));
app.use(cookieParser());
app.use(authenticate);

type Bucket = { count: number; resetAt: number };
const buckets = new Map<string, Bucket>();
function rateLimit(
  name: string,
  limit: number,
  windowMs: number,
): express.RequestHandler {
  return (req, res, next) => {
    const key = `${name}:${req.ip}`;
    const now = Date.now();
    const bucket = buckets.get(key);
    if (!bucket || bucket.resetAt <= now)
      buckets.set(key, { count: 1, resetAt: now + windowMs });
    else if (++bucket.count > limit)
      return res.status(429).json({
        success: false,
        error: "تعداد درخواست‌ها بیش از حد مجاز است. کمی بعد دوباره تلاش کنید.",
      });
    next();
  };
}
const asyncRoute =
  (handler: express.RequestHandler): express.RequestHandler =>
  (req, res, next) =>
    Promise.resolve(handler(req, res, next)).catch(next);
const otpRequestSchema = z.object({ mobile: z.string().min(10).max(20) });
const otpVerifySchema = z.object({
  requestId: z.string().uuid(),
  mobile: z.string(),
  code: z.string().regex(/^\d{6}$/),
  referralCode: z.string().max(16).optional(),
});
const emailSchema = z.string().trim().email().max(254);
const passwordSchema = z.string().min(12).max(128);
const registerSchema = z.object({
  email: emailSchema,
  password: passwordSchema,
  referralCode: z.string().trim().max(16).optional(),
});
const loginSchema = z.object({ email: emailSchema, password: z.string().min(1).max(128) });
const forgotSchema = z.object({ email: emailSchema });
const resetSchema = z.object({ token: z.string().min(32).max(128), password: passwordSchema });
const analyzeSchema = z.object({
  query: z.string().min(1).max(32),
  reportMode: z.enum(["audited", "latest_codal"]).default("audited"),
});

async function auditAuth(action: string, ip: string, targetId?: string, metadata: Record<string, unknown> = {}) {
  await pool.query(
    `INSERT INTO admin_audit_logs(admin_user_id,action,target_type,target_id,metadata,ip) VALUES(NULL,$1,'auth',$2,$3,$4::inet)`,
    [action, targetId ?? null, metadata, ip],
  );
}

async function recordAnalysisAttempt(
  userId: string,
  symbol: string,
  reportMode: string,
  success: boolean,
  errorCode?: string,
) {
  await pool.query(
    `INSERT INTO analysis_attempts(user_id,symbol,report_mode,success,error_code) VALUES($1,$2,$3,$4,$5)`,
    [userId, symbol, reportMode, success, errorCode?.slice(0, 80) ?? null],
  );
}

async function sendOtp(mobile: string, code: string): Promise<string> {
  if (process.env.OTP_GATEWAY === "mock") {
    if (isProduction)
      throw new Error("Mock OTP gateway is forbidden in production");
    return "mock";
  }
  if (
    process.env.OTP_PENDING_APPROVAL === "true" ||
    process.env.OTP_ENABLED !== "true" ||
    process.env.OTP_GATEWAY !== "kavenegar"
  )
    throw new Error("OTP_DISABLED");
  const apiKey = process.env.KAVENEGAR_API_KEY;
  const template = process.env.KAVENEGAR_OTP_TEMPLATE;
  if (!apiKey || !template) throw new Error("OTP gateway is not configured");
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 8_000);
  try {
    const response = await fetch(
      `https://api.kavenegar.com/v1/${encodeURIComponent(apiKey)}/verify/lookup.json?receptor=${encodeURIComponent(`0${mobile.slice(3)}`)}&token=${code}&template=${encodeURIComponent(template)}`,
      { signal: controller.signal },
    );
    if (!response.ok) throw new Error("OTP delivery failed");
    const payload: any = await response.json();
    if (payload?.return?.status !== 200)
      throw new Error("OTP_PROVIDER_REJECTED");
    return String(payload.entries?.[0]?.messageid || "");
  } finally {
    clearTimeout(timeout);
  }
}

app.get("/healthz", (_req, res) => res.json({ status: "ok", auth: "email_password" }));
app.get("/api/health", (_req, res) =>
  res.json({ status: "ok", auth: "email_password" }),
);
app.get(
  "/readyz",
  asyncRoute(async (_req, res) => {
    await pool.query("SELECT 1");
    res.json({ status: "ready", auth: "email_password", mail: mailDeliveryReady() ? "ready" : "not_configured" });
  }),
);
app.post(
  "/api/auth/register",
  rateLimit("register", 5, 15 * 60_000),
  asyncRoute(async (req, res) => {
    const parsed = registerSchema.safeParse(req.body);
    const email = parsed.success ? normalizeEmail(parsed.data.email) : null;
    if (!parsed.success || !email)
      return res.status(400).json({ success: false, error: "ایمیل یا رمز عبور معتبر نیست. رمز باید حداقل ۱۲ نویسه باشد." });
    try {
      const result = await registerWithEmail(email, parsed.data.password, req.ip || "127.0.0.1", req.header("user-agent") || "", parsed.data.referralCode);
      setSessionCookie(res, result.sessionToken);
      res.status(201).json({ success: true, csrfToken: result.csrfToken, user: result.user });
    } catch (error) {
      if ((error as { code?: string })?.code === "23505")
        return res.status(409).json({ success: false, error: "امکان ثبت این حساب وجود ندارد. اگر قبلاً ثبت‌نام کرده‌اید، وارد شوید." });
      throw error;
    }
  }),
);
app.post(
  "/api/auth/login",
  rateLimit("login", 10, 15 * 60_000),
  asyncRoute(async (req, res) => {
    const parsed = loginSchema.safeParse(req.body);
    const email = parsed.success ? normalizeEmail(parsed.data.email) : null;
    if (!parsed.success || !email)
      return res.status(401).json({ success: false, error: "ایمیل یا رمز عبور نادرست است." });
    try {
      const result = await loginWithEmail(email, parsed.data.password, req.ip || "127.0.0.1", req.header("user-agent") || "");
      setSessionCookie(res, result.sessionToken);
      res.json({ success: true, csrfToken: result.csrfToken, user: result.user });
    } catch (error) {
      if (error instanceof Error && error.message === "INVALID_CREDENTIALS")
        return res.status(401).json({ success: false, error: "ایمیل یا رمز عبور نادرست است." });
      throw error;
    }
  }),
);
app.post(
  "/api/auth/password/forgot",
  rateLimit("forgot-password", 5, 30 * 60_000),
  asyncRoute(async (req, res) => {
    const parsed = forgotSchema.safeParse(req.body);
    const email = parsed.success ? normalizeEmail(parsed.data.email) : null;
    const requestIp = req.ip || "127.0.0.1";
    await auditAuth("password_reset_requested", requestIp, undefined, { mailReady: mailDeliveryReady() });
    if (email && mailDeliveryReady()) {
      const token = await createPasswordReset(email, requestIp);
      if (token) {
        const publicOrigin = process.env.PUBLIC_ORIGIN || "https://boursnegar.ir";
        try {
          await sendPasswordResetEmail(email, `${publicOrigin}/?reset-token=${encodeURIComponent(token)}`);
          await auditAuth("password_reset_dispatched", requestIp, undefined, { delivery: "submitted" });
        } catch {
          await auditAuth("password_reset_delivery_failed", requestIp, undefined, { delivery: "failed" });
        }
      }
    }
    res.status(202).json({ success: true, message: "اگر حسابی با این ایمیل وجود داشته باشد، لینک بازیابی برای آن ارسال می‌شود." });
  }),
);
app.post(
  "/api/auth/password/reset",
  rateLimit("reset-password", 8, 30 * 60_000),
  asyncRoute(async (req, res) => {
    const parsed = resetSchema.safeParse(req.body);
    if (!parsed.success)
      return res.status(400).json({ success: false, error: "لینک بازیابی یا رمز جدید معتبر نیست." });
    try {
      const userId = await resetPassword(parsed.data.token, parsed.data.password);
      await auditAuth("password_reset_completed", req.ip || "127.0.0.1", userId);
      res.json({ success: true, message: "رمز عبور تغییر کرد. اکنون با رمز جدید وارد شوید." });
    } catch (error) {
      if (error instanceof Error && error.message === "INVALID_RESET_TOKEN")
        return res.status(400).json({ success: false, error: "لینک بازیابی نامعتبر یا منقضی شده است." });
      throw error;
    }
  }),
);
app.post(
  "/api/auth/otp/request",
  (_req, res) =>
    res.status(410).json({
      success: false,
      error: "ورود پیامکی حذف شده است. از ایمیل و رمز عبور استفاده کنید.",
    }),
);
app.post(
  "/api/auth/otp/request/legacy-disabled",
  rateLimit("otp", 5, 600_000),
  asyncRoute(async (req, res) => {
    const parsed = otpRequestSchema.safeParse(req.body);
    const mobile = parsed.success
      ? normalizeIranMobile(parsed.data.mobile)
      : null;
    if (!mobile)
      return res
        .status(400)
        .json({ success: false, error: "شماره موبایل معتبر نیست." });
    const otp = await createOtp(mobile, req.ip || "127.0.0.1");
    try {
      const providerId = await sendOtp(mobile, otp.code);
      await pool.query(
        `INSERT INTO sms_delivery_attempts(mobile_e164,purpose,provider_message_id,status,deduplication_key) VALUES($1,'otp',$2,'submitted',$3)`,
        [mobile, providerId, `otp:${otp.requestId}`],
      );
    } catch (error) {
      await pool.query(
        `UPDATE otp_requests SET consumed_at=now() WHERE id=$1`,
        [otp.requestId],
      );
      await pool
        .query(
          `INSERT INTO sms_delivery_attempts(mobile_e164,purpose,status,error_code,deduplication_key) VALUES($1,'otp','failed',$2,$3) ON CONFLICT(deduplication_key) DO NOTHING`,
          [
            mobile,
            error instanceof Error ? error.message.slice(0, 80) : "UNKNOWN",
            `otp:${otp.requestId}`,
          ],
        )
        .catch(() => {});
      throw error;
    }
    res
      .status(202)
      .json({ success: true, requestId: otp.requestId, expiresInSeconds: 120 });
  }),
);
app.post(
  "/api/auth/otp/verify",
  (_req, res) =>
    res.status(410).json({
      success: false,
      error: "ورود پیامکی حذف شده است. از ایمیل و رمز عبور استفاده کنید.",
    }),
);
app.post(
  "/api/auth/otp/verify/legacy-disabled",
  rateLimit("verify", 10, 600_000),
  asyncRoute(async (req, res) => {
    const parsed = otpVerifySchema.safeParse(req.body);
    const mobile = parsed.success
      ? normalizeIranMobile(parsed.data.mobile)
      : null;
    if (!parsed.success || !mobile)
      return res
        .status(400)
        .json({ success: false, error: "اطلاعات ورود معتبر نیست." });
    try {
      const result = await verifyOtp(
        parsed.data.requestId,
        mobile,
        parsed.data.code,
        req.ip || "127.0.0.1",
        req.header("user-agent") || "",
        parsed.data.referralCode,
      );
      setSessionCookie(res, result.sessionToken);
      res.json({
        success: true,
        csrfToken: result.csrfToken,
        user: result.user,
      });
    } catch {
      res.status(400).json({
        success: false,
        error: "کد واردشده معتبر نیست یا منقضی شده است.",
      });
    }
  }),
);
app.get("/api/auth/me", requireUser, (req, res) =>
  res.json({ success: true, user: req.authUser }),
);
app.post(
  "/api/auth/logout",
  requireUser,
  requireCsrf,
  asyncRoute(async (req, res) => {
    await revokeSession(req, res);
    res.json({ success: true });
  }),
);

app.post(
  "/api/analyze",
  rateLimit("analyze", 12, 60_000),
  requireUser,
  requireCsrf,
  asyncRoute(async (req, res) => {
    const parsed = analyzeSchema.safeParse(req.body);
    if (!parsed.success)
      return res
        .status(400)
        .json({ success: false, error: "نماد یا حالت گزارش معتبر نیست." });
    const symbol = parsed.data.query.trim().replace(/^نماد\s+/, "");
    if (!/^[\u0600-\u06FFa-zA-Z0-9‌_-]{1,32}$/.test(symbol))
      return res
        .status(400)
        .json({ success: false, error: "نماد واردشده معتبر نیست." });
    const key = String(
      req.header("idempotency-key") || crypto.randomUUID(),
    ).slice(0, 128);
    const ledgerKey = `analysis:${req.authUser!.id}:${key}`;
    const replay = await pool.query(
      `SELECT h.id,h.symbol,h.report_mode,h.result,h.created_at,c.balance AS remaining_credits
       FROM credit_ledger l
       JOIN analysis_history h ON h.id::text=l.reference_id
       JOIN analysis_credits c ON c.user_id=l.user_id
       WHERE l.user_id=$1 AND l.idempotency_key=$2`,
      [req.authUser!.id, ledgerKey],
    );
    if (replay.rows[0]) {
      const previous = replay.rows[0];
      if (
        previous.symbol !== symbol ||
        previous.report_mode !== parsed.data.reportMode
      )
        return res.status(409).json({
          success: false,
          error: "این کلید تکرار قبلاً برای درخواست دیگری استفاده شده است.",
        });
      return res.json({
        success: true,
        replayed: true,
        data: previous.result,
        analysis: {
          id: previous.id,
          created_at: previous.created_at,
          remainingCredits: previous.remaining_credits,
        },
      });
    }
    try {
      const data = await generateRealHealthCard(symbol, parsed.data.reportMode);
      const saved = await withTransaction(async (client) => {
        const existing = await client.query(
          `SELECT h.id,h.symbol,h.report_mode,h.result,h.created_at,c.balance AS remaining_credits
           FROM credit_ledger l
           JOIN analysis_history h ON h.id::text=l.reference_id
           JOIN analysis_credits c ON c.user_id=l.user_id
           WHERE l.user_id=$1 AND l.idempotency_key=$2`,
          [req.authUser!.id, ledgerKey],
        );
        if (existing.rows[0]) {
          const previous = existing.rows[0];
          if (
            previous.symbol !== symbol ||
            previous.report_mode !== parsed.data.reportMode
          )
            throw new Error("IDEMPOTENCY_CONFLICT");
          return {
            id: previous.id,
            created_at: previous.created_at,
            remainingCredits: previous.remaining_credits,
            replayed: true,
            replayData: previous.result,
          };
        }
        const credit = await client.query(
          `SELECT balance FROM analysis_credits WHERE user_id=$1 FOR UPDATE`,
          [req.authUser!.id],
        );
        const balance = credit.rows[0]?.balance ?? 0;
        if (balance < 1) throw new Error("NO_CREDIT");
        const history = await client.query(
          `INSERT INTO analysis_history(user_id,symbol,report_mode,result,source_metadata) VALUES($1,$2,$3,$4,$5) RETURNING id,created_at`,
          [
            req.authUser!.id,
            symbol,
            parsed.data.reportMode,
            data,
            { source: "BrsApi/Codal", reportDate: data.header.reportDate },
          ],
        );
        await client.query(
          `UPDATE analysis_credits SET balance=balance-1,updated_at=now() WHERE user_id=$1`,
          [req.authUser!.id],
        );
        await client.query(
          `INSERT INTO credit_ledger(user_id,delta,balance_after,reason,reference_type,reference_id,idempotency_key) VALUES($1,-1,$2,'analysis','analysis_history',$3,$4)`,
          [
            req.authUser!.id,
            balance - 1,
            history.rows[0].id,
            ledgerKey,
          ],
        );
        return { ...history.rows[0], remainingCredits: balance - 1 };
      });
      await recordAnalysisAttempt(
        req.authUser!.id,
        symbol,
        parsed.data.reportMode,
        true,
      );
      res.json({
        success: true,
        replayed: Boolean(saved.replayed),
        data: saved.replayData ?? data,
        analysis: {
          id: saved.id,
          created_at: saved.created_at,
          remainingCredits: saved.remainingCredits,
        },
      });
    } catch (error) {
      await recordAnalysisAttempt(
        req.authUser!.id,
        symbol,
        parsed.data.reportMode,
        false,
        error instanceof Error ? error.message : "UNKNOWN",
      );
      throw error;
    }
  }),
);
app.get(
  "/api/account/analyses",
  requireUser,
  asyncRoute(async (req, res) => {
    const result = await pool.query(
      `SELECT id,symbol,report_mode,result,created_at FROM analysis_history WHERE user_id=$1 ORDER BY created_at DESC LIMIT 100`,
      [req.authUser!.id],
    );
    res.json({ success: true, analyses: result.rows });
  }),
);
app.get(
  "/api/account/credits",
  requireUser,
  asyncRoute(async (req, res) => {
    const result = await pool.query(
      `SELECT balance FROM analysis_credits WHERE user_id=$1`,
      [req.authUser!.id],
    );
    const ledger = await pool.query(
      `SELECT id,delta,balance_after,reason,created_at FROM credit_ledger WHERE user_id=$1 ORDER BY created_at DESC LIMIT 50`,
      [req.authUser!.id],
    );
    res.json({
      success: true,
      balance: result.rows[0]?.balance ?? 0,
      ledger: ledger.rows,
    });
  }),
);

const uploadDir = path.resolve(
  process.env.UPLOAD_DIR || path.join(process.cwd(), "uploads"),
);
fs.mkdirSync(uploadDir, { recursive: true });
const upload = multer({
  storage: multer.diskStorage({
    destination: uploadDir,
    filename: (_req, file, cb) =>
      cb(
        null,
        `${crypto.randomUUID()}${file.mimetype === "application/pdf" ? ".pdf" : file.mimetype === "image/png" ? ".png" : ".jpg"}`,
      ),
  }),
  limits: { fileSize: 4 * 1024 * 1024, files: 1 },
  fileFilter: (_req, file, cb) =>
    cb(
      null,
      ["image/jpeg", "image/png", "application/pdf"].includes(file.mimetype),
    ),
});
app.post(
  "/api/payments",
  rateLimit("upload", 5, 3_600_000),
  requireUser,
  requireCsrf,
  upload.single("receipt"),
  asyncRoute(async (req, res) => {
    if (!req.file)
      return res
        .status(400)
        .json({ success: false, error: "رسید معتبر لازم است." });
    const signature = fs.readFileSync(req.file.path).subarray(0, 8);
    const validSignature =
      req.file.mimetype === "application/pdf"
        ? signature.subarray(0, 5).toString() === "%PDF-"
        : req.file.mimetype === "image/png"
          ? signature.equals(Buffer.from([137, 80, 78, 71, 13, 10, 26, 10]))
          : signature[0] === 255 &&
            signature[1] === 216 &&
            signature[2] === 255;
    if (!validSignature) {
      fs.unlink(req.file.path, () => {});
      return res.status(400).json({
        success: false,
        error: "محتوای فایل رسید با نوع اعلام‌شده مطابقت ندارد.",
      });
    }
    const body = z
      .object({
        planId: z.string().uuid().optional(),
        campaignId: z.string().uuid().optional(),
        amountToman: z.coerce.number().int().positive(),
        trackingNumber: z.string().min(4).max(80),
        paidAt: z.string().datetime(),
      })
      .refine((v) => Boolean(v.planId) !== Boolean(v.campaignId))
      .safeParse(req.body);
    if (!body.success) {
      fs.unlink(req.file.path, () => {});
      return res
        .status(400)
        .json({ success: false, error: "اطلاعات پرداخت معتبر نیست." });
    }
    const offer = body.data.planId
      ? await pool.query(`SELECT price_toman,active FROM plans WHERE id=$1`, [
          body.data.planId,
        ])
      : await pool.query(
          `SELECT p.price_toman,p.active,p.starts_at,p.ends_at,p.capacity,p.rules,(SELECT count(*) FROM promotion_redemptions WHERE promotion_id=p.id) AS used,u.created_at AS user_created_at FROM promotions p CROSS JOIN users u WHERE p.id=$1 AND u.id=$2`,
          [body.data.campaignId, req.authUser!.id],
        );
    const selected = offer.rows[0];
    const campaignAvailable =
      !body.data.campaignId ||
      (selected &&
        new Date(selected.starts_at) <= new Date() &&
        new Date(selected.ends_at) > new Date() &&
        !(
          selected.rules?.audience === "new_users" &&
          new Date(selected.user_created_at) < new Date(selected.starts_at)
        ) &&
        !(
          selected.rules?.audience === "existing_users" &&
          new Date(selected.user_created_at) >= new Date(selected.starts_at)
        ) &&
        (selected.capacity == null ||
          Number(selected.used) < Number(selected.capacity)));
    if (
      !selected?.active ||
      !campaignAvailable ||
      Number(selected.price_toman) !== body.data.amountToman
    ) {
      fs.unlink(req.file.path, () => {});
      return res.status(400).json({
        success: false,
        error: "مبلغ پرداخت با پلن انتخاب‌شده مطابقت ندارد.",
      });
    }
    const result = await pool.query(
      `INSERT INTO payment_submissions(user_id,plan_id,promotion_id,amount_toman,tracking_number,paid_at,receipt_storage_key,receipt_mime) VALUES($1,$2,$3,$4,$5,$6,$7,$8) RETURNING id,status,created_at`,
      [
        req.authUser!.id,
        body.data.planId ?? null,
        body.data.campaignId ?? null,
        body.data.amountToman,
        body.data.trackingNumber,
        body.data.paidAt,
        req.file.filename,
        req.file.mimetype,
      ],
    );
    res.status(201).json({ success: true, payment: result.rows[0] });
  }),
);
app.use("/api/admin", rateLimit("admin", 120, 60_000));
app.get(
  "/api/admin/stats",
  requireUser,
  requireAdmin,
  asyncRoute(async (_req, res) => {
    const stats = await pool.query(
      `SELECT
        (SELECT count(*) FROM users) AS users,
        (SELECT count(*) FROM users WHERE created_at >= now()-interval '30 days') AS registrations_30d,
        (SELECT count(DISTINCT user_id) FROM (SELECT user_id,last_login_at FROM mobile_identities UNION ALL SELECT user_id,last_login_at FROM email_identities) identities WHERE last_login_at >= now()-interval '30 days') AS active_users_30d,
        (SELECT count(*) FROM analysis_attempts WHERE success) AS successful_analyses,
        (SELECT count(*) FROM analysis_attempts WHERE NOT success) AS failed_analyses,
        (SELECT count(*) FROM payment_submissions WHERE status='pending') AS pending_payments,
        (SELECT coalesce(sum(amount_toman),0) FROM payment_submissions WHERE status='approved') AS revenue_toman,
        (SELECT coalesce(-sum(delta),0) FROM credit_ledger WHERE delta<0 AND reason='analysis') AS credits_consumed`,
    );
    res.json({ success: true, stats: stats.rows[0] });
  }),
);
app.get(
  "/api/admin/users",
  requireUser,
  requireAdmin,
  asyncRoute(async (req, res) => {
    const q = String(req.query.q || "").slice(0, 32);
    const users = await pool.query(
      `SELECT u.id,u.mobile_e164,e.email,u.status,r.code AS role,coalesce(c.balance,0) AS credits,u.created_at FROM users u LEFT JOIN email_identities e ON e.user_id=u.id JOIN roles r ON r.id=u.role_id LEFT JOIN analysis_credits c ON c.user_id=u.id WHERE $1='' OR coalesce(u.mobile_e164,'') LIKE '%'||$1||'%' OR coalesce(e.email,'') ILIKE '%'||$1||'%' ORDER BY u.created_at DESC LIMIT 100`,
      [q],
    );
    res.json({ success: true, users: users.rows });
  }),
);
app.get(
  "/api/admin/payments/:id/receipt",
  requireUser,
  requireAdmin,
  asyncRoute(async (req, res) => {
    const found = await pool.query(
      `SELECT receipt_storage_key,receipt_mime FROM payment_submissions WHERE id=$1`,
      [req.params.id],
    );
    const receipt = found.rows[0];
    if (!receipt)
      return res.status(404).json({ success: false, error: "رسید پیدا نشد." });
    if (
      path.basename(receipt.receipt_storage_key) !== receipt.receipt_storage_key
    )
      return res
        .status(400)
        .json({ success: false, error: "مسیر رسید معتبر نیست." });
    res.setHeader("Cache-Control", "private, no-store");
    res.type(receipt.receipt_mime);
    res.sendFile(receipt.receipt_storage_key, { root: uploadDir });
  }),
);
installPlatformRoutes(app);

app.use("/api", (_req, res) =>
  res.status(404).json({ success: false, error: "مسیر API پیدا نشد." }),
);

const distPath = path.join(process.cwd(), "dist");
async function start() {
  if (!isProduction)
    app.use(
      (
        await createViteServer({
          server: { middlewareMode: true },
          appType: "spa",
        })
      ).middlewares,
    );
  else {
    app.use(express.static(distPath, { index: false, maxAge: "1h" }));
    app.get("*", (_req, res) =>
      res.sendFile(path.join(distPath, "index.html")),
    );
  }
  app.use(
    (
      error: unknown,
      _req: express.Request,
      res: express.Response,
      _next: express.NextFunction,
    ) => {
      const message = error instanceof Error ? error.message : "";
      const code = (error as any)?.code;
      const type = (error as any)?.type;
      const status =
        error instanceof SyntaxError && "body" in error
          ? 400
          : error instanceof UpstreamAnalysisError
            ? 502
            : message === "NO_CREDIT"
              ? 402
              : message === "NOT_FOUND"
                ? 404
                : [
                      "ALREADY_DECIDED",
                      "CAMPAIGN_UNAVAILABLE",
                      "INVALID_BALANCE",
                      "IDEMPOTENCY_CONFLICT",
                    ].includes(message)
                  ? 409
                  : message === "OTP_DISABLED"
                    ? 503
                    : type === "entity.parse.failed" ||
                        code === "LIMIT_FILE_SIZE"
                      ? 400
                      : 500;
      console.error("[request-error]", {
        name: error instanceof Error ? error.name : "UnknownError",
        status,
        ...(isProduction ? {} : { message }),
      });
      res.status(status).json({
        success: false,
        error:
          status === 402
            ? "اعتبار تحلیل شما کافی نیست."
            : status === 409
              ? "این عملیات قبلاً انجام شده یا دیگر قابل انجام نیست."
              : status === 503
                ? "ورود پیامکی در حال فعال‌سازی است."
                : status === 400
                  ? "ساختار درخواست یا فایل معتبر نیست."
                  : "در انجام درخواست خطایی رخ داد. دوباره تلاش کنید.",
      });
    },
  );
  app.listen(PORT, "127.0.0.1", () =>
    console.log(`[boursnegar] listening on 127.0.0.1:${PORT}`),
  );
}
start().catch((error) => {
  console.error(
    "[startup-error]",
    error instanceof Error ? error.message : "unknown",
  );
  process.exit(1);
});
export { app };
