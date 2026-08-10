import React from 'react';
import { GoldenSummary } from '../types';
import { Star, ShieldAlert, Sparkles, Award } from 'lucide-react';

interface GoldenSummaryBannerProps {
  summary: GoldenSummary;
}

export const GoldenSummaryBanner: React.FC<GoldenSummaryBannerProps> = ({ summary }) => {
  return (
    <section className="mb-5">
      <div className="bg-yellow-500/90 text-slate-950 p-4 rounded-xl shadow-lg relative overflow-hidden flex flex-col md:flex-row items-start md:items-center justify-between gap-4 font-bold">
        
        {/* Main Text Content */}
        <div className="space-y-2 max-w-4xl">
          <div className="flex items-center gap-2 text-slate-950">
            <Star className="w-5 h-5 text-slate-950 fill-slate-950 shrink-0" />
            <span className="text-xs uppercase tracking-wider font-extrabold flex items-center gap-1">
              <Sparkles className="w-3.5 h-3.5" />
              جمع‌بندی نهایی کیفی:
            </span>
            <span className="text-sm font-black text-slate-900 border-r border-slate-950/30 pr-2">
              {summary?.badgeTitle || 'بنیاد باثبات'}
            </span>
          </div>

          <p className="text-xs md:text-sm text-slate-950/90 font-medium leading-relaxed">
            {summary?.summaryText || ''}
          </p>

          <div className="bg-slate-950/10 border border-slate-950/20 rounded-lg p-2 text-[11px] text-slate-900 font-semibold flex items-center gap-2">
            <ShieldAlert className="w-4 h-4 text-slate-950 shrink-0" />
            <span>
              <strong>ارزش‌گذاری در برابر کیفیت:</strong> {summary?.valuationVsQualityNote || ''}
            </span>
          </div>
        </div>

        {/* Diagnosis Badge */}
        <div className="bg-slate-950 text-white rounded-lg p-3 text-center shrink-0 min-w-[190px] border border-slate-800 shadow-md">
          <Award className="w-6 h-6 text-yellow-400 mx-auto mb-1" />
          <span className="text-[10px] text-slate-400 block font-normal">نتیجه تحلیل ۶ گام</span>
          <span className="text-sm font-black text-yellow-400 block mt-0.5">
            {summary?.badgeTitle || 'پایدار'}
          </span>
        </div>

      </div>
    </section>
  );
};
