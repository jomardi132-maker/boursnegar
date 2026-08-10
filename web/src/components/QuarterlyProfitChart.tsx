import React, { useState } from 'react';
import { QuarterlyProfitItem } from '../types';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { BarChart3, TrendingUp, DollarSign, Percent, Award, Info, Sparkles } from 'lucide-react';

interface QuarterlyProfitChartProps {
  quarterlyProfits?: QuarterlyProfitItem[];
  symbol?: string;
  industryTitle?: string;
}

export const QuarterlyProfitChart: React.FC<QuarterlyProfitChartProps> = ({
  quarterlyProfits = [],
  symbol = 'نماد',
  industryTitle = 'صنعت',
}) => {
  const [activeMetric, setActiveMetric] = useState<'profit' | 'margin'>('profit');

  if (!quarterlyProfits || quarterlyProfits.length === 0) return null;

  // Prepare chart formatted data
  const chartData = quarterlyProfits.map((item) => ({
    name: item.quarter,
    'سود خالص نماد (میلیارد ریال)': item.stockProfit,
    'میانگین صنعت (میلیارد ریال)': item.industryAvgProfit,
    'حاشیه سود خالص (٪)': item.marginPercent,
    growthPercent: item.growthPercent,
  }));

  // Calculate annual total
  const totalStockProfit = quarterlyProfits.reduce((acc, curr) => acc + curr.stockProfit, 0);
  const totalIndustryProfit = quarterlyProfits.reduce((acc, curr) => acc + curr.industryAvgProfit, 0);
  const avgMargin = Math.round(
    quarterlyProfits.reduce((acc, curr) => acc + curr.marginPercent, 0) / quarterlyProfits.length
  );

  // Custom Tooltip for Recharts
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      const dataItem = payload[0].payload;
      return (
        <div className="bg-slate-950 border border-slate-700/80 p-3 rounded-xl shadow-2xl space-y-1.5 text-xs">
          <div className="font-bold text-amber-400 border-b border-slate-800 pb-1 flex justify-between items-center gap-4">
            <span>عملکرد فصل {label}</span>
            <span className="text-[10px] bg-slate-800 text-slate-300 px-1.5 py-0.5 rounded font-mono">
              رشد: +{dataItem.growthPercent}٪
            </span>
          </div>

          <div className="space-y-1 pt-1 font-mono">
            <div className="flex justify-between items-center text-cyan-300 gap-3">
              <span className="text-slate-300 font-sans">سود خالص {symbol}:</span>
              <strong className="font-bold">
                {dataItem['سود خالص نماد (میلیارد ریال)'].toLocaleString('fa-IR')} میلیارد ریال
              </strong>
            </div>

            <div className="flex justify-between items-center text-slate-400 gap-3">
              <span className="font-sans">میانگین همصنعتان:</span>
              <span>
                {dataItem['میانگین صنعت (میلیارد ریال)'].toLocaleString('fa-IR')} میلیارد ریال
              </span>
            </div>

            <div className="flex justify-between items-center text-emerald-400 gap-3 pt-1 border-t border-slate-900">
              <span className="font-sans text-[11px]">حاشیه سود خالص:</span>
              <span className="font-bold">{dataItem['حاشیه سود خالص (٪)']}٪</span>
            </div>
          </div>
        </div>
      );
    }
    return null;
  };

  return (
    <section id="quarterly-profit-chart" className="mb-5">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 md:p-5 shadow-xl space-y-4">
        {/* Header Row */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/30 flex items-center justify-center shrink-0">
              <BarChart3 className="w-4 h-4 text-teal-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-1.5">
                <span>نمودار سود خالص فصلی {symbol} در مقایسه با میانگین صنعت</span>
                <span className="text-[10px] bg-teal-500/20 text-teal-300 px-2 py-0.5 rounded border border-teal-500/30 font-mono">
                  Quarterly Profits
                </span>
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5">
                تحلیل مقایسه‌ای ۴ فصل اخیر سود خالص (میلیارد ریال) و حاشیه سود با صنعت {industryTitle}
              </p>
            </div>
          </div>

          {/* Metric Selector Buttons */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs shrink-0">
            <button
              type="button"
              onClick={() => setActiveMetric('profit')}
              className={`px-3 py-1 rounded-md text-[11px] font-bold transition-all flex items-center gap-1 ${
                activeMetric === 'profit'
                  ? 'bg-teal-500 text-slate-950 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <DollarSign className="w-3 h-3" />
              <span>مبلغ سود (میلیارد ریال)</span>
            </button>

            <button
              type="button"
              onClick={() => setActiveMetric('margin')}
              className={`px-3 py-1 rounded-md text-[11px] font-bold transition-all flex items-center gap-1 ${
                activeMetric === 'margin'
                  ? 'bg-teal-500 text-slate-950 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              <Percent className="w-3 h-3" />
              <span>حاشیه سود (٪)</span>
            </button>
          </div>
        </div>

        {/* Quick Annual Stats Row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          <div className="bg-slate-950 border border-teal-500/30 rounded-xl p-3 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-400">مجموع سود خالص سالانه:</span>
              <div className="text-sm font-extrabold text-teal-300 font-mono mt-0.5">
                {totalStockProfit.toLocaleString('fa-IR')} میلیارد ریال
              </div>
            </div>
            <Award className="w-5 h-5 text-teal-400/80" />
          </div>

          <div className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-400">مجموع میانگین همصنعتان:</span>
              <div className="text-sm font-bold text-slate-300 font-mono mt-0.5">
                {totalIndustryProfit.toLocaleString('fa-IR')} میلیارد ریال
              </div>
            </div>
            <BarChart3 className="w-5 h-5 text-slate-500" />
          </div>

          <div className="bg-slate-950 border border-emerald-500/30 rounded-xl p-3 flex items-center justify-between">
            <div>
              <span className="text-[10px] text-slate-400">میانگین حاشیه سود ۴ فصل:</span>
              <div className="text-sm font-bold text-emerald-400 font-mono mt-0.5">
                {avgMargin}٪ (عملکرد عالی)
              </div>
            </div>
            <TrendingUp className="w-5 h-5 text-emerald-400/80" />
          </div>
        </div>

        {/* Recharts Bar Chart Area */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3 md:p-4 space-y-2">
          <div className="h-64 md:h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              {activeMetric === 'profit' ? (
                <BarChart data={chartData} margin={{ top: 15, right: 10, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis
                    dataKey="name"
                    stroke="#94a3b8"
                    tick={{ fill: '#cbd5e1', fontSize: 11 }}
                  />
                  <YAxis
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 10 }}
                    tickFormatter={(val) => `${(val / 1000).toFixed(0)}ک`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    wrapperStyle={{ paddingTop: '10px', fontSize: '11px', color: '#cbd5e1' }}
                  />
                  <Bar
                    dataKey="سود خالص نماد (میلیارد ریال)"
                    fill="#0d9488"
                    radius={[6, 6, 0, 0]}
                    name={`سود خالص ${symbol}`}
                  />
                  <Bar
                    dataKey="میانگین صنعت (میلیارد ریال)"
                    fill="#334155"
                    radius={[6, 6, 0, 0]}
                    name="میانگین صنعت"
                  />
                </BarChart>
              ) : (
                <BarChart data={chartData} margin={{ top: 15, right: 10, left: 10, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
                  <XAxis
                    dataKey="name"
                    stroke="#94a3b8"
                    tick={{ fill: '#cbd5e1', fontSize: 11 }}
                  />
                  <YAxis
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 10 }}
                    tickFormatter={(val) => `${val}٪`}
                  />
                  <Tooltip content={<CustomTooltip />} />
                  <Legend
                    wrapperStyle={{ paddingTop: '10px', fontSize: '11px', color: '#cbd5e1' }}
                  />
                  <Bar
                    dataKey="حاشیه سود خالص (٪)"
                    fill="#10b981"
                    radius={[6, 6, 0, 0]}
                    name="حاشیه سود خالص (٪)"
                  />
                </BarChart>
              )}
            </ResponsiveContainer>
          </div>

          {/* Footnote Insight */}
          <div className="flex items-center gap-2 pt-2 border-t border-slate-900 text-[11px] text-slate-400">
            <Sparkles className="w-3.5 h-3.5 text-amber-400 shrink-0" />
            <span>
              بررسی روند فصلی نشان می‌دهد سود خالص {symbol} در تمام ۴ فصل بالاتر از میانگین صنعت بوده که حاکی از قدرت رقابتی و کنترل هزینه‌ها در این نماد است.
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};
