'use client';

import React from 'react';
import { CONFIG } from '@/lib/constants';
import { RetentionModelType } from '@/types/simulation';

interface RetentionCurveChartProps {
  modelType: RetentionModelType;
  actualRetention?: Record<number, number>;
  showComparison?: boolean;
}

const CURVE_COLORS: Record<string, string> = {
  social_app: 'emerald',
  crypto_app: 'amber',
  gaming: 'purple',
  utility: 'blue',
  vcoin: 'cyan',
  custom: 'slate',
};

const CURVE_NAMES: Record<string, string> = {
  social_app: 'Social App',
  crypto_app: 'Crypto App',
  gaming: 'Gaming',
  utility: 'Utility',
  vcoin: 'VCoin',
  custom: 'Custom',
};

export const RetentionCurveChart: React.FC<RetentionCurveChartProps> = ({
  modelType,
  actualRetention,
  showComparison = false,
}) => {
  // Handle 'custom' type which isn't in CONFIG.RETENTION_CURVES
  const curveKey = modelType === 'custom' ? 'social_app' : modelType;
  const curve = CONFIG.RETENTION_CURVES[curveKey as keyof typeof CONFIG.RETENTION_CURVES] || CONFIG.RETENTION_CURVES.social_app;
  
  // Generate points for smooth curve (interpolate between defined points)
  const generateCurvePoints = (retentionCurve: Record<number, number>) => {
    const points: { month: number; rate: number }[] = [];
    const months = Object.keys(retentionCurve).map(Number).sort((a, b) => a - b);
    
    for (let month = 1; month <= 24; month++) {
      if (retentionCurve[month] !== undefined) {
        points.push({ month, rate: retentionCurve[month] * 100 });
      } else {
        // Interpolate
        const lowerMonth = Math.max(...months.filter(m => m <= month), 0);
        const upperMonth = Math.min(...months.filter(m => m >= month), 24);
        
        if (lowerMonth === 0) {
          points.push({ month, rate: 100 });
        } else if (lowerMonth === upperMonth) {
          points.push({ month, rate: retentionCurve[lowerMonth] * 100 });
        } else {
          // Linear interpolation
          const lowerRate = lowerMonth === 0 ? 1 : retentionCurve[lowerMonth];
          const upperRate = retentionCurve[upperMonth];
          const t = (month - lowerMonth) / (upperMonth - lowerMonth);
          const rate = lowerRate + t * (upperRate - lowerRate);
          points.push({ month, rate: rate * 100 });
        }
      }
    }
    
    return points;
  };

  const curvePoints = generateCurvePoints(curve);
  const color = CURVE_COLORS[modelType];

  // Key milestones to highlight
  const milestones = [1, 3, 6, 12];

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="text-xl">📉</span>
          Retention Curve: {CURVE_NAMES[modelType]}
        </h3>
      </div>

      {/* Chart Area */}
      <div className="relative h-48 mb-4">
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 bottom-0 w-8 flex flex-col justify-between text-xs text-slate-500">
          <span>100%</span>
          <span>75%</span>
          <span>50%</span>
          <span>25%</span>
          <span>0%</span>
        </div>

        {/* Grid lines */}
        <div className="absolute left-10 right-0 top-0 bottom-0">
          {[0, 25, 50, 75, 100].map((pct) => (
            <div
              key={pct}
              className="absolute left-0 right-0 border-t border-slate-700/50"
              style={{ bottom: `${pct}%` }}
            />
          ))}
        </div>

        {/* Curve */}
        <div className="absolute left-10 right-0 top-0 bottom-0">
          <svg className="w-full h-full" preserveAspectRatio="none">
            {/* Area fill */}
            <defs>
              <linearGradient id={`gradient-${modelType}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" className={`text-${color}-500`} stopColor="currentColor" stopOpacity="0.3" />
                <stop offset="100%" className={`text-${color}-500`} stopColor="currentColor" stopOpacity="0" />
              </linearGradient>
            </defs>
            
            {/* Area */}
            <path
              d={`
                M 0 ${100 - 100}
                ${curvePoints.map((p, i) => `L ${(p.month / 24) * 100}% ${100 - p.rate}%`).join(' ')}
                L 100% 100%
                L 0 100%
                Z
              `}
              fill={`url(#gradient-${modelType})`}
            />
            
            {/* Line */}
            <path
              d={`
                M 0 ${100 - 100}%
                ${curvePoints.map((p, i) => `L ${(p.month / 24) * 100}% ${100 - p.rate}%`).join(' ')}
              `}
              fill="none"
              className={`stroke-${color}-500`}
              stroke="currentColor"
              strokeWidth="2"
            />
          </svg>

          {/* Milestone points */}
          {milestones.map((month) => {
            const point = curvePoints.find(p => p.month === month);
            if (!point) return null;
            
            return (
              <div
                key={month}
                className={`absolute w-3 h-3 bg-${color}-500 rounded-full border-2 border-slate-800 transform -translate-x-1/2 translate-y-1/2`}
                style={{
                  left: `${(month / 24) * 100}%`,
                  bottom: `${point.rate}%`,
                }}
              >
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-1 text-xs text-slate-300 whitespace-nowrap">
                  {point.rate.toFixed(0)}%
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* X-axis labels */}
      <div className="flex justify-between text-xs text-slate-500 pl-10">
        <span>M1</span>
        <span>M6</span>
        <span>M12</span>
        <span>M18</span>
        <span>M24</span>
      </div>

      {/* Retention milestones */}
      <div className="grid grid-cols-4 gap-2 mt-4 pt-4 border-t border-slate-700">
        {milestones.map((month) => (
          <div key={month} className="text-center">
            <div className="text-slate-400 text-xs mb-1">Month {month}</div>
            <div className={`text-${color}-400 font-semibold`}>
              {(((curve as Record<number, number>)[month] || 0) * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>

      {/* Comparison with other curves */}
      {showComparison && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <h4 className="text-sm font-medium text-slate-300 mb-2">Compare with other models:</h4>
          <div className="grid grid-cols-4 gap-2 text-xs">
            {(Object.keys(CONFIG.RETENTION_CURVES) as Array<keyof typeof CONFIG.RETENTION_CURVES>)
              .filter(type => type !== curveKey)
              .map((type) => (
                <button
                  key={type}
                  className={`p-2 rounded border border-slate-600 bg-slate-700/50 hover:bg-slate-600/50 transition-all`}
                >
                  <div className={`text-${CURVE_COLORS[type as RetentionModelType] || 'slate'}-400 font-medium`}>
                    {CURVE_NAMES[type as RetentionModelType] || type}
                  </div>
                  <div className="text-slate-400 mt-1">
                    M12: {((CONFIG.RETENTION_CURVES[type][12] || 0) * 100).toFixed(0)}%
                  </div>
                </button>
              ))}
          </div>
        </div>
      )}

      <p className="text-xs text-slate-500 mt-4">
        Industry benchmarks from App Annie, AppsFlyer, and Adjust 2024 reports.
        Actual retention may vary based on product-market fit and engagement features.
      </p>
    </div>
  );
};

export default RetentionCurveChart;

