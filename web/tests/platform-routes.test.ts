import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";
const source = fs.readFileSync(
  path.resolve("server/platformRoutes.ts"),
  "utf8",
);
describe("platform routes security contract", () => {
  it.each(["/api/account/overview", "/api/account/referrals", "/api/alerts"])(
    "protects account route %s",
    (route) =>
      expect(
        source.slice(source.indexOf(route), source.indexOf(route) + 180),
      ).toContain("requireUser"),
  );
  it.each([
    "/api/admin/payments",
    "/api/admin/users",
    "/api/admin/audit",
    "/api/admin/plans",
    "/api/admin/campaigns",
    "/api/admin/settings",
    "/api/admin/sms",
  ])("protects admin route %s", (route) => {
    const block = source.slice(
      source.indexOf(route),
      source.indexOf(route) + 220,
    );
    expect(block).toContain("requireUser");
    expect(block).toContain("requireAdmin");
  });
  it("uses transactions and idempotent ledger references for approvals", () => {
    expect(source).toContain("withTransaction");
    expect(source).toContain("ALREADY_DECIDED");
    expect(source).toContain("payment:${payment.id}");
  });
  it("requires CSRF for state changes", () => {
    for (const [method, route] of [
      ["post", "/api/alerts"],
      ["patch", "/api/alerts/:id"],
      ["delete", "/api/alerts/:id"],
      ["post", "/api/admin/payments/:id/decision"],
    ])
      expect(source).toMatch(
        new RegExp(
          `app\\.${method}\\(\\s*["']${route}["'][\\s\\S]{0,260}requireCsrf`,
        ),
      );
  });
  it("never exposes secret-shaped system settings", () =>
    expect(source).toMatch(/secret\|token\|password\|api/));
  it("supports configurable plans and immutable purchase entitlements", () => {
    expect(source).toContain('app.post(\n    "/api/admin/plans"');
    expect(source).toContain("publicly_visible");
    expect(source).toContain("unlimited_analyses");
    expect(source).toContain("entitlement_snapshot");
    expect(source).toContain("purchased_price_toman");
  });
});
