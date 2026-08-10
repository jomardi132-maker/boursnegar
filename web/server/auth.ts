import crypto from 'crypto';
import type { Request, Response, NextFunction } from 'express';
import { pool, withTransaction } from './postgres';

const SESSION_COOKIE = 'boursnegar_session';
const SESSION_DAYS = 14;

export type AuthUser = { id: string; mobile: string; role: 'user' | 'admin'; credits: number };
declare global { namespace Express { interface Request { authUser?: AuthUser; sessionId?: string } } }

const required = (name: string): string => {
  const value = process.env[name];
  if (!value) throw new Error(`Missing required environment variable: ${name}`);
  return value;
};
const sha256 = (value: string) => crypto.createHash('sha256').update(value).digest('hex');
const randomToken = (bytes = 32) => crypto.randomBytes(bytes).toString('base64url');
const equalHex = (a: string, b: string) => a.length === b.length && crypto.timingSafeEqual(Buffer.from(a), Buffer.from(b));

export function normalizeIranMobile(raw: string): string | null {
  const digits = String(raw).replace(/[\s()-]/g, '').replace(/^00/, '+');
  let national = digits;
  if (national.startsWith('+98')) national = `0${national.slice(3)}`;
  else if (national.startsWith('98')) national = `0${national.slice(2)}`;
  if (!/^09\d{9}$/.test(national)) return null;
  return `+98${national.slice(1)}`;
}

export async function createOtp(mobile: string, ip: string): Promise<{ requestId: string; code: string }> {
  const pepper = required('OTP_PEPPER');
  const recent = await pool.query(
    `SELECT count(*)::int AS count FROM otp_requests WHERE (mobile_e164=$1 OR request_ip=$2::inet) AND created_at > now()-interval '10 minutes'`,
    [mobile, ip],
  );
  if (recent.rows[0].count >= 5) throw new Error('RATE_LIMITED');
  const code = crypto.randomInt(0, 1_000_000).toString().padStart(6, '0');
  const hash = sha256(`${mobile}:${code}:${pepper}`);
  const result = await pool.query(
    `INSERT INTO otp_requests(mobile_e164,code_hash,expires_at,request_ip) VALUES($1,$2,now()+interval '2 minutes',$3::inet) RETURNING id`,
    [mobile, hash, ip],
  );
  return { requestId: result.rows[0].id, code };
}

export async function verifyOtp(requestId: string, mobile: string, code: string, ip: string, userAgent: string, referralCode?: string) {
  return withTransaction(async (client) => {
    const found = await client.query(`SELECT * FROM otp_requests WHERE id=$1 FOR UPDATE`, [requestId]);
    const otp = found.rows[0];
    const supplied = sha256(`${mobile}:${code}:${required('OTP_PEPPER')}`);
    const valid = otp && otp.mobile_e164 === mobile && !otp.consumed_at && !otp.locked_until && new Date(otp.expires_at) > new Date() && otp.attempts < otp.max_attempts && equalHex(otp.code_hash, supplied);
    if (otp) {
      await client.query(`UPDATE otp_requests SET attempts=attempts+1, consumed_at=CASE WHEN $2 THEN now() ELSE consumed_at END, locked_until=CASE WHEN NOT $2 AND attempts+1>=max_attempts THEN now()+interval '15 minutes' ELSE locked_until END WHERE id=$1`, [requestId, valid]);
      await client.query(`INSERT INTO otp_attempts(otp_request_id,success,attempt_ip) VALUES($1,$2,$3::inet)`, [requestId, valid, ip]);
    }
    if (!valid) throw new Error('INVALID_OTP');

    let user = (await client.query(`SELECT u.id,u.mobile_e164,r.code AS role FROM users u JOIN roles r ON r.id=u.role_id WHERE u.mobile_e164=$1`, [mobile])).rows[0];
    let created = false;
    if (!user) {
      created = true;
      const referral = randomToken(8).replace(/[-_]/g, '').slice(0, 10).toUpperCase();
      user = (await client.query(`INSERT INTO users(mobile_e164,role_id,referral_code) SELECT $1,id,$2 FROM roles WHERE code='user' RETURNING id,mobile_e164,'user' AS role`, [mobile, referral])).rows[0];
      await client.query(`INSERT INTO mobile_identities(user_id,mobile_e164,verified_at,last_login_at) VALUES($1,$2,now(),now())`, [user.id, mobile]);
      await client.query(`INSERT INTO analysis_credits(user_id,balance) VALUES($1,5)`, [user.id]);
      await client.query(`INSERT INTO credit_ledger(user_id,delta,balance_after,reason,idempotency_key) VALUES($1,5,5,'welcome',$2)`, [user.id, `welcome:${user.id}`]);
      if (referralCode) await client.query(`INSERT INTO referrals(referrer_user_id,referred_user_id) SELECT id,$1 FROM users WHERE referral_code=$2 AND id<>$1 ON CONFLICT DO NOTHING`, [user.id, referralCode.toUpperCase()]);
    } else {
      await client.query(`UPDATE mobile_identities SET last_login_at=now() WHERE user_id=$1`, [user.id]);
    }
    const sessionToken = randomToken();
    const csrfToken = randomToken();
    const session = await client.query(`INSERT INTO sessions(user_id,token_hash,csrf_hash,expires_at,created_ip,user_agent_hash) VALUES($1,$2,$3,now()+interval '${SESSION_DAYS} days',$4::inet,$5) RETURNING id`, [user.id, sha256(sessionToken), sha256(csrfToken), ip, sha256(userAgent)]);
    const credits = (await client.query(`SELECT balance FROM analysis_credits WHERE user_id=$1`, [user.id])).rows[0]?.balance ?? 0;
    return { sessionToken, csrfToken, created, user: { id: user.id, mobile, role: user.role, credits }, sessionId: session.rows[0].id };
  });
}

export function setSessionCookie(res: Response, token: string) {
  res.cookie(SESSION_COOKIE, token, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'strict', path: '/', maxAge: SESSION_DAYS * 86400_000 });
}

export async function authenticate(req: Request, _res: Response, next: NextFunction) {
  try {
    const token = req.cookies?.[SESSION_COOKIE];
    if (!token) return next();
    const result = await pool.query(`SELECT s.id,u.id AS user_id,u.mobile_e164,r.code AS role,coalesce(c.balance,0)::int AS credits FROM sessions s JOIN users u ON u.id=s.user_id JOIN roles r ON r.id=u.role_id LEFT JOIN analysis_credits c ON c.user_id=u.id WHERE s.token_hash=$1 AND s.revoked_at IS NULL AND s.expires_at>now() AND u.status='active'`, [sha256(token)]);
    if (result.rows[0]) {
      const row = result.rows[0];
      req.sessionId = row.id;
      req.authUser = { id: row.user_id, mobile: row.mobile_e164, role: row.role, credits: row.credits };
    }
    next();
  } catch (error) { next(error); }
}

export const requireUser = (req: Request, res: Response, next: NextFunction) => req.authUser ? next() : res.status(401).json({ success: false, error: 'ابتدا وارد حساب کاربری شوید.' });
export const requireAdmin = (req: Request, res: Response, next: NextFunction) => req.authUser?.role === 'admin' ? next() : res.status(403).json({ success: false, error: 'دسترسی مجاز نیست.' });
export function requireCsrf(req: Request, res: Response, next: NextFunction) {
  if (!req.sessionId) return res.status(401).json({ success: false, error: 'نشست معتبر نیست.' });
  const token = req.header('x-csrf-token') || '';
  pool.query(`SELECT 1 FROM sessions WHERE id=$1 AND csrf_hash=$2 AND revoked_at IS NULL`, [req.sessionId, sha256(token)])
    .then((r) => r.rowCount ? next() : res.status(403).json({ success: false, error: 'درخواست معتبر نیست.' })).catch(next);
}

export async function revokeSession(req: Request, res: Response) {
  if (req.sessionId) await pool.query(`UPDATE sessions SET revoked_at=now() WHERE id=$1`, [req.sessionId]);
  res.clearCookie(SESSION_COOKIE, { httpOnly: true, secure: process.env.NODE_ENV === 'production', sameSite: 'strict', path: '/' });
}
