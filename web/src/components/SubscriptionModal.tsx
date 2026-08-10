import React, { useState } from 'react';
import { UserProfile, SubscriptionPlan } from '../types';
import { Crown, Check, Sparkles, X, Shield, CreditCard, ArrowLeft, Zap, Gift } from 'lucide-react';

interface SubscriptionModalProps {
  isOpen: boolean;
  onClose: () => void;
  user: UserProfile | null;
  onUpgradeSuccess: (plan: SubscriptionPlan) => void;
}

const SUBSCRIPTION_PLANS: SubscriptionPlan[] = [
  {
    id: '1_month',
    title: 'اشتراک ۱ ماهه طلایی',
    durationMonths: 1,
    priceToman: 190000,
    originalPriceToman: 240000,
    discountBadge: '۲۰٪ تخفیف',
    features: [
      'تحلیل نامحدود تمام نمادهای بورس و فرابورس',
      'دسترسی کامل به شبیه‌ساز P/E و Forward EPS',
      'نمودارهای سود خالص فصلی و مقایسه صنعت',
      'ثبت تا ۱۰ هشدار پیامکی تغییرات قیمت و P/E',
      'خروجی اکسل (CSV) و PDF تحلیل جامع صورت‌ها',
    ],
  },
  {
    id: '3_months',
    title: 'اشتراک ۳ ماهه اقتصادی (پیشنهاد ویژه)',
    durationMonths: 3,
    priceToman: 450000,
    originalPriceToman: 570000,
    discountBadge: 'محبوب‌ترین (۳۰٪ تخفیف)',
    isPopular: true,
    features: [
      'تمام امکانات اشتراک ۱ ماهه',
      'تحلیل نامحدود بدون سقف برای ۳ ماه',
      'ثبت تا ۵۰ هشدار پیامکی آنی',
      'اولویت در به‌روزرسانی زنده صورت‌های کدال',
      'پشتیبانی اختصاصی تلگرام و پیامکی',
    ],
  },
  {
    id: '12_months',
    title: 'اشتراک ۱ ساله حرفه‌ای VIP',
    durationMonths: 12,
    priceToman: 1200000,
    originalPriceToman: 2280000,
    discountBadge: 'حداکثر صرفه‌جویی (۴۸٪ تخفیف)',
    features: [
      'دسترسی کامل و بدون محدودیت به مدت ۳۶۵ روز',
      'ثبت نامحدود هشدارهای قیمت و P/E روی تمام نمادها',
      'دانلود اکسل جامع مدل‌های ارزش‌گذاری مالی',
      'دسترسی پیش‌فرض به سرویس هوش مصنوعی تحلیلی',
      'مشاوره و راهنمای راه‌اندازی سرور اختصاصی',
    ],
  },
];

export const SubscriptionModal: React.FC<SubscriptionModalProps> = ({
  isOpen,
  onClose,
  user,
  onUpgradeSuccess,
}) => {
  const [selectedPlanId, setSelectedPlanId] = useState<'1_month' | '3_months' | '12_months'>('3_months');
  const [isProcessingPayment, setIsProcessingPayment] = useState(false);

  if (!isOpen) return null;

  const selectedPlan = SUBSCRIPTION_PLANS.find((p) => p.id === selectedPlanId) || SUBSCRIPTION_PLANS[1];

  const handlePayment = () => {
    setIsProcessingPayment(true);

    // Simulate Zarinpal/IDPay Iranian payment gateway redirect and activation
    setTimeout(() => {
      setIsProcessingPayment(false);
      onUpgradeSuccess(selectedPlan);
      onClose();
    }, 1200);
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
            <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center text-amber-400 shrink-0">
              <Crown className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base md:text-lg font-bold text-white flex items-center gap-2">
                <span>ارتقا به پنل اشتراک ویژه (VIP Analysis)</span>
                <span className="text-xs bg-amber-500/20 text-amber-300 px-2 py-0.5 rounded border border-amber-500/30 font-mono">
                  VIP Plan
                </span>
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                دسترسی نامحدود به تحلیگر بنیادی، شبیه‌ساز سود سال آینده، هشدارهای پیامکی و خروجی اکسل
              </p>
            </div>
          </div>

          {/* Quota Badge */}
          <div className="bg-slate-950 border border-slate-800 px-3 py-1.5 rounded-xl text-xs font-mono shrink-0">
            {user?.isVip ? (
              <span className="text-emerald-400 font-bold flex items-center gap-1">
                <Crown className="w-3.5 h-3.5" />
                <span>اشتراک ویژه فعال است</span>
              </span>
            ) : (
              <span className="text-amber-400 font-bold flex items-center gap-1">
                <Gift className="w-3.5 h-3.5" />
                <span>تحلیل‌های رایگان باقی‌مانده: {user?.remainingFreeQuota ?? 5} از ۵</span>
              </span>
            )}
          </div>
        </div>

        {/* Subscription Plans Bento Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {SUBSCRIPTION_PLANS.map((plan) => {
            const isSelected = plan.id === selectedPlanId;
            return (
              <div
                key={plan.id}
                onClick={() => setSelectedPlanId(plan.id)}
                className={`cursor-pointer rounded-2xl p-4 border transition-all flex flex-col justify-between relative ${
                  isSelected
                    ? 'bg-slate-950 border-amber-500 ring-2 ring-amber-500/30 shadow-xl'
                    : 'bg-slate-950/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                {/* Popular badge */}
                {plan.isPopular && (
                  <div className="absolute -top-3 right-4 bg-amber-500 text-slate-950 font-bold text-[10px] px-2.5 py-0.5 rounded-full shadow">
                    پیشنهاد ویژه بورس‌بازان
                  </div>
                )}

                <div>
                  <div className="flex justify-between items-start gap-2 mb-2 pt-1">
                    <h4 className="text-xs md:text-sm font-bold text-white leading-snug">{plan.title}</h4>
                    {plan.discountBadge && (
                      <span className="text-[10px] bg-rose-500/20 text-rose-300 px-1.5 py-0.5 rounded border border-rose-500/30 font-bold shrink-0">
                        {plan.discountBadge}
                      </span>
                    )}
                  </div>

                  {/* Price */}
                  <div className="my-3 font-mono">
                    {plan.originalPriceToman && (
                      <div className="text-[11px] text-slate-500 line-through">
                        {plan.originalPriceToman.toLocaleString('fa-IR')} تومان
                      </div>
                    )}
                    <div className="text-base md:text-lg font-extrabold text-amber-400">
                      {plan.priceToman.toLocaleString('fa-IR')} <span className="text-xs font-normal text-slate-300">تومان</span>
                    </div>
                  </div>

                  {/* Features Bullet List */}
                  <ul className="space-y-1.5 text-[11px] text-slate-300/90 pt-3 border-t border-slate-900">
                    {plan.features.map((ft, i) => (
                      <li key={i} className="flex items-start gap-1.5">
                        <Check className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                        <span>{ft}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Select Radio Pill */}
                <div className="mt-4 pt-3 border-t border-slate-900 flex justify-between items-center text-xs">
                  <span className={isSelected ? 'text-amber-400 font-bold' : 'text-slate-400'}>
                    {isSelected ? 'انتخاب شده' : 'انتخاب طرح'}
                  </span>
                  <div
                    className={`w-4 h-4 rounded-full border flex items-center justify-center ${
                      isSelected ? 'border-amber-400 bg-amber-400/20' : 'border-slate-600'
                    }`}
                  >
                    {isSelected && <div className="w-2 h-2 rounded-full bg-amber-400" />}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Payment Gateway Box */}
        <div className="bg-slate-950 border border-slate-800 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="space-y-1 text-xs">
            <div className="font-bold text-white flex items-center gap-2">
              <CreditCard className="w-4 h-4 text-emerald-400" />
              <span>پرداخت آنلاین امن از طریق درگاه‌های شتاب (زرین‌پال / آی‌دی‌پی)</span>
            </div>
            <p className="text-[11px] text-slate-400">
              مبلغ فاکتور: <strong className="text-amber-400 font-mono">{selectedPlan.priceToman.toLocaleString('fa-IR')} تومان</strong> برای {selectedPlan.durationMonths} ماه اشتراک
            </p>
          </div>

          <button
            type="button"
            onClick={handlePayment}
            disabled={isProcessingPayment}
            className="w-full sm:w-auto bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold py-2.5 px-6 rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 text-sm shrink-0"
          >
            {isProcessingPayment ? (
              <>
                <Zap className="w-4 h-4 animate-bounce text-slate-950" />
                <span>در حال اتصال به درگاه بانکی...</span>
              </>
            ) : (
              <>
                <span>پرداخت و فعال‌سازی آنی اشتراک</span>
                <ArrowLeft className="w-4 h-4" />
              </>
            )}
          </button>
        </div>

        {/* Guarantee Footer */}
        <div className="flex items-center justify-between text-[11px] text-slate-500 pt-2 border-t border-slate-800">
          <div className="flex items-center gap-1.5">
            <Shield className="w-3.5 h-3.5 text-cyan-400" />
            <span>ضماد بازگشت وجه ۱۰۰٪ در صورت نارضایتی تا ۴۸ ساعت اول</span>
          </div>
          <span className="font-mono">فعال‌سازی آنی پس از پرداخت</span>
        </div>
      </div>
    </div>
  );
};
