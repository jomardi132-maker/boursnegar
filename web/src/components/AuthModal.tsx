import React, { useState, useEffect } from 'react';
import { UserProfile } from '../types';
import { Phone, ShieldCheck, Lock, Sparkles, X, CheckCircle2, ArrowRight, RefreshCw, MessageSquare } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginSuccess: (user: UserProfile) => void;
}

export const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, onLoginSuccess }) => {
  const [step, setStep] = useState<'mobile' | 'otp'>('mobile');
  const [mobile, setMobile] = useState('');
  const [otpCode, setOtpCode] = useState('');
  const [countdown, setCountdown] = useState(60);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [demoOtpNotice, setDemoOtpNotice] = useState('');

  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (step === 'otp' && countdown > 0) {
      timer = setInterval(() => {
        setCountdown((prev) => prev - 1);
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [step, countdown]);

  if (!isOpen) return null;

  const validateMobile = (num: string) => {
    const clean = num.trim();
    return /^09\d{9}$/.test(clean);
  };

  const handleSendOtp = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    if (!validateMobile(mobile)) {
      setErrorMessage('لطفاً یک شماره موبایل معتبر ۱۱ رقمی (مانند ۰۹۱۲۳۴۵۶۷۸۹) وارد کنید.');
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      setStep('otp');
      setCountdown(60);
      const testCode = Math.floor(100000 + Math.random() * 900000).toString();
      setDemoOtpNotice(`کد پیامک‌شده به شماره ${mobile}: ${testCode} (یا کد تست عمومی ۱۲۳۴۵۶)`);
    }, 800);
  };

  const handleVerifyOtp = (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage('');

    if (otpCode.length < 5) {
      setErrorMessage('لطفاً کد تایید ۵ یا ۶ رقمی دریافتی را به طور کامل وارد کنید.');
      return;
    }

    setIsLoading(true);

    setTimeout(() => {
      setIsLoading(false);
      // Construct user profile
      const user: UserProfile = {
        mobile,
        isLoggedIn: true,
        isVip: false, // initial free user
        remainingFreeQuota: 5, // 5 free analyses
        usedQuota: 0,
        subscriptionPlan: 'free',
      };

      // Save user to localStorage
      localStorage.setItem('bourse_user_profile', JSON.stringify(user));
      onLoginSuccess(user);
      onClose();
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/80 backdrop-blur-md">
      <div className="relative w-full max-w-md bg-slate-900 border border-slate-800 rounded-2xl p-6 shadow-2xl space-y-5 text-right">
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 left-4 p-1 text-slate-400 hover:text-white rounded-lg hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Modal Header */}
        <div className="flex items-center gap-3 border-b border-slate-800 pb-4">
          <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
            <ShieldCheck className="w-5 h-5" />
          </div>
          <div>
            <h3 className="text-base font-bold text-white">ورود / ثبت‌نام با شماره موبایل</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              ۵ تحلیل اول حساب کاربری شما کاملاً رایگان خواهد بود
            </p>
          </div>
        </div>

        {/* Step 1: Mobile Form */}
        {step === 'mobile' ? (
          <form onSubmit={handleSendOtp} className="space-y-4">
            <div className="space-y-1.5">
              <label className="text-xs font-bold text-slate-300 flex items-center justify-between">
                <span>شماره تلفن همراه شما:</span>
                <span className="text-[10px] text-amber-400 font-mono">دریافت پیامک یک‌بارمصرف</span>
              </label>

              <div className="relative">
                <input
                  type="tel"
                  dir="ltr"
                  placeholder="09123456789"
                  value={mobile}
                  onChange={(e) => setMobile(e.target.value)}
                  maxLength={11}
                  className="w-full bg-slate-950 border border-slate-700 focus:border-amber-500 text-white rounded-xl py-2.5 px-4 pr-10 text-left font-mono text-sm focus:outline-none transition-all"
                  required
                />
                <Phone className="w-4 h-4 text-slate-400 absolute top-3 right-3" />
              </div>
            </div>

            {errorMessage && (
              <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-lg">
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold py-2.5 px-4 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 text-sm disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>در حال ارسال پیامک...</span>
                </>
              ) : (
                <>
                  <MessageSquare className="w-4 h-4" />
                  <span>ارسال کد تایید یک‌بارمصرف (OTP)</span>
                </>
              )}
            </button>

            <div className="text-[11px] text-slate-500 text-center leading-relaxed">
              با ورود به سامانه، شرایط استفاده از تحلیل‌های بنیادی و قوانین حفظ حریم خصوصی را می‌پذیرید.
            </div>
          </form>
        ) : (
          /* Step 2: OTP Verification Form */
          <form onSubmit={handleVerifyOtp} className="space-y-4">
            <div className="space-y-1.5">
              <div className="flex justify-between items-center text-xs">
                <span className="text-slate-300 font-bold">کد تایید پیامک‌شده را وارد کنید:</span>
                <button
                  type="button"
                  onClick={() => setStep('mobile')}
                  className="text-cyan-400 hover:underline flex items-center gap-1 text-[11px]"
                >
                  <ArrowRight className="w-3 h-3" />
                  <span>ویرایش شماره ({mobile})</span>
                </button>
              </div>

              <div className="relative">
                <input
                  type="text"
                  dir="ltr"
                  placeholder="کد ۶ رقمی"
                  value={otpCode}
                  onChange={(e) => setOtpCode(e.target.value)}
                  maxLength={6}
                  className="w-full bg-slate-950 border border-slate-700 focus:border-amber-500 text-white rounded-xl py-3 px-4 text-center font-mono text-lg tracking-widest focus:outline-none transition-all"
                  required
                  autoFocus
                />
                <Lock className="w-4 h-4 text-slate-400 absolute top-3.5 right-3" />
              </div>
            </div>

            {demoOtpNotice && (
              <div className="p-2.5 bg-amber-500/10 border border-amber-500/30 text-amber-300 text-xs rounded-lg font-mono text-center">
                {demoOtpNotice}
              </div>
            )}

            {errorMessage && (
              <div className="p-2.5 bg-rose-500/10 border border-rose-500/30 text-rose-300 text-xs rounded-lg">
                {errorMessage}
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-2.5 px-4 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 text-sm disabled:opacity-50"
            >
              {isLoading ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>در حال بررسی کد...</span>
                </>
              ) : (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  <span>تایید کد و ورود به سامانه</span>
                </>
              )}
            </button>

            {/* Countdown / Resend */}
            <div className="flex justify-between items-center text-xs text-slate-400 pt-2 border-t border-slate-800">
              {countdown > 0 ? (
                <span className="font-mono text-slate-300">
                  ارسال مجدد پیامک تا {countdown} ثانیه دیگر
                </span>
              ) : (
                <button
                  type="button"
                  onClick={handleSendOtp}
                  className="text-amber-400 hover:underline font-bold"
                >
                  ارسال مجدد کد پیامک
                </button>
              )}

              <span className="text-[10px] bg-slate-800 px-2 py-0.5 rounded text-slate-300 font-mono">
                کد یک‌بارمصرف
              </span>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
