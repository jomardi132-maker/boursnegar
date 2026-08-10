import { describe, expect, it } from 'vitest';
import { normalizeIranMobile } from '../server/auth';

describe('Iranian mobile normalization', () => {
  it.each([
    ['09123456789', '+989123456789'],
    ['989123456789', '+989123456789'],
    ['+989123456789', '+989123456789'],
  ])('normalizes %s', (input, expected) => expect(normalizeIranMobile(input)).toBe(expected));
  it.each(['9123456789', '0912345678', '+981212345678', '09123abc789'])('rejects %s', (input) => expect(normalizeIranMobile(input)).toBeNull());
});
