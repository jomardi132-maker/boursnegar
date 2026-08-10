import React, { useState } from 'react';
import { CodalKeyEvent, CodalEventType } from '../types';
import { Calendar, Building2, Users, TrendingUp, Award, ExternalLink, Filter, Sparkles, AlertCircle, FileText } from 'lucide-react';

interface KeyEventsCardProps {
  keyEvents?: CodalKeyEvent[];
  symbol?: string;
}

export const KeyEventsCard: React.FC<KeyEventsCardProps> = ({
  keyEvents = [],
  symbol = 'نماد',
}) => {
  const [selectedFilter, setSelectedFilter] = useState<CodalEventType | 'all'>('all');

  if (!keyEvents || keyEvents.length === 0) return null;

  const filteredEvents =
    selectedFilter === 'all'
      ? keyEvents
      : keyEvents.filter((evt) => evt.type === selectedFilter);

  const getEventIcon = (type: CodalEventType) => {
    switch (type) {
      case 'assembly':
        return <Award className="w-4 h-4 text-amber-400 shrink-0" />;
      case 'capital_increase':
        return <TrendingUp className="w-4 h-4 text-emerald-400 shrink-0" />;
      case 'board_change':
        return <Users className="w-4 h-4 text-cyan-400 shrink-0" />;
      case 'dividend':
        return <Building2 className="w-4 h-4 text-blue-400 shrink-0" />;
      default:
        return <FileText className="w-4 h-4 text-slate-400 shrink-0" />;
    }
  };

  const getEventTypeTitle = (type: CodalEventType) => {
    switch (type) {
      case 'assembly':
        return 'مجمع عمومی';
      case 'capital_increase':
        return 'افزایش سرمایه';
      case 'board_change':
        return 'هیئت مدیره';
      case 'dividend':
        return 'تقسیم سود';
      default:
        return 'اطلاعیه کدال';
    }
  };

  const getBadgeStyle = (impact?: 'positive' | 'neutral' | 'negative') => {
    switch (impact) {
      case 'positive':
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
      case 'negative':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      default:
        return 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40';
    }
  };

  return (
    <section id="codal-key-events-card" className="mb-5">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 md:p-5 shadow-xl space-y-4">
        {/* Header Title */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-amber-500/10 border border-amber-500/30 flex items-center justify-center shrink-0">
              <Calendar className="w-4 h-4 text-amber-400" />
            </div>
            <div>
              <h2 className="text-base font-bold text-white flex items-center gap-1.5">
                <span>رویدادهای کلیدی اخیر کدال ({symbol})</span>
                <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30 font-mono">
                  Codal Events
                </span>
              </h2>
              <p className="text-[11px] text-slate-400 mt-0.5">
                خلاصه تصمیمات مجمع عمومی، آگهی افزایش سرمایه و تغییرات هیئت مدیره
              </p>
            </div>
          </div>

          {/* Event Filter Pills */}
          <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800 text-xs shrink-0">
            <button
              type="button"
              onClick={() => setSelectedFilter('all')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                selectedFilter === 'all'
                  ? 'bg-amber-500 text-slate-950 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              همه ({keyEvents.length})
            </button>

            <button
              type="button"
              onClick={() => setSelectedFilter('assembly')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                selectedFilter === 'assembly'
                  ? 'bg-amber-500 text-slate-950 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              مجامع
            </button>

            <button
              type="button"
              onClick={() => setSelectedFilter('capital_increase')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                selectedFilter === 'capital_increase'
                  ? 'bg-amber-500 text-slate-950 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              افزایش سرمایه
            </button>

            <button
              type="button"
              onClick={() => setSelectedFilter('board_change')}
              className={`px-2.5 py-1 rounded-md text-[11px] font-bold transition-all ${
                selectedFilter === 'board_change'
                  ? 'bg-amber-500 text-slate-950 shadow'
                  : 'text-slate-400 hover:text-white'
              }`}
            >
              هیئت مدیره
            </button>
          </div>
        </div>

        {/* Events Cards List */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {filteredEvents.map((evt) => (
            <div
              key={evt.id}
              className="bg-slate-950/80 border border-slate-800/80 hover:border-amber-500/40 rounded-xl p-3.5 space-y-2.5 transition-all hover:bg-slate-950 flex flex-col justify-between"
            >
              <div>
                {/* Event Type & Date */}
                <div className="flex items-center justify-between gap-2 pb-2 border-b border-slate-900">
                  <div className="flex items-center gap-1.5">
                    {getEventIcon(evt.type)}
                    <span className="text-[11px] font-bold text-amber-300">
                      {getEventTypeTitle(evt.type)}
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400 bg-slate-900 px-2 py-0.5 rounded border border-slate-800">
                    {evt.date}
                  </span>
                </div>

                {/* Event Title */}
                <h3 className="text-xs font-bold text-white mt-2 leading-snug">
                  {evt.title}
                </h3>

                {/* Summary Description */}
                <p className="text-[11px] text-slate-300/90 leading-relaxed mt-1.5">
                  {evt.summary}
                </p>
              </div>

              {/* Event Key Result Badge & Codal Link */}
              <div className="pt-2 border-t border-slate-900 flex items-center justify-between gap-2 text-[10px]">
                <span
                  className={`px-2 py-0.5 rounded text-[10px] font-bold border font-mono ${getBadgeStyle(
                    evt.impactStatus
                  )}`}
                >
                  {evt.badgeText}
                </span>

                <a
                  href="https://codal.ir"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-slate-400 hover:text-cyan-300 flex items-center gap-1 transition-colors"
                >
                  <span>مشاهده در کدال</span>
                  <ExternalLink className="w-2.5 h-2.5" />
                </a>
              </div>
            </div>
          ))}
        </div>

        {/* Card Footer Note */}
        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[10px] text-slate-500">
          <span>
            منبع اطلاعیه‌ها: سامانه جامع اطلاع‌رسانی ناشران (Codal.ir)
          </span>
          <span className="font-mono">
            ثبت رسمی در سازمان بورس و اوراق بهادار
          </span>
        </div>
      </div>
    </section>
  );
};
