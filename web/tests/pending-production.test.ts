import fs from 'fs';
import path from 'path';
import { describe, expect, it } from 'vitest';

const server=fs.readFileSync(path.resolve('server.pending-otp.ts'),'utf8');
const ui=fs.readFileSync(path.resolve('src/AppPending.tsx'),'utf8');
describe('Pending OTP production mode',()=>{
  it('rejects every OTP entry point without sending',()=>{
    expect(server).toContain("OTP_PENDING_APPROVAL");
    expect(server).not.toContain('verify/lookup');
    expect(server).toContain("OTP_GATEWAY === 'mock'");
  });
  it('keeps anonymous analysis available',()=>{
    const route=server.slice(server.indexOf("app.post('/api/analyze'"),server.indexOf("app.get('/api/account"));
    expect(route).not.toContain('requireUser');
    expect(route).toContain('anonymous:true');
  });
  it('keeps account and admin authorization',()=>{
    expect(server).toContain("app.get('/api/account/analyses', requireUser");
    expect(server).toContain("app.get('/api/admin/stats', requireUser, requireAdmin");
  });
  it('shows the activation message and all three questions',()=>{
    expect(ui).toContain('ورود پیامکی در حال فعال‌سازی است');
    expect(ui).toContain('[1,2,3].map');
  });
});
