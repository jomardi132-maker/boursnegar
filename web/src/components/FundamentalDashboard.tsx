import { useLayoutEffect, useRef } from 'react';
import { ArrowUpLeft, Database, Gauge, ShieldCheck, Sparkles } from 'lucide-react';
import gsap from 'gsap';

export type FundamentalDashboardOverview = {
  catalog: { instruments: number };
  prices: { rows: number; instruments: number; from_date: string; to_date: string };
  disclosures: { rows: number; issuers: number; updated_at: string | null };
  analysis: { analyzed: number };
};

function fa(value: number | null | undefined) {
  return value == null ? '—' : value.toLocaleString('fa-IR');
}

function displayDate(value: string | null | undefined) {
  if (!value) return '—';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return value;
  return parsed.toLocaleDateString('fa-IR', { year: 'numeric', month: '2-digit', day: '2-digit' });
}

export function FundamentalDashboard({ overview }: { overview: FundamentalDashboardOverview | null }) {
  const root = useRef<HTMLElement>(null);

  useLayoutEffect(() => {
    if (!root.current || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const ctx = gsap.context(() => {
      gsap.from('.fundamental-dashboard__item', { y: 18, opacity: 0, duration: 0.55, stagger: 0.08, ease: 'power2.out' });
    }, root);
    return () => ctx.revert();
  }, []);

  const metrics = [
    { label: 'نماد و ابزار فعال', value: fa(overview?.catalog.instruments), icon: Database },
    { label: 'رکورد قیمت روزانه', value: fa(overview?.prices.rows), icon: ArrowUpLeft },
    { label: 'نسخه اطلاعیه کدال', value: fa(overview?.disclosures.rows), icon: ShieldCheck },
    { label: 'تحلیل ثبت‌شده', value: fa(overview?.analysis.analyzed), icon: Sparkles },
  ];

  return (
    <section ref={root} className="fundamental-dashboard" id="fundamental-dashboard" aria-labelledby="fundamental-dashboard-title">
      <header className="fundamental-dashboard__header fundamental-dashboard__item">
        <div>
          <span className="fundamental-dashboard__eyebrow">نمای زنده / داده بنیادی</span>
          <h2 id="fundamental-dashboard-title">داشبوردی برای تصمیم‌های قابل ردیابی</h2>
          <p>از پوشش بازار تا کیفیت داده؛ هر عدد باید منبع، زمان و وضعیت مشخص داشته باشد.</p>
        </div>
        <div className="fundamental-dashboard__status"><span /> {overview ? 'اتصال عملیاتی' : 'در انتظار داده'}</div>
      </header>
      <div className="fundamental-dashboard__grid">
        {metrics.map(({ label, value, icon: Icon }) => (
          <article className="fundamental-dashboard__card fundamental-dashboard__item" key={label}>
            <Icon aria-hidden="true" />
            <span>{label}</span>
            <strong>{value}</strong>
            <small>{overview ? 'دریافت‌شده از پایگاه داده عملیاتی' : 'داده در این لحظه در دسترس نیست'}</small>
          </article>
        ))}
      </div>
      <footer className="fundamental-dashboard__footer fundamental-dashboard__item">
        <div><Gauge aria-hidden="true" /><span>پوشش قیمت: {displayDate(overview?.prices.from_date)} تا {displayDate(overview?.prices.to_date)}</span></div>
        <span>عدد ساختگی یا fallback در این نما استفاده نمی‌شود.</span>
      </footer>
    </section>
  );
}
