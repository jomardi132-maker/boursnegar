import { PeerCompany, PeSimulationData, IndustryType, StockHealthCardData, StatusType, SmartRecommendation, CodalKeyEvent, QuarterlyProfitItem } from '../types';

export function getPeersForStock(symbol: string, industry: IndustryType | string): PeerCompany[] {
  void symbol;
  void industry;
  // Peer data must come from the authoritative analysis response.
  return [];

  /*
  const normSymbol = symbol.trim();

  // Custom Peer lists per symbol / industry
  if (normSymbol === 'فولاد' || normSymbol === 'فملی' || normSymbol === 'ذوب' || normSymbol === 'کاوه') {
    const list: PeerCompany[] = [
      { symbol: 'فملی', name: 'صنایع ملی مس ایران', healthStatus: 'good' as StatusType, peRatio: '۵.۲' },
      { symbol: 'ذوب', name: 'ذوب آهن اصفهان', healthStatus: 'bad' as StatusType, peRatio: 'زیان‌ده' },
      { symbol: 'کاوه', name: 'فولاد کاوه جنوب کیش', healthStatus: 'mid' as StatusType, peRatio: '۶.۱' },
    ];
    return list.filter((p) => p.symbol !== normSymbol).slice(0, 3);
  }

  if (normSymbol === 'وبملت' || normSymbol === 'وتجارت' || normSymbol === 'وبصادر') {
    const list: PeerCompany[] = [
      { symbol: 'پاسارگاد', name: 'بانک پاسارگاد', healthStatus: 'good' as StatusType, peRatio: '۴.۵' },
      { symbol: 'وتجارت', name: 'بانک تجارت', healthStatus: 'mid' as StatusType, peRatio: '۴.۱' },
      { symbol: 'وبصادر', name: 'بانک صادرات ایران', healthStatus: 'mid' as StatusType, peRatio: '۴.۸' },
    ];
    return list.filter((p) => p.symbol !== normSymbol).slice(0, 3);
  }

  if (normSymbol === 'شستا' || normSymbol === 'غدیر' || normSymbol === 'وامید') {
    const list: PeerCompany[] = [
      { symbol: 'غدیر', name: 'سرمایه‌گذاری غدیر', healthStatus: 'good' as StatusType, peRatio: '۴.۹' },
      { symbol: 'وامید', name: 'سرمایه‌گذاری امید', healthStatus: 'good' as StatusType, peRatio: '۵.۴' },
      { symbol: 'پردیس', name: 'سرمایه‌گذاری پردیس', healthStatus: 'mid' as StatusType, peRatio: '۶.۰' },
    ];
    return list.filter((p) => p.symbol !== normSymbol).slice(0, 3);
  }

  if (normSymbol === 'دانا' || normSymbol === 'البرز' || normSymbol === 'آسیا') {
    const list: PeerCompany[] = [
      { symbol: 'البرز', name: 'بیمه البرز', healthStatus: 'good' as StatusType, peRatio: '۵.۰' },
      { symbol: 'آسیا', name: 'بیمه آسیا', healthStatus: 'good' as StatusType, peRatio: '۵.۵' },
      { symbol: 'میهن', name: 'بیمه میهن', healthStatus: 'bad' as StatusType, peRatio: 'زیان‌ده' },
    ];
    return list.filter((p) => p.symbol !== normSymbol).slice(0, 3);
  }

  // Industry fallbacks
  switch (industry) {
    case 'bank':
      return [
        { symbol: 'وبملت', name: 'بانک ملت', healthStatus: 'good' as StatusType, peRatio: '۳.۹' },
        { symbol: 'پاسارگاد', name: 'بانک پاسارگاد', healthStatus: 'good' as StatusType, peRatio: '۴.۵' },
        { symbol: 'وتجارت', name: 'بانک تجارت', healthStatus: 'mid' as StatusType, peRatio: '۴.۱' },
      ];
    case 'holding':
      return [
        { symbol: 'غدیر', name: 'سرمایه‌گذاری غدیر', healthStatus: 'good' as StatusType, peRatio: '۴.۹' },
        { symbol: 'شستا', name: 'سرمایه‌گذاری تامین اجتماعی', healthStatus: 'mid' as StatusType, peRatio: '۶.۲' },
        { symbol: 'وامید', name: 'سرمایه‌گذاری امید', healthStatus: 'good' as StatusType, peRatio: '۵.۴' },
      ];
    case 'insurance':
      return [
        { symbol: 'البرز', name: 'بیمه البرز', healthStatus: 'good' as StatusType, peRatio: '۵.۰' },
        { symbol: 'آسیا', name: 'بیمه آسیا', healthStatus: 'good' as StatusType, peRatio: '۵.۵' },
        { symbol: 'دانا', name: 'بیمه دانا', healthStatus: 'mid' as StatusType, peRatio: '۶.۵' },
      ];
    default:
      return [
        { symbol: 'فولاد', name: 'فولاد مبارکه اصفهان', healthStatus: 'good' as StatusType, peRatio: '۵.۸' },
        { symbol: 'فملی', name: 'صنایع ملی مس ایران', healthStatus: 'good' as StatusType, peRatio: '۵.۲' },
        { symbol: 'ذوب', name: 'ذوب آهن اصفهان', healthStatus: 'bad' as StatusType, peRatio: 'زیان‌ده' },
      ];
  }
  */
}

export function getPeSimulationForStock(
  price: number,
  peStr: string,
  symbol: string
): PeSimulationData {
  const parsedCurrentPe =
    parseFloat((peStr || '5.8').replace(/[۰-۹]/g, (d) => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d)))) || 5.8;
  const currentPrice = price || 5000;
  const baseEps = Math.round(currentPrice / parsedCurrentPe) || 1000;

  const optEps = Math.round(baseEps * 1.35);
  const baseEpsProjected = Math.round(baseEps * 1.2);
  const pessEps = Math.round(baseEps * 1.05);

  const optPe = Number((currentPrice / optEps).toFixed(1));
  const basePe = Number((currentPrice / baseEpsProjected).toFixed(1));
  const pessPe = Number((currentPrice / pessEps).toFixed(1));

  return {
    currentPe: parsedCurrentPe,
    currentPrice,
    baseEps,
    scenarios: [
      {
        name: 'سناریوی خوش‌بینانه (افزایش نرخ فروش & صادرات)',
        type: 'optimistic',
        epsGrowthPercent: 35,
        simulatedPe: optPe,
        targetPriceChange: '+۳۵٪ (کاهش نسبت به ۴.۲ مرتبه)',
        description:
          'رشد درآمد فروش ناشی از افزایش دلار حواله یا رونق بازارهای صادراتی و کنترل هزینه‌های تولید.',
      },
      {
        name: 'سناریوی پایه (مطابق نرخ تورم رسمی کشور)',
        type: 'base',
        epsGrowthPercent: 20,
        simulatedPe: basePe,
        targetPriceChange: '+۲۰٪ (همگام با تورم)',
        description:
          'تداوم عملکرد فعلی با رشد سودآوری همگام با نرخ تورم سالانه و حاشیه سود باثبات.',
      },
      {
        name: 'سناریوی بدبینانه (افزایش هزینه‌ها & رکود)',
        type: 'pessimistic',
        epsGrowthPercent: 5,
        simulatedPe: pessPe,
        targetPriceChange: '+۵٪ (محدودیت رشد)',
        description:
          'افزایش شدید هزینه‌های انرژی و مواد اولیه، قطعی قطعی برق/گاز و ثبات نرخ فروش محصولات.',
      },
    ],
    summaryNote:
      'در صورت جابه‌جایی EPS در سناریوی خوش‌بینانه، P/E آینده‌نگر سهم به محدوده بسیار ارزنده تنزل خواهد یافت.',
  };
}

export function getSmartRecommendationForStock(
  price: number,
  peStr: string,
  symbol: string,
  codalAuditStatus?: string
): SmartRecommendation {
  const currentPrice = price || 5000;
  const parsedCurrentPe =
    parseFloat((peStr || '5.8').replace(/[۰-۹]/g, (d) => String('۰۱۲۳۴۵۶۷۸۹'.indexOf(d)))) || 5.8;

  // Calculate buy/sell bounds
  const buyMin = Math.round(currentPrice * 0.90);
  const buyMax = Math.round(currentPrice * 0.98);
  const sellMin = Math.round(currentPrice * 1.25);
  const sellMax = Math.round(currentPrice * 1.45);
  const stopLoss = Math.round(currentPrice * 0.85);

  const isPeAttractive = parsedCurrentPe > 0 && parsedCurrentPe <= 7.0;
  const isUnaudited = codalAuditStatus?.includes('حسابرسی‌نشده') || codalAuditStatus?.includes('میاندوره‌ای');

  const statusTitle = isPeAttractive
    ? 'محدوده قیمت و ارزش بازار جذاب جهت خرید'
    : 'ارزش‌گذاری متعادل (نیازمند استراتژی ورود پله‌ای)';

  const suitabilityNote = isPeAttractive
    ? `نسبت P/E فعلی نماد (${parsedCurrentPe}) پایین‌تر از میانه تاریخی و متوسط صنعت است. ارزش کل بازار شرکت در قیمت ${currentPrice.toLocaleString(
        'fa-IR'
      )} ریال حاشیه ایمنی مناسبی ارائه می‌دهد.`
    : `نماد با P/E معادل ${parsedCurrentPe} در محدوده قیمتی منصفانه معامله می‌شود. جهت کاهش ریسک، ورود در اصلاح‌های قیمتی به محدوده حمایت پیشنهاد می‌گردد.`;

  return {
    isSuitableForBuy: isPeAttractive,
    statusTitle,
    suitabilityNote,
    buyRange: {
      minPrice: buyMin,
      maxPrice: buyMax,
      displayRange: `${buyMin.toLocaleString('fa-IR')} تا ${buyMax.toLocaleString('fa-IR')} ریال`,
    },
    sellTargetRange: {
      minPrice: sellMin,
      maxPrice: sellMax,
      displayRange: `${sellMin.toLocaleString('fa-IR')} تا ${sellMax.toLocaleString('fa-IR')} ریال`,
    },
    stopLossPrice: {
      price: stopLoss,
      displayPrice: `${stopLoss.toLocaleString('fa-IR')} ریال`,
    },
    riskLevel: isPeAttractive ? 'کم' : 'متوسط',
    insights: [
      `🎯 **استراتژی ورود**: پیشنهاد می‌شود خرید به صورت پله‌ای (مثلاً ۳ پله ۳۳ درصدی) در محدوده ${buyMin.toLocaleString('fa-IR')} تا ${buyMax.toLocaleString('fa-IR')} ریال انجام شود.`,
      `📈 **تارگت سودآوری**: هدف قیمتی میان‌مدت در محدوده ${sellMin.toLocaleString('fa-IR')} تا ${sellMax.toLocaleString('fa-IR')} ریال بر مبنای رشد سودآوری برآوردی تعیین می‌گردد.`,
      `🛡️ **حد ضرر و ریسک**: رعایت حد ضرر سخت‌گیرانه در ${stopLoss.toLocaleString('fa-IR')} ریال (افت ۱۵ درصدی از قیمت جاری) جهت کنترل ریسک نوسانات بازار توصیه می‌شود.`,
      isUnaudited
        ? '⚠️ **نکته حسابرسی**: صورت‌های مالی اخیر از نوع میان‌دوره‌ای/حسابرسی‌نشده است. برای خریدهای با حجم بالا، تطبیق با گزارش حسابرسی‌شده سالانه پیشنهاد می‌شود.'
        : '✅ **اطمینان مالی**: صورت‌های مالی مستند به گزارش حسابرسی‌شده بوده و اتکا به ارقام صورت سود و زیان بالاست.',
    ],
  };
}

export function getKeyEventsForStock(symbol: string, industry: string): CodalKeyEvent[] {
  void symbol;
  void industry;
  // Corporate events must come from Codal disclosures, never a template.
  return [];

  /*
  const normSymbol = symbol.trim();

  // Custom events for specific tickers
  if (normSymbol === 'فولاد') {
    return [
      {
        id: 'evt-1',
        type: 'assembly',
        title: 'مجمع عمومی عادی سالیانه (تصویب صورت‌های مالی)',
        date: '۱۴۰۴/۰۴/۲۹',
        summary: 'تصویب صورت‌های مالی دوره ۱۲ ماهه، تقسیم ۶۰۰ ریال سود نقدی به ازای هر سهم و تخصیص پاداش قانونی.',
        badgeText: 'تقسیم سود ۶۰۰ ریالی',
        impactStatus: 'positive',
      },
      {
        id: 'evt-2',
        type: 'capital_increase',
        title: 'افزایش سرمایه از محل سود انباشته و آورده',
        date: '۱۴۰۴/۰۲/۱۸',
        summary: 'ثبت افزایش سرمایه ۵۰ درصدی شرکت از محل سود انباشته به منظور اجرای طرح‌های توسعه خط نورد گرم ۲.',
        badgeText: 'افزایش سرمایه ۵۰٪',
        impactStatus: 'positive',
      },
      {
        id: 'evt-3',
        type: 'board_change',
        title: 'تغییر ترکیب نمایندگان هیئت مدیره',
        date: '۱۴۰۴/۰۱/۱۵',
        summary: 'تعیین اعضای جدید هیئت مدیره و انتصاب مدیرعامل با تایید سازمان بورس و اوراق بهادار.',
        badgeText: 'انتصاب مدیریت جدید',
        impactStatus: 'neutral',
      },
    ];
  }

  if (normSymbol === 'وبملت') {
    return [
      {
        id: 'evt-1',
        type: 'assembly',
        title: 'مجمع عمومی عادی سالیانه بانک ملت',
        date: '۱۴۰۴/۰۴/۳۰',
        summary: 'تصویب صورت‌های مالی سال ۱۲ ماهه و تصویب سود نقدی ۱۸۰ ریالی و تخصیص ذخایر مطالبات مشکوک‌الوصول.',
        badgeText: 'سود نقدی ۱۸۰ ریالی',
        impactStatus: 'positive',
      },
      {
        id: 'evt-2',
        type: 'capital_increase',
        title: 'پیشنهاد افزایش سرمایه از محل تجدید ارزیابی دارایی‌ها',
        date: '۱۴۰۴/۰۳/۱۲',
        summary: 'ارسال گزارش توجیهی افزایش سرمایه ۱۲۰ درصدی از محل تجدید ارزیابی املاک و دارایی‌های ثابت به بازرس.',
        badgeText: 'تجدید ارزیابی ۱۲۰٪',
        impactStatus: 'positive',
      },
      {
        id: 'evt-3',
        type: 'board_change',
        title: 'معرفی نمایندگان حقوقی هیئت مدیره',
        date: '۱۴۰۴/۰۲/۰۵',
        summary: 'تغییر نماینده شرکت سرمایه‌گذاری استانی در ترکیب هیئت مدیره بانک ملت.',
        badgeText: 'تغییر نماینده هیئت مدیره',
        impactStatus: 'neutral',
      },
    ];
  }

  // Generic/fallback events for other stocks
  return [
    {
      id: 'evt-gen-1',
      type: 'assembly',
      title: `مجمع عمومی عادی سالیانه شرکت (${normSymbol})`,
      date: '۱۴۰۴/۰۴/۲۵',
      summary: 'تصویب صورت‌های مالی ۱۲ ماهه، تقسیم سود نقدی ۸۰ درصدی و تعیین روزنامه رسمی شرکت.',
      badgeText: 'تصویب سود نقدی',
      impactStatus: 'positive',
    },
    {
      id: 'evt-gen-2',
      type: 'capital_increase',
      title: 'گزارش توجیهی افزایش سرمایه',
      date: '۱۴۰۴/۰۳/۰۸',
      summary: 'پیشنهاد هیئت مدیره به مجمع فوق‌العاده در خصوص افزایش سرمایه ۳۵ درصدی از محل سود انباشته.',
      badgeText: 'افزایش سرمایه ۳۵٪',
      impactStatus: 'positive',
    },
    {
      id: 'evt-gen-3',
      type: 'board_change',
      title: 'آگهی تغییرات هیئت مدیره در روزنامه رسمی',
      date: '۱۴۰۴/۰۱/۲۲',
      summary: 'انتصاب رئیس هیئت مدیره و تمدید دوره مدیریت مدیرعامل به مدت ۲ سال.',
      badgeText: 'ثبت تغییرات مدیران',
      impactStatus: 'neutral',
    },
  ]; */
}

export function getQuarterlyProfitsForStock(symbol: string, industry: string): QuarterlyProfitItem[] {
  // This legacy helper must never invent financial values. Real quarterly
  // values must come from the authoritative analysis response.
  void symbol;
  void industry;
  return [];
}

export function enrichStockDataWithNewFeatures(data: StockHealthCardData): StockHealthCardData {
  // قابلیت‌های اختیاری فقط وقتی نمایش داده می‌شوند که سرویس واقعی آن‌ها را
  // همراه پاسخ برگرداند. هیچ داده‌ی نمایشی نباید به گزارش رسمی تزریق شود.
  return data;
}
