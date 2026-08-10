import express from 'express';
import path from 'path';
import fs from 'fs';
import dotenv from 'dotenv';
import { createServer as createViteServer } from 'vite';

import { db } from './server/db';
import { generateRealHealthCard, UpstreamAnalysisError } from './server/realAnalysisAdapter';

dotenv.config();

const __dirname = process.cwd();

const app = express();
const PORT = 3000;

function requireAdminApi(req: express.Request, res: express.Response, next: express.NextFunction) {
  const expected = process.env.ADMIN_API_KEY;
  if (!expected || req.header('x-admin-key') !== expected) {
    return res.status(404).json({ success: false, error: 'مسیر در دسترس نیست.' });
  }
  next();
}

app.use(express.json({ limit: '10mb' }));

// REST API: Permanent Database Stats
app.get('/api/db/stats', requireAdminApi, (req, res) => {
  try {
    const stats = db.getStats();
    res.json({ success: true, stats });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// REST API: Saved Analyses
app.get('/api/db/analyses', requireAdminApi, (req, res) => {
  try {
    const userId = (req.query.userId as string) || 'admin_user_1';
    const list = db.getAnalyses(userId);
    res.json({ success: true, list });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.post('/api/db/analyses', requireAdminApi, (req, res) => {
  try {
    const { userId, symbol, fullName, reportDate, industry, peRatio, currentPrice, healthScore, data } = req.body;
    const saved = db.saveAnalysis({
      userId: userId || 'admin_user_1',
      symbol: symbol || 'نماد',
      fullName: fullName || 'شرکت بورسی',
      reportDate: reportDate || '۱۴۰۵',
      industry: industry || 'manufacturing',
      peRatio: peRatio || '۵.۸',
      currentPrice: currentPrice || 0,
      healthScore: healthScore || 85,
      data,
    });
    res.json({ success: true, saved });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

app.delete('/api/db/analyses/:id', requireAdminApi, (req, res) => {
  try {
    const userId = (req.query.userId as string) || 'admin_user_1';
    const deleted = db.deleteAnalysis(req.params.id, userId);
    res.json({ success: deleted });
  } catch (err: any) {
    res.status(500).json({ success: false, error: err.message });
  }
});

// User Auth API (بدون تغییر - ربطی به داده مالی نداره)
app.post('/api/auth/register', (req, res) => {
  return res.status(501).json({ success: false, error: 'سامانه ورود هنوز فعال نشده است.' });
});

app.post('/api/auth/login', (req, res) => {
  return res.status(501).json({ success: false, error: 'سامانه ورود هنوز فعال نشده است.' });
});

// Primary API Route: تحلیل بنیادی واقعی (بدون هیچ داده‌ی ساختگی)
// این endpoint حالا صرفاً یک لایه‌ی نازک روی سرویس Python واقعی است که
// در server/realAnalysisAdapter.ts پیاده‌سازی شده.
app.post('/api/analyze', async (req, res) => {
  try {
    const { query, userId, reportMode = 'audited' } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'لطفاً نماد یا نام شرکت بورس تهران را وارد کنید.' });
    }

    const cleanSymbol = String(query).trim().replace(/^نماد\s+/, '');
    if (!/^[\u0600-\u06FFa-zA-Z0-9‌_-]{1,32}$/.test(cleanSymbol)) {
      return res.status(400).json({ success: false, error: 'نماد واردشده معتبر نیست.' });
    }
    const cleanReportMode = reportMode === 'latest_codal' ? 'latest_codal' : 'audited';

    const finalData = await generateRealHealthCard(cleanSymbol, cleanReportMode);

    // ذخیره در دیتابیس محلی (تاریخچه‌ی جست‌وجوهای کاربر)
    db.setStockCache(cleanSymbol, {
      symbol: cleanSymbol,
      fullName: finalData.header.fullName,
      price: finalData.header.currentPrice,
      pe: finalData.header.peRatio,
      eps: null,
      marketCap: finalData.header.marketCap,
      industry: finalData.header.industry,
      updatedAt: new Date().toISOString(),
    });

    db.saveAnalysis({
      userId: userId || 'admin_user_1',
      symbol: cleanSymbol,
      fullName: finalData.header.fullName,
      reportDate: finalData.header.reportDate,
      industry: finalData.header.industry,
      peRatio: finalData.header.peRatio,
      currentPrice: finalData.header.currentPrice,
      healthScore: finalData.goldenSummary.badgeStatus === 'good' ? 90 : finalData.goldenSummary.badgeStatus === 'mid' ? 65 : 35,
      data: finalData,
    });

    db.incrementUserAnalysis(userId || 'admin_user_1');

    return res.json({ success: true, data: finalData });
  } catch (err: any) {
    console.error('[Analysis Error]:', err);
    const status = err instanceof UpstreamAnalysisError ? 502 : 500;
    return res.status(status).json({
      success: false,
      error: err.message || 'خطا در انجام تحلیل بنیادی توسط سرور.',
    });
  }
});

async function startServer() {
  const distPath = path.join(process.cwd(), 'dist');
  const isProduction = process.env.NODE_ENV === 'production' || fs.existsSync(path.join(distPath, 'index.html'));

  if (!isProduction) {
    try {
      const vite = await createViteServer({
        server: { middlewareMode: true },
        appType: 'spa',
      });
      app.use(vite.middlewares);
      console.log('[Dev Mode] Vite middleware mounted');
    } catch (e) {
      console.error('[Dev Mode Error] Failed to mount Vite, falling back to static:', e);
      app.use(express.static(distPath));
      app.get('*', (req, res) => {
        res.sendFile(path.join(distPath, 'index.html'));
      });
    }
  } else {
    console.log('[Production Mode] Serving static files from dist');
    app.use(express.static(distPath));
    app.get('*', (req, res) => {
      res.sendFile(path.join(distPath, 'index.html'));
    });
  }

  app.listen(PORT, '127.0.0.1', () => {
    console.log(`[Bourse Analyzer] Server running on http://127.0.0.1:${PORT}`);
    console.log(`[Bourse Analyzer] Using REAL data service at ${process.env.PYTHON_API_BASE || 'http://localhost:8001'}`);
  });
}

startServer().catch((err) => {
  console.error('Fatal Server Startup Error:', err);
});
