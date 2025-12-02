'use client';

import React, { useState } from 'react';
import { SimulationResult, LiquidityFarmingResult, FarmingSimulation } from '@/types/simulation';

interface LiquidityFarmingSectionProps {
  result: SimulationResult;
}

export function LiquidityFarmingSection({ result }: LiquidityFarmingSectionProps) {
  const [selectedScenario, setSelectedScenario] = useState<string>('stable_case');
  const farmingData = result.tokenMetrics?.liquidityFarming;

  if (!farmingData) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-4">
          🌾 Liquidity Farming
        </h2>
        <div className="text-center py-8 text-slate-400">
          <div className="text-4xl mb-3">💧</div>
          <p>Liquidity farming data not available</p>
        </div>
      </div>
    );
  }

  const simulation = farmingData.simulations?.[selectedScenario];
  const finalResult = simulation?.finalResult;

  const scenarioLabels: Record<string, { label: string; icon: string; color: string }> = {
    bull_case: { label: 'Bull Market (+100%)', icon: '📈', color: 'emerald' },
    bear_case: { label: 'Bear Market (-50%)', icon: '📉', color: 'red' },
    stable_case: { label: 'Stable Market', icon: '➡️', color: 'blue' },
  };

  const riskColors: Record<string, string> = {
    Low: 'bg-emerald-100 text-emerald-700 border-emerald-300',
    Moderate: 'bg-amber-100 text-amber-700 border-amber-300',
    High: 'bg-red-100 text-red-700 border-red-300',
  };

  return (
    <div className="space-y-6">
      {/* Header with APY */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            🌾 Liquidity Farming Analysis
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            LP rewards, impermanent loss scenarios, and yield projections
          </p>
        </div>
        <div className="bg-gradient-to-br from-emerald-100 to-teal-100 px-5 py-3 rounded-xl border border-emerald-300">
          <div className="text-3xl font-bold text-emerald-700">
            {(farmingData.apy?.totalApy ?? 0).toFixed(1)}%
          </div>
          <div className="text-xs text-emerald-600 text-center">Total APY</div>
        </div>
      </div>

      {/* APY Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl p-4 border border-purple-200">
          <div className="text-2xl font-bold text-purple-700">
            {(farmingData.apy?.rewardApy ?? 0).toFixed(1)}%
          </div>
          <div className="text-sm text-purple-600">Reward APY</div>
          <div className="text-xs text-purple-500 mt-1">
            {(farmingData.apy?.rewardApr ?? 0).toFixed(1)}% APR
          </div>
        </div>
        <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl p-4 border border-blue-200">
          <div className="text-2xl font-bold text-blue-700">
            {(farmingData.apy?.feeApy ?? 0).toFixed(1)}%
          </div>
          <div className="text-sm text-blue-600">Fee APY</div>
          <div className="text-xs text-blue-500 mt-1">
            Trading fees earned
          </div>
        </div>
        <div className="bg-gradient-to-br from-slate-50 to-gray-50 rounded-xl p-4 border border-slate-200">
          <div className="text-2xl font-bold text-slate-700">
            ${((farmingData.apy?.poolTvlUsd ?? 0) / 1000).toFixed(0)}K
          </div>
          <div className="text-sm text-slate-600">Pool TVL</div>
          <div className="text-xs text-slate-500 mt-1">
            Total value locked
          </div>
        </div>
        <div className={`rounded-xl p-4 border ${
          farmingData.apy?.isSustainable 
            ? 'bg-emerald-50 border-emerald-200' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className={`text-2xl font-bold ${
            farmingData.apy?.isSustainable ? 'text-emerald-700' : 'text-red-700'
          }`}>
            {farmingData.apy?.isSustainable ? '✅' : '⚠️'}
          </div>
          <div className={`text-sm ${
            farmingData.apy?.isSustainable ? 'text-emerald-600' : 'text-red-600'
          }`}>
            {farmingData.apy?.isSustainable ? 'Sustainable' : 'High Emission'}
          </div>
        </div>
      </div>

      {/* Investment Example */}
      <div className="bg-gradient-to-br from-amber-50 to-yellow-50 rounded-xl border border-amber-200 p-5">
        <h3 className="font-semibold text-amber-900 mb-3 flex items-center gap-2">
          💰 $1,000 Investment Projection (1 Year)
        </h3>
        <div className="grid grid-cols-3 gap-4">
          <div className="text-center p-3 bg-white/60 rounded-lg">
            <div className="text-sm text-slate-500">Initial</div>
            <div className="text-xl font-bold text-slate-700">$1,000</div>
          </div>
          <div className="text-center p-3 bg-white/60 rounded-lg">
            <div className="text-sm text-slate-500">Final Value</div>
            <div className="text-xl font-bold text-emerald-600">
              ${(farmingData.apy?.example1000Final ?? 1000).toFixed(0)}
            </div>
          </div>
          <div className="text-center p-3 bg-white/60 rounded-lg">
            <div className="text-sm text-slate-500">Profit</div>
            <div className="text-xl font-bold text-emerald-600">
              +${(farmingData.apy?.example1000Profit ?? 0).toFixed(0)}
            </div>
          </div>
        </div>
        <div className="text-xs text-amber-700 mt-3 text-center">
          * Assuming no impermanent loss and constant APY (compound daily)
        </div>
      </div>

      {/* Impermanent Loss Scenarios */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          📊 Impermanent Loss Scenarios
        </h3>
        <p className="text-sm text-slate-500 mb-4">
          IL occurs when the price ratio of pooled assets changes. The larger the change, the greater the IL.
        </p>
        
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-200">
                <th className="text-left py-2 px-3 text-slate-600">Scenario</th>
                <th className="text-right py-2 px-3 text-slate-600">Price Change</th>
                <th className="text-right py-2 px-3 text-slate-600">IL %</th>
                <th className="text-left py-2 px-3 text-slate-600">Impact</th>
              </tr>
            </thead>
            <tbody>
              {(farmingData.ilScenarios ?? []).map((scenario, idx) => (
                <tr key={idx} className="border-b border-slate-100 hover:bg-slate-50">
                  <td className="py-2 px-3 font-medium text-slate-800">{scenario.scenario}</td>
                  <td className={`py-2 px-3 text-right font-medium ${
                    (scenario.priceChangePercent ?? 0) >= 0 ? 'text-emerald-600' : 'text-red-600'
                  }`}>
                    {(scenario.priceChangePercent ?? 0) >= 0 ? '+' : ''}
                    {scenario.priceChangePercent}%
                  </td>
                  <td className={`py-2 px-3 text-right font-bold ${
                    Math.abs(scenario.impermanentLossPercent ?? 0) > 10 ? 'text-red-600' :
                    Math.abs(scenario.impermanentLossPercent ?? 0) > 5 ? 'text-amber-600' :
                    'text-slate-700'
                  }`}>
                    {(scenario.impermanentLossPercent ?? 0).toFixed(2)}%
                  </td>
                  <td className="py-2 px-3">
                    <span className={`px-2 py-1 rounded text-xs ${
                      scenario.interpretation === 'Severe IL' ? 'bg-red-100 text-red-700' :
                      scenario.interpretation === 'Significant IL' ? 'bg-orange-100 text-orange-700' :
                      scenario.interpretation === 'Moderate IL' ? 'bg-amber-100 text-amber-700' :
                      scenario.interpretation === 'Minor IL' ? 'bg-blue-100 text-blue-700' :
                      'bg-emerald-100 text-emerald-700'
                    }`}>
                      {scenario.interpretation}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* IL Breakeven */}
        <div className="mt-4 pt-4 border-t border-slate-200">
          <div className="flex items-center justify-between text-sm">
            <span className="text-slate-600">IL Breakeven Range (with current APY)</span>
            <div className="font-medium">
              <span className="text-red-600">
                ${(farmingData.riskMetrics?.ilBreakevenPriceDown ?? 0).toFixed(4)}
              </span>
              <span className="text-slate-400 mx-2">→</span>
              <span className="text-emerald-600">
                ${(farmingData.riskMetrics?.ilBreakevenPriceUp ?? 0).toFixed(4)}
              </span>
            </div>
          </div>
          <div className="text-xs text-slate-500 mt-1">
            Price can move {((farmingData.riskMetrics?.ilBreakevenMultiplier ?? 1) * 100 - 100).toFixed(0)}% 
            in either direction before IL exceeds your yield
          </div>
        </div>
      </div>

      {/* Simulation Scenarios */}
      <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-xl border border-slate-200 p-5">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          📈 12-Month Simulation
        </h3>
        
        {/* Scenario Selector */}
        <div className="flex gap-2 mb-4">
          {Object.entries(scenarioLabels).map(([key, { label, icon, color }]) => (
            <button
              key={key}
              onClick={() => setSelectedScenario(key)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                selectedScenario === key
                  ? `bg-${color}-600 text-white`
                  : `bg-white text-slate-700 hover:bg-slate-100 border border-slate-200`
              }`}
              style={selectedScenario === key ? {
                backgroundColor: color === 'emerald' ? '#059669' : color === 'red' ? '#dc2626' : '#2563eb'
              } : {}}
            >
              {icon} {label}
            </button>
          ))}
        </div>

        {/* Simulation Results */}
        {finalResult && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
            <div className="bg-white rounded-lg p-3 text-center">
              <div className={`text-xl font-bold ${
                (finalResult.totalPnlPercent ?? 0) >= 0 ? 'text-emerald-600' : 'text-red-600'
              }`}>
                {(finalResult.totalPnlPercent ?? 0) >= 0 ? '+' : ''}
                {(finalResult.totalPnlPercent ?? 0).toFixed(1)}%
              </div>
              <div className="text-xs text-slate-500">Total Return</div>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-slate-700">
                ${(finalResult.totalValueUsd ?? 1000).toFixed(0)}
              </div>
              <div className="text-xs text-slate-500">Final Value ($1K)</div>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <div className="text-xl font-bold text-red-600">
                {(finalResult.impermanentLossPercent ?? 0).toFixed(2)}%
              </div>
              <div className="text-xs text-slate-500">Impermanent Loss</div>
            </div>
            <div className="bg-white rounded-lg p-3 text-center">
              <div className={`text-xl font-bold ${
                (finalResult.netVsHoldingUsd ?? 0) >= 0 ? 'text-emerald-600' : 'text-red-600'
              }`}>
                {(finalResult.netVsHoldingUsd ?? 0) >= 0 ? '+' : ''}
                ${(finalResult.netVsHoldingUsd ?? 0).toFixed(0)}
              </div>
              <div className="text-xs text-slate-500">vs. Holding</div>
            </div>
          </div>
        )}

        {/* Monthly Breakdown (simplified) */}
        {simulation?.monthlyProjections && simulation.monthlyProjections.length > 0 && (
          <div className="bg-white rounded-lg p-4">
            <div className="text-sm font-medium text-slate-600 mb-2">Monthly Progression</div>
            <div className="flex items-end gap-1 h-24">
              {simulation.monthlyProjections.map((month, idx) => {
                const height = Math.max(5, Math.min(100, 
                  ((month.totalValueUsd ?? 1000) / (simulation.initialInvestmentUsd || 1000) - 0.5) * 100
                ));
                return (
                  <div 
                    key={idx}
                    className="flex-1 bg-gradient-to-t from-blue-400 to-blue-200 rounded-t"
                    style={{ height: `${height}%` }}
                    title={`Month ${month.month}: $${(month.totalValueUsd ?? 0).toFixed(0)}`}
                  />
                );
              })}
            </div>
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>Month 1</span>
              <span>Month 12</span>
            </div>
          </div>
        )}
      </div>

      {/* Risk Assessment */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* Risk Score */}
        <div className={`rounded-xl p-5 border ${
          riskColors[farmingData.riskMetrics?.riskLevel || 'Moderate']
        }`}>
          <h3 className="font-semibold mb-4 flex items-center gap-2">
            ⚠️ Risk Assessment
          </h3>
          <div className="text-center mb-4">
            <div className="text-4xl font-bold">
              {(farmingData.riskMetrics?.riskScore ?? 30).toFixed(0)}
            </div>
            <div className="text-sm">{farmingData.riskMetrics?.riskLevel ?? 'Moderate'} Risk</div>
          </div>
          <div className="h-3 bg-white/50 rounded-full overflow-hidden">
            <div 
              className={`h-full rounded-full ${
                (farmingData.riskMetrics?.riskScore ?? 30) >= 60 ? 'bg-red-500' :
                (farmingData.riskMetrics?.riskScore ?? 30) >= 30 ? 'bg-amber-500' : 'bg-emerald-500'
              }`}
              style={{ width: `${farmingData.riskMetrics?.riskScore ?? 30}%` }}
            />
          </div>
        </div>

        {/* Daily Metrics */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
            📅 Daily Metrics
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-500">Daily Reward Rate</span>
              <span className="font-medium text-slate-800">
                {(farmingData.apy?.dailyRewardRate ?? 0).toFixed(4)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Daily Total Rate</span>
              <span className="font-medium text-slate-800">
                {(farmingData.apy?.dailyTotalRate ?? 0).toFixed(4)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Daily Reward (VCoin)</span>
              <span className="font-medium text-slate-800">
                {(farmingData.apy?.dailyRewardVcoin ?? 0).toFixed(0)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Daily Reward (USD)</span>
              <span className="font-medium text-emerald-600">
                ${(farmingData.apy?.dailyRewardUsd ?? 0).toFixed(2)}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {farmingData.recommendations && farmingData.recommendations.length > 0 && (
        <div className="bg-blue-50 rounded-xl border border-blue-200 p-5">
          <h3 className="font-semibold text-blue-900 mb-3 flex items-center gap-2">
            💡 LP Strategy Recommendations
          </h3>
          <ul className="space-y-2">
            {farmingData.recommendations.map((rec, idx) => (
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
        <h3 className="font-semibold text-slate-800 mb-4">📖 Liquidity Farming Guide</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-slate-700 mb-2">APY vs APR</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• APR: Simple annual return</li>
              <li>• APY: Compound return</li>
              <li>• Daily compound = higher APY</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Impermanent Loss</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• 2x price = ~5.7% IL</li>
              <li>• 3x price = ~13.4% IL</li>
              <li>• 5x price = ~25.5% IL</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Risk Factors</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• Low TVL = higher IL risk</li>
              <li>• High APY = emission dilution</li>
              <li>• Volatile pairs = more IL</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

