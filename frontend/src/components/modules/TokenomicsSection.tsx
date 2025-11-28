'use client';

import { useMemo } from 'react';
import { SimulationParameters, MonthlyProgressionResult } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { TOKEN_ALLOCATION, TGE_BREAKDOWN, CONFIG } from '@/lib/constants';

interface TokenomicsSectionProps {
  parameters: SimulationParameters;
  monthlyResult?: MonthlyProgressionResult;
}

// Allocation colors for pie chart
const ALLOCATION_COLORS: Record<string, string> = {
  SEED: '#FF6B6B',       // Coral red
  PRIVATE: '#4ECDC4',    // Teal
  PUBLIC: '#45B7D1',     // Sky blue
  TEAM: '#96CEB4',       // Sage green
  ADVISORS: '#FFEAA7',   // Soft yellow
  TREASURY: '#DDA0DD',   // Plum
  REWARDS: '#98D8C8',    // Mint
  LIQUIDITY: '#F7DC6F',  // Golden
  FOUNDATION: '#BB8FCE', // Lavender
  MARKETING: '#85C1E9',  // Light blue
};

// Calculate vesting unlock for a month
// NOTE: vesting_months = actual duration of vesting (NOT including cliff)
// Total unlock period = cliff_months + vesting_months
function getMonthlyUnlock(category: string, month: number): number {
  const config = TOKEN_ALLOCATION[category as keyof typeof TOKEN_ALLOCATION];
  if (!config) return 0;
  
  const tokens = config.tokens;
  const tgePercent = config.tge_percent || 0;
  const cliffMonths = config.cliff_months || 0;
  const vestingMonths = config.vesting_months || 0;
  
  // TGE (month 0)
  if (month === 0) {
    return Math.floor(tokens * tgePercent);
  }
  
  // Programmatic (Treasury, Rewards)
  if (config.is_programmatic) {
    if (category === 'REWARDS' && config.emission_months) {
      if (month >= 1 && month <= config.emission_months) {
        return Math.floor(tokens / config.emission_months);
      }
    }
    return 0;
  }
  
  // During cliff (no unlocks)
  if (month <= cliffMonths) {
    return 0;
  }
  
  // Calculate vesting end month: cliff + vesting duration
  const vestingEndMonth = cliffMonths + vestingMonths;
  
  // After full vesting
  if (vestingMonths === 0 || month > vestingEndMonth) {
    return 0;
  }
  
  // During vesting (after cliff, before end)
  const tokensAfterTge = tokens - Math.floor(tokens * tgePercent);
  // vestingMonths IS the actual vesting duration
  if (vestingMonths > 0) {
    return Math.floor(tokensAfterTge / vestingMonths);
  }
  
  return 0;
}

// Calculate cumulative circulating at month
function getCirculatingAtMonth(month: number): { total: number; breakdown: Record<string, number> } {
  const categories = Object.keys(TOKEN_ALLOCATION) as (keyof typeof TOKEN_ALLOCATION)[];
  const breakdown: Record<string, number> = {};
  let total = 0;
  
  for (const cat of categories) {
    let cumulative = 0;
    for (let m = 0; m <= month; m++) {
      cumulative += getMonthlyUnlock(cat, m);
    }
    breakdown[cat] = cumulative;
    total += cumulative;
  }
  
  return { total, breakdown };
}

export function TokenomicsSection({ parameters, monthlyResult }: TokenomicsSectionProps) {
  // Calculate pie chart segments
  const pieSegments = useMemo(() => {
    const categories = Object.entries(TOKEN_ALLOCATION);
    let startAngle = 0;
    
    return categories.map(([key, config]) => {
      const percent = config.percent;
      const angle = percent * 360;
      const segment = {
        key,
        name: config.name,
        percent: percent * 100,
        tokens: config.tokens,
        color: ALLOCATION_COLORS[key],
        startAngle,
        endAngle: startAngle + angle,
        tgePercent: config.tge_percent * 100,
        cliffMonths: config.cliff_months || 0,
        vestingMonths: config.vesting_months || 0,
        isProgrammatic: config.is_programmatic || false,
      };
      startAngle += angle;
      return segment;
    });
  }, []);
  
  // Calculate vesting milestones
  const vestingMilestones = useMemo(() => {
    const milestones = [];
    const checkMonths = [0, 3, 6, 12, 18, 24, 36, 48, 60];
    
    for (const month of checkMonths) {
      const { total, breakdown } = getCirculatingAtMonth(month);
      const percent = (total / CONFIG.SUPPLY.TOTAL) * 100;
      milestones.push({ month, total, percent, breakdown });
    }
    
    return milestones;
  }, []);
  
  // Get current month data from progression if available
  const currentMonth = monthlyResult?.monthlyData?.length || 0;
  const currentCirculating = monthlyResult?.finalCirculatingSupply || getCirculatingAtMonth(currentMonth).total;
  const currentPercent = monthlyResult?.finalCirculatingPercent || (currentCirculating / CONFIG.SUPPLY.TOTAL * 100);
  
  // Treasury tracking
  const treasuryAccumulated = monthlyResult?.totalTreasuryAccumulatedUsd || 0;
  const treasuryRevenueShare = (parameters.treasuryRevenueShare || 0.20) * 100;
  
  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-900/40 to-indigo-900/40 rounded-xl p-6 border border-purple-500/30">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center">
            <span className="text-2xl">🪙</span>
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">Token Allocation</h2>
            <p className="text-purple-300 text-sm">Official VCoin Tokenomics - 1B Total Supply</p>
          </div>
        </div>
        
        {/* Key Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-purple-400 text-xs font-medium">Total Supply</div>
            <div className="text-white text-lg font-bold">{formatNumber(CONFIG.SUPPLY.TOTAL)}</div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-purple-400 text-xs font-medium">TGE Circulating</div>
            <div className="text-white text-lg font-bold">{formatNumber(TGE_BREAKDOWN.TOTAL)}</div>
            <div className="text-purple-300 text-xs">{((TGE_BREAKDOWN.TOTAL / CONFIG.SUPPLY.TOTAL) * 100).toFixed(1)}%</div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-purple-400 text-xs font-medium">Rewards Pool</div>
            <div className="text-white text-lg font-bold">{formatNumber(CONFIG.SUPPLY.REWARDS_ALLOCATION)}</div>
            <div className="text-purple-300 text-xs">{CONFIG.SUPPLY.REWARDS_DURATION_MONTHS} months</div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-purple-400 text-xs font-medium">Monthly Emission</div>
            <div className="text-white text-lg font-bold">{formatNumber(CONFIG.MONTHLY_EMISSION)}</div>
            <div className="text-purple-300 text-xs">5% platform fee</div>
          </div>
        </div>
      </div>
      
      {/* Allocation Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Pie Chart Visual */}
        <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-700/50">
          <h3 className="text-lg font-semibold text-white mb-4">Allocation Distribution</h3>
          
          {/* SVG Pie Chart */}
          <div className="flex justify-center">
            <svg viewBox="0 0 200 200" className="w-64 h-64">
              {pieSegments.map((segment) => {
                const startRad = (segment.startAngle - 90) * (Math.PI / 180);
                const endRad = (segment.endAngle - 90) * (Math.PI / 180);
                const largeArc = segment.percent > 50 ? 1 : 0;
                
                const x1 = 100 + 80 * Math.cos(startRad);
                const y1 = 100 + 80 * Math.sin(startRad);
                const x2 = 100 + 80 * Math.cos(endRad);
                const y2 = 100 + 80 * Math.sin(endRad);
                
                const d = `M 100 100 L ${x1} ${y1} A 80 80 0 ${largeArc} 1 ${x2} ${y2} Z`;
                
                return (
                  <path
                    key={segment.key}
                    d={d}
                    fill={segment.color}
                    stroke="#1f2937"
                    strokeWidth="1"
                    className="hover:opacity-80 transition-opacity cursor-pointer"
                  >
                    <title>{`${segment.name}: ${segment.percent.toFixed(0)}% (${formatNumber(segment.tokens)})`}</title>
                  </path>
                );
              })}
              {/* Center circle */}
              <circle cx="100" cy="100" r="40" fill="#111827" />
              <text x="100" y="95" textAnchor="middle" fill="white" fontSize="12" fontWeight="bold">1B</text>
              <text x="100" y="110" textAnchor="middle" fill="#9ca3af" fontSize="8">VCoin</text>
            </svg>
          </div>
          
          {/* Legend */}
          <div className="grid grid-cols-2 gap-2 mt-4">
            {pieSegments.map((segment) => (
              <div key={segment.key} className="flex items-center gap-2 text-sm">
                <div 
                  className="w-3 h-3 rounded-full" 
                  style={{ backgroundColor: segment.color }}
                />
                <span className="text-gray-400">{segment.name}</span>
                <span className="text-white font-medium ml-auto">{segment.percent.toFixed(0)}%</span>
              </div>
            ))}
          </div>
        </div>
        
        {/* Allocation Table */}
        <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-700/50">
          <h3 className="text-lg font-semibold text-white mb-4">Vesting Schedule</h3>
          
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-400 border-b border-gray-700">
                  <th className="text-left py-2">Category</th>
                  <th className="text-right py-2">TGE</th>
                  <th className="text-right py-2">Cliff</th>
                  <th className="text-right py-2">Vesting</th>
                </tr>
              </thead>
              <tbody>
                {pieSegments.map((segment) => (
                  <tr key={segment.key} className="border-b border-gray-800 hover:bg-gray-800/30">
                    <td className="py-2">
                      <div className="flex items-center gap-2">
                        <div 
                          className="w-2 h-2 rounded-full" 
                          style={{ backgroundColor: segment.color }}
                        />
                        <span className="text-white">{segment.name}</span>
                      </div>
                    </td>
                    <td className="text-right text-gray-300 py-2">
                      {segment.tgePercent.toFixed(0)}%
                    </td>
                    <td className="text-right text-gray-300 py-2">
                      {segment.isProgrammatic ? '-' : `${segment.cliffMonths}m`}
                    </td>
                    <td className="text-right text-gray-300 py-2">
                      {segment.isProgrammatic ? 'Programmatic' : `${segment.vestingMonths}m`}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      {/* Circulating Supply Timeline */}
      <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">Circulating Supply Over Time</h3>
        
        {/* Timeline Bar */}
        <div className="relative h-8 bg-gray-800 rounded-full overflow-hidden mb-4">
          {vestingMilestones.map((milestone, idx) => {
            const width = milestone.percent;
            return (
              <div
                key={milestone.month}
                className="absolute h-full bg-gradient-to-r from-purple-600 to-indigo-600 transition-all duration-500"
                style={{ width: `${width}%` }}
                title={`Month ${milestone.month}: ${milestone.percent.toFixed(1)}%`}
              />
            );
          })}
          {/* Current position marker */}
          {currentMonth > 0 && (
            <div 
              className="absolute top-0 h-full w-1 bg-yellow-400"
              style={{ left: `${currentPercent}%` }}
            />
          )}
        </div>
        
        {/* Milestones Grid */}
        <div className="grid grid-cols-3 md:grid-cols-5 lg:grid-cols-9 gap-2">
          {vestingMilestones.map((milestone) => (
            <div 
              key={milestone.month}
              className={`text-center p-2 rounded-lg ${
                milestone.month === currentMonth 
                  ? 'bg-purple-600/30 border border-purple-500' 
                  : 'bg-gray-800/50'
              }`}
            >
              <div className="text-gray-400 text-xs">
                {milestone.month === 0 ? 'TGE' : `M${milestone.month}`}
              </div>
              <div className="text-white font-medium text-sm">
                {milestone.percent.toFixed(0)}%
              </div>
              <div className="text-gray-500 text-xs">
                {(milestone.total / 1_000_000).toFixed(0)}M
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Treasury Tracking */}
      <div className="bg-gradient-to-r from-amber-900/30 to-yellow-900/30 rounded-xl p-6 border border-amber-500/30">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-10 h-10 bg-gradient-to-br from-amber-500 to-yellow-600 rounded-lg flex items-center justify-center">
            <span className="text-xl">🏛️</span>
          </div>
          <div>
            <h3 className="text-lg font-semibold text-white">Treasury / DAO</h3>
            <p className="text-amber-300 text-sm">{treasuryRevenueShare}% of platform revenue</p>
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-amber-400 text-xs font-medium">Total Allocation</div>
            <div className="text-white text-lg font-bold">{formatNumber(CONFIG.SUPPLY.TREASURY_ALLOCATION)}</div>
            <div className="text-amber-300 text-xs">20% of supply</div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-amber-400 text-xs font-medium">Revenue Share</div>
            <div className="text-white text-lg font-bold">{treasuryRevenueShare}%</div>
            <div className="text-amber-300 text-xs">of platform revenue</div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-amber-400 text-xs font-medium">Accumulated (USD)</div>
            <div className="text-white text-lg font-bold">{formatCurrency(treasuryAccumulated)}</div>
            <div className="text-amber-300 text-xs">from {currentMonth} months</div>
          </div>
          <div className="bg-black/30 rounded-lg p-3">
            <div className="text-amber-400 text-xs font-medium">Release Type</div>
            <div className="text-white text-lg font-bold">Programmatic</div>
            <div className="text-amber-300 text-xs">Governance controlled</div>
          </div>
        </div>
      </div>
      
      {/* TGE Breakdown */}
      <div className="bg-gray-900/50 rounded-xl p-6 border border-gray-700/50">
        <h3 className="text-lg font-semibold text-white mb-4">TGE Circulating Breakdown</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
          {Object.entries(TGE_BREAKDOWN).filter(([key]) => key !== 'TOTAL').map(([key, tokens]) => (
            <div 
              key={key}
              className={`rounded-lg p-3 ${tokens > 0 ? 'bg-green-900/20' : 'bg-gray-800/30'}`}
            >
              <div className="flex items-center gap-2 mb-1">
                <div 
                  className="w-2 h-2 rounded-full" 
                  style={{ backgroundColor: ALLOCATION_COLORS[key] }}
                />
                <span className="text-gray-400 text-xs">{TOKEN_ALLOCATION[key as keyof typeof TOKEN_ALLOCATION]?.name}</span>
              </div>
              <div className={`font-bold ${tokens > 0 ? 'text-green-400' : 'text-gray-500'}`}>
                {tokens > 0 ? formatNumber(tokens) : '0'}
              </div>
              {tokens > 0 && (
                <div className="text-green-300 text-xs">
                  {((tokens / TGE_BREAKDOWN.TOTAL) * 100).toFixed(1)}% of TGE
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="mt-4 p-3 bg-green-900/20 rounded-lg border border-green-500/30">
          <div className="flex justify-between items-center">
            <span className="text-green-400 font-medium">Total TGE Circulating</span>
            <div className="text-right">
              <span className="text-white font-bold">{formatNumber(TGE_BREAKDOWN.TOTAL)}</span>
              <span className="text-green-300 text-sm ml-2">
                ({((TGE_BREAKDOWN.TOTAL / CONFIG.SUPPLY.TOTAL) * 100).toFixed(1)}%)
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

