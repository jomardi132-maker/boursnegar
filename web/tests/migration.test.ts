import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";

const sql = fs.readFileSync(path.resolve("migrations/001_core.sql"), "utf8");
const campaignSql = fs.readFileSync(
  path.resolve("migrations/003_campaign_redemptions.sql"),
  "utf8",
);
describe("core migration safety contract", () => {
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
});
