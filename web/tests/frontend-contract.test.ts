import fs from 'fs';
import path from 'path';
import { describe, expect, it } from 'vitest';

const source = fs.readFileSync(path.resolve('src/AppProduction.tsx'), 'utf8');
const reportSource = fs.readFileSync(path.resolve('src/components/DecisionReport.tsx'), 'utf8');
describe('analysis UI contract', () => {
  it('always presents the three fundamental questions', () => {
    expect(reportSource).toContain('earnings_vs_bank');
    expect(reportSource).toContain('cash_quality');
    expect(reportSource).toContain('real_growth');
  });
  it('does not persist user profile or OTP in localStorage', () => expect(source).not.toContain('localStorage'));
  it('states insufficiency instead of inventing comparative data', () => {
    expect(reportSource).toContain('INSUFFICIENT_DATA');
    expect(reportSource).toContain('داده ناکافی');
  });
});
