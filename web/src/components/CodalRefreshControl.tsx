import React from 'react';
import { RefreshCw, FileCheck2, FileText, Info, ShieldAlert, Sparkles, Check } from 'lucide-react';

interface CodalRefreshControlProps {
  reportMode: 'latest_codal' | 'audited';
  onChangeReportMode: (mode: 'latest_codal' | 'audited') => void;
  onRefreshData: () => void;
  isLoading: boolean;
  currentSymbol: string;
  auditStatusStr?: string;
  lastUpdateStr?: string;
}

export const CodalRefreshControl: React.FC<CodalRefreshControlProps> = ({
  reportMode,
  onChangeReportMode,
  onRefreshData,
  isLoading,
  currentSymbol,
  auditStatusStr = 'حسابرسی‌شده',
  lastUpdateStr = '۱۴۰۵/۰۵/۰۶',
}) => {
  return (
    <div id="codal-refresh-control" className="mb-5 bg-slate-900 border border-slate-800 rounded-xl p-3.5 md:p-4 shadow-xl space-y-3">
      {/* Top Header & Buttons Row */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
        {/* Title */}
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center shrink-0">
            <RefreshCw className={`w-4 h-4 text-cyan-400 ${isLoading ? 'animate-spin' : ''}`} />
          </div>
          <div>
            <h3 className="text-xs md:text-sm font-bold text-white flex items-center gap-2">
              <span>تنظیمات مبنای گزارشات کدال & بروزرسانی داده‌ها ({currentSymbol})</span>
              <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded border border-slate-700 font-mono">
                Live Codal Sync
              </span>
            </h3>
            <p className="text-[10px] md:text-[11px] text-slate-400 mt-0.5">
              امکان دریافت و استعلام مستقیم آخرین قیمت و صورت‌های مالی سالانه/میان‌دوره‌ای کدال
            </p>
          </div>
        </div>

        {/* Refresh Action Button */}
        <button
          type="button"
          onClick={onRefreshData}
          disabled={isLoading}
          className="w-full md:w-auto px-4 py-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 active:scale-95 text-white font-bold text-xs rounded-xl shadow-lg border border-cyan-400/30 flex items-center justify-center gap-2 transition-all disabled:opacity-50 disabled:cursor-not-allowed shrink-0"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isLoading ? 'animate-spin' : ''}`} />
          <span>{isLoading ? 'در حال بروزرسانی و استعلام...' : 'بروزرسانی زنده قیمت و گزارشات کدال'}</span>
        </button>
      </div>

      {/* Report Mode Selector (حسابرسی شده vs آخرین گزارش کدال) */}
      <div className="pt-2 border-t border-slate-800 grid grid-cols-1 sm:grid-cols-2 gap-2">
        {/* Option A: Latest Codal (Includes Unaudited/Interim) */}
        <button
          type="button"
          onClick={() => onChangeReportMode('latest_codal')}
          className={`p-2.5 rounded-xl border text-right transition-all flex items-start gap-2.5 ${
            reportMode === 'latest_codal'
              ? 'bg-amber-950/40 border-amber-500/60 ring-1 ring-amber-500/30 text-white'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-400'
          }`}
        >
          <FileText className={`w-4 h-4 shrink-0 mt-0.5 ${reportMode === 'latest_codal' ? 'text-amber-400' : 'text-slate-500'}`} />
          <div className="space-y-0.5">
            <div className="text-xs font-bold flex items-center justify-between">
              <span className={reportMode === 'latest_codal' ? 'text-amber-300' : 'text-slate-300'}>
                آخرین گزارش‌های موجود در کدال
              </span>
              {reportMode === 'latest_codal' && (
                <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              )}
            </div>
            <p className="text-[10px] text-slate-400 leading-tight">
              شامل صورت‌های مالی ۳، ۶ و ۹ ماهه میان‌دوره‌ای (حسابرسی نشده/شده جدید)
            </p>
          </div>
        </button>

        {/* Option B: Audited Annual Reports Only */}
        <button
          type="button"
          onClick={() => onChangeReportMode('audited')}
          className={`p-2.5 rounded-xl border text-right transition-all flex items-start gap-2.5 ${
            reportMode === 'audited'
              ? 'bg-emerald-950/40 border-emerald-500/60 ring-1 ring-emerald-500/30 text-white'
              : 'bg-slate-950/60 border-slate-800 hover:border-slate-700 text-slate-400'
          }`}
        >
          <FileCheck2 className={`w-4 h-4 shrink-0 mt-0.5 ${reportMode === 'audited' ? 'text-emerald-400' : 'text-slate-500'}`} />
          <div className="space-y-0.5">
            <div className="text-xs font-bold flex items-center justify-between">
              <span className={reportMode === 'audited' ? 'text-emerald-300' : 'text-slate-300'}>
                فقط گزارش‌های حسابرسی‌شده
              </span>
              {reportMode === 'audited' && (
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              )}
            </div>
            <p className="text-[10px] text-slate-400 leading-tight">
              صورت‌های مالی سالانه ۱۲ ماهه تایید شده توسط حسابرس معتمد سازمان بورس
            </p>
          </div>
        </button>
      </div>

      {/* Explanatory Info Box */}
      <div className="bg-slate-950/90 border border-slate-800 rounded-lg p-2.5 text-[11px] text-slate-300 flex items-start gap-2">
        <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
        <div className="space-y-1">
          <p className="text-[10px] md:text-[11px] leading-relaxed">
            <strong>نکته مهم شفافیت داده‌ها:</strong> به‌دلیل محدودیت‌های دسترسی مستقیم سرورها به کدال، داده‌ها با کلیک روی دکمه فوق از طریق موتور هوشمند استعلام و تحلیل می‌شوند.
          </p>
          <div className="flex flex-wrap items-center gap-3 text-[10px] text-slate-400 pt-1 border-t border-slate-900">
            <span>
              وضعیت فعلی داده‌ها: <strong className="text-cyan-300">{auditStatusStr}</strong>
            </span>
            <span>•</span>
            <span>
              آخرین زمان بروزرسانی: <strong className="text-amber-300 font-mono">{lastUpdateStr}</strong>
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
