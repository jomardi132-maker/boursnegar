import React from 'react';
import { CompanyHeaderInfo, UserProfile } from '../types';
import { Building2, CalendarDays, CheckCircle2, Database, Download, Landmark, TrendingUp } from 'lucide-react';

interface HeaderProps {
  info: CompanyHeaderInfo;
  user: UserProfile | null;
  onOpenAuth: () => void;
  onOpenSubscription: () => void;
  onOpenAlerts: () => void;
  onOpenExport: () => void;
  onOpenAdmin: () => void;
  onOpenServerGuide: () => void;
}

export const Header: React.FC<HeaderProps> = ({ info, onOpenExport }) => {
  const hasPrice = Number.isFinite(info.currentPrice) && info.currentPrice > 0;
  const priceDisplay = hasPrice ? `${info.currentPrice.toLocaleString('fa-IR')} ریال` : 'در دسترس نیست';

  return (
    <header className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900 shadow-2xl">
      <div className="flex flex-col gap-4 border-b border-slate-800 bg-slate-950/70 px-5 py-4 md:flex-row md:items-center md:justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-cyan-400 text-slate-950 shadow-lg shadow-cyan-500/20">
            <Landmark className="h-6 w-6" />
          </div>
          <div>
            <div className="text-lg font-black text-white">بورس‌نگار</div>
            <div className="text-[11px] text-slate-400">سامانه تحلیل بنیادی بورس تهران</div>
          </div>
        </div>
        <button
          type="button"
          onClick={onOpenExport}
          className="no-print inline-flex items-center justify-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-xs font-bold text-slate-200 transition hover:border-cyan-500/60 hover:text-white"
        >
          <Download className="h-4 w-4 text-cyan-400" />
          خروجی گزارش
        </button>
      </div>

      <div className="grid gap-6 p-5 md:p-7 lg:grid-cols-[1fr_320px]">
        <div className="space-y-5">
          <div className="flex flex-wrap items-center gap-2 text-xs">
            <span className="inline-flex items-center gap-1.5 rounded-full border border-cyan-500/30 bg-cyan-500/10 px-3 py-1 text-cyan-300">
              <Building2 className="h-3.5 w-3.5" />
              {info.industryTitle || 'بورس تهران'}
            </span>
            <span className="inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-emerald-300">
              <CheckCircle2 className="h-3.5 w-3.5" />
              {info.codalAuditStatus || 'گزارش رسمی کدال'}
            </span>
          </div>

          <div>
            <p className="mb-2 text-xs font-bold tracking-wide text-cyan-400">کارت سلامت بنیادی</p>
            <h1 className="text-2xl font-black leading-tight text-white md:text-4xl">
              {info.fullName}
              <span className="mr-2 text-cyan-400">({info.symbol})</span>
            </h1>
            <p className="mt-3 max-w-3xl text-sm leading-7 text-slate-400">{info.financialReportTitle}</p>
          </div>

          <div className="flex flex-wrap gap-2 text-xs text-slate-300">
            <span className="rounded-lg border border-slate-700 bg-slate-800/70 px-3 py-2">
              ارزش بازار: <strong className="text-white">{info.marketCap || 'نامشخص'}</strong>
            </span>
            {info.reportDate && (
              <span className="inline-flex items-center gap-1.5 rounded-lg border border-slate-700 bg-slate-800/70 px-3 py-2">
                <CalendarDays className="h-3.5 w-3.5 text-amber-400" />
                انتشار: <strong className="text-white">{info.reportDate}</strong>
              </span>
            )}
          </div>
        </div>

        <div className="grid grid-cols-2 gap-3 lg:grid-cols-1">
          <div className="rounded-xl border border-emerald-500/20 bg-emerald-500/5 p-4">
            <div className="mb-1 text-[11px] text-slate-400">آخرین قیمت</div>
            <div className="text-xl font-black text-emerald-300">{priceDisplay}</div>
          </div>
          <div className="rounded-xl border border-cyan-500/20 bg-cyan-500/5 p-4">
            <div className="mb-1 flex items-center gap-1 text-[11px] text-slate-400"><TrendingUp className="h-3.5 w-3.5" /> نسبت P/E</div>
            <div className="text-xl font-black text-cyan-300">{info.peRatio || 'نامشخص'}</div>
          </div>
          <div className="col-span-2 rounded-xl border border-slate-700 bg-slate-950/60 p-4 lg:col-span-1">
            <div className="mb-2 flex items-center gap-1.5 text-[11px] font-bold text-slate-300"><Database className="h-3.5 w-3.5 text-cyan-400" /> منبع و زمان استعلام</div>
            <p className="text-[10px] leading-5 text-slate-400">{info.dataStamp.source}</p>
            <div className="mt-2 border-t border-slate-800 pt-2 text-[10px] text-slate-500">{info.dataStamp.updatedAt || 'زمان ثبت نشده'}</div>
          </div>
        </div>
      </div>
    </header>
  );
};
