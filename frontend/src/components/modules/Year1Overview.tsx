'use client';

import { useState, useMemo } from 'react';
import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency, getMarginStatus, getRecaptureStatus } from '@/lib/utils';
import { GROWTH_SCENARIOS, MARKET_CONDITIONS } from '@/lib/constants';

interface Year1OverviewProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

// Dynamic allocation formula (matches backend)
function calculateDynamicAllocation(
  currentUsers: number,
  tokenPrice: number,
  initialUsers: number = 1000,
  targetUsers: number = 1000000,
  minAllocation: number = 0.05,
  maxAllocation: number = 0.90,
  maxPerUserMonthlyUsd: number = 50.0,
  monthlyEmission: number = 5833333
): { allocation: number; growthFactor: number; perUserUsd: number; capped: boolean } {
  const users = Math.max(1, currentUsers);
  
  let growthFactor = 0;
  if (users <= initialUsers) {
    growthFactor = 0;
  } else if (users >= targetUsers) {
    growthFactor = 1;
  } else {
    growthFactor = Math.min(1, Math.max(0, 
      Math.log(users / initialUsers) / Math.log(targetUsers / initialUsers)
    ));
  }
  
  let allocation = minAllocation + (maxAllocation - minAllocation) * growthFactor;
  
  const grossEmission = monthlyEmission * allocation;
  const netEmission = grossEmission * 0.95;
  const perUserVcoin = netEmission / users;
  let perUserUsd = perUserVcoin * tokenPrice;
  
  let capped = false;
  if (perUserUsd > maxPerUserMonthlyUsd) {
    const requiredNetEmission = (maxPerUserMonthlyUsd / tokenPrice) * users;
    const requiredGross = requiredNetEmission / 0.95;
    allocation = Math.max(minAllocation, requiredGross / monthlyEmission);
    perUserUsd = maxPerUserMonthlyUsd;
    capped = true;
  }
  
  return { allocation, growthFactor, perUserUsd, capped };
}

// Calculate monthly projections for Year 1
function calculateMonthlyProjections(
  baseResult: SimulationResult,
  scenarioConfig: typeof GROWTH_SCENARIOS['base'],
  marketConfig: typeof MARKET_CONDITIONS['bull'],
  baseTokenPrice: number,
  enableDynamicAllocation: boolean = true,
  initialUsersForAllocation: number = 1000,
  targetUsersForMaxAllocation: number = 1000000,
  maxPerUserMonthlyUsd: number = 50.0
) {
  const projections = [];
  const baseUsers = baseResult.customerAcquisition.totalUsers;
  const baseRevenue = baseResult.totals.revenue;
  const baseCosts = baseResult.totals.costs;
  
  const stakingRevenue = baseResult.staking?.revenue || 0;
  const contentVcoinRevenue = (Number(baseResult.content?.breakdown?.postFeesVcoin) || 0) * baseTokenPrice;
  const tokenBasedRevenue = stakingRevenue + contentVcoinRevenue;
  const usdFixedRevenue = baseRevenue - tokenBasedRevenue;
  
  let currentUsers = baseUsers;
  let cumulativeRevenue = 0;
  let cumulativeProfit = 0;
  
  const baseAllocation = 0.08;
  
  for (let month = 1; month <= 12; month++) {
    const growthRate = scenarioConfig.monthlyGrowthRates[month - 1] || 0;
    const adjustedGrowthRate = growthRate * marketConfig.growthMultiplier;
    
    if (month > 1) {
      currentUsers = Math.max(1, Math.round(currentUsers * (1 + adjustedGrowthRate)));
    }
    
    let priceMultiplier: number;
    if (month <= 6) {
      const t = month / 6;
      priceMultiplier = 1 + (scenarioConfig.tokenPriceMonth6Multiplier - 1) * t;
    } else {
      const t = (month - 6) / 6;
      priceMultiplier = scenarioConfig.tokenPriceMonth6Multiplier + 
        (scenarioConfig.tokenPriceEndMultiplier - scenarioConfig.tokenPriceMonth6Multiplier) * t;
    }
    priceMultiplier *= marketConfig.priceMultiplier;
    const tokenPrice = baseTokenPrice * priceMultiplier;
    
    const dynamicAlloc = enableDynamicAllocation 
      ? calculateDynamicAllocation(
          currentUsers, 
          tokenPrice,
          initialUsersForAllocation,
          targetUsersForMaxAllocation,
          0.05,
          0.90,
          maxPerUserMonthlyUsd
        )
      : { allocation: baseAllocation, growthFactor: 0, perUserUsd: 0, capped: false };
    
    const grossEmission = 5833333 * dynamicAlloc.allocation;
    const platformFeeVcoin = grossEmission * 0.05;
    const platformFeeUsd = platformFeeVcoin * tokenPrice;
    
    let monthRevenue: number;
    let monthCosts: number;
    let monthProfit: number;
    
    const userScaleFactor = currentUsers / baseUsers;
    
    if (month === 1) {
      monthRevenue = baseRevenue;
      monthCosts = baseCosts;
      monthProfit = baseResult.totals.profit;
    } else {
      const scaledTokenRevenue = tokenBasedRevenue * userScaleFactor * priceMultiplier;
      const scaledUsdRevenue = usdFixedRevenue * userScaleFactor;
      const basePlatformFee = baseResult.platformFees?.rewardFeeUsd || 0;
      const scaledPlatformFee = enableDynamicAllocation ? platformFeeUsd : basePlatformFee * userScaleFactor;
      
      monthRevenue = scaledTokenRevenue + scaledUsdRevenue + (scaledPlatformFee - basePlatformFee * userScaleFactor);
      monthCosts = baseCosts * Math.sqrt(userScaleFactor);
      monthProfit = monthRevenue - monthCosts;
    }
    const monthMargin = monthRevenue > 0 ? (monthProfit / monthRevenue) * 100 : 0;
    
    cumulativeRevenue += monthRevenue;
    cumulativeProfit += monthProfit;
    
    const fomoEvent = scenarioConfig.fomoEvents.find(e => e.month === month);
    
    projections.push({
      month,
      users: currentUsers,
      revenue: monthRevenue,
      costs: monthCosts,
      profit: monthProfit,
      margin: monthMargin,
      tokenPrice,
      priceMultiplier,
      growthRate: adjustedGrowthRate * 100,
      cumulativeRevenue,
      cumulativeProfit,
      fomoEvent: fomoEvent || null,
      allocation: dynamicAlloc.allocation * 100,
      growthFactor: dynamicAlloc.growthFactor * 100,
      perUserUsd: dynamicAlloc.perUserUsd,
      allocationCapped: dynamicAlloc.capped,
      platformFeeUsd,
    });
  }
  
  return projections;
}

export function Year1Overview({ result, parameters }: Year1OverviewProps) {
  const [selectedMonth, setSelectedMonth] = useState(1);
  
  const scenario = (parameters.growthScenario || 'base') as keyof typeof GROWTH_SCENARIOS;
  const marketCondition = (parameters.marketCondition || 'bull') as keyof typeof MARKET_CONDITIONS;
  const scenarioConfig = GROWTH_SCENARIOS[scenario];
  const marketConfig = MARKET_CONDITIONS[marketCondition];
  const useGrowthScenarios = parameters.useGrowthScenarios || false;
  const enableDynamicAllocation = parameters.enableDynamicAllocation !== false;
  
  const monthlyProjections = useMemo(() => {
    if (!useGrowthScenarios) return null;
    return calculateMonthlyProjections(
      result, scenarioConfig, marketConfig, parameters.tokenPrice,
      enableDynamicAllocation, parameters.initialUsersForAllocation,
      parameters.targetUsersForMaxAllocation, parameters.maxPerUserMonthlyUsd
    );
  }, [result, scenarioConfig, marketConfig, parameters.tokenPrice, useGrowthScenarios,
      enableDynamicAllocation, parameters.initialUsersForAllocation,
      parameters.targetUsersForMaxAllocation, parameters.maxPerUserMonthlyUsd]);
  
  const currentMonthData = monthlyProjections?.[selectedMonth - 1] || null;
  
  const modules = [
    { name: 'Identity', data: result.identity, color: 'violet', icon: '🆔', enabled: true },
    { name: 'Content', data: result.content, color: 'pink', icon: '📄', enabled: true },
    { name: 'Advertising', data: result.advertising, color: 'blue', icon: '📢', enabled: parameters.enableAdvertising },
    { name: 'Exchange', data: result.exchange, color: 'teal', icon: '💱', enabled: parameters.enableExchange },
    { name: 'Staking', data: result.staking ? { 
      revenue: result.staking.revenue, costs: result.staking.costs, 
      profit: result.staking.profit, margin: result.staking.margin 
    } : { revenue: 0, costs: 0, profit: 0, margin: 0 }, color: 'indigo', icon: '🔒', enabled: true },
  ];
  
  const marginStatus = getMarginStatus(result.totals.margin);
  const recaptureStatus = getRecaptureStatus(result.recapture.recaptureRate);

  return (
    <section className="space-y-8">
      {/* Hero Stats - First Year Focus */}
      <div className="bg-gradient-to-br from-indigo-600 via-purple-600 to-pink-500 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">📅</span>
          <div>
            <h2 className="text-2xl font-bold">Year 1 Financial Overview</h2>
            <p className="text-indigo-200">First 12 months projections and performance metrics</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-3xl font-bold">{formatCurrency(result.totals.revenue)}</div>
            <div className="text-sm text-indigo-200 uppercase font-semibold mt-1">M1 Revenue</div>
          </div>
          <div className="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-3xl font-bold ${result.totals.profit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(result.totals.profit)}
            </div>
            <div className="text-sm text-indigo-200 uppercase font-semibold mt-1">M1 Profit</div>
          </div>
          <div className="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-3xl font-bold">{result.totals.margin.toFixed(1)}%</div>
            <div className="text-sm text-indigo-200 uppercase font-semibold mt-1">Profit Margin</div>
          </div>
          <div className="bg-white/15 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-3xl font-bold">{formatNumber(result.customerAcquisition.totalUsers)}</div>
            <div className="text-sm text-indigo-200 uppercase font-semibold mt-1">Active Users</div>
          </div>
        </div>
      </div>

      {/* 12-Month Timeline (when growth scenarios enabled) */}
      {useGrowthScenarios && monthlyProjections && currentMonthData && (
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-lg flex items-center gap-2">
              <span>📈</span> 12-Month Projection Timeline
            </h3>
            <div className={`px-3 py-1 rounded-full text-sm font-bold ${
              scenario === 'bullish' ? 'bg-emerald-100 text-emerald-700' :
              scenario === 'conservative' ? 'bg-blue-100 text-blue-700' :
              'bg-purple-100 text-purple-700'
            }`}>
              Month {selectedMonth}
              {currentMonthData.fomoEvent && <span className="ml-2">⚡</span>}
            </div>
          </div>

          {/* Month Slider */}
          <div className="mb-6">
            <input
              type="range"
              min={1}
              max={12}
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(Number(e.target.value) || 1)}
              className="w-full h-3 rounded-full appearance-none cursor-pointer"
              style={{
                background: `linear-gradient(to right, 
                  ${scenario === 'bullish' ? '#10b981' : scenario === 'conservative' ? '#3b82f6' : '#a855f7'} 0%, 
                  ${scenario === 'bullish' ? '#10b981' : scenario === 'conservative' ? '#3b82f6' : '#a855f7'} ${((selectedMonth - 1) / 11) * 100}%, 
                  #e5e7eb ${((selectedMonth - 1) / 11) * 100}%, 
                  #e5e7eb 100%)`
              }}
            />
            <div className="flex justify-between mt-2 text-xs text-gray-500">
              {monthlyProjections.map((m) => (
                <button
                  key={m.month}
                  onClick={() => setSelectedMonth(m.month)}
                  className={`w-6 h-6 rounded-full flex items-center justify-center transition-all ${
                    m.month === selectedMonth
                      ? scenario === 'bullish' ? 'bg-emerald-500 text-white' :
                        scenario === 'conservative' ? 'bg-blue-500 text-white' : 'bg-purple-500 text-white'
                      : m.fomoEvent ? 'bg-amber-100 text-amber-700 hover:bg-amber-200' : 'hover:bg-gray-100'
                  }`}
                  title={m.fomoEvent ? m.fomoEvent.description : `Month ${m.month}`}
                >
                  {m.fomoEvent ? '⚡' : m.month}
                </button>
              ))}
            </div>
          </div>

          {/* Current Month Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-blue-700">{formatNumber(currentMonthData.users)}</div>
              <div className="text-xs text-blue-600 uppercase font-semibold">Active Users</div>
              <div className="text-xs text-gray-500 mt-1">
                {currentMonthData.growthRate > 0 ? '+' : ''}{currentMonthData.growthRate.toFixed(1)}% growth
              </div>
            </div>
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-emerald-700">{formatCurrency(currentMonthData.revenue)}</div>
              <div className="text-xs text-emerald-600 uppercase font-semibold">Monthly Revenue</div>
            </div>
            <div className={`bg-gradient-to-br ${currentMonthData.profit >= 0 ? 'from-green-50 to-green-100' : 'from-red-50 to-red-100'} rounded-xl p-4 text-center`}>
              <div className={`text-2xl font-bold ${currentMonthData.profit >= 0 ? 'text-green-700' : 'text-red-700'}`}>
                {formatCurrency(currentMonthData.profit)}
              </div>
              <div className={`text-xs uppercase font-semibold ${currentMonthData.profit >= 0 ? 'text-green-600' : 'text-red-600'}`}>Monthly Profit</div>
            </div>
            <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-amber-700">${currentMonthData.tokenPrice.toFixed(4)}</div>
              <div className="text-xs text-amber-600 uppercase font-semibold">Token Price</div>
            </div>
            {enableDynamicAllocation && (
              <div className={`bg-gradient-to-br ${currentMonthData.allocationCapped ? 'from-red-50 to-red-100' : 'from-purple-50 to-purple-100'} rounded-xl p-4 text-center`}>
                <div className={`text-2xl font-bold ${currentMonthData.allocationCapped ? 'text-red-700' : 'text-purple-700'}`}>
                  {currentMonthData.allocation?.toFixed(1)}%
                </div>
                <div className={`text-xs uppercase font-semibold ${currentMonthData.allocationCapped ? 'text-red-600' : 'text-purple-600'}`}>
                  Reward Alloc{currentMonthData.allocationCapped && ' (CAP)'}
                </div>
              </div>
            )}
          </div>

          {/* Cumulative Totals */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-600">Cumulative Revenue (M1-{selectedMonth})</div>
              <div className="text-xl font-bold text-gray-800">{formatCurrency(currentMonthData.cumulativeRevenue)}</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-600">Cumulative Profit (M1-{selectedMonth})</div>
              <div className={`text-xl font-bold ${currentMonthData.cumulativeProfit >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                {formatCurrency(currentMonthData.cumulativeProfit)}
              </div>
            </div>
          </div>

          {currentMonthData.fomoEvent && (
            <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="text-2xl">⚡</span>
                <div>
                  <h4 className="font-bold text-amber-800">
                    FOMO Event: {currentMonthData.fomoEvent.eventType.split('_').map(
                      (w: string) => w.charAt(0).toUpperCase() + w.slice(1)
                    ).join(' ')}
                  </h4>
                  <p className="text-sm text-amber-700">{currentMonthData.fomoEvent.description}</p>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Module Performance Grid */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>📊</span> Core Module Performance (Month 1)
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {modules.filter(m => m.enabled).map((module) => (
            <div 
              key={module.name}
              className={`bg-gradient-to-br from-${module.color}-50 to-${module.color}-100 border border-${module.color}-200 rounded-xl p-4`}
            >
              <div className="flex items-center gap-2 mb-3">
                <span className="text-2xl">{module.icon}</span>
                <span className="font-bold text-gray-800">{module.name}</span>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600 text-sm">Revenue</span>
                  <span className="font-semibold">{formatCurrency(module.data.revenue)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600 text-sm">Costs</span>
                  <span className="font-semibold text-amber-600">{formatCurrency(module.data.costs)}</span>
                </div>
                <div className="flex justify-between pt-2 border-t border-gray-200">
                  <span className="text-gray-600 text-sm">Profit</span>
                  <span className={`font-bold ${module.data.profit >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                    {formatCurrency(module.data.profit)}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Key Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Rewards */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h4 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>🎁</span> Rewards Distribution
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Daily Reward Pool</span>
              <span className="font-semibold">{formatNumber(result.rewards.dailyRewardPool)} VC</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Monthly Emission</span>
              <span className="font-semibold">{formatNumber(result.rewards.monthlyRewardPool)} VC</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Platform Fee (5%)</span>
              <span className="font-semibold text-purple-600">{formatCurrency(result.platformFees.rewardFeeUsd)}</span>
            </div>
            <div className="flex justify-between pt-2 border-t">
              <span className="text-gray-600">Allocation</span>
              <span className="font-bold">{(result.rewards.allocationPercent).toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Recapture */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h4 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>🔄</span> Token Recapture
          </h4>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Total Recaptured</span>
              <span className="font-semibold">{formatNumber(result.recapture.totalRecaptured)} VC</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Burns</span>
              <span className="font-semibold text-red-600">{formatNumber(result.recapture.burns)} VC</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Buybacks</span>
              <span className="font-semibold text-blue-600">{formatNumber(result.recapture.buybacks)} VC</span>
            </div>
            <div className="flex justify-between pt-2 border-t">
              <span className="text-gray-600">Recapture Rate</span>
              <span className={`font-bold ${recaptureStatus.color}`}>{result.recapture.recaptureRate.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Liquidity & Staking */}
        <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
          <h4 className="font-bold text-lg mb-4 flex items-center gap-2">
            <span>💧</span> Liquidity & Staking
          </h4>
          <div className="space-y-3">
            {result.liquidity && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600">Liquidity Health</span>
                  <span className={`font-semibold ${result.liquidity.healthScore >= 70 ? 'text-emerald-600' : 'text-amber-600'}`}>
                    {result.liquidity.healthScore.toFixed(0)}%
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Initial Liquidity</span>
                  <span className="font-semibold">{formatCurrency(result.liquidity.initialLiquidity)}</span>
                </div>
              </>
            )}
            {result.staking && (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-600">Staking APY</span>
                  <span className="font-semibold text-indigo-600">{result.staking.stakingApy.toFixed(1)}%</span>
                </div>
                <div className="flex justify-between pt-2 border-t">
                  <span className="text-gray-600">Total Staked</span>
                  <span className="font-bold">{formatNumber(result.staking.totalStaked)} VC</span>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Customer Acquisition */}
      <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>👥</span> Customer Acquisition Breakdown
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-700">{result.customerAcquisition.totalUsers}</div>
            <div className="text-sm text-blue-600">Total Users</div>
          </div>
          <div className="bg-emerald-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-emerald-700">{formatCurrency(result.customerAcquisition.blendedCAC)}</div>
            <div className="text-sm text-emerald-600">Blended CAC</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-700">{result.customerAcquisition.northAmericaUsers}</div>
            <div className="text-sm text-purple-600">NA Users</div>
          </div>
          <div className="bg-amber-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-amber-700">{result.customerAcquisition.globalLowIncomeUsers}</div>
            <div className="text-sm text-amber-600">Global Users</div>
          </div>
        </div>
      </div>
    </section>
  );
}

