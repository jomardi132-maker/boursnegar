import React from 'react';
import { ConcludingCards } from '../types';
import { ShieldCheck, Compass, Database, ExternalLink, AlertTriangle } from 'lucide-react';

interface ConclusionAndSourcesProps {
  conclusion: ConcludingCards;
}

export const ConclusionAndSources: React.FC<ConclusionAndSourcesProps> = ({ conclusion }) => {
  const valuationCard = conclusion?.valuationCard || { title: 'ارزش‌گذاری', body: '' };
  const outlookCard = conclusion?.outlookCard || { title: 'چشم‌انداز', body: '' };
  const dataSourceStamp = conclusion?.dataSourceStamp || {
    title: 'منابع داده',
    codalLinkText: 'سامانه کدال (Codal.ir)',
    lastUpdate: '۱۴۰۵/۰۵/۰۶',
    disclaimer: 'این اطلاعات بر اساس گزارش‌های رسمی منتشر شده در سامانه کدال تهیه گردیده است.',
  };

  return (
    <section className="space-y-4 mb-6">
      {/* Two Bento Concluding Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        
        {/* Card 1: Business Quality / Valuation */}
        <div className="bg-emerald-900/20 border border-emerald-500/30 p-3.5 rounded-lg flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-2 text-emerald-400 font-bold">
            <ShieldCheck className="w-4 h-4 shrink-0" />
            <h3 className="text-xs uppercase tracking-wider text-emerald-400">{valuationCard.title}</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/80 p-3 rounded border border-slate-800">
            {valuationCard.body}
          </p>
        </div>

        {/* Card 2: Long-Term Outlook / Price Value */}
        <div className="bg-rose-900/20 border border-rose-500/30 p-3.5 rounded-lg flex flex-col justify-between">
          <div className="flex items-center gap-2 mb-2 text-rose-400 font-bold">
            <Compass className="w-4 h-4 shrink-0" />
            <h3 className="text-xs uppercase tracking-wider text-rose-400">{outlookCard.title}</h3>
          </div>
          <p className="text-xs text-slate-300 leading-relaxed bg-slate-900/80 p-3 rounded border border-slate-800">
            {outlookCard.body}
          </p>
        </div>

      </div>

      {/* Bento Data Sources & Verification Footer Stamp */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col md:flex-row items-center justify-between gap-3">
        
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center shrink-0">
            <Database className="w-4 h-4 text-cyan-400" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-white flex items-center gap-2">
              {dataSourceStamp.title}
            </h4>
            <div className="flex flex-wrap items-center gap-2 text-[10px] text-slate-400 mt-0.5">
              <a
                href="https://codal.ir"
                target="_blank"
                rel="noopener noreferrer"
                className="text-cyan-400 hover:underline inline-flex items-center gap-1 font-mono font-bold"
              >
                <span>{dataSourceStamp.codalLinkText}</span>
                <ExternalLink className="w-3 h-3" />
              </a>
              <span>•</span>
              <span>{dataSourceStamp.lastUpdate}</span>
            </div>
          </div>
        </div>

        {/* Disclaimer Warning */}
        <div className="text-[10px] text-slate-400 bg-slate-950 p-2.5 rounded border border-slate-800 flex items-center gap-2 max-w-xl">
          <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>{dataSourceStamp.disclaimer}</span>
        </div>

      </div>
    </section>
  );
};
