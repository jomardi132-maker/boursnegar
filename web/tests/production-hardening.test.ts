import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";

const source = fs.readFileSync(path.resolve("server.production.ts"), "utf8");

describe("production hardening contract", () => {
  it("exposes machine-readable health and API 404 responses", () => {
    expect(source).toContain('app.get("/api/health"');
    expect(source).toContain('app.use("/api"');
    expect(source).toContain("مسیر API پیدا نشد");
  });

  it("keeps SMS login disabled", () => {
    expect(source).toMatch(
      /"\/api\/auth\/otp\/request",[\s\S]{0,220}status\(410\)/,
    );
    expect(source).toMatch(
      /"\/api\/auth\/otp\/verify",[\s\S]{0,220}status\(410\)/,
    );
  });

  it("replays an analysis idempotency key without another debit", () => {
    expect(source).toContain("replayed: true");
    expect(source).toContain("IDEMPOTENCY_CONFLICT");
    expect(source).toContain("l.idempotency_key=$2");
  });
  it("does not charge v2 analyses with insufficient data", () => {
    expect(source).toContain('"/api/v2/analyze"');
    expect(source).toContain('data.decision !== "INSUFFICIENT_DATA"');
    expect(source).toContain("analysis_usage");
    expect(source).toContain("charge ? -1 : 0");
  });
});
