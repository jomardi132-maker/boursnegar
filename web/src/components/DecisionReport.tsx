import { AlertTriangle, CheckCircle2, Database, ShieldCheck, TrendingUp } from "lucide-react";

export type AnalysisPayload = {
  symbol: string;
  companyName: string | null;
  decision: "BUY" | "HOLD" | "SELL" | "INSUFFICIENT_DATA";
  healthScore: number | null;
  dataCoverage: number;
  confidence: number;
  valuation: null | {
    method: string;
    modelVersion: string;
    fairValueLow: number;
    fairValueBase: number;
    fairValueHigh: number;
    assumptions: Record<string, unknown>;
  };
  analysisState?: "STANDARD" | "MARKET_FUNDAMENTAL_DIVERGENCE" | "TURNAROUND_CANDIDATE" | "CAPITAL_ACTION_DATA_GAP";
  analysisContext?: { financial_periods?: number; monthly_disclosures?: number; price_observations?: number; price_return_90d_percent?: number | null; price_return_365d_percent?: number | null; shares_change_percent?: number | null; corporate_actions?: number };
  references?: { bankDepositRate: number | null; inflationRate: number | null };
  keyMetrics?: Record<string, number | null>;
  report?: { title: string | null; publishedAt: string | null; periodEnd?: string | null; periodLengthMonths?: number | null; audited: boolean; basisNote?: string | null; relatedDisclosures?: Array<{ title: string; publishedAt: string | null; detailUrl?: string | null }> };
  coreQuestions: Record<string, { value: number | null; benchmark: number | null; status: string }>;
  reasons: string[];
  risks: string[];
  criticalWarning: string | null;
  calculatedAt: string;
  staleAfter: string;
  sourceLineage: { codalTracingNo?: string; codalDocument?: string; marketSource?: string };
  policyVersion: string;
  modelVersion: string;
};

const decisionFa = {
  BUY: "خرید",
  HOLD: "نگهداری",
  SELL: "فروش",
  INSUFFICIENT_DATA: "داده ناکافی",
};

const questionLabels: Record<string, string> = {
  earnings_vs_bank: "بازده سودآوری در برابر سپرده بانکی",
  cash_quality: "پوشش نقدی سود عملیاتی",
  real_growth: "رشد واقعی پس از تورم",
};

const metricLabels: Record<string, { label: string; suffix: string }> = {
  eps: { label: "سود هر سهم (EPS)", suffix: " ریال" },
  pe: { label: "نسبت P/E", suffix: "" },
  roe: { label: "بازده حقوق صاحبان سهام (ROE)", suffix: "٪" },
  roa: { label: "بازده دارایی‌ها (ROA)", suffix: "٪" },
  grossMargin: { label: "حاشیه سود ناخالص", suffix: "٪" },
  operatingMargin: { label: "حاشیه سود عملیاتی", suffix: "٪" },
  netMargin: { label: "حاشیه سود خالص", suffix: "٪" },
  debtRatio: { label: "نسبت بدهی", suffix: "٪" },
  cashToProfit: { label: "پوشش نقدی سود", suffix: "٪" },
  revenueGrowth: { label: "رشد درآمد هم‌دوره", suffix: "٪" },
  netProfitGrowth: { label: "رشد سود خالص هم‌دوره", suffix: "٪" },
};

const number = (value: number | null, suffix = "") =>
  value == null ? "نامشخص" : `${value.toLocaleString("fa-IR", { maximumFractionDigits: 1 })}${suffix}`;

const precisePercent = (value: number | null) => value == null
  ? "داده موجود نیست"
  : `${value.toLocaleString("fa-IR", { minimumFractionDigits: value > 0 && value < 0.1 ? 2 : 0, maximumFractionDigits: 2 })}٪`;

const dateFa = (value: string | null | undefined) => value ? new Date(value).toLocaleDateString("fa-IR") : "نامشخص";

export function DecisionReport({ report }: { report: AnalysisPayload }) {
  const actionable = report.decision !== "INSUFFICIENT_DATA";
  const availableMetrics = Object.keys(metricLabels).filter((key) => report.keyMetrics?.[key] != null).length;
  return <section id="analysis" className="decision-report">
    <header className={`decision-hero decision-${report.decision.toLowerCase()}`}>
      <div><small>نتیجه موتور تحلیل نسخه‌دار</small><h2>{report.companyName || report.symbol}</h2><span>{report.symbol}</span><div className="report-badges"><em className={report.report?.audited ? "audited" : "unaudited"}>{report.report?.audited ? "گزارش حسابرسی‌شده" : "گزارش حسابرسی‌نشده"}</em><em>محاسبه {dateFa(report.calculatedAt)}</em></div></div>
      <div className="decision-seal"><small>جمع‌بندی</small><strong>{decisionFa[report.decision]}</strong><em>{actionable ? `اطمینان ${number(report.confidence, "٪")}` : "بدون کسر اعتبار"}</em></div>
    </header>
    <div className="analysis-context"><span><b>مبنای تحلیل:</b> {report.report?.title || "آخرین داده‌های رسمی در دسترس"}{report.report?.periodEnd?` · دوره منتهی به ${report.report.periodEnd}`:""}{report.report?.publishedAt?` · منتشرشده در ${report.report.publishedAt}`:""}</span><span><b>تازگی محاسبه:</b> تا {dateFa(report.staleAfter)}</span></div>
    {report.criticalWarning&&<div className="critical-warning"><AlertTriangle/><span>{report.criticalWarning}</span></div>}
    {report.analysisState==="MARKET_FUNDAMENTAL_DIVERGENCE"&&<div className="report-basis-note"><TrendingUp/><span><b>واگرایی قیمت و بنیاد:</b> بازده ۹۰روزه {precisePercent(report.analysisContext?.price_return_90d_percent??null)} است؛ {(report.analysisContext?.financial_periods??0).toLocaleString("fa-IR")} دوره بنیادی و {(report.analysisContext?.monthly_disclosures??0).toLocaleString("fa-IR")} گزارش ماهانه شناسایی شده، اما داده ماهانه هنوز کامل وارد محاسبه نشده است. نتیجه قطعی صادر نمی‌شود.</span></div>}
    {report.analysisState==="TURNAROUND_CANDIDATE"&&<div className="report-basis-note"><TrendingUp/><span><b>نامزد چرخش سودآوری:</b> بهبود دوره‌ای مشاهده شده، اما برای صدور نتیجه قطعی باید در گزارش بعدی نیز تکرار شود.</span></div>}
    {report.analysisState==="CAPITAL_ACTION_DATA_GAP"&&<div className="report-basis-note"><AlertTriangle/><span><b>نیاز به تطبیق افزایش سرمایه:</b> تعداد سهام حدود {precisePercent(report.analysisContext?.shares_change_percent??null)} تغییر کرده، اما اقدام شرکتی متناظر در داده ساختاریافته موجود نیست؛ قیمت و EPS تا تکمیل تطبیق مبنای نتیجه قطعی نیستند.</span></div>}
    <div className="evidence-strip">
      <article><ShieldCheck/><span><small>امتیاز سلامت</small><b>{number(report.healthScore, " از ۱۰۰")}</b></span></article>
      <article><Database/><span><small>پوشش داده</small><b>{number(report.dataCoverage, "٪")}</b></span></article>
      <article><CheckCircle2/><span><small>اطمینان محاسبه</small><b>{number(report.confidence, "٪")}</b></span></article>
    </div>
    {report.keyMetrics&&<section className="fundamental-metrics"><header><div><small>اعداد استخراج‌شده از صورت مالی</small><h3>شاخص‌های بنیادی کلیدی</h3><em>{availableMetrics.toLocaleString("fa-IR")} شاخص از گزارش استخراج شده</em></div>{report.report&&<span>{report.report.audited?"حسابرسی‌شده":"حسابرسی‌نشده"}{report.report.publishedAt?` · ${report.report.publishedAt}`:""}</span>}</header>{report.report?.basisNote&&<div className="report-basis-note"><AlertTriangle/><span>{report.report.basisNote}</span></div>}{report.report?.relatedDisclosures?.length&&<div className="report-basis-note"><AlertTriangle/><span>اطلاعیه توضیحی/اصلاحیه مرتبط وجود دارد و باید بررسی شود: {report.report.relatedDisclosures.slice(0,2).map((d)=>d.title).join("، ")}</span></div>}<div>{Object.entries(metricLabels).map(([key,meta])=>{const value=report.keyMetrics?.[key];return <article key={key} data-missing={value==null}><small>{meta.label}</small><strong>{value==null?"داده موجود نیست":number(value,meta.suffix)}</strong></article>;})}</div>{report.report?.title&&<p>{report.report.title}</p>}</section>}
    {report.valuation&&<section className="valuation-panel"><div><small>ارزش منصفانه سناریویی ـ ریال به‌ازای هر سهم</small><h3>{number(report.valuation.fairValueBase)}</h3><p>مدل {report.valuation.method} · نسخه {report.valuation.modelVersion}{typeof report.valuation.assumptions?.multiple==="number"?` · فرض P/E برابر ${number(report.valuation.assumptions.multiple as number)}`:""}</p></div><div className="valuation-range"><span><small>سناریوی محتاطانه</small><b>{number(report.valuation.fairValueLow)}</b></span><i/><span><small>سناریوی خوش‌بینانه</small><b>{number(report.valuation.fairValueHigh)}</b></span></div></section>}
    <section className="question-grid">{Object.entries(report.coreQuestions).map(([key,item])=>{
      const detail = key==="earnings_vs_bank"
        ? `نرخ سپرده مرجع: ${precisePercent(report.references?.bankDepositRate ?? item.benchmark)}`
        : key==="cash_quality"
        ? (item.value==null ? "صورت جریان وجوه نقد این دوره موجود نیست؛ این شاخص سود تقسیمی نیست." : "جریان نقد عملیاتی ÷ سود خالص؛ این شاخص سود تقسیمی نیست.")
        : item.value==null
        ? `رشد هم‌دوره موجود نیست؛ نرخ تورم مرجع: ${precisePercent(report.references?.inflationRate ?? null)}`
        : `پس از کسر اثر تورم ${precisePercent(report.references?.inflationRate ?? null)}`;
      return <article key={key} data-status={item.status}><small>{questionLabels[key]||key}</small><strong>{precisePercent(item.value)}</strong><p>{detail}</p><span>{item.status==="PASS"?"عبور از معیار":item.status==="FAIL"?"پایین‌تر از معیار":"داده ناکافی برای محاسبه"}</span></article>;
    })}</section>
    <div className="decision-details"><section><h3><TrendingUp/> دلایل اصلی</h3><ul>{report.reasons.map((reason)=><li key={reason}>{reason}</li>)}</ul></section><section><h3><AlertTriangle/> ریسک‌ها و محدودیت‌ها</h3><ul>{report.risks.map((risk)=><li key={risk}>{risk}</li>)}</ul></section></div>
    <footer className="report-lineage"><span>سیاست: {report.policyVersion}</span><span>موتور: {report.modelVersion}</span><span>منبع بازار: {report.sourceLineage.marketSource||"نامشخص"}</span>{report.sourceLineage.codalDocument&&<a href={report.sourceLineage.codalDocument} target="_blank" rel="noreferrer">مشاهده سند کدال</a>}</footer>
  </section>;
}
