import { useEffect, useMemo, useState, type CSSProperties } from "react";
import { ArrowRight, BarChart3, CalendarDays, Database, ExternalLink, FileText, ShieldCheck, TrendingDown, TrendingUp } from "lucide-react";
import { api } from "../AppProduction";
import { DecisionReport, type AnalysisPayload } from "./DecisionReport";
import { Comments } from "./Comments";

type Price = { trading_date: string; trading_date_jalali: string; close: string | null; adjusted_close: string | null; volume: string | null; value: string | null; trade_count: number | null };
type Payload = {
  stock: { symbol: string; legal_name: string; isin: string; industry: string | null; model_family: string | null };
  latest: Price | null; returns: { oneMonth: number | null; sixMonths: number | null; oneYear: number | null }; prices: Price[];
  disclosures: Array<{ source_disclosure_id: string; title: string; published_date_jalali: string | null; is_audited: boolean | null; detail_url: string | null }>;
  snapshot: null | { decision: string; score: string | null; coverage: string; confidence: string; fair_value_low: string | null; fair_value_base: string | null; fair_value_high: string | null; calculated_at: string; top_reasons: string[]; top_risks: string[] };
};

const fa = (value: unknown, digits = 0) => value == null ? "—" : Number(value).toLocaleString("fa-IR", { maximumFractionDigits: digits });
const decisionFa: Record<string, string> = { BUY: "خرید", HOLD: "نگهداری", SELL: "فروش", INSUFFICIENT_DATA: "داده ناکافی" };

export function StockPage({ symbol, user, onLogin, onAnalyze, analysis, analysisLoading, analysisError }: { symbol: string; user: import("../AppProduction").User | null; onLogin:()=>void; onAnalyze: (symbol: string) => void; analysis: AnalysisPayload | null; analysisLoading: boolean; analysisError: string }) {
  const [data, setData] = useState<Payload | null>(null);
  const [error, setError] = useState("");
  useEffect(() => {
    setData(null); setError("");
    api<Payload>(`/api/stocks/${encodeURIComponent(symbol)}`).then(setData).catch((e) => setError(e instanceof Error ? e.message : "خطا در دریافت اطلاعات"));
  }, [symbol]);
  useEffect(() => {
    if (!data) return;
    document.title = `${data.stock.symbol} | ${data.stock.legal_name} — بورس‌نگار`;
    let meta = document.querySelector('meta[name="description"]');
    if (!meta) { meta = document.createElement("meta"); meta.setAttribute("name", "description"); document.head.appendChild(meta); }
    meta.setAttribute("content", `قیمت، نمودار، اطلاعیه‌های کدال و تحلیل بنیادی ${data.stock.symbol} — ${data.stock.legal_name}`);
    let canonical = document.querySelector('link[rel="canonical"]') as HTMLLinkElement | null;
    if (!canonical) { canonical = document.createElement("link"); canonical.rel = "canonical"; document.head.appendChild(canonical); }
    canonical.href = `https://boursnegar.ir/s/${encodeURIComponent(data.stock.symbol)}`;
    let structured = document.getElementById("stock-structured-data") as HTMLScriptElement | null;
    if (!structured) { structured = document.createElement("script"); structured.id="stock-structured-data"; structured.type="application/ld+json"; document.head.appendChild(structured); }
    structured.textContent = JSON.stringify({ "@context":"https://schema.org", "@type":"Dataset", name:`داده بازار و کدال ${data.stock.symbol}`, description:meta.getAttribute("content"), url:canonical.href, creator:{"@type":"Organization",name:"بورس‌نگار"}, temporalCoverage:"2025-03-21/..", variableMeasured:["قیمت پایانی","حجم معاملات","اطلاعیه‌های کدال"] });
  }, [data]);
  if (error) return <main className="stock-page"><div className="stock-error"><b>این صفحه در دسترس نیست</b><span>{error}</span><a href="/">بازگشت به بورس‌نگار</a></div></main>;
  if (!data) return <main className="stock-page"><div className="stock-loading"><i/><i/><i/></div></main>;
  const chartReturn = data.returns.oneYear ?? data.returns.sixMonths ?? data.returns.oneMonth;
  const positive = Number(chartReturn || 0) >= 0;
  return <div className="stock-shell" dir="rtl">
    <header className="stock-topbar"><a href="/" className="brand"><span className="brand-mark"><BarChart3/></span><span><b>بورس‌نگار</b><small>مرجع تحلیلی بازار ایران</small></span></a><a href="/" className="back-home"><ArrowRight/> جست‌وجوی سهم دیگر</a></header>
    <main className="stock-page">
      <section className="stock-identity"><div><span className="stock-symbol">{data.stock.symbol}</span><div><h1 style={{color:"var(--navy)"}}>{data.stock.legal_name}</h1><p>{data.stock.industry || "بازار سرمایه"} · {data.stock.isin}</p></div></div><button disabled={analysisLoading} onClick={() => onAnalyze(data.stock.symbol)}>{analysisLoading ? "در حال تحلیل…" : "تحلیل بنیادی کامل"}</button></section>
      <section className="market-strip">
        <Metric label="آخرین قیمت" value={`${fa(data.latest?.adjusted_close)} ریال`} detail={data.latest?.trading_date_jalali || "—"}/>
        <ReturnMetric label="بازده یک‌ماهه" value={data.returns.oneMonth}/>
        <ReturnMetric label="بازده شش‌ماهه" value={data.returns.sixMonths}/>
        <ReturnMetric label="بازده یک‌ساله" value={data.returns.oneYear}/>
        <Metric label="حجم آخرین روز" value={fa(data.latest?.volume)} detail={`${fa(data.latest?.trade_count)} معامله`}/>
        <Metric label="پوشش تاریخچه" value={`${fa(data.prices.length)} روز`} detail="از ابتدای ۱۴۰۴"/>
      </section>
      <section className="stock-grid">
        <article className="chart-card"><header><div><span>روند قیمت پایانی</span><h2>عملکرد یک‌سال اخیر</h2></div><span className={positive ? "trend positive" : "trend negative"}>{positive ? <TrendingUp/> : <TrendingDown/>}{fa(chartReturn,1)}٪</span></header><PriceChart prices={data.prices}/><footer><span><i className="legend-price"/> قیمت پایانی (ریال)</span><span>منبع: BrsApi / TSETMC</span></footer></article>
        <SnapshotCard snapshot={data.snapshot}/>
      </section>
      {analysisError && <div className="error-state" role="alert">{analysisError}</div>}
      {analysisLoading && <section className="analysis-skeleton" aria-label="در حال تحلیل"><div/><div/><div/></section>}
      {analysis && <DecisionReport report={analysis}/>}
      <section className="disclosure-section"><header><div><span>اسناد رسمی</span><h2>آخرین اطلاعیه‌های کدال</h2></div><FileText/></header>{data.disclosures.length ? <div className="disclosure-list">{data.disclosures.map((item) => <a key={item.source_disclosure_id} href={item.detail_url || `https://codal.ir/ReportList.aspx?search&Symbol=${encodeURIComponent(data.stock.symbol)}`} target="_blank" rel="noreferrer"><span className="doc-icon"><FileText/></span><span><b>{item.title}</b><small><CalendarDays/> {item.published_date_jalali || "تاریخ نامشخص"} {item.is_audited ? "· حسابرسی‌شده" : ""}</small></span><ExternalLink/></a>)}</div> : <div className="empty-docs">هنوز اطلاعیه‌ای برای این نماد وارد نشده است.</div>}</section>
      <Comments kind="symbol_comment" symbol={data.stock.symbol} user={user} onLogin={onLogin}/>
      <section className="stock-disclaimer"><ShieldCheck/><p><b>داده را از نتیجه جدا می‌کنیم.</b><br/>قیمت و اطلاعیه‌ها مستقیماً از منابع بازار گردآوری شده‌اند. برچسب تحلیلی توصیهٔ خرید یا فروش نیست و در نبود دادهٔ کافی نمایش داده نمی‌شود.</p></section>
    </main>
  </div>;
}

function Metric({ label, value, detail, tone = "" }: { label: string; value: string; detail: string; tone?: string }) { return <article><small>{label}</small><strong className={tone}>{value}</strong><span>{detail}</span></article>; }

function ReturnMetric({ label, value }: { label: string; value: number | null }) {
  const tone = value == null ? "" : value >= 0 ? "positive" : "negative";
  return <Metric label={label} value={value == null ? "داده ناکافی" : `${fa(value, 1)}٪`} detail="بر مبنای قیمت تعدیل‌شده" tone={tone}/>;
}

function SnapshotCard({ snapshot }: { snapshot: Payload["snapshot"] }) {
  if (!snapshot) return <article className="snapshot-card empty"><Database/><h2>هنوز تصمیم تحلیلی ثبت نشده</h2><p>برای دریافت نتیجهٔ خرید، نگهداری یا فروش، «تحلیل بنیادی کامل» را انتخاب کنید.</p></article>;
  return <article className={`snapshot-card ${snapshot.decision?.toLowerCase()}`}><header><span>آخرین تحلیل ثبت‌شده</span><em>{decisionFa[snapshot.decision] || snapshot.decision}</em></header><div className="score-ring" style={{"--score": `${Number(snapshot.score || 0) * 3.6}deg`} as CSSProperties}><strong>{fa(snapshot.score,0)}</strong><small>امتیاز سلامت</small></div><div className="snapshot-metrics"><span>پوشش داده <b>{fa(snapshot.coverage,0)}٪</b></span><span>اطمینان <b>{fa(snapshot.confidence,0)}٪</b></span></div>{snapshot.fair_value_base && <div className="fair-band"><small>ارزش منصفانهٔ سناریوی پایه</small><b>{fa(snapshot.fair_value_base)} ریال</b><span>{fa(snapshot.fair_value_low)} تا {fa(snapshot.fair_value_high)}</span></div>}<small className="snapshot-date">محاسبه: {new Date(snapshot.calculated_at).toLocaleString("fa-IR")}</small></article>;
}

function PriceChart({ prices }: { prices: Price[] }) {
  const points = useMemo(() => {
    const latestDate = prices.at(-1) ? new Date(prices.at(-1)!.trading_date) : null;
    const cutoff = latestDate ? new Date(latestDate) : null;
    cutoff?.setUTCFullYear(cutoff.getUTCFullYear() - 1);
    const visible = cutoff ? prices.filter(p => new Date(p.trading_date) >= cutoff) : prices;
    const values = visible.map(p => Number(p.adjusted_close ?? p.close)).filter(Number.isFinite);
    if (values.length < 2) return { line: "", area: "", min: 0, max: 0 };
    const min = Math.min(...values), max = Math.max(...values), spread = max - min || 1;
    const coords = values.map((v, i) => `${(i/(values.length-1))*900},${260-((v-min)/spread)*220}`);
    return { line: `M${coords.join(" L")}`, area: `M0,280 L${coords.join(" L")} L900,280 Z`, min, max };
  }, [prices]);
  if (!points.line) return <div className="chart-empty">دادهٔ کافی برای نمودار وجود ندارد.</div>;
  return <div className="price-chart"><svg viewBox="0 0 900 300" preserveAspectRatio="none" role="img" aria-label="نمودار قیمت سهم"><defs><linearGradient id="chartFill" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#15b8a6" stopOpacity=".32"/><stop offset="100%" stopColor="#15b8a6" stopOpacity="0"/></linearGradient></defs>{[60,115,170,225,280].map(y => <line key={y} x1="0" y1={y} x2="900" y2={y} className="grid-line"/>)}<path d={points.area} fill="url(#chartFill)"/><path d={points.line} className="price-line"/></svg><span className="chart-max">{fa(points.max)}</span><span className="chart-min">{fa(points.min)}</span></div>;
}
