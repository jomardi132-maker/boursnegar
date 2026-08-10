import crypto from 'crypto';
import type express from 'express';
import { z } from 'zod';
import { pool, withTransaction } from './postgres';
import { requireAdmin, requireCsrf, requireUser } from './auth';

const asyncRoute = (fn: express.RequestHandler): express.RequestHandler => (req,res,next) => Promise.resolve(fn(req,res,next)).catch(next);
const audit = async (adminId:string,action:string,targetType:string,targetId:string,ip:string,metadata:object={}) => pool.query(`INSERT INTO admin_audit_logs(admin_user_id,action,target_type,target_id,metadata,ip) VALUES($1,$2,$3,$4,$5,$6::inet)`,[adminId,action,targetType,targetId,metadata,ip]);

export function installPlatformRoutes(app: express.Express) {
  app.get('/api/plans', asyncRoute(async (_req,res) => {
    const r=await pool.query(`SELECT id,code,title_fa,duration_days,price_toman,analysis_credits FROM plans WHERE active ORDER BY duration_days`);
    res.json({success:true,plans:r.rows});
  }));
  app.get('/api/public/settings', asyncRoute(async (_req,res) => {
    const r=await pool.query(`SELECT key,value FROM system_settings WHERE is_public`);
    res.json({success:true,settings:Object.fromEntries(r.rows.map(x=>[x.key,x.value]))});
  }));

  app.get('/api/account/overview',requireUser,asyncRoute(async(req,res)=>{
    const [credits,subscription,payments,referral]=await Promise.all([
      pool.query(`SELECT balance FROM analysis_credits WHERE user_id=$1`,[req.authUser!.id]),
      pool.query(`SELECT s.id,s.status,s.starts_at,s.ends_at,p.code,p.title_fa FROM subscriptions s JOIN plans p ON p.id=s.plan_id WHERE s.user_id=$1 ORDER BY s.created_at DESC LIMIT 1`,[req.authUser!.id]),
      pool.query(`SELECT id,amount_toman,tracking_number,status,created_at FROM payment_submissions WHERE user_id=$1 ORDER BY created_at DESC LIMIT 30`,[req.authUser!.id]),
      pool.query(`SELECT referral_code FROM users WHERE id=$1`,[req.authUser!.id]),
    ]);
    res.json({success:true,credits:credits.rows[0]?.balance??0,subscription:subscription.rows[0]??null,payments:payments.rows,referralCode:referral.rows[0]?.referral_code});
  }));
  app.get('/api/account/referrals',requireUser,asyncRoute(async(req,res)=>{
    const r=await pool.query(`SELECT rf.id,rf.status,rf.created_at,rf.rewarded_at,u.mobile_e164 FROM referrals rf JOIN users u ON u.id=rf.referred_user_id WHERE rf.referrer_user_id=$1 ORDER BY rf.created_at DESC`,[req.authUser!.id]);
    res.json({success:true,referrals:r.rows.map(x=>({...x,mobile_e164:x.mobile_e164.replace(/(\+989\d{2})\d{4}(\d{3})/,'$1****$2')}))});
  }));

  const alertSchema=z.object({symbol:z.string().regex(/^[\u0600-\u06FFa-zA-Z0-9‌_-]{1,32}$/),kind:z.enum(['price','pe','codal']),comparator:z.enum(['gte','lte']).optional(),targetValue:z.number().positive().optional()}).superRefine((v,c)=>{if(v.kind==='codal'&&v.targetValue!=null)c.addIssue({code:'custom',message:'targetValue forbidden'});if(v.kind!=='codal'&&v.targetValue==null)c.addIssue({code:'custom',message:'targetValue required'});});
  app.get('/api/alerts',requireUser,asyncRoute(async(req,res)=>{const r=await pool.query(`SELECT id,symbol,kind,comparator,target_value,active,created_at FROM alerts WHERE user_id=$1 ORDER BY created_at DESC`,[req.authUser!.id]);res.json({success:true,alerts:r.rows});}));
  app.post('/api/alerts',requireUser,requireCsrf,asyncRoute(async(req,res)=>{const p=alertSchema.safeParse(req.body);if(!p.success)return res.status(400).json({success:false,error:'اطلاعات هشدار معتبر نیست.'});const v=p.data;const r=await pool.query(`INSERT INTO alerts(user_id,symbol,kind,comparator,target_value) VALUES($1,$2,$3,$4,$5) RETURNING *`,[req.authUser!.id,v.symbol,v.kind,v.kind==='codal'?null:v.comparator,v.kind==='codal'?null:v.targetValue]);res.status(201).json({success:true,alert:r.rows[0]});}));
  app.patch('/api/alerts/:id',requireUser,requireCsrf,asyncRoute(async(req,res)=>{const p=z.object({active:z.boolean()}).safeParse(req.body);if(!p.success)return res.status(400).json({success:false,error:'درخواست معتبر نیست.'});const r=await pool.query(`UPDATE alerts SET active=$3 WHERE id=$1 AND user_id=$2 RETURNING id,active`,[req.params.id,req.authUser!.id,p.data.active]);if(!r.rowCount)return res.status(404).json({success:false,error:'هشدار پیدا نشد.'});res.json({success:true,alert:r.rows[0]});}));
  app.delete('/api/alerts/:id',requireUser,requireCsrf,asyncRoute(async(req,res)=>{const r=await pool.query(`DELETE FROM alerts WHERE id=$1 AND user_id=$2`,[req.params.id,req.authUser!.id]);res.status(r.rowCount?200:404).json({success:Boolean(r.rowCount)});}));

  app.get('/api/admin/payments',requireUser,requireAdmin,asyncRoute(async(req,res)=>{const status=z.enum(['pending','approved','rejected']).catch('pending').parse(req.query.status);const r=await pool.query(`SELECT ps.id,ps.amount_toman,ps.tracking_number,ps.paid_at,ps.status,ps.created_at,u.mobile_e164,p.code AS plan_code,p.analysis_credits,p.duration_days FROM payment_submissions ps JOIN users u ON u.id=ps.user_id LEFT JOIN plans p ON p.id=ps.plan_id WHERE ps.status=$1 ORDER BY ps.created_at`,[status]);res.json({success:true,payments:r.rows});}));
  app.post('/api/admin/payments/:id/decision',requireUser,requireAdmin,requireCsrf,asyncRoute(async(req,res)=>{
    const parsed=z.object({decision:z.enum(['approved','rejected']),note:z.string().max(500).optional()}).safeParse(req.body);if(!parsed.success)return res.status(400).json({success:false,error:'تصمیم معتبر نیست.'});
    const result=await withTransaction(async client=>{const found=await client.query(`SELECT ps.*,p.analysis_credits,p.duration_days FROM payment_submissions ps LEFT JOIN plans p ON p.id=ps.plan_id WHERE ps.id=$1 FOR UPDATE`,[req.params.id]);const payment=found.rows[0];if(!payment)throw new Error('NOT_FOUND');if(payment.status!=='pending')throw new Error('ALREADY_DECIDED');await client.query(`UPDATE payment_submissions SET status=$2 WHERE id=$1`,[payment.id,parsed.data.decision]);await client.query(`INSERT INTO payment_approvals(payment_id,admin_user_id,decision,note) VALUES($1,$2,$3,$4)`,[payment.id,req.authUser!.id,parsed.data.decision,parsed.data.note]);if(parsed.data.decision==='approved'){if(payment.duration_days>0)await client.query(`INSERT INTO subscriptions(user_id,plan_id,status,starts_at,ends_at) VALUES($1,$2,'active',now(),now()+($3||' days')::interval)`,[payment.user_id,payment.plan_id,payment.duration_days]);if(payment.analysis_credits>0){const c=await client.query(`UPDATE analysis_credits SET balance=balance+$2,updated_at=now() WHERE user_id=$1 RETURNING balance`,[payment.user_id,payment.analysis_credits]);await client.query(`INSERT INTO credit_ledger(user_id,delta,balance_after,reason,reference_type,reference_id,idempotency_key) VALUES($1,$2,$3,'purchase','payment',$4,$5)`,[payment.user_id,payment.analysis_credits,c.rows[0].balance,payment.id,`payment:${payment.id}`]);}}return{paymentId:payment.id,status:parsed.data.decision};});
    await audit(req.authUser!.id,'payment.decision','payment',req.params.id,req.ip||'127.0.0.1',{decision:parsed.data.decision});res.json({success:true,result});
  }));
  app.patch('/api/admin/users/:id',requireUser,requireAdmin,requireCsrf,asyncRoute(async(req,res)=>{const p=z.object({status:z.enum(['active','suspended']).optional(),role:z.enum(['user','admin']).optional()}).refine(v=>v.status||v.role).safeParse(req.body);if(!p.success)return res.status(400).json({success:false,error:'تغییر معتبر نیست.'});const r=await pool.query(`UPDATE users SET status=coalesce($2,status),role_id=coalesce((SELECT id FROM roles WHERE code=$3),role_id),updated_at=now() WHERE id=$1 RETURNING id,status`,[req.params.id,p.data.status,p.data.role]);if(!r.rowCount)return res.status(404).json({success:false});await audit(req.authUser!.id,'user.update','user',req.params.id,req.ip||'127.0.0.1',p.data);res.json({success:true,user:r.rows[0]});}));
  app.post('/api/admin/users/:id/credits',requireUser,requireAdmin,requireCsrf,asyncRoute(async(req,res)=>{const p=z.object({delta:z.number().int().min(-10000).max(10000).refine(x=>x!==0),note:z.string().min(3).max(300)}).safeParse(req.body);if(!p.success)return res.status(400).json({success:false,error:'تغییر اعتبار معتبر نیست.'});const key=`admin:${req.authUser!.id}:${crypto.randomUUID()}`;const balance=await withTransaction(async c=>{const r=await c.query(`UPDATE analysis_credits SET balance=balance+$2,updated_at=now() WHERE user_id=$1 AND balance+$2>=0 RETURNING balance`,[req.params.id,p.data.delta]);if(!r.rowCount)throw new Error('INVALID_BALANCE');await c.query(`INSERT INTO credit_ledger(user_id,delta,balance_after,reason,reference_type,reference_id,idempotency_key) VALUES($1,$2,$3,'admin_adjustment','admin',$4,$5)`,[req.params.id,p.data.delta,r.rows[0].balance,req.authUser!.id,key]);return r.rows[0].balance;});await audit(req.authUser!.id,'credit.adjust','user',req.params.id,req.ip||'127.0.0.1',{delta:p.data.delta,note:p.data.note});res.json({success:true,balance});}));
  app.get('/api/admin/audit',requireUser,requireAdmin,asyncRoute(async(_req,res)=>{const r=await pool.query(`SELECT id,action,target_type,target_id,metadata,created_at FROM admin_audit_logs ORDER BY created_at DESC LIMIT 200`);res.json({success:true,logs:r.rows});}));
}
