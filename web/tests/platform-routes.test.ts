import fs from'fs';import path from'path';import{describe,expect,it}from'vitest';
const source=fs.readFileSync(path.resolve('server/platformRoutes.ts'),'utf8');
describe('platform routes security contract',()=>{
 it.each(['/api/account/overview','/api/account/referrals','/api/alerts'])('protects account route %s',route=>expect(source.slice(source.indexOf(route),source.indexOf(route)+180)).toContain('requireUser'));
 it.each(['/api/admin/payments','/api/admin/users','/api/admin/audit'])('protects admin route %s',route=>{const block=source.slice(source.indexOf(route),source.indexOf(route)+220);expect(block).toContain('requireUser');expect(block).toContain('requireAdmin');});
 it('uses transactions and idempotent ledger references for approvals',()=>{expect(source).toContain('withTransaction');expect(source).toContain('ALREADY_DECIDED');expect(source).toContain('payment:${payment.id}');});
 it('requires CSRF for state changes',()=>{for(const marker of ["app.post('/api/alerts'","app.patch('/api/alerts/:id'","app.delete('/api/alerts/:id'","app.post('/api/admin/payments/:id/decision'"])expect(source.slice(source.indexOf(marker),source.indexOf(marker)+180)).toContain('requireCsrf');});
});
