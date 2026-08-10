import React from 'react';
import { StatusBannerMetric, StatusType } from '../types';
import { Gauge } from 'lucide-react';

interface StatusBannerProps {
  metrics: StatusBannerMetric[];
}

export const StatusBanner: React.FC<StatusBannerProps> = ({ metrics }) => {
  const list = metrics || [];

  const getStatusStyle = (status: StatusType) => {
    switch (status) {
      case 'good':
        return {
          container: 'bg-emerald-500/10 border-emerald-500/20 text-emerald-300',
          dot: 'bg-emerald-500',
        };
      case 'mid':
        return {
          container: 'bg-amber-500/10 border-amber-500/20 text-amber-300',
          dot: 'bg-amber-500',
        };
      case 'bad':
        return {
          container: 'bg-rose-500/10 border-rose-500/20 text-rose-300',
          dot: 'bg-rose-500',
        };
      default:
        return {
          container: 'bg-slate-800 border-slate-700 text-slate-300',
          dot: 'bg-cyan-400',
        };
    }
  };

  return (
    <section className="mb-5">
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg">
        <div className="flex items-center gap-2 mb-3 pb-2 border-b border-slate-800">
          <Gauge className="w-4 h-4 text-cyan-400" />
          <h3 className="text-sm font-bold text-white">نوار شش‌تایی وضعیت و معیارهای بنیادی</h3>
          <span className="text-[11px] text-slate-400 font-normal mr-auto">خلاصه کارنامه ۶ شاخص کلیدی</span>
        </div>

        {/* 6 Grid Bento Metrics */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2.5">
          {list.map((item) => {
            const style = getStatusStyle(item.status);
            return (
              <div
                key={item.id}
                className={`border rounded p-2.5 flex items-center justify-between gap-2 ${style.container} transition-all hover:bg-slate-800/80`}
              >
                <div className="space-y-0.5 truncate">
                  <span className="text-[10px] font-bold block truncate">{item.label}</span>
                  <span className="text-xs font-bold font-mono text-white block">
                    {item.value}
                  </span>
                </div>
                <div className={`w-2.5 h-2.5 rounded-full shrink-0 ${style.dot}`} />
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
};
