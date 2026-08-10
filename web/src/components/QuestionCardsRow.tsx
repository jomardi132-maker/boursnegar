import React from 'react';
import { QuestionCard, StatusType } from '../types';
import { HelpCircle, CheckCircle, AlertTriangle, XCircle, ArrowUpRight } from 'lucide-react';

interface QuestionCardsRowProps {
  questions: QuestionCard[];
}

export const QuestionCardsRow: React.FC<QuestionCardsRowProps> = ({ questions }) => {
  const list = questions || [];

  const getStatusBadge = (status: StatusType, label: string) => {
    switch (status) {
      case 'good':
        return (
          <span className="px-2.5 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 rounded text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
            <CheckCircle className="w-3 h-3 text-emerald-400" />
                    {label || 'خوب'}
          </span>
        );
      case 'mid':
        return (
          <span className="px-2.5 py-0.5 bg-amber-500/20 text-amber-400 border border-amber-500/30 rounded text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
            <AlertTriangle className="w-3 h-3 text-amber-400" />
                    {label || 'متوسط'}
          </span>
        );
      case 'bad':
        return (
          <span className="px-2.5 py-0.5 bg-rose-500/20 text-rose-400 border border-rose-500/30 rounded text-[10px] font-bold uppercase tracking-wider flex items-center gap-1">
            <XCircle className="w-3 h-3 text-rose-400" />
                    {label || 'ضعیف'}
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <section className="mb-5">
      <div className="flex items-center gap-2 mb-3 text-slate-200">
        <HelpCircle className="w-4 h-4 text-cyan-400" />
        <h2 className="text-base font-bold text-white">پرسش‌های کلیدی بر پایه داده موجود</h2>
      </div>

      {/* Grid of 3 Question Cards in a Row - Bento Style */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {list.map((q) => (
          <div
            key={q.id}
            className="bg-slate-900 border-l-4 border-yellow-500 border-y border-r border-slate-800 p-4 rounded-r-xl shadow-lg relative flex flex-col justify-between hover:border-r-slate-700 transition-all"
          >
            <div>
              {/* Top Row: Number & Status Pill */}
              <div className="flex items-center justify-between gap-2 pb-2.5 border-b border-slate-800 mb-2.5">
                <div className="text-slate-500 text-[10px] font-bold uppercase tracking-widest flex items-center gap-1.5">
                  <span className="w-5 h-5 rounded bg-amber-500/10 text-amber-400 font-extrabold text-[10px] flex items-center justify-center border border-amber-500/20">
                    {(q.id ?? 1).toLocaleString('fa-IR')}
                  </span>
                  <span>سؤال شماره ۰{(q.id ?? 1).toLocaleString('fa-IR')}</span>
                </div>
                {getStatusBadge(q.status, q.statusLabel)}
              </div>

              {/* Title & Subtitle */}
              <h3 className="text-sm font-semibold text-white leading-snug mb-1">
                {q.title}
              </h3>
              <p className="text-[11px] text-slate-400 mb-3 leading-relaxed">
                {q.subtitle}
              </p>

              {/* Main Metric Banner inside Card */}
              <div className="bg-slate-950/80 border border-slate-800 rounded p-2.5 mb-3 text-xs space-y-1">
                <div className="font-bold text-cyan-300 flex items-center justify-between text-[11px]">
                  <span>شاخص سنجش:</span>
                  <span className="text-slate-100 font-mono">{q.mainMetricValue}</span>
                </div>
                <div className="text-slate-400 text-[10px] flex items-center gap-1 pt-1 border-t border-slate-900">
                  <ArrowUpRight className="w-3 h-3 text-amber-400 shrink-0" />
                  <span>{q.comparisonDetail}</span>
                </div>
              </div>
            </div>

            {/* Answer Synthesis */}
            <div className="pt-2 border-t border-slate-800 text-[11px] text-slate-300 leading-relaxed bg-slate-950/40 p-2.5 rounded border border-slate-800/80">
              <strong className="text-amber-400 block mb-0.5 font-semibold">پاسخ بنیادی محتاطانه:</strong>
              {q.summaryAnswer}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
