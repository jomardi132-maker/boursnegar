import fs from "fs";
import path from "path";
import { describe, expect, it } from "vitest";

const server = fs.readFileSync(path.resolve("server.pending-otp.ts"), "utf8");
const ui = fs.readFileSync(path.resolve("src/AppPending.tsx"), "utf8");
describe("Pending OTP production mode", () => {
  it("rejects every OTP entry point without sending", () => {
    expect(server).toContain("OTP_PENDING_APPROVAL");
    expect(server).not.toContain("verify/lookup");
    expect(server).toMatch(/OTP_GATEWAY === ["']mock["']/);
  });
  it("keeps anonymous analysis available", () => {
    const route = server.slice(
      server.indexOf('"/api/analyze"'),
      server.indexOf('"/api/account/analyses"'),
    );
    expect(route).not.toContain("requireUser");
    expect(route).toMatch(/anonymous:\s*true/);
  });
  it("keeps account and admin authorization", () => {
    expect(server).toMatch(/"\/api\/account\/analyses"[\s\S]{0,80}requireUser/);
    expect(server).toMatch(
      /"\/api\/admin\/stats"[\s\S]{0,80}requireUser[\s\S]{0,40}requireAdmin/,
    );
  });
  it("shows the activation message and all three questions", () => {
    expect(ui).toContain("ورود پیامکی در حال فعال‌سازی است");
    expect(ui).toContain("[1,2,3].map");
  });
});
