import { FormEvent, useEffect, useRef, useState } from 'react';
import { ArrowLeft, BarChart3, Database, LogOut, Menu, Search, ShieldCheck, Sparkles, X } from 'lucide-react';
import { DecisionReport, type AnalysisPayload } from './components/DecisionReport';
import { AccountDashboard } from './components/AccountDashboard';
import { LegalModal, type LegalDocument } from './components/LegalModal';
import { StockPage } from './components/StockPage';
import { MarketExplorer } from './components/MarketExplorer';
import './dashboard.css';

export type User = { id: string; email: string | null; mobile: string | null; role: 'user' | 'admin'; credits: number };
type SymbolSuggestion = { symbol: string; legal_name: string; industry: string | null; isin: string };
type MarketOverview = { catalog: { instruments: number }; prices: { rows: number; instruments: number; from_date: string; to_date: string }; disclosures: { rows: number; issuers: number; updated_at: string | null }; analysis: { analyzed: number } };
const csrfStorage = 'boursnegar_csrf';

export async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { credentials: 'same-origin', ...init, headers: { ...(init?.body instanceof FormData ? {} : { 'content-type': 'application/json' }), ...(sessionStorage.getItem(csrfStorage) ? { 'x-csrf-token': sessionStorage.getItem(csrfStorage)! } : {}), ...init?.headers } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || 'در انجام درخواست خطایی رخ داد.');
  return body;
}

export function AppProduction() {
  const [user, setUser] = useState<User | null>(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState<SymbolSuggestion[]>([]);
  const [searchFocused, setSearchFocused] = useState(false);
  const [result, setResult] = useState<AnalysisPayload | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const [legalDocument, setLegalDocument] = useState<LegalDocument | null>(null);
  const [overview, setOverview] = useState<MarketOverview | null>(null);
  const [pendingAnalysis, setPendingAnalysis] = useState('');
  const requestedAnalysisStarted = useRef(false);
  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get('analyze');
    api<{ user: User; csrfToken: string }>('/api/auth/me').then((r) => { sessionStorage.setItem(csrfStorage, r.csrfToken); setUser(r.user); if(requested) setQuery(requested); }).catch(() => { sessionStorage.removeItem(csrfStorage); setUser(null); if(requested){ setQuery(requested); setAuthOpen(true); } });
  }, []);
  useEffect(() => { api<MarketOverview>('/api/market/overview').then(setOverview).catch(()=>setOverview(null)); }, []);
  useEffect(() => {
    const requested = new URLSearchParams(window.location.search).get('analyze')?.trim();
    if (!user || !requested || requestedAnalysisStarted.current) return;
    requestedAnalysisStarted.current = true;
    setQuery(requested);
    void runAnalysis(requested).finally(() => history.replaceState({}, '', window.location.pathname));
  }, [user]);
  useEffect(() => {
    if (!user || !pendingAnalysis || loading) return;
    const symbol = pendingAnalysis;
    setPendingAnalysis('');
    void runAnalysis(symbol);
  }, [user, pendingAnalysis]);
  useEffect(() => { if (new URLSearchParams(window.location.search).has('reset-token')) setAuthOpen(true); }, []);
  useEffect(() => {
    const term = query.trim();
    if (!term) { setSuggestions([]); return; }
    const controller = new AbortController();
    const timer = window.setTimeout(() => {
      api<{ results: SymbolSuggestion[] }>(`/api/symbols/search?q=${encodeURIComponent(term)}`, { signal: controller.signal })
        .then((response) => setSuggestions(response.results))
        .catch(() => setSuggestions([]));
    }, 180);
    return () => { controller.abort(); window.clearTimeout(timer); };
  }, [query]);

  async function runAnalysis(symbolQuery: string) {
    if (!user) return;
    setError('');
    setLoading(true);
    try {
      const response = await api<{ data: AnalysisPayload; analysis: { remainingCredits: number } }>('/api/v2/analyze', { method: 'POST', headers: { 'idempotency-key': crypto.randomUUID() }, body: JSON.stringify({ query: symbolQuery, reportMode: 'latest_codal' }) });
      setResult(response.data);
      setUser({ ...user, credits: response.analysis.remainingCredits });
      requestAnimationFrame(() => document.getElementById('analysis')?.scrollIntoView({ behavior: 'smooth' }));
    } catch (e) { setError(e instanceof Error ? e.message : 'خطای ناشناخته'); }
    finally { setLoading(false); }
  }

  async function resolveSymbol(input: string) {
    const normalized = input.trim().replace(/[يى]/g, 'ی').replace(/ك/g, 'ک');
    const response = await api<{ results: SymbolSuggestion[] }>(`/api/symbols/search?q=${encodeURIComponent(normalized)}`);
    const exact = response.results.find((item) => item.symbol === normalized || item.legal_name === normalized);
    return exact?.symbol || response.results[0]?.symbol || '';
  }

  async function analyze(event: FormEvent) {
    event.preventDefault();
    setError('');
    const symbol = await resolveSymbol(query);
    if (!symbol) { setError('نماد یا شرکت موردنظر پیدا نشد.'); return; }
    if (!user) { window.location.assign(`/s/${encodeURIComponent(symbol)}`); return; }
    await runAnalysis(symbol);
  }

  async function logout() { await api('/api/auth/logout', { method: 'POST', body: '{}' }); sessionStorage.removeItem(csrfStorage); setUser(null); setResult(null); }
  const stockMatch = window.location.pathname.match(/^\/s\/([^/]+)\/?$/);
  if (stockMatch) return <><StockPage symbol={decodeURIComponent(stockMatch[1])} analysis={result} analysisLoading={loading} analysisError={error} onAnalyze={(stockSymbol)=>{ setPendingAnalysis(stockSymbol); if(!user) setAuthOpen(true); }}/>{authOpen && <AuthDialog onClose={() => { setAuthOpen(false); setPendingAnalysis(''); }} onLogin={(next, csrf) => { sessionStorage.setItem(csrfStorage, csrf); setUser(next); setAuthOpen(false); }}/>}</>;
  return <div className="app-shell" dir="rtl">
    <header className="topbar"><a className="brand" href="#top" aria-label="بورس‌نگار"><span className="brand-mark"><BarChart3 /></span><span><b>بورس‌نگار</b><small>تحلیل بنیادی شفاف</small></span></a>
      <nav className={menuOpen ? 'nav open' : 'nav'} aria-label="ناوبری اصلی"><a href="#market">بازار و اسکرینر</a><a href="#method">روش تحلیل</a><a href="#sources">منابع داده</a><a href="#trust">اعتمادپذیری</a></nav>
      <div className="header-actions">{user ? <><button className="credit-pill dashboard-trigger" onClick={()=>setDashboardOpen(true)}>{user.credits.toLocaleString('fa-IR')} اعتبار · پنل من</button><button className="icon-button" onClick={logout} aria-label="خروج"><LogOut /></button></> : <button className="button ghost" onClick={() => setAuthOpen(true)}>ورود / ثبت‌نام</button>}<button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label="منو">{menuOpen ? <X /> : <Menu />}</button></div>
    </header>
    <main id="top">
      <section className="hero"><div className="hero-copy"><span className="eyebrow"><span /> پایگاه تحلیلی مستقل بازار سرمایه</span><h1>هر سهم، یک صفحهٔ<br/><em>شفاف و قابل پیگیری.</em></h1><p>قیمت تاریخی، اسناد کدال و تحلیل بنیادی صنعت‌محور را در یک مسیر روشن ببینید؛ عددها از منبع می‌آیند، نتیجه از مدل مستند.</p>
        <div className="symbol-search"><form className="search-box" onSubmit={analyze}><Search aria-hidden="true"/><label className="sr-only" htmlFor="symbol">نماد یا نام شرکت</label><input id="symbol" value={query} onChange={(e) => setQuery(e.target.value)} onFocus={()=>setSearchFocused(true)} onBlur={()=>window.setTimeout(()=>setSearchFocused(false),120)} placeholder="نام شرکت یا نماد؛ مثلاً مبارکه، فولاد یا وبملت" required maxLength={80} autoComplete="off" aria-autocomplete="list" aria-expanded={searchFocused&&suggestions.length>0}/><button disabled={loading}>{loading ? <span className="spinner"/> : <>{user?'تحلیل کامل':'مشاهده سهم'} <ArrowLeft /></>}</button></form>{searchFocused&&suggestions.length>0&&<div className="symbol-suggestions" role="listbox">{suggestions.map((item)=><button type="button" role="option" key={item.isin} onMouseDown={()=>window.location.assign(`/s/${encodeURIComponent(item.symbol)}`)}><span><b>{item.symbol}</b><small>{item.legal_name}</small></span><em>{item.industry||'بازار سرمایه'}</em></button>)}</div>}</div>
        {error && <div className="error-state" role="alert">{error}</div>}<div className="trust-line"><ShieldCheck/> تاریخچه بازار از ۱۴۰۴ <span/> اطلاعیه‌های رسمی کدال <span/> بدون عدد ساختگی</div></div>
        <div className="hero-panel"><div className="panel-head"><span>وضعیت زندهٔ پایگاه داده</span><span className="live-dot">متصل</span></div><div className="database-number"><strong>{overview ? overview.catalog.instruments.toLocaleString('fa-IR') : '—'}</strong><span>نماد و ابزار فعال</span></div><div className="database-grid"><div><b>{overview ? overview.prices.rows.toLocaleString('fa-IR') : '—'}</b><small>رکورد قیمت روزانه</small></div><div><b>{overview ? overview.disclosures.rows.toLocaleString('fa-IR') : '—'}</b><small>نسخه اطلاعیه کدال</small></div><div><b>{overview ? overview.prices.instruments.toLocaleString('fa-IR') : '—'}</b><small>نماد با تاریخچه ۱۴۰۴</small></div><div><b>{overview ? overview.analysis.analyzed.toLocaleString('fa-IR') : '—'}</b><small>نسخه تحلیل ثبت‌شده</small></div></div><div className="panel-note">این اعداد مستقیماً از پایگاه دادهٔ عملیاتی بورس‌نگار خوانده می‌شوند.</div></div>
      </section>
      <MarketExplorer/>
      <section className="method-section" id="method"><div className="section-heading"><span>روش کار</span><h2>از داده خام تا پاسخ روشن</h2><p>هر نتیجه، مسیر قابل مشاهده‌ای از منبع تا محاسبه دارد.</p></div><div className="steps-grid">{[[Database,'گردآوری','قیمت از BrsApi و گزارش رسمی از کدال'],[BarChart3,'محاسبه','نسبت‌های deterministic با دوره و واحد مشخص'],[Sparkles,'توضیح','پاسخ فارسی محتاطانه و قابل حسابرسی']].map(([Icon,title,text],i)=><article key={String(title)}><span className="step-index">۰{i+1}</span><Icon/><h3>{title as string}</h3><p>{text as string}</p></article>)}</div></section>
      <section className="source-band" id="sources"><div><Database/><span><b>منبع بازار</b><small>BrsApi — قیمت و مشخصات تابلو</small></span></div><div><ShieldCheck/><span><b>منبع مالی</b><small>کدال — صورت‌های مالی رسمی</small></span></div><p>زمان گزارش، وضعیت حسابرسی و تاریخ به‌روزرسانی در هر تحلیل نمایش داده می‌شود.</p></section>
      {loading && <section className="analysis-skeleton" aria-label="در حال تحلیل"><div/><div/><div/></section>}
      {result && <DecisionReport report={result}/>}
      <section className="trust-section" id="trust"><div><span className="eyebrow"><span/> تعهد بورس‌نگار</span><h2>ابهام را پنهان نمی‌کنیم.</h2></div><p>هرجا داده کافی نباشد، وضعیت «نامشخص» همراه با دلیل دقیق نمایش داده می‌شود. این سامانه ابزار آموزشی و تحلیلی است و توصیه سرمایه‌گذاری محسوب نمی‌شود.</p></section>
    </main><footer><b>بورس‌نگار</b><span>صاحب‌امتیاز: محمد جوانمردی راد</span><button onClick={()=>setLegalDocument('terms')}>شرایط استفاده</button><button onClick={()=>setLegalDocument('privacy')}>حریم خصوصی</button><small>© ۱۴۰۵ — مسئولیت تصمیم نهایی سرمایه‌گذاری با کاربر است.</small></footer>
    {dashboardOpen&&user&&<AccountDashboard user={user} onClose={()=>setDashboardOpen(false)} onCredits={(credits)=>setUser({...user,credits})}/>} {authOpen && <AuthDialog onClose={() => setAuthOpen(false)} onLogin={(next, csrf) => { sessionStorage.setItem(csrfStorage, csrf); setUser(next); setAuthOpen(false); }}/>} {legalDocument&&<LegalModal document={legalDocument} onClose={()=>setLegalDocument(null)}/>}</div>;
}

function AuthDialog({ onClose, onLogin }: { onClose: () => void; onLogin: (u: User, csrf: string) => void }) {
  type Mode = 'login' | 'register' | 'verify' | 'forgot' | 'reset';
  const resetToken = new URLSearchParams(window.location.search).get('reset-token') || '';
  const [mode,setMode]=useState<Mode>(resetToken ? 'reset' : 'login');
  const [email,setEmail]=useState(''); const [password,setPassword]=useState(''); const [code,setCode]=useState(''); const [busy,setBusy]=useState(false); const [error,setError]=useState(''); const [notice,setNotice]=useState('');
  const close = () => { if (resetToken) history.replaceState({}, '', window.location.pathname); onClose(); };
  async function submit(e:FormEvent){e.preventDefault();setBusy(true);setError('');setNotice('');try{
    if(mode==='forgot'){const r=await api<{message:string}>('/api/auth/password/forgot',{method:'POST',body:JSON.stringify({email})});setNotice(r.message);return;}
    if(mode==='verify'){const r=await api<{message:string}>('/api/auth/email/verify',{method:'POST',body:JSON.stringify({email,code})});setNotice(r.message);setMode('login');setCode('');return;}
    if(mode==='reset'){const r=await api<{message:string}>('/api/auth/password/reset',{method:'POST',body:JSON.stringify({token:resetToken,password})});history.replaceState({},'',window.location.pathname);setNotice(r.message);setPassword('');setMode('login');return;}
    const endpoint=mode==='register'?'/api/auth/register':'/api/auth/login';
    const r=await api<{user:User;csrfToken:string;verificationRequired?:boolean}>(endpoint,{method:'POST',body:JSON.stringify({email,password})});if(r.verificationRequired){setMode('verify');setNotice('کد تأیید به ایمیل شما ارسال شد.');return;}onLogin(r.user,r.csrfToken);
  }catch(e){setError(e instanceof Error?e.message:'خطا در انجام درخواست');}finally{setBusy(false)}}
  const title=mode==='login'?'ورود به بورس‌نگار':mode==='register'?'ساخت حساب کاربری':mode==='verify'?'تأیید ایمیل':mode==='forgot'?'بازیابی رمز عبور':'تعیین رمز عبور جدید';
  return <div className="modal-backdrop" onMouseDown={(e)=>e.target===e.currentTarget&&close()}><div className="auth-dialog" role="dialog" aria-modal="true" aria-labelledby="auth-title"><button className="close" onClick={close} aria-label="بستن"><X/></button><span className="brand-mark"><ShieldCheck/></span><h2 id="auth-title">{title}</h2><p>{mode==='verify'?'کد ۶ رقمی ارسال‌شده به ایمیل را وارد کنید.':mode==='forgot'?'ایمیل حساب را وارد کنید تا لینک امن بازیابی ارسال شود.':mode==='reset'?'رمز تازه باید دست‌کم ۸ نویسه باشد.':'با ایمیل و رمز عبور امن وارد شوید.'}</p><form onSubmit={submit}>{mode!=='reset'&&<><label htmlFor="auth-email">ایمیل</label><input id="auth-email" dir="ltr" type="email" autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="name@example.com" required/></>} {mode==='verify'&&<><label htmlFor="auth-code">کد تأیید</label><input id="auth-code" dir="ltr" inputMode="numeric" pattern="[0-9]{6}" maxLength={6} value={code} onChange={e=>setCode(e.target.value.replace(/\D/g,''))} required/></>} {mode!=='forgot'&&mode!=='verify'&&<><label htmlFor="auth-password">رمز عبور</label><input id="auth-password" dir="ltr" type="password" minLength={mode==='login'?1:8} maxLength={128} autoComplete={mode==='login'?'current-password':'new-password'} value={password} onChange={e=>setPassword(e.target.value)} required/></>} {error&&<div className="error-state" role="alert">{error}</div>}{notice&&<div className="success-state" role="status">{notice}</div>}<button className="button primary" disabled={busy}>{busy?'لطفاً صبر کنید':mode==='login'?'ورود':mode==='register'?'ساخت حساب':mode==='verify'?'تأیید ایمیل':mode==='forgot'?'ارسال لینک بازیابی':'ثبت رمز جدید'}</button></form><div className="auth-switch">{mode==='verify'&&<><button type="button" onClick={async()=>{setNotice('');try{const r=await api<{message:string}>('/api/auth/email/resend',{method:'POST',body:JSON.stringify({email})});setNotice(r.message)}catch(e){setError(e instanceof Error?e.message:'خطا')}}}>ارسال دوباره کد</button><button type="button" onClick={()=>setMode('login')}>بازگشت به ورود</button></>}{mode==='login'&&<><button type="button" onClick={()=>setMode('forgot')}>رمز را فراموش کرده‌اید؟</button><button type="button" onClick={()=>setMode('register')}>حساب ندارید؟ ثبت‌نام</button></>}{mode==='register'&&<button type="button" onClick={()=>setMode('login')}>حساب دارید؟ وارد شوید</button>}{mode==='forgot'&&<button type="button" onClick={()=>setMode('login')}>بازگشت به ورود</button>}</div><small>رمز عبور به‌صورت hash نگهداری می‌شود و هرگز با ایمیل ارسال یا قابل بازیابی نیست.</small></div></div>;
}
