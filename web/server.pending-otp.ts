import fs from 'fs';
import path from 'path';
import express from 'express';
import cookieParser from 'cookie-parser';
import helmet from 'helmet';
import { z } from 'zod';
import dotenv from 'dotenv';
import { generateRealHealthCard, UpstreamAnalysisError } from './server/realAnalysisAdapter';
import { pool } from './server/postgres';
import { authenticate, requireAdmin, requireUser } from './server/auth';
import { installPlatformRoutes } from './server/platformRoutes';

dotenv.config();
if (process.env.OTP_GATEWAY === 'mock') throw new Error('Mock OTP gateway is forbidden in Production');
const app = express();
const port = Number(process.env.PORT || 3000);
app.disable('x-powered-by');
app.set('trust proxy', 1);
app.use(helmet({ contentSecurityPolicy: { directives: { defaultSrc: ["'self'"], scriptSrc: ["'self'"], styleSrc: ["'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'], fontSrc: ["'self'", 'https://fonts.gstatic.com'], imgSrc: ["'self'", 'data:'], connectSrc: ["'self'"] } }, crossOriginEmbedderPolicy: false }));
app.use(express.json({ limit: '128kb' }));
app.use(cookieParser());
app.use(authenticate);

const requests = new Map<string, { count: number; reset: number }>();
const rateLimit = (limit: number, windowMs: number): express.RequestHandler => (req, res, next) => {
  const key = req.ip || 'unknown'; const now = Date.now(); const current = requests.get(key);
  if (!current || current.reset <= now) requests.set(key, { count: 1, reset: now + windowMs });
  else if (++current.count > limit) return res.status(429).json({ success: false, error: 'تعداد درخواست‌ها بیش از حد مجاز است.' });
  next();
};
const asyncRoute = (fn: express.RequestHandler): express.RequestHandler => (req,res,next) => Promise.resolve(fn(req,res,next)).catch(next);
const otpPending = (_req: express.Request, res: express.Response) => res.status(503).json({ success: false, code: 'OTP_PENDING_APPROVAL', error: 'ورود پیامکی در حال فعال‌سازی است.' });

app.get('/healthz', (_req,res) => res.json({ status: 'ok', otp: 'pending_approval' }));
app.get('/readyz', asyncRoute(async (_req,res) => { await pool.query('SELECT 1'); res.json({ status: 'ready', database: 'ok', otp: 'disabled' }); }));
app.post('/api/auth/otp/request', otpPending);
app.post('/api/auth/otp/verify', otpPending);
app.post('/api/auth/login', otpPending);
app.post('/api/auth/register', otpPending);
app.get('/api/auth/me', (req,res) => req.authUser ? res.json({ success:true,user:req.authUser }) : res.status(503).json({ success:false,code:'OTP_PENDING_APPROVAL',error:'ورود پیامکی در حال فعال‌سازی است.' }));

app.post('/api/analyze', rateLimit(15, 60_000), asyncRoute(async (req,res) => {
  const parsed = z.object({ query:z.string().min(1).max(32), reportMode:z.enum(['audited','latest_codal']).default('audited') }).safeParse(req.body);
  if (!parsed.success) return res.status(400).json({ success:false,error:'نماد یا حالت گزارش معتبر نیست.' });
  const symbol=parsed.data.query.trim().replace(/^نماد\s+/,'');
  if (!/^[\u0600-\u06FFa-zA-Z0-9‌_-]{1,32}$/.test(symbol)) return res.status(400).json({success:false,error:'نماد واردشده معتبر نیست.'});
  const data=await generateRealHealthCard(symbol,parsed.data.reportMode);
  res.setHeader('Cache-Control','no-store');
  res.json({success:true,data,analysis:{anonymous:true,remainingCredits:null}});
}));

app.get('/api/account/analyses', requireUser, (_req,res) => res.json({success:true,analyses:[]}));
app.get('/api/admin/stats', requireUser, requireAdmin, asyncRoute(async (_req,res) => {
  const result=await pool.query(`SELECT (SELECT count(*) FROM users) AS users,(SELECT count(*) FROM analysis_history) AS analyses`);
  res.json({success:true,stats:result.rows[0]});
}));
installPlatformRoutes(app);

const dist=path.join(process.cwd(),'dist');
app.use(express.static(dist,{index:false,maxAge:'1h'}));
app.get('*',(_req,res)=>res.sendFile(path.join(dist,'index.html')));
app.use((error:unknown,_req:express.Request,res:express.Response,_next:express.NextFunction)=>{
  const status=error instanceof UpstreamAnalysisError?502:500;
  console.error('[request-error]',{name:error instanceof Error?error.name:'Unknown',status});
  res.status(status).json({success:false,error:'در انجام درخواست خطایی رخ داد. دوباره تلاش کنید.'});
});
app.listen(port,'127.0.0.1',()=>console.log(`[boursnegar] pending-otp mode on 127.0.0.1:${port}`));
