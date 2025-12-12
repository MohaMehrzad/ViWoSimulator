'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency, getMarginStatus, getRecaptureStatus } from '@/lib/utils';
import { GROWTH_SCENARIOS, MARKET_CONDITIONS, MARKET_CYCLE_2026_2030 } from '@/lib/constants';

interface SummarySectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function SummarySection({ result, parameters }: SummarySectionProps) {
  const { totals, recapture, rewards, customerAcquisition, platformFees, liquidity, staking } = result;
  const marginStatus = getMarginStatus(totals.margin);
  const recaptureStatus = getRecaptureStatus(recapture.recaptureRate);
  
  // Liquidity and Staking health metrics
  const liquidityHealthScore = liquidity?.healthScore || 0;
  const liquidityMeets70 = liquidityHealthScore >= 70;
  const stakingHealthy = staking?.isHealthy || false;
  const stakingParticipation = staking?.participationRate || 0;
  
  // Governance metrics
  const governance = result.governance;
  const governanceParticipation = governance?.effectiveParticipationRate || governance?.votingParticipationRate || 0;
  
  // Token metrics - ensure all values are numbers
  const tokenMetrics = result.tokenMetrics;
  const tokenVelocity = Number(tokenMetrics?.velocity?.velocity ?? 0) || 0;
  const realYield = Number(tokenMetrics?.realYield?.annualRealYield ?? 0) || 0;
  const valueAccrual = Number(tokenMetrics?.valueAccrual?.totalScore ?? 0) || 0;
  
  // Future modules
  const futureModulesEnabled = {
    vchain: parameters.enableVchain || false,
    marketplace: parameters.enableMarketplace || false,
    businessHub: parameters.enableBusinessHub || false,
    crossPlatform: parameters.enableCrossPlatform || false,
  };
  const enabledFutureModulesCount = Object.values(futureModulesEnabled).filter(Boolean).length;
  
  // Growth scenario info
  const useGrowthScenarios = parameters.useGrowthScenarios || false;
  const scenario = parameters.growthScenario || 'base';
  const marketCondition = parameters.marketCondition || 'bull';
  const scenarioConfig = GROWTH_SCENARIOS[scenario];
  const marketConfig = MARKET_CONDITIONS[marketCondition];
  
  // Issue #1 Fix: Guard against division by zero for both totalUsers and blendedCAC
  // Dec 2025: Use total users with organic if available
  const totalUsersForCalc = customerAcquisition.totalUsersWithOrganic || customerAcquisition.totalUsers;
  const arpu = totalUsersForCalc > 0 
    ? totals.revenue / totalUsersForCalc 
    : 0;
  const ltvCacRatio = (customerAcquisition.blendedCAC > 0 && totalUsersForCalc > 0)
    ? arpu / customerAcquisition.blendedCAC 
    : 0;

  const coreModules = [
    { name: 'Identity', data: result.identity, icon: '🆔', enabled: true },
    { name: 'Content', data: result.content, icon: '📄', enabled: true },
    { name: 'Advertising', data: result.advertising, icon: '📢', enabled: parameters.enableAdvertising },
    { name: 'Exchange', data: result.exchange, icon: '💱', enabled: parameters.enableExchange },
  ];

  // Platform fees as a pseudo-module for display purposes
  const platformFeesModule = {
    name: 'Platform Fees',
    data: { 
      revenue: platformFees.rewardFeeUsd, 
      costs: 0, 
      profit: platformFees.rewardFeeUsd, 
      margin: 100 
    },
    icon: '💰',
    enabled: true,
  };

  // Staking as a module
  const stakingModule = {
    name: 'Staking',
    data: {
      revenue: staking?.revenue || 0,
      costs: staking?.costs || 0,
      profit: staking?.profit || 0,
      margin: staking?.margin || 0,
    },
    icon: '🔒',
    enabled: true,
  };

  const enabledModules = [...coreModules.filter(m => m.enabled), stakingModule, platformFeesModule];

  // Calculate projections using scenario if available
  const baseGrowthRate = useGrowthScenarios 
    ? (scenarioConfig?.monthlyGrowthRates?.[5] || 0.05) 
    : 0.05;
  const priceMultiplier = useGrowthScenarios 
    ? (scenarioConfig?.tokenPriceEndMultiplier || 1) * (marketConfig?.priceMultiplier || 1)
    : 1.5;
  
  // Year 1 projections with growth
  const year1Revenue = totals.revenue * 12 * (1 + baseGrowthRate * 6);
  const year1Profit = totals.profit * 12 * (1 + baseGrowthRate * 6);
  const year1EndUsers = customerAcquisition.totalUsers * Math.pow(1 + baseGrowthRate, 12);
  
  // 5-year projections (simplified)
  const fiveYearMultiplier = useGrowthScenarios ? 3 : 2;
  const fiveYearRevenue = year1Revenue * fiveYearMultiplier;
  const fiveYearProfit = year1Profit * fiveYearMultiplier;

  return (
    <section className="space-y-8">
      {/* Executive Summary Header */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-4xl">📈</span>
            <div>
              <h2 className="text-2xl font-bold">Executive Summary</h2>
              <p className="text-gray-400">Complete ViWO Token Economy Overview</p>
            </div>
          </div>
          {useGrowthScenarios && (
            <div className={`px-4 py-2 rounded-xl ${
              scenario === 'bullish' ? 'bg-emerald-500/20 border border-emerald-400' :
              scenario === 'conservative' ? 'bg-blue-500/20 border border-blue-400' :
              'bg-purple-500/20 border border-purple-400'
            }`}>
              <div className="text-sm font-semibold">{scenarioConfig?.name} Scenario</div>
              <div className="text-xs text-gray-300">{marketConfig?.name} Market</div>
            </div>
          )}
        </div>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${marginStatus.color.replace('text-', 'text-')}`}>
              {formatCurrency(totals.revenue)}
            </div>
            <div className="text-xs text-gray-400 uppercase font-semibold">Monthly Revenue</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${totals.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {formatCurrency(totals.profit)}
            </div>
            <div className="text-xs text-gray-400 uppercase font-semibold">Monthly Profit</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${marginStatus.color.replace('text-', 'text-')}`}>
              {totals.margin.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-400 uppercase font-semibold">Profit Margin</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${recaptureStatus.color.replace('text-', 'text-')}`}>
              {recapture.recaptureRate.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-400 uppercase font-semibold">Recapture Rate</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold text-amber-400">
              ${parameters.tokenPrice.toFixed(2)}
            </div>
            <div className="text-xs text-gray-400 uppercase font-semibold">Token Price</div>
          </div>
        </div>
      </div>

      {/* Health Indicators */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Profitability Status */}
        <div className={`rounded-xl p-6 border-2 ${
          totals.margin >= 30 
            ? 'bg-emerald-50 border-emerald-300' 
            : totals.margin >= 15 
              ? 'bg-amber-50 border-amber-300'
              : 'bg-red-50 border-red-300'
        }`}>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">
              {totals.margin >= 30 ? '✅' : totals.margin >= 15 ? '⚠️' : '🚨'}
            </span>
            <div>
              <div className="font-bold text-lg">Profitability: {marginStatus.label}</div>
              <div className="text-sm text-gray-600">
                {totals.margin >= 30 
                  ? 'Excellent margins for sustainable growth' 
                  : totals.margin >= 15 
                    ? 'Acceptable but could be improved'
                    : 'Needs optimization'}
              </div>
            </div>
          </div>
        </div>

        {/* Token Economy Status */}
        <div className={`rounded-xl p-6 border-2 ${
          recapture.recaptureRate >= 100 
            ? 'bg-emerald-50 border-emerald-300' 
            : recapture.recaptureRate >= 80 
              ? 'bg-amber-50 border-amber-300'
              : 'bg-red-50 border-red-300'
        }`}>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">
              {recapture.recaptureRate >= 100 ? '✅' : recapture.recaptureRate >= 80 ? '⚠️' : '🚨'}
            </span>
            <div>
              <div className="font-bold text-lg">Token Economy: {recaptureStatus.label}</div>
              <div className="text-sm text-gray-600">
                {recapture.recaptureRate >= 100 
                  ? 'Deflationary - excellent for token value' 
                  : recapture.recaptureRate >= 80 
                    ? 'Near sustainable levels'
                    : 'Inflationary pressure detected'}
              </div>
            </div>
          </div>
        </div>

        {/* NEW: Liquidity Health Status */}
        <div className={`rounded-xl p-6 border-2 ${
          liquidityMeets70 
            ? 'bg-emerald-50 border-emerald-300' 
            : liquidityHealthScore >= 50 
              ? 'bg-amber-50 border-amber-300'
              : 'bg-red-50 border-red-300'
        }`}>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">
              {liquidityMeets70 ? '✅' : liquidityHealthScore >= 50 ? '⚠️' : '🚨'}
            </span>
            <div>
              <div className="font-bold text-lg">Liquidity Health: {liquidityHealthScore.toFixed(0)}%</div>
              <div className="text-sm text-gray-600">
                {liquidityMeets70 
                  ? 'Healthy liquidity for trading' 
                  : liquidityHealthScore >= 50 
                    ? 'Moderate liquidity - consider adding more'
                    : 'Low liquidity - trading may have high slippage'}
              </div>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">Target: 70%+ health score</div>
        </div>

        {/* NEW: LTV/CAC Ratio Status */}
        <div className={`rounded-xl p-6 border-2 ${
          ltvCacRatio >= 3 
            ? 'bg-emerald-50 border-emerald-300' 
            : ltvCacRatio >= 1 
              ? 'bg-amber-50 border-amber-300'
              : 'bg-red-50 border-red-300'
        }`}>
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">
              {ltvCacRatio >= 3 ? '✅' : ltvCacRatio >= 1 ? '⚠️' : '🚨'}
            </span>
            <div>
              <div className="font-bold text-lg">LTV/CAC: {ltvCacRatio.toFixed(1)}x</div>
              <div className="text-sm text-gray-600">
                {ltvCacRatio >= 3 
                  ? 'Excellent unit economics' 
                  : ltvCacRatio >= 1 
                    ? 'Break-even - needs improvement'
                    : 'Losing money per user acquisition'}
              </div>
            </div>
          </div>
          <div className="mt-2 text-xs text-gray-500">Target: 3x+ LTV/CAC ratio</div>
        </div>
      </div>

      {/* Module Performance Summary */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <h3 className="font-bold text-lg">📊 Module Performance Ranking</h3>
        </div>
        <div className="p-4">
          <div className="space-y-4">
            {enabledModules
              .sort((a, b) => b.data.profit - a.data.profit)
              .map((module, index) => (
                <div key={module.name} className="flex items-center gap-4">
                  <div className="w-8 h-8 rounded-full bg-gray-100 flex items-center justify-center font-bold text-gray-600">
                    #{index + 1}
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-medium flex items-center gap-2">
                        <span>{module.icon}</span> {module.name}
                      </span>
                      <span className={`font-bold ${module.data.profit >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                        {formatCurrency(module.data.profit)}
                      </span>
                    </div>
                    <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className={`h-full ${module.data.profit >= 0 ? 'bg-emerald-500' : 'bg-red-500'}`}
                        style={{ 
                          width: `${Math.abs(module.data.profit) / Math.max(...enabledModules.map(m => Math.abs(m.data.profit))) * 100}%` 
                        }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                      <span>Rev: {formatCurrency(module.data.revenue)}</span>
                      <span>Margin: {module.data.margin.toFixed(1)}%</span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🎯 Key Performance Indicators</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatNumber(customerAcquisition.totalUsers)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Total Users</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(customerAcquisition.blendedCAC)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Blended CAC</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(arpu)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">ARPU</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {ltvCacRatio.toFixed(1)}x
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">LTV/CAC Ratio</div>
          </div>
        </div>
      </div>

      {/* Token Economics Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🪙 Token Economics Summary</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
            <div className="text-sm text-amber-600 mb-1">Gross Emission</div>
            <div className="text-xl font-bold text-amber-700">{formatNumber(rewards.grossMonthlyEmission)}</div>
            <div className="text-xs text-amber-500">{formatCurrency(rewards.grossEmissionUsd)}</div>
          </div>
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Platform Fee (5%)</div>
            <div className="text-xl font-bold text-emerald-700">{formatNumber(rewards.platformFeeVcoin)}</div>
            <div className="text-xs text-emerald-500">{formatCurrency(rewards.platformFeeUsd)} revenue</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="text-sm text-blue-600 mb-1">Net to Users (95%)</div>
            <div className="text-xl font-bold text-blue-700">{formatNumber(rewards.monthlyEmission)}</div>
            <div className="text-xs text-blue-500">{formatCurrency(rewards.emissionUsd)}</div>
          </div>
          <div className="bg-rose-50 rounded-lg p-4 border border-rose-200">
            <div className="text-sm text-rose-600 mb-1">Total Recaptured</div>
            <div className="text-xl font-bold text-rose-700">{formatNumber(recapture.totalRecaptured)}</div>
            <div className="text-xs text-rose-500">{formatCurrency(recapture.totalRecaptured * parameters.tokenPrice)}</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="text-sm text-purple-600 mb-1">Token Price</div>
            <div className="text-xl font-bold text-purple-700">{formatCurrency(parameters.tokenPrice)}</div>
            <div className="text-xs text-purple-500">Simulation price</div>
          </div>
        </div>
      </div>

      {/* Annual Projections */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📅 Financial Projections</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Year 1 */}
          <div className="bg-gradient-to-br from-emerald-50 to-green-50 rounded-xl p-5 border border-emerald-200">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🚀</span>
              <h4 className="font-bold text-emerald-800">Year 1 Projection</h4>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-emerald-600">Revenue</div>
                <div className="text-xl font-bold text-emerald-700">{formatCurrency(year1Revenue)}</div>
              </div>
              <div>
                <div className="text-xs text-emerald-600">Profit</div>
                <div className="text-xl font-bold text-emerald-700">{formatCurrency(year1Profit)}</div>
              </div>
              <div>
                <div className="text-xs text-emerald-600">End Users</div>
                <div className="text-xl font-bold text-emerald-700">{formatNumber(year1EndUsers)}</div>
              </div>
              <div>
                <div className="text-xs text-emerald-600">Token Price</div>
                <div className="text-xl font-bold text-amber-600">
                  ${(parameters.tokenPrice * (useGrowthScenarios ? priceMultiplier : 1.5)).toFixed(2)}
                </div>
              </div>
            </div>
          </div>
          
          {/* 5-Year */}
          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-xl p-5 border border-purple-200">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🎯</span>
              <h4 className="font-bold text-purple-800">5-Year Projection</h4>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-purple-600">Total Revenue</div>
                <div className="text-xl font-bold text-purple-700">{formatCurrency(fiveYearRevenue)}</div>
              </div>
              <div>
                <div className="text-xs text-purple-600">Total Profit</div>
                <div className="text-xl font-bold text-purple-700">{formatCurrency(fiveYearProfit)}</div>
              </div>
              <div>
                <div className="text-xs text-purple-600">Future Modules</div>
                <div className="text-xl font-bold text-purple-700">{enabledFutureModulesCount}/4</div>
              </div>
              <div>
                <div className="text-xs text-purple-600">Market Cycles</div>
                <div className="text-sm font-bold text-purple-700">
                  {Object.keys(MARKET_CYCLE_2026_2030 || {}).length} years
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Token Metrics & Governance */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Token Metrics */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>📊</span> Token Health Metrics
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Token Velocity</span>
              <span className={`font-bold ${tokenVelocity < 10 ? 'text-emerald-600' : tokenVelocity < 20 ? 'text-amber-600' : 'text-red-600'}`}>
                {tokenVelocity.toFixed(2)}x
              </span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full ${tokenVelocity < 10 ? 'bg-emerald-500' : tokenVelocity < 20 ? 'bg-amber-500' : 'bg-red-500'}`}
                style={{ width: `${Math.min(100, (tokenVelocity / 30) * 100)}%` }}
              />
            </div>
            <div className="text-xs text-gray-500">Lower is better (store of value). Target: &lt;10x</div>
            
            <div className="flex items-center justify-between mt-4">
              <span className="text-gray-600">Real Yield APY</span>
              <span className={`font-bold ${realYield > 5 ? 'text-emerald-600' : realYield > 2 ? 'text-amber-600' : 'text-gray-600'}`}>
                {realYield.toFixed(1)}%
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Value Accrual Score</span>
              <span className={`font-bold ${valueAccrual >= 70 ? 'text-emerald-600' : valueAccrual >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
                {valueAccrual.toFixed(0)}/100
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Staking APY</span>
              <span className="font-bold text-indigo-600">
                {(staking?.stakingApy || (parameters.stakingApy || 0.07) * 100).toFixed(1)}%
              </span>
            </div>
          </div>
        </div>

        {/* Governance */}
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>🗳️</span> Governance & DAO
          </h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Participation Rate</span>
              <span className={`font-bold ${governanceParticipation >= 30 ? 'text-emerald-600' : governanceParticipation >= 15 ? 'text-amber-600' : 'text-red-600'}`}>
                {governanceParticipation.toFixed(1)}%
              </span>
            </div>
            <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className={`h-full ${governanceParticipation >= 30 ? 'bg-emerald-500' : governanceParticipation >= 15 ? 'bg-amber-500' : 'bg-red-500'}`}
                style={{ width: `${Math.min(100, governanceParticipation)}%` }}
              />
            </div>
            <div className="text-xs text-gray-500">Target: 30%+ participation</div>
            
            <div className="bg-slate-50 rounded-lg p-3 mt-4">
              <div className="text-sm text-slate-600 mb-2">veVCoin Voting Power</div>
              <div className="text-xs text-slate-500">
                • 1 week lock = 1x voting power<br/>
                • 4 year lock = 4x voting power<br/>
                • Quorum: 4% of voting supply
              </div>
            </div>
            
            <div className="flex items-center justify-between mt-2">
              <span className="text-gray-600">Staking Participation</span>
              <span className="font-bold text-indigo-600">
                {stakingParticipation.toFixed(1)}%
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Future Modules Overview */}
      {enabledFutureModulesCount > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-200 p-6">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>🔮</span> Enabled Future Modules ({enabledFutureModulesCount}/4)
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {futureModulesEnabled.crossPlatform && (
              <div className="bg-white rounded-lg p-3 text-center border border-purple-100">
                <span className="text-2xl">🌐</span>
                <div className="font-semibold text-sm mt-1">Cross-Platform</div>
                <div className="text-xs text-gray-500">Month 15</div>
              </div>
            )}
            {futureModulesEnabled.marketplace && (
              <div className="bg-white rounded-lg p-3 text-center border border-purple-100">
                <span className="text-2xl">🛒</span>
                <div className="font-semibold text-sm mt-1">Marketplace</div>
                <div className="text-xs text-gray-500">Month 18</div>
              </div>
            )}
            {futureModulesEnabled.businessHub && (
              <div className="bg-white rounded-lg p-3 text-center border border-purple-100">
                <span className="text-2xl">💼</span>
                <div className="font-semibold text-sm mt-1">Business Hub</div>
                <div className="text-xs text-gray-500">Month 21</div>
              </div>
            )}
            {futureModulesEnabled.vchain && (
              <div className="bg-white rounded-lg p-3 text-center border border-purple-100">
                <span className="text-2xl">🔗</span>
                <div className="font-semibold text-sm mt-1">VChain</div>
                <div className="text-xs text-gray-500">Month 24</div>
              </div>
            )}
          </div>
          <div className="mt-4 text-sm text-purple-700">
            These modules will add additional revenue streams as they launch. See the 5-Year Projection in Overview for detailed impact.
          </div>
        </div>
      )}
      
      {/* Liquidity & Staking Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>💧</span> Liquidity Status
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div className="text-xs text-blue-600">Health Score</div>
              <div className={`text-xl font-bold ${liquidityMeets70 ? 'text-emerald-600' : 'text-amber-600'}`}>
                {liquidityHealthScore.toFixed(0)}%
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div className="text-xs text-blue-600">Pool Depth</div>
              <div className="text-xl font-bold text-blue-700">
                ${formatNumber(liquidity?.initialLiquidity || parameters.initialLiquidityUsd || 0)}
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div className="text-xs text-blue-600">Slippage (1K)</div>
              <div className="text-xl font-bold text-blue-700">
                {((liquidity?.slippage1k || 0) * 100).toFixed(2)}%
              </div>
            </div>
            <div className="bg-blue-50 rounded-lg p-3 border border-blue-100">
              <div className="text-xs text-blue-600">POL Ratio</div>
              <div className="text-xl font-bold text-blue-700">
                {(liquidity?.protocolOwnedPercent || (parameters.protocolOwnedLiquidity || 0.3) * 100).toFixed(0)}%
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>🔒</span> Staking Summary
          </h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-100">
              <div className="text-xs text-indigo-600">Staked Supply</div>
              <div className="text-xl font-bold text-indigo-700">
                {formatNumber(staking?.totalStaked || 0)}
              </div>
            </div>
            <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-100">
              <div className="text-xs text-indigo-600">Participation</div>
              <div className="text-xl font-bold text-indigo-700">
                {stakingParticipation.toFixed(1)}%
              </div>
            </div>
            <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-100">
              <div className="text-xs text-indigo-600">APY</div>
              <div className="text-xl font-bold text-emerald-600">
                {(staking?.stakingApy || (parameters.stakingApy || 0.07) * 100).toFixed(1)}%
              </div>
            </div>
            <div className="bg-indigo-50 rounded-lg p-3 border border-indigo-100">
              <div className="text-xs text-indigo-600">Fee Revenue</div>
              <div className="text-xl font-bold text-indigo-700">
                ${(staking?.revenue || 0).toFixed(0)}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💡 Recommendations</h3>
        <div className="space-y-4">
          {totals.margin < 30 && (
            <div className="flex items-start gap-3 p-4 bg-amber-50 rounded-lg border border-amber-200">
              <span className="text-xl">⚠️</span>
              <div>
                <div className="font-semibold text-amber-800">Improve Profit Margins</div>
                <div className="text-sm text-amber-700">
                  Consider increasing prices or reducing operational costs to achieve 30%+ margins.
                </div>
              </div>
            </div>
          )}
          {recapture.recaptureRate < 25 && (
            <div className="flex items-start gap-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <span className="text-xl">💎</span>
              <div>
                <div className="font-semibold text-blue-800">Increase Token Recapture</div>
                <div className="text-sm text-blue-700">
                  Target 25-35% recapture rate. Increase burn rate (5%) and buyback (3%) for sustainable tokenomics.
                </div>
              </div>
            </div>
          )}
          {!liquidityMeets70 && (
            <div className="flex items-start gap-3 p-4 bg-cyan-50 rounded-lg border border-cyan-200">
              <span className="text-xl">💧</span>
              <div>
                <div className="font-semibold text-cyan-800">Improve Liquidity Health</div>
                <div className="text-sm text-cyan-700">
                  Current health score: {liquidityHealthScore.toFixed(0)}%. Add more liquidity to achieve 70%+ health and reduce slippage.
                </div>
              </div>
            </div>
          )}
          {ltvCacRatio < 3 && (
            <div className="flex items-start gap-3 p-4 bg-purple-50 rounded-lg border border-purple-200">
              <span className="text-xl">📊</span>
              <div>
                <div className="font-semibold text-purple-800">Improve Unit Economics</div>
                <div className="text-sm text-purple-700">
                  LTV/CAC is {ltvCacRatio.toFixed(1)}x. Target 3x+ by increasing monetization or reducing CAC.
                </div>
              </div>
            </div>
          )}
          {!stakingHealthy && (
            <div className="flex items-start gap-3 p-4 bg-indigo-50 rounded-lg border border-indigo-200">
              <span className="text-xl">🔒</span>
              <div>
                <div className="font-semibold text-indigo-800">Boost Staking Participation</div>
                <div className="text-sm text-indigo-700">
                  Staking participation at {stakingParticipation.toFixed(1)}%. Consider increasing APY or fee discounts to attract more stakers.
                </div>
              </div>
            </div>
          )}
          {customerAcquisition.blendedCAC > arpu * 3 && (
            <div className="flex items-start gap-3 p-4 bg-red-50 rounded-lg border border-red-200">
              <span className="text-xl">🚨</span>
              <div>
                <div className="font-semibold text-red-800">High Customer Acquisition Cost</div>
                <div className="text-sm text-red-700">
                  CAC is high relative to ARPU. Focus on organic growth or increase monetization.
                </div>
              </div>
            </div>
          )}
          {totals.margin >= 30 && ltvCacRatio >= 3 && liquidityMeets70 && (
            <div className="flex items-start gap-3 p-4 bg-emerald-50 rounded-lg border border-emerald-200">
              <span className="text-xl">✅</span>
              <div>
                <div className="font-semibold text-emerald-800">Healthy Economy</div>
                <div className="text-sm text-emerald-700">
                  Your token economy meets all key targets. Continue monitoring and scaling while maintaining these metrics.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}


