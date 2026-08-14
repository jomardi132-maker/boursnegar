import crypto from "crypto";
import dotenv from "dotenv";
import { createPasswordReset, hashPassword, normalizeEmail } from "../server/auth";
import { mailDeliveryReady, sendPasswordResetEmail } from "../server/mailer";
import { pool, withTransaction } from "../server/postgres";

dotenv.config({ quiet: true });

async function main() {
  const email = normalizeEmail(process.env.ADMIN_EMAIL || "");
  if (!email) throw new Error("ADMIN_EMAIL is required and must be valid");
  const userId = await withTransaction(async (client) => {
    const existing = await client.query(
      `SELECT user_id FROM email_identities WHERE email=$1 FOR UPDATE`,
      [email],
    );
    let id = existing.rows[0]?.user_id as string | undefined;
    if (!id) {
      const referral = crypto
        .randomBytes(8)
        .toString("hex")
        .slice(0, 12)
        .toUpperCase();
      id = (
        await client.query(
          `INSERT INTO users(role_id,referral_code)
           SELECT id,$1 FROM roles WHERE code='user' RETURNING id`,
          [referral],
        )
      ).rows[0].id;
      const unusablePassword = await hashPassword(crypto.randomBytes(64).toString("base64url"));
      await client.query(
        `INSERT INTO email_identities(user_id,email,password_hash) VALUES($1,$2,$3)`,
        [id, email, unusablePassword],
      );
      await client.query(
        `INSERT INTO analysis_credits(user_id,balance) VALUES($1,5)`,
        [id],
      );
      await client.query(
        `INSERT INTO credit_ledger(
           user_id,delta,balance_after,reason,idempotency_key
         ) VALUES($1,5,5,'welcome',$2)`,
        [id, `welcome:${id}`],
      );
    }
    await client.query(
      `UPDATE users SET role_id=(SELECT id FROM roles WHERE code='admin'),
         status='active',updated_at=now() WHERE id=$1`,
      [id],
    );
    await client.query(
      `UPDATE sessions SET revoked_at=now() WHERE user_id=$1 AND revoked_at IS NULL`,
      [id],
    );
    await client.query(
      `INSERT INTO admin_audit_logs(
         admin_user_id,action,target_type,target_id,metadata,ip
       ) VALUES($1,'admin.bootstrap','user',$1::text,$2,'127.0.0.1'::inet)`,
      [id, { source: "local-cli", idempotent: true }],
    );
    return id;
  });
  const token = await createPasswordReset(email, "127.0.0.1");
  if (!token) throw new Error("Could not create the one-time activation token");
  const origin = process.env.PUBLIC_ORIGIN || "https://boursnegar.ir";
  const link = `${origin}/?reset-token=${encodeURIComponent(token)}`;
  if (mailDeliveryReady()) {
    await sendPasswordResetEmail(email, link);
    console.log("ADMIN_BOOTSTRAP=READY ACTIVATION=EMAIL_SUBMITTED");
  } else {
    console.log(`ADMIN_BOOTSTRAP=READY ACTIVATION_LINK=${link}`);
  }
  console.log(`ADMIN_USER_ID=${userId}`);
}

main()
  .catch((error) => {
    console.error(error instanceof Error ? error.message : "bootstrap failed");
    process.exitCode = 1;
  })
  .finally(() => pool.end());
