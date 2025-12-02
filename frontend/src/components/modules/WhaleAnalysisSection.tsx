'use client';

import React, { useState } from 'react';
import { SimulationResult, WhaleAnalysisResult, DumpScenarioResult } from '@/types/simulation';

interface WhaleAnalysisSectionProps {
  result: SimulationResult;
}

export function WhaleAnalysisSection({ result }: WhaleAnalysisSectionProps) {
  const [selectedScenario, setSelectedScenario] = useState<number>(0);
  const whaleData = result.tokenMetrics?.whaleAnalysis;

  if (!whaleData) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-4">
          🐋 Whale Analysis
        </h2>
        <div className="text-center py-8 text-slate-400">
          <div className="text-4xl mb-3">🔍</div>
          <p>Whale analysis not available</p>
        </div>
      </div>
    );
  }

  const riskColors: Record<string, string> = {
    emerald: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    amber: 'bg-amber-100 text-amber-800 border-amber-300',
    orange: 'bg-orange-100 text-orange-800 border-orange-300',
    red: 'bg-red-100 text-red-800 border-red-300',
    gray: 'bg-slate-100 text-slate-800 border-slate-300',
  };

  const severityColors: Record<string, string> = {
    low: 'bg-emerald-100 text-emerald-700',
    medium: 'bg-amber-100 text-amber-700',
    high: 'bg-orange-100 text-orange-700',
    critical: 'bg-red-100 text-red-700',
  };

  const scenario = whaleData.dumpScenarios?.[selectedScenario];

  return (
    <div className="space-y-6">
      {/* Header with Risk Score */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            🐋 Whale Concentration Analysis
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Token distribution risk assessment and dump scenario modeling
          </p>
        </div>
        <div className={`px-5 py-3 rounded-xl border ${riskColors[whaleData.riskColor || 'gray']}`}>
          <div className="text-3xl font-bold">
            {(whaleData.concentrationRiskScore ?? 0).toFixed(0)}
          </div>
          <div className="text-xs text-center">{whaleData.riskLevel ?? 'Unknown'} Risk</div>
        </div>
      </div>

      {/* Holder Distribution Overview */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-4 border border-purple-200">
          <div className="text-3xl font-bold text-purple-700">
            {(whaleData.whaleCount ?? 0).toLocaleString()}
          </div>
          <div className="text-sm text-purple-600">🐋 Whales (≥1%)</div>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
          <div className="text-3xl font-bold text-blue-700">
            {(whaleData.largeHolderCount ?? 0).toLocaleString()}
          </div>
          <div className="text-sm text-blue-600">🦈 Large (0.1-1%)</div>
        </div>
        <div className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-xl p-4 border border-cyan-200">
          <div className="text-3xl font-bold text-cyan-700">
            {(whaleData.mediumHolderCount ?? 0).toLocaleString()}
          </div>
          <div className="text-sm text-cyan-600">🐟 Medium</div>
        </div>
        <div className="bg-gradient-to-br from-slate-50 to-gray-50 rounded-xl p-4 border border-slate-200">
          <div className="text-3xl font-bold text-slate-700">
            {(whaleData.smallHolderCount ?? 0).toLocaleString()}
          </div>
          <div className="text-sm text-slate-600">🐠 Small Holders</div>
        </div>
      </div>

      {/* Concentration Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Top Holder Groups */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            📊 Top Holder Concentration
          </h3>
          
          <div className="space-y-4">
            {/* Top 10 */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">Top 10 Holders</span>
                <span className={`font-bold ${
                  (whaleData.top10?.percentage ?? 0) > 50 ? 'text-red-600' :
                  (whaleData.top10?.percentage ?? 0) > 30 ? 'text-amber-600' : 'text-emerald-600'
                }`}>
                  {(whaleData.top10?.percentage ?? 0).toFixed(1)}%
                </span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${
                    (whaleData.top10?.percentage ?? 0) > 50 ? 'bg-red-400' :
                    (whaleData.top10?.percentage ?? 0) > 30 ? 'bg-amber-400' : 'bg-emerald-400'
                  }`}
                  style={{ width: `${Math.min(100, whaleData.top10?.percentage ?? 0)}%` }}
                />
              </div>
              <div className="text-xs text-slate-500 mt-1">
                ${((whaleData.top10?.amountUsd ?? 0) / 1000).toFixed(0)}K value
              </div>
            </div>

            {/* Top 50 */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">Top 50 Holders</span>
                <span className={`font-bold ${
                  (whaleData.top50?.percentage ?? 0) > 70 ? 'text-red-600' :
                  (whaleData.top50?.percentage ?? 0) > 50 ? 'text-amber-600' : 'text-emerald-600'
                }`}>
                  {(whaleData.top50?.percentage ?? 0).toFixed(1)}%
                </span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full ${
                    (whaleData.top50?.percentage ?? 0) > 70 ? 'bg-red-400' :
                    (whaleData.top50?.percentage ?? 0) > 50 ? 'bg-amber-400' : 'bg-emerald-400'
                  }`}
                  style={{ width: `${Math.min(100, whaleData.top50?.percentage ?? 0)}%` }}
                />
              </div>
            </div>

            {/* Top 100 */}
            <div>
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-600">Top 100 Holders</span>
                <span className="font-bold text-slate-800">
                  {(whaleData.top100?.percentage ?? 0).toFixed(1)}%
                </span>
              </div>
              <div className="h-3 bg-slate-100 rounded-full overflow-hidden">
                <div 
                  className="h-full rounded-full bg-blue-400"
                  style={{ width: `${Math.min(100, whaleData.top100?.percentage ?? 0)}%` }}
                />
              </div>
            </div>

            {/* Percentile breakdowns */}
            <div className="pt-4 border-t border-slate-100 grid grid-cols-3 gap-3 text-center">
              <div>
                <div className="text-lg font-bold text-slate-800">
                  {(whaleData.top1Percent?.percentage ?? 0).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-500">Top 1%</div>
              </div>
              <div>
                <div className="text-lg font-bold text-slate-800">
                  {(whaleData.top5Percent?.percentage ?? 0).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-500">Top 5%</div>
              </div>
              <div>
                <div className="text-lg font-bold text-slate-800">
                  {(whaleData.top10Percent?.percentage ?? 0).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-500">Top 10%</div>
              </div>
            </div>
          </div>
        </div>

        {/* Top Whales List */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            🏆 Top Whale Holders
          </h3>
          
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {(whaleData.whales ?? []).slice(0, 10).map((whale, idx) => (
              <div 
                key={whale.rank}
                className="flex items-center justify-between p-2 bg-slate-50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                    idx === 0 ? 'bg-yellow-100 text-yellow-700' :
                    idx === 1 ? 'bg-slate-200 text-slate-700' :
                    idx === 2 ? 'bg-orange-100 text-orange-700' :
                    'bg-slate-100 text-slate-600'
                  }`}>
                    {idx === 0 ? '🥇' : idx === 1 ? '🥈' : idx === 2 ? '🥉' : `#${whale.rank}`}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-slate-800">
                      Holder #{whale.rank}
                    </div>
                    <div className="text-xs text-slate-500">
                      {((whale.balance ?? 0) / 1000).toFixed(0)}K VCoin
                    </div>
                  </div>
                </div>
                <div className={`px-2 py-1 rounded text-xs font-bold ${
                  (whale.percentage ?? 0) >= 5 ? 'bg-red-100 text-red-700' :
                  (whale.percentage ?? 0) >= 2 ? 'bg-amber-100 text-amber-700' :
                  'bg-emerald-100 text-emerald-700'
                }`}>
                  {(whale.percentage ?? 0).toFixed(2)}%
                </div>
              </div>
            ))}
            
            {(!whaleData.whales || whaleData.whales.length === 0) && (
              <div className="text-center py-4 text-slate-400">
                No whale holders detected
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Dump Scenario Modeling */}
      <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-xl border border-red-200 p-6">
        <h3 className="font-bold text-lg text-red-900 mb-4 flex items-center gap-2">
          ⚠️ Whale Dump Scenario Modeling
        </h3>
        <p className="text-sm text-red-700 mb-4">
          Simulated price impact if major holders sell their positions
        </p>

        {/* Scenario Selector */}
        <div className="flex flex-wrap gap-2 mb-6">
          {(whaleData.dumpScenarios ?? []).map((s, idx) => (
            <button
              key={idx}
              onClick={() => setSelectedScenario(idx)}
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedScenario === idx
                  ? 'bg-red-600 text-white'
                  : 'bg-white text-red-700 hover:bg-red-100 border border-red-200'
              }`}
            >
              {s.scenarioName}
            </button>
          ))}
        </div>

        {/* Selected Scenario Details */}
        {scenario && (
          <div className="bg-white rounded-xl p-5 border border-red-200">
            <div className="flex items-center justify-between mb-4">
              <h4 className="font-bold text-slate-800">{scenario.scenarioName}</h4>
              <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                severityColors[scenario.severity] || severityColors.low
              }`}>
                {(scenario.severity ?? 'low').toUpperCase()} SEVERITY
              </span>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
              <div className="text-center p-3 bg-slate-50 rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  -{(scenario.priceImpactPercent ?? 0).toFixed(1)}%
                </div>
                <div className="text-xs text-slate-500">Price Impact</div>
              </div>
              <div className="text-center p-3 bg-slate-50 rounded-lg">
                <div className="text-2xl font-bold text-slate-800">
                  ${(scenario.newPrice ?? 0).toFixed(4)}
                </div>
                <div className="text-xs text-slate-500">New Price</div>
              </div>
              <div className="text-center p-3 bg-slate-50 rounded-lg">
                <div className="text-2xl font-bold text-amber-600">
                  {scenario.recoveryDaysEstimate ?? 0}
                </div>
                <div className="text-xs text-slate-500">Recovery Days</div>
              </div>
              <div className="text-center p-3 bg-slate-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">
                  {(scenario.liquidityAbsorbedPercent ?? 0).toFixed(0)}%
                </div>
                <div className="text-xs text-slate-500">Liquidity Used</div>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex justify-between p-2 bg-slate-50 rounded">
                <span className="text-slate-500">Sellers</span>
                <span className="font-medium">{scenario.sellersCount ?? 0} holders</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-50 rounded">
                <span className="text-slate-500">Sell %</span>
                <span className="font-medium">{scenario.sellPercentage ?? 0}% of holdings</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-50 rounded">
                <span className="text-slate-500">Sell Amount</span>
                <span className="font-medium">{((scenario.sellAmountVcoin ?? 0) / 1_000_000).toFixed(2)}M VCoin</span>
              </div>
              <div className="flex justify-between p-2 bg-slate-50 rounded">
                <span className="text-slate-500">USD Value</span>
                <span className="font-medium">${((scenario.sellAmountUsd ?? 0) / 1000).toFixed(0)}K</span>
              </div>
            </div>

            {/* Price Impact Visualization */}
            <div className="mt-4 pt-4 border-t border-slate-200">
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="flex justify-between text-xs text-slate-500 mb-1">
                    <span>Current</span>
                    <span>After Dump</span>
                  </div>
                  <div className="h-4 bg-slate-200 rounded-full overflow-hidden relative">
                    <div 
                      className="absolute inset-y-0 left-0 bg-gradient-to-r from-emerald-400 to-red-400 rounded-full"
                      style={{ width: `${100 - (scenario.priceImpactPercent ?? 0)}%` }}
                    />
                    <div 
                      className="absolute inset-y-0 right-0 bg-red-500 rounded-r-full"
                      style={{ width: `${scenario.priceImpactPercent ?? 0}%` }}
                    />
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-lg font-bold text-red-600">
                    -${((scenario.marketCapLoss ?? 0) / 1_000_000).toFixed(2)}M
                  </div>
                  <div className="text-xs text-slate-500">Market Cap Loss</div>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {whaleData.recommendations && whaleData.recommendations.length > 0 && (
        <div className="bg-blue-50 rounded-xl border border-blue-200 p-5">
          <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
            💡 Risk Mitigation Recommendations
          </h3>
          <ul className="space-y-2">
            {whaleData.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-blue-800">
                <span className="text-blue-500 mt-0.5">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Interpretation Guide */}
      <div className="bg-slate-50 rounded-xl p-5">
        <h3 className="font-semibold text-slate-800 mb-4">📖 Whale Analysis Guide</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Concentration Risk</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-emerald-600">0-40:</span> Low risk, well distributed</li>
              <li>• <span className="text-amber-600">40-60:</span> Moderate concentration</li>
              <li>• <span className="text-orange-600">60-80:</span> High risk, monitor closely</li>
              <li>• <span className="text-red-600">80+:</span> Critical, action needed</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Healthy Benchmarks</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• Top 10 holders: &lt;30%</li>
              <li>• Top 50 holders: &lt;50%</li>
              <li>• Whale count: 10-50</li>
              <li>• No single holder &gt;5%</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Dump Severity</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-emerald-600">Low:</span> &lt;15% price impact</li>
              <li>• <span className="text-amber-600">Medium:</span> 15-30% impact</li>
              <li>• <span className="text-orange-600">High:</span> 30-50% impact</li>
              <li>• <span className="text-red-600">Critical:</span> &gt;50% impact</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

