import React, { useState } from 'react';
import { PeerCompany } from '../types';
import { Users, ChevronDown, ChevronUp, ExternalLink, CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

interface PeerIndustryWidgetProps {
  peers: PeerCompany[];
  currentSymbol: string;
  industryTitle: string;
  onSelectPeer?: (symbol: string) => void;
}

export const PeerIndustryWidget: React.FC<PeerIndustryWidgetProps> = ({
  peers,
  currentSymbol,
  industryTitle,
  onSelectPeer,
}) => {
  const [isCollapsed, setIsCollapsed] = useState(false);

  if (!peers || peers.length === 0) return null;

  const renderStatusBadge = (status: 'good' | 'mid' | 'bad') => {
    switch (status) {
      case 'good':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 className="w-3 h-3 text-emerald-400 shrink-0" />
            <span>سلامت: خوب</span>
          </span>
        );
      case 'mid':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-amber-500/20 text-amber-400 border border-amber-500/30">
            <AlertTriangle className="w-3 h-3 text-amber-400 shrink-0" />
            <span>سلامت: متوسط</span>
          </span>
        );
      case 'bad':
        return (
          <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[10px] font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
            <XCircle className="w-3 h-3 text-rose-400 shrink-0" />
            <span>سلامت: ضعیف</span>
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div
      id="peer-industry-corner-widget"
      className="no-print fixed bottom-4 left-4 z-40 max-w-[280px] w-full bg-slate-900/95 backdrop-blur-md border border-cyan-500/40 rounded-xl shadow-2xl overflow-hidden transition-all duration-300"
    >
      {/* Header Bar */}
      <div
        onClick={() => setIsCollapsed(!isCollapsed)}
        className="px-3 py-2 bg-slate-950/80 border-b border-slate-800 flex items-center justify-between cursor-pointer hover:bg-slate-800/60 transition-colors"
      >
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse" />
          <Users className="w-3.5 h-3.5 text-cyan-400" />
          <span className="text-xs font-bold text-white tracking-wide">
            ۳ رقیب همصنعت ({currentSymbol})
          </span>
        </div>

        <button
          type="button"
          aria-label="تغییر وضعیت نمایش"
          className="text-slate-400 hover:text-white p-0.5"
        >
          {isCollapsed ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Widget Body */}
      {!isCollapsed && (
        <div className="p-2.5 space-y-2 text-xs">
          <p className="text-[10px] text-slate-400 leading-tight">
            برترین شرکت‌های گروه <strong className="text-cyan-300 font-normal">{industryTitle}</strong>:
          </p>

          <div className="space-y-1.5">
            {peers.slice(0, 3).map((peer, idx) => (
              <div
                key={peer.symbol || idx}
                onClick={() => onSelectPeer && onSelectPeer(peer.symbol)}
                className="group flex items-center justify-between p-2 rounded-lg bg-slate-800/60 hover:bg-slate-800 border border-slate-700/50 hover:border-cyan-500/50 transition-all cursor-pointer"
              >
                <div className="flex items-center gap-2 truncate">
                  <span className="w-5 h-5 rounded bg-slate-900 text-cyan-400 text-[10px] font-mono font-bold flex items-center justify-center border border-slate-700">
                    ۰{idx + 1}
                  </span>
                  <div className="truncate">
                    <div className="font-bold text-white text-[11px] group-hover:text-cyan-300 transition-colors flex items-center gap-1">
                      <span>{peer.symbol}</span>
                      <ExternalLink className="w-2.5 h-2.5 opacity-0 group-hover:opacity-100 transition-opacity text-cyan-400" />
                    </div>
                    <div className="text-[9px] text-slate-400 truncate">{peer.name}</div>
                  </div>
                </div>

                <div className="shrink-0 mr-1">
                  {renderStatusBadge(peer.healthStatus)}
                </div>
              </div>
            ))}
          </div>

          <div className="pt-1 text-[9px] text-slate-500 text-center font-mono border-t border-slate-800">
            برای بررسی نماد کلیک کنید
          </div>
        </div>
      )}
    </div>
  );
};
