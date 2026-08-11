import { describe, expect, it } from 'vitest';
import { hashPassword, normalizeEmail, normalizeIranMobile, verifyPassword } from '../server/auth';
import fs from 'fs';
import path from 'path';

describe('Iranian mobile normalization', () => {
  it.each([
    ['09123456789', '+989123456789'],
    ['989123456789', '+989123456789'],
    ['+989123456789', '+989123456789'],
  ])('normalizes %s', (input, expected) => expect(normalizeIranMobile(input)).toBe(expected));
  it.each(['9123456789', '0912345678', '+981212345678', '09123abc789'])('rejects %s', (input) => expect(normalizeIranMobile(input)).toBeNull());
});

describe('email/password security', () => {
  it('normalizes email without accepting malformed input', () => {
    expect(normalizeEmail('  User@Example.COM ')).toBe('user@example.com');
    expect(normalizeEmail('not-an-email')).toBeNull();
  });
  it('stores a salted scrypt hash and verifies in constant-time comparison path', async () => {
    process.env.PASSWORD_PEPPER = 'test-only-pepper-that-is-never-used-in-production';
    const first = await hashPassword('correct horse battery staple');
    const second = await hashPassword('correct horse battery staple');
    expect(first).toMatch(/^scrypt\$131072\$8\$1\$/);
    expect(first).not.toBe(second);
    expect(await verifyPassword('correct horse battery staple', first)).toBe(true);
    expect(await verifyPassword('wrong password', first)).toBe(false);
  }, 15_000);
  it('keeps reset responses generic and records password-reset audits', () => {
    const server = fs.readFileSync(path.resolve('server.production.ts'), 'utf8');
    const mailer = fs.readFileSync(path.resolve('server/mailer.ts'), 'utf8');
    expect(server).toContain('password_reset_requested');
    expect(server).toContain('password_reset_completed');
    expect(server).toContain('اگر حسابی با این ایمیل وجود داشته باشد');
    expect(mailer).toContain("process.env.EMAIL_ENABLED === 'true'");
    expect(server).not.toMatch(/console\.(?:log|error)\([^\n]*(?:token|email)/i);
  });
});
