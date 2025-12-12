'use client';

import { useMemo } from 'react';
import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { GROWTH_SCENARIOS, MARKET_CONDITIONS, FUTURE_MODULE_DEFAULTS, MARKET_CYCLE_2026_2030 } from '@/lib/constants';

interface Year5OverviewProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export interface YearlyProjection {
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
  // Marketing budget (Dec 2025)
  marketingBudget: number;
  marketingMultiplier: number;
  // User growth price impact (Dec 2025)
  userGrowthPriceMultiplier: number;
  userGrowthRatio: number;
}

/**
 * Calculate marketing budget for a specific year based on multipliers.
 * 
 * Year 1: Base marketing_budget
 * Year 2: Year 1 * year2Multiplier (default 2x)
 * Year 3: Year 2 * year3Multiplier (default 2x = 4x of Y1)
 * Year 4: Year 3 * year4Multiplier (default 2x = 8x of Y1)
 * Year 5: Year 4 * year5Multiplier (default 2x = 16x of Y1)
 */
function getMarketingBudgetForYear(year: number, parameters: SimulationParameters): { budget: number; multiplier: number } {
  const baseBudget = parameters.marketingBudget || 150000;
  // Default to 2x (doubling each year) for realistic growth
  const year2Mult = parameters.marketingBudgetYear2Multiplier ?? 2.0;
  const year3Mult = parameters.marketingBudgetYear3Multiplier ?? 2.0;
  const year4Mult = parameters.marketingBudgetYear4Multiplier ?? 2.0;
  const year5Mult = parameters.marketingBudgetYear5Multiplier ?? 2.0;
  
  if (year <= 1) return { budget: baseBudget, multiplier: 1.0 };
  
  const year2Budget = baseBudget * year2Mult;
  if (year === 2) return { budget: year2Budget, multiplier: year2Mult };
  
  const year3Budget = year2Budget * year3Mult;
  if (year === 3) return { budget: year3Budget, multiplier: year2Mult * year3Mult };
  
  const year4Budget = year3Budget * year4Mult;
  if (year === 4) return { budget: year4Budget, multiplier: year2Mult * year3Mult * year4Mult };
  
  const year5Budget = year4Budget * year5Mult;
  return { budget: year5Budget, multiplier: year2Mult * year3Mult * year4Mult * year5Mult };
}

/**
 * Calculate token price multiplier based on user growth with logarithmic dampening.
 * 
 * Based on research:
 * - Blockchain gaming: ~2.4x elasticity (12% DAU growth = 29% value increase)
 * - Friend.tech: Strong correlation but needs dampening
 * - Metcalfe's Law: Overstated for crypto; use dampened version
 * 
 * @param currentUsers - Current active user count
 * @param baselineUsers - Baseline users (Year 1) for comparison
 * @param elasticity - How much growth translates to price (0.35 = 35%)
 * @param maxMultiplier - Maximum price multiplier cap
 */
function calculateUserGrowthPriceMultiplier(
  currentUsers: number,
  baselineUsers: number,
  elasticity: number = 0.35,
  maxMultiplier: number = 3.0
): { multiplier: number; userGrowthRatio: number; dampeningFactor: number } {
  if (baselineUsers <= 0 || currentUsers <= 0) {
    return { multiplier: 1.0, userGrowthRatio: 1.0, dampeningFactor: 1.0 };
  }
  
  const userGrowthRatio = currentUsers / baselineUsers;
  
  // No positive impact if users haven't grown
  if (userGrowthRatio <= 1.0) {
    return { multiplier: 1.0, userGrowthRatio, dampeningFactor: 1.0 };
  }
  
  // Logarithmic dampening based on user scale
  // At 1K users: dampening = 1.0, At 100K: 0.50, At 1M: 0.25
  const logUsers = Math.log10(Math.max(currentUsers, 1000));
  let dampeningFactor = 1.0 / (1.0 + 0.25 * (logUsers - 3)); // log10(1000) = 3
  dampeningFactor = Math.max(0.1, Math.min(1.0, dampeningFactor));
  
  // Calculate impact: (growth_ratio - 1) * elasticity * dampening
  const rawGrowthFactor = userGrowthRatio - 1.0;
  const dampenedImpact = rawGrowthFactor * elasticity * dampeningFactor;
  
  // Final multiplier, capped
  const multiplier = Math.min(1.0 + dampenedImpact, maxMultiplier);
  
  return { multiplier, userGrowthRatio, dampeningFactor };
}

// ARPU bounds based on industry benchmarks for social/crypto apps
const MIN_ARPU = 0.10;  // $0.10/user/month floor (freemium baseline)
const MAX_ARPU = 5.00;  // $5.00/user/month ceiling (mature platform)

// Maximum token price revenue boost to prevent unrealistic compounding
const MAX_TOKEN_REVENUE_BOOST = 5.0;

// Calculate 5-year (60-month) projections
export function calculate5YearProjections(
  baseResult: SimulationResult,
  scenarioConfig: typeof GROWTH_SCENARIOS['base'],
  marketConfig: typeof MARKET_CONDITIONS['bull'],
  baseTokenPrice: number,
  parameters: SimulationParameters
): YearlyProjection[] {
  const projections: YearlyProjection[] = [];
  // Use total users with organic if available
  const baseUsers = Math.max(1, baseResult.customerAcquisition.totalUsersWithOrganic || baseResult.customerAcquisition.totalUsers);
  const baseRevenue = baseResult.totals.revenue;
  
  // Calculate ARPU from base results with bounds checking
  // This is the key fix: use per-user economics instead of scale-factor exponentiation
  const rawArpu = baseUsers > 0 ? baseRevenue / baseUsers : 0;
  const baseArpu = Math.max(MIN_ARPU, Math.min(MAX_ARPU, rawArpu));
  
  let currentUsers = baseUsers;
  let currentTokenPrice = baseTokenPrice;
  
  for (let year = 1; year <= 5; year++) {
    const startMonth = (year - 1) * 12 + 1;
    const endMonth = year * 12;
    const startUsers = currentUsers;
    const startPrice = currentTokenPrice;
    
    const calendarYear = 2026 + year - 1;
    const cycleData = MARKET_CYCLE_2026_2030?.[calendarYear] || { year: calendarYear, phase: 'neutral', growthMultiplier: 1, retentionMultiplier: 1, priceMultiplier: 1, description: '' };
    const cycleMultiplier = cycleData.growthMultiplier || 1;
    
    // Get marketing budget for this year (Dec 2025)
    const { budget: yearMarketingBudget, multiplier: marketingMultiplier } = getMarketingBudgetForYear(year, parameters);
    
    // Calculate effective CAC (blended from NA and Global)
    const naPercent = parameters.northAmericaBudgetPercent || 0.35;
    const globalPercent = parameters.globalLowIncomeBudgetPercent || 0.65;
    const naCac = parameters.cacNorthAmericaConsumer || 75;
    const globalCac = parameters.cacGlobalLowIncomeConsumer || 25;
    const effectiveCac = naPercent * naCac + globalPercent * globalCac;
    
    // Calculate marketing-driven user acquisition for years 2-5
    // Year 1 users come from baseResult, years 2-5 add from marketing budget
    // Apply diminishing returns: CAC increases and efficiency decreases in later years
    let marketingUsersThisYear = 0;
    if (year > 1 && yearMarketingBudget > 0 && effectiveCac > 0) {
      // Diminishing returns on marketing efficiency:
      // Year 2: 85% efficiency, Year 3: 70%, Year 4: 60%, Year 5: 50%
      // This accounts for market saturation and competition
      const cacEfficiency = 1 / Math.pow(year, 0.4);
      
      // Marketing budget drives additional user acquisition with diminishing efficiency
      marketingUsersThisYear = Math.floor(yearMarketingBudget / effectiveCac * cacEfficiency);
    }
    
    // Calculate user growth price impact at START of year (Dec 2025)
    // Based on research: user growth drives token value via network effects
    const enablePriceImpact = parameters.enableUserGrowthPriceImpact !== false;
    const elasticity = parameters.userGrowthPriceElasticity ?? 0.35;
    const maxPriceMultiplier = parameters.userGrowthPriceMaxMultiplier ?? 3.0;
    
    let userGrowthPriceMultiplier = 1.0;
    let userGrowthRatio = 1.0;
    
    if (enablePriceImpact && year > 1) {
      // Calculate based on start-of-year users vs Year 1 baseline
      const priceImpact = calculateUserGrowthPriceMultiplier(
        startUsers,
        baseUsers,
        elasticity,
        maxPriceMultiplier
      );
      userGrowthPriceMultiplier = priceImpact.multiplier;
      userGrowthRatio = priceImpact.userGrowthRatio;
      
      // Apply user growth boost to token price at start of year
      // This will compound with market cycle effects during the year
      currentTokenPrice *= userGrowthPriceMultiplier;
    }
    
    let yearRevenue = 0;
    let yearProfit = 0;
    let yearCoreRevenue = 0;
    let yearFutureRevenue = 0;
    const activeModulesSet = new Set<string>();
    
    for (let month = startMonth; month <= endMonth; month++) {
      let monthlyGrowthRate: number;
      if (year === 1) {
        const monthIndex = month - 1;
        monthlyGrowthRate = (scenarioConfig.monthlyGrowthRates[monthIndex] || 0.05) * cycleMultiplier;
      } else {
        // FIXED: Monthly compounding growth rates for years 2-5
        // For social/crypto platforms, organic growth INCREASES over time due to network effects
        
        // Check if organic growth is enabled
        const organicEnabled = parameters.organicGrowth?.enableOrganicGrowth || false;
        
        let baseMonthlyRate;
        if (organicEnabled) {
          // With organic growth enabled: REALISTIC social platform growth
          // These are MONTHLY rates that compound to massive yearly growth
          // Year 2: 6.5% monthly → 120% yearly (network effects kick in)
          // Year 3: 7.5% monthly → 145% yearly (strong network effects dominate)
          // Year 4: 6.0% monthly → 100% yearly (mature but sustained)
          // Year 5: 5.0% monthly → 80% yearly (established platform)
          const monthlyRates = [0, 0.065, 0.075, 0.060, 0.050];
          baseMonthlyRate = monthlyRates[year - 1];
        } else {
          // Without organic: Only marketing-driven growth (much slower)
          // Year 2: 3% monthly → 43% yearly
          // Year 3: 2.5% monthly → 34% yearly
          // Year 4: 2% monthly → 27% yearly
          // Year 5: 1.5% monthly → 20% yearly
          const monthlyRates = [0, 0.030, 0.025, 0.020, 0.015];
          baseMonthlyRate = monthlyRates[year - 1];
        }
        
        monthlyGrowthRate = baseMonthlyRate * cycleMultiplier;
      }
      
      if (month > 1) {
        // Apply monthly compounding growth
        // CRITICAL: This is where organic growth compounds exponentially!
        // Example: 6.5% monthly × 12 months = 120% yearly growth (users MORE than double!)
        currentUsers = Math.round(currentUsers * (1 + monthlyGrowthRate));
        
        // Add marketing-driven users (distributed across the year)
        // Using same front-loaded distribution as backend: 50% in first 3 months
        if (year > 1 && marketingUsersThisYear > 0) {
          const monthInYear = ((month - 1) % 12) + 1;
          const distribution: Record<number, number> = {
            1: 0.2333, 2: 0.1667, 3: 0.1000,
            4: 0.0667, 5: 0.0667, 6: 0.0667,
            7: 0.0556, 8: 0.0556, 9: 0.0556,
            10: 0.0444, 11: 0.0444, 12: 0.0444,
          };
          const monthlyMarketingUsers = Math.floor(marketingUsersThisYear * (distribution[monthInYear] || 0));
          currentUsers += monthlyMarketingUsers;
        }
      }
      
      let priceGrowthRate: number;
      if (year <= 2) {
        priceGrowthRate = ((cycleData.priceMultiplier || 1) - 1) / 12;
      } else {
        priceGrowthRate = (0.05 * (cycleData.priceMultiplier || 1)) / 12;
      }
      currentTokenPrice *= (1 + priceGrowthRate);
      
      // Token price affects revenue: ~50% of revenue is token-denominated
      // When token price rises, USD value of token-based revenue increases
      const tokenPriceRatio = currentTokenPrice / baseTokenPrice;
      const rawTokenRevenueBoost = 0.5 * (tokenPriceRatio - 1) + 1; // 50% of revenue scales with price
      // Cap token revenue boost to prevent unrealistic compounding
      const tokenRevenueBoost = Math.min(MAX_TOKEN_REVENUE_BOOST, rawTokenRevenueBoost);
      
      // Platform maturity multiplier: revenue per user improves over time
      // as features mature, monetization improves, and user engagement increases
      // Year 1: 1.0x, Year 2: 1.12x, Year 3: 1.24x, Year 4: 1.36x, Year 5: 1.48x (capped at 1.5x)
      const maturityMultiplier = 1 + Math.min(0.5, (year - 1) * 0.12);
      
      // FIXED: Use ARPU-based linear calculation instead of exponential scale-factor
      // Revenue = users × ARPU × maturity × token boost
      // This ensures revenue scales linearly with users, not exponentially
      const monthCoreRevenue = currentUsers * baseArpu * maturityMultiplier * tokenRevenueBoost;
      yearCoreRevenue += monthCoreRevenue;
      
      let monthFutureRevenue = 0;
      
      const vchainLaunchMonth = FUTURE_MODULE_DEFAULTS?.vchain?.vchainLaunchMonth || 24;
      if ((parameters.enableVchain || false) && month >= vchainLaunchMonth) {
        const monthsActive = month - vchainLaunchMonth + 1;
        const rampUp = Math.min(1, monthsActive / 12);
        const baseVolume = 25_000_000 * rampUp;
        const revenue = baseVolume * 0.002 + baseVolume * 0.3 * 0.001 + baseVolume * 0.1 * 0.08;
        monthFutureRevenue += revenue;
        activeModulesSet.add('VChain');
      }
      
      const marketplaceLaunchMonth = FUTURE_MODULE_DEFAULTS?.marketplace?.marketplaceLaunchMonth || 18;
      if ((parameters.enableMarketplace || false) && month >= marketplaceLaunchMonth) {
        const monthsActive = month - marketplaceLaunchMonth + 1;
        const rampUp = Math.min(1, monthsActive / 12);
        const gmv = currentUsers * 5 * rampUp;
        const revenue = gmv * 0.4 * 0.08 + gmv * 0.6 * 0.15;
        monthFutureRevenue += revenue;
        activeModulesSet.add('Marketplace');
      }
      
      const businessHubLaunchMonth = FUTURE_MODULE_DEFAULTS?.businessHub?.businessHubLaunchMonth || 21;
      if ((parameters.enableBusinessHub || false) && month >= businessHubLaunchMonth) {
        const monthsActive = month - businessHubLaunchMonth + 1;
        const rampUp = Math.min(1, monthsActive / 12);
        const freelancers = currentUsers * 0.02 * rampUp;
        const revenue = freelancers * 500 * 0.12 + currentUsers * 0.05 * rampUp * 15;
        monthFutureRevenue += revenue;
        activeModulesSet.add('Business Hub');
      }
      
      const crossPlatformLaunchMonth = FUTURE_MODULE_DEFAULTS?.crossPlatform?.crossPlatformLaunchMonth || 15;
      if ((parameters.enableCrossPlatform || false) && month >= crossPlatformLaunchMonth) {
        const monthsActive = month - crossPlatformLaunchMonth + 1;
        const rampUp = Math.min(1, monthsActive / 12);
        const revenue = currentUsers * 0.03 * rampUp * 10 + currentUsers * 0.01 * rampUp * 50 * 0.15;
        monthFutureRevenue += revenue;
        activeModulesSet.add('Cross-Platform');
      }
      
      yearFutureRevenue += monthFutureRevenue;
      const monthTotalRevenue = monthCoreRevenue + monthFutureRevenue;
      // Costs include operational costs (25% of revenue) plus marketing spend
      const monthOperationalCosts = monthTotalRevenue * 0.25;
      yearRevenue += monthTotalRevenue;
      yearProfit += monthTotalRevenue - monthOperationalCosts;
    }
    
    // Subtract marketing budget from profit (it's an expense)
    const yearProfitAfterMarketing = yearProfit - yearMarketingBudget;
    
    // Update end-of-year user growth ratio for reporting (already applied at start of year)
    const endOfYearGrowthRatio = currentUsers / baseUsers;
    
    projections.push({
      year,
      startMonth,
      endMonth,
      startUsers,
      endUsers: currentUsers,
      avgUsers: Math.round((startUsers + currentUsers) / 2),
      totalRevenue: yearRevenue,
      totalProfit: yearProfitAfterMarketing,
      avgMargin: yearRevenue > 0 ? (yearProfitAfterMarketing / yearRevenue) * 100 : 0,
      tokenPriceStart: startPrice,
      tokenPriceEnd: currentTokenPrice,
      coreModulesRevenue: yearCoreRevenue,
      futureModulesRevenue: yearFutureRevenue,
      activeModules: Array.from(activeModulesSet),
      marketCycle: cycleData.phase,
      cycleMultiplier,
      // Marketing budget (Dec 2025)
      marketingBudget: yearMarketingBudget,
      marketingMultiplier,
      // User growth price impact (Dec 2025)
      userGrowthPriceMultiplier,
      userGrowthRatio: endOfYearGrowthRatio,
    });
  }
  
  return projections;
}

export function Year5Overview({ result, parameters }: Year5OverviewProps) {
  const scenario = (parameters.growthScenario || 'base') as keyof typeof GROWTH_SCENARIOS;
  const marketCondition = (parameters.marketCondition || 'bull') as keyof typeof MARKET_CONDITIONS;
  const scenarioConfig = GROWTH_SCENARIOS[scenario];
  const marketConfig = MARKET_CONDITIONS[marketCondition];
  
  const fiveYearProjections = useMemo(() => {
    return calculate5YearProjections(result, scenarioConfig, marketConfig, parameters.tokenPrice, parameters);
  }, [result, scenarioConfig, marketConfig, parameters]);
  
  const enabledFutureModules = {
    vchain: parameters.enableVchain || false,
    marketplace: parameters.enableMarketplace || false,
    businessHub: parameters.enableBusinessHub || false,
    crossPlatform: parameters.enableCrossPlatform || false,
  };
  const hasFutureModules = Object.values(enabledFutureModules).some(Boolean);
  
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

