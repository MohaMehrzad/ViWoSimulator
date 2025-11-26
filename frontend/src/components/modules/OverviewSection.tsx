'use client';

import { useState, useMemo } from 'react';
import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency, getMarginStatus, getRecaptureStatus } from '@/lib/utils';
import { GROWTH_SCENARIOS, MARKET_CONDITIONS } from '@/lib/constants';

interface OverviewSectionProps {
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
  
  // Logarithmic growth factor
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
  
  // Calculate allocation
  let allocation = minAllocation + (maxAllocation - minAllocation) * growthFactor;
  
  // Calculate per-user reward
  const grossEmission = monthlyEmission * allocation;
  const netEmission = grossEmission * 0.95; // After 5% platform fee
  const perUserVcoin = netEmission / users;
  let perUserUsd = perUserVcoin * tokenPrice;
  
  // Apply cap
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

// Calculate monthly projections based on growth scenario
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
  
  // Separate token-based revenue (affected by price) from USD-fixed revenue
  // Staking, Content fees, etc. are in VCoin - their USD value scales with token price
  const stakingRevenue = baseResult.staking?.revenue || 0;
  const contentVcoinRevenue = (baseResult.content?.breakdown?.postFeesVcoin || 0) * baseTokenPrice;
  const tokenBasedRevenue = stakingRevenue + contentVcoinRevenue;
  const usdFixedRevenue = baseRevenue - tokenBasedRevenue;
  
  // Initial multiplier (Month 1)
  const month1Multiplier = scenarioConfig.month1FomoMultiplier * marketConfig.fomoMultiplier * 0.3;
  let currentUsers = baseUsers;
  let cumulativeRevenue = 0;
  let cumulativeProfit = 0;
  
  // Track allocation-based profit
  let cumulativeAllocationProfit = 0;
  const baseAllocation = 0.08; // Default static allocation
  
  for (let month = 1; month <= 12; month++) {
    // Calculate growth for this month
    const growthRate = scenarioConfig.monthlyGrowthRates[month - 1] || 0;
    const adjustedGrowthRate = growthRate * marketConfig.growthMultiplier;
    
    // Apply growth (Month 1 uses base, subsequent months grow)
    if (month > 1) {
      currentUsers = Math.max(1, Math.round(currentUsers * (1 + adjustedGrowthRate)));
    }
    
    // Calculate token price for this month
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
    
    // Calculate dynamic allocation for this month
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
    
    // Calculate platform fee revenue based on allocation
    // Platform fee = 5% of (monthlyEmission * allocation)
    const grossEmission = 5833333 * dynamicAlloc.allocation;
    const platformFeeVcoin = grossEmission * 0.05;
    const platformFeeUsd = platformFeeVcoin * tokenPrice;
    
    // Static allocation platform fee (for comparison)
    const staticGrossEmission = 5833333 * baseAllocation;
    const staticPlatformFeeUsd = staticGrossEmission * 0.05 * tokenPrice;
    
    // Additional profit from dynamic allocation
    const allocationProfitBoost = platformFeeUsd - staticPlatformFeeUsd;
    cumulativeAllocationProfit += allocationProfitBoost;
    
    // Scale revenue based on user count AND token price
    const userScaleFactor = currentUsers / baseUsers;
    
    // Token-based revenue scales with BOTH users AND token price
    const scaledTokenRevenue = tokenBasedRevenue * userScaleFactor * priceMultiplier;
    // USD-fixed revenue scales with users only
    const scaledUsdRevenue = usdFixedRevenue * userScaleFactor;
    
    // Add platform fee to revenue (this now scales with allocation!)
    const basePlatformFee = baseResult.platformFees?.rewardFeeUsd || 0;
    const scaledPlatformFee = enableDynamicAllocation ? platformFeeUsd : basePlatformFee * userScaleFactor;
    
    const monthRevenue = scaledTokenRevenue + scaledUsdRevenue + (scaledPlatformFee - basePlatformFee * userScaleFactor);
    
    // Costs scale sub-linearly with users (economies of scale)
    const monthCosts = baseCosts * Math.sqrt(userScaleFactor);
    const monthProfit = monthRevenue - monthCosts;
    const monthMargin = monthRevenue > 0 ? (monthProfit / monthRevenue) * 100 : 0;
    
    cumulativeRevenue += monthRevenue;
    cumulativeProfit += monthProfit;
    
    // Check for FOMO event
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
      // Dynamic allocation fields
      allocation: dynamicAlloc.allocation * 100,
      growthFactor: dynamicAlloc.growthFactor * 100,
      perUserUsd: dynamicAlloc.perUserUsd,
      allocationCapped: dynamicAlloc.capped,
      platformFeeUsd,
      allocationProfitBoost,
      cumulativeAllocationProfit,
      // Breakdown for debugging
      tokenBasedRevenue: scaledTokenRevenue,
      usdFixedRevenue: scaledUsdRevenue,
    });
  }
  
  return projections;
}

export function OverviewSection({ result, parameters }: OverviewSectionProps) {
  const [selectedMonth, setSelectedMonth] = useState(1);
  
  const marginStatus = getMarginStatus(result.totals.margin);
  const recaptureStatus = getRecaptureStatus(result.recapture.recaptureRate);
  
  // Check if growth scenarios are enabled
  const useGrowthScenarios = parameters.useGrowthScenarios || false;
  const scenario = parameters.growthScenario || 'base';
  const marketCondition = parameters.marketCondition || 'bull';
  const scenarioConfig = GROWTH_SCENARIOS[scenario];
  const marketConfig = MARKET_CONDITIONS[marketCondition];
  
  // Check if dynamic allocation is enabled
  const enableDynamicAllocation = parameters.enableDynamicAllocation !== false;
  
  // Calculate monthly projections when growth scenarios are enabled
  const monthlyProjections = useMemo(() => {
    if (!useGrowthScenarios) return null;
    return calculateMonthlyProjections(
      result,
      scenarioConfig,
      marketConfig,
      parameters.tokenPrice,
      enableDynamicAllocation,
      parameters.initialUsersForAllocation || 1000,
      parameters.targetUsersForMaxAllocation || 1000000,
      parameters.maxPerUserMonthlyUsd || 50
    );
  }, [result, scenarioConfig, marketConfig, parameters.tokenPrice, useGrowthScenarios, 
      enableDynamicAllocation, parameters.initialUsersForAllocation, 
      parameters.targetUsersForMaxAllocation, parameters.maxPerUserMonthlyUsd]);
  
  // Get current month's data
  const currentMonthData = monthlyProjections?.[selectedMonth - 1] || null;

  const modules = [
    { name: 'Identity', data: result.identity, color: 'violet', enabled: true },
    { name: 'Content', data: result.content, color: 'pink', enabled: true },
    { name: 'Community', data: result.community, color: 'emerald', enabled: parameters.enableCommunity },
    { name: 'Advertising', data: result.advertising, color: 'blue', enabled: parameters.enableAdvertising },
    { name: 'Messaging', data: result.messaging, color: 'cyan', enabled: parameters.enableMessaging },
    { name: 'Exchange', data: result.exchange, color: 'teal', enabled: parameters.enableExchange },
    { name: 'Staking', data: result.staking ? { 
      revenue: result.staking.revenue, 
      costs: result.staking.costs, 
      profit: result.staking.profit, 
      margin: result.staking.margin 
    } : { revenue: 0, costs: 0, profit: 0, margin: 0 }, color: 'indigo', enabled: true },
  ];

  return (
    <section className="space-y-8">
      {/* Growth Scenario Banner (when enabled) */}
      {useGrowthScenarios && (
        <div className={`rounded-xl p-4 border-2 ${
          scenario === 'bullish' ? 'bg-emerald-50 border-emerald-300' :
          scenario === 'conservative' ? 'bg-blue-50 border-blue-300' :
          'bg-purple-50 border-purple-300'
        }`}>
          <div className="flex items-center justify-between flex-wrap gap-3">
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
                  {scenarioConfig.name} Growth Scenario Active
                </h4>
                <p className="text-sm text-gray-600">
                  {marketConfig.name} conditions • {(scenarioConfig.month1FomoMultiplier * marketConfig.fomoMultiplier * 0.3).toFixed(1)}x user multiplier
                </p>
              </div>
            </div>
            <div className="flex gap-4 text-sm">
              <div className="text-center">
                <div className={`font-bold ${
                  scenario === 'bullish' ? 'text-emerald-600' :
                  scenario === 'conservative' ? 'text-blue-600' :
                  'text-purple-600'
                }`}>{formatNumber(result.customerAcquisition.totalUsers)}</div>
                <div className="text-gray-500 text-xs">Scenario Users</div>
              </div>
              <div className="text-center">
                <div className="font-bold text-amber-600">
                  {scenarioConfig.tokenPriceEndMultiplier * marketConfig.priceMultiplier}x
                </div>
                <div className="text-gray-500 text-xs">Price Target (12mo)</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* 12-Month Timeline Slider (when growth scenarios enabled) */}
      {useGrowthScenarios && monthlyProjections && currentMonthData && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-bold text-lg">📅 12-Month Projection Timeline</h3>
            <div className={`px-3 py-1 rounded-full text-sm font-bold ${
              scenario === 'bullish' ? 'bg-emerald-100 text-emerald-700' :
              scenario === 'conservative' ? 'bg-blue-100 text-blue-700' :
              'bg-purple-100 text-purple-700'
            }`}>
              Month {selectedMonth}
              {currentMonthData.fomoEvent && (
                <span className="ml-2">⚡</span>
              )}
            </div>
          </div>

          {/* Month Slider */}
          <div className="mb-6">
            <input
              type="range"
              min={1}
              max={12}
              value={selectedMonth}
              onChange={(e) => setSelectedMonth(Number(e.target.value))}
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
                        scenario === 'conservative' ? 'bg-blue-500 text-white' :
                        'bg-purple-500 text-white'
                      : m.fomoEvent 
                        ? 'bg-amber-100 text-amber-700 hover:bg-amber-200' 
                        : 'hover:bg-gray-100'
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
              <div className="text-3xl font-bold text-blue-700">
                {formatNumber(currentMonthData.users)}
              </div>
              <div className="text-xs text-blue-600 uppercase font-semibold">Active Users</div>
              <div className="text-xs text-gray-500 mt-1">
                {currentMonthData.growthRate > 0 ? '+' : ''}{currentMonthData.growthRate.toFixed(1)}% growth
              </div>
            </div>
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-emerald-700">
                {formatCurrency(currentMonthData.revenue)}
              </div>
              <div className="text-xs text-emerald-600 uppercase font-semibold">Monthly Revenue</div>
            </div>
            <div className={`bg-gradient-to-br ${
              currentMonthData.profit >= 0 
                ? 'from-green-50 to-green-100' 
                : 'from-red-50 to-red-100'
            } rounded-xl p-4 text-center`}>
              <div className={`text-3xl font-bold ${
                currentMonthData.profit >= 0 ? 'text-green-700' : 'text-red-700'
              }`}>
                {formatCurrency(currentMonthData.profit)}
              </div>
              <div className={`text-xs uppercase font-semibold ${
                currentMonthData.profit >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>Monthly Profit</div>
              <div className="text-xs text-gray-500 mt-1">
                {currentMonthData.margin.toFixed(1)}% margin
              </div>
            </div>
            <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-amber-700">
                ${currentMonthData.tokenPrice.toFixed(4)}
              </div>
              <div className="text-xs text-amber-600 uppercase font-semibold">Token Price</div>
              <div className="text-xs text-gray-500 mt-1">
                {currentMonthData.priceMultiplier.toFixed(2)}x from launch
              </div>
            </div>
            {/* Dynamic Allocation Card */}
            {enableDynamicAllocation && (
              <div className={`bg-gradient-to-br ${
                currentMonthData.allocationCapped 
                  ? 'from-red-50 to-red-100' 
                  : 'from-purple-50 to-purple-100'
              } rounded-xl p-4 text-center`}>
                <div className={`text-3xl font-bold ${
                  currentMonthData.allocationCapped ? 'text-red-700' : 'text-purple-700'
                }`}>
                  {currentMonthData.allocation?.toFixed(1)}%
                </div>
                <div className={`text-xs uppercase font-semibold ${
                  currentMonthData.allocationCapped ? 'text-red-600' : 'text-purple-600'
                }`}>
                  Reward Allocation
                  {currentMonthData.allocationCapped && ' (CAPPED)'}
                </div>
                <div className="text-xs text-gray-500 mt-1">
                  ${currentMonthData.perUserUsd?.toFixed(2)}/user/mo
                </div>
              </div>
            )}
          </div>
          
          {/* Dynamic Allocation Profit Boost */}
          {enableDynamicAllocation && currentMonthData.cumulativeAllocationProfit > 0 && (
            <div className="bg-gradient-to-r from-purple-100 to-indigo-100 border border-purple-300 rounded-lg p-4 mb-4">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">🎯</span>
                  <div>
                    <div className="font-bold text-purple-800">Dynamic Allocation Profit Boost</div>
                    <div className="text-sm text-purple-600">
                      Additional revenue from scaling allocation with user growth
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-purple-700">
                    +{formatCurrency(currentMonthData.cumulativeAllocationProfit)}
                  </div>
                  <div className="text-xs text-purple-500">
                    Cumulative through Month {selectedMonth}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Cumulative Totals */}
          <div className="grid grid-cols-2 gap-4 mt-4 pt-4 border-t border-gray-200">
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-600">Cumulative Revenue (Months 1-{selectedMonth})</div>
              <div className="text-xl font-bold text-gray-800">
                {formatCurrency(currentMonthData.cumulativeRevenue)}
              </div>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-center">
              <div className="text-sm text-gray-600">Cumulative Profit (Months 1-{selectedMonth})</div>
              <div className={`text-xl font-bold ${
                currentMonthData.cumulativeProfit >= 0 ? 'text-emerald-600' : 'text-red-600'
              }`}>
                {formatCurrency(currentMonthData.cumulativeProfit)}
              </div>
            </div>
          </div>

          {/* FOMO Event Alert */}
          {currentMonthData.fomoEvent && (
            <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="text-2xl">⚡</span>
                <div>
                  <h4 className="font-bold text-amber-800">
                    FOMO Event: {currentMonthData.fomoEvent.eventType.split('_').map(
                      w => w.charAt(0).toUpperCase() + w.slice(1)
                    ).join(' ')}
                  </h4>
                  <p className="text-sm text-amber-700">{currentMonthData.fomoEvent.description}</p>
                  <p className="text-xs text-amber-600 mt-1">
                    Impact: {currentMonthData.fomoEvent.impactMultiplier}x boost
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Month 1 vs Month 12 Comparison */}
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-semibold text-gray-700 mb-3">📊 First Month vs Last Month</h4>
            <div className="grid grid-cols-4 gap-2 text-center text-sm">
              <div></div>
              <div className="font-semibold text-gray-600">Month 1</div>
              <div className="font-semibold text-gray-600">Month 12</div>
              <div className="font-semibold text-gray-600">Change</div>
              
              <div className="text-left text-gray-600">Users</div>
              <div>{formatNumber(monthlyProjections[0].users)}</div>
              <div>{formatNumber(monthlyProjections[11].users)}</div>
              <div className={monthlyProjections[11].users >= monthlyProjections[0].users ? 'text-emerald-600' : 'text-red-600'}>
                {((monthlyProjections[11].users / monthlyProjections[0].users - 1) * 100).toFixed(0)}%
              </div>
              
              <div className="text-left text-gray-600">Revenue</div>
              <div>{formatCurrency(monthlyProjections[0].revenue)}</div>
              <div>{formatCurrency(monthlyProjections[11].revenue)}</div>
              <div className={monthlyProjections[11].revenue >= monthlyProjections[0].revenue ? 'text-emerald-600' : 'text-red-600'}>
                {((monthlyProjections[11].revenue / monthlyProjections[0].revenue - 1) * 100).toFixed(0)}%
              </div>
              
              <div className="text-left text-gray-600">Profit</div>
              <div className={monthlyProjections[0].profit >= 0 ? 'text-emerald-600' : 'text-red-600'}>
                {formatCurrency(monthlyProjections[0].profit)}
              </div>
              <div className={monthlyProjections[11].profit >= 0 ? 'text-emerald-600' : 'text-red-600'}>
                {formatCurrency(monthlyProjections[11].profit)}
              </div>
              <div className={monthlyProjections[11].profit >= monthlyProjections[0].profit ? 'text-emerald-600' : 'text-red-600'}>
                {monthlyProjections[0].profit !== 0 
                  ? `${((monthlyProjections[11].profit / monthlyProjections[0].profit - 1) * 100).toFixed(0)}%`
                  : 'N/A'
                }
              </div>
              
              <div className="text-left text-gray-600">Token Price</div>
              <div className="text-amber-600">${monthlyProjections[0].tokenPrice.toFixed(4)}</div>
              <div className="text-amber-600">${monthlyProjections[11].tokenPrice.toFixed(4)}</div>
              <div className="text-amber-600">
                {((monthlyProjections[11].tokenPrice / monthlyProjections[0].tokenPrice - 1) * 100).toFixed(0)}%
              </div>
              
              {/* Dynamic Allocation Row */}
              {enableDynamicAllocation && (
                <>
                  <div className="text-left text-purple-700 font-semibold">Allocation</div>
                  <div className="text-purple-600">{monthlyProjections[0].allocation?.toFixed(1)}%</div>
                  <div className="text-purple-600">{monthlyProjections[11].allocation?.toFixed(1)}%</div>
                  <div className="text-purple-600 font-bold">
                    +{((monthlyProjections[11].allocation || 0) - (monthlyProjections[0].allocation || 0)).toFixed(1)}%
                  </div>
                  
                  <div className="text-left text-purple-700 font-semibold">$/User/Mo</div>
                  <div className="text-purple-600">${monthlyProjections[0].perUserUsd?.toFixed(2)}</div>
                  <div className="text-purple-600">${monthlyProjections[11].perUserUsd?.toFixed(2)}</div>
                  <div className={monthlyProjections[11].perUserUsd >= monthlyProjections[0].perUserUsd ? 'text-emerald-600' : 'text-red-600'}>
                    {monthlyProjections[0].perUserUsd 
                      ? `${(((monthlyProjections[11].perUserUsd || 0) / monthlyProjections[0].perUserUsd - 1) * 100).toFixed(0)}%`
                      : 'N/A'}
                  </div>
                </>
              )}
            </div>
            
            {/* Total Allocation Profit Boost */}
            {enableDynamicAllocation && monthlyProjections[11].cumulativeAllocationProfit > 0 && (
              <div className="mt-4 bg-purple-50 border border-purple-200 rounded-lg p-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="text-xl">💰</span>
                    <span className="font-semibold text-purple-800">
                      Total Extra Profit from Dynamic Allocation (12 months):
                    </span>
                  </div>
                  <span className="text-2xl font-bold text-purple-700">
                    +{formatCurrency(monthlyProjections[11].cumulativeAllocationProfit)}
                  </span>
                </div>
                <div className="text-xs text-purple-600 mt-1">
                  This is the additional platform fee revenue generated by scaling allocation from{' '}
                  {monthlyProjections[0].allocation?.toFixed(1)}% to {monthlyProjections[11].allocation?.toFixed(1)}%{' '}
                  as users grew from {formatNumber(monthlyProjections[0].users)} to {formatNumber(monthlyProjections[11].users)}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Mission Summary */}
      <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <span className="text-emerald-500 text-xl">✓</span>
          <div>
            <strong className="text-emerald-800">Mission Accomplished:</strong>
            <span className="text-emerald-700 ml-1">
              {modules.filter(m => m.enabled).length} revenue modules generate{' '}
              {formatCurrency(result.totals.revenue)} monthly revenue with{' '}
              {formatCurrency(result.totals.profit)} net profit ({result.totals.margin.toFixed(1)}% margin) 
              starting from Day 1 with {formatNumber(result.customerAcquisition.totalUsers)} users
              {useGrowthScenarios && ` (${scenarioConfig.name} scenario)`}.
            </span>
          </div>
        </div>
      </div>

      {/* Module Performance Table */}
      <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
        <div className="p-4 border-b border-gray-200 bg-gray-50">
          <h3 className="font-bold text-lg">📊 Module Performance Overview</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-gray-100">
                <th className="px-4 py-3 text-left font-semibold text-gray-600 uppercase text-xs">Module</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 uppercase text-xs">Revenue</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 uppercase text-xs">Costs</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 uppercase text-xs">Profit</th>
                <th className="px-4 py-3 text-right font-semibold text-gray-600 uppercase text-xs">Margin</th>
              </tr>
            </thead>
            <tbody>
              {modules.map((module) => (
                <tr 
                  key={module.name} 
                  className={`border-b border-gray-100 ${!module.enabled ? 'opacity-50' : ''}`}
                >
                  <td className="px-4 py-3 font-medium">
                    <span className={`inline-block w-2 h-2 rounded-full bg-${module.color}-500 mr-2`}></span>
                    {module.name}
                    {!module.enabled && <span className="text-gray-400 ml-2 text-xs">(Disabled)</span>}
                  </td>
                  <td className="px-4 py-3 text-right font-semibold">
                    {formatCurrency(module.data.revenue)}
                  </td>
                  <td className="px-4 py-3 text-right text-gray-600">
                    {formatCurrency(module.data.costs)}
                  </td>
                  <td className={`px-4 py-3 text-right font-semibold ${
                    module.data.profit >= 0 ? 'text-emerald-600' : 'text-red-600'
                  }`}>
                    {formatCurrency(module.data.profit)}
                  </td>
                  <td className="px-4 py-3 text-right">
                    {module.data.margin.toFixed(1)}%
                  </td>
                </tr>
              ))}
              <tr className="border-b border-gray-100 bg-amber-50">
                <td className="px-4 py-3 font-medium">
                  <span className="inline-block w-2 h-2 rounded-full bg-amber-500 mr-2"></span>
                  Rewards (Cost Center)
                </td>
                <td className="px-4 py-3 text-right font-semibold">$0</td>
                <td className="px-4 py-3 text-right text-gray-600">
                  {formatCurrency(result.rewards.opCosts)}
                </td>
                <td className="px-4 py-3 text-right font-semibold text-red-600">
                  -{formatCurrency(result.rewards.opCosts)}
                </td>
                <td className="px-4 py-3 text-right">-</td>
              </tr>
              <tr className="border-b border-gray-100 bg-emerald-50">
                <td className="px-4 py-3 font-medium">
                  <span className="inline-block w-2 h-2 rounded-full bg-emerald-500 mr-2"></span>
                  Platform Fees (5% of Rewards)
                </td>
                <td className="px-4 py-3 text-right font-semibold text-emerald-600">
                  {formatCurrency(result.platformFees.rewardFeeUsd)}
                </td>
                <td className="px-4 py-3 text-right text-gray-600">$0</td>
                <td className="px-4 py-3 text-right font-semibold text-emerald-600">
                  {formatCurrency(result.platformFees.rewardFeeUsd)}
                </td>
                <td className="px-4 py-3 text-right">100%</td>
              </tr>
              <tr className="bg-gray-900 text-white font-bold">
                <td className="px-4 py-3">TOTAL</td>
                <td className="px-4 py-3 text-right">{formatCurrency(result.totals.revenue)}</td>
                <td className="px-4 py-3 text-right">{formatCurrency(result.totals.costs)}</td>
                <td className={`px-4 py-3 text-right ${
                  result.totals.profit >= 0 ? 'text-emerald-400' : 'text-red-400'
                }`}>
                  {formatCurrency(result.totals.profit)}
                </td>
                <td className="px-4 py-3 text-right">{result.totals.margin.toFixed(1)}%</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Recapture Flow */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🔄 Monthly Reward Recapture Flow</h3>
        
        <div className="mb-4">
          <div className="text-sm text-gray-600 mb-2">
            Gross Emission: {formatNumber(result.rewards.grossMonthlyEmission)} VCoin | 
            Net to Users (after 5% platform fee): {formatNumber(result.rewards.monthlyEmission)} VCoin
          </div>
          
          {/* Recapture Bar */}
          <div className="h-10 bg-gray-100 rounded-lg overflow-hidden flex">
            <div 
              className="bg-emerald-500 flex items-center justify-center text-white text-xs font-bold"
              style={{ width: `${(result.rewards.platformFeeVcoin / result.rewards.grossMonthlyEmission) * 100}%` }}
            >
              5%
            </div>
            <div 
              className="bg-red-500 flex items-center justify-center text-white text-xs font-bold"
              style={{ width: `${(result.recapture.burns / result.rewards.grossMonthlyEmission) * 100}%` }}
            >
              {((result.recapture.burns / result.rewards.grossMonthlyEmission) * 100).toFixed(1)}%
            </div>
            <div 
              className="bg-purple-500 flex items-center justify-center text-white text-xs font-bold"
              style={{ width: `${(result.recapture.buybacks / result.rewards.grossMonthlyEmission) * 100}%` }}
            >
              {((result.recapture.buybacks / result.rewards.grossMonthlyEmission) * 100).toFixed(1)}%
            </div>
            <div 
              className="bg-blue-500 flex items-center justify-center text-white text-xs font-bold"
              style={{ width: `${(result.recapture.staking / result.rewards.grossMonthlyEmission) * 100}%` }}
            >
              {((result.recapture.staking / result.rewards.grossMonthlyEmission) * 100).toFixed(1)}%
            </div>
            <div 
              className="bg-amber-500 flex items-center justify-center text-white text-xs font-bold"
              style={{ width: `${(result.recapture.treasury / result.rewards.grossMonthlyEmission) * 100}%` }}
            >
              {((result.recapture.treasury / result.rewards.grossMonthlyEmission) * 100).toFixed(1)}%
            </div>
            <div 
              className="bg-gray-400 flex items-center justify-center text-white text-xs font-bold flex-1"
            >
              Net
            </div>
          </div>
          
          {/* Legend */}
          <div className="flex flex-wrap gap-4 mt-3 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-emerald-500"></div>
              <span>Platform Fee: {formatNumber(result.rewards.platformFeeVcoin)} VCoin</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-red-500"></div>
              <span>Burns: {formatNumber(result.recapture.burns)} VCoin</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-purple-500"></div>
              <span>Buybacks: {formatNumber(result.recapture.buybacks)} VCoin</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-blue-500"></div>
              <span>Staking: {formatNumber(result.recapture.staking)} VCoin</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded bg-amber-500"></div>
              <span>Treasury: {formatNumber(result.recapture.treasury)} VCoin</span>
            </div>
          </div>
        </div>

        {/* Recapture Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatNumber(result.recapture.totalRecaptured)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">VCoin Recaptured</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className={`text-2xl font-bold ${recaptureStatus.color}`}>
              {result.recapture.recaptureRate.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Recapture Rate</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(result.recapture.totalRecaptured * parameters.tokenPrice)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Recapture Value</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatNumber(result.rewards.monthlyEmission - result.recapture.totalRecaptured)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Net Circulation</div>
          </div>
        </div>
      </div>

      {/* Customer Acquisition Summary */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">👥 Customer Acquisition Breakdown</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(result.customerAcquisition.totalCreatorCost)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Creator Cost</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(result.customerAcquisition.consumerAcquisitionBudget)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Consumer Budget</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {formatNumber(result.customerAcquisition.northAmericaUsers)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">NA Users</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-emerald-600">
              {formatNumber(result.customerAcquisition.globalLowIncomeUsers)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Global Users</div>
          </div>
        </div>
        
        {/* Growth Scenario Effect */}
        {useGrowthScenarios && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between flex-wrap gap-4">
              <div>
                <span className="text-sm text-gray-600">Base Users (from Marketing):</span>
                <span className="ml-2 font-semibold">
                  {formatNumber(result.customerAcquisition.northAmericaUsers + result.customerAcquisition.globalLowIncomeUsers + 
                    (parameters.highQualityCreatorsNeeded || 0) + (parameters.midLevelCreatorsNeeded || 0))}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600">Scenario Multiplier:</span>
                <span className={`px-2 py-1 rounded text-sm font-bold ${
                  scenario === 'bullish' ? 'bg-emerald-100 text-emerald-700' :
                  scenario === 'conservative' ? 'bg-blue-100 text-blue-700' :
                  'bg-purple-100 text-purple-700'
                }`}>
                  {(scenarioConfig.month1FomoMultiplier * marketConfig.fomoMultiplier * 0.3).toFixed(2)}x
                </span>
              </div>
              <div>
                <span className="text-sm text-gray-600">Total Active Users:</span>
                <span className={`ml-2 font-bold text-lg ${
                  scenario === 'bullish' ? 'text-emerald-600' :
                  scenario === 'conservative' ? 'text-blue-600' :
                  'text-purple-600'
                }`}>
                  {formatNumber(result.customerAcquisition.totalUsers)}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>
    </section>
  );
}


