import React from 'react';
import { ExplanationCard, StatusType } from '../types';
import { BookOpen, CheckCircle, AlertTriangle, XCircle, Sparkles } from 'lucide-react';

interface ExplanationCardsGridProps {
  cards: ExplanationCard[];
}

export const ExplanationCardsGrid: React.FC<ExplanationCardsGridProps> = ({ cards }) => {
  const list = cards || [];

  const getStatusBadge = (status: StatusType) => {
    switch (status) {
      case 'good':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
            <CheckCircle className="w-3 h-3" />
            خوب
          </span>
        );
      case 'mid':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30 flex items-center gap-1">
            <AlertTriangle className="w-3 h-3" />
            متوسط
          </span>
        );
      case 'bad':
        return (
          <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30 flex items-center gap-1">
            <XCircle className="w-3 h-3" />
            ضعیف
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <section className="mb-5">
      <div className="flex items-center gap-2 mb-3 text-slate-200">
        <BookOpen className="w-4 h-4 text-cyan-400" />
        <h2 className="text-base font-bold text-white">شش کارت توضیحی (آموزش روان به زبان ساده)</h2>
        <span className="text-[11px] text-slate-400 font-normal mr-auto">درک ساده اصطلاحات مالی (بدون استفاده از جدول)</span>
      </div>

      {/* Grid of 6 Explanation Cards in 3 Columns - Bento Style */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {list.map((card) => (
          <div
            key={card.id}
            className="bg-slate-800/40 p-3.5 rounded-lg border border-slate-700/50 flex flex-col justify-between hover:border-cyan-500/40 transition-colors"
          >
            <div>
              {/* Header: Number Badge & Status */}
              <div className="flex items-center justify-between pb-2 border-b border-slate-700/60 mb-2">
                <div className="flex items-center gap-2">
                  <span className="w-6 h-6 rounded bg-cyan-500/10 border border-cyan-500/30 text-cyan-300 font-mono font-bold text-[10px] flex items-center justify-center">
                    {card.numberLabel}
                  </span>
                  <h3 className="text-xs font-bold text-cyan-300">{card.title}</h3>
                </div>
                {getStatusBadge(card.status)}
              </div>

              {/* Value Highlight */}
              <div className="bg-slate-900/90 border border-slate-800 rounded px-2.5 py-1.5 text-[11px] font-mono font-bold text-cyan-300 mb-2.5 flex items-center justify-between">
                <span className="text-slate-400 font-sans font-normal text-[10px]">مقدار استخراج‌شده:</span>
                <span>{card.valueText}</span>
              </div>

              {/* 13-Year-Old Digestible Definition */}
              <div className="space-y-1 mb-2.5 bg-slate-900/50 p-2.5 rounded border border-slate-800/60 text-[11px]">
                <div className="text-amber-400 font-semibold flex items-center gap-1 text-[10px]">
                  <Sparkles className="w-3 h-3" />
                  <span>توضیح ساده:</span>
                </div>
                <p className="text-slate-300 leading-relaxed text-[10px]">
                  {card.simpleDefinition13Yo}
                </p>
              </div>
            </div>

            {/* Company Context Note */}
            <div className="pt-2 border-t border-slate-700/50 text-[10px] text-slate-400">
              <strong className="text-slate-300 font-semibold ml-1">وضعیت در این نماد:</strong>
              {card.companyContextNote}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};
