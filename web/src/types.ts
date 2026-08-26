export type IndustryType = 
  | 'manufacturing' 
  | 'bank' 
  | 'holding' 
  | 'insurance' 
  | 'leasing' 
  | 'services';

export type StatusType = 'good' | 'mid' | 'bad';

export interface CompanyHeaderInfo {
  symbol: string;
  fullName: string;
  industry: IndustryType;
  industryTitle: string;
  financialReportTitle: string;
  currentPrice: number;
  peRatio: string;
  marketCap: string;
  reportDate: string;
  codalAuditStatus: string;
  dataStamp: {
    source: string;
    updatedAt: string;
    verificationCode: string;
  };
}

export interface QuestionCard {
  id: number;
  title: string;
  subtitle: string;
  status: StatusType;
  statusLabel: string;
  mainMetricValue: string;
  comparisonDetail: string;
  summaryAnswer: string;
}

export interface TrendPoint {
  period: string;
  value: number;
  displayValue: string;
}

export interface DonutSegment {
  label: string;
  percentage: number; // 0 to 100
  valueString: string;
  color: string;
}

export interface RatioBarItem {
  label: string;
  valuePercentage: number; // 0 to 100
  displayValue: string;
  status: StatusType;
  isNegative?: boolean;
}

export interface VisualRowData {
  trendChart: {
    title: string;
    subtitle: string;
    points: TrendPoint[]; // exactly 4 points for the trend
    unit: string;
  };
  donutChart: {
    title: string;
    subtitle: string;
    centerLabel: string;
    centerValue: string;
    segments: DonutSegment[];
  };
  ratioBars: {
    title: string;
    subtitle: string;
    bars: RatioBarItem[];
  };
}

export interface StatusBannerMetric {
  id: number;
  key: string;
  label: string;
  value: string;
  status: StatusType;
  description: string;
}

export interface GoldenSummary {
  badgeTitle: 'بنیاد قوی و باثبات' | 'بنیاد متوسط / تحت فشار' | 'بنیاد ضعیف و پرریسک';
  badgeStatus: StatusType;
  summaryText: string;
  valuationVsQualityNote: string;
  investmentOutlook: string;
}

export interface ExplanationCard {
  id: number;
  numberLabel: string;
  title: string;
  status: StatusType;
  valueText: string;
  simpleDefinition13Yo: string;
  companyContextNote: string;
}

export interface ConcludingCards {
  valuationCard: {
    title: string;
    body: string;
  };
  outlookCard: {
    title: string;
    body: string;
  };
  dataSourceStamp: {
    title: string;
    codalLinkText: string;
    lastUpdate: string;
    disclaimer: string;
  };
}

export interface PeerCompany {
  symbol: string;
  name: string;
  healthStatus: StatusType; // 'good' | 'mid' | 'bad'
  peRatio?: string;
}

export interface PeScenario {
  name: string; // 'خوش‌بینانه' | 'پایه' | 'بدبینانه'
  type: 'optimistic' | 'base' | 'pessimistic';
  epsGrowthPercent: number; // e.g. +35%
  simulatedPe: number; // e.g. 4.2
  targetPriceChange: string; // e.g. +30%
  description: string;
}

export interface PeSimulationData {
  currentPe: number;
  currentPrice: number;
  baseEps: number;
  scenarios: PeScenario[];
  summaryNote: string;
}

export interface SmartRecommendation {
  isSuitableForBuy: boolean;
  statusTitle: string; // e.g. 'محدوده جذاب و کم‌ریسک برای خرید' | 'احتیاط - نزدیکی به سقف کارشناسی'
  suitabilityNote: string; // Detailed reason
  buyRange: {
    minPrice: number;
    maxPrice: number;
    displayRange: string; // e.g. '۴,۸۰۰ تا ۵,۱۵0 ریال'
  };
  sellTargetRange: {
    minPrice: number;
    maxPrice: number;
    displayRange: string; // e.g. '۶,۷۰۰ تا ۷,۴۰۰ ریال'
  };
  stopLossPrice: {
    price: number;
    displayPrice: string; // e.g. '۴,۵۰۰ ریال'
  };
  riskLevel: 'کم' | 'متوسط' | 'زیاد';
  insights: string[]; // Smart advice bullet points
}

export type CodalEventType = 'assembly' | 'capital_increase' | 'board_change' | 'dividend' | 'other';

export interface CodalKeyEvent {
  id: string;
  type: CodalEventType;
  title: string; // e.g. 'مجمع عمومی عادی سالیانه'
  date: string; // e.g. '۱۴۰۴/۰۴/۲۸'
  summary: string; // Key details
  badgeText: string; // e.g. 'تصویب سود ۶۵۰ ریالی'
  impactStatus?: 'positive' | 'neutral' | 'negative';
}

export interface QuarterlyProfitItem {
  quarter: 'بهار' | 'تابستان' | 'پاییز' | 'زمستان';
  stockProfit: number; // Billion Rials (میلیارد ریال)
  industryAvgProfit: number; // Billion Rials (میلیارد ریال)
  marginPercent: number; // Profit margin %
  growthPercent: number; // Year-over-year profit growth %
}

// --- USER AUTHENTICATION & SUBSCRIPTION TYPES ---
export interface UserProfile {
  mobile: string;
  isLoggedIn: boolean;
  isVip: boolean;
  remainingFreeQuota: number; // Starts at 5 free analyses
  usedQuota: number;
  subscriptionPlan?: 'free' | '1_month' | '3_months' | '12_months';
  subscriptionExpiresAt?: string; // e.g. '۱۴۰۴/۰۶/۳۰'
}

export interface StockAlert {
  id: string;
  symbol: string;
  targetPrice?: number;
  targetPe?: number;
  condition: 'above' | 'below';
  mobile: string;
  createdAt: string;
  active: boolean;
}

export interface SubscriptionPlan {
  id: '1_month' | '3_months' | '12_months';
  title: string;
  durationMonths: number;
  priceToman: number;
  originalPriceToman?: number;
  discountBadge?: string;
  features: string[];
  isPopular?: boolean;
}

export interface SmsGatewayConfig {
  serviceProvider?: 'unconfigured' | 'kavenegar' | 'ippanel' | 'ghasedak' | 'farapayamak';
  serviceValue?: string;
  lineNumber?: string;
  otpPatternCode?: string;
}

export interface AdminStats {
  totalUsers: number;
  vipUsers: number;
  totalAnalysesCount: number;
  totalRevenueToman: number;
  serviceConfig: SmsGatewayConfig;
}

export interface StockHealthCardData {
  header: CompanyHeaderInfo;
  questions: QuestionCard[]; // 3 question cards
  visuals: VisualRowData; // trend, donut, ratio bars
  statusBanner: StatusBannerMetric[]; // 6 metrics
  goldenSummary: GoldenSummary; // gold banner with star
  explanationCards: ExplanationCard[]; // 6 detailed cards
  conclusion: ConcludingCards; // 2 cards + sources
  peers?: PeerCompany[]; // top 3 industry peers
  peSimulation?: PeSimulationData; // future P/E scenario simulation
  smartRecommendation?: SmartRecommendation; // buying/selling bounds & investment insights
  keyEvents?: CodalKeyEvent[]; // recent corporate events from Codal
  quarterlyProfits?: QuarterlyProfitItem[]; // quarterly net profit comparison vs industry
  reportMode?: 'audited' | 'latest_codal';
}
