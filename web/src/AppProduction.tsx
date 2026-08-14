import { FormEvent, useEffect, useMemo, useState } from 'react';
import { ArrowLeft, BarChart3, CheckCircle2, Database, LogOut, Menu, Search, ShieldCheck, Sparkles, X } from 'lucide-react';
import type { QuestionCard, StockHealthCardData } from './types';
import { QuestionCardsRow } from './components/QuestionCardsRow';
import { StatusBanner } from './components/StatusBanner';
import { GoldenSummaryBanner } from './components/GoldenSummaryBanner';
import { ExplanationCardsGrid } from './components/ExplanationCardsGrid';
import { ConclusionAndSources } from './components/ConclusionAndSources';
import { AccountDashboard } from './components/AccountDashboard';
import { LegalModal, type LegalDocument } from './components/LegalModal';
import './dashboard.css';

export type User = { id: string; email: string | null; mobile: string | null; role: 'user' | 'admin'; credits: number };
const csrfStorage = 'boursnegar_csrf';

export async function api<T>(url: string, init?: RequestInit): Promise<T> {
  const response = await fetch(url, { credentials: 'same-origin', ...init, headers: { ...(init?.body instanceof FormData ? {} : { 'content-type': 'application/json' }), ...(sessionStorage.getItem(csrfStorage) ? { 'x-csrf-token': sessionStorage.getItem(csrfStorage)! } : {}), ...init?.headers } });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.error || 'در انجام درخواست خطایی رخ داد.');
  return body;
}

function completeQuestions(data: StockHealthCardData): StockHealthCardData {
  const current = [...(data.questions || [])];
  const third: QuestionCard = {
    id: 3,
    title: '۳) آیا رشد واقعی شرکت از تورم بیشتر است؟',
    subtitle: 'مقایسه دوره جاری با دوره هم‌طول قبلی و نرخ تورم مرجع',
    status: 'mid', statusLabel: 'نامشخص', mainMetricValue: 'داده مقایسه‌ای کافی نیست',
    comparisonDetail: 'API باید درآمد/سود دو دوره قابل‌مقایسه و نرخ تورم دارای منبع و تاریخ ارائه کند.',
    summaryAnswer: 'به‌دلیل نبود داده مقایسه‌ای مستند، درباره رشد واقعی نتیجه‌گیری نمی‌شود.',
  };
  if (!current.some((q) => q.id === 3)) current.push(third);
  return { ...data, questions: [1, 2, 3].map((id) => current.find((q) => q.id === id) || { ...third, id, title: id === 1 ? '۱) آیا بازده سودآوری از سود بانکی بهتر است؟' : id === 2 ? '۲) آیا سود اعلام‌شده همراه با جریان نقد است؟' : third.title }) };
}

export function AppProduction() {
  const [user, setUser] = useState<User | null>(null);
  const [authOpen, setAuthOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<StockHealthCardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [dashboardOpen, setDashboardOpen] = useState(false);
  const [legalDocument, setLegalDocument] = useState<LegalDocument | null>(null);
  useEffect(() => { api<{ user: User }>('/api/auth/me').then((r) => setUser(r.user)).catch(() => setUser(null)); }, []);
  useEffect(() => { if (new URLSearchParams(window.location.search).has('reset-token')) setAuthOpen(true); }, []);
  const questions = useMemo(() => result ? completeQuestions(result) : null, [result]);

  async function analyze(event: FormEvent) {
    event.preventDefault(); setError('');
    if (!user) { setAuthOpen(true); return; }
    setLoading(true);
    try {
      const response = await api<{ data: StockHealthCardData; analysis: { remainingCredits: number } }>('/api/analyze', { method: 'POST', headers: { 'idempotency-key': crypto.randomUUID() }, body: JSON.stringify({ query, reportMode: 'audited' }) });
      setResult(completeQuestions(response.data));
      setUser({ ...user, credits: response.analysis.remainingCredits });
      requestAnimationFrame(() => document.getElementById('analysis')?.scrollIntoView({ behavior: 'smooth' }));
    } catch (e) { setError(e instanceof Error ? e.message : 'خطای ناشناخته'); }
    finally { setLoading(false); }
  }

  async function logout() { await api('/api/auth/logout', { method: 'POST', body: '{}' }); sessionStorage.removeItem(csrfStorage); setUser(null); setResult(null); }
  return <div className="app-shell" dir="rtl">
    <header className="topbar"><a className="brand" href="#top" aria-label="بورس‌نگار"><span className="brand-mark"><BarChart3 /></span><span><b>بورس‌نگار</b><small>تحلیل بنیادی شفاف</small></span></a>
      <nav className={menuOpen ? 'nav open' : 'nav'} aria-label="ناوبری اصلی"><a href="#method">روش تحلیل</a><a href="#sources">منابع داده</a><a href="#trust">اعتمادپذیری</a></nav>
      <div className="header-actions">{user ? <><button className="credit-pill dashboard-trigger" onClick={()=>setDashboardOpen(true)}>{user.credits.toLocaleString('fa-IR')} اعتبار · پنل من</button><button className="icon-button" onClick={logout} aria-label="خروج"><LogOut /></button></> : <button className="button ghost" onClick={() => setAuthOpen(true)}>ورود / ثبت‌نام</button>}<button className="menu-button" onClick={() => setMenuOpen(!menuOpen)} aria-label="منو">{menuOpen ? <X /> : <Menu />}</button></div>
    </header>
    <main id="top">
      <section className="hero"><div className="hero-copy"><span className="eyebrow"><span /> داده واقعی بازار تهران و کدال</span><h1>صورت‌های مالی را<br/><em>قابل فهم</em> ببینید.</h1><p>سه پرسش بنیادی، منابع قابل ردگیری و نتیجه‌ای محتاطانه؛ بدون داده ساختگی و بدون توصیه قطعی خرید یا فروش.</p>
        <form className="search-box" onSubmit={analyze}><Search aria-hidden="true"/><label className="sr-only" htmlFor="symbol">نماد بورسی</label><input id="symbol" value={query} onChange={(e) => setQuery(e.target.value)} placeholder="مثلاً فولاد، شپنا یا فملی" required maxLength={32}/><button disabled={loading}>{loading ? <span className="spinner"/> : <>تحلیل نماد <ArrowLeft /></>}</button></form>
        {error && <div className="error-state" role="alert">{error}</div>}<div className="trust-line"><ShieldCheck/> اطلاعات بازار از BrsApi <span/> صورت‌های مالی از کدال</div></div>
        <div className="hero-panel" aria-hidden="true"><div className="panel-head"><span>نمونه ساختار گزارش</span><span className="live-dot">داده مستند</span></div>{['بازده سودآوری در برابر سود بانکی','کیفیت نقدی سود','رشد واقعی در برابر تورم'].map((x,i)=><div className="metric-row" key={x}><span className="metric-num">۰{i+1}</span><div><b>{x}</b><small>{i===2?'در صورت وجود دوره مقایسه‌ای معتبر':'با ذکر منبع و تاریخ داده'}</small></div><CheckCircle2/></div>)}<div className="panel-note">این نمایش صرفاً ساختار گزارش است و عدد مالی نمونه تولید نمی‌کند.</div></div>
      </section>
      <section className="method-section" id="method"><div className="section-heading"><span>روش کار</span><h2>از داده خام تا پاسخ روشن</h2><p>هر نتیجه، مسیر قابل مشاهده‌ای از منبع تا محاسبه دارد.</p></div><div className="steps-grid">{[[Database,'گردآوری','قیمت از BrsApi و گزارش رسمی از کدال'],[BarChart3,'محاسبه','نسبت‌های deterministic با دوره و واحد مشخص'],[Sparkles,'توضیح','پاسخ فارسی محتاطانه و قابل حسابرسی']].map(([Icon,title,text],i)=><article key={String(title)}><span className="step-index">۰{i+1}</span><Icon/><h3>{title as string}</h3><p>{text as string}</p></article>)}</div></section>
      <section className="source-band" id="sources"><div><Database/><span><b>منبع بازار</b><small>BrsApi — قیمت و مشخصات تابلو</small></span></div><div><ShieldCheck/><span><b>منبع مالی</b><small>کدال — صورت‌های مالی رسمی</small></span></div><p>زمان گزارش، وضعیت حسابرسی و تاریخ به‌روزرسانی در هر تحلیل نمایش داده می‌شود.</p></section>
      {loading && <section className="analysis-skeleton" aria-label="در حال تحلیل"><div/><div/><div/></section>}
      {questions && <section id="analysis" className="analysis-wrap"><div className="analysis-title"><span>گزارش بنیادی</span><h2>{questions.header.fullName} <small>{questions.header.symbol}</small></h2><p>گزارش {questions.header.reportDate} · {questions.header.dataStamp.source}</p></div><QuestionCardsRow questions={questions.questions}/><StatusBanner metrics={questions.statusBanner}/><GoldenSummaryBanner summary={questions.goldenSummary}/><ExplanationCardsGrid cards={questions.explanationCards}/><ConclusionAndSources conclusion={questions.conclusion}/></section>}
      <section className="trust-section" id="trust"><div><span className="eyebrow"><span/> تعهد بورس‌نگار</span><h2>ابهام را پنهان نمی‌کنیم.</h2></div><p>هرجا داده کافی نباشد، وضعیت «نامشخص» همراه با دلیل دقیق نمایش داده می‌شود. این سامانه ابزار آموزشی و تحلیلی است و توصیه سرمایه‌گذاری محسوب نمی‌شود.</p></section>
    </main><footer><b>بورس‌نگار</b><span>صاحب‌امتیاز: محمد جوانمردی راد</span><button onClick={()=>setLegalDocument('terms')}>شرایط استفاده</button><button onClick={()=>setLegalDocument('privacy')}>حریم خصوصی</button><small>© ۱۴۰۵ — مسئولیت تصمیم نهایی سرمایه‌گذاری با کاربر است.</small></footer>
    {dashboardOpen&&user&&<AccountDashboard user={user} onClose={()=>setDashboardOpen(false)} onCredits={(credits)=>setUser({...user,credits})}/>} {authOpen && <AuthDialog onClose={() => setAuthOpen(false)} onLogin={(next, csrf) => { sessionStorage.setItem(csrfStorage, csrf); setUser(next); setAuthOpen(false); }}/>} {legalDocument&&<LegalModal document={legalDocument} onClose={()=>setLegalDocument(null)}/>}</div>;
}

function AuthDialog({ onClose, onLogin }: { onClose: () => void; onLogin: (u: User, csrf: string) => void }) {
  type Mode = 'login' | 'register' | 'forgot' | 'reset';
  const resetToken = new URLSearchParams(window.location.search).get('reset-token') || '';
  const [mode,setMode]=useState<Mode>(resetToken ? 'reset' : 'login');
  const [email,setEmail]=useState(''); const [password,setPassword]=useState(''); const [busy,setBusy]=useState(false); const [error,setError]=useState(''); const [notice,setNotice]=useState('');
  const close = () => { if (resetToken) history.replaceState({}, '', window.location.pathname); onClose(); };
  async function submit(e:FormEvent){e.preventDefault();setBusy(true);setError('');setNotice('');try{
    if(mode==='forgot'){const r=await api<{message:string}>('/api/auth/password/forgot',{method:'POST',body:JSON.stringify({email})});setNotice(r.message);return;}
    if(mode==='reset'){const r=await api<{message:string}>('/api/auth/password/reset',{method:'POST',body:JSON.stringify({token:resetToken,password})});history.replaceState({},'',window.location.pathname);setNotice(r.message);setPassword('');setMode('login');return;}
    const endpoint=mode==='register'?'/api/auth/register':'/api/auth/login';
    const r=await api<{user:User;csrfToken:string}>(endpoint,{method:'POST',body:JSON.stringify({email,password})});onLogin(r.user,r.csrfToken);
  }catch(e){setError(e instanceof Error?e.message:'خطا در انجام درخواست');}finally{setBusy(false)}}
  const title=mode==='login'?'ورود به بورس‌نگار':mode==='register'?'ساخت حساب کاربری':mode==='forgot'?'بازیابی رمز عبور':'تعیین رمز عبور جدید';
  return <div className="modal-backdrop" onMouseDown={(e)=>e.target===e.currentTarget&&close()}><div className="auth-dialog" role="dialog" aria-modal="true" aria-labelledby="auth-title"><button className="close" onClick={close} aria-label="بستن"><X/></button><span className="brand-mark"><ShieldCheck/></span><h2 id="auth-title">{title}</h2><p>{mode==='forgot'?'ایمیل حساب را وارد کنید تا لینک امن بازیابی ارسال شود.':mode==='reset'?'رمز تازه باید دست‌کم ۱۲ نویسه باشد.':'با ایمیل و رمز عبور امن وارد شوید.'}</p><form onSubmit={submit}>{mode!=='reset'&&<><label htmlFor="auth-email">ایمیل</label><input id="auth-email" dir="ltr" type="email" autoComplete="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="name@example.com" required/></>} {mode!=='forgot'&&<><label htmlFor="auth-password">رمز عبور</label><input id="auth-password" dir="ltr" type="password" minLength={mode==='login'?1:12} maxLength={128} autoComplete={mode==='login'?'current-password':'new-password'} value={password} onChange={e=>setPassword(e.target.value)} required/></>} {error&&<div className="error-state" role="alert">{error}</div>}{notice&&<div className="success-state" role="status">{notice}</div>}<button className="button primary" disabled={busy}>{busy?'لطفاً صبر کنید':mode==='login'?'ورود':mode==='register'?'ساخت حساب':mode==='forgot'?'ارسال لینک بازیابی':'ثبت رمز جدید'}</button></form><div className="auth-switch">{mode==='login'&&<><button type="button" onClick={()=>setMode('forgot')}>رمز را فراموش کرده‌اید؟</button><button type="button" onClick={()=>setMode('register')}>حساب ندارید؟ ثبت‌نام</button></>}{mode==='register'&&<button type="button" onClick={()=>setMode('login')}>حساب دارید؟ وارد شوید</button>}{mode==='forgot'&&<button type="button" onClick={()=>setMode('login')}>بازگشت به ورود</button>}</div><small>رمز عبور به‌صورت hash نگهداری می‌شود و هرگز با ایمیل ارسال یا قابل بازیابی نیست.</small></div></div>;
}
