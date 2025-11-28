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

      {/* Interpretation Guide */}
      <div className="bg-slate-50 rounded-xl p-5">
        <h3 className="font-semibold text-slate-800 mb-4">📖 Metrics Guide</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
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
            <h4 className="font-medium text-slate-700 mb-2">Value Accrual Grade</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-emerald-600">A (80+):</span> Excellent</li>
              <li>• <span className="text-blue-600">B (60-79):</span> Good</li>
              <li>• <span className="text-amber-600">C (40-59):</span> Moderate</li>
              <li>• <span className="text-red-600">D/F (&lt;40):</span> Weak</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

