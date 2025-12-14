'use client';

import { useMemo } from 'react';
import { SimulationResult, SimulationParameters, YearlyProjection } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { GROWTH_SCENARIOS, MARKET_CONDITIONS, MARKET_CYCLE_2026_2030 } from '@/lib/constants';

interface Year5OverviewProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function Year5Overview({ result, parameters }: Year5OverviewProps) {
  // Get scenario and market config for display purposes
  const scenario = (parameters.growthScenario || 'base') as keyof typeof GROWTH_SCENARIOS;
  const marketCondition = (parameters.marketCondition || 'neutral') as keyof typeof MARKET_CONDITIONS;
  const scenarioConfig = GROWTH_SCENARIOS[scenario];
  const marketConfig = MARKET_CONDITIONS[marketCondition];
  
  // Use backend-calculated projections from result
  const fiveYearProjections = useMemo(() => {
    // Backend now calculates these - just use them directly
    if (result.fiveYearProjections && result.fiveYearProjections.available) {
      return result.fiveYearProjections.years;
    }
    // Fallback: empty array if not available
    return [];
  }, [result]);
  
  const enabledFutureModules = {
    vchain: parameters.enableVchain || false,
    marketplace: parameters.enableMarketplace || false,
    businessHub: parameters.enableBusinessHub || false,
    crossPlatform: parameters.enableCrossPlatform || false,
  };
  const hasFutureModules = Object.values(enabledFutureModules).some(Boolean);
  
  // If no projections available, show fallback message
  if (!fiveYearProjections || fiveYearProjections.length === 0) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-6">
        <h3 className="font-bold text-lg text-yellow-800 mb-2">5-Year Projections Not Available</h3>
        <p className="text-yellow-700">
          Backend calculations are in progress. Please run the simulation again to see 5-year projections.
        </p>
      </div>
    );
  }
  
  const totalRevenue = fiveYearProjections.reduce((s, y) => s + y.totalRevenue, 0);
  const totalProfit = fiveYearProjections.reduce((s, y) => s + y.totalProfit, 0);
  const totalFutureRevenue = fiveYearProjections.reduce((s, y) => s + y.futureModulesRevenue, 0);

  return (
    <section className="space-y-8">
      {/* Hero - 5 Year Summary */}
      <div className="bg-gradient-to-br from-slate-900 via-indigo-900 to-purple-900 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">📈</span>
          <div>
            <h2 className="text-2xl font-bold">5-Year Financial Projection</h2>
            <p className="text-indigo-300">Long-term growth analysis (2026-2030)</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-3xl font-bold">{formatNumber(fiveYearProjections[4].endUsers)}</div>
            <div className="text-sm text-indigo-200 uppercase font-semibold mt-1">Year 5 Users</div>
            <div className="text-xs text-indigo-300">
              {((fiveYearProjections[4].endUsers / fiveYearProjections[0].startUsers - 1) * 100).toFixed(0)}% growth
            </div>
          </div>
          <div className="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-3xl font-bold">{formatCurrency(totalRevenue)}</div>
            <div className="text-sm text-indigo-200 uppercase font-semibold mt-1">Total Revenue</div>
          </div>
          <div className="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-3xl font-bold ${totalProfit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(totalProfit)}
            </div>
            <div className="text-sm text-indigo-200 uppercase font-semibold mt-1">Total Profit</div>
          </div>
          <div className="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-3xl font-bold text-amber-300">${fiveYearProjections[4].tokenPriceEnd.toFixed(2)}</div>
            <div className="text-sm text-indigo-200 uppercase font-semibold mt-1">Y5 Token Price</div>
            <div className="text-xs text-indigo-300">
              {(fiveYearProjections[4].tokenPriceEnd / parameters.tokenPrice).toFixed(1)}x from TGE
            </div>
          </div>
        </div>
      </div>

      {/* Market Cycle Analysis (2026-2030) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🔄</span> Market Cycle Analysis (2026-2030)
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Object.entries(MARKET_CYCLE_2026_2030 || {}).map(([year, data]) => {
            const cycleColors: Record<string, string> = {
              'bull': 'from-emerald-500 to-green-600',
              'bear': 'from-red-500 to-orange-600',
              'recovery': 'from-blue-500 to-cyan-600',
              'accumulation': 'from-amber-500 to-yellow-600',
              'expansion': 'from-purple-500 to-pink-600',
              'neutral': 'from-gray-500 to-slate-600',
            };
            const phase = (data as any)?.phase || 'neutral';
            return (
              <div key={year} className={`bg-gradient-to-br ${cycleColors[phase] || cycleColors['neutral']} rounded-xl p-4 text-white text-center`}>
                <div className="text-xl font-bold">{year}</div>
                <div className="text-sm capitalize opacity-90">{phase}</div>
                <div className="text-xs opacity-75 mt-2">
                  Growth: {(data.growthMultiplier || 1).toFixed(2)}x
                </div>
                <div className="text-xs opacity-75">
                  Price: {(data.priceMultiplier || 1).toFixed(2)}x
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Yearly Breakdown Table */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>📊</span> Yearly Financial Breakdown
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-3 py-2 text-left font-semibold text-gray-600">Year</th>
                <th className="px-3 py-2 text-right font-semibold text-gray-600">Users</th>
                <th className="px-3 py-2 text-right font-semibold text-gray-600">Marketing</th>
                <th className="px-3 py-2 text-right font-semibold text-gray-600">Core Revenue</th>
                <th className="px-3 py-2 text-right font-semibold text-gray-600">Future Modules</th>
                <th className="px-3 py-2 text-right font-semibold text-gray-600">Total Revenue</th>
                <th className="px-3 py-2 text-right font-semibold text-gray-600">Profit</th>
                <th className="px-3 py-2 text-right font-semibold text-gray-600">Margin</th>
                <th className="px-3 py-2 text-right font-semibold text-gray-600">Token Price</th>
                <th className="px-3 py-2 text-center font-semibold text-gray-600">Market</th>
              </tr>
            </thead>
            <tbody>
              {fiveYearProjections.map((year) => {
                const marketCycleColors: Record<string, string> = {
                  'bull': 'bg-emerald-100 text-emerald-700',
                  'bear': 'bg-red-100 text-red-700',
                  'recovery': 'bg-blue-100 text-blue-700',
                  'accumulation': 'bg-amber-100 text-amber-700',
                  'expansion': 'bg-purple-100 text-purple-700',
                  'neutral': 'bg-gray-100 text-gray-700',
                };
                return (
                  <tr key={year.year} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="px-3 py-3 font-semibold">
                      <div className="flex items-center gap-2">
                        <span className="text-lg">
                          {year.year === 1 ? '🚀' : year.year === 2 ? '📈' : year.year === 3 ? '🏗️' : year.year === 4 ? '🎯' : '🏆'}
                        </span>
                        Year {year.year}
                        <span className="text-xs text-gray-400">({2025 + year.year})</span>
                      </div>
                      {year.activeModules.length > 0 && (
                        <div className="text-xs text-purple-500 mt-1">
                          {year.activeModules.join(' • ')}
                        </div>
                      )}
                    </td>
                    <td className="px-3 py-3 text-right">
                      <div>{formatNumber(year.endUsers)}</div>
                      <div className="text-xs text-gray-400">
                        +{((year.endUsers / year.startUsers - 1) * 100).toFixed(0)}%
                      </div>
                    </td>
                    <td className="px-3 py-3 text-right">
                      <div className="text-orange-600 font-semibold">
                        {formatCurrency(year.marketingBudget)}
                      </div>
                      <div className="text-xs text-gray-400">
                        {year.marketingMultiplier.toFixed(0)}x
                      </div>
                    </td>
                    <td className="px-3 py-3 text-right">
                      {formatCurrency(year.coreModulesRevenue)}
                    </td>
                    <td className="px-3 py-3 text-right">
                      {year.futureModulesRevenue > 0 ? (
                        <span className="text-purple-600 font-semibold">
                          +{formatCurrency(year.futureModulesRevenue)}
                        </span>
                      ) : (
                        <span className="text-gray-400">-</span>
                      )}
                    </td>
                    <td className="px-3 py-3 text-right font-semibold text-emerald-600">
                      {formatCurrency(year.totalRevenue)}
                    </td>
                    <td className={`px-3 py-3 text-right font-semibold ${year.totalProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                      {formatCurrency(year.totalProfit)}
                    </td>
                    <td className="px-3 py-3 text-right">
                      {year.avgMargin.toFixed(1)}%
                    </td>
                    <td className="px-3 py-3 text-right text-amber-600">
                      ${year.tokenPriceEnd.toFixed(2)}
                    </td>
                    <td className="px-3 py-3 text-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${marketCycleColors[year.marketCycle] || marketCycleColors['neutral']}`}>
                        {year.marketCycle}
                      </span>
                    </td>
                  </tr>
                );
              })}
              {/* Total Row */}
              <tr className="bg-gray-900 text-white font-bold">
                <td className="px-3 py-3">5-Year Total</td>
                <td className="px-3 py-3 text-right">{formatNumber(fiveYearProjections[4].endUsers)}</td>
                <td className="px-3 py-3 text-right text-orange-300">
                  {formatCurrency(fiveYearProjections.reduce((s, y) => s + y.marketingBudget, 0))}
                </td>
                <td className="px-3 py-3 text-right">
                  {formatCurrency(fiveYearProjections.reduce((s, y) => s + y.coreModulesRevenue, 0))}
                </td>
                <td className="px-3 py-3 text-right text-purple-300">
                  +{formatCurrency(totalFutureRevenue)}
                </td>
                <td className="px-3 py-3 text-right text-emerald-300">
                  {formatCurrency(totalRevenue)}
                </td>
                <td className="px-3 py-3 text-right text-green-300">
                  {formatCurrency(totalProfit)}
                </td>
                <td className="px-3 py-3 text-right">
                  {(totalProfit / totalRevenue * 100).toFixed(1)}%
                </td>
                <td className="px-3 py-3 text-right text-amber-300">
                  {(fiveYearProjections[4].tokenPriceEnd / parameters.tokenPrice).toFixed(1)}x
                </td>
                <td className="px-3 py-3"></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Future Modules Section */}
      {hasFutureModules && (
        <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl border border-purple-200 p-6 shadow-sm">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2 text-purple-800">
            <span>🔮</span> Future Module Revenue Impact
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {enabledFutureModules.crossPlatform && (
              <div className="bg-white rounded-lg p-4 border border-purple-200 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">🌐</span>
                  <span className="font-bold">Cross-Platform</span>
                </div>
                <div className="text-sm text-gray-500 mb-2">Launches Month 15</div>
                <div className="text-xl font-bold text-purple-600">
                  {formatCurrency((fiveYearProjections[1]?.futureModulesRevenue || 0) * 0.3)}/yr
                </div>
                <div className="text-xs text-gray-500 mt-1">Content sharing & rentals</div>
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="text-xs text-gray-600">Subscription: $10/mo</div>
                  <div className="text-xs text-gray-600">Rental commission: 15%</div>
                </div>
              </div>
            )}
            {enabledFutureModules.marketplace && (
              <div className="bg-white rounded-lg p-4 border border-purple-200 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">🛒</span>
                  <span className="font-bold">Marketplace</span>
                </div>
                <div className="text-sm text-gray-500 mb-2">Launches Month 18</div>
                <div className="text-xl font-bold text-purple-600">
                  {formatCurrency((fiveYearProjections[2]?.futureModulesRevenue || 0) * 0.35)}/yr
                </div>
                <div className="text-xs text-gray-500 mt-1">Physical & digital goods</div>
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="text-xs text-gray-600">Physical: 8% commission</div>
                  <div className="text-xs text-gray-600">Digital: 15% commission</div>
                </div>
              </div>
            )}
            {enabledFutureModules.businessHub && (
              <div className="bg-white rounded-lg p-4 border border-purple-200 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">💼</span>
                  <span className="font-bold">Business Hub</span>
                </div>
                <div className="text-sm text-gray-500 mb-2">Launches Month 21</div>
                <div className="text-xl font-bold text-purple-600">
                  {formatCurrency((fiveYearProjections[2]?.futureModulesRevenue || 0) * 0.25)}/yr
                </div>
                <div className="text-xs text-gray-500 mt-1">Freelancer ecosystem</div>
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="text-xs text-gray-600">Freelance: 12% fee</div>
                  <div className="text-xs text-gray-600">PM tools: $15/mo</div>
                </div>
              </div>
            )}
            {enabledFutureModules.vchain && (
              <div className="bg-white rounded-lg p-4 border border-purple-200 shadow-sm">
                <div className="flex items-center gap-2 mb-3">
                  <span className="text-2xl">🔗</span>
                  <span className="font-bold">VChain Network</span>
                </div>
                <div className="text-sm text-gray-500 mb-2">Launches Month 24</div>
                <div className="text-xl font-bold text-purple-600">
                  {formatCurrency((fiveYearProjections[2]?.futureModulesRevenue || 0) * 0.4)}/yr
                </div>
                <div className="text-xs text-gray-500 mt-1">Cross-chain infrastructure</div>
                <div className="mt-3 pt-3 border-t border-gray-100">
                  <div className="text-xs text-gray-600">TX fees: 0.2%</div>
                  <div className="text-xs text-gray-600">Bridge: 0.1% fee</div>
                </div>
              </div>
            )}
          </div>
          <div className="mt-4 bg-white/70 rounded-lg p-4">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-purple-800">Total Future Module Contribution (5 years)</span>
              <span className="text-2xl font-bold text-purple-700">{formatCurrency(totalFutureRevenue)}</span>
            </div>
            <div className="text-sm text-purple-600 mt-1">
              {(totalFutureRevenue / totalRevenue * 100).toFixed(1)}% of total 5-year revenue
            </div>
          </div>
        </div>
      )}

      {/* Token Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Token Value Accrual */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>💎</span> Token Value Accrual
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center p-3 bg-amber-50 rounded-lg">
              <span className="text-gray-700">TGE Price</span>
              <span className="font-bold text-amber-600">${parameters.tokenPrice.toFixed(4)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-blue-50 rounded-lg">
              <span className="text-gray-700">Year 1 End</span>
              <span className="font-bold text-blue-600">${fiveYearProjections[0].tokenPriceEnd.toFixed(4)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-purple-50 rounded-lg">
              <span className="text-gray-700">Year 3 End</span>
              <span className="font-bold text-purple-600">${fiveYearProjections[2].tokenPriceEnd.toFixed(2)}</span>
            </div>
            <div className="flex justify-between items-center p-3 bg-emerald-50 rounded-lg">
              <span className="text-gray-700">Year 5 End</span>
              <span className="font-bold text-emerald-600">${fiveYearProjections[4].tokenPriceEnd.toFixed(2)}</span>
            </div>
            <div className="pt-3 border-t border-gray-200">
              <div className="flex justify-between">
                <span className="font-semibold">5-Year Appreciation</span>
                <span className="font-bold text-emerald-600">
                  {(fiveYearProjections[4].tokenPriceEnd / parameters.tokenPrice).toFixed(1)}x
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Token Metrics */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>📐</span> Token Economics
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Velocity Factor</span>
              <span className="font-semibold">{(result.tokenMetrics?.velocity?.velocity || 2.5).toFixed(2)}x</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Burn Rate (Annual)</span>
              <span className="font-semibold text-red-600">
                {formatNumber((result.recapture?.burns || 0) * 12)} VC
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Buyback (Annual)</span>
              <span className="font-semibold text-blue-600">
                {formatNumber((result.recapture?.buybacks || 0) * 12)} VC
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Staking APY</span>
              <span className="font-semibold text-indigo-600">
                {(result.staking?.stakingApy || 0).toFixed(1)}%
              </span>
            </div>
            <div className="pt-3 border-t border-gray-200">
              <div className="flex justify-between">
                <span className="font-semibold">Recapture Rate</span>
                <span className="font-bold text-purple-600">
                  {(result.recapture?.recaptureRate || 0).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Governance & Treasury */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Governance Projections */}
        {result.governance && (
          <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
            <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
              <span>🏛️</span> Governance Projections
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Active Voting Power</span>
                <span className="font-semibold">{formatNumber(result.governance?.activeVotingPower || 0)} VP</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Expected Monthly Proposals</span>
                <span className="font-semibold">{result.governance?.expectedMonthlyProposals || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Participation Rate</span>
                <span className="font-semibold">{(result.governance?.effectiveParticipationRate || result.governance?.votingParticipationRate || 0).toFixed(1)}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Governance Revenue</span>
                <span className="font-semibold text-emerald-600">{formatCurrency(result.governance?.revenue || 0)}</span>
              </div>
            </div>
          </div>
        )}

        {/* Treasury Accumulation */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>🏦</span> Treasury Accumulation (5Y)
          </h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Y1 Treasury Add</span>
              <span className="font-semibold">{formatCurrency(fiveYearProjections[0].totalProfit * 0.15)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Y3 Treasury Add</span>
              <span className="font-semibold">{formatCurrency(fiveYearProjections[2].totalProfit * 0.15)}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Y5 Treasury Add</span>
              <span className="font-semibold">{formatCurrency(fiveYearProjections[4].totalProfit * 0.15)}</span>
            </div>
            <div className="pt-3 border-t border-gray-200">
              <div className="flex justify-between">
                <span className="font-semibold">5-Year Total (15% of profits)</span>
                <span className="font-bold text-emerald-600">{formatCurrency(totalProfit * 0.15)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Key Milestones */}
      <div className="bg-gradient-to-br from-gray-50 to-slate-100 rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🎯</span> Key Milestones Timeline
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="flex items-center gap-3 bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
            <span className="text-3xl">🚀</span>
            <div>
              <div className="font-bold">TGE Launch</div>
              <div className="text-sm text-gray-500">Month 1 • {formatNumber(fiveYearProjections[0].startUsers)} users</div>
            </div>
          </div>
          <div className="flex items-center gap-3 bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
            <span className="text-3xl">📊</span>
            <div>
              <div className="font-bold">Break-even</div>
              <div className="text-sm text-gray-500">
                {fiveYearProjections[0].totalProfit > 0 ? 'Profitable from Day 1!' : 'Month 3 projected'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
            <span className="text-3xl">🎉</span>
            <div>
              <div className="font-bold">100K Users</div>
              <div className="text-sm text-gray-500">
                {fiveYearProjections.findIndex(y => y.endUsers >= 100000) >= 0 
                  ? `Year ${fiveYearProjections.findIndex(y => y.endUsers >= 100000) + 1}` 
                  : 'Beyond 5 years'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-3 bg-white rounded-lg p-4 border border-gray-200 shadow-sm">
            <span className="text-3xl">💰</span>
            <div>
              <div className="font-bold">$1M Annual Revenue</div>
              <div className="text-sm text-gray-500">
                {fiveYearProjections.findIndex(y => y.totalRevenue >= 1_000_000) >= 0 
                  ? `Year ${fiveYearProjections.findIndex(y => y.totalRevenue >= 1_000_000) + 1}` 
                  : 'Beyond 5 years'}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Growth Scenario Info */}
      <div className={`rounded-xl p-4 border-2 ${
        scenario === 'bullish' ? 'bg-emerald-50 border-emerald-300' :
        scenario === 'conservative' ? 'bg-blue-50 border-blue-300' :
        'bg-purple-50 border-purple-300'
      }`}>
        <div className="flex items-center gap-3">
          <span className="text-2xl">
            {scenario === 'bullish' ? '🚀' : scenario === 'conservative' ? '🐢' : '⚖️'}
          </span>
          <div>
            <h4 className={`font-bold ${
              scenario === 'bullish' ? 'text-emerald-800' :
              scenario === 'conservative' ? 'text-blue-800' :
              'text-purple-800'
            }`}>
              {scenarioConfig.name} Growth Scenario
            </h4>
            <p className="text-sm text-gray-600">
              {marketConfig.name} market conditions • These projections are estimates based on the selected scenario
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

