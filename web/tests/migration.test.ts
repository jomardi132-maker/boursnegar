import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";

const sql = fs.readFileSync(path.resolve("migrations/001_core.sql"), "utf8");
const campaignSql = fs.readFileSync(
  path.resolve("migrations/003_campaign_redemptions.sql"),
  "utf8",
);
const emailAuthSql = fs.readFileSync(path.resolve("migrations/005_email_password_auth.sql"), "utf8");
const creditPackagesSql = fs.readFileSync(path.resolve("migrations/008_credit_packages.sql"), "utf8");
const screenerSql = fs.readFileSync(path.resolve("migrations/010_market_screener.sql"), "utf8");
describe("core migration safety contract", () => {
  it("never executes rollback files in the forward migration runner", () => {
    const runner = fs.readFileSync(path.resolve("scripts/migrate.ts"), "utf8");
    expect(runner).toContain("!f.endsWith('.rollback.sql')");
  });
  it("contains every required domain table", () => {
    for (const table of [
      "users",
      "mobile_identities",
      "otp_requests",
      "otp_attempts",
      "sessions",
      "roles",
      "plans",
      "subscriptions",
      "analysis_credits",
      "credit_ledger",
      "analysis_history",
      "payment_submissions",
      "payment_approvals",
      "promotions",
      "referrals",
      "alerts",
      "sms_delivery_attempts",
      "admin_audit_logs",
      "system_settings",
    ]) {
      expect(sql).toContain(`CREATE TABLE IF NOT EXISTS ${table}`);
    }
  });
  it("tracks successful and failed analysis attempts", () => {
    const sql = fs.readFileSync(
      path.resolve("migrations/004_analysis_attempts.sql"),
      "utf8",
    );
    expect(sql).toContain("analysis_attempts");
    expect(sql).toContain("success boolean NOT NULL");
    expect(sql).toContain("user_id uuid REFERENCES users");
  });
  it("tracks campaign use once per user and payment", () => {
    expect(campaignSql).toContain("promotion_redemptions");
    expect(campaignSql).toContain("UNIQUE (promotion_id, user_id)");
    expect(campaignSql).toContain("UNIQUE (payment_id)");
  });
  it("makes the credit ledger append-only and idempotent", () => {
    expect(sql).toContain("credit_ledger_immutable");
    expect(sql).toContain("idempotency_key text NOT NULL UNIQUE");
  });
  it("constrains OTP and session records", () => {
    expect(sql).toContain("code_hash char(64)");
    expect(sql).toContain("token_hash char(64)");
    expect(sql).not.toMatch(/password/i);
  });
  it("supports email identities and one-time password resets", () => {
    expect(emailAuthSql).toContain("email_identities");
    expect(emailAuthSql).toContain("password_reset_tokens");
    expect(emailAuthSql).toContain("token_hash char(64)");
    expect(emailAuthSql).toContain("consumed_at timestamptz");
  });
  it("seeds non-expiring credit packages using the approved pricing rule", () => {
    expect(creditPackagesSql).toContain("generate_series(6,20)");
    expect(creditPackagesSql).toContain("(credits - 1) * 100000");
    expect(creditPackagesSql).toContain("بدون تاریخ انقضا");
  });
  it("indexes the latest valid prices used by the market screener", () => {
    expect(screenerSql).toContain("daily_prices_date_instrument_idx");
    expect(screenerSql).toContain("WHERE quality_status='VALID'");
  });
});
