'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { useMemo } from 'react';

// Token allocation configuration matching backend (viwo-tokenomics-2025-12-03.csv)
// Note: Ecosystem rewards start at TGE (month 0) per tokenomics tool
const TOKEN_ALLOCATIONS = {
  SEED: { name: 'Seed Round', percent: 4, tokens: 40_000_000, tge: 0, cliff: 12, vesting: 24, color: 'bg-amber-500' },
  PRIVATE: { name: 'Private Round', percent: 4, tokens: 40_000_000, tge: 10, cliff: 6, vesting: 18, color: 'bg-purple-500' },
  PUBLIC: { name: 'Public Sale', percent: 8, tokens: 80_000_000, tge: 50, cliff: 0, vesting: 3, color: 'bg-blue-500' },
  TEAM: { name: 'Team', percent: 15, tokens: 150_000_000, tge: 0, cliff: 12, vesting: 36, color: 'bg-rose-500' },
  ADVISORS: { name: 'Advisors', percent: 3, tokens: 30_000_000, tge: 0, cliff: 6, vesting: 18, color: 'bg-cyan-500' },
  TREASURY: { name: 'Treasury', percent: 20, tokens: 200_000_000, tge: 0, cliff: 0, vesting: 0, color: 'bg-slate-500', isGovernance: true },
  REWARDS: { name: 'Ecosystem', percent: 35, tokens: 350_000_000, tge: 0, cliff: 0, vesting: 60, color: 'bg-emerald-500', isDynamic: true, startsAtTGE: true },
  LIQUIDITY: { name: 'Liquidity', percent: 5, tokens: 50_000_000, tge: 100, cliff: 0, vesting: 0, color: 'bg-indigo-500' },
  MARKETING: { name: 'Marketing', percent: 6, tokens: 60_000_000, tge: 25, cliff: 3, vesting: 18, color: 'bg-pink-500' },
};

// Calculate unlock for a category at a specific month
function calculateUnlock(category: typeof TOKEN_ALLOCATIONS[keyof typeof TOKEN_ALLOCATIONS], month: number): number {
  // Governance/Treasury - no automatic unlock
  if (category.isGovernance) {
    return 0;
  }
  
  // Dynamic rewards (Ecosystem) - starts at TGE (month 0) per viwo-tokenomics tool
  if (category.isDynamic && category.vesting > 0) {
    // Ecosystem distributes from month 0 to month 59 (60 months total)
    if (month >= 0 && month < category.vesting) {
      return Math.floor(category.tokens / category.vesting);
    }
    return 0;
  }
  
  // TGE unlock (for non-programmatic categories)
  if (month === 0) {
    return Math.floor(category.tokens * (category.tge / 100));
  }
  
  // No vesting
  if (category.vesting === 0) {
    return 0;
  }
  
  // During cliff
  if (month <= category.cliff) {
    return 0;
  }
  
  // After vesting complete
  const vestingEnd = category.cliff + category.vesting;
  if (month > vestingEnd) {
    return 0;
  }
  
  // During vesting
  const tokensAfterTge = category.tokens - Math.floor(category.tokens * (category.tge / 100));
  return Math.floor(tokensAfterTge / category.vesting);
}

// Calculate cumulative supply at a month
function calculateCumulativeSupply(month: number): { total: number; byCategory: Record<string, number> } {
  const byCategory: Record<string, number> = {};
  let total = 0;
  
  for (const [key, category] of Object.entries(TOKEN_ALLOCATIONS)) {
    let cumulative = 0;
    for (let m = 0; m <= month; m++) {
      cumulative += calculateUnlock(category, m);
    }
    byCategory[key] = cumulative;
    total += cumulative;
  }
  
  return { total, byCategory };
}

interface TokenUnlocksSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function TokenUnlocksSection({ result, parameters }: TokenUnlocksSectionProps) {
  // Calculate milestones
  const milestones = useMemo(() => {
    const totalSupply = 1_000_000_000;
    let month25 = 0, month50 = 0, month75 = 0, month100 = 0;
    
    for (let m = 0; m <= 60; m++) {
      const { total } = calculateCumulativeSupply(m);
      const pct = (total / totalSupply) * 100;
      
      if (month25 === 0 && pct >= 25) month25 = m;
      if (month50 === 0 && pct >= 50) month50 = m;
      if (month75 === 0 && pct >= 75) month75 = m;
      if (month100 === 0 && pct >= 99) month100 = m;
    }
    
    return { month25, month50, month75, month100 };
  }, []);

  // Generate vesting schedule data
  const vestingSchedule = useMemo(() => {
    const schedule = [];
    for (let month = 0; month <= 60; month++) {
      const unlocks: Record<string, number> = {};
      let totalUnlock = 0;
      
      for (const [key, category] of Object.entries(TOKEN_ALLOCATIONS)) {
        const unlock = calculateUnlock(category, month);
        unlocks[key] = unlock;
        totalUnlock += unlock;
      }
      
      const { total: cumulative } = calculateCumulativeSupply(month);
      
      schedule.push({
        month,
        unlocks,
        totalUnlock,
        cumulative,
        percentCirculating: (cumulative / 1_000_000_000) * 100,
      });
    }
    return schedule;
  }, []);

  // TGE breakdown
  const tgeBreakdown = useMemo(() => {
    return Object.entries(TOKEN_ALLOCATIONS)
      .filter(([_, cat]) => cat.tge > 0)
      .map(([key, cat]) => ({
        key,
        name: cat.name,
        amount: Math.floor(cat.tokens * (cat.tge / 100)),
        color: cat.color,
      }));
  }, []);

  const tgeTotal = tgeBreakdown.reduce((sum, item) => sum + item.amount, 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200 p-6">
        <h2 className="text-xl font-bold text-indigo-900 flex items-center gap-2 mb-2">
          <span className="text-2xl">📅</span> Token Vesting Schedule
        </h2>
        <p className="text-indigo-600 text-sm">
          Complete token unlock timeline from TGE to full circulation (60 months)
        </p>
      </div>

      {/* TGE Breakdown */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
          <span className="text-xl">🎯</span> TGE (Token Generation Event)
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {tgeBreakdown.map(({ key, name, amount, color }) => (
            <div key={key} className="bg-slate-50 rounded-lg p-3">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-3 h-3 rounded-full ${color}`} />
                <span className="text-sm font-medium text-slate-700">{name}</span>
              </div>
              <div className="text-lg font-bold text-slate-900">
                {(amount / 1_000_000).toFixed(0)}M
              </div>
              <div className="text-xs text-slate-500">
                {((amount / 1_000_000_000) * 100).toFixed(1)}% of supply
              </div>
            </div>
          ))}
        </div>
        <div className="bg-indigo-50 rounded-lg p-4 flex justify-between items-center">
          <span className="font-medium text-indigo-800">Total TGE Circulating</span>
          <span className="text-2xl font-bold text-indigo-600">
            {(tgeTotal / 1_000_000).toFixed(0)}M
            <span className="text-sm font-normal ml-2">
              ({((tgeTotal / 1_000_000_000) * 100).toFixed(1)}%)
            </span>
          </span>
        </div>
      </div>

      {/* Milestones */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
          <span className="text-xl">🏁</span> Supply Milestones
        </h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center p-4 bg-emerald-50 rounded-xl">
            <div className="text-3xl font-bold text-emerald-600">Month {milestones.month25}</div>
            <div className="text-sm text-emerald-700">25% Circulating</div>
            <div className="text-xs text-slate-500 mt-1">250M tokens</div>
          </div>
          <div className="text-center p-4 bg-blue-50 rounded-xl">
            <div className="text-3xl font-bold text-blue-600">Month {milestones.month50}</div>
            <div className="text-sm text-blue-700">50% Circulating</div>
            <div className="text-xs text-slate-500 mt-1">500M tokens</div>
          </div>
          <div className="text-center p-4 bg-purple-50 rounded-xl">
            <div className="text-3xl font-bold text-purple-600">Month {milestones.month75}</div>
            <div className="text-sm text-purple-700">75% Circulating</div>
            <div className="text-xs text-slate-500 mt-1">750M tokens</div>
          </div>
          <div className="text-center p-4 bg-amber-50 rounded-xl">
            <div className="text-3xl font-bold text-amber-600">Month {milestones.month100}</div>
            <div className="text-sm text-amber-700">~100% Circulating</div>
            <div className="text-xs text-slate-500 mt-1">800M tokens*</div>
          </div>
        </div>
        <p className="text-xs text-slate-500 mt-3 text-center">
          *Treasury (200M) is governance-controlled and not included in automatic vesting
        </p>
      </div>

      {/* Category Vesting Timeline */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
        <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
          <span className="text-xl">📊</span> Category Vesting Timeline
        </h3>
        <div className="space-y-3">
          {Object.entries(TOKEN_ALLOCATIONS).map(([key, category]) => {
            const vestingEnd = category.cliff + category.vesting;
            const tgeWidth = category.tge > 0 ? 2 : 0;
            const cliffWidth = (category.cliff / 60) * 100;
            const vestingWidth = (category.vesting / 60) * 100;
            
            return (
              <div key={key} className="flex items-center gap-3">
                <div className="w-24 text-sm font-medium text-slate-700 flex items-center gap-2">
                  <div className={`w-3 h-3 rounded-full ${category.color}`} />
                  {category.name}
                </div>
                <div className="flex-1 relative">
                  <div className="h-6 bg-slate-100 rounded-full overflow-hidden flex">
                    {/* TGE */}
                    {category.tge > 0 && (
                      <div 
                        className={`${category.color} h-full flex items-center justify-center text-white text-xs font-medium`}
                        style={{ width: `${tgeWidth}%`, minWidth: '24px' }}
                        title={`TGE: ${category.tge}%`}
                      >
                        TGE
                      </div>
                    )}
                    {/* Cliff */}
                    {category.cliff > 0 && (
                      <div 
                        className="bg-slate-300 h-full flex items-center justify-center text-slate-600 text-xs"
                        style={{ width: `${cliffWidth}%` }}
                        title={`Cliff: ${category.cliff} months`}
                      >
                        {cliffWidth > 5 && 'Cliff'}
                      </div>
                    )}
                    {/* Vesting */}
                    {category.vesting > 0 && !category.isGovernance && (
                      <div 
                        className={`${category.color} opacity-60 h-full flex items-center justify-center text-white text-xs`}
                        style={{ width: `${vestingWidth}%` }}
                        title={`Vesting: ${category.vesting} months`}
                      >
                        {vestingWidth > 8 && `${category.vesting}mo`}
                      </div>
                    )}
                    {/* Governance */}
                    {category.isGovernance && (
                      <div 
                        className="bg-slate-400 h-full flex items-center justify-center text-white text-xs flex-1"
                        title="Governance-controlled"
                      >
                        DAO Controlled
                      </div>
                    )}
                  </div>
                </div>
                <div className="w-20 text-right text-sm">
                  <span className="font-medium text-slate-800">{category.percent}%</span>
                  <span className="text-slate-500 text-xs ml-1">({(category.tokens / 1_000_000)}M)</span>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Legend */}
        <div className="flex flex-wrap gap-4 mt-4 pt-4 border-t border-slate-200 text-xs">
          <div className="flex items-center gap-1">
            <div className="w-4 h-3 bg-emerald-500 rounded" />
            <span className="text-slate-600">TGE Unlock</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-3 bg-slate-300 rounded" />
            <span className="text-slate-600">Cliff Period</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-3 bg-emerald-500 opacity-60 rounded" />
            <span className="text-slate-600">Linear Vesting</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-4 h-3 bg-slate-400 rounded" />
            <span className="text-slate-600">Governance Controlled</span>
          </div>
        </div>
      </div>

      {/* Detailed Monthly Schedule (First 12 months) */}
      <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm overflow-x-auto">
        <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
          <span className="text-xl">📋</span> Year 1 Monthly Unlocks
        </h3>
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-200">
              <th className="py-2 px-2 text-left text-slate-600 font-medium">Month</th>
              {Object.entries(TOKEN_ALLOCATIONS)
                .filter(([_, cat]) => !cat.isGovernance)
                .map(([key, cat]) => (
                  <th key={key} className="py-2 px-2 text-right text-slate-600 font-medium">
                    <div className="flex items-center justify-end gap-1">
                      <div className={`w-2 h-2 rounded-full ${cat.color}`} />
                      {cat.name.split(' ')[0]}
                    </div>
                  </th>
                ))}
              <th className="py-2 px-2 text-right text-slate-800 font-bold">Total</th>
              <th className="py-2 px-2 text-right text-slate-800 font-bold">Cumulative</th>
            </tr>
          </thead>
          <tbody>
            {vestingSchedule.slice(0, 13).map((month) => (
              <tr 
                key={month.month} 
                className={`border-b border-slate-100 ${month.month === 0 ? 'bg-indigo-50' : ''}`}
              >
                <td className="py-2 px-2 font-medium text-slate-700">
                  {month.month === 0 ? 'TGE' : `M${month.month}`}
                </td>
                {Object.entries(TOKEN_ALLOCATIONS)
                  .filter(([_, cat]) => !cat.isGovernance)
                  .map(([key]) => (
                    <td key={key} className="py-2 px-2 text-right text-slate-600">
                      {month.unlocks[key] > 0 
                        ? `${(month.unlocks[key] / 1_000_000).toFixed(1)}M`
                        : '-'
                      }
                    </td>
                  ))}
                <td className="py-2 px-2 text-right font-medium text-slate-800">
                  {(month.totalUnlock / 1_000_000).toFixed(1)}M
                </td>
                <td className="py-2 px-2 text-right font-bold text-indigo-600">
                  {(month.cumulative / 1_000_000).toFixed(0)}M
                  <span className="text-xs text-slate-500 ml-1">
                    ({month.percentCirculating.toFixed(1)}%)
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Key Years Summary */}
      <div className="bg-gradient-to-br from-slate-50 to-indigo-50 rounded-xl border border-slate-200 p-6">
        <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
          <span className="text-xl">📈</span> 5-Year Circulation Summary
        </h3>
        <div className="grid grid-cols-5 gap-4">
          {[12, 24, 36, 48, 60].map((month) => {
            const data = vestingSchedule[month];
            return (
              <div key={month} className="bg-white rounded-xl p-4 text-center shadow-sm">
                <div className="text-sm text-slate-500 mb-1">Year {month / 12}</div>
                <div className="text-2xl font-bold text-indigo-600">
                  {(data.cumulative / 1_000_000).toFixed(0)}M
                </div>
                <div className="text-xs text-slate-500">
                  {data.percentCirculating.toFixed(1)}% of supply
                </div>
                <div className="mt-2 h-2 bg-slate-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-indigo-500 rounded-full"
                    style={{ width: `${Math.min(100, data.percentCirculating)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

export default TokenUnlocksSection;

