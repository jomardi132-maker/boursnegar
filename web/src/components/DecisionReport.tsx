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
  cash_quality: "کیفیت نقدی سود",
  real_growth: "رشد واقعی پس از تورم",
};

const number = (value: number | null, suffix = "") =>
  value == null ? "نامشخص" : `${value.toLocaleString("fa-IR", { maximumFractionDigits: 1 })}${suffix}`;

export function DecisionReport({ report }: { report: AnalysisPayload }) {
  const actionable = report.decision !== "INSUFFICIENT_DATA";
  return <section id="analysis" className="decision-report">
    <header className={`decision-hero decision-${report.decision.toLowerCase()}`}>
      <div><small>نتیجه موتور تحلیل نسخه‌دار</small><h2>{report.companyName || report.symbol}</h2><span>{report.symbol}</span></div>
      <div className="decision-seal"><small>جمع‌بندی</small><strong>{decisionFa[report.decision]}</strong><em>{actionable ? `اطمینان ${number(report.confidence, "٪")}` : "بدون کسر اعتبار"}</em></div>
    </header>
    {report.criticalWarning&&<div className="critical-warning"><AlertTriangle/><span>{report.criticalWarning}</span></div>}
    <div className="evidence-strip">
      <article><ShieldCheck/><span><small>امتیاز سلامت</small><b>{number(report.healthScore, " از ۱۰۰")}</b></span></article>
      <article><Database/><span><small>پوشش داده</small><b>{number(report.dataCoverage, "٪")}</b></span></article>
      <article><CheckCircle2/><span><small>اطمینان محاسبه</small><b>{number(report.confidence, "٪")}</b></span></article>
    </div>
    {report.valuation&&<section className="valuation-panel"><div><small>ارزش منصفانه سناریویی ـ ریال به‌ازای هر سهم</small><h3>{number(report.valuation.fairValueBase)}</h3><p>مدل {report.valuation.method} · نسخه {report.valuation.modelVersion}</p></div><div className="valuation-range"><span><small>سناریوی محتاطانه</small><b>{number(report.valuation.fairValueLow)}</b></span><i/><span><small>سناریوی خوش‌بینانه</small><b>{number(report.valuation.fairValueHigh)}</b></span></div></section>}
    <section className="question-grid">{Object.entries(report.coreQuestions).map(([key,item])=><article key={key} data-status={item.status}><small>{questionLabels[key]||key}</small><strong>{number(item.value,"٪")}</strong><p>مرجع: {number(item.benchmark,"٪")}</p><span>{item.status==="PASS"?"عبور از معیار":item.status==="FAIL"?"پایین‌تر از معیار":"داده ناکافی"}</span></article>)}</section>
    <div className="decision-details"><section><h3><TrendingUp/> دلایل اصلی</h3><ul>{report.reasons.map((reason)=><li key={reason}>{reason}</li>)}</ul></section><section><h3><AlertTriangle/> ریسک‌ها و محدودیت‌ها</h3><ul>{report.risks.map((risk)=><li key={risk}>{risk}</li>)}</ul></section></div>
    <footer className="report-lineage"><span>سیاست: {report.policyVersion}</span><span>موتور: {report.modelVersion}</span><span>منبع بازار: {report.sourceLineage.marketSource||"نامشخص"}</span>{report.sourceLineage.codalDocument&&<a href={report.sourceLineage.codalDocument} target="_blank" rel="noreferrer">مشاهده سند کدال</a>}</footer>
  </section>;
}
