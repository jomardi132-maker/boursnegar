import React, { useState } from 'react';
import { X, Sliders, Check } from 'lucide-react';

interface CustomDataModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (data: any) => void;
  initialSymbol: string;
}

export const CustomDataModal: React.FC<CustomDataModalProps> = ({
  isOpen,
  onClose,
  onSubmit,
  initialSymbol,
}) => {
  const [symbol, setSymbol] = useState(initialSymbol || 'سهم_سفارشی');
  const [fullName, setFullName] = useState('شرکت آزمایشی بورس');
  const [industry, setIndustry] = useState('manufacturing');
  const [price, setPrice] = useState('4500');
  const [eps, setEps] = useState('750');
  const [salesGrowth, setSalesGrowth] = useState('45');
  const [inflationRate, setInflationRate] = useState('42');
  const [grossMargin, setGrossMargin] = useState('32');
  const [cashFlowQuality, setCashFlowQuality] = useState('88');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({
      symbol,
      fullName,
      industry,
      currentPrice: Number(price),
      eps: Number(eps),
      salesGrowth: Number(salesGrowth),
      inflationRate: Number(inflationRate),
      grossMargin: Number(grossMargin),
      cashFlowQuality: Number(cashFlowQuality),
    });
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-700 rounded-2xl w-full max-w-xl p-6 shadow-2xl space-y-5 relative">
        
        <div className="flex items-center justify-between pb-3 border-b border-slate-800">
          <div className="flex items-center gap-2 text-teal-400 font-bold">
            <Sliders className="w-5 h-5" />
            <h3 className="text-white text-base">ورودی سفارشی صورت مالی و تحلیل بنیادی</h3>
          </div>
          <button
            onClick={onClose}
            className="text-slate-400 hover:text-white p-1 rounded-lg hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4 text-xs">
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">نماد سهام:</label>
              <input
                type="text"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-400"
                required
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">نام کامل شرکت:</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-400"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">نوع صنعت:</label>
              <select
                value={industry}
                onChange={(e) => setIndustry(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-400"
              >
                <option value="manufacturing">تولیدی / فلزات و پتروشیمی</option>
                <option value="bank">بانک و موسسات اعتباری</option>
                <option value="holding">هلدینگ و سرمایه‌گذاری</option>
                <option value="insurance">بیمه و صندوق تقاعد</option>
                <option value="services">خدماتی و سایر</option>
              </select>
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">قیمت روز (ریال):</label>
              <input
                type="number"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-400"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">سود دوازده‌ماهه EPS (ریال):</label>
              <input
                type="number"
                value={eps}
                onChange={(e) => setEps(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-400"
                required
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">رشد اسمی درآمد (درصد):</label>
              <input
                type="number"
                value={salesGrowth}
                onChange={(e) => setSalesGrowth(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-400"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-slate-300 font-medium mb-1">حاشیه سود ناخالص / حاشیه اصلی (درصد):</label>
              <input
                type="number"
                value={grossMargin}
                onChange={(e) => setGrossMargin(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-400"
                required
              />
            </div>
            <div>
              <label className="block text-slate-300 font-medium mb-1">نسبت جریان نقد به سود (درصد):</label>
              <input
                type="number"
                value={cashFlowQuality}
                onChange={(e) => setCashFlowQuality(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-teal-400"
                required
              />
            </div>
          </div>

          <div className="pt-3 border-t border-slate-800 flex justify-end gap-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 font-medium"
            >
              انصراف
            </button>
            <button
              type="submit"
              className="px-5 py-2 rounded-xl bg-gradient-to-r from-teal-500 to-emerald-500 hover:from-teal-400 hover:to-emerald-400 text-white font-bold flex items-center gap-1.5 shadow-lg shadow-teal-500/20"
            >
              <Check className="w-4 h-4" />
              تولید کارت سلامت سفارشی
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
