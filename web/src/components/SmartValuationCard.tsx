import React from 'react';
import { SmartRecommendation } from '../types';
import { Target, ShieldCheck, TrendingUp, AlertTriangle, Lightbulb, ArrowUpRight, ArrowDownRight, CheckCircle2 } from 'lucide-react';

interface SmartValuationCardProps {
  smartRecommendation?: SmartRecommendation;
  symbol?: string;
  codalAuditStatus?: string;
}

export const SmartValuationCard: React.FC<SmartValuationCardProps> = ({
  smartRecommendation,
  symbol = 'نماد',
  codalAuditStatus = 'حسابرسی‌شده',
}) => {
  if (!smartRecommendation) return null;

  const {
    isSuitableForBuy,
    statusTitle,
    suitabilityNote,
    buyRange,
    sellTargetRange,
    stopLossPrice,
    riskLevel,
    insights,
  } = smartRecommendation;

  const isUnaudited =
    codalAuditStatus.includes('حسابرسی‌نشده') || codalAuditStatus.includes('میاندوره‌ای');

  return (
    <section id="smart-valuation-card" className="mb-5">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 md:p-5 shadow-xl space-y-4">
        {/* Header Title */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center shrink-0">
              <Target className="w-4 h-4 text-emerald-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-1.5">
                <span>تحلیل ارزش بازار & محدوده قیمت خرید و فروش ({symbol})</span>
                <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-2 py-0.5 rounded border border-emerald-500/30 font-mono">
                  Smart Trade Zone
                </span>
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5">
                پیشنهاد هوشمندانه محدوده ورود، حد سود و حد ضرر بر اساس ارزش ذاتی و ریسک
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2 shrink-0">
            <span className="text-[10px] text-slate-400">سطح ریسک:</span>
            <span
              className={`px-2.5 py-1 rounded-full text-xs font-bold border font-mono ${
                riskLevel === 'کم'
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40'
                  : riskLevel === 'متوسط'
                  ? 'bg-amber-500/20 text-amber-300 border-amber-500/40'
                  : 'bg-rose-500/20 text-rose-300 border-rose-500/40'
              }`}
            >
              ریسک {riskLevel}
            </span>
          </div>
        </div>

        {/* Buy Suitability Main Banner */}
        <div
          className={`p-3.5 rounded-xl border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 ${
            isSuitableForBuy
              ? 'bg-emerald-950/30 border-emerald-500/40'
              : 'bg-amber-950/30 border-amber-500/40'
          }`}
        >
          <div className="flex items-start gap-2.5">
            {isSuitableForBuy ? (
              <CheckCircle2 className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
            ) : (
              <AlertTriangle className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
            )}
            <div>
              <div className="text-sm font-bold text-white flex items-center gap-2">
                <span>ارزیابی خرید: {statusTitle}</span>
              </div>
              <p className="text-xs text-slate-300 mt-1 leading-relaxed">{suitabilityNote}</p>
            </div>
          </div>
        </div>

        {/* 3 Price Bounds Cards Grid (خرید / فروش / حد ضرر) */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {/* Card 1: Buy Range */}
          <div className="bg-slate-950 border border-emerald-500/30 rounded-xl p-3.5 space-y-2 relative overflow-hidden">
            <div className="w-1.5 h-full bg-emerald-500 absolute top-0 right-0" />
            <div className="flex justify-between items-center pr-2">
              <span className="text-xs font-bold text-emerald-400 flex items-center gap-1">
                <ArrowDownRight className="w-3.5 h-3.5" />
                محدوده خرید پیشنهادی (جذاب)
              </span>
              <span className="text-[10px] bg-emerald-500/20 text-emerald-300 px-1.5 py-0.5 rounded font-mono">
                Buy Zone
              </span>
            </div>
            <div className="text-base font-extrabold font-mono text-white pr-2">
              {buyRange.displayRange}
            </div>
            <p className="text-[10px] text-slate-400 pr-2">
              محدوده اصلاحی با حاشیه ایمنی بالا جهت ورود پله‌ای
            </p>
          </div>

          {/* Card 2: Sell Target Range */}
          <div className="bg-slate-950 border border-cyan-500/30 rounded-xl p-3.5 space-y-2 relative overflow-hidden">
            <div className="w-1.5 h-full bg-cyan-500 absolute top-0 right-0" />
            <div className="flex justify-between items-center pr-2">
              <span className="text-xs font-bold text-cyan-400 flex items-center gap-1">
                <ArrowUpRight className="w-3.5 h-3.5" />
                محدوده هدف فروش (تارگت)
              </span>
              <span className="text-[10px] bg-cyan-500/20 text-cyan-300 px-1.5 py-0.5 rounded font-mono">
                Target Zone
              </span>
            </div>
            <div className="text-base font-extrabold font-mono text-white pr-2">
              {sellTargetRange.displayRange}
            </div>
            <p className="text-[10px] text-slate-400 pr-2">
              تارگت قیمتی میان‌مدت بر اساس ارزش کارشناسی نماد
            </p>
          </div>

          {/* Card 3: Stop Loss */}
          <div className="bg-slate-950 border border-rose-500/30 rounded-xl p-3.5 space-y-2 relative overflow-hidden">
            <div className="w-1.5 h-full bg-rose-500 absolute top-0 right-0" />
            <div className="flex justify-between items-center pr-2">
              <span className="text-xs font-bold text-rose-400 flex items-center gap-1">
                <ShieldCheck className="w-3.5 h-3.5" />
                حد ضرر پیشنهادی (Stop Loss)
              </span>
              <span className="text-[10px] bg-rose-500/20 text-rose-300 px-1.5 py-0.5 rounded font-mono">
                Risk Limit
              </span>
            </div>
            <div className="text-base font-extrabold font-mono text-white pr-2">
              {stopLossPrice.displayPrice}
            </div>
            <p className="text-[10px] text-slate-400 pr-2">
              تثبیت زیر این قیمت نشانه خروج یا تغییر روند است
            </p>
          </div>
        </div>

        {/* Smart Investment Advice Bullet Points */}
        <div className="bg-slate-950/80 border border-slate-800 rounded-xl p-3.5 space-y-2">
          <div className="flex items-center gap-1.5 text-xs font-bold text-amber-400 pb-2 border-b border-slate-800">
            <Lightbulb className="w-4 h-4 text-amber-400" />
            <span>پیشنهادات هوشمندانه و نکات کلیدی معامله:</span>
          </div>

          <ul className="space-y-2 pt-1 text-xs text-slate-300 leading-relaxed">
            {insights.map((item, idx) => (
              <li key={idx} className="flex items-start gap-2 bg-slate-900/50 p-2 rounded border border-slate-800/60">
                <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 shrink-0 mt-1.5" />
                <span
                  className="text-slate-300 text-[11px]"
                  dangerouslySetInnerHTML={{
                    __html: item
                      .replace(/\*\*(.*?)\*\*/g, '<strong class="text-white font-bold">$1</strong>')
                      .replace(/🎯|📈|🛡️|⚠️|✅/g, ''),
                  }}
                />
              </li>
            ))}
          </ul>
        </div>

        {/* Codal Audit Status Clarification Banner */}
        <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-[11px] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 text-slate-400">
          <div className="flex items-center gap-2">
            <span className="font-semibold text-slate-300">وضعیت گزارش کدال:</span>
            <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${isUnaudited ? 'bg-amber-500/20 text-amber-400 border border-amber-500/30' : 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/30'}`}>
              {codalAuditStatus}
            </span>
          </div>
          <span className="text-[10px] text-slate-500">
            {isUnaudited
              ? 'تذکر: تحلیل فوق بر اساس آخرین صورت‌های مالی میان‌دوره‌ای منتشر شده در کدال است.'
              : 'تاییدیه: صورت‌های مالی پایه توسط حسابرس معتمد سازمان بورس تایید شده‌اند.'}
          </span>
        </div>
      </div>
    </section>
  );
};
