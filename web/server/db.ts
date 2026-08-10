import fs from 'fs';
import path from 'path';

export interface UserRecord {
  id: string;
  email: string;
  name: string;
  passwordHash: string;
  plan: 'free' | 'pro' | 'vip';
  dailyAnalysesCount: number;
  lastAnalysisDate: string;
  createdAt: string;
}

export interface SavedAnalysisRecord {
  id: string;
  userId: string;
  symbol: string;
  fullName: string;
  reportDate: string;
  industry: string;
  peRatio: string;
  currentPrice: number;
  healthScore: number;
  data: any;
  createdAt: string;
}

export interface StockCacheRecord {
  symbol: string;
  fullName: string;
  price: number;
  pe: string;
  eps: number;
  marketCap: string;
  industry: string;
  updatedAt: string;
  rawTsetmcData?: any;
  rawCodalData?: any;
}

export interface AlertRecord {
  id: string;
  userId: string;
  symbol: string;
  targetPrice?: number;
  targetPe?: number;
  codalNotify: boolean;
  createdAt: string;
}

export interface CodalReportRecord {
  id: string;
  symbol: string;
  title: string;
  publishDate: string;
  letterCode: string;
  url: string;
  isAudited: boolean;
}

export interface CodalFinancialsCacheRecord {
  symbol: string;
  financials: any; // ParsedCodalFinancials
  extractedAt: string;
}

interface DatabaseSchema {
  users: UserRecord[];
  analyses: SavedAnalysisRecord[];
  stocksCache: Record<string, StockCacheRecord>;
  codalFinancialsCache: Record<string, CodalFinancialsCacheRecord>;
  alerts: AlertRecord[];
  codalReports: CodalReportRecord[];
  meta: {
    installedAt: string;
    version: string;
    totalAnalysesExecuted: number;
  };
}

const DATA_DIR = path.join(process.cwd(), 'data');
const DB_FILE = path.join(DATA_DIR, 'db.json');

class LocalDB {
  private data: DatabaseSchema;

  constructor() {
    this.ensureDataDir();
    this.data = this.loadDatabase();
  }

  private ensureDataDir() {
    if (!fs.existsSync(DATA_DIR)) {
      fs.mkdirSync(DATA_DIR, { recursive: true });
    }
  }

  private loadDatabase(): DatabaseSchema {
    try {
      if (fs.existsSync(DB_FILE)) {
        const fileContent = fs.readFileSync(DB_FILE, 'utf-8');
        const parsed = JSON.parse(fileContent);
        return {
          users: parsed.users || [],
          analyses: parsed.analyses || [],
          stocksCache: parsed.stocksCache || {},
          codalFinancialsCache: parsed.codalFinancialsCache || {},
          alerts: parsed.alerts || [],
          codalReports: parsed.codalReports || [],
          meta: parsed.meta || {
            installedAt: new Date().toISOString(),
            version: '2.5.0',
            totalAnalysesExecuted: 0,
          },
        };
      }
    } catch (err) {
      console.error('[Database] Error reading db.json, creating new database instance:', err);
    }

    const initialSchema: DatabaseSchema = {
      users: [
        {
          id: 'admin_user_1',
          email: 'admin@boursnegar.ir',
          name: 'مدیر سامانه بورس‌نگار',
          passwordHash: 'admin123',
          plan: 'vip',
          dailyAnalysesCount: 0,
          lastAnalysisDate: new Date().toISOString().split('T')[0],
          createdAt: new Date().toISOString(),
        },
      ],
      analyses: [],
      stocksCache: {},
      codalFinancialsCache: {},
      alerts: [],
      codalReports: [],
      meta: {
        installedAt: new Date().toISOString(),
        version: '2.5.0',
        totalAnalysesExecuted: 0,
      },
    };

    this.saveData(initialSchema);
    return initialSchema;
  }

  private saveData(schema?: DatabaseSchema) {
    try {
      this.ensureDataDir();
      const contentToSave = JSON.stringify(schema || this.data, null, 2);
      fs.writeFileSync(DB_FILE, contentToSave, 'utf-8');
    } catch (err) {
      console.error('[Database] Save failed:', err);
    }
  }

  public getStats() {
    return {
      version: this.data.meta.version,
      installedAt: this.data.meta.installedAt,
      totalAnalysesExecuted: this.data.meta.totalAnalysesExecuted,
      usersCount: this.data.users.length,
      savedAnalysesCount: this.data.analyses.length,
      cachedStocksCount: Object.keys(this.data.stocksCache).length,
      activeAlertsCount: this.data.alerts.length,
      dbFilePath: DB_FILE,
      dbSizeBytes: fs.existsSync(DB_FILE) ? fs.statSync(DB_FILE).size : 0,
    };
  }

  // User Auth & Subscription Management
  public getUserByEmail(email: string): UserRecord | undefined {
    return this.data.users.find((u) => u.email.toLowerCase() === email.toLowerCase());
  }

  public getUserById(id: string): UserRecord | undefined {
    return this.data.users.find((u) => u.id === id);
  }

  public createUser(user: Omit<UserRecord, 'id' | 'createdAt' | 'dailyAnalysesCount' | 'lastAnalysisDate'>): UserRecord {
    const newUser: UserRecord = {
      ...user,
      id: 'usr_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
      dailyAnalysesCount: 0,
      lastAnalysisDate: new Date().toISOString().split('T')[0],
      createdAt: new Date().toISOString(),
    };
    this.data.users.push(newUser);
    this.saveData();
    return newUser;
  }

  public incrementUserAnalysis(userId: string): { allowed: boolean; remaining: number; plan: string } {
    const user = this.getUserById(userId);
    const today = new Date().toISOString().split('T')[0];

    this.data.meta.totalAnalysesExecuted += 1;

    if (!user) {
      this.saveData();
      return { allowed: true, remaining: 999, plan: 'free' };
    }

    if (user.lastAnalysisDate !== today) {
      user.dailyAnalysesCount = 0;
      user.lastAnalysisDate = today;
    }

    const limit = user.plan === 'vip' || user.plan === 'pro' ? 1000 : 3;

    if (user.dailyAnalysesCount >= limit) {
      this.saveData();
      return { allowed: false, remaining: 0, plan: user.plan };
    }

    user.dailyAnalysesCount += 1;
    this.saveData();
    return {
      allowed: true,
      remaining: limit - user.dailyAnalysesCount,
      plan: user.plan,
    };
  }

  public updateUserPlan(userId: string, plan: 'free' | 'pro' | 'vip'): boolean {
    const user = this.getUserById(userId);
    if (user) {
      user.plan = plan;
      this.saveData();
      return true;
    }
    return false;
  }

  // Saved Analyses
  public saveAnalysis(analysis: Omit<SavedAnalysisRecord, 'id' | 'createdAt'>): SavedAnalysisRecord {
    const record: SavedAnalysisRecord = {
      ...analysis,
      id: 'anl_' + Date.now() + '_' + Math.random().toString(36).substr(2, 4),
      createdAt: new Date().toISOString(),
    };
    this.data.analyses.unshift(record);
    // Limit saved history to last 500 items
    if (this.data.analyses.length > 500) {
      this.data.analyses = this.data.analyses.slice(0, 500);
    }
    this.saveData();
    return record;
  }

  public getAnalyses(userId?: string): SavedAnalysisRecord[] {
    if (userId) {
      return this.data.analyses.filter((a) => a.userId === userId);
    }
    return this.data.analyses;
  }

  public deleteAnalysis(id: string, userId: string): boolean {
    const initialLen = this.data.analyses.length;
    this.data.analyses = this.data.analyses.filter((a) => a.id !== id || (userId && a.userId !== userId));
    if (this.data.analyses.length !== initialLen) {
      this.saveData();
      return true;
    }
    return false;
  }

  // Stock TSETMC & Codal Caching
  public getStockCache(symbol: string): StockCacheRecord | undefined {
    return this.data.stocksCache[symbol];
  }

  public setStockCache(symbol: string, record: StockCacheRecord) {
    this.data.stocksCache[symbol] = record;
    this.saveData();
  }

  // Codal Financial Statements Cache
  public getCodalFinancialsCache(symbol: string): CodalFinancialsCacheRecord | undefined {
    return this.data.codalFinancialsCache ? this.data.codalFinancialsCache[symbol] : undefined;
  }

  public saveCodalFinancialsCache(symbol: string, financials: any) {
    if (!this.data.codalFinancialsCache) {
      this.data.codalFinancialsCache = {};
    }
    this.data.codalFinancialsCache[symbol] = {
      symbol,
      financials,
      extractedAt: new Date().toISOString(),
    };
    this.saveData();
  }

  // Alerts Management
  public addAlert(userId: string, symbol: string, targetPrice?: number, targetPe?: number): AlertRecord {
    const alert: AlertRecord = {
      id: 'alt_' + Date.now(),
      userId,
      symbol,
      targetPrice,
      targetPe,
      codalNotify: true,
      createdAt: new Date().toISOString(),
    };
    this.data.alerts.push(alert);
    this.saveData();
    return alert;
  }

  public getAlerts(userId: string): AlertRecord[] {
    return this.data.alerts.filter((a) => a.userId === userId);
  }

  public deleteAlert(alertId: string, userId: string): boolean {
    const len = this.data.alerts.length;
    this.data.alerts = this.data.alerts.filter((a) => a.id !== alertId || a.userId !== userId);
    if (this.data.alerts.length !== len) {
      this.saveData();
      return true;
    }
    return false;
  }
}

export const db = new LocalDB();
