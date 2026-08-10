import React, { useState } from 'react';
import { PeSimulationData } from '../types';
import {
  Calculator,
  TrendingUp,
  Sparkles,
  Sliders,
  ShieldCheck,
  DollarSign,
  PieChart,
  ArrowUpRight,
  Lightbulb,
  RefreshCw,
  BarChart2,
  TrendingDown,
} from 'lucide-react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface PeSimulationCardProps {
  peSimulation?: PeSimulationData;
  currentPrice?: number;
  currentPeStr?: string;
  symbol?: string;
}

export const PeSimulationCard: React.FC<PeSimulationCardProps> = ({
  peSimulation,
  currentPrice = 5420,
  currentPeStr = '۵.۸',
  symbol = 'نماد',
}) => {
  // Parse numeric current P/E ratio
  const parsedCurrentPe =
    parseFloat((currentPeStr || '5.8').replace(/[۰-۹]/g, (d) => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d)))) ||
    5.8;
  const priceVal = currentPrice || 5000;
  const baseEps = Math.round(priceVal / parsedCurrentPe) || 1000;

  // Base operational parameters
  const baseRevenue = 120000; // 120,000 Billion Rials base sales
  const baseMarginVal = 35; // 35% base margin

  // Interactive Operational Sliders State
  const [salesGrowthRate, setSalesGrowthRate] = useState<number>(15); // +15% default sales rate growth
  const [targetMargin, setTargetMargin] = useState<number>(35); // 35% net profit margin
  const [totalSharesCount, setTotalSharesCount] = useState<number>(50000); // 50,000 Million Shares (۵۰ میلیارد سهم)

  // Custom EPS Growth Slider State
  const [customEpsGrowth, setCustomEpsGrowth] = useState<number>(25);

  // Live Calculations based on operational sliders
  const simRevenue = Math.round(baseRevenue * (1 + salesGrowthRate / 100)); // Billion Rials
  const simNetProfit = Math.round(simRevenue * (targetMargin / 100)); // Billion Rials
  const simEps = Math.round((simNetProfit * 1000000000) / (totalSharesCount * 1000000)); // Rials
  const epsChangePercent = Math.round(((simEps - baseEps) / baseEps) * 100);
  const simForwardPe = simEps > 0 ? (priceVal / simEps).toFixed(1) : 'نامحدود';
  const priceTargetWithHistoricPe = Math.round(simEps * parsedCurrentPe);
  const potentialUpside = Math.round(((priceTargetWithHistoricPe - priceVal) / priceVal) * 100);

  // Projected 4 Quarters Breakdown based on simulated net profit
  const projectedQuartersData = [
    {
      quarter: 'بهار (Q1)',
      baseProfit: Math.round(baseRevenue * 0.22 * (baseMarginVal / 100)),
      simProfit: Math.round(simRevenue * 0.22 * (targetMargin / 100)),
    },
    {
      quarter: 'تابستان (Q2)',
      baseProfit: Math.round(baseRevenue * 0.27 * (baseMarginVal / 100)),
      simProfit: Math.round(simRevenue * 0.27 * (targetMargin / 100)),
    },
    {
      quarter: 'پاییز (Q3)',
      baseProfit: Math.round(baseRevenue * 0.24 * (baseMarginVal / 100)),
      simProfit: Math.round(simRevenue * 0.24 * (targetMargin / 100)),
    },
    {
      quarter: 'زمستان (Q4)',
      baseProfit: Math.round(baseRevenue * 0.27 * (baseMarginVal / 100)),
      simProfit: Math.round(simRevenue * 0.27 * (targetMargin / 100)),
    },
  ];

  // Quick Preset Handlers
  const handleApplyPreset = (preset: 'bull' | 'cost_reduction' | 'bear' | 'reset') => {
    switch (preset) {
      case 'bull':
        setSalesGrowthRate(30);
        setTargetMargin(40);
        break;
      case 'cost_reduction':
        setSalesGrowthRate(10);
        setTargetMargin(45);
        break;
      case 'bear':
        setSalesGrowthRate(-15);
        setTargetMargin(25);
        break;
      case 'reset':
        setSalesGrowthRate(0);
        setTargetMargin(35);
        break;
    }
  };

  // Default scenario cards
  const defaultScenarios = [
    {
      name: 'سناریوی خوش‌بینانه (صادرات عالی & رشد قیمت)',
      type: 'optimistic' as const,
      epsGrowthPercent: 35,
      simulatedPe: Number((priceVal / (baseEps * 1.35)).toFixed(1)),
      targetPriceChange: '+۳۵٪ (افزایش سودآوری)',
      description: 'افزایش نرخ دلار حواله یا رشد ۳۵ درصدی درآمد فروش ناشی از رونق بازار و کنترل هزینه‌ها.',
    },
    {
      name: 'سناریوی پایه (مطابق تورم و عملکرد جاری)',
      type: 'base' as const,
      epsGrowthPercent: 20,
      simulatedPe: Number((priceVal / (baseEps * 1.2)).toFixed(1)),
      targetPriceChange: '+۲۰٪ (همگام با تورم)',
      description: 'حفظ حاشیه سود جاری و رشد سودآوری متناسب با تورم رسمی و خروجی عملیاتی سال گذشته.',
    },
    {
      name: 'سناریوی بدبینانه (رکود قیمت‌ها & رکود فروش)',
      type: 'pessimistic' as const,
      epsGrowthPercent: 5,
      simulatedPe: Number((priceVal / (baseEps * 1.05)).toFixed(1)),
      targetPriceChange: '+۵٪ (ثبات اسمی)',
      description: 'توقف رشد نرخ فروش، افزایش شدید هزینه‌های انرژی و مواد اولیه و فشار بر حاشیه سود خالص.',
    },
  ];

  const scenarios = peSimulation?.scenarios || defaultScenarios;

  // Custom EPS calculation
  const customEps = Math.round(baseEps * (1 + customEpsGrowth / 100));
  const customForwardPe = (priceVal / customEps).toFixed(1);

  const getScenarioBg = (type: 'optimistic' | 'base' | 'pessimistic') => {
    switch (type) {
      case 'optimistic':
        return 'bg-cyan-950/40 border-cyan-500/40 text-cyan-300';
      case 'base':
        return 'bg-amber-950/40 border-amber-500/40 text-amber-300';
      case 'pessimistic':
        return 'bg-rose-950/40 border-rose-500/40 text-rose-300';
      default:
        return 'bg-slate-900 border-slate-800 text-slate-300';
    }
  };

  const getScenarioBadge = (type: 'optimistic' | 'base' | 'pessimistic') => {
    switch (type) {
      case 'optimistic':
        return 'bg-cyan-500/20 text-cyan-400 border-cyan-500/30';
      case 'base':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/30';
      case 'pessimistic':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/30';
    }
  };

  return (
    <section id="pe-simulation-card" className="mb-5">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 md:p-5 shadow-xl space-y-5">
        {/* Header Title */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center shrink-0">
              <Calculator className="w-4 h-4 text-cyan-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-1.5">
                <span>شبیه‌سازی P/E و ابزار آنی تخمین سود خالص سال آینده ({symbol})</span>
                <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-2 py-0.5 rounded border border-cyan-500/30 font-mono">
                  Real-time Simulation
                </span>
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5">
                تغییر زنده لغزنده‌های نرخ فروش و حاشیه سود و مشاهده آنی تأثیر عملیاتی بر نمودار سود فصلی و EPS
              </p>
            </div>
          </div>

          {/* Current Base Metrics Pill */}
          <div className="flex items-center gap-2 bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-lg text-xs shrink-0 font-mono">
            <span className="text-slate-400">P/E فعلی TTM:</span>
            <span className="text-cyan-400 font-bold">{parsedCurrentPe}</span>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">EPS TTM:</span>
            <span className="text-amber-400 font-bold">{baseEps.toLocaleString('fa-IR')} ریال</span>
          </div>
        </div>

        {/* --- INTERACTIVE OPERATIONAL SLIDERS & REAL-TIME CHART --- */}
        <div className="bg-slate-950 border border-cyan-500/30 rounded-xl p-4 space-y-4 relative overflow-hidden">
          <div className="w-1.5 h-full bg-cyan-500 absolute top-0 right-0" />

          {/* Title & Presets */}
          <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-3 pr-2 border-b border-slate-900 pb-3">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-amber-400" />
              <h3 className="text-xs md:text-sm font-bold text-white">
                شبیه‌ساز عملیاتی زنده: لغزنده‌های تغییر نرخ فروش و حاشیه سود
              </h3>
            </div>

            {/* Quick Preset Buttons */}
            <div className="flex flex-wrap items-center gap-1.5 text-[10px]">
              <span className="text-slate-400 font-medium ml-1">سناریوهای آماده:</span>
              <button
                type="button"
                onClick={() => handleApplyPreset('bull')}
                className="bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 border border-cyan-500/30 px-2 py-1 rounded transition-all flex items-center gap-1 font-semibold"
              >
                <TrendingUp className="w-3 h-3 text-cyan-400" />
                <span>جهش ۳۰٪ فروش و ۴۰٪ حاشیه سود</span>
              </button>

              <button
                type="button"
                onClick={() => handleApplyPreset('cost_reduction')}
                className="bg-emerald-950/80 hover:bg-emerald-900 text-emerald-300 border border-emerald-500/30 px-2 py-1 rounded transition-all flex items-center gap-1 font-semibold"
              >
                <Sparkles className="w-3 h-3 text-emerald-400" />
                <span>کنترل هزینه (حاشیه سود ۴۵٪)</span>
              </button>

              <button
                type="button"
                onClick={() => handleApplyPreset('bear')}
                className="bg-rose-950/80 hover:bg-rose-900 text-rose-300 border border-rose-500/30 px-2 py-1 rounded transition-all flex items-center gap-1 font-semibold"
              >
                <TrendingDown className="w-3 h-3 text-rose-400" />
                <span>افت ۱۵٪ فروش (رکود)</span>
              </button>

              <button
                type="button"
                onClick={() => handleApplyPreset('reset')}
                className="bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 px-2 py-1 rounded transition-all flex items-center gap-1"
              >
                <RefreshCw className="w-2.5 h-2.5" />
                <span>بازنشانی</span>
              </button>
            </div>
          </div>

          {/* Main Controls & Live Chart Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 items-stretch pr-2">
            {/* Left Sliders & Summary Metrics (6 cols) */}
            <div className="lg:col-span-6 space-y-4 bg-slate-900/70 p-3.5 rounded-xl border border-slate-800 flex flex-col justify-between">
              <div className="space-y-3.5">
                {/* Slider 1: Sales Growth Rate % */}
                <div className="space-y-1.5">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-200 font-bold flex items-center gap-1">
                      <span>تغییر نرخ فروش / درآمد عملیاتی:</span>
                    </span>
                    <span
                      className={`font-mono font-bold px-2 py-0.5 rounded text-xs border ${
                        salesGrowthRate > 0
                          ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
                          : salesGrowthRate < 0
                          ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                          : 'bg-slate-800 text-slate-300 border-slate-700'
                      }`}
                    >
                      {salesGrowthRate > 0 ? `+${salesGrowthRate}` : salesGrowthRate}٪ رشد فروش
                    </span>
                  </div>

                  <input
                    type="range"
                    min="-30"
                    max="60"
                    step="5"
                    value={salesGrowthRate}
                    onChange={(e) => setSalesGrowthRate(Number(e.target.value))}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
                  />

                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>افت شدید (-۳۰٪)</span>
                    <span className="text-slate-300">درآمد جدید: {simRevenue.toLocaleString('fa-IR')} میلیارد ریال</span>
                    <span>جهش فروش (+۶۰٪)</span>
                  </div>
                </div>

                {/* Slider 2: Net Margin % */}
                <div className="space-y-1.5 pt-2 border-t border-slate-800/80">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-200 font-bold">حاشیه سود خالص پیش‌بینی‌شده:</span>
                    <span className="font-mono font-bold bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded text-xs border border-emerald-500/40">
                      {targetMargin}٪ حاشیه سود
                    </span>
                  </div>

                  <input
                    type="range"
                    min="10"
                    max="60"
                    step="1"
                    value={targetMargin}
                    onChange={(e) => setTargetMargin(Number(e.target.value))}
                    className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-emerald-400"
                  />

                  <div className="flex justify-between text-[10px] text-slate-400 font-mono">
                    <span>حاشیه پایین (۱۰٪)</span>
                    <span className="text-emerald-400">حاشیه سود فعلی: ۳۵٪</span>
                    <span>حاشیه عالی (۶۰٪)</span>
                  </div>
                </div>
              </div>

              {/* Live Metric Badges */}
              <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-800">
                <div className="bg-slate-950 p-2 rounded-lg border border-emerald-500/30">
                  <span className="text-[10px] text-slate-400">سود خالص شبیه‌سازی‌شده:</span>
                  <div className="text-xs md:text-sm font-extrabold text-emerald-400 font-mono mt-0.5">
                    {simNetProfit.toLocaleString('fa-IR')} میلیارد ریال
                  </div>
                </div>

                <div className="bg-slate-950 p-2 rounded-lg border border-cyan-500/30">
                  <span className="text-[10px] text-slate-400">EPS کارشناسی پیش‌بینی:</span>
                  <div className="text-xs md:text-sm font-extrabold text-cyan-300 font-mono mt-0.5">
                    {simEps.toLocaleString('fa-IR')} ریال ({epsChangePercent > 0 ? `+${epsChangePercent}` : epsChangePercent}٪)
                  </div>
                </div>

                <div className="bg-slate-950 p-2 rounded-lg border border-amber-500/30">
                  <span className="text-[10px] text-slate-400">P/E آینده‌نگر (Forward):</span>
                  <div className="text-xs md:text-sm font-extrabold text-amber-300 font-mono mt-0.5">
                    {simForwardPe} مرتبه
                  </div>
                </div>

                <div className="bg-slate-950 p-2 rounded-lg border border-teal-500/30">
                  <span className="text-[10px] text-slate-400">تارگت قیمتی / پتانسیل:</span>
                  <div className="text-xs md:text-sm font-extrabold text-teal-300 font-mono mt-0.5">
                    {priceTargetWithHistoricPe.toLocaleString('fa-IR')} ({potentialUpside > 0 ? `+${potentialUpside}` : potentialUpside}٪)
                  </div>
                </div>
              </div>
            </div>

            {/* Right Live Projected Chart (6 cols) */}
            <div className="lg:col-span-6 bg-slate-900/90 p-3.5 rounded-xl border border-slate-800 space-y-2 flex flex-col justify-between">
              <div className="flex items-center justify-between pb-1.5 border-b border-slate-800">
                <div className="flex items-center gap-1.5">
                  <BarChart2 className="w-4 h-4 text-cyan-400" />
                  <span className="text-xs font-bold text-white">
                    نمودار آنی پیش‌بینی سود ۴ فصل بعد ({symbol})
                  </span>
                </div>
                <span className="text-[10px] text-slate-400 font-mono">
                  واحد: میلیارد ریال
                </span>
              </div>

              {/* Recharts Mini Live Bar Chart */}
              <div className="h-48 w-full pt-1">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={projectedQuartersData} margin={{ top: 10, right: 5, left: 5, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                    <XAxis
                      dataKey="quarter"
                      stroke="#94a3b8"
                      tick={{ fill: '#cbd5e1', fontSize: 10 }}
                    />
                    <YAxis
                      stroke="#94a3b8"
                      tick={{ fill: '#94a3b8', fontSize: 9 }}
                      tickFormatter={(v) => `${(v / 1000).toFixed(0)}ک`}
                    />
                    <Tooltip
                      content={({ active, payload, label }) => {
                        if (active && payload && payload.length) {
                          return (
                            <div className="bg-slate-950 border border-slate-700 p-2.5 rounded-lg text-xs space-y-1 shadow-xl">
                              <div className="font-bold text-amber-400 border-b border-slate-800 pb-1">
                                {label}
                              </div>
                              <div className="text-slate-300 font-mono flex justify-between gap-3">
                                <span>حالت مبنا:</span>
                                <span>{payload[0].value?.toLocaleString('fa-IR')} میلیارد</span>
                              </div>
                              <div className="text-cyan-300 font-mono font-bold flex justify-between gap-3">
                                <span>شبیه‌سازی شده:</span>
                                <span>{payload[1].value?.toLocaleString('fa-IR')} میلیارد</span>
                              </div>
                            </div>
                          );
                        }
                        return null;
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '6px' }} />
                    <Bar
                      dataKey="baseProfit"
                      fill="#334155"
                      radius={[4, 4, 0, 0]}
                      name="سود فصلی مبنا"
                    />
                    <Bar
                      dataKey="simProfit"
                      fill="#06b6d4"
                      radius={[4, 4, 0, 0]}
                      name="سود فصلی شبیه‌سازی‌شده"
                    />
                  </BarChart>
                </ResponsiveContainer>
              </div>

              <div className="text-[10px] text-slate-400 bg-slate-950 p-2 rounded border border-slate-800/80 flex items-center justify-between font-mono">
                <span>تغییر کل سود فصلی سال آینده:</span>
                <span className={`font-bold ${epsChangePercent >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {epsChangePercent >= 0 ? `+${epsChangePercent}` : epsChangePercent}٪ نسبت به عملکرد گذشته
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 3 Scenario Cards Bento Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {scenarios.map((sc, idx) => (
            <div
              key={idx}
              className={`border rounded-xl p-3.5 flex flex-col justify-between ${getScenarioBg(
                sc.type
              )} transition-all hover:scale-[1.01]`}
            >
              <div>
                <div className="flex items-center justify-between gap-2 mb-2 pb-2 border-b border-slate-800/80">
                  <span className="text-xs font-bold text-white truncate">{sc.name}</span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold border shrink-0 ${getScenarioBadge(
                      sc.type
                    )}`}
                  >
                    رشد سود: +{sc.epsGrowthPercent}٪
                  </span>
                </div>

                <div className="my-2 bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80 space-y-1">
                  <div className="flex justify-between items-center text-xs">
                    <span className="text-slate-400 font-medium text-[11px]">P/E آینده‌نگر (Forward):</span>
                    <span className="font-mono font-bold text-sm text-white">{sc.simulatedPe} مرتبه</span>
                  </div>

                  <div className="flex justify-between items-center text-[10px] pt-1 border-t border-slate-900">
                    <span className="text-slate-400">تأثیر بر ارزش کارشناسی:</span>
                    <span className="font-bold text-cyan-300 font-mono">{sc.targetPriceChange}</span>
                  </div>
                </div>

                <p className="text-[11px] text-slate-300/90 leading-relaxed mt-2">
                  {sc.description}
                </p>
              </div>

              {/* Progress bar visual for P/E compressed comparison */}
              <div className="mt-3 pt-2 border-t border-slate-800/80">
                <div className="flex justify-between text-[10px] text-slate-400 mb-1">
                  <span>P/E فعلی ({parsedCurrentPe})</span>
                  <span>P/E سناریو ({sc.simulatedPe})</span>
                </div>
                <div className="w-full bg-slate-800 h-1.5 rounded-full overflow-hidden">
                  <div
                    className={`h-full rounded-full ${
                      sc.type === 'optimistic'
                        ? 'bg-cyan-400'
                        : sc.type === 'base'
                        ? 'bg-amber-400'
                        : 'bg-rose-400'
                    }`}
                    style={{
                      width: `${Math.min(Math.max((sc.simulatedPe / parsedCurrentPe) * 100, 20), 100)}%`,
                    }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {/* Interactive Custom EPS Growth Simulator Box */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-3.5 space-y-3">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <Sliders className="w-4 h-4 text-amber-400" />
              <span className="text-xs font-bold text-white">
                شبیه‌ساز تعاملی سریع: درصد رشد سود هر سهم (EPS)
              </span>
            </div>

            <span className="text-xs font-mono text-cyan-300 bg-slate-900 px-2.5 py-1 rounded border border-slate-800">
              P/E برآوردی شما: <strong className="text-amber-400 text-sm font-bold ml-1">{customForwardPe}</strong> مرتبه
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
            {/* Slider */}
            <div className="md:col-span-8 space-y-1">
              <div className="flex justify-between text-[11px] text-slate-400">
                <span>افت سود (-۲۰٪)</span>
                <span className="text-amber-300 font-bold">نرخ رشد انتخابی: {customEpsGrowth > 0 ? `+${customEpsGrowth}` : customEpsGrowth}٪</span>
                <span>جهش سود (+۶۰٪)</span>
              </div>
              <input
                type="range"
                min="-20"
                max="60"
                step="5"
                value={customEpsGrowth}
                onChange={(e) => setCustomEpsGrowth(Number(e.target.value))}
                className="w-full h-2 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-cyan-400"
              />
            </div>

            {/* Calculated Values Output */}
            <div className="md:col-span-4 bg-slate-900 border border-slate-800 rounded-lg p-2.5 text-xs space-y-1">
              <div className="flex justify-between text-slate-300">
                <span>EPS جدید:</span>
                <span className="font-mono font-bold text-cyan-300">{customEps.toLocaleString('fa-IR')} ریال</span>
              </div>
              <div className="flex justify-between text-slate-300">
                <span>قیمت فعلی سهم:</span>
                <span className="font-mono text-slate-200">{priceVal.toLocaleString('fa-IR')} ریال</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Formula & Valuation Guidance Note */}
        <div className="pt-2 border-t border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-2 text-[10px] text-slate-400">
          <div className="flex items-center gap-1.5 text-slate-300">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
            <span>
              فرمول محاسبه: <strong>سود خالص = فروش سالانه × حاشیه سود | Forward EPS = سود خالص ÷ تعداد سهام</strong>
            </span>
          </div>
          <span className="text-slate-500">
            توصیه بنیادی: P/Eهای آینده‌نگر پایین‌تر از متوسط صنعت (زیر ۵) نشان‌دهنده حاشیه ایمنی بالای معامله است.
          </span>
        </div>
      </div>
    </section>
  );
};

