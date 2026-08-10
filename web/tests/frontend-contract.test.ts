import fs from 'fs';
import path from 'path';
import { describe, expect, it } from 'vitest';

const source = fs.readFileSync(path.resolve('src/AppProduction.tsx'), 'utf8');
describe('analysis UI contract', () => {
  it('always presents the three fundamental questions', () => {
    expect(source).toContain('[1, 2, 3].map');
    expect(source).toContain('آیا رشد واقعی شرکت از تورم بیشتر است؟');
  });
  it('does not persist user profile or OTP in localStorage', () => expect(source).not.toContain('localStorage'));
  it('states insufficiency instead of inventing comparative data', () => expect(source).toContain('داده مقایسه‌ای کافی نیست'));
});
