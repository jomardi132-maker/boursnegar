import React, { useState } from 'react';
import { StockAlert, UserProfile } from '../types';
import { Bell, Plus, Trash2, X, AlertCircle, Phone, CheckCircle, ShieldAlert } from 'lucide-react';

interface StockAlertsModalProps {
  isOpen: boolean;
  onClose: () => void;
  activeSymbol?: string;
  user: UserProfile | null;
  onOpenAuth: () => void;
  onOpenSubscription: () => void;
}

export const StockAlertsModal: React.FC<StockAlertsModalProps> = ({
  isOpen,
  onClose,
  activeSymbol = 'فولاد',
  user,
  onOpenAuth,
  onOpenSubscription,
}) => {
  const [alerts, setAlerts] = useState<StockAlert[]>([
    {
      id: 'alt-1',
      symbol: 'فولاد',
      targetPrice: 4800,
      condition: 'below',
      mobile: user?.mobile || '09123456789',
      createdAt: '۱۴۰۴/۰۵/۰۱',
      active: true,
    },
    {
      id: 'alt-2',
      symbol: 'وبملت',
      targetPe: 4.5,
      condition: 'below',
      mobile: user?.mobile || '09123456789',
      createdAt: '۱۴۰۴/۰۵/۰۳',
      active: true,
    },
  ]);

  const [targetPriceInput, setTargetPriceInput] = useState<string>('5000');
  const [targetPeInput, setTargetPeInput] = useState<string>('5.0');
  const [alertType, setAlertType] = useState<'price' | 'pe'>('price');
  const [condition, setCondition] = useState<'below' | 'above'>('below');

  if (!isOpen) return null;

  const handleAddAlert = (e: React.FormEvent) => {
    e.preventDefault();

    if (!user?.isLoggedIn) {
      onOpenAuth();
      return;
    }

    if (!user.isVip) {
      onOpenSubscription();
      return;
    }

    const newAlert: StockAlert = {
      id: `alt-${Date.now()}`,
      symbol: activeSymbol,
      targetPrice: alertType === 'price' ? Number(targetPriceInput) : undefined,
      targetPe: alertType === 'pe' ? Number(targetPeInput) : undefined,
      condition,
      mobile: user.mobile,
      createdAt: new Date().toLocaleDateString('fa-IR'),
      active: true,
    };

    setAlerts([newAlert, ...alerts]);
  };

  const handleDeleteAlert = (id: string) => {
    setAlerts(alerts.filter((a) => a.id !== id));
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md">
      <div className="relative w-full max-w-lg bg-slate-900 border border-slate-800 rounded-2xl p-5 md:p-6 shadow-2xl space-y-5 text-right">
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
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
            <Bell className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white flex items-center gap-2">
              <span>مدیریت هشدارهای هوشمند پیامکی ({activeSymbol})</span>
              <span className="text-[10px] bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30 font-mono">
                SMS Alert Engine
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              ارسال پیامک آنی روی شماره موبایل با رسیدن قیمت یا P/E به حد هدف
            </p>
          </div>
        </div>

        {/* User Auth/VIP Check banner */}
        {!user?.isLoggedIn ? (
          <div className="p-3 bg-amber-500/10 border border-amber-500/30 rounded-xl text-xs space-y-2 text-amber-300">
            <p className="font-bold flex items-center gap-1.5">
              <AlertCircle className="w-4 h-4 text-amber-400 shrink-0" />
              <span>برای ثبت هشدار پیامکی ابتدا وارد حساب کاربری شوید:</span>
            </p>
            <button
              type="button"
              onClick={onOpenAuth}
              className="w-full bg-amber-500 text-slate-950 font-bold py-1.5 rounded-lg text-xs"
            >
              ورود با شماره موبایل
            </button>
          </div>
        ) : !user.isVip ? (
          <div className="p-3 bg-cyan-500/10 border border-cyan-500/30 rounded-xl text-xs space-y-2 text-cyan-300">
            <p className="font-bold flex items-center gap-1.5">
              <ShieldAlert className="w-4 h-4 text-cyan-400 shrink-0" />
              <span>هشدارهای پیامکی مخصوص مشترکین پنل ویژه (VIP) می‌باشد:</span>
            </p>
            <button
              type="button"
              onClick={onOpenSubscription}
              className="w-full bg-amber-500 text-slate-950 font-bold py-1.5 rounded-lg text-xs"
            >
              ارتقا به پنل VIP
            </button>
          </div>
        ) : null}

        {/* Form to Add New Alert */}
        <form onSubmit={handleAddAlert} className="space-y-3 bg-slate-950 p-3.5 rounded-xl border border-slate-800">
          <div className="text-xs font-bold text-slate-200 border-b border-slate-900 pb-2 flex justify-between items-center">
            <span>افزودن هشدار جدید برای {activeSymbol}:</span>
            <span className="text-[10px] text-slate-400 font-mono">ارسال به {user?.mobile || 'شماره شما'}</span>
          </div>

          <div className="grid grid-cols-2 gap-2 text-xs">
            {/* Alert Type */}
            <div>
              <label className="text-slate-400 text-[11px] block mb-1">نوع پارامتر:</label>
              <select
                value={alertType}
                onChange={(e) => setAlertType(e.target.value as 'price' | 'pe')}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-xs focus:outline-none"
              >
                <option value="price">قیمت سهم (ریال)</option>
                <option value="pe">P/E آینده‌نگر (مرتبه)</option>
              </select>
            </div>

            {/* Condition */}
            <div>
              <label className="text-slate-400 text-[11px] block mb-1">شرط هشدار:</label>
              <select
                value={condition}
                onChange={(e) => setCondition(e.target.value as 'below' | 'above')}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-xs focus:outline-none"
              >
                <option value="below">افت به کمتر از حد هدف</option>
                <option value="above">عبور به بالاتر از حد هدف</option>
              </select>
            </div>
          </div>

          {/* Target Value Input */}
          <div className="space-y-1">
            <label className="text-slate-400 text-[11px]">
              {alertType === 'price' ? 'قیمت هدف (ریال):' : 'مقدار P/E هدف (مرتبه):'}
            </label>
            <input
              type="number"
              value={alertType === 'price' ? targetPriceInput : targetPeInput}
              onChange={(e) =>
                alertType === 'price'
                  ? setTargetPriceInput(e.target.value)
                  : setTargetPeInput(e.target.value)
              }
              className="w-full bg-slate-900 border border-slate-700 text-amber-400 font-mono font-bold rounded-lg p-2 text-sm focus:outline-none text-left"
              placeholder={alertType === 'price' ? '5000' : '5.0'}
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold py-2 rounded-lg transition-all text-xs flex items-center justify-center gap-1.5 shadow"
          >
            <Plus className="w-4 h-4" />
            <span>ثبت و فعال‌سازی هشدار پیامکی</span>
          </button>
        </form>

        {/* Existing Alerts List */}
        <div className="space-y-2">
          <h4 className="text-xs font-bold text-slate-300">هشدارهای فعال شما:</h4>

          {alerts.length === 0 ? (
            <div className="p-4 bg-slate-950 rounded-xl text-center text-xs text-slate-500">
              هنوز هیچ هشداری ثبت نکرده‌اید.
            </div>
          ) : (
            <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
              {alerts.map((alt) => (
                <div
                  key={alt.id}
                  className="bg-slate-950 border border-slate-800 rounded-xl p-3 flex items-center justify-between text-xs"
                >
                  <div className="space-y-0.5">
                    <div className="font-bold text-white flex items-center gap-2">
                      <span className="text-amber-400 font-mono">{alt.symbol}</span>
                      <span className="text-slate-400">
                        {alt.targetPrice
                          ? `قیمت ${alt.condition === 'below' ? 'کمتر از' : 'بیشتر از'} ${alt.targetPrice.toLocaleString('fa-IR')} ریال`
                          : `P/E ${alt.condition === 'below' ? 'کمتر از' : 'بیشتر از'} ${alt.targetPe} مرتبه`}
                      </span>
                    </div>
                    <div className="text-[10px] text-slate-500 font-mono">
                      شماره: {alt.mobile} | تاریخ ثبت: {alt.createdAt}
                    </div>
                  </div>

                  <button
                    type="button"
                    onClick={() => handleDeleteAlert(alt.id)}
                    className="p-1.5 text-slate-500 hover:text-rose-400 hover:bg-rose-500/10 rounded-lg transition-colors"
                    title="حذف هشدار"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
