'use client';

import React, { useState } from 'react';
import { GrowthProjectionResult, FomoEvent, GrowthScenario } from '@/types/simulation';
import { GROWTH_SCENARIOS, GROWTH_SCENARIO_SUMMARY } from '@/lib/constants';

interface GrowthProjectionChartProps {
  result?: GrowthProjectionResult;
  showComparison?: boolean;
}

const SCENARIO_COLORS = {
  conservative: { line: '#3b82f6', bg: 'rgba(59, 130, 246, 0.1)', text: 'text-blue-400' },
  base: { line: '#a855f7', bg: 'rgba(168, 85, 247, 0.1)', text: 'text-purple-400' },
  bullish: { line: '#10b981', bg: 'rgba(16, 185, 129, 0.1)', text: 'text-emerald-400' },
};

const FOMO_EVENT_ICONS: Record<string, string> = {
  tge_launch: '🚀',
  partnership: '🤝',
  viral_moment: '🔥',
  exchange_listing: '📊',
  influencer: '⭐',
  holiday: '🎄',
  feature_launch: '✨',
  milestone: '🏆',
};

const formatNumber = (value: number): string => {
  if (value >= 1000000000000) return `${(value / 1000000000000).toFixed(2)}T`;
  if (value >= 1000000000) return `${(value / 1000000000).toFixed(2)}B`;
  if (value >= 1000000) return `${(value / 1000000).toFixed(2)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return value.toFixed(0);
};

const formatPrice = (value: number): string => {
  return `$${value.toFixed(4)}`;
};

type ViewMode = 'users' | 'price' | 'growth' | 'comparison';

export const GrowthProjectionChart: React.FC<GrowthProjectionChartProps> = ({
  result,
  showComparison = false,
}) => {
  const [viewMode, setViewMode] = useState<ViewMode>('users');
  const [hoveredMonth, setHoveredMonth] = useState<number | null>(null);

  if (!result && !showComparison) {
    return (
      <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
        <div className="text-center text-slate-400">
          <p className="text-lg mb-2">📈 Growth Projection</p>
          <p className="text-sm">Enable Growth Scenarios to see projections</p>
        </div>
      </div>
    );
  }

  // Generate comparison data if no result provided
  const comparisonData = showComparison || !result ? generateComparisonData() : null;
  const displayResult = result || comparisonData?.base;

  const maxUsers = displayResult ? Math.max(...displayResult.monthlyMau) : 10000;
  const maxPrice = displayResult ? Math.max(...displayResult.tokenPriceCurve) : 0.1;

  const getBarHeight = (value: number, max: number): string => {
    return `${Math.max(5, (value / max) * 100)}%`;
  };

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-lg font-semibold text-white">Growth Projection</h3>
          {displayResult && (
            <span className={`px-2 py-0.5 text-xs rounded-full ${
              displayResult.scenario === 'bullish' ? 'bg-emerald-500/20 text-emerald-400' :
              displayResult.scenario === 'conservative' ? 'bg-blue-500/20 text-blue-400' :
              'bg-purple-500/20 text-purple-400'
            }`}>
              {displayResult.scenario}
            </span>
          )}
        </div>
        
        {/* View Mode Toggle */}
        <div className="flex gap-1">
          {(['users', 'price', 'growth', 'comparison'] as ViewMode[]).map((mode) => (
            <button
              key={mode}
              onClick={() => setViewMode(mode)}
              className={`px-3 py-1 text-xs rounded-lg transition-all ${
                viewMode === mode
                  ? 'bg-emerald-500 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {mode === 'users' ? '👥 Users' :
               mode === 'price' ? '💰 Price' :
               mode === 'growth' ? '📈 Growth' :
               '🔄 Compare'}
            </button>
          ))}
        </div>
      </div>

      {/* Chart Area */}
      <div className="relative">
        {viewMode === 'comparison' && comparisonData ? (
          <ComparisonView data={comparisonData} />
        ) : (
          <>
            {/* Main Chart */}
            <div className="flex items-end gap-1 h-48 mb-4 relative">
              {displayResult?.monthlyMau.map((mau, index) => {
                const month = index + 1;
                const price = displayResult.tokenPriceCurve[index];
                const growthRate = displayResult.monthlyGrowthRates[index];
                const fomoEvent = displayResult.fomoEvents.find(e => e.month === month);
                
                const value = viewMode === 'users' ? mau : 
                              viewMode === 'price' ? price :
                              Math.abs(growthRate);
                const maxValue = viewMode === 'users' ? maxUsers :
                                viewMode === 'price' ? maxPrice :
                                Math.max(...displayResult.monthlyGrowthRates.map(Math.abs));

                const barColor = viewMode === 'users' ? 'bg-emerald-500' :
                                viewMode === 'price' ? 'bg-amber-500' :
                                growthRate >= 0 ? 'bg-green-500' : 'bg-red-500';

                return (
                  <div
                    key={month}
                    className="flex-1 flex flex-col items-center group relative"
                    onMouseEnter={() => setHoveredMonth(month)}
                    onMouseLeave={() => setHoveredMonth(null)}
                  >
                    {/* FOMO Event Marker */}
                    {fomoEvent && (
                      <div className="absolute -top-6 text-lg animate-bounce">
                        {FOMO_EVENT_ICONS[fomoEvent.eventType] || '⚡'}
                      </div>
                    )}
                    
                    <div className="w-full h-40 flex items-end px-0.5">
                      <div
                        className={`w-full ${barColor} rounded-t transition-all group-hover:opacity-80 ${
                          hoveredMonth === month ? 'ring-2 ring-white' : ''
                        }`}
                        style={{ height: getBarHeight(value, maxValue) }}
                      />
                    </div>
                    <span className="text-[10px] text-slate-500 mt-1">{month}</span>

                    {/* Tooltip */}
                    {hoveredMonth === month && (
                      <div className="absolute bottom-full mb-8 left-1/2 -translate-x-1/2 bg-slate-900 border border-slate-600 rounded-lg p-3 text-xs z-10 min-w-[160px] shadow-xl">
                        <div className="font-semibold text-white mb-2">Month {month}</div>
                        <div className="space-y-1">
                          <div className="flex justify-between">
                            <span className="text-slate-400">Active Users:</span>
                            <span className="text-emerald-400">{formatNumber(mau)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Token Price:</span>
                            <span className="text-amber-400">{formatPrice(price)}</span>
                          </div>
                          <div className="flex justify-between">
                            <span className="text-slate-400">Growth Rate:</span>
                            <span className={growthRate >= 0 ? 'text-green-400' : 'text-red-400'}>
                              {growthRate > 0 ? '+' : ''}{growthRate.toFixed(1)}%
                            </span>
                          </div>
                          {fomoEvent && (
                            <div className="mt-2 pt-2 border-t border-slate-700">
                              <span className="text-amber-400">
                                {FOMO_EVENT_ICONS[fomoEvent.eventType]} {fomoEvent.description}
                              </span>
                              <div className="text-slate-500 mt-1">
                                Impact: {fomoEvent.impactMultiplier}x
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="flex justify-center gap-6 text-xs text-slate-400 mb-4">
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-emerald-500 rounded"></span>
                Active Users
              </span>
              <span className="flex items-center gap-1">
                <span className="w-3 h-3 bg-amber-500 rounded"></span>
                Token Price
              </span>
              {displayResult?.fomoEvents && displayResult.fomoEvents.length > 0 && (
                <span className="flex items-center gap-1">
                  <span>⚡</span>
                  FOMO Events
                </span>
              )}
            </div>
          </>
        )}
      </div>

      {/* Summary Stats */}
      {displayResult && viewMode !== 'comparison' && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 pt-4 border-t border-slate-700">
          <div className="text-center">
            <div className="text-slate-400 text-xs mb-1">Month 1 Users</div>
            <div className="text-white font-semibold">{formatNumber(displayResult.month1Users)}</div>
          </div>
          <div className="text-center">
            <div className="text-slate-400 text-xs mb-1">Peak MAU</div>
            <div className="text-emerald-400 font-semibold">{formatNumber(displayResult.peakMau)}</div>
          </div>
          <div className="text-center">
            <div className="text-slate-400 text-xs mb-1">Final MAU</div>
            <div className="text-white font-semibold">{formatNumber(displayResult.finalMau)}</div>
          </div>
          <div className="text-center">
            <div className="text-slate-400 text-xs mb-1">Growth</div>
            <div className={`font-semibold ${displayResult.growthPercentage >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {displayResult.growthPercentage > 0 ? '+' : ''}{displayResult.growthPercentage.toFixed(1)}%
            </div>
          </div>
          <div className="text-center">
            <div className="text-slate-400 text-xs mb-1">Start Price</div>
            <div className="text-slate-300 font-semibold">{formatPrice(displayResult.tokenPriceStart)}</div>
          </div>
          <div className="text-center">
            <div className="text-slate-400 text-xs mb-1">Month 6 Price</div>
            <div className="text-amber-400 font-semibold">{formatPrice(displayResult.tokenPriceMonth6)}</div>
          </div>
          <div className="text-center">
            <div className="text-slate-400 text-xs mb-1">End Price</div>
            <div className="text-amber-400 font-semibold">{formatPrice(displayResult.tokenPriceEnd)}</div>
          </div>
          <div className="text-center">
            <div className="text-slate-400 text-xs mb-1">FOMO Events</div>
            <div className="text-purple-400 font-semibold">{displayResult.fomoEvents.length}</div>
          </div>
        </div>
      )}
    </div>
  );
};

// Comparison View Component
const ComparisonView: React.FC<{ data: Record<GrowthScenario, GrowthProjectionResult> }> = ({ data }) => {
  const scenarios: GrowthScenario[] = ['conservative', 'base', 'bullish'];
  const maxMau = Math.max(...Object.values(data).flatMap(d => d.monthlyMau));

  return (
    <div className="space-y-4">
      {/* Comparison Chart */}
      <div className="h-48 flex items-end gap-1 relative">
        {Array.from({ length: 12 }, (_, i) => i + 1).map((month) => (
          <div key={month} className="flex-1 flex gap-0.5 h-full items-end">
            {scenarios.map((s) => {
              const mau = data[s].monthlyMau[month - 1];
              const height = `${(mau / maxMau) * 100}%`;
              const color = SCENARIO_COLORS[s];
              
              return (
                <div
                  key={s}
                  className="flex-1 rounded-t transition-all hover:opacity-80"
                  style={{ 
                    height,
                    backgroundColor: color.line,
                    opacity: 0.8,
                  }}
                />
              );
            })}
          </div>
        ))}
      </div>

      {/* Month Labels */}
      <div className="flex justify-between text-[10px] text-slate-500 px-1">
        {Array.from({ length: 12 }, (_, i) => (
          <span key={i}>{i + 1}</span>
        ))}
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-4 text-xs">
        {scenarios.map((s) => (
          <span key={s} className="flex items-center gap-1">
            <span
              className="w-3 h-3 rounded"
              style={{ backgroundColor: SCENARIO_COLORS[s].line }}
            />
            <span className={SCENARIO_COLORS[s].text}>
              {GROWTH_SCENARIOS[s].name}
            </span>
          </span>
        ))}
      </div>

      {/* Comparison Table */}
      <div className="grid grid-cols-4 gap-2 text-xs mt-4 pt-4 border-t border-slate-700">
        <div className="text-slate-500">Metric</div>
        {scenarios.map((s) => (
          <div key={s} className={`text-center font-medium ${SCENARIO_COLORS[s].text}`}>
            {GROWTH_SCENARIOS[s].name}
          </div>
        ))}
        
        <div className="text-slate-400">Month 1</div>
        {scenarios.map((s) => (
          <div key={s} className="text-center text-white">{formatNumber(data[s].month1Users)}</div>
        ))}
        
        <div className="text-slate-400">Month 12</div>
        {scenarios.map((s) => (
          <div key={s} className="text-center text-white">{formatNumber(data[s].finalMau)}</div>
        ))}
        
        <div className="text-slate-400">Price (End)</div>
        {scenarios.map((s) => (
          <div key={s} className="text-center text-amber-400">{formatPrice(data[s].tokenPriceEnd)}</div>
        ))}
        
        <div className="text-slate-400">Growth</div>
        {scenarios.map((s) => (
          <div key={s} className={`text-center ${data[s].growthPercentage >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {data[s].growthPercentage > 0 ? '+' : ''}{data[s].growthPercentage.toFixed(0)}%
          </div>
        ))}
      </div>
    </div>
  );
};

// Generate comparison data from constants
function generateComparisonData(): Record<GrowthScenario, GrowthProjectionResult> {
  const scenarios: GrowthScenario[] = ['conservative', 'base', 'bullish'];
  const result: Record<string, GrowthProjectionResult> = {};

  scenarios.forEach((s) => {
    const config = GROWTH_SCENARIOS[s];
    const basePrice = config.tokenPriceStart;
    
    // Generate monthly data
    let currentUsers = Math.round(1000 * config.waitlistConversionRate * config.month1FomoMultiplier * 0.3);
    const monthlyMau: number[] = [currentUsers];
    const monthlyAcquired: number[] = [currentUsers];
    const monthlyChurned: number[] = [0];
    
    for (let i = 1; i < 12; i++) {
      const growth = config.monthlyGrowthRates[i];
      const newUsers = Math.round(currentUsers * growth);
      const churned = Math.round(currentUsers * 0.1);
      currentUsers = Math.max(0, currentUsers + newUsers - churned);
      monthlyMau.push(currentUsers);
      monthlyAcquired.push(Math.max(0, newUsers));
      monthlyChurned.push(churned);
    }

    // Generate price curve
    const tokenPriceCurve: number[] = [];
    for (let i = 0; i < 12; i++) {
      const month = i + 1;
      let multiplier: number;
      if (month <= 6) {
        const t = month / 6;
        multiplier = 1 + (config.tokenPriceMonth6Multiplier - 1) * t;
      } else {
        const t = (month - 6) / 6;
        multiplier = config.tokenPriceMonth6Multiplier + (config.tokenPriceEndMultiplier - config.tokenPriceMonth6Multiplier) * t;
      }
      tokenPriceCurve.push(basePrice * multiplier);
    }

    result[s] = {
      scenario: s,
      marketCondition: 'bull',
      startingWaitlist: 1000,
      monthlyMau,
      monthlyAcquired,
      monthlyChurned,
      monthlyGrowthRates: config.monthlyGrowthRates.map(r => r * 100),
      tokenPriceCurve,
      tokenPriceStart: basePrice,
      tokenPriceMonth6: tokenPriceCurve[5],
      tokenPriceEnd: tokenPriceCurve[11],
      fomoEvents: config.fomoEvents,
      totalUsersAcquired: monthlyAcquired.reduce((a, b) => a + b, 0),
      month1Users: monthlyMau[0],
      month6Mau: monthlyMau[5],
      finalMau: monthlyMau[11],
      peakMau: Math.max(...monthlyMau),
      growthPercentage: ((monthlyMau[11] / monthlyMau[0]) - 1) * 100,
      waitlistConversionRate: config.waitlistConversionRate,
      month1FomoMultiplier: config.month1FomoMultiplier,
      viralCoefficient: config.viralCoefficient,
    };
  });

  return result as Record<GrowthScenario, GrowthProjectionResult>;
}

export default GrowthProjectionChart;

