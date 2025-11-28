'use client';

import { useState, useMemo } from 'react';
import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency, getMarginStatus, getRecaptureStatus } from '@/lib/utils';
import { GROWTH_SCENARIOS, MARKET_CONDITIONS, FUTURE_MODULE_DEFAULTS, MARKET_CYCLE_2025_2030 } from '@/lib/constants';

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
  const contentVcoinRevenue = (Number(baseResult.content?.breakdown?.postFeesVcoin) || 0) * baseTokenPrice;
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
    
    // Additional profit from dynamic allocation (only applies from Month 2+)
    const allocationProfitBoost = platformFeeUsd - staticPlatformFeeUsd;
    if (month > 1) {
      cumulativeAllocationProfit += allocationProfitBoost;
    }
    
    // FIX: Month 1 should use the exact base result values for consistency with Module Performance Overview
    // This ensures the "12-Month Projection Month 1" matches "Module Performance TOTAL"
    let monthRevenue: number;
    let monthCosts: number;
    let monthProfit: number;
    let scaledTokenRevenueForBreakdown: number;
    let scaledUsdRevenueForBreakdown: number;
    
    const userScaleFactor = currentUsers / baseUsers;
    
    if (month === 1) {
      // Month 1: Use base simulation results directly for consistency
      monthRevenue = baseRevenue;
      monthCosts = baseCosts;
      monthProfit = baseResult.totals.profit;
      scaledTokenRevenueForBreakdown = tokenBasedRevenue;
      scaledUsdRevenueForBreakdown = usdFixedRevenue;
    } else {
      // Month 2+: Scale revenue based on user count AND token price
      // Token-based revenue scales with BOTH users AND token price
      scaledTokenRevenueForBreakdown = tokenBasedRevenue * userScaleFactor * priceMultiplier;
      // USD-fixed revenue scales with users only
      scaledUsdRevenueForBreakdown = usdFixedRevenue * userScaleFactor;
      
      // Add platform fee to revenue (this now scales with allocation!)
      const basePlatformFee = baseResult.platformFees?.rewardFeeUsd || 0;
      const scaledPlatformFee = enableDynamicAllocation ? platformFeeUsd : basePlatformFee * userScaleFactor;
      
      monthRevenue = scaledTokenRevenueForBreakdown + scaledUsdRevenueForBreakdown + (scaledPlatformFee - basePlatformFee * userScaleFactor);
      
      // Costs scale sub-linearly with users (economies of scale)
      monthCosts = baseCosts * Math.sqrt(userScaleFactor);
      monthProfit = monthRevenue - monthCosts;
    }
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
      allocationProfitBoost: month === 1 ? 0 : allocationProfitBoost, // Month 1 uses base result, no boost
      cumulativeAllocationProfit: month === 1 ? 0 : cumulativeAllocationProfit,
      // Breakdown for debugging
      tokenBasedRevenue: scaledTokenRevenueForBreakdown,
      usdFixedRevenue: scaledUsdRevenueForBreakdown,
    });
  }
  
  return projections;
}

// Future module revenue calculation
interface FutureModuleRevenue {
  name: string;
  icon: string;
  launchMonth: number;
  enabled: boolean;
  monthlyRevenue: number;
  monthlyProfit: number;
  margin: number;
}

function calculateFutureModuleRevenue(
  month: number,
  users: number,
  tokenPrice: number,
  parameters: SimulationParameters
): FutureModuleRevenue[] {
  const modules: FutureModuleRevenue[] = [];
  
  // VChain Network (Month 24)
  const vchainLaunchMonth = FUTURE_MODULE_DEFAULTS?.vchain?.vchainLaunchMonth || 24;
  const vchainEnabled = parameters.enableVchain || false;
  if (vchainEnabled && month >= vchainLaunchMonth) {
    const monthsActive = month - vchainLaunchMonth + 1;
    const rampUp = Math.min(1, monthsActive / 12); // 12 month ramp
    const baseVolume = 25_000_000 * rampUp;
    const txFeeRevenue = baseVolume * 0.002;
    const bridgeFeeRevenue = baseVolume * 0.3 * 0.001;
    const gasRevenue = baseVolume * 0.1 * 0.08;
    const revenue = txFeeRevenue + bridgeFeeRevenue + gasRevenue;
    const costs = revenue * 0.35;
    modules.push({
      name: 'VChain Network',
      icon: '🔗',
      launchMonth: vchainLaunchMonth,
      enabled: true,
      monthlyRevenue: revenue,
      monthlyProfit: revenue - costs,
      margin: ((revenue - costs) / revenue) * 100
    });
  }
  
  // Marketplace (Month 18)
  const marketplaceLaunchMonth = FUTURE_MODULE_DEFAULTS?.marketplace?.marketplaceLaunchMonth || 18;
  const marketplaceEnabled = parameters.enableMarketplace || false;
  if (marketplaceEnabled && month >= marketplaceLaunchMonth) {
    const monthsActive = month - marketplaceLaunchMonth + 1;
    const rampUp = Math.min(1, monthsActive / 12);
    const gmv = users * 5 * rampUp; // $5 GMV per user
    const physicalRevenue = gmv * 0.4 * 0.08; // 40% physical, 8% commission
    const digitalRevenue = gmv * 0.6 * 0.15; // 60% digital, 15% commission
    const revenue = physicalRevenue + digitalRevenue;
    const costs = revenue * 0.25;
    modules.push({
      name: 'Marketplace',
      icon: '🛒',
      launchMonth: marketplaceLaunchMonth,
      enabled: true,
      monthlyRevenue: revenue,
      monthlyProfit: revenue - costs,
      margin: ((revenue - costs) / revenue) * 100
    });
  }
  
  // Business Hub (Month 21)
  const businessHubLaunchMonth = FUTURE_MODULE_DEFAULTS?.businessHub?.businessHubLaunchMonth || 21;
  const businessHubEnabled = parameters.enableBusinessHub || false;
  if (businessHubEnabled && month >= businessHubLaunchMonth) {
    const monthsActive = month - businessHubLaunchMonth + 1;
    const rampUp = Math.min(1, monthsActive / 12);
    const freelancers = users * 0.02 * rampUp; // 2% are freelancers
    const freelanceVolume = freelancers * 500; // $500 avg monthly volume
    const freelanceRevenue = freelanceVolume * 0.12;
    const pmUsers = users * 0.05 * rampUp;
    const pmRevenue = pmUsers * 15; // $15/month average
    const revenue = freelanceRevenue + pmRevenue;
    const costs = revenue * 0.30;
    modules.push({
      name: 'Business Hub',
      icon: '💼',
      launchMonth: businessHubLaunchMonth,
      enabled: true,
      monthlyRevenue: revenue,
      monthlyProfit: revenue - costs,
      margin: ((revenue - costs) / revenue) * 100
    });
  }
  
  // Cross-Platform (Month 15)
  const crossPlatformLaunchMonth = FUTURE_MODULE_DEFAULTS?.crossPlatform?.crossPlatformLaunchMonth || 15;
  const crossPlatformEnabled = parameters.enableCrossPlatform || false;
  if (crossPlatformEnabled && month >= crossPlatformLaunchMonth) {
    const monthsActive = month - crossPlatformLaunchMonth + 1;
    const rampUp = Math.min(1, monthsActive / 12);
    const subscribers = users * 0.03 * rampUp; // 3% subscribe
    const subscriptionRevenue = subscribers * 10; // $10/month
    const renters = users * 0.01 * rampUp;
    const rentalRevenue = renters * 50 * 0.15; // $50 avg rental, 15% commission
    const revenue = subscriptionRevenue + rentalRevenue;
    const costs = revenue * 0.20;
    modules.push({
      name: 'Cross-Platform',
      icon: '🌐',
      launchMonth: crossPlatformLaunchMonth,
      enabled: true,
      monthlyRevenue: revenue,
      monthlyProfit: revenue - costs,
      margin: ((revenue - costs) / revenue) * 100
    });
  }
  
  return modules;
}

// Calculate 5-year (60-month) projections
interface YearlyProjection {
  year: number;
  startMonth: number;
  endMonth: number;
  startUsers: number;
  endUsers: number;
  avgUsers: number;
  totalRevenue: number;
  totalProfit: number;
  avgMargin: number;
  tokenPriceStart: number;
  tokenPriceEnd: number;
  coreModulesRevenue: number;
  futureModulesRevenue: number;
  activeModules: string[];
  marketCycle: string;
  cycleMultiplier: number;
}

function calculate5YearProjections(
  baseResult: SimulationResult,
  scenarioConfig: typeof GROWTH_SCENARIOS['base'],
  marketConfig: typeof MARKET_CONDITIONS['bull'],
  baseTokenPrice: number,
  parameters: SimulationParameters
): YearlyProjection[] {
  const projections: YearlyProjection[] = [];
  const baseUsers = baseResult.customerAcquisition.totalUsers;
  const baseRevenue = baseResult.totals.revenue;
  
  let currentUsers = baseUsers;
  let currentTokenPrice = baseTokenPrice;
  
  for (let year = 1; year <= 5; year++) {
    const startMonth = (year - 1) * 12 + 1;
    const endMonth = year * 12;
    const startUsers = currentUsers;
    const startPrice = currentTokenPrice;
    
    // Get market cycle for this year
    const calendarYear = 2025 + year - 1;
    const cycleData = MARKET_CYCLE_2025_2030?.[calendarYear] || { year: calendarYear, phase: 'neutral', growthMultiplier: 1, retentionMultiplier: 1, priceMultiplier: 1, description: '' };
    const cycleMultiplier = cycleData.growthMultiplier || 1;
    
    let yearRevenue = 0;
    let yearProfit = 0;
    let yearCoreRevenue = 0;
    let yearFutureRevenue = 0;
    const activeModulesSet = new Set<string>();
    
    // Process each month of the year
    for (let month = startMonth; month <= endMonth; month++) {
      // Growth rate varies by year
      let monthlyGrowthRate: number;
      if (year === 1) {
        // Year 1: Use scenario growth rates
        const monthIndex = month - 1;
        monthlyGrowthRate = (scenarioConfig.monthlyGrowthRates[monthIndex] || 0.05) * cycleMultiplier;
      } else {
        // Years 2-5: Slower but steady growth
        const yearGrowthRates = [0, 0.08, 0.06, 0.04, 0.03]; // Y1 handled above
        monthlyGrowthRate = (yearGrowthRates[year - 1] / 12) * cycleMultiplier;
      }
      
      if (month > 1) {
        currentUsers = Math.round(currentUsers * (1 + monthlyGrowthRate));
      }
      
      // Token price progression
      let priceMultiplier: number;
      if (year === 1) {
        // Year 1: Use scenario multipliers
        if (month <= 6) {
          const t = month / 6;
          priceMultiplier = 1 + (scenarioConfig.tokenPriceMonth6Multiplier - 1) * t;
        } else {
          const t = (month - 6) / 6;
          priceMultiplier = scenarioConfig.tokenPriceMonth6Multiplier + 
            (scenarioConfig.tokenPriceEndMultiplier - scenarioConfig.tokenPriceMonth6Multiplier) * t;
        }
      } else {
        // Years 2-5: More gradual price evolution with cycle
        const yearPriceGrowth = [0, 0.5, 0.3, 0.2, 0.15]; // Cumulative growth per year
        const baseY1End = scenarioConfig.tokenPriceEndMultiplier * marketConfig.priceMultiplier;
        const yearProgress = (month - startMonth) / 12;
        priceMultiplier = baseY1End * (1 + yearPriceGrowth.slice(1, year).reduce((a, b) => a + b, 0) + yearPriceGrowth[year - 1] * yearProgress);
        priceMultiplier *= (cycleData.priceMultiplier || 1);
      }
      
      currentTokenPrice = baseTokenPrice * priceMultiplier * marketConfig.priceMultiplier;
      
      // Calculate core module revenue (scales with users)
      const userScale = currentUsers / baseUsers;
      const coreRevenue = baseRevenue * Math.sqrt(userScale) * (1 + (year - 1) * 0.1);
      const coreCosts = baseResult.totals.costs * Math.pow(userScale, 0.4);
      const coreProfit = coreRevenue - coreCosts;
      
      yearCoreRevenue += coreRevenue;
      
      // Calculate future module revenue
      const futureModules = calculateFutureModuleRevenue(month, currentUsers, currentTokenPrice, parameters);
      let futureRevenue = 0;
      let futureProfit = 0;
      
      for (const fm of futureModules) {
        futureRevenue += fm.monthlyRevenue;
        futureProfit += fm.monthlyProfit;
        activeModulesSet.add(`${fm.icon} ${fm.name}`);
      }
      
      yearFutureRevenue += futureRevenue;
      yearRevenue += coreRevenue + futureRevenue;
      yearProfit += coreProfit + futureProfit;
    }
    
    projections.push({
      year,
      startMonth,
      endMonth,
      startUsers,
      endUsers: currentUsers,
      avgUsers: (startUsers + currentUsers) / 2,
      totalRevenue: yearRevenue,
      totalProfit: yearProfit,
      avgMargin: yearRevenue > 0 ? (yearProfit / yearRevenue) * 100 : 0,
      tokenPriceStart: startPrice,
      tokenPriceEnd: currentTokenPrice,
      coreModulesRevenue: yearCoreRevenue,
      futureModulesRevenue: yearFutureRevenue,
      activeModules: Array.from(activeModulesSet),
      marketCycle: cycleData.phase || 'neutral',
      cycleMultiplier
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

  // Calculate 5-year projections
  const fiveYearProjections = useMemo(() => {
    if (!useGrowthScenarios) return null;
    return calculate5YearProjections(
      result,
      scenarioConfig,
      marketConfig,
      parameters.tokenPrice,
      parameters
    );
  }, [result, scenarioConfig, marketConfig, parameters]);

  // Check which future modules are enabled
  const enabledFutureModules = {
    vchain: parameters.enableVchain || false,
    marketplace: parameters.enableMarketplace || false,
    businessHub: parameters.enableBusinessHub || false,
    crossPlatform: parameters.enableCrossPlatform || false,
  };
  const hasFutureModules = Object.values(enabledFutureModules).some(Boolean);

  const modules = [
    { name: 'Identity', data: result.identity, color: 'violet', enabled: true },
    { name: 'Content', data: result.content, color: 'pink', enabled: true },
    { name: 'Advertising', data: result.advertising, color: 'blue', enabled: parameters.enableAdvertising },
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
              // Issue #32 Fix: Add fallback to 1 if Number() returns NaN
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

      {/* 5-Year Projection Section */}
      {useGrowthScenarios && fiveYearProjections && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="font-bold text-xl flex items-center gap-2">
                📈 5-Year Financial Projection (2025-2030)
              </h3>
              <p className="text-sm text-gray-500 mt-1">
                Long-term revenue forecast including core modules and future revenue streams
              </p>
            </div>
            {hasFutureModules && (
              <div className="text-right">
                <div className="text-sm text-purple-600 font-semibold">Future Modules Enabled</div>
                <div className="flex gap-2 mt-1">
                  {enabledFutureModules.crossPlatform && <span title="Cross-Platform (M15)">🌐</span>}
                  {enabledFutureModules.marketplace && <span title="Marketplace (M18)">🛒</span>}
                  {enabledFutureModules.businessHub && <span title="Business Hub (M21)">💼</span>}
                  {enabledFutureModules.vchain && <span title="VChain (M24)">🔗</span>}
                </div>
              </div>
            )}
          </div>

          {/* Summary Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-blue-700">
                {formatNumber(fiveYearProjections[4].endUsers)}
              </div>
              <div className="text-xs text-blue-600 uppercase font-semibold">Year 5 Users</div>
              <div className="text-xs text-gray-500 mt-1">
                {((fiveYearProjections[4].endUsers / fiveYearProjections[0].startUsers - 1) * 100).toFixed(0)}% growth
              </div>
            </div>
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-emerald-700">
                ${(fiveYearProjections.reduce((sum, y) => sum + y.totalRevenue, 0) / 1_000_000).toFixed(2)}M
              </div>
              <div className="text-xs text-emerald-600 uppercase font-semibold">5-Year Revenue</div>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-green-700">
                ${(fiveYearProjections.reduce((sum, y) => sum + y.totalProfit, 0) / 1_000_000).toFixed(2)}M
              </div>
              <div className="text-xs text-green-600 uppercase font-semibold">5-Year Profit</div>
            </div>
            <div className="bg-gradient-to-br from-amber-50 to-amber-100 rounded-xl p-4 text-center">
              <div className="text-3xl font-bold text-amber-700">
                ${fiveYearProjections[4].tokenPriceEnd.toFixed(2)}
              </div>
              <div className="text-xs text-amber-600 uppercase font-semibold">Year 5 Token Price</div>
              <div className="text-xs text-gray-500 mt-1">
                {(fiveYearProjections[4].tokenPriceEnd / parameters.tokenPrice).toFixed(1)}x from TGE
              </div>
            </div>
          </div>

          {/* Yearly Breakdown Table */}
          <div className="overflow-x-auto mb-6">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-gray-100">
                  <th className="px-3 py-2 text-left font-semibold text-gray-600">Year</th>
                  <th className="px-3 py-2 text-right font-semibold text-gray-600">Users</th>
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
                          <span className="text-xs text-gray-400">({2024 + year.year})</span>
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
                        ${(year.coreModulesRevenue / 1000).toFixed(0)}K
                      </td>
                      <td className="px-3 py-3 text-right">
                        {year.futureModulesRevenue > 0 ? (
                          <span className="text-purple-600 font-semibold">
                            +${(year.futureModulesRevenue / 1000).toFixed(0)}K
                          </span>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </td>
                      <td className="px-3 py-3 text-right font-semibold text-emerald-600">
                        ${(year.totalRevenue / 1000).toFixed(0)}K
                      </td>
                      <td className={`px-3 py-3 text-right font-semibold ${
                        year.totalProfit >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        ${(year.totalProfit / 1000).toFixed(0)}K
                      </td>
                      <td className="px-3 py-3 text-right">
                        {year.avgMargin.toFixed(1)}%
                      </td>
                      <td className="px-3 py-3 text-right text-amber-600">
                        ${year.tokenPriceEnd.toFixed(2)}
                      </td>
                      <td className="px-3 py-3 text-center">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          marketCycleColors[year.marketCycle] || marketCycleColors['neutral']
                        }`}>
                          {year.marketCycle}
                        </span>
                      </td>
                    </tr>
                  );
                })}
                {/* Total Row */}
                <tr className="bg-gray-900 text-white font-bold">
                  <td className="px-3 py-3">5-Year Total</td>
                  <td className="px-3 py-3 text-right">
                    {formatNumber(fiveYearProjections[4].endUsers)}
                  </td>
                  <td className="px-3 py-3 text-right">
                    ${(fiveYearProjections.reduce((s, y) => s + y.coreModulesRevenue, 0) / 1000).toFixed(0)}K
                  </td>
                  <td className="px-3 py-3 text-right text-purple-300">
                    +${(fiveYearProjections.reduce((s, y) => s + y.futureModulesRevenue, 0) / 1000).toFixed(0)}K
                  </td>
                  <td className="px-3 py-3 text-right text-emerald-300">
                    ${(fiveYearProjections.reduce((s, y) => s + y.totalRevenue, 0) / 1_000_000).toFixed(2)}M
                  </td>
                  <td className="px-3 py-3 text-right text-green-300">
                    ${(fiveYearProjections.reduce((s, y) => s + y.totalProfit, 0) / 1_000_000).toFixed(2)}M
                  </td>
                  <td className="px-3 py-3 text-right">
                    {(fiveYearProjections.reduce((s, y) => s + y.totalProfit, 0) / 
                      fiveYearProjections.reduce((s, y) => s + y.totalRevenue, 0) * 100).toFixed(1)}%
                  </td>
                  <td className="px-3 py-3 text-right text-amber-300">
                    {(fiveYearProjections[4].tokenPriceEnd / parameters.tokenPrice).toFixed(1)}x
                  </td>
                  <td className="px-3 py-3"></td>
                </tr>
              </tbody>
            </table>
          </div>

          {/* Future Modules Launch Timeline */}
          {hasFutureModules && (
            <div className="bg-purple-50 rounded-xl p-5 mb-6">
              <h4 className="font-semibold text-purple-800 mb-4 flex items-center gap-2">
                🔮 Future Module Revenue Impact
              </h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {enabledFutureModules.crossPlatform && (
                  <div className="bg-white rounded-lg p-3 border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">🌐</span>
                      <span className="font-semibold text-sm">Cross-Platform</span>
                    </div>
                    <div className="text-xs text-gray-500">Launches Month 15</div>
                    <div className="text-lg font-bold text-purple-600 mt-1">
                      ${((fiveYearProjections[1]?.futureModulesRevenue || 0) * 0.3 / 1000).toFixed(0)}K/yr
                    </div>
                    <div className="text-xs text-gray-400">Content sharing & renting</div>
                  </div>
                )}
                {enabledFutureModules.marketplace && (
                  <div className="bg-white rounded-lg p-3 border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">🛒</span>
                      <span className="font-semibold text-sm">Marketplace</span>
                    </div>
                    <div className="text-xs text-gray-500">Launches Month 18</div>
                    <div className="text-lg font-bold text-purple-600 mt-1">
                      ${((fiveYearProjections[2]?.futureModulesRevenue || 0) * 0.35 / 1000).toFixed(0)}K/yr
                    </div>
                    <div className="text-xs text-gray-400">Physical & digital goods</div>
                  </div>
                )}
                {enabledFutureModules.businessHub && (
                  <div className="bg-white rounded-lg p-3 border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">💼</span>
                      <span className="font-semibold text-sm">Business Hub</span>
                    </div>
                    <div className="text-xs text-gray-500">Launches Month 21</div>
                    <div className="text-lg font-bold text-purple-600 mt-1">
                      ${((fiveYearProjections[2]?.futureModulesRevenue || 0) * 0.25 / 1000).toFixed(0)}K/yr
                    </div>
                    <div className="text-xs text-gray-400">Freelancer ecosystem</div>
                  </div>
                )}
                {enabledFutureModules.vchain && (
                  <div className="bg-white rounded-lg p-3 border border-purple-200">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xl">🔗</span>
                      <span className="font-semibold text-sm">VChain Network</span>
                    </div>
                    <div className="text-xs text-gray-500">Launches Month 24</div>
                    <div className="text-lg font-bold text-purple-600 mt-1">
                      ${((fiveYearProjections[2]?.futureModulesRevenue || 0) * 0.4 / 1000).toFixed(0)}K/yr
                    </div>
                    <div className="text-xs text-gray-400">Cross-chain infrastructure</div>
                  </div>
                )}
              </div>
              <div className="mt-4 text-sm text-purple-700">
                <strong>Total Future Module Contribution (5 years):</strong>{' '}
                <span className="text-lg font-bold">
                  ${(fiveYearProjections.reduce((s, y) => s + y.futureModulesRevenue, 0) / 1000).toFixed(0)}K
                </span>
                {' '}({(fiveYearProjections.reduce((s, y) => s + y.futureModulesRevenue, 0) / 
                  fiveYearProjections.reduce((s, y) => s + y.totalRevenue, 0) * 100).toFixed(1)}% of total revenue)
              </div>
            </div>
          )}

          {/* Key Milestones */}
          <div className="bg-gray-50 rounded-xl p-5">
            <h4 className="font-semibold text-gray-800 mb-4 flex items-center gap-2">
              🎯 Key Milestones
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="flex items-center gap-3 bg-white rounded-lg p-3 border border-gray-200">
                <span className="text-2xl">🚀</span>
                <div>
                  <div className="font-semibold text-sm">TGE Launch</div>
                  <div className="text-xs text-gray-500">Month 1 • {formatNumber(fiveYearProjections[0].startUsers)} users</div>
                </div>
              </div>
              <div className="flex items-center gap-3 bg-white rounded-lg p-3 border border-gray-200">
                <span className="text-2xl">📊</span>
                <div>
                  <div className="font-semibold text-sm">Break-even</div>
                  <div className="text-xs text-gray-500">
                    {fiveYearProjections[0].totalProfit > 0 ? 'Profitable from Day 1!' : 'Month 3 projected'}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 bg-white rounded-lg p-3 border border-gray-200">
                <span className="text-2xl">🎉</span>
                <div>
                  <div className="font-semibold text-sm">100K Users</div>
                  <div className="text-xs text-gray-500">
                    {fiveYearProjections.findIndex(y => y.endUsers >= 100000) >= 0 
                      ? `Year ${fiveYearProjections.findIndex(y => y.endUsers >= 100000) + 1}` 
                      : 'Beyond 5 years'}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-3 bg-white rounded-lg p-3 border border-gray-200">
                <span className="text-2xl">💰</span>
                <div>
                  <div className="font-semibold text-sm">$1M Annual Revenue</div>
                  <div className="text-xs text-gray-500">
                    {fiveYearProjections.findIndex(y => y.totalRevenue >= 1_000_000) >= 0 
                      ? `Year ${fiveYearProjections.findIndex(y => y.totalRevenue >= 1_000_000) + 1}` 
                      : 'Beyond 5 years'}
                  </div>
                </div>
              </div>
            </div>
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


