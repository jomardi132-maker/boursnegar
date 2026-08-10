import React, { useState } from 'react';
import { DEFAULT_TICKERS } from '../data/stocksData';
import { Search, Sparkles, SlidersHorizontal, Printer, RefreshCw } from 'lucide-react';

interface StockSearchControlsProps {
  onSelectStock: (symbol: string) => void;
  onAnalyzeQuery: (query: string) => void;
  onOpenCustomModal: () => void;
  activeSymbol: string;
  isLoading: boolean;
}

export const StockSearchControls: React.FC<StockSearchControlsProps> = ({
  onSelectStock,
  onAnalyzeQuery,
  onOpenCustomModal,
  activeSymbol,
  isLoading,
}) => {
  const [searchInput, setSearchInput] = useState('');

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchInput.trim()) return;
    onAnalyzeQuery(searchInput.trim());
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="no-print bg-slate-900 border border-slate-800 rounded-xl p-3 shadow-lg mb-5 space-y-3">
      <div className="flex flex-col lg:flex-row items-center justify-between gap-3">
        
        {/* Search Input Form */}
        <form onSubmit={handleSearchSubmit} className="w-full lg:w-auto flex-1 max-w-2xl flex items-center gap-2">
          <div className="relative w-full">
            <Search className="w-4 h-4 text-slate-400 absolute right-3 top-2.5 pointer-events-none" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => setSearchInput(e.target.value)}
              placeholder="جستجوی نماد یا نام شرکت بورس تهران (مثلاً فولاد، وبملت، شستا، فملی، دانا...)"
              className="w-full bg-slate-950 border border-slate-800 rounded-lg pr-9 pl-3 py-1.5 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-400 transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={isLoading || !searchInput.trim()}
            className="px-3.5 py-1.5 rounded-lg bg-cyan-500 hover:bg-cyan-400 disabled:opacity-50 text-slate-950 font-bold text-xs flex items-center gap-1.5 shrink-0 transition-colors"
          >
            {isLoading ? (
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
            ) : (
              <Sparkles className="w-3.5 h-3.5" />
            )}
            <span>تحلیل هوشمند</span>
          </button>
        </form>

        {/* Custom Data & Print Actions */}
        <div className="flex items-center gap-2 w-full lg:w-auto justify-end">
          <button
            onClick={onOpenCustomModal}
            className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:border-slate-600 text-slate-300 hover:text-white font-semibold text-[11px] flex items-center gap-1.5 transition-colors"
          >
            <SlidersHorizontal className="w-3.5 h-3.5 text-amber-400" />
            <span>ثبت داده اختصاصی</span>
          </button>

          <button
            onClick={handlePrint}
            className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 hover:border-slate-600 text-slate-300 hover:text-white font-semibold text-[11px] flex items-center gap-1.5 transition-colors"
          >
            <Printer className="w-3.5 h-3.5 text-emerald-400" />
            <span>چاپ / PDF</span>
          </button>
        </div>

      </div>

      {/* Preset Stock Ticker Quick Selectors */}
      <div className="pt-2 border-t border-slate-800 flex flex-wrap items-center gap-1.5 text-xs">
        <span className="text-slate-400 font-bold text-[10px] uppercase ml-1">پیش‌فرض بورس:</span>
        {(DEFAULT_TICKERS || []).map((t) => {
          const isActive = activeSymbol === t.symbol;
          return (
            <button
              key={t.symbol}
              onClick={() => onSelectStock(t.symbol)}
              className={`px-2.5 py-1 rounded text-[11px] font-bold transition-all flex items-center gap-1 ${
                isActive
                  ? 'bg-cyan-500/20 border border-cyan-400 text-cyan-300'
                  : 'bg-slate-800/80 border border-slate-700/60 text-slate-300 hover:border-slate-600 hover:text-white'
              }`}
            >
              <span className={`w-1.5 h-1.5 rounded-full ${isActive ? 'bg-cyan-400' : 'bg-slate-500'}`} />
              <span>{t.symbol} ({t.industry})</span>
            </button>
          );
        })}
      </div>
    </div>
  );
};
