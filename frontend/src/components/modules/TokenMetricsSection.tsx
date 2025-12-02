'use client';

import React from 'react';
import { SimulationResult, TokenMetricsResult } from '@/types/simulation';

interface TokenMetricsSectionProps {
  result: SimulationResult;
}

export function TokenMetricsSection({ result }: TokenMetricsSectionProps) {
  const metrics = result.tokenMetrics;

  if (!metrics) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-4">
          📊 Token Metrics
        </h2>
        <div className="text-center py-8 text-slate-400">
          <div className="text-4xl mb-3">📉</div>
          <p>Token metrics not available</p>
        </div>
      </div>
    );
  }

  // Safely destructure with defaults
  const velocity = metrics.velocity || {
    velocity: 0,
    annualizedVelocity: 0,
    daysToTurnover: 0,
    transactionVolume: 0,
    healthScore: 0,
    interpretation: 'N/A'
  };
  
  const realYield = metrics.realYield || {
    monthlyRealYield: 0,
    annualRealYield: 0,
    yieldPer1000Usd: 0,
    protocolRevenue: 0,
    stakedValueUsd: 0,
    isSustainable: false,
    interpretation: 'N/A'
  };
  
  const valueAccrual = metrics.valueAccrual || {
    totalScore: 0,
    grade: 'F',
    breakdown: {},
    weights: {},
    interpretation: 'N/A'
  };
  
  const overallHealth = metrics.overallHealth ?? 0;

  // Overall health color
  const healthColor = overallHealth >= 70 ? 'text-emerald-500' : overallHealth >= 40 ? 'text-amber-500' : 'text-red-500';
  const healthBg = overallHealth >= 70 ? 'bg-emerald-50 border-emerald-200' : overallHealth >= 40 ? 'bg-amber-50 border-amber-200' : 'bg-red-50 border-red-200';

  // Grade color
  const gradeColors: Record<string, string> = {
    'A': 'text-emerald-600 bg-emerald-50',
    'B': 'text-blue-600 bg-blue-50',
    'C': 'text-amber-600 bg-amber-50',
    'D': 'text-orange-600 bg-orange-50',
    'F': 'text-red-600 bg-red-50',
  };

  return (
    <div className="space-y-6">
      {/* Header with Overall Health */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            📊 Token Metrics
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Advanced tokenomics health indicators
          </p>
        </div>
        <div className={`px-5 py-3 rounded-xl border ${healthBg}`}>
          <div className={`text-3xl font-bold ${healthColor}`}>
            {(overallHealth ?? 0).toFixed(0)}
          </div>
          <div className="text-xs text-slate-500 text-center">Overall Health</div>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        {/* Token Velocity */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
              ⚡ Token Velocity
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
              (velocity.healthScore ?? 0) >= 70 ? 'bg-emerald-100 text-emerald-700' :
              (velocity.healthScore ?? 0) >= 40 ? 'bg-amber-100 text-amber-700' :
              'bg-red-100 text-red-700'
            }`}>
              {velocity.healthScore ?? 0}/100
            </span>
          </div>

          <div className="text-center mb-4">
            <div className="text-4xl font-bold text-slate-800">
              {(velocity.velocity ?? 0).toFixed(2)}
            </div>
            <div className="text-sm text-slate-500">{velocity.interpretation ?? 'N/A'}</div>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Annualized</span>
              <span className="font-medium">{(velocity.annualizedVelocity ?? 0).toFixed(2)}x</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Days to Turnover</span>
              <span className="font-medium">{(velocity.daysToTurnover ?? 0) > 0 ? (velocity.daysToTurnover ?? 0).toFixed(0) : '∞'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">TX Volume</span>
              <span className="font-medium">{((velocity.transactionVolume ?? 0) / 1_000_000).toFixed(2)}M</span>
            </div>
          </div>

          <div className="mt-4 pt-4 border-t border-slate-100">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400">Optimal Range</span>
              <span className="text-slate-500">1.0 - 3.0</span>
            </div>
            <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${
                  (velocity.velocity ?? 0) >= 1 && (velocity.velocity ?? 0) <= 3 ? 'bg-emerald-400' :
                  (velocity.velocity ?? 0) < 1 ? 'bg-blue-400' : 'bg-amber-400'
                }`}
                style={{ width: `${Math.min(100, ((velocity.velocity ?? 0) / 5) * 100)}%` }}
              />
            </div>
          </div>
        </div>

        {/* Real Yield */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
              💰 Real Yield
            </h3>
            <span className={`px-2 py-1 text-xs font-medium rounded-full ${
              realYield.isSustainable ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'
            }`}>
              {realYield.isSustainable ? 'Sustainable' : 'Emission-Backed'}
            </span>
          </div>

          <div className="text-center mb-4">
            <div className="text-4xl font-bold text-slate-800">
              {(realYield.annualRealYield ?? 0).toFixed(2)}%
            </div>
            <div className="text-sm text-slate-500">Annual Real Yield</div>
          </div>

          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">Monthly Yield</span>
              <span className="font-medium">{(realYield.monthlyRealYield ?? 0).toFixed(3)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Per $1,000 Staked</span>
              <span className="font-medium">${(realYield.yieldPer1000Usd ?? 0).toFixed(2)}/mo</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Protocol Revenue</span>
              <span className="font-medium">${(realYield.protocolRevenue ?? 0).toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Staked Value</span>
              <span className="font-medium">${((realYield.stakedValueUsd ?? 0) / 1_000).toFixed(0)}K</span>
            </div>
          </div>

          <div className="mt-4 p-3 bg-slate-50 rounded-lg">
            <p className="text-xs text-slate-500">{realYield.interpretation ?? 'N/A'}</p>
          </div>
        </div>

        {/* Value Accrual */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-slate-800 flex items-center gap-2">
              📈 Value Accrual
            </h3>
            <span className={`px-3 py-1 text-lg font-bold rounded-lg ${gradeColors[valueAccrual.grade ?? 'F'] || 'bg-slate-100 text-slate-600'}`}>
              {valueAccrual.grade ?? 'F'}
            </span>
          </div>

          <div className="text-center mb-4">
            <div className="text-4xl font-bold text-slate-800">
              {(valueAccrual.totalScore ?? 0).toFixed(0)}
            </div>
            <div className="text-sm text-slate-500">{valueAccrual.interpretation ?? 'N/A'}</div>
          </div>

          {/* Component Breakdown */}
          <div className="space-y-2">
            {Object.entries(valueAccrual.breakdown || {}).map(([key, score]) => {
              const numScore = typeof score === 'number' ? score : 0;
              return (
                <div key={key} className="flex items-center gap-2">
                  <div className="w-20 text-xs text-slate-500 capitalize">{key}</div>
                  <div className="flex-1 h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div 
                      className={`h-full rounded-full ${
                        numScore >= 70 ? 'bg-emerald-400' :
                        numScore >= 40 ? 'bg-amber-400' : 'bg-red-400'
                      }`}
                      style={{ width: `${numScore}%` }}
                    />
                  </div>
                  <div className="w-12 text-xs text-right text-slate-600">
                    {numScore.toFixed(0)}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Gini & Runway Section - 2025 Industry Compliance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Token Distribution (Gini) */}
        {metrics.gini && (
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                🎯 Token Distribution
              </h3>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                (metrics.gini.decentralizationScore ?? 0) >= 50 ? 'bg-emerald-100 text-emerald-700' :
                (metrics.gini.decentralizationScore ?? 0) >= 30 ? 'bg-amber-100 text-amber-700' :
                'bg-red-100 text-red-700'
              }`}>
                {(metrics.gini.decentralizationScore ?? 0).toFixed(0)}% Decentralized
              </span>
            </div>

            <div className="text-center mb-4">
              <div className="text-4xl font-bold text-slate-800">
                {(metrics.gini.gini ?? 0.7).toFixed(3)}
              </div>
              <div className="text-sm text-slate-500">Gini Coefficient</div>
              <div className={`text-xs mt-1 ${
                (metrics.gini.gini ?? 0.7) < 0.5 ? 'text-emerald-600' :
                (metrics.gini.gini ?? 0.7) < 0.7 ? 'text-amber-600' : 'text-red-600'
              }`}>
                {metrics.gini.interpretation ?? 'Concentrated'}
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Total Holders</span>
                <span className="font-medium">{(metrics.gini.holderCount ?? 0).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Top 1% Hold</span>
                <span className={`font-medium ${
                  (metrics.gini.top1PercentConcentration ?? 0) > 50 ? 'text-red-600' : 'text-slate-800'
                }`}>
                  {(metrics.gini.top1PercentConcentration ?? 0).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Top 10% Hold</span>
                <span className={`font-medium ${
                  (metrics.gini.top10PercentConcentration ?? 0) > 80 ? 'text-red-600' : 'text-slate-800'
                }`}>
                  {(metrics.gini.top10PercentConcentration ?? 0).toFixed(1)}%
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-100">
              <div className="flex justify-between text-xs mb-2">
                <span className="text-slate-400">Distribution Health</span>
                <span className="text-slate-500">Lower Gini = Better</span>
              </div>
              <div className="h-3 bg-gradient-to-r from-emerald-200 via-amber-200 to-red-200 rounded-full relative">
                <div 
                  className="absolute top-0 bottom-0 w-1 bg-slate-800 rounded-full transform -translate-x-1/2"
                  style={{ left: `${Math.min(100, (metrics.gini.gini ?? 0.7) * 100)}%` }}
                />
              </div>
              <div className="flex justify-between text-xs mt-1 text-slate-400">
                <span>0 (Equal)</span>
                <span>1 (Concentrated)</span>
              </div>
            </div>
          </div>
        )}

        {/* Treasury Runway */}
        {metrics.runway && (
          <div className="bg-white rounded-xl border border-slate-200 p-5">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-slate-800 flex items-center gap-2">
                🏦 Treasury Runway
              </h3>
              <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                metrics.runway.isSustainable ? 'bg-emerald-100 text-emerald-700' :
                (metrics.runway.runwayMonths ?? 0) >= 12 ? 'bg-amber-100 text-amber-700' :
                'bg-red-100 text-red-700'
              }`}>
                {metrics.runway.isSustainable ? 'Self-Sustaining' : 
                 (metrics.runway.runwayMonths ?? 0) >= 999 ? '∞' : 
                 `${(metrics.runway.runwayMonths ?? 0).toFixed(0)}mo`}
              </span>
            </div>

            <div className="text-center mb-4">
              <div className="text-4xl font-bold text-slate-800">
                {(metrics.runway.runwayMonths ?? 0) >= 999 ? '∞' : 
                 (metrics.runway.runwayYears ?? 0).toFixed(1)}
              </div>
              <div className="text-sm text-slate-500">
                {(metrics.runway.runwayMonths ?? 0) >= 999 ? 'Self-Sustaining' : 'Years Runway'}
              </div>
              <div className={`text-xs mt-1 ${
                (metrics.runway.runwayHealth ?? 0) >= 80 ? 'text-emerald-600' :
                (metrics.runway.runwayHealth ?? 0) >= 50 ? 'text-amber-600' : 'text-red-600'
              }`}>
                {metrics.runway.interpretation ?? ''}
              </div>
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-slate-500">Treasury Balance</span>
                <span className="font-medium">${((metrics.runway.treasuryBalance ?? 0) / 1000).toFixed(0)}K</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Monthly Revenue</span>
                <span className="font-medium text-emerald-600">+${(metrics.runway.monthlyRevenue ?? 0).toLocaleString()}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Monthly Expenses</span>
                <span className="font-medium text-red-600">-${(metrics.runway.monthlyExpenses ?? 0).toLocaleString()}</span>
              </div>
              <div className="flex justify-between border-t border-slate-100 pt-2 mt-2">
                <span className="text-slate-500">Net Monthly</span>
                <span className={`font-bold ${
                  (metrics.runway.netBurnMonthly ?? 0) <= 0 ? 'text-emerald-600' : 'text-red-600'
                }`}>
                  {(metrics.runway.netBurnMonthly ?? 0) <= 0 ? '+' : '-'}
                  ${Math.abs(metrics.runway.netBurnMonthly ?? 0).toLocaleString()}
                </span>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-slate-100">
              <div className="flex justify-between text-xs mb-2">
                <span className="text-slate-400">Runway Health</span>
                <span className="text-slate-500">{(metrics.runway.runwayHealth ?? 0)}/100</span>
              </div>
              <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${
                    (metrics.runway.runwayHealth ?? 0) >= 80 ? 'bg-emerald-400' :
                    (metrics.runway.runwayHealth ?? 0) >= 50 ? 'bg-amber-400' : 'bg-red-400'
                  }`}
                  style={{ width: `${metrics.runway.runwayHealth ?? 0}%` }}
                />
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Inflation Dashboard - 2025 Compliance */}
      {metrics.inflation && (
        <div className="bg-gradient-to-br from-violet-50 to-fuchsia-50 rounded-xl border border-violet-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-lg text-violet-900 flex items-center gap-2">
                📈 Inflation Dashboard
              </h3>
              <p className="text-sm text-violet-600 mt-1">
                Token supply dynamics and deflationary mechanisms
              </p>
            </div>
            <div className={`px-4 py-2 rounded-xl ${
              metrics.inflation.isDeflationary 
                ? 'bg-emerald-100 border border-emerald-300' 
                : 'bg-amber-100 border border-amber-300'
            }`}>
              <div className={`text-2xl font-bold ${
                metrics.inflation.isDeflationary ? 'text-emerald-700' : 'text-amber-700'
              }`}>
                {metrics.inflation.isDeflationary ? '📉' : '📈'} {Math.abs(metrics.inflation.annualNetInflationRate ?? 0).toFixed(2)}%
              </div>
              <div className="text-xs text-center">
                {metrics.inflation.deflationStrength ?? 'Annual Rate'}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            {/* Emission (Inflationary) */}
            <div className="bg-white/80 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center text-red-600">⬆️</span>
                <div>
                  <h4 className="font-semibold text-slate-800">Emission</h4>
                  <p className="text-xs text-slate-500">New tokens entering</p>
                </div>
              </div>
              <div className="text-2xl font-bold text-red-600 mb-2">
                +{((metrics.inflation.monthlyEmission ?? 0) / 1_000_000).toFixed(2)}M
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Monthly Value</span>
                  <span className="font-medium">${((metrics.inflation.monthlyEmissionUsd ?? 0) / 1000).toFixed(0)}K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Rate</span>
                  <span className="font-medium">{(metrics.inflation.emissionRate ?? 0).toFixed(3)}%</span>
                </div>
              </div>
            </div>

            {/* Burns & Buybacks (Deflationary) */}
            <div className="bg-white/80 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="w-8 h-8 rounded-full bg-emerald-100 flex items-center justify-center text-emerald-600">🔥</span>
                <div>
                  <h4 className="font-semibold text-slate-800">Deflationary</h4>
                  <p className="text-xs text-slate-500">Burns + Buybacks</p>
                </div>
              </div>
              <div className="text-2xl font-bold text-emerald-600 mb-2">
                -{((metrics.inflation.totalDeflationary ?? 0) / 1_000_000).toFixed(2)}M
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Burns</span>
                  <span className="font-medium text-orange-600">🔥 {((metrics.inflation.monthlyBurns ?? 0) / 1000).toFixed(0)}K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Buybacks</span>
                  <span className="font-medium text-blue-600">💰 {((metrics.inflation.monthlyBuybacks ?? 0) / 1000).toFixed(0)}K</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">USD Spent</span>
                  <span className="font-medium">${((metrics.inflation.monthlyBuybacksUsd ?? 0) / 1000).toFixed(0)}K</span>
                </div>
              </div>
            </div>

            {/* Net Result */}
            <div className="bg-white/80 rounded-xl p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className={`w-8 h-8 rounded-full flex items-center justify-center ${
                  metrics.inflation.isDeflationary 
                    ? 'bg-emerald-100 text-emerald-600' 
                    : 'bg-amber-100 text-amber-600'
                }`}>
                  {metrics.inflation.isDeflationary ? '✅' : '⚠️'}
                </span>
                <div>
                  <h4 className="font-semibold text-slate-800">Net Supply Change</h4>
                  <p className="text-xs text-slate-500">Monthly net inflation</p>
                </div>
              </div>
              <div className={`text-2xl font-bold mb-2 ${
                metrics.inflation.isDeflationary ? 'text-emerald-600' : 'text-amber-600'
              }`}>
                {metrics.inflation.isDeflationary ? '' : '+'}
                {((metrics.inflation.netMonthlyInflation ?? 0) / 1_000_000).toFixed(3)}M
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-500">Monthly %</span>
                  <span className={`font-medium ${
                    metrics.inflation.isDeflationary ? 'text-emerald-600' : 'text-amber-600'
                  }`}>
                    {(metrics.inflation.netInflationRate ?? 0).toFixed(3)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-500">Annual %</span>
                  <span className={`font-bold ${
                    metrics.inflation.isDeflationary ? 'text-emerald-600' : 'text-amber-600'
                  }`}>
                    {(metrics.inflation.annualNetInflationRate ?? 0).toFixed(2)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Supply Progress Bar */}
          <div className="bg-white/60 rounded-xl p-4">
            <div className="flex justify-between text-sm mb-2">
              <span className="text-slate-600 font-medium">Circulating Supply Progress</span>
              <span className="font-bold text-slate-800">
                {((metrics.inflation.circulatingSupply ?? 0) / (metrics.inflation.totalSupply ?? 1_000_000_000) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="h-4 bg-slate-200 rounded-full overflow-hidden mb-2">
              <div 
                className="h-full bg-gradient-to-r from-violet-400 to-fuchsia-500 rounded-full transition-all"
                style={{ 
                  width: `${Math.min(100, (metrics.inflation.circulatingSupply ?? 0) / (metrics.inflation.totalSupply ?? 1_000_000_000) * 100)}%` 
                }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-500">
              <span>{((metrics.inflation.circulatingSupply ?? 0) / 1_000_000).toFixed(0)}M Circulating</span>
              <span>{((metrics.inflation.totalSupply ?? 0) / 1_000_000).toFixed(0)}M Total Supply</span>
            </div>

            <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-slate-200">
              <div className="text-center">
                <div className="text-lg font-bold text-violet-600">
                  {metrics.inflation.monthsToMaxSupply ?? 60}
                </div>
                <div className="text-xs text-slate-500">Months to Max Supply</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-violet-600">
                  {(metrics.inflation.supplyHealthScore ?? 50).toFixed(0)}
                </div>
                <div className="text-xs text-slate-500">Supply Health Score</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-violet-600">
                  {((metrics.inflation.projectedYear5Supply ?? 0) / 1_000_000).toFixed(0)}M
                </div>
                <div className="text-xs text-slate-500">Year 5 Projection</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Interpretation Guide */}
      <div className="bg-slate-50 rounded-xl p-5">
        <h3 className="font-semibold text-slate-800 mb-4">📖 Metrics Guide</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Token Velocity</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-blue-600">&lt;1.0:</span> Holding (bullish for price)</li>
              <li>• <span className="text-emerald-600">1.0-3.0:</span> Optimal usage</li>
              <li>• <span className="text-amber-600">&gt;5.0:</span> Excessive selling</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Real Yield</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-emerald-600">&gt;15%:</span> Exceptional</li>
              <li>• <span className="text-blue-600">2-15%:</span> Sustainable</li>
              <li>• <span className="text-amber-600">&lt;2%:</span> Emission-backed</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Gini Coefficient</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-emerald-600">&lt;0.5:</span> Decentralized</li>
              <li>• <span className="text-amber-600">0.5-0.7:</span> Concentrated</li>
              <li>• <span className="text-red-600">&gt;0.7:</span> Highly concentrated</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Treasury Runway</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-emerald-600">36+ mo:</span> Healthy</li>
              <li>• <span className="text-amber-600">12-36 mo:</span> Moderate</li>
              <li>• <span className="text-red-600">&lt;12 mo:</span> Critical</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Net Inflation</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-emerald-600">&lt;0%:</span> Deflationary 🔥</li>
              <li>• <span className="text-blue-600">0-1%:</span> Low inflation</li>
              <li>• <span className="text-amber-600">1-5%:</span> Moderate</li>
              <li>• <span className="text-red-600">&gt;5%:</span> High inflation</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

