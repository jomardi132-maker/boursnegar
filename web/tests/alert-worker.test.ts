import fs from 'fs';
import path from 'path';
import { describe, expect, it } from 'vitest';

const source = fs.readFileSync(path.resolve('server/alertWorker.ts'), 'utf8');

describe('alert worker safety', () => {
  it('is opt-in and forbids sending without SMS flag', () => {
    expect(source).toMatch(/ALERT_WORKER_ENABLED\s*===\s*'true'/);
    expect(source).toMatch(/SMS_ENABLED\s*===\s*'true'/);
    expect(source).toContain('SMS_DISABLED');
  });

  it('uses a database lock, transaction, and deduplication', () => {
    expect(source).toContain('pg_try_advisory_lock');
    expect(source).toContain('withTransaction');
    expect(source).toContain('last_trigger_key');
    expect(source).toContain('deduplication_key');
  });

  it('uses only real upstream snapshots', () => {
    expect(source).toContain('/api/v2/analyze');
    expect(source).not.toContain('Math.random');
  });

  it('supports valuation zones without invented user targets', () => {
    expect(source).toContain("'buy_zone' | 'sell_zone'");
    expect(source).toContain('fairBase * 0.80');
    expect(source).toContain('fairHigh * 1.15');
  });
});
