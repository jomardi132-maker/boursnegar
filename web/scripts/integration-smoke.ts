import crypto from 'crypto';
import { createOtp, verifyOtp } from '../server/auth';
import { pool, withTransaction } from '../server/postgres';

const suffix=crypto.randomInt(1000000,9999999).toString();
const mobile=`+98912${suffix}`;
const ip='127.0.0.1';

async function main(){
 const otp=await createOtp(mobile,ip);
 if(!/^\d{6}$/.test(otp.code))throw new Error('OTP_FORMAT');
 const invalidOtp=await createOtp(mobile,ip);
 for(let attempt=0;attempt<5;attempt++){try{await verifyOtp(invalidOtp.requestId,mobile,'000000',ip,'integration-test');}catch{}}
 const locked=(await pool.query(`SELECT attempts,locked_until FROM otp_requests WHERE id=$1`,[invalidOtp.requestId])).rows[0];
 if(Number(locked.attempts)!==5||!locked.locked_until)throw new Error('OTP_LOCK_NOT_PERSISTED');
 const expiredOtp=await createOtp(mobile,ip);
 await pool.query(`UPDATE otp_requests SET expires_at=now()-interval '1 second' WHERE id=$1`,[expiredOtp.requestId]);
 let expiredRejected=false;try{await verifyOtp(expiredOtp.requestId,mobile,expiredOtp.code,ip,'integration-test');}catch{expiredRejected=true}if(!expiredRejected)throw new Error('OTP_EXPIRY');
 const verified=await verifyOtp(otp.requestId,mobile,otp.code,ip,'integration-test');
 if(!verified.sessionToken||!verified.csrfToken||verified.user.credits!==5)throw new Error('AUTH_CONTRACT');
 const consume=async(key:string)=>withTransaction(async c=>{const r=await c.query(`SELECT balance FROM analysis_credits WHERE user_id=$1 FOR UPDATE`,[verified.user.id]);const balance=Number(r.rows[0].balance);if(balance<1)throw new Error('NO_CREDIT');await c.query(`UPDATE analysis_credits SET balance=balance-1 WHERE user_id=$1`,[verified.user.id]);await c.query(`INSERT INTO credit_ledger(user_id,delta,balance_after,reason,idempotency_key) VALUES($1,-1,$2,'analysis',$3)`,[verified.user.id,balance-1,key]);});
 await Promise.all([consume(`test:${crypto.randomUUID()}`),consume(`test:${crypto.randomUUID()}`)]);
 const balance=Number((await pool.query(`SELECT balance FROM analysis_credits WHERE user_id=$1`,[verified.user.id])).rows[0].balance);
 if(balance!==3)throw new Error('CONCURRENT_BALANCE');
 let immutable=false;try{await pool.query(`UPDATE credit_ledger SET delta=9 WHERE user_id=$1`,[verified.user.id]);}catch{immutable=true}if(!immutable)throw new Error('LEDGER_MUTABLE');
 const plan=(await pool.query(`UPDATE plans SET price_toman=1000,analysis_credits=2 WHERE code='1_month' RETURNING id`)).rows[0];
 await import('../server.production');await new Promise(resolve=>setTimeout(resolve,200));const base=`http://127.0.0.1:${process.env.PORT||3201}`;
 const cookie=`boursnegar_session=${verified.sessionToken}`;const csrf=verified.csrfToken;
 const forbidden=await fetch(`${base}/api/admin/stats`,{headers:{Cookie:cookie}});if(forbidden.status!==403)throw new Error('ADMIN_AUTHORIZATION');
 const paymentForm=(tracking:string,bytes:Uint8Array)=>{const form=new FormData();form.set('planId',plan.id);form.set('amountToman','1000');form.set('trackingNumber',tracking);form.set('paidAt',new Date().toISOString());form.set('receipt',new Blob([bytes],{type:'image/png'}),'receipt.png');return form};
 const spoofed=await fetch(`${base}/api/payments`,{method:'POST',headers:{Cookie:cookie,'x-csrf-token':csrf},body:paymentForm('TEST-SPOOF',new TextEncoder().encode('not an image'))});if(spoofed.status!==400)throw new Error('UPLOAD_SIGNATURE');
 const valid=await fetch(`${base}/api/payments`,{method:'POST',headers:{Cookie:cookie,'x-csrf-token':csrf},body:paymentForm('TEST-VALID',new Uint8Array([137,80,78,71,13,10,26,10]))});if(valid.status!==201)throw new Error(`UPLOAD_VALID_${valid.status}`);const validBody:any=await valid.json();
 await pool.query(`UPDATE users SET role_id=(SELECT id FROM roles WHERE code='admin') WHERE id=$1`,[verified.user.id]);
 const receipt=await fetch(`${base}/api/admin/payments/${validBody.payment.id}/receipt`,{headers:{Cookie:cookie}});if(receipt.status!==200||receipt.headers.get('cache-control')!=='private, no-store')throw new Error('RECEIPT_ACCESS');
 const decision={method:'POST',headers:{Cookie:cookie,'x-csrf-token':csrf,'content-type':'application/json'},body:JSON.stringify({decision:'approved'})};const approved=await fetch(`${base}/api/admin/payments/${validBody.payment.id}/decision`,decision);if(approved.status!==200)throw new Error(`PAYMENT_APPROVAL_${approved.status}`);
 const duplicate=await fetch(`${base}/api/admin/payments/${validBody.payment.id}/decision`,decision);if(duplicate.status!==409)throw new Error(`PAYMENT_DUPLICATE_${duplicate.status}`);
 const campaign=(await pool.query(`INSERT INTO promotions(code,title_fa,starts_at,ends_at,capacity,credit_amount,price_toman,active,rules) VALUES('TEST_CAMPAIGN','کمپین تست',now()-interval '1 day',now()+interval '1 day',1,10,500,true,'{"audience":"all","perUser":1}') RETURNING id`)).rows[0];
 const campaignForm=new FormData();campaignForm.set('campaignId',campaign.id);campaignForm.set('amountToman','500');campaignForm.set('trackingNumber','TEST-CAMPAIGN');campaignForm.set('paidAt',new Date().toISOString());campaignForm.set('receipt',new Blob([new Uint8Array([137,80,78,71,13,10,26,10])],{type:'image/png'}),'receipt.png');
 const campaignPayment=await fetch(`${base}/api/payments`,{method:'POST',headers:{Cookie:cookie,'x-csrf-token':csrf},body:campaignForm});if(campaignPayment.status!==201)throw new Error(`CAMPAIGN_PAYMENT_${campaignPayment.status}`);const campaignBody:any=await campaignPayment.json();
 const campaignApproved=await fetch(`${base}/api/admin/payments/${campaignBody.payment.id}/decision`,decision);if(campaignApproved.status!==200)throw new Error(`CAMPAIGN_APPROVAL_${campaignApproved.status}`);
 const redemption=Number((await pool.query(`SELECT count(*) FROM promotion_redemptions WHERE promotion_id=$1 AND user_id=$2`,[campaign.id,verified.user.id])).rows[0].count);if(redemption!==1)throw new Error('CAMPAIGN_REDEMPTION');
 const publicCampaigns:any=await (await fetch(`${base}/api/campaigns`)).json();if(publicCampaigns.campaigns.some((x:any)=>x.id===campaign.id))throw new Error('CAMPAIGN_CAPACITY');
 console.log('integration-smoke: PASS');
}
main().then(async()=>{await pool.end();process.exit(0)}).catch(async error=>{console.error(error instanceof Error?error.message:'integration failed');await pool.end();process.exit(1)});
