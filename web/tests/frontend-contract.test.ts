import fs from 'fs';
import path from 'path';
import { describe, expect, it } from 'vitest';

const source = fs.readFileSync(path.resolve('src/AppProduction.tsx'), 'utf8');
const reportSource = fs.readFileSync(path.resolve('src/components/DecisionReport.tsx'), 'utf8');
const dashboardSource = fs.readFileSync(path.resolve('src/components/AccountDashboard.tsx'), 'utf8');
const stockSource = fs.readFileSync(path.resolve('src/components/StockPage.tsx'), 'utf8');
const marketSource = fs.readFileSync(path.resolve('src/components/MarketExplorer.tsx'), 'utf8');
describe('analysis UI contract', () => {
  it('always presents the three fundamental questions', () => {
    expect(reportSource).toContain('earnings_vs_bank');
    expect(reportSource).toContain('این شاخص سود تقسیمی نیست');
    expect(reportSource).toContain('نرخ تورم مرجع');
    expect(reportSource).toContain('MARKET_FUNDAMENTAL_DIVERGENCE');
    expect(reportSource).toContain('CAPITAL_ACTION_DATA_GAP');
    expect(reportSource).toContain('cash_quality');
    expect(reportSource).toContain('real_growth');
  });
  it('does not persist user profile or OTP in localStorage', () => expect(source).not.toContain('localStorage'));
  it('states insufficiency instead of inventing comparative data', () => {
    expect(reportSource).toContain('INSUFFICIENT_DATA');
    expect(reportSource).toContain('داده ناکافی');
  });
  it('shows real key fundamentals with report provenance', () => {
    expect(reportSource).toContain('سود هر سهم (EPS)');
    expect(reportSource).toContain('بازده حقوق صاحبان سهام (ROE)');
    expect(reportSource).toContain('نسبت بدهی');
    expect(reportSource).toContain('report.publishedAt');
  });
  it('keeps the dashboard in a loading state until its first payload arrives', () => {
    expect(dashboardSource).toContain('busy || !data');
  });
  it('resolves typed company names and keeps full analysis on the stock page', () => {
    expect(source).toContain('async function resolveSymbol');
    expect(stockSource).toContain('<DecisionReport report={analysis}/>');
    expect(stockSource).toContain('بازده یک‌ماهه');
    expect(stockSource).toContain('بازده شش‌ماهه');
    expect(stockSource).toContain('بازده یک‌ساله');
  });
  it('restores the CSRF token when an existing session is loaded', () => {
    expect(source).toContain("sessionStorage.setItem(csrfStorage, r.csrfToken)");
    expect(source).toContain("api<{ user: User; csrfToken: string }>('/api/auth/me')");
  });
  it('shows a sourced market dashboard and links screener rows to stock pages', () => {
    expect(marketSource).toContain('/api/market/dashboard');
    expect(marketSource).toContain('/api/market/screener');
    expect(marketSource).toContain('محدوده خرید');
    expect(marketSource).toContain('بررسی مشروط');
    expect(marketSource).toContain('fundamental_strength');
    expect(marketSource).toContain('برداشت سریع');
    expect(marketSource).toContain('داده ناقص؛ فعلاً صبر برای تکمیل');
    expect(marketSource).toContain('محدوده خرید ارزش‌گذاری');
    expect(marketSource).toContain('technical_state');
    expect(fs.readFileSync(path.resolve('src/components/StockPage.tsx'), 'utf8')).toContain('سنجه‌های غایب');
    expect(marketSource).toContain('بالاتر از میانگین ۲۰روزه');
    expect(marketSource).toContain('/s/${encodeURIComponent(row.symbol)}');
  });
});
