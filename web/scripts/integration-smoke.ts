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
 console.log('integration-smoke: PASS');
}
main().finally(()=>pool.end());
