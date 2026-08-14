import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";
const source = fs.readFileSync(
  path.resolve("server/platformRoutes.ts"),
  "utf8",
);
describe("platform routes security contract", () => {
  it("provides a bounded public symbol search over normalized catalog data", () => {
    expect(source).toContain('"/api/symbols/search"');
    expect(source).toContain("similarity(sa.symbol,$1)");
    expect(source).toContain("LIMIT 10");
  });
  it("publishes evidence-backed stock pages and market coverage", () => {
    expect(source).toContain('"/api/stocks/:symbol"');
    expect(source).toContain('"/api/market/overview"');
    expect(source).toContain("FROM daily_prices WHERE instrument_id=$1");
    expect(source).toContain("FROM disclosures d JOIN disclosure_versions v");
    expect(source).toContain('"/sitemap.xml"');
    expect(source).toContain("oneMonth: priceReturn(prices, 1)");
    expect(source).toContain("sixMonths: priceReturn(prices, 6)");
    expect(source).toContain("oneYear: priceReturn(prices, 12)");
  });
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
    "/api/admin/data-status",
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
  it("validates and audits editable economic reference rates", () => {
    expect(source).toContain('"/api/admin/reference-rates"');
    expect(source).toContain('"reference_rates.update"');
    expect(source).toContain('value.startsWith("https://")');
  });
  it("supports configurable plans and immutable purchase entitlements", () => {
    expect(source).toContain('app.post(\n    "/api/admin/plans"');
    expect(source).toContain("publicly_visible");
    expect(source).toContain("unlimited_analyses");
    expect(source).toContain("entitlement_snapshot");
    expect(source).toContain("purchased_price_toman");
  });
});
