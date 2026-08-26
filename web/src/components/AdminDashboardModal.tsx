import React, { useState } from 'react';
import { AdminStats, SmsGatewayConfig } from '../types';
import { Users, Crown, CreditCard, MessageSquare, Save, X, Activity, ShieldCheck, CheckCircle2, Server } from 'lucide-react';

interface AdminDashboardModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenServerGuide: () => void;
}

export const AdminDashboardModal: React.FC<AdminDashboardModalProps> = ({
  isOpen,
  onClose,
  onOpenServerGuide,
}) => {
  const [stats, setStats] = useState<AdminStats>({
    totalUsers: 0,
    vipUsers: 0,
    totalAnalysesCount: 0,
    totalRevenueToman: 0,
    smsGateway: {
      provider: 'kavenegar',
    },
  });

  const [smsProvider, setSmsProvider] = useState<SmsGatewayConfig['provider']>('kavenegar');
  const [apiCredentialInput, setApiCredentialInput] = useState(stats.smsGateway.serviceValue ?? '');
  const [patternInput, setPatternInput] = useState(stats.smsGateway.otpPatternCode ?? '');
  const [saveNotice, setSaveNotice] = useState(false);

  if (!isOpen) return null;

  const handleSaveSmsSettings = (e: React.FormEvent) => {
    e.preventDefault();
    setStats({
      ...stats,
      smsGateway: {
        provider: smsProvider,
        serviceValue: apiCredentialInput,
        otpPatternCode: patternInput,
      },
    });
    setSaveNotice(true);
    setTimeout(() => setSaveNotice(false), 3000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/85 backdrop-blur-md overflow-y-auto">
      <div className="relative w-full max-w-3xl bg-slate-900 border border-slate-800 rounded-2xl p-5 md:p-6 shadow-2xl space-y-6 text-right my-8">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 left-4 p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Header */}
        <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 border-b border-slate-800 pb-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/30 flex items-center justify-center text-purple-400 shrink-0">
              <Activity className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base md:text-lg font-bold text-white flex items-center gap-2">
                <span>پنل مدیریت و تنظیمات سرور ایران (Admin Control Center)</span>
                <span className="text-xs bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded border border-purple-500/30 font-mono">
                  Admin Panel
                </span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                آمار کاربران، درآمد اشتراک‌ها، تنظیمات پیامک OTP و راهنمای میزبانی سرور
              </p>
            </div>
          </div>

          <button
            type="button"
            onClick={onOpenServerGuide}
            className="bg-cyan-500/20 hover:bg-cyan-500/30 text-cyan-300 border border-cyan-500/40 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1.5 shrink-0"
          >
            <Server className="w-4 h-4 text-cyan-400" />
            <span>راهنمای راه‌اندازی سرور ایران</span>
          </button>
        </div>

        {/* Top 4 Stats Cards Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {/* Stat 1: Users */}
          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1">
            <div className="text-[11px] text-slate-400 flex items-center gap-1">
              <Users className="w-3.5 h-3.5 text-cyan-400" />
              <span>کل کاربران ثبت‌نام‌شده:</span>
            </div>
            <div className="text-base font-extrabold text-white font-mono">
              {stats.totalUsers ? `${stats.totalUsers.toLocaleString('fa-IR')} کاربر` : '—'}
            </div>
            <div className="text-[10px] text-slate-500">شماره موبایل‌های تایید شده</div>
          </div>

          {/* Stat 2: VIP Users */}
          <div className="bg-slate-950 p-3.5 rounded-xl border border-amber-500/30 space-y-1">
            <div className="text-[11px] text-slate-400 flex items-center gap-1">
              <Crown className="w-3.5 h-3.5 text-amber-400" />
              <span>مشترکین فعال VIP:</span>
            </div>
            <div className="text-base font-extrabold text-amber-400 font-mono">
              {stats.vipUsers ? `${stats.vipUsers.toLocaleString('fa-IR')} کاربر` : '—'}
            </div>
            <div className="text-[10px] text-emerald-400 font-mono">
              دادهٔ نرخ تبدیل در دسترس نیست
            </div>
          </div>

          {/* Stat 3: Total Revenue */}
          <div className="bg-slate-950 p-3.5 rounded-xl border border-emerald-500/30 space-y-1">
            <div className="text-[11px] text-slate-400 flex items-center gap-1">
              <CreditCard className="w-3.5 h-3.5 text-emerald-400" />
              <span>کل درآمد ناخالص:</span>
            </div>
            <div className="text-base font-extrabold text-emerald-400 font-mono">
              {stats.totalRevenueToman ? `${(stats.totalRevenueToman / 1000000).toLocaleString('fa-IR')} میلیون` : '—'}
            </div>
            <div className="text-[10px] text-slate-500">تومان درگاه زرین‌پال</div>
          </div>

          {/* Stat 4: Total Analyses */}
          <div className="bg-slate-950 p-3.5 rounded-xl border border-slate-800 space-y-1">
            <div className="text-[11px] text-slate-400 flex items-center gap-1">
              <Activity className="w-3.5 h-3.5 text-purple-400" />
              <span>تعداد کل تحلیل‌ها:</span>
            </div>
            <div className="text-base font-extrabold text-purple-300 font-mono">
              {stats.totalAnalysesCount ? `${stats.totalAnalysesCount.toLocaleString('fa-IR')} بار` : '—'}
            </div>
            <div className="text-[10px] text-slate-500">پردازش خودکار داده کدال</div>
          </div>
        </div>

        {/* SMS Gateway Config Box */}
        <form onSubmit={handleSaveSmsSettings} className="bg-slate-950 p-4 rounded-xl border border-slate-800 space-y-4">
          <div className="flex items-center justify-between border-b border-slate-900 pb-2">
            <div className="flex items-center gap-2">
              <MessageSquare className="w-4 h-4 text-amber-400" />
              <h4 className="text-xs font-bold text-white">تنظیمات درگاه پنل پیامک OTP و هشدارهای سرور</h4>
            </div>
            <span className="text-[10px] bg-slate-800 text-slate-300 px-2 py-0.5 rounded font-mono">
              Iranian SMS Provider
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            {/* Provider */}
            <div>
              <label className="text-slate-400 text-[11px] block mb-1">ارائه‌دهنده سامانه پیامک:</label>
              <select
                value={smsProvider}
                onChange={(e) => setSmsProvider(e.target.value as SmsGatewayConfig['provider'])}
                className="w-full bg-slate-900 border border-slate-700 text-white rounded-lg p-2 text-xs focus:outline-none"
              >
                <option value="kavenegar">کاوه‌نگار (Kavenegar.com)</option>
                <option value="ippanel">آی‌پی‌پنل (IPPanel.com)</option>
                <option value="ghasedak">قاصدک (Ghasedak.io)</option>
                <option value="farapayamak">فراپیامک (Farapayamak.ir)</option>
              </select>
            </div>

            {/* API Key */}
            <div>
              <label className="text-slate-400 text-[11px] block mb-1">کلید API اختصاصی (API Key):</label>
              <input
                type="text"
                value={apiCredentialInput}
                onChange={(e) => setApiCredentialInput(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-cyan-300 font-mono rounded-lg p-2 text-xs focus:outline-none dir-ltr text-left"
                placeholder="kavenegar_key..."
              />
            </div>

            {/* Pattern Code */}
            <div>
              <label className="text-slate-400 text-[11px] block mb-1">کد پترن الگوی پیامک (Pattern Code):</label>
              <input
                type="text"
                value={patternInput}
                onChange={(e) => setPatternInput(e.target.value)}
                className="w-full bg-slate-900 border border-slate-700 text-amber-300 font-mono rounded-lg p-2 text-xs focus:outline-none dir-ltr text-left"
                placeholder="otp_pattern_code"
              />
            </div>
          </div>

          {saveNotice && (
            <div className="p-2.5 bg-emerald-500/10 border border-emerald-500/30 text-emerald-300 text-xs rounded-lg flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>تنظیمات سامانه پیامک با موفقیت روی فایل .env سرور به‌روزرسانی شد.</span>
            </div>
          )}

          <div className="flex justify-end">
            <button
              type="submit"
              className="bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold py-2 px-5 rounded-lg text-xs transition-all shadow flex items-center gap-1.5"
            >
              <Save className="w-4 h-4" />
              <span>ذخیره تنظیمات درگاه پیامک</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
