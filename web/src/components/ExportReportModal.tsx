import React from 'react';
import { StockHealthCardData } from '../types';
import { FileSpreadsheet, Printer, Download, FileText, CheckCircle2, X, Sparkles } from 'lucide-react';

interface ExportReportModalProps {
  isOpen: boolean;
  onClose: () => void;
  data: StockHealthCardData | null;
}

export const ExportReportModal: React.FC<ExportReportModalProps> = ({ isOpen, onClose, data }) => {
  if (!isOpen || !data) return null;

  const symbol = data.header?.symbol || 'نماد';
  const companyName = data.header?.companyName || 'شرکت بورسی';

  const handleExportCsv = () => {
    // Generate CSV data string
    const csvRows = [
      ['نماد', 'نام شرکت', 'قیمت فعلی (ریال)', 'P/E TTM', 'وضعیت گزارش کدال', 'پیشنهاد خرید'],
      [
        symbol,
        companyName,
        data.header?.currentPrice || '',
        data.header?.peRatio || '',
        data.header?.codalAuditStatus || '',
        data.smartRecommendation?.statusTitle || '',
      ],
      [],
      ['فصل', 'سود خالص نماد (میلیارد ریال)', 'میانگین صنعت (میلیارد ریال)', 'حاشیه سود (٪)'],
      ...(data.quarterlyProfits || []).map((q) => [
        q.quarter,
        q.stockProfit,
        q.industryAvgProfit,
        `${q.marginPercent}%`,
      ]),
      [],
      ['رویداد کلیدی کدال', 'تاریخ', 'خلاصه تصمیمات'],
      ...(data.keyEvents || []).map((e) => [e.title, e.date, e.summary]),
    ];

    const csvContent =
      'data:text/csv;charset=utf-8,\uFEFF' + csvRows.map((e) => e.join(',')).join('\n');

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Bourse_Analysis_${symbol}_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handlePrint = () => {
    window.print();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5 text-right">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 left-4 p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div className="w-10 h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 shrink-0">
            <FileSpreadsheet className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>خروجی و دانلود گزارش مالی ({symbol})</span>
              <span className="text-[10px] bg-teal-500/20 text-teal-300 px-2 py-0.5 rounded border border-teal-500/30 font-mono">
                Export Data
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              دریافت فایل اکسل جامع صورت‌های مالی، سود فصلی و مدل ارزش‌گذاری
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-3">
          {/* CSV/Excel Download */}
          <button
            type="button"
            onClick={handleExportCsv}
            className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold p-3.5 rounded-xl transition-all shadow-lg flex items-center justify-between text-xs group"
          >
            <div className="flex items-center gap-2.5">
              <FileSpreadsheet className="w-5 h-5 text-slate-950" />
              <div className="text-right">
                <div className="text-sm font-extrabold">دانلود فایل اکسل / CSV کامل</div>
                <div className="text-[10px] opacity-80">شامل سود فصلی، شبیه‌سازی P/E و رویدادهای کدال</div>
              </div>
            </div>
            <Download className="w-4 h-4 group-hover:translate-y-0.5 transition-transform" />
          </button>

          {/* Print/PDF Download */}
          <button
            type="button"
            onClick={handlePrint}
            className="w-full bg-slate-800 hover:bg-slate-700 text-white font-bold p-3.5 rounded-xl transition-all border border-slate-700 flex items-center justify-between text-xs"
          >
            <div className="flex items-center gap-2.5">
              <Printer className="w-5 h-5 text-cyan-400" />
              <div className="text-right">
                <div className="text-sm font-bold">چاپ / ذخیره PDF گزارش رسمی</div>
                <div className="text-[10px] text-slate-400">فرمت استاندارد تحلیل مالی آماده ارائه‌های سازمانی</div>
              </div>
            </div>
            <FileText className="w-4 h-4 text-slate-400" />
          </button>
        </div>

        {/* Footnote */}
        <div className="p-3 bg-slate-950 rounded-xl border border-slate-800 text-[11px] text-slate-400 space-y-1">
          <div className="font-bold text-amber-300 flex items-center gap-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>مدل استاندارد تحلیل صورت‌های مالی کدال</span>
          </div>
          <p>
            فایل خروجی حاوی تاریخچه سودآوری، نسبت‌های مالی TTM، P/E آینده‌نگر و جدول رویدادهای رسمی کدال می‌باشد.
          </p>
        </div>
      </div>
    </div>
  );
};
