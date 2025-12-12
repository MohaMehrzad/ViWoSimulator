'use client';

import React, { useState } from 'react';
import { MonthlyProgressionResult, MonthlyMetrics, FomoEvent } from '@/types/simulation';
import { DEFAULT_PARAMETERS } from '@/lib/constants';

// NEW-LOW-003 FIX: Use constant for default token price
const DEFAULT_TOKEN_PRICE = DEFAULT_PARAMETERS.tokenPrice;

interface MonthlyProgressionChartProps {
  result: MonthlyProgressionResult;
}

type MetricType = 'users' | 'financials' | 'tokens' | 'retention' | 'price' | 'allocation';

const formatCurrency = (value: number): string => {
  if (value >= 1000000000000) return `$${(value / 1000000000000).toFixed(2)}T`;
  if (value >= 1000000000) return `$${(value / 1000000000).toFixed(2)}B`;
  if (value >= 1000000) return `$${(value / 1000000).toFixed(2)}M`;
  if (value >= 1000) return `$${(value / 1000).toFixed(1)}K`;
  return `$${value.toFixed(0)}`;
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

// FOMO event icons
const FOMO_ICONS: Record<string, string> = {
  tge_launch: '🚀',
  partnership: '🤝',
  viral_moment: '🔥',
  exchange_listing: '📊',
  influencer: '⭐',
  holiday: '🎄',
  feature_launch: '✨',
  milestone: '🏆',
};

export const MonthlyProgressionChart: React.FC<MonthlyProgressionChartProps> = ({ result }) => {
  const [metricType, setMetricType] = useState<MetricType>('users');
  const [showCumulative, setShowCumulative] = useState(false);

  const { monthlyData, cumulativeProfitCurve, growthProjection, scenarioUsed, fomoEventsTriggered } = result;

  // Calculate max values for scaling
  const maxUsers = Math.max(...monthlyData.map(m => m.activeUsers));
  const maxRevenue = Math.max(...monthlyData.map(m => m.revenue));
  const maxTokens = Math.max(...monthlyData.map(m => m.tokensDistributed));
  const maxPrice = Math.max(...monthlyData.map(m => m.tokenPrice || DEFAULT_TOKEN_PRICE));
  const maxAllocation = 90; // Max allocation is always 90%
  
  // Check if dynamic allocation is being used
  const hasDynamicAllocation = monthlyData.some(m => (m.dynamicAllocationPercent || 0) > 0);
  
  // Check if growth scenarios are enabled
  const hasGrowthScenario = scenarioUsed != null && growthProjection != null;
  
  // Get FOMO event for a specific month
  const getFomoEventForMonth = (month: number): FomoEvent | undefined => {
    if (!fomoEventsTriggered) return undefined;
    return fomoEventsTriggered.find(e => e.month === month);
  };

  const getBarHeight = (value: number, max: number): string => {
    return `${Math.max(5, (value / max) * 100)}%`;
  };

  const renderBars = () => {
    return monthlyData.map((month, index) => {
      let primaryValue: number;
      let secondaryValue: number;
      let primaryLabel: string;
      let secondaryLabel: string;
      let primaryColor: string;
      let secondaryColor: string;
      let maxValue: number;
      
      // Get FOMO event for this month
      const fomoEvent = getFomoEventForMonth(month.month);

      switch (metricType) {
        case 'users':
          primaryValue = month.activeUsers;
          secondaryValue = month.usersAcquired;
          primaryLabel = 'Active';
          secondaryLabel = 'Acquired';
          primaryColor = 'bg-emerald-500';
          secondaryColor = 'bg-emerald-300/50';
          maxValue = maxUsers;
          break;
        case 'financials':
          primaryValue = month.revenue;
          secondaryValue = month.costs;
          primaryLabel = 'Revenue';
          secondaryLabel = 'Costs';
          primaryColor = month.profit >= 0 ? 'bg-emerald-500' : 'bg-red-500';
          secondaryColor = 'bg-slate-500';
          maxValue = maxRevenue;
          break;
        case 'tokens':
          primaryValue = month.tokensDistributed;
          secondaryValue = month.tokensRecaptured;
          primaryLabel = 'Distributed';
          secondaryLabel = 'Recaptured';
          primaryColor = 'bg-amber-500';
          secondaryColor = 'bg-amber-300/50';
          maxValue = maxTokens;
          break;
        case 'retention':
          primaryValue = month.retentionRate;
          secondaryValue = 0;
          primaryLabel = 'Retention %';
          secondaryLabel = '';
          primaryColor = 'bg-purple-500';
          secondaryColor = '';
          maxValue = 100;
          break;
        case 'price':
          primaryValue = month.tokenPrice || DEFAULT_TOKEN_PRICE;
          secondaryValue = 0;
          primaryLabel = 'Token Price';
          secondaryLabel = '';
          primaryColor = 'bg-amber-500';
          secondaryColor = '';
          maxValue = maxPrice;
          break;
        case 'allocation':
          primaryValue = month.dynamicAllocationPercent || 0;
          secondaryValue = month.perUserMonthlyUsd || 0;
          primaryLabel = 'Allocation %';
          secondaryLabel = '$/User';
          primaryColor = month.allocationCapped ? 'bg-red-500' : 'bg-purple-500';
          secondaryColor = 'bg-indigo-400/50';
          maxValue = maxAllocation;
          break;
        default:
          return null;
      }

      return (
        <div key={month.month} className="flex-1 flex flex-col items-center group relative">
          {/* FOMO Event Marker */}
          {fomoEvent && (
            <div className="absolute -top-6 z-20 text-lg animate-bounce" title={fomoEvent.description}>
              {FOMO_ICONS[fomoEvent.eventType] || '⚡'}
            </div>
          )}
          
          <div className="w-full h-32 flex items-end gap-0.5 px-0.5">
            {secondaryValue > 0 && (
              <div
                className={`flex-1 ${secondaryColor} rounded-t transition-all opacity-50 group-hover:opacity-80`}
                style={{ height: getBarHeight(secondaryValue, maxValue) }}
              />
            )}
            <div
              className={`flex-1 ${primaryColor} rounded-t transition-all group-hover:opacity-80 ${
                fomoEvent ? 'ring-2 ring-amber-400 ring-offset-1 ring-offset-slate-800' : ''
              }`}
              style={{ height: getBarHeight(primaryValue, maxValue) }}
            />
          </div>
          <span className="text-[9px] text-slate-500 mt-1">{month.month}</span>
          
          {/* Tooltip */}
          <div className="absolute bottom-full mb-8 left-1/2 -translate-x-1/2 bg-slate-800 border border-slate-600 rounded-lg p-2 text-xs opacity-0 group-hover:opacity-100 transition-opacity z-10 whitespace-nowrap pointer-events-none shadow-xl">
            <div className="font-semibold text-white mb-1">Month {month.month}</div>
            <div className="text-slate-300">
              {primaryLabel}: <span className="text-emerald-400">
                {metricType === 'financials' ? formatCurrency(primaryValue) : 
                 metricType === 'retention' ? `${primaryValue.toFixed(1)}%` :
                 metricType === 'price' ? formatPrice(primaryValue) :
                 formatNumber(primaryValue)}
              </span>
            </div>
            {secondaryValue > 0 && (
              <div className="text-slate-400">
                {secondaryLabel}: {metricType === 'financials' ? formatCurrency(secondaryValue) : formatNumber(secondaryValue)}
              </div>
            )}
            {metricType === 'financials' && (
              <div className={`mt-1 ${month.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                Profit: {formatCurrency(month.profit)}
              </div>
            )}
            {month.tokenPrice && metricType !== 'price' && (
              <div className="text-amber-400 mt-1">
                Price: {formatPrice(month.tokenPrice)}
              </div>
            )}
            {month.growthRate !== undefined && month.growthRate !== 0 && (
              <div className={`mt-1 ${month.growthRate >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                Growth: {month.growthRate > 0 ? '+' : ''}{month.growthRate.toFixed(1)}%
              </div>
            )}
            {month.dynamicAllocationPercent !== undefined && month.dynamicAllocationPercent > 0 && (
              <div className="mt-1 text-purple-400">
                Allocation: {month.dynamicAllocationPercent.toFixed(1)}%
                {month.allocationCapped && <span className="text-red-400 ml-1">(capped)</span>}
              </div>
            )}
            {month.perUserMonthlyUsd !== undefined && month.perUserMonthlyUsd > 0 && (
              <div className="text-indigo-400">
                ${month.perUserMonthlyUsd.toFixed(2)}/user/mo
              </div>
            )}
            {fomoEvent && (
              <div className="mt-2 pt-2 border-t border-slate-700 text-amber-400">
                ⚡ {fomoEvent.description}
                <div className="text-slate-500 text-[10px]">
                  Impact: {fomoEvent.impactMultiplier}x
                </div>
              </div>
            )}
          </div>
        </div>
      );
    });
  };

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <h3 className="text-lg font-semibold text-white">Monthly Progression</h3>
          {hasGrowthScenario && scenarioUsed && (
            <span className={`px-2 py-0.5 text-xs rounded-full ${
              scenarioUsed === 'bullish' ? 'bg-emerald-500/20 text-emerald-400' :
              scenarioUsed === 'conservative' ? 'bg-blue-500/20 text-blue-400' :
              'bg-purple-500/20 text-purple-400'
            }`}>
              {scenarioUsed.charAt(0).toUpperCase() + scenarioUsed.slice(1)} Scenario
            </span>
          )}
          {fomoEventsTriggered && fomoEventsTriggered.length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded-full bg-amber-500/20 text-amber-400">
              ⚡ {fomoEventsTriggered.length} FOMO Events
            </span>
          )}
        </div>
        <div className="flex gap-1">
          {([
            'users', 
            'financials', 
            'tokens', 
            'retention', 
            ...(hasGrowthScenario ? ['price' as MetricType] : []),
            ...(hasDynamicAllocation ? ['allocation' as MetricType] : [])
          ] as MetricType[]).map((type) => (
            <button
              key={type}
              onClick={() => setMetricType(type)}
              className={`px-3 py-1 text-xs rounded-lg transition-all ${
                metricType === type
                  ? type === 'price' ? 'bg-amber-500 text-white' 
                  : type === 'allocation' ? 'bg-purple-500 text-white'
                  : 'bg-emerald-500 text-white'
                  : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
              }`}
            >
              {type === 'price' ? '💰 Price' : 
               type === 'allocation' ? '🎯 Allocation' :
               type.charAt(0).toUpperCase() + type.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Chart */}
      <div className="flex items-end gap-1 h-40 mb-4">
        {renderBars()}
      </div>

      {/* Legend */}
      <div className="flex justify-center gap-4 text-xs text-slate-400">
        {metricType === 'users' && (
          <>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-emerald-500 rounded"></span> Active Users
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-emerald-300/50 rounded"></span> Acquired
            </span>
          </>
        )}
        {metricType === 'financials' && (
          <>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-emerald-500 rounded"></span> Revenue
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-slate-500 rounded"></span> Costs
            </span>
          </>
        )}
        {metricType === 'price' && (
          <>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-amber-500 rounded"></span> Token Price (USD)
            </span>
          </>
        )}
        {metricType === 'allocation' && (
          <>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-purple-500 rounded"></span> Dynamic Allocation %
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-indigo-400/50 rounded"></span> USD/User/Month
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 bg-red-500 rounded"></span> Capped
            </span>
          </>
        )}
        {hasGrowthScenario && fomoEventsTriggered && fomoEventsTriggered.length > 0 && (
          <span className="flex items-center gap-1">
            <span className="text-lg">⚡</span> FOMO Events
          </span>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mt-4 pt-4 border-t border-slate-700">
        <div className="text-center">
          <div className="text-slate-400 text-xs mb-1">Total Acquired</div>
          <div className="text-white font-semibold">{formatNumber(result.totalUsersAcquired)}</div>
        </div>
        <div className="text-center">
          <div className="text-slate-400 text-xs mb-1">Peak Active</div>
          <div className="text-emerald-400 font-semibold">{formatNumber(result.peakActiveUsers)}</div>
        </div>
        <div className="text-center">
          <div className="text-slate-400 text-xs mb-1">Final Active</div>
          <div className="text-white font-semibold">{formatNumber(result.finalActiveUsers)}</div>
        </div>
        <div className="text-center">
          <div className="text-slate-400 text-xs mb-1">Avg Retention</div>
          <div className="text-purple-400 font-semibold">{result.averageRetentionRate.toFixed(1)}%</div>
        </div>
        <div className="text-center">
          <div className="text-slate-400 text-xs mb-1">Total Revenue</div>
          <div className="text-emerald-400 font-semibold">{formatCurrency(result.totalRevenue)}</div>
        </div>
        <div className="text-center">
          <div className="text-slate-400 text-xs mb-1">Total Profit</div>
          <div className={`font-semibold ${result.totalProfit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {formatCurrency(result.totalProfit)}
          </div>
        </div>
        <div className="text-center">
          <div className="text-slate-400 text-xs mb-1">User CAGR</div>
          <div className="text-white font-semibold">{result.cagrUsers.toFixed(1)}%</div>
        </div>
        <div className="text-center">
          <div className="text-slate-400 text-xs mb-1">Profitability</div>
          <div className={`font-semibold ${result.monthsToProfitability ? 'text-emerald-400' : 'text-amber-400'}`}>
            {result.monthsToProfitability ? `Month ${result.monthsToProfitability}` : 'Not yet'}
          </div>
        </div>
      </div>

      {/* Cumulative Profit Curve */}
      <div className="mt-4 pt-4 border-t border-slate-700">
        <h4 className="text-sm font-medium text-slate-300 mb-2">Cumulative Profit</h4>
        <div className="flex items-center gap-1 h-16">
          {cumulativeProfitCurve.map((profit, index) => {
            const maxProfit = Math.max(...cumulativeProfitCurve.map(Math.abs));
            const height = maxProfit > 0 ? (Math.abs(profit) / maxProfit) * 100 : 0;
            const isPositive = profit >= 0;
            
            return (
              <div
                key={index}
                className={`flex-1 rounded-sm transition-all ${
                  isPositive ? 'bg-emerald-500' : 'bg-red-500'
                }`}
                style={{
                  height: `${Math.max(2, height)}%`,
                  marginTop: isPositive ? 'auto' : 0,
                  marginBottom: isPositive ? 0 : 'auto',
                }}
              />
            );
          })}
        </div>
        <div className="flex justify-between text-xs text-slate-500 mt-1">
          <span>Month 1</span>
          <span>Month {result.durationMonths}</span>
        </div>
      </div>

      {/* Dynamic Allocation Summary (when enabled) */}
      {hasDynamicAllocation && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
            🎯 Dynamic Reward Allocation
            <span className="px-2 py-0.5 text-xs rounded-full bg-purple-500/20 text-purple-400">
              User-Growth Based
            </span>
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Month 1 Allocation</div>
              <div className="text-purple-400 font-semibold">
                {(monthlyData[0]?.dynamicAllocationPercent || 0).toFixed(1)}%
              </div>
            </div>
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Final Allocation</div>
              <div className="text-purple-400 font-semibold">
                {(monthlyData[monthlyData.length - 1]?.dynamicAllocationPercent || 0).toFixed(1)}%
              </div>
            </div>
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Growth Factor</div>
              <div className="text-indigo-400 font-semibold">
                {((monthlyData[monthlyData.length - 1]?.dynamicGrowthFactor || 0) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Avg $/User/Mo</div>
              <div className="text-emerald-400 font-semibold">
                ${(monthlyData.reduce((sum, m) => sum + (m.perUserMonthlyUsd || 0), 0) / monthlyData.length).toFixed(2)}
              </div>
            </div>
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Months Capped</div>
              <div className={`font-semibold ${monthlyData.filter(m => m.allocationCapped).length > 0 ? 'text-amber-400' : 'text-emerald-400'}`}>
                {monthlyData.filter(m => m.allocationCapped).length} / {monthlyData.length}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Growth Scenario Summary (when enabled) */}
      {hasGrowthScenario && growthProjection && (
        <div className="mt-4 pt-4 border-t border-slate-700">
          <h4 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
            📈 Growth Scenario Analysis
            <span className={`px-2 py-0.5 text-xs rounded-full ${
              scenarioUsed === 'bullish' ? 'bg-emerald-500/20 text-emerald-400' :
              scenarioUsed === 'conservative' ? 'bg-blue-500/20 text-blue-400' :
              'bg-purple-500/20 text-purple-400'
            }`}>
              {result.marketConditionUsed?.charAt(0).toUpperCase()}{result.marketConditionUsed?.slice(1)} Market
            </span>
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Waitlist Conversion</div>
              <div className="text-emerald-400 font-semibold">
                {(growthProjection.waitlistConversionRate * 100).toFixed(0)}%
              </div>
            </div>
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Month 1 FOMO</div>
              <div className="text-amber-400 font-semibold">
                {growthProjection.month1FomoMultiplier}x
              </div>
            </div>
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Viral Coefficient</div>
              <div className="text-purple-400 font-semibold">
                {growthProjection.viralCoefficient}
              </div>
            </div>
            <div className="bg-slate-700/30 rounded p-2 text-center">
              <div className="text-slate-400 text-xs mb-1">Price Change</div>
              <div className="text-amber-400 font-semibold">
                {formatPrice(growthProjection.tokenPriceStart)} → {formatPrice(growthProjection.tokenPriceEnd)}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default MonthlyProgressionChart;

