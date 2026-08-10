import dotenv from 'dotenv';
import { pool, withTransaction } from './postgres';

dotenv.config();

const enabled = process.env.ALERT_WORKER_ENABLED === 'true';
const smsEnabled = process.env.SMS_ENABLED === 'true';

type Alert = {
  id: string;
  user_id: string;
  mobile_e164: string;
  symbol: string;
  kind: 'price' | 'pe' | 'codal';
  comparator: 'gte' | 'lte' | null;
  target_value: string | null;
  last_trigger_key: string | null;
};

async function timeoutFetch(url: string, init?: RequestInit) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 10_000);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function sendSms(mobile: string, message: string) {
  if (!smsEnabled) throw new Error('SMS_DISABLED');
  const key = process.env.KAVENEGAR_API_KEY;
  const sender = process.env.KAVENEGAR_ALERT_SENDER;
  if (!key || !sender) throw new Error('SMS_CONFIG_MISSING');

  const body = new URLSearchParams({
    receptor: `0${mobile.slice(3)}`,
    sender,
    message,
  });
  const response = await timeoutFetch(
    `https://api.kavenegar.com/v1/${encodeURIComponent(key)}/sms/send.json`,
    { method: 'POST', body },
  );
  if (!response.ok) throw new Error('SMS_PROVIDER_ERROR');
  const payload: any = await response.json();
  if (payload?.return?.status !== 200) throw new Error('SMS_PROVIDER_REJECTED');
  return String(payload.entries?.[0]?.messageid || '');
}

async function main() {
  if (!enabled) {
    console.log('alert-worker disabled');
    return;
  }

  const lock = await pool.query(
    `SELECT pg_try_advisory_lock(hashtext('boursnegar-alert-worker')) AS ok`,
  );
  if (!lock.rows[0]?.ok) return;

  try {
    const rows = await pool.query<Alert>(`
      SELECT a.id,a.user_id,u.mobile_e164,a.symbol,a.kind,a.comparator,
             a.target_value,a.last_trigger_key
      FROM alerts a
      JOIN users u ON u.id=a.user_id
      WHERE a.active AND u.status='active'
      ORDER BY a.created_at
      LIMIT 500
    `);
    const symbols = [...new Set(rows.rows.map((item) => item.symbol))];
    const snapshots = new Map<string, any>();

    for (const symbol of symbols) {
      try {
        const response = await timeoutFetch(
          `${process.env.PYTHON_API_BASE || 'http://127.0.0.1:8001'}/api/analyze/${encodeURIComponent(symbol)}?report_mode=latest_codal`,
        );
        if (response.ok) snapshots.set(symbol, await response.json());
      } catch {
        // A later scheduled run retries transient data-service errors.
      }
    }

    let submittedThisRun=0;
    const maxPerRun=Math.max(1,Math.min(Number(process.env.ALERT_SMS_MAX_PER_RUN||50),100));
    for (const alert of rows.rows) {
      if(submittedThisRun>=maxPerRun) break;
      const data = snapshots.get(alert.symbol);
      if (!data) continue;
      const price = Number(data.live_price?.last_price);
      const pe = Number(data.live_price?.pe_ratio);
      const trace = String(data.report_used?.tracing_no || '');
      let value: number | undefined;
      let key = '';
      let message = '';

      if (alert.kind === 'price') {
        value = price;
        key = `price:${alert.target_value}:${alert.comparator}`;
        message = `قیمت ${alert.symbol} به ${price.toLocaleString('fa-IR')} ریال رسید.`;
      } else if (alert.kind === 'pe') {
        value = pe;
        key = `pe:${alert.target_value}:${alert.comparator}`;
        message = `نسبت P/E نماد ${alert.symbol} به ${pe.toLocaleString('fa-IR')} رسید.`;
      } else {
        key = `codal:${trace}`;
        message = `اطلاعیه جدید کدال برای ${alert.symbol} منتشر شد.`;
      }

      const target = Number(alert.target_value);
      const triggered =
        alert.kind === 'codal'
          ? Boolean(trace)
          : Number.isFinite(value) &&
            ((alert.comparator === 'gte' && value! >= target) ||
              (alert.comparator === 'lte' && value! <= target));
      if (!triggered || alert.last_trigger_key === key) continue;

      const deduplicationKey=`alert:${alert.id}:${key}`;
      const claimed=await pool.query(
        `INSERT INTO sms_delivery_attempts(user_id,mobile_e164,purpose,status,deduplication_key)
         VALUES($1,$2,'alert','pending',$3) ON CONFLICT(deduplication_key) DO NOTHING RETURNING id`,
        [alert.user_id,alert.mobile_e164,deduplicationKey],
      );
      if(!claimed.rowCount) continue;
      const attemptId=claimed.rows[0].id;
      try {
        submittedThisRun++;
        const providerId = await sendSms(alert.mobile_e164, message);
        await withTransaction(async (client) => {
          const updated = await client.query(
            `UPDATE alerts SET last_trigger_key=$2
             WHERE id=$1 AND last_trigger_key IS DISTINCT FROM $2`,
            [alert.id, key],
          );
          if (updated.rowCount !== 1) return;
          await client.query(`UPDATE sms_delivery_attempts SET provider_message_id=$2,status='submitted' WHERE id=$1`,[attemptId,providerId]);
        });
      } catch (error) {
        await pool
          .query(
            `UPDATE sms_delivery_attempts SET status='failed',error_code=$2 WHERE id=$1`,
            [attemptId,error instanceof Error ? error.message.slice(0, 80) : 'UNKNOWN'],
          )
          .catch(() => {});
      }
    }
  } finally {
    await pool.query(`SELECT pg_advisory_unlock(hashtext('boursnegar-alert-worker'))`);
    await pool.end();
  }
}

main().catch((error) => {
  console.error('alert-worker failed', {
    name: error instanceof Error ? error.name : 'Unknown',
  });
  process.exit(1);
});
