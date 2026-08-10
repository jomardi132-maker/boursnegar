import React from 'react';
import { VisualRowData, StatusType } from '../types';
import { TrendingUp, PieChart, BarChart3 } from 'lucide-react';

interface VisualRowProps {
  visuals: VisualRowData;
}

export const VisualRow: React.FC<VisualRowProps> = ({ visuals }) => {
  const trendChart = visuals?.trendChart || {
    title: 'روند مالی',
    subtitle: 'داده رسمی',
    unit: 'تومان',
    points: [],
  };
  const donutChart = visuals?.donutChart || {
    title: 'ترکیب درآمد',
    subtitle: 'سهم تفکیکی',
    centerLabel: 'کل',
    centerValue: '۱۰۰٪',
    segments: [],
  };
  const ratioBars = visuals?.ratioBars || {
    title: 'نسبت‌های کلیدی',
    subtitle: 'شاخص‌ها',
    bars: [],
  };

  const pointsList = trendChart.points || [];
  const segmentsList = donutChart.segments || [];
  const barsList = ratioBars.bars || [];

  if (!pointsList.length && !segmentsList.length) {
    if (!barsList.length) return null;
    return (
      <section className="rounded-2xl border border-slate-800 bg-slate-900 p-5 shadow-xl">
        <div className="mb-5 flex items-start justify-between gap-3 border-b border-slate-800 pb-4">
          <div>
            <h2 className="flex items-center gap-2 text-base font-black text-white">
              <BarChart3 className="h-5 w-5 text-cyan-400" />
              {ratioBars.title}
            </h2>
            <p className="mt-1 text-xs text-slate-400">{ratioBars.subtitle}</p>
          </div>
          <span className="rounded-full border border-slate-700 bg-slate-800 px-3 py-1 text-[10px] text-slate-400">داده رسمی</span>
        </div>
        <div className="grid gap-5 md:grid-cols-3">
          {barsList.map((bar, idx) => {
            const clampedPercent = Math.min(Math.max(bar.valuePercentage, 0), 100);
            return (
              <div key={`${bar.label}-${idx}`} className="rounded-xl border border-slate-800 bg-slate-950/60 p-4">
                <div className="mb-3 flex items-center justify-between gap-3 text-xs">
                  <span className="font-bold text-slate-200">{bar.label}</span>
                  <span className="font-black text-cyan-300">{bar.displayValue}</span>
                </div>
                <div className="h-2.5 overflow-hidden rounded-full bg-slate-800">
                  <div className={`h-full rounded-full ${getBarColor(bar.status)}`} style={{ width: `${clampedPercent}%` }} />
                </div>
              </div>
            );
          })}
        </div>
      </section>
    );
  }

  // Formula calculation for Trend SVG Y points:
  const values = pointsList.map((p) => p.value || 0);
  const minVal = values.length ? Math.min(...values) : 0;
  const maxVal = values.length ? Math.max(...values) : 1;
  const valRange = Math.max(maxVal - minVal, 1);

  const pointsWithY = pointsList.map((p, idx) => {
    const x = pointsList.length > 1 ? 50 + idx * (320 / (pointsList.length - 1)) : 210;
    const y = 150 - (((p.value || 0) - minVal) / valRange) * 115;
    return { ...p, x, y };
  });

  const pathD = pointsWithY.length
    ? pointsWithY.reduce((acc, point, index) => {
        if (index === 0) return `M ${point.x} ${point.y}`;
        const prev = pointsWithY[index - 1];
        const cp1x = prev.x + 40;
        const cp1y = prev.y;
        const cp2x = point.x - 40;
        const cp2y = point.y;
        return `${acc} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${point.x} ${point.y}`;
      }, '')
    : 'M 50 150 L 370 150';

  const fillD = pointsWithY.length
    ? `${pathD} L ${pointsWithY[pointsWithY.length - 1].x} 180 L ${pointsWithY[0].x} 180 Z`
    : 'M 50 180 L 370 180 Z';

  let cumulativePercentage = 0;
  const donutSegmentsWithAngles = segmentsList.map((seg) => {
    const startAngle = (cumulativePercentage / 100) * 360;
    cumulativePercentage += seg.percentage || 0;
    const endAngle = (cumulativePercentage / 100) * 360;
    return { ...seg, startAngle, endAngle };
  });

  const getCoordinatesForPercent = (angleInDegrees: number, radius = 70, cx = 90, cy = 90) => {
    const angleInRadians = ((angleInDegrees - 90) * Math.PI) / 180;
    return {
      x: cx + radius * Math.cos(angleInRadians),
      y: cy + radius * Math.sin(angleInRadians),
    };
  };

  function getBarColor(status: StatusType) {
    switch (status) {
      case 'good':
        return 'bg-cyan-400';
      case 'mid':
        return 'bg-amber-400';
      case 'bad':
        return 'bg-rose-400';
      default:
        return 'bg-emerald-400';
    }
  }

  return (
    <section className="mb-5">
      {/* Three-piece Visual Row Grid in Bento Style */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        
        {/* Right: Trend Chart (5 cols) */}
        <div className="lg:col-span-5 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-800 mb-2">
              <div className="flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">{trendChart.title}</h3>
              </div>
              <span className="text-[10px] font-mono text-cyan-300 bg-slate-800 px-2 py-0.5 rounded border border-slate-700">
                ۴ دوره اخیر
              </span>
            </div>
            <p className="text-[11px] text-slate-400 mb-1 uppercase tracking-tighter">{trendChart.subtitle}</p>
          </div>

          {/* SVG Smooth Trend Curve Container */}
          <div className="w-full relative my-2 bg-slate-950/80 border border-slate-800 rounded-lg p-3 overflow-hidden">
            <svg viewBox="0 0 420 200" className="w-full h-auto overflow-visible">
              <defs>
                <linearGradient id="trendGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#22d3ee" stopOpacity="0.3" />
                  <stop offset="100%" stopColor="#22d3ee" stopOpacity="0.0" />
                </linearGradient>
              </defs>

              <line x1="20" y1="35" x2="400" y2="35" stroke="#1e293b" strokeDasharray="3 3" />
              <line x1="20" y1="85" x2="400" y2="85" stroke="#1e293b" strokeDasharray="3 3" />
              <line x1="20" y1="135" x2="400" y2="135" stroke="#1e293b" strokeDasharray="3 3" />
              <line x1="20" y1="180" x2="400" y2="180" stroke="#334155" strokeWidth="1.5" />

              <path d={fillD} fill="url(#trendGradient)" />
              <path d={pathD} fill="none" stroke="#22d3ee" strokeWidth="3.5" strokeLinecap="round" />

              {pointsWithY.map((pt, idx) => (
                <g key={idx}>
                  <circle cx={pt.x} cy={pt.y} r="6" fill="#0f172a" stroke="#22d3ee" strokeWidth="2.5" />
                  <circle cx={pt.x} cy={pt.y} r="2.5" fill="#67e8f9" />

                  <text
                    x={pt.x}
                    y="196"
                    textAnchor="middle"
                    fill="#94a3b8"
                    fontSize="10"
                    fontWeight="600"
                  >
                    {pt.period}
                  </text>

                  <rect
                    x={pt.x - 28}
                    y={pt.y - 26}
                    width="56"
                    height="18"
                    rx="4"
                    fill="#0f172a"
                    stroke="#22d3ee"
                    strokeWidth="1"
                  />
                  <text
                    x={pt.x}
                    y={pt.y - 13}
                    textAnchor="middle"
                    fill="#22d3ee"
                    fontSize="10"
                    fontWeight="bold"
                  >
                    {pt.displayValue}
                  </text>
                </g>
              ))}
            </svg>
          </div>

          <div className="text-[10px] text-slate-400 text-center pt-1">
            واحد: <strong className="text-slate-300">{trendChart.unit}</strong>
          </div>
        </div>

        {/* Middle: Donut Breakdown (3 cols) */}
        <div className="lg:col-span-3 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between items-center text-center">
          <div className="w-full">
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-800 mb-2">
              <div className="flex items-center gap-1.5 mx-auto">
                <PieChart className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-bold text-white">{donutChart.title}</h3>
              </div>
            </div>
            <p className="text-[10px] text-slate-400 uppercase tracking-tight">{donutChart.subtitle}</p>
          </div>

          {/* Donut Chart SVG */}
          <div className="relative w-36 h-36 my-2 flex items-center justify-center">
            <svg viewBox="0 0 180 180" className="w-full h-full transform -rotate-90">
              {donutSegmentsWithAngles.map((seg, idx) => {
                const start = getCoordinatesForPercent(seg.startAngle);
                const end = getCoordinatesForPercent(seg.endAngle);
                const largeArcFlag = seg.percentage > 50 ? 1 : 0;

                const pathData = [
                  `M ${start.x} ${start.y}`,
                  `A 70 70 0 ${largeArcFlag} 1 ${end.x} ${end.y}`,
                ].join(' ');

                return (
                  <path
                    key={idx}
                    d={pathData}
                    fill="none"
                    stroke={seg.color === '#00c4b4' ? '#22d3ee' : seg.color}
                    strokeWidth="20"
                    strokeLinecap="butt"
                  />
                );
              })}
            </svg>

            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
              <span className="text-[10px] text-slate-400">{donutChart.centerLabel}</span>
              <span className="text-sm font-extrabold text-white font-mono">{donutChart.centerValue}</span>
            </div>
          </div>

          {/* Donut Legend */}
          <div className="w-full space-y-1 pt-2 border-t border-slate-800 text-[11px]">
            {segmentsList.map((seg, idx) => (
              <div key={idx} className="flex items-center justify-between text-slate-300">
                <div className="flex items-center gap-1.5 truncate max-w-[130px]">
                  <span
                    className="w-2 h-2 rounded-full shrink-0"
                    style={{ backgroundColor: seg.color === '#00c4b4' ? '#22d3ee' : seg.color }}
                  />
                  <span className="truncate text-[10px]">{seg.label}</span>
                </div>
                <span className="font-mono text-[10px] font-bold text-cyan-300">
                  {seg.percentage}٪
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Left: Key Operational Ratios (4 cols) */}
        <div className="lg:col-span-4 bg-slate-900 border border-slate-800 rounded-xl p-4 shadow-lg flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between pb-2.5 border-b border-slate-800 mb-2">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-amber-400" />
                <h3 className="text-sm font-bold text-white">{ratioBars.title}</h3>
              </div>
            </div>
            <p className="text-[10px] text-slate-400 mb-3 uppercase tracking-tight">{ratioBars.subtitle}</p>
          </div>

          {/* Percentage Horizontal Bars */}
          <div className="space-y-3.5 my-auto">
            {barsList.map((bar, idx) => {
              const clampedPercent = Math.min(Math.max(bar.valuePercentage, 0), 100);

              return (
                <div key={idx} className="space-y-1">
                  <div className="flex justify-between items-center text-[10px]">
                    <span className="font-semibold text-slate-200">{bar.label}</span>
                    <span className="font-bold font-mono text-cyan-300">{bar.displayValue}</span>
                  </div>

                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full ${getBarColor(
                        bar.status
                      )} transition-all duration-500`}
                      style={{ width: `${clampedPercent}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>

          <div className="pt-2 border-t border-slate-800 text-[10px] text-slate-400 flex justify-between items-center">
            <span>مقادیر ۰ تا ۱۰۰ درصد</span>
            <span className="text-cyan-400 font-semibold">حاشیه امن عملیاتی</span>
          </div>
        </div>

      </div>
    </section>
  );
};
