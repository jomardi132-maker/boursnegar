/**
 * این فایل جایگزین کامل server/tsetmc.ts + server/codal.ts + server/financialEngine.ts
 * قدیمی است. برخلاف نسخه‌ی قبلی، اینجا هیچ داده‌ی ساختگی/hardcoded وجود ندارد.
 *
 * منبع داده: سرویس Python (FastAPI) که روی پورت ۸۰۰۱ همین سرور اجرا می‌شود و
 * واقعاً به کدال و تستمسی/BrsApi وصل می‌شود.
 *
 * تصمیم مهم: بخش‌های smartRecommendation (محدوده خرید/فروش) و peSimulation
 * (شبیه‌سازی رشد) عمداً تولید نمی‌شوند، چون هنوز روش‌شناسی واقعی و مستندی
 * برایشان نداریم. نسخه‌ی قبلی این‌ها را با درصدهای دلخواه هاردکد می‌کرد که
 * برای یک ابزار تحلیل مالی واقعی گمراه‌کننده و غیرمسئولانه است.
 */

import type {
  StockHealthCardData,
  IndustryType,
  StatusType,
  StatusBannerMetric,
  ExplanationCard,
  QuestionCard,
} from '../src/types';
import { pool } from './postgres';

const PYTHON_API_BASE = process.env.PYTHON_API_BASE || 'http://localhost:8001';

export class UpstreamAnalysisError extends Error {}

async function referenceNumber(name: string) {
  const keys=[`${name}_percent`,`${name}_source`,`${name}_as_of`];
  const result=await pool.query(`SELECT key,value FROM system_settings WHERE key=ANY($1::text[])`,[keys]);
  const values=Object.fromEntries(result.rows.map(row=>[row.key,row.value]));
  const percent=Number(values[keys[0]]);
  const source=typeof values[keys[1]]==='string'?values[keys[1]]:'';
  const asOf=typeof values[keys[2]]==='string'?values[keys[2]]:'';
  return Number.isFinite(percent)&&percent>=0&&source&&/^\d{4}-\d{2}-\d{2}$/.test(asOf)?{percent,source,asOf}:null;
}

// نگاشت دسته‌بندی صنعت تستمسی به enum داخلی فرانت‌اند
const INDUSTRY_MAP: Record<string, IndustryType> = {
  'بانک‌ها و موسسات اعتباری': 'bank',
  'بیمه و صندوق بازنشستگی به جز تامین اجتماعی': 'insurance',
  'سایر واسطه‌گری‌های مالی': 'leasing',
  'فعالیت‌های کمکی به نهادهای مالی واسط': 'leasing',
  'شرکت‌های چند رشته‌ای صنعتی': 'holding',
  'سرمایه‌گذاری‌ها': 'holding',
  'خدمات فنی و مهندسی': 'services',
};

function mapIndustry(category: string | null | undefined): { type: IndustryType; title: string } {
  const title = category || 'بورس تهران';
  const type = (category && INDUSTRY_MAP[category]) || 'manufacturing';
  return { type, title };
}

function formatMarketCap(rials: number | null | undefined): string {
  if (!rials) return 'نامشخص';
  const tomanBillion = rials / 10 / 1_000_000_000; // ریال -> تومان -> میلیارد تومان
  if (tomanBillion >= 1000) {
    return `${(tomanBillion / 1000).toFixed(1)} هزار میلیارد تومان`;
  }
  return `${tomanBillion.toFixed(0)} میلیارد تومان`;
}

function fmtNum(n: number | null | undefined, digits = 0): string {
  if (n === null || n === undefined) return 'نامشخص';
  return n.toLocaleString('fa-IR', { maximumFractionDigits: digits });
}

function statusFromNote(note: string): StatusType {
  if (note.includes('خوب') || note.includes('بالا') || note.includes('کم‌ریسک') || note.includes('طبیعی')) {
    return 'good';
  }
  if (note.includes('متوسط') || note.includes('نیازمند بررسی') || note.includes('کمی بالاتر')) {
    return 'mid';
  }
  return 'bad';
}

/**
 * فراخوانی سرویس Python واقعی و دریافت تحلیل خام.
 */
async function fetchRealAnalysis(symbol: string, reportMode: 'audited' | 'latest_codal'): Promise<any> {
  const url = `${PYTHON_API_BASE}/api/analyze/${encodeURIComponent(symbol)}?report_mode=${reportMode}`;
  const resp = await fetch(url, { signal: AbortSignal.timeout(30000) });

  if (!resp.ok) {
    const body = await resp.json().catch(() => ({}));
    throw new UpstreamAnalysisError(body.detail || `خطای سرویس داده (کد ${resp.status})`);
  }

  return resp.json();
}

export async function generateV2Analysis(
  symbol: string,
  reportMode: "audited" | "latest_codal",
) {
  const response = await fetch(`${PYTHON_API_BASE}/api/v2/analyze`, {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ query: symbol, reportMode }),
    signal: AbortSignal.timeout(45_000),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok)
    throw new UpstreamAnalysisError(
      body.detail || `خطای سرویس داده (کد ${response.status})`,
    );
  return body.data;
}

/**
 * تبدیل پاسخ خام سرویس Python به فرمت StockHealthCardData که کامپوننت‌های
 * React از قبل انتظارش را دارند.
 */
export async function generateRealHealthCard(
  symbolInput: string,
  reportMode: 'audited' | 'latest_codal' = 'audited'
): Promise<StockHealthCardData> {
  const symbol = symbolInput.trim().replace(/^نماد\s+/, '');
  const raw = await fetchRealAnalysis(symbol, reportMode);

  const live = raw.live_price || null;
  const metrics = raw.financial_metrics || {};
  const ratios = raw.ratios || {};
  const health = raw.health || { flags: [], industry_classified_as: null };

  const { type: industryType, title: industryTitle } = mapIndustry(live?.market_category);

  const currentPrice = live?.last_price ?? live?.closing_price ?? 0;
  const peDisplay = ratios.pe_ratio != null ? String(ratios.pe_ratio) : 'نامشخص';

  // --- Header ---
  const header: StockHealthCardData['header'] = {
    symbol,
    fullName: raw.company_name || live?.full_name || symbol,
    industry: industryType,
    industryTitle,
    financialReportTitle: raw.report_used?.title || 'آخرین صورت مالی رسمی کدال',
    currentPrice,
    peRatio: peDisplay,
    marketCap: formatMarketCap(live?.market_cap),
    reportDate: raw.report_used?.publish_datetime || '',
    codalAuditStatus: raw.report_used?.title?.includes('حسابرسی') ? 'حسابرسی‌شده' : 'گزارش رسمی کدال',
    dataStamp: {
      source: live
        ? 'داده‌ی زنده‌ی بازار (BrsApi) و صورت مالی رسمی کدال'
        : 'صورت مالی رسمی کدال (نماد در حال حاضر بدون قیمت زنده - احتمالاً تعلیق/متوقف)',
      updatedAt: live?.last_trade_time || raw.report_used?.publish_datetime || '',
      verificationCode: `REAL-${symbol}-${raw.report_used?.tracing_no || ''}`,
    },
  };

  // --- Question Cards (فقط با داده‌ی واقعی؛ اگر داده نبود صادقانه اعلام می‌کنیم) ---
  const questions: QuestionCard[] = [];
  const bankReference=await referenceNumber('bank_deposit_rate');

  if (ratios.earnings_yield_percent != null && bankReference) {
    const bankYield = bankReference.percent;
    const isBetter = ratios.earnings_yield_percent > bankYield;
    questions.push({
      id: 1,
      title: '۱) آیا بازده سودآوری از سود بانکی بهتر است؟',
      subtitle: `بازده معکوس P/E (${ratios.earnings_yield_percent}٪) در برابر سود سپرده بانکی (${bankYield}٪)`,
      status: isBetter ? 'good' : 'mid',
      statusLabel: isBetter ? 'خوب' : 'متوسط',
      mainMetricValue: `P/E: ${peDisplay} | بازده سود: ${ratios.earnings_yield_percent}٪`,
      comparisonDetail: `نرخ سود بانکی مرجع: ${bankYield}٪ · منبع: ${bankReference.source} · تاریخ داده: ${bankReference.asOf}`,
      summaryAnswer: isBetter
        ? `بله. با P/E فعلی معادل ${peDisplay}، بازده سودآوری این سهم از سود سپرده بانکی بالاتر است.`
        : `بازده این سهم (${ratios.earnings_yield_percent}٪) فاصله‌ی زیادی با سود بانکی ندارد؛ نیاز به بررسی بیشتر دارد.`,
    });
  } else {
    questions.push({id:1,title:'۱) آیا بازده سودآوری از سود بانکی بهتر است؟',subtitle:'مقایسه بازده معکوس P/E با نرخ رسمی و تاریخ‌دار سپرده بانکی',status:'mid',statusLabel:'نامشخص',mainMetricValue:ratios.earnings_yield_percent!=null?`بازده سود: ${ratios.earnings_yield_percent}٪`:'بازده سود در دسترس نیست',comparisonDetail:'نرخ سود بانکی مرجع دارای منبع و تاریخ در تنظیمات ثبت نشده است.',summaryAnswer:'تا زمان ثبت نرخ بانکی رسمی همراه با منبع و تاریخ، نتیجه‌گیری انجام نمی‌شود.'});
  }

  if (ratios.cash_to_profit_ratio_percent != null) {
    const good = ratios.cash_to_profit_ratio_percent >= 80;
    questions.push({
      id: 2,
      title: '۲) آیا سود اعلام‌شده واقعی و همراه با جریان نقد است؟',
      subtitle: 'نسبت جریان نقد عملیاتی به سود خالص (از صورت مالی رسمی کدال)',
      status: good ? 'good' : 'mid',
      statusLabel: good ? 'خوب' : 'متوسط',
      mainMetricValue: `نسبت جریان نقد به سود خالص: ${ratios.cash_to_profit_ratio_percent}٪`,
      comparisonDetail: 'آستانه‌ی مطلوب معمول: بالای ۸۰٪',
      summaryAnswer: good
        ? `بله. حدود ${ratios.cash_to_profit_ratio_percent}٪ از سود خالص با جریان نقد عملیاتی پوشش داده شده است.`
        : `بخشی از سود هنوز به نقد تبدیل نشده (${ratios.cash_to_profit_ratio_percent}٪ پوشش)؛ نیاز به بررسی کیفیت مطالبات دارد.`,
    });
  } else {
    questions.push({
      id: 2,
      title: '۲) آیا سود اعلام‌شده واقعی و همراه با جریان نقد است؟',
      subtitle: 'داده‌ی جریان نقد عملیاتی از این صورت مالی قابل استخراج نبود',
      status: 'mid',
      statusLabel: 'نامشخص',
      mainMetricValue: 'داده در دسترس نیست',
      comparisonDetail: 'فرمت این گزارش خاص شامل ردیف صورت جریان وجه نقد به‌شکل قابل‌تشخیص نبود',
      summaryAnswer: 'برای این نماد، در گزارش فعلی امکان استخراج خودکار جریان نقد عملیاتی وجود نداشت.',
    });
  }

  const inflationReference=await referenceNumber('inflation_rate');
  const comparison=raw.period_comparison;
  if(comparison?.revenue_growth_percent!=null&&inflationReference){
    const nominal=Number(comparison.revenue_growth_percent);
    const real=((1+nominal/100)/(1+inflationReference.percent/100)-1)*100;
    const better=real>0;
    questions.push({id:3,title:'۳) آیا رشد واقعی شرکت از تورم بیشتر است؟',subtitle:`مقایسه درآمد ${comparison.period_label} جاری و دوره هم‌طول قبلی`,status:better?'good':'mid',statusLabel:better?'خوب':'متوسط',mainMetricValue:`رشد اسمی: ${nominal.toLocaleString('fa-IR',{maximumFractionDigits:1})}٪ · رشد واقعی: ${real.toLocaleString('fa-IR',{maximumFractionDigits:1})}٪`,comparisonDetail:`تورم مرجع: ${inflationReference.percent}٪ · منبع: ${inflationReference.source} · تاریخ داده: ${inflationReference.asOf} · کدال: ${comparison.previous_report} ← ${comparison.current_report}`,summaryAnswer:better?'رشد درآمد پس از تعدیل اثر تورم مثبت است.':'رشد درآمد پس از تعدیل اثر تورم مثبت نیست.'});
  }else{
    const reason=!comparison?raw.period_comparison_unavailable_reason||'داده دوره هم‌طول قبلی موجود نیست.':'نرخ تورم مرجع دارای منبع و تاریخ در تنظیمات ثبت نشده است.';
    questions.push({id:3,title:'۳) آیا رشد واقعی شرکت از تورم بیشتر است؟',subtitle:'مقایسه دوره جاری با دوره هم‌طول قبلی و تورم مرجع',status:'mid',statusLabel:'نامشخص',mainMetricValue:'داده مقایسه‌ای کافی نیست',comparisonDetail:reason,summaryAnswer:'به‌دلیل نبود همه داده‌های مستند لازم، درباره رشد واقعی نتیجه‌گیری نمی‌شود.'});
  }

  // --- Status Banner (شش قلم، فقط اگر داده واقعی موجود باشه) ---
  const statusBanner: StatusBannerMetric[] = [];
  let sbId = 1;

  const pushBanner = (key: string, label: string, value: number | null, unit: string, goodIfHigh = true, thresholds: [number, number] = [40, 65]) => {
    if (value === null || value === undefined) return;
    let status: StatusType = 'mid';
    if (goodIfHigh) {
      status = value >= thresholds[1] ? 'good' : value >= thresholds[0] ? 'mid' : 'bad';
    } else {
      status = value <= thresholds[0] ? 'good' : value <= thresholds[1] ? 'mid' : 'bad';
    }
    statusBanner.push({
      id: sbId++,
      key,
      label,
      value: `${fmtNum(value, 1)}${unit}`,
      status,
      description: '',
    });
  };

  pushBanner('gross_margin', 'حاشیه سود ناخالص', ratios.gross_margin_percent, '٪', true, [15, 30]);
  pushBanner('operating_margin', 'حاشیه سود عملیاتی', ratios.operating_margin_percent, '٪', true, [10, 25]);
  pushBanner('net_margin', 'حاشیه سود خالص', ratios.net_margin_percent, '٪', true, [5, 15]);
  pushBanner('roe', 'بازده حقوق صاحبان سهام', ratios.roe_percent, '٪', true, [10, 20]);
  if (ratios.pe_ratio != null) {
    statusBanner.push({
      id: sbId++,
      key: 'pe',
      label: 'نسبت P/E',
      value: String(ratios.pe_ratio),
      status: ratios.pe_ratio < 8 ? 'good' : ratios.pe_ratio < 15 ? 'mid' : 'bad',
      description: 'ارزش‌گذاری بر اساس سود',
    });
  }
  pushBanner('debt_ratio', 'نسبت بدهی', ratios.debt_ratio_percent, '٪', false, [40, 65]);

  // --- Golden Summary (بر پایه‌ی health.flags واقعی) ---
  const badFlags = (health.flags || []).filter((f: any) => statusFromNote(f.note) === 'bad').length;
  const overallStatus: StatusType = badFlags >= 2 ? 'bad' : badFlags === 1 ? 'mid' : 'good';
  const badgeTitle =
    overallStatus === 'good' ? 'بنیاد قوی و باثبات' : overallStatus === 'mid' ? 'بنیاد متوسط / تحت فشار' : 'بنیاد ضعیف و پرریسک';

  const flagsSummary = (health.flags || [])
    .map((f: any) => `${f.label}: ${f.value} (${f.note})`)
    .join('؛ ');

  const goldenSummary: StockHealthCardData['goldenSummary'] = {
    badgeTitle: badgeTitle as any,
    badgeStatus: overallStatus,
    summaryText: flagsSummary
      ? `بر اساس آخرین صورت مالی رسمی کدال: ${flagsSummary}.`
      : 'داده‌ی کافی برای جمع‌بندی کامل در دسترس نیست.',
    valuationVsQualityNote:
      health.industry_classified_as === 'مالی (بانک/بیمه/واسطه‌گری)'
        ? 'این نماد جزو نهادهای مالی است؛ آستانه‌های ارزیابی (به‌ویژه نسبت بدهی) متناسب با این صنعت تنظیم شده‌اند.'
        : 'آستانه‌های ارزیابی متناسب با شرکت‌های تولیدی/خدماتی عمومی تنظیم شده‌اند.',
    investmentOutlook: 'این تحلیل صرفاً بر پایه‌ی داده‌های رسمی گذشته است و توصیه‌ی سرمایه‌گذاری محسوب نمی‌شود.',
  };

  // --- Explanation Cards (بر پایه‌ی نسبت‌های واقعی) ---
  const explanationCards: ExplanationCard[] = [];
  let ecId = 1;

  const pushExplanation = (title: string, value: string | null, def: string, context: string, status: StatusType) => {
    if (value === null) return;
    explanationCards.push({
      id: ecId,
      numberLabel: String(ecId).padStart(2, '۰'),
      title,
      status,
      valueText: value,
      simpleDefinition13Yo: def,
      companyContextNote: context,
    });
    ecId++;
  };

  if (ratios.gross_margin_percent != null) {
    pushExplanation(
      'حاشیه سود ناخالص',
      `${ratios.gross_margin_percent}٪`,
      'یعنی از هر ۱۰۰ تومان فروش، بعد از کسر هزینه‌ی مستقیم تولید، چقدر باقی می‌ماند.',
      `این نماد حاشیه‌ی ناخالص ${ratios.gross_margin_percent}٪ ثبت کرده است.`,
      ratios.gross_margin_percent >= 30 ? 'good' : ratios.gross_margin_percent >= 15 ? 'mid' : 'bad'
    );
  }
  if (ratios.roe_percent != null) {
    pushExplanation(
      'بازده حقوق صاحبان سهام (ROE)',
      `${ratios.roe_percent}٪`,
      'یعنی به ازای هر ۱۰۰ تومان سرمایه‌ی سهامداران، شرکت چقدر سود ساخته است.',
      `ROE این نماد ${ratios.roe_percent}٪ است.`,
      ratios.roe_percent >= 20 ? 'good' : ratios.roe_percent >= 10 ? 'mid' : 'bad'
    );
  }
  if (ratios.debt_ratio_percent != null) {
    const isFinancial = health.industry_classified_as === 'مالی (بانک/بیمه/واسطه‌گری)';
    pushExplanation(
      'نسبت بدهی',
      `${ratios.debt_ratio_percent}٪`,
      'یعنی چند درصد از کل دارایی‌های شرکت از محل بدهی (نه سرمایه‌ی سهامداران) تامین شده است.',
      isFinancial
        ? `برای نهادهای مالی مثل بانک/بیمه، نسبت بدهی بالا (${ratios.debt_ratio_percent}٪) طبیعی است چون سپرده‌ی مشتریان هم بدهی محسوب می‌شود.`
        : `نسبت بدهی این نماد ${ratios.debt_ratio_percent}٪ است.`,
      isFinancial ? 'good' : ratios.debt_ratio_percent <= 40 ? 'good' : ratios.debt_ratio_percent <= 65 ? 'mid' : 'bad'
    );
  }
  if (ratios.roa_percent != null) {
    pushExplanation(
      'بازده دارایی‌ها (ROA)',
      `${ratios.roa_percent}٪`,
      'یعنی شرکت به ازای هر ۱۰۰ تومان کل دارایی‌هایش، چقدر سود ساخته است.',
      `ROA این نماد ${ratios.roa_percent}٪ است.`,
      ratios.roa_percent >= 10 ? 'good' : ratios.roa_percent >= 5 ? 'mid' : 'bad'
    );
  }
  if (metrics.revenue != null) {
    pushExplanation(
      'درآمد عملیاتی',
      `${fmtNum(metrics.revenue)} میلیون ریال`,
      'کل فروش شرکت از فعالیت اصلی‌اش در این دوره‌ی مالی.',
      `طبق آخرین صورت مالی رسمی، درآمد عملیاتی ${fmtNum(metrics.revenue)} میلیون ریال بوده است.`,
      'good'
    );
  }
  if (metrics.net_profit != null) {
    pushExplanation(
      'سود خالص',
      `${fmtNum(metrics.net_profit)} میلیون ریال`,
      'سودی که بعد از کسر تمام هزینه‌ها و مالیات، واقعاً برای شرکت باقی می‌ماند.',
      `سود خالص این دوره ${fmtNum(metrics.net_profit)} میلیون ریال ثبت شده است.`,
      metrics.net_profit > 0 ? 'good' : 'bad'
    );
  }

  return {
    header,
    questions,
    visuals: {
      trendChart: { title: 'روند سودآوری', subtitle: 'داده‌ی چند دوره‌ای هنوز پیاده‌سازی نشده', unit: '', points: [] },
      donutChart: { title: 'ترکیب درآمد', subtitle: 'داده‌ی تفکیک محصول در دسترس نیست', centerLabel: '', centerValue: '', segments: [] },
      ratioBars: {
        title: 'نسبت‌های کلیدی مالی',
        subtitle: 'بر اساس آخرین صورت مالی رسمی کدال',
        bars: [
          ratios.gross_margin_percent != null && {
            label: 'حاشیه سود ناخالص',
            valuePercentage: Math.min(Math.max(ratios.gross_margin_percent, 0), 100),
            displayValue: `${ratios.gross_margin_percent}٪`,
            status: statusFromNote(ratios.gross_margin_percent >= 30 ? 'خوب' : 'متوسط'),
          },
          ratios.net_margin_percent != null && {
            label: 'حاشیه سود خالص',
            valuePercentage: Math.min(Math.max(ratios.net_margin_percent, 0), 100),
            displayValue: `${ratios.net_margin_percent}٪`,
            status: statusFromNote(ratios.net_margin_percent >= 15 ? 'خوب' : 'متوسط'),
          },
          ratios.debt_ratio_percent != null && {
            label: 'نسبت بدهی',
            valuePercentage: Math.min(Math.max(ratios.debt_ratio_percent, 0), 100),
            displayValue: `${ratios.debt_ratio_percent}٪`,
            status: statusFromNote(ratios.debt_ratio_percent <= 40 ? 'خوب' : 'متوسط'),
          },
        ].filter(Boolean) as any,
      },
    },
    statusBanner,
    goldenSummary,
    explanationCards,
    conclusion: {
      valuationCard: {
        title: 'نتیجه‌گیری بر پایه‌ی داده‌ی رسمی',
        body: flagsSummary || 'داده‌ی کافی برای جمع‌بندی در دسترس نیست.',
      },
      outlookCard: {
        title: 'محدودیت‌های این تحلیل',
        body: 'این گزارش صرفاً بر پایه‌ی آخرین صورت مالی رسمی منتشرشده در کدال و قیمت لحظه‌ای بازار است. پیش‌بینی رشد آینده و محدوده‌ی پیشنهادی خرید/فروش در این نسخه ارائه نمی‌شود، چون هنوز روش‌شناسی مستند و قابل‌اتکایی برایشان پیاده‌سازی نشده است.',
      },
      dataSourceStamp: {
        title: 'منابع داده',
        codalLinkText: raw.report_used?.excel_url || '',
        lastUpdate: header.dataStamp.updatedAt,
        disclaimer:
          'داده‌های این گزارش از صورت مالی رسمی ثبت‌شده در سامانه‌ی کدال و قیمت لحظه‌ای سامانه‌ی معاملات بورس تهران استخراج شده‌اند. این گزارش توصیه‌ی خرید یا فروش نیست.',
      },
    },
    peers: [],
    reportMode: raw.report_used?.title?.includes('حسابرسی') ? 'audited' : 'latest_codal',
    // عمداً خالی/حذف‌شده: smartRecommendation و peSimulation و quarterlyProfits و keyEvents
    // چون روش‌شناسی واقعی و مستندی برایشان هنوز پیاده‌سازی نشده است.
  };
}
