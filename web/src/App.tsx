import React, { useState, useEffect } from 'react';
import { StockHealthCardData, UserProfile, SubscriptionPlan } from './types';
import { enrichStockDataWithNewFeatures } from './utils/stockHelpers';
import { Header } from './components/Header';
import { QuestionCardsRow } from './components/QuestionCardsRow';
import { VisualRow } from './components/VisualRow';
import { StatusBanner } from './components/StatusBanner';
import { GoldenSummaryBanner } from './components/GoldenSummaryBanner';
import { ExplanationCardsGrid } from './components/ExplanationCardsGrid';
import { ConclusionAndSources } from './components/ConclusionAndSources';
import { StockSearchControls } from './components/StockSearchControls';
import { CustomDataModal } from './components/CustomDataModal';
import { PeerIndustryWidget } from './components/PeerIndustryWidget';
import { PeSimulationCard } from './components/PeSimulationCard';
import { SmartValuationCard } from './components/SmartValuationCard';
import { CodalRefreshControl } from './components/CodalRefreshControl';
import { KeyEventsCard } from './components/KeyEventsCard';
import { QuarterlyProfitChart } from './components/QuarterlyProfitChart';
import { AuthModal } from './components/AuthModal';
import { SubscriptionModal } from './components/SubscriptionModal';
import { StockAlertsModal } from './components/StockAlertsModal';
import { ExportReportModal } from './components/ExportReportModal';
import { AdminDashboardModal } from './components/AdminDashboardModal';
import { IranianServerGuideModal } from './components/IranianServerGuideModal';
import { AlertCircle, Loader2, Sparkles, Crown } from 'lucide-react';

export default function App() {
  const [currentData, setCurrentData] = useState<StockHealthCardData | null>(null);
  const [activeSymbol, setActiveSymbol] = useState<string>('فولاد');
  const [reportMode, setReportMode] = useState<'latest_codal' | 'audited'>('audited');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Modals state
  const [isCustomModalOpen, setIsCustomModalOpen] = useState<boolean>(false);
  const [isAuthOpen, setIsAuthOpen] = useState<boolean>(false);
  const [isSubOpen, setIsSubOpen] = useState<boolean>(false);
  const [isAlertsOpen, setIsAlertsOpen] = useState<boolean>(false);
  const [isExportOpen, setIsExportOpen] = useState<boolean>(false);
  const [isAdminOpen, setIsAdminOpen] = useState<boolean>(false);
  const [isGuideOpen, setIsGuideOpen] = useState<boolean>(false);

  // User Profile State
  const [user, setUser] = useState<UserProfile>(() => {
    const saved = localStorage.getItem('bourse_user_profile');
    if (saved) {
      try {
        return JSON.parse(saved);
      } catch (e) {
        console.error(e);
      }
    }
    return {
      mobile: '',
      isLoggedIn: false,
      isVip: false,
      remainingFreeQuota: 5, // 5 free initial analyses
      usedQuota: 0,
      subscriptionPlan: 'free',
    };
  });

  // Save user profile state
  useEffect(() => {
    localStorage.setItem('bourse_user_profile', JSON.stringify(user));
  }, [user]);

  // Initial mount live fetch for default ticker
  useEffect(() => {
    handleAnalyzeQuery('فولاد', reportMode, true);
  }, []);

  const activeHealthCard = currentData ? enrichStockDataWithNewFeatures(currentData) : null;

  // Check and deduct free quota
  const checkAndDeductQuota = (): boolean => {
    if (user.isVip) return true; // VIP users have unlimited queries

    if (user.remainingFreeQuota > 0) {
      setUser((prev) => ({
        ...prev,
        remainingFreeQuota: prev.remainingFreeQuota - 1,
        usedQuota: prev.usedQuota + 1,
      }));
      return true;
    } else {
      // Out of quota -> prompt subscription modal
      setIsSubOpen(true);
      return false;
    }
  };

  // Handle Preset Ticker Selection
  const handleSelectPreset = (symbol: string) => {
    if (!checkAndDeductQuota()) return;

    setActiveSymbol(symbol);
    setErrorMessage(null);
    handleAnalyzeQuery(symbol, reportMode, true);
  };

  // Handle AI Live Stock Analysis Request
  const handleAnalyzeQuery = async (
    query: string,
    modeOverride?: 'latest_codal' | 'audited',
    skipQuotaCheck: boolean = false
  ) => {
    if (!skipQuotaCheck && !checkAndDeductQuota()) return;

    setIsLoading(true);
    setErrorMessage(null);

    const targetMode = modeOverride || reportMode;
    const trimmed = query.trim();

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: trimmed, reportMode: targetMode }),
      });

      const result = await response.json();

      if (result.success && result.data) {
        setCurrentData(result.data);
        setActiveSymbol(result.data.header?.symbol || trimmed);
      } else {
        throw new Error(result.error || 'خطا در تحلیل بنیادی سهم.');
      }
    } catch (err: any) {
      console.warn('Analysis error:', err);
      setErrorMessage(err.message || 'ارتباط با سرویس داده برقرار نشد. چند دقیقه دیگر دوباره تلاش کنید.');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Upgrade VIP Success
  const handleUpgradeSuccess = (plan: SubscriptionPlan) => {
    setUser((prev) => ({
      ...prev,
      isVip: true,
      subscriptionPlan: plan.id,
      subscriptionExpiresAt: '۱۴۰۵/۰۶/۳۰',
    }));
  };

  // Handle Manual Refresh
  const handleRefreshStockData = () => {
    handleAnalyzeQuery(activeSymbol, reportMode, true);
  };

  // Handle Custom Input Form Submit
  const handleCustomSubmit = async (customData: any) => {
    setIsLoading(true);
    setErrorMessage(null);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: customData.symbol,
          customData,
        }),
      });

      const result = await response.json();

      if (result.success && result.data) {
        setCurrentData(result.data);
        setActiveSymbol(result.data.header?.symbol || customData.symbol);
      } else {
        // Fallback custom card generation
        throw new Error('تحلیل آنلاین در دسترس نیست. محاسبه دستی انجام شد.');
      }
    } catch (err: any) {
      console.warn('Custom analysis unavailable:', err);
      setErrorMessage('تحلیل سفارشی فقط پس از دریافت و اعتبارسنجی دادهٔ واقعی نمایش داده می‌شود.');
      setCurrentData(null);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-['Vazirmatn',sans-serif] selection:bg-teal-500 selection:text-white">
      {/* Container scaled to 1920px width format */}
      <main className="w-full max-w-[1920px] mx-auto p-4 md:p-6 lg:p-8 space-y-6">
        
        {/* Top Search Controls Bar (Non-printable) */}
        <StockSearchControls
          onSelectStock={handleSelectPreset}
          onAnalyzeQuery={(q) => handleAnalyzeQuery(q, reportMode)}
          onOpenCustomModal={() => setIsCustomModalOpen(true)}
          activeSymbol={activeSymbol}
          isLoading={isLoading}
        />

        {/* Codal Data Live Refresh Control */}
        <CodalRefreshControl
          reportMode={reportMode}
          onChangeReportMode={(newMode) => {
            setReportMode(newMode);
            handleAnalyzeQuery(activeSymbol, newMode, true);
          }}
          onRefreshData={handleRefreshStockData}
          isLoading={isLoading}
          currentSymbol={activeHealthCard?.header?.symbol || activeSymbol}
          auditStatusStr={activeHealthCard?.header?.codalAuditStatus}
          lastUpdateStr={activeHealthCard?.header?.dataStamp?.updatedAt}
        />

        {/* Error Notification Banner */}
        {errorMessage && (
          <div className="bg-rose-950/80 border border-rose-500/40 rounded-xl p-4 text-rose-200 text-xs flex items-center gap-3">
            <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Loading Overlay */}
        {isLoading ? (
          <div className="w-full bg-slate-900/90 border border-slate-800 rounded-2xl p-16 flex flex-col items-center justify-center text-center space-y-4 shadow-2xl">
            <Loader2 className="w-12 h-12 text-teal-400 animate-spin" />
            <div className="space-y-1">
              <h3 className="text-lg font-bold text-white flex items-center gap-2 justify-center">
                <Sparkles className="w-5 h-5 text-teal-400" />
                در حال دریافت و تحلیل داده‌های رسمی...
              </h3>
              <p className="text-xs text-slate-400">
                دریافت قیمت بازار، صورت مالی کدال و محاسبه نسبت‌های بنیادی
              </p>
            </div>
          </div>
        ) : activeHealthCard ? (
          <div id="fundamental-health-report" className="space-y-6">
            
            {/* 1) Broad Header (هدر عریض) */}
            <Header
              info={activeHealthCard.header}
              user={user}
              onOpenAuth={() => setIsAuthOpen(true)}
              onOpenSubscription={() => setIsSubOpen(true)}
              onOpenAlerts={() => setIsAlertsOpen(true)}
              onOpenExport={() => setIsExportOpen(true)}
              onOpenAdmin={() => setIsAdminOpen(true)}
              onOpenServerGuide={() => setIsGuideOpen(true)}
            />

            {/* 2) Three Question Cards in a Row (سه کارت سؤال در یک ردیف) */}
            <QuestionCardsRow questions={activeHealthCard.questions} />

            {/* 3) Three-piece Visual Row (ردیف تصویری سه‌تکه) */}
            <VisualRow visuals={activeHealthCard.visuals} />

            {/* 4) Six-part Status Banner (نوار شش‌تایی وضعیت) */}
            <StatusBanner metrics={activeHealthCard.statusBanner} />

            {/* 5) Golden Summary Banner with Star Icon (بند طلایی جمع‌بندی با آیکون ستاره) */}
            <GoldenSummaryBanner summary={activeHealthCard.goldenSummary} />

            {/* 6) Smart Valuation & Buy/Sell Range Card (پیشنهاد هوشمندانه محدوده خرید و فروش) */}
            <SmartValuationCard
              smartRecommendation={activeHealthCard.smartRecommendation}
              symbol={activeHealthCard.header?.symbol}
              codalAuditStatus={activeHealthCard.header?.codalAuditStatus}
            />

            {/* 7) Codal Key Events Card (رویدادهای کلیدی اخیر شامل مجمع عمومی، افزایش سرمایه و تغییرات هیئت مدیره) */}
            <KeyEventsCard
              keyEvents={activeHealthCard.keyEvents}
              symbol={activeHealthCard.header?.symbol}
            />

            {/* 8) Quarterly Net Profit Chart (نمودار میله‌ای سود خالص فصلی مقایسه با صنعت) */}
            <QuarterlyProfitChart
              quarterlyProfits={activeHealthCard.quarterlyProfits}
              symbol={activeHealthCard.header?.symbol}
              industryTitle={activeHealthCard.header?.industryTitle}
            />

            {/* 9) Six Explanation Cards Grid (شش کارت توضیحی در Grid سه ستونه) */}
            <ExplanationCardsGrid cards={activeHealthCard.explanationCards} />

            {/* 9) Future P/E Simulation Card (شبیه‌سازی P/E آینده‌نگر) */}
            <PeSimulationCard
              peSimulation={activeHealthCard.peSimulation}
              currentPrice={activeHealthCard.header?.currentPrice}
              currentPeStr={activeHealthCard.header?.peRatio}
              symbol={activeHealthCard.header?.symbol}
            />

            {/* 10) Two Concluding Cards & Data Sources Section (دو کارت پایانی و بخش منابع) */}
            <ConclusionAndSources conclusion={activeHealthCard.conclusion} />

          </div>
        ) : (
          <section className="rounded-2xl border border-slate-800 bg-slate-900/70 px-6 py-16 text-center shadow-2xl">
            <div className="mx-auto max-w-xl space-y-3">
              <h1 className="text-2xl font-black text-white md:text-3xl">تحلیل بنیادی شفاف برای بورس تهران</h1>
              <p className="text-sm leading-7 text-slate-400">
                نماد موردنظر را جستجو کنید تا آخرین قیمت بازار و صورت مالی رسمی کدال دریافت و نسبت‌های بنیادی محاسبه شود.
              </p>
              <p className="text-xs text-slate-500">در صورت نبود داده معتبر، نتیجه‌ای نمایش داده نخواهد شد.</p>
            </div>
          </section>
        )}

        {/* Top 3 Peer Industry Corner Widget */}
        <PeerIndustryWidget
          peers={activeHealthCard?.peers || []}
          currentSymbol={activeHealthCard?.header?.symbol || activeSymbol}
          industryTitle={activeHealthCard?.header?.industryTitle || 'همصنعت'}
          onSelectPeer={handleSelectPreset}
        />

        {/* Custom Data Input Modal */}
        <CustomDataModal
          isOpen={isCustomModalOpen}
          onClose={() => setIsCustomModalOpen(false)}
          onSubmit={handleCustomSubmit}
          initialSymbol={activeSymbol}
        />

        {/* Auth Modal (ورود با SMS OTP) */}
        <AuthModal
          isOpen={isAuthOpen}
          onClose={() => setIsAuthOpen(false)}
          onLoginSuccess={(loggedUser) => setUser(loggedUser)}
        />

        {/* Subscription Modal (خرید اشتراک ۵ تحلیل رایگان) */}
        <SubscriptionModal
          isOpen={isSubOpen}
          onClose={() => setIsSubOpen(false)}
          user={user}
          onUpgradeSuccess={handleUpgradeSuccess}
        />

        {/* Stock Alerts Modal (هشدارهای پیامکی) */}
        <StockAlertsModal
          isOpen={isAlertsOpen}
          onClose={() => setIsAlertsOpen(false)}
          activeSymbol={activeSymbol}
          user={user}
          onOpenAuth={() => {
            setIsAlertsOpen(false);
            setIsAuthOpen(true);
          }}
          onOpenSubscription={() => {
            setIsAlertsOpen(false);
            setIsSubOpen(true);
          }}
        />

        {/* Export Report Modal (دانلود اکسل/PDF) */}
        {activeHealthCard && <ExportReportModal
          isOpen={isExportOpen}
          onClose={() => setIsExportOpen(false)}
          data={activeHealthCard}
        />}

        {/* Admin Dashboard Modal (پنل مدیریت) */}
        <AdminDashboardModal
          isOpen={isAdminOpen}
          onClose={() => setIsAdminOpen(false)}
          onOpenServerGuide={() => {
            setIsAdminOpen(false);
            setIsGuideOpen(true);
          }}
        />

        {/* Iranian Server Deployment Guide Modal (راهنمای سرور ایران) */}
        <IranianServerGuideModal
          isOpen={isGuideOpen}
          onClose={() => setIsGuideOpen(false)}
        />
      </main>
    </div>
  );
}

// Fallback Helper for Custom Data Input
function constructFallbackCustomCard(custom: any): StockHealthCardData {
  const pe = custom.eps > 0 ? (custom.currentPrice / custom.eps).toFixed(1) : 'معنادار نیست';
  const realGrowth = custom.salesGrowth - custom.inflationRate;
  const isGoodPE = custom.eps > 0 && Number(pe) < 8;
  const isGoodGrowth = realGrowth > 0;
  const isGoodCash = custom.cashFlowQuality >= 80;

  return {
    header: {
      symbol: custom.symbol,
      fullName: custom.fullName,
      industry: custom.industry || 'manufacturing',
      industryTitle: 'سفارشی / کاربر',
      financialReportTitle: 'صورت مالی سفارشی - ورودی دستی',
      currentPrice: custom.currentPrice,
      peRatio: String(pe),
      marketCap: 'نامشخص (ورودی دستی)',
      reportDate: '۱۴۰۵/۰۵/۰۶',
      codalAuditStatus: 'ورودی کاربر',
      dataStamp: {
        source: 'محاسبه دستی کاربر',
        updatedAt: '۱۴۰۵/۰۵/۰۶',
        verificationCode: 'USER-CUSTOM-01',
      },
    },
    questions: [
      {
        id: 1,
        title: '۱) آیا از سود بانکی بهتر است؟',
        subtitle: 'مقایسه بازده سود با نرخ سپرده ۲۳.۵٪',
        status: isGoodPE ? 'good' : 'mid',
        statusLabel: isGoodPE ? 'خوب' : 'متوسط',
        mainMetricValue: `P/E: ${pe} | بازده سود: ${custom.eps > 0 ? ((custom.eps / custom.currentPrice) * 100).toFixed(1) : 0}٪`,
        comparisonDetail: 'نرخ سود بانکی: ۲۳.۵٪',
        summaryAnswer: isGoodPE
          ? 'بله، نسبت P/E مناسب بوده و بازده متوقع بهتری ایجاد می‌کند.'
          : 'متوسط، بازده مستقیماً فاصله زیادی با سود بانکی ندارد.',
      },
      {
        id: 2,
        title: '۲) آیا سود واقعی و نقد است؟',
        subtitle: 'کیفیت نقدینگی سود جریان عملیاتی',
        status: isGoodCash ? 'good' : 'mid',
        statusLabel: isGoodCash ? 'خوب' : 'متوسط',
        mainMetricValue: `نسبت جریان نقد به سود: ${custom.cashFlowQuality}٪`,
        comparisonDetail: 'آستانه مطلوب: بالای ۸۰٪',
        summaryAnswer: isGoodCash
          ? 'بله، بخش اعظم سود ناشی از نقدینگی واقعی است.'
          : 'متوسط، بخشی از سود در مطالبات باقی مانده است.',
      },
      {
        id: 3,
        title: '۳) آیا رشد واقعی بالاتر از تورم دارد؟',
        subtitle: 'رشد اسمی منهای تورم',
        status: isGoodGrowth ? 'good' : 'mid',
        statusLabel: isGoodGrowth ? 'خوب' : 'متوسط',
        mainMetricValue: `رشد واقعی: ${realGrowth > 0 ? '+' : ''}${realGrowth}٪`,
        comparisonDetail: `رشد اسمی: ${custom.salesGrowth}٪ | تورم: ${custom.inflationRate}٪`,
        summaryAnswer: isGoodGrowth
          ? 'بله، شرکت توانسته ارزش دارایی‌ها را در برابر تورم حفظ کرده و رشد واقعی کند.'
          : 'خیر، رشد اسمی کمتر از نرخ تورم رسمی بوده است.',
      },
    ],
    visuals: {
      trendChart: {
        title: 'روند سود خالص ۴ دوره اخیر',
        subtitle: 'برآورد دوره بر برسی دستی',
        unit: 'ریال/تومان',
        points: [
          { period: '۱۴۰۱', value: custom.eps * 0.6, displayValue: `${Math.round(custom.eps * 0.6)}` },
          { period: '۱۴۰۲', value: custom.eps * 0.8, displayValue: `${Math.round(custom.eps * 0.8)}` },
          { period: '۱۴۰۳', value: custom.eps * 0.9, displayValue: `${Math.round(custom.eps * 0.9)}` },
          { period: '۱۴۰۴', value: custom.eps, displayValue: `${custom.eps}` },
        ],
      },
      donutChart: {
        title: 'ترکیب محصولات / منابع',
        subtitle: 'سهم درآمد عملیاتی',
        centerLabel: 'کل درآمد',
        centerValue: '۱۰۰٪',
        segments: [
          { label: 'محصول اصلی A', percentage: 60, valueString: '۶۰٪', color: '#00c4b4' },
          { label: 'محصول فرعی B', percentage: 25, valueString: '۲۵٪', color: '#3b82f6' },
          { label: 'سایر درآمدها', percentage: 15, valueString: '۱۵٪', color: '#f59e0b' },
        ],
      },
      ratioBars: {
        title: 'میله‌های حاشیه و نسبت‌های کلیدی',
        subtitle: 'معیارهای سفارشی',
        bars: [
          { label: 'حاشیه سود ناخالص', valuePercentage: custom.grossMargin, displayValue: `${custom.grossMargin}٪`, status: custom.grossMargin > 30 ? 'good' : 'mid' },
          { label: 'کیفیت نقدینگی سود', valuePercentage: custom.cashFlowQuality, displayValue: `${custom.cashFlowQuality}٪`, status: custom.cashFlowQuality > 80 ? 'good' : 'mid' },
          { label: 'رشد اسمی درآمد', valuePercentage: Math.min(custom.salesGrowth, 100), displayValue: `${custom.salesGrowth}٪`, status: 'good' },
        ],
      },
    },
    statusBanner: [
      { id: 1, key: 'pe', label: 'نسبت P/E', value: String(pe), status: isGoodPE ? 'good' : 'mid', description: 'قیمت به سود' },
      { id: 2, key: 'growth', label: 'رشد واقعی', value: `${realGrowth}٪`, status: isGoodGrowth ? 'good' : 'mid', description: 'منهای تورم' },
      { id: 3, key: 'cash', label: 'کیفیت نقد', value: `${custom.cashFlowQuality}٪`, status: isGoodCash ? 'good' : 'mid', description: 'وصول نقدی' },
      { id: 4, key: 'margin', label: 'حاشیه ناخالص', value: `${custom.grossMargin}٪`, status: custom.grossMargin > 30 ? 'good' : 'mid', description: 'سودآوری' },
      { id: 5, key: 'price', label: 'قیمت روز', value: `${custom.currentPrice}`, status: 'good', description: 'ریال' },
      { id: 6, key: 'eps', label: 'سود EPS', value: `${custom.eps}`, status: 'good', description: 'ریال' },
    ],
    goldenSummary: {
      badgeTitle: isGoodPE && isGoodGrowth ? 'بنیاد قوی و باثبات' : 'بنیاد متوسط / تحت فشار',
      badgeStatus: isGoodPE && isGoodGrowth ? 'good' : 'mid',
      summaryText: `تحلیل ورودی سفارشی برای نماد «${custom.symbol}»: شرکت دارای حاشیه سود ${custom.grossMargin}٪ و رشد واقعی ${realGrowth}٪ در برابر تورم است.`,
      valuationVsQualityNote: 'این کارنامه بر اساس داده‌های سفارشی دستی شما محاسبه شده است.',
      investmentOutlook: 'چشم‌انداز بستگی به ثبات متغیرهای ورودی دارد.',
    },
    explanationCards: [
      { id: 1, numberLabel: '۰۱', title: 'حاشیه سود ناخالص', status: 'good', valueText: `${custom.grossMargin}٪`, simpleDefinition13Yo: 'میزان سود باقی‌مانده بعد از هزینه ساخت جنس.', companyContextNote: 'ورودی سفارشی کاربر.' },
      { id: 2, numberLabel: '۰۲', title: 'نسبت P/E', status: isGoodPE ? 'good' : 'mid', valueText: String(pe), simpleDefinition13Yo: 'چند سال طول می‌کشد سود شرکت اصل پولت را بدهد.', companyContextNote: 'محاسبه شده از قیمت و EPS.' },
      { id: 3, numberLabel: '۰۳', title: 'کیفیت نقد سود', status: isGoodCash ? 'good' : 'mid', valueText: `${custom.cashFlowQuality}٪`, simpleDefinition13Yo: 'آیا پول‌ها واقعی و نقد است.', companyContextNote: 'ورودی کاربر.' },
      { id: 4, numberLabel: '۰۴', title: 'رشد واقعی', status: isGoodGrowth ? 'good' : 'mid', valueText: `${realGrowth}٪`, simpleDefinition13Yo: 'رشد شرکت بعد از کم کردن گرانی تورم.', companyContextNote: 'منهای تورم ۴۲٪.' },
      { id: 5, numberLabel: '۰۵', title: 'قیمت روز', status: 'good', valueText: `${custom.currentPrice} ریال`, simpleDefinition13Yo: 'قیمت فعلی خرید یک سهم در بازار.', companyContextNote: 'ورودی کاربر.' },
      { id: 6, numberLabel: '۰۶', title: 'سود هر سهم EPS', status: 'good', valueText: `${custom.eps} ریال`, simpleDefinition13Yo: 'سودی که شرکت به ازای هر ۱ سهم ساخته است.', companyContextNote: 'ورودی کاربر.' },
    ],
    conclusion: {
      valuationCard: { title: 'ارزش‌گذاری سفارشی', body: 'این نتیجه حاصل فرمول‌های ورودی دستی شماست.' },
      outlookCard: { title: 'چشم‌انداز', body: 'توصیه می‌شود قبل از معامله صورت‌های مالی کدال بررسی شوند.' },
      dataSourceStamp: { title: 'منبع داده', codalLinkText: 'ورودی سفارشی کاربر', lastUpdate: '۱۴۰۵/۰۵/۰۶', disclaimer: 'صرفاً محاسبه سفارشی است.' },
    },
  };
}
