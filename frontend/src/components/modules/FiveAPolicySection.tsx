'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface FiveAPolicySectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

// Star icon component with fill percentage
function StarIcon({ fillPercent, size = 24 }: { fillPercent: number; size?: number }) {
  const fillWidth = Math.min(100, Math.max(0, fillPercent));
  
  return (
    <div className="relative" style={{ width: size, height: size }}>
      {/* Background star (empty) */}
      <svg 
        viewBox="0 0 24 24" 
        fill="none" 
        stroke="currentColor" 
        strokeWidth="2"
        className="absolute inset-0 text-gray-600"
        style={{ width: size, height: size }}
      >
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
      {/* Filled star (partial) */}
      <div className="absolute inset-0 overflow-hidden" style={{ width: `${fillWidth}%` }}>
        <svg 
          viewBox="0 0 24 24" 
          fill="currentColor" 
          className="text-yellow-400"
          style={{ width: size, height: size }}
        >
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      </div>
    </div>
  );
}

// Star row component
function StarRow({ 
  name, 
  displayName, 
  avgPercent, 
  tierCounts,
  weight 
}: { 
  name: string;
  displayName: string;
  avgPercent: number;
  tierCounts: Record<string, number>;
  weight: number;
}) {
  const total = Object.values(tierCounts).reduce((a, b) => a + b, 0);
  
  return (
    <div className="flex items-center gap-4 p-3 bg-gray-800/50 rounded-lg">
      <div className="flex items-center gap-2 w-48">
        <StarIcon fillPercent={avgPercent} size={28} />
        <div>
          <div className="font-medium text-white">{displayName}</div>
          <div className="text-xs text-gray-400">Weight: {(weight * 100).toFixed(0)}%</div>
        </div>
      </div>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <div className="text-2xl font-bold text-yellow-400">{avgPercent.toFixed(1)}%</div>
          <div className="text-sm text-gray-400">avg</div>
        </div>
      </div>
      <div className="flex gap-3 text-xs">
        <div className="text-center">
          <div className="text-orange-400 font-medium">{formatNumber(tierCounts.bronze || 0)}</div>
          <div className="text-gray-500">Bronze</div>
        </div>
        <div className="text-center">
          <div className="text-gray-300 font-medium">{formatNumber(tierCounts.silver || 0)}</div>
          <div className="text-gray-500">Silver</div>
        </div>
        <div className="text-center">
          <div className="text-yellow-400 font-medium">{formatNumber(tierCounts.gold || 0)}</div>
          <div className="text-gray-500">Gold</div>
        </div>
        <div className="text-center">
          <div className="text-cyan-400 font-medium">{formatNumber(tierCounts.diamond || 0)}</div>
          <div className="text-gray-500">Diamond</div>
        </div>
      </div>
    </div>
  );
}

// Multiplier distribution bar
function MultiplierBar({ 
  label, 
  count, 
  total, 
  color 
}: { 
  label: string; 
  count: number; 
  total: number; 
  color: string;
}) {
  const percent = total > 0 ? (count / total) * 100 : 0;
  
  return (
    <div className="mb-2">
      <div className="flex justify-between text-sm mb-1">
        <span className="text-gray-400">{label}</span>
        <span className={color}>{formatNumber(count)} ({percent.toFixed(1)}%)</span>
      </div>
      <div className="h-2 bg-gray-700 rounded-full overflow-hidden">
        <div 
          className={`h-full ${color.replace('text-', 'bg-')} rounded-full transition-all`}
          style={{ width: `${percent}%` }}
        />
      </div>
    </div>
  );
}

export function FiveAPolicySection({ result, parameters }: FiveAPolicySectionProps) {
  const fiveA = result.fiveA;
  
  // If 5A is not enabled or not available, show disabled state
  if (!fiveA || !fiveA.enabled) {
    return (
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <div className="flex items-center gap-3 mb-4">
          <div className="flex gap-1">
            {[1, 2, 3, 4, 5].map((i) => (
              <StarIcon key={i} fillPercent={0} size={20} />
            ))}
          </div>
          <h2 className="text-xl font-bold text-white">5A Policy Gamification</h2>
          <span className="px-2 py-1 bg-gray-700 text-gray-400 text-xs rounded">Disabled</span>
        </div>
        <p className="text-gray-500">
          Enable the 5A Policy to evaluate users based on Authenticity, Accuracy, Agility, Activity, and Approved stars.
          Users start at 50% (neutral). Below 50% = earn less, down to 0x. Above 50% = earn more, up to 2x.
        </p>
      </div>
    );
  }
  
  const totalUsers = fiveA.totalUsers || 0;
  
  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="flex gap-1">
            {[
              fiveA.populationAvgIdentity,
              fiveA.populationAvgAccuracy,
              fiveA.populationAvgAgility,
              fiveA.populationAvgActivity,
              fiveA.populationAvgApproved,
            ].map((pct, i) => (
              <StarIcon key={i} fillPercent={pct} size={24} />
            ))}
          </div>
          <div>
            <h2 className="text-xl font-bold text-white">5A Policy Gamification</h2>
            <p className="text-sm text-gray-400">
              {formatNumber(totalUsers)} users | 50% = 1x neutral | 0% = 0x | 100% = 2x
            </p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-yellow-400">
            {fiveA.avgCompoundMultiplier.toFixed(2)}x
          </div>
          <div className="text-sm text-gray-400">Avg Multiplier</div>
        </div>
      </div>
      
      {/* Star Distributions */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Star Distributions</h3>
        <div className="space-y-2">
          <StarRow 
            name="identity"
            displayName="🔐 Authenticity (Authority)"
            avgPercent={fiveA.identityStar?.avgPercentage || 50}
            tierCounts={fiveA.identityStar?.tierCounts || {}}
            weight={fiveA.identityStar?.weight || 0.2}
          />
          <StarRow 
            name="accuracy"
            displayName="✓ Accuracy (Honesty)"
            avgPercent={fiveA.accuracyStar?.avgPercentage || 50}
            tierCounts={fiveA.accuracyStar?.tierCounts || {}}
            weight={fiveA.accuracyStar?.weight || 0.2}
          />
          <StarRow 
            name="agility"
            displayName="⚡ Agility"
            avgPercent={fiveA.agilityStar?.avgPercentage || 50}
            tierCounts={fiveA.agilityStar?.tierCounts || {}}
            weight={fiveA.agilityStar?.weight || 0.2}
          />
          <StarRow 
            name="activity"
            displayName="📊 Activity"
            avgPercent={fiveA.activityStar?.avgPercentage || 50}
            tierCounts={fiveA.activityStar?.tierCounts || {}}
            weight={fiveA.activityStar?.weight || 0.2}
          />
          <StarRow 
            name="approved"
            displayName="✅ Approved (Liability)"
            avgPercent={fiveA.approvedStar?.avgPercentage || 50}
            tierCounts={fiveA.approvedStar?.tierCounts || {}}
            weight={fiveA.approvedStar?.weight || 0.2}
          />
        </div>
      </div>
      
      {/* Multiplier Distribution - Linear Scale: 0% = 0x, 50% = 1x, 100% = 2x */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        <div className="bg-gray-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Multiplier Distribution</h3>
          <p className="text-xs text-gray-500 mb-3">Linear scale: 0% stars = 0x | 50% = 1x (neutral) | 100% = 2x</p>
          <MultiplierBar 
            label="Below Neutral (0x - 0.8x)"
            count={fiveA.penalizedUsersCount}
            total={totalUsers}
            color="text-red-400"
          />
          <MultiplierBar 
            label="Neutral Zone (0.8x - 1.2x)"
            count={fiveA.neutralUsersCount}
            total={totalUsers}
            color="text-gray-400"
          />
          <MultiplierBar 
            label="Above Neutral (1.2x - 1.6x)"
            count={fiveA.boostedUsersCount}
            total={totalUsers}
            color="text-green-400"
          />
          <MultiplierBar 
            label="High Performer (1.6x - 2x)"
            count={fiveA.eliteUsersCount}
            total={totalUsers}
            color="text-cyan-400"
          />
        </div>
        
        {/* Multiplier Stats */}
        <div className="bg-gray-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-4">Multiplier Metrics</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-2xl font-bold text-green-400">
                {fiveA.top10PercentMultiplier.toFixed(2)}x
              </div>
              <div className="text-xs text-gray-500">Top 10% Multiplier</div>
            </div>
            <div>
              <div className="text-2xl font-bold text-red-400">
                {fiveA.bottom10PercentMultiplier.toFixed(2)}x
              </div>
              <div className="text-xs text-gray-500">Bottom 10% Multiplier</div>
            </div>
            <div>
              <div className="text-xl font-bold text-yellow-400">
                {fiveA.medianCompoundMultiplier.toFixed(2)}x
              </div>
              <div className="text-xs text-gray-500">Median Multiplier</div>
            </div>
            <div>
              <div className="text-xl font-bold text-gray-300">
                ±{fiveA.stdCompoundMultiplier.toFixed(2)}
              </div>
              <div className="text-xs text-gray-500">Std Deviation</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Economic Impact */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Economic Impact</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-4 text-center">
            <div className="text-xl font-bold text-yellow-400">
              {fiveA.rewardRedistributionPercent.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">Reward Redistribution</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 text-center">
            <div className="text-xl font-bold text-green-400">
              {formatCurrency(fiveA.feeDiscountTotalUsd)}
            </div>
            <div className="text-xs text-gray-500">Fee Discounts Given</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 text-center">
            <div className="text-xl font-bold text-purple-400">
              +{fiveA.stakingApyBoostAvg.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">Avg Staking APY Boost</div>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-4 text-center">
            <div className="text-xl font-bold text-blue-400">
              +{fiveA.governancePowerBoostAvg.toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500">Avg Governance Boost</div>
          </div>
        </div>
      </div>
      
      {/* Module Impacts */}
      {fiveA.moduleImpacts && fiveA.moduleImpacts.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Module Impacts</h3>
          <div className="space-y-2">
            {fiveA.moduleImpacts.map((impact, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg">
                <div>
                  <div className="font-medium text-white">{impact.moduleName}</div>
                  <div className="text-xs text-gray-500">{impact.description}</div>
                </div>
                <div className="text-right">
                  <div className={`font-bold ${impact.boostPercent >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                    {impact.boostPercent >= 0 ? '+' : ''}{impact.boostPercent.toFixed(1)}%
                  </div>
                  <div className="text-xs text-gray-500">
                    {formatCurrency(impact.adjustedValue)} adjusted
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Platform-Wide Impact */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Platform-Wide Impact</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gradient-to-br from-green-900/50 to-green-800/30 rounded-lg p-4 text-center border border-green-700/30">
            <div className="text-xl font-bold text-green-400">
              {((fiveA.retentionBoost || 0) * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-400">Retention Boost</div>
            <div className="text-xs text-green-600 mt-1">Higher user loyalty</div>
          </div>
          <div className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 rounded-lg p-4 text-center border border-blue-700/30">
            <div className="text-xl font-bold text-blue-400">
              {((fiveA.growthBoost || 0) * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-400">Growth Boost</div>
            <div className="text-xs text-blue-600 mt-1">Faster user acquisition</div>
          </div>
          <div className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 rounded-lg p-4 text-center border border-purple-700/30">
            <div className="text-xl font-bold text-purple-400">
              {((fiveA.revenueBoost || 0) * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-400">Revenue Boost</div>
            <div className="text-xs text-purple-600 mt-1">Increased earnings</div>
          </div>
          <div className="bg-gradient-to-br from-yellow-900/50 to-yellow-800/30 rounded-lg p-4 text-center border border-yellow-700/30">
            <div className={`text-xl font-bold ${
              (fiveA.tokenPriceImpact || 0) >= 0 ? 'text-yellow-400' : 'text-red-400'
            }`}>
              {((fiveA.tokenPriceImpact || 0) * 100) >= 0 ? '+' : ''}{((fiveA.tokenPriceImpact || 0) * 100).toFixed(2)}%
            </div>
            <div className="text-xs text-gray-400">Token Price Impact</div>
            <div className="text-xs text-yellow-600 mt-1">VCoin value effect</div>
          </div>
        </div>
      </div>
      
      {/* User Segments (90-9-1 Rule) */}
      {fiveA.useSegments && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-400 mb-3">User Segments (Based on Real Social Media Behavior)</h3>
          <p className="text-xs text-gray-500 mb-3">
            20% inactive (ghost accounts), 40% lurkers (view only), 25% casual (weekly), 12% active (daily), 3% power users
          </p>
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3">
            {/* Inactive / Ghost Users */}
            <div className="bg-gradient-to-br from-red-950/80 to-red-900/50 rounded-lg p-4 border border-red-800/50">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">👻</span>
                <div className="text-sm font-medium text-red-300">Inactive</div>
              </div>
              <div className="text-2xl font-bold text-red-400">
                {formatNumber(fiveA.inactiveCount || 0)}
              </div>
              <div className="text-xs text-red-500/70">
                {fiveA.totalUsers > 0 
                  ? ((fiveA.inactiveCount || 0) / fiveA.totalUsers * 100).toFixed(0)
                  : 20}% of users
              </div>
              <div className="mt-2 pt-2 border-t border-red-800/50">
                <div className="text-xs text-red-500 font-bold">
                  {(fiveA.inactiveAvgMultiplier || 0.03).toFixed(2)}x avg
                </div>
                <div className="text-xs text-red-700">ZERO VCoin earned</div>
              </div>
            </div>
            
            {/* Lurkers */}
            <div className="bg-gradient-to-br from-gray-800/80 to-gray-900/80 rounded-lg p-4 border border-gray-700">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">👀</span>
                <div className="text-sm font-medium text-gray-300">Lurkers</div>
              </div>
              <div className="text-2xl font-bold text-gray-400">
                {formatNumber(fiveA.lurkersCount || 0)}
              </div>
              <div className="text-xs text-gray-500">
                {fiveA.totalUsers > 0 
                  ? ((fiveA.lurkersCount || 0) / fiveA.totalUsers * 100).toFixed(0)
                  : 40}% of users
              </div>
              <div className="mt-2 pt-2 border-t border-gray-700">
                <div className="text-xs text-orange-400">
                  {(fiveA.lurkersAvgMultiplier || 0.23).toFixed(2)}x avg
                </div>
                <div className="text-xs text-gray-600">View only, minimal</div>
              </div>
            </div>
            
            {/* Casual */}
            <div className="bg-gradient-to-br from-blue-900/40 to-blue-800/30 rounded-lg p-4 border border-blue-700/30">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📱</span>
                <div className="text-sm font-medium text-blue-300">Casual</div>
              </div>
              <div className="text-2xl font-bold text-blue-400">
                {formatNumber(fiveA.casualCount || 0)}
              </div>
              <div className="text-xs text-blue-500/70">
                {fiveA.totalUsers > 0 
                  ? ((fiveA.casualCount || 0) / fiveA.totalUsers * 100).toFixed(0)
                  : 25}% of users
              </div>
              <div className="mt-2 pt-2 border-t border-blue-700/30">
                <div className="text-xs text-yellow-400">
                  {(fiveA.casualAvgMultiplier || 0.95).toFixed(2)}x avg
                </div>
                <div className="text-xs text-blue-600/70">Weekly activity</div>
              </div>
            </div>
            
            {/* Active */}
            <div className="bg-gradient-to-br from-green-900/40 to-green-800/30 rounded-lg p-4 border border-green-700/30">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🔥</span>
                <div className="text-sm font-medium text-green-300">Active</div>
              </div>
              <div className="text-2xl font-bold text-green-400">
                {formatNumber(fiveA.activeCount || 0)}
              </div>
              <div className="text-xs text-green-500/70">
                {fiveA.totalUsers > 0 
                  ? ((fiveA.activeCount || 0) / fiveA.totalUsers * 100).toFixed(0)
                  : 12}% of users
              </div>
              <div className="mt-2 pt-2 border-t border-green-700/30">
                <div className="text-xs text-green-400">
                  {(fiveA.activeAvgMultiplier || 1.40).toFixed(2)}x avg
                </div>
                <div className="text-xs text-green-600/70">Daily activity</div>
              </div>
            </div>
            
            {/* Power Users */}
            <div className="bg-gradient-to-br from-purple-900/40 to-purple-800/30 rounded-lg p-4 border border-purple-700/30">
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">⚡</span>
                <div className="text-sm font-medium text-purple-300">Power Users</div>
              </div>
              <div className="text-2xl font-bold text-purple-400">
                {formatNumber(fiveA.powerUsersCount || 0)}
              </div>
              <div className="text-xs text-purple-500/70">
                {fiveA.totalUsers > 0 
                  ? ((fiveA.powerUsersCount || 0) / fiveA.totalUsers * 100).toFixed(0)
                  : 3}% of users
              </div>
              <div className="mt-2 pt-2 border-t border-purple-700/30">
                <div className="text-xs text-cyan-400">
                  {(fiveA.powerUsersAvgMultiplier || 1.74).toFixed(2)}x avg
                </div>
                <div className="text-xs text-purple-600/70">Top creators</div>
              </div>
            </div>
          </div>
        </div>
      )}
      
      {/* ZERO Earners Highlight */}
      {(fiveA.zeroEarnersCount || 0) > 0 && (
        <div className="mb-6 p-4 bg-gradient-to-r from-red-950/50 to-red-900/30 rounded-lg border border-red-800/50">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">🚫</span>
              <div>
                <div className="text-lg font-bold text-red-400">
                  {formatNumber(fiveA.zeroEarnersCount || 0)} Users Earning ZERO VCoin
                </div>
                <div className="text-sm text-red-500/70">
                  {(fiveA.zeroEarnersPercent || 0).toFixed(1)}% of users have multiplier {'<'} 0.1x (effectively 0 earnings)
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-red-500">
                0 VCoin
              </div>
              <div className="text-xs text-red-600/70">per month earned</div>
            </div>
          </div>
          <div className="mt-3 text-xs text-gray-500">
            These are primarily inactive/ghost accounts that signed up but never engaged with the platform.
          </div>
        </div>
      )}
      
      {/* Fairness & Health */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className={`text-2xl font-bold ${
            fiveA.fairnessScore >= 70 ? 'text-green-400' : 
            fiveA.fairnessScore >= 50 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {fiveA.fairnessScore.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">Fairness Score</div>
          <div className="text-xs text-gray-600 mt-1">
            Gini: {fiveA.giniCoefficient.toFixed(3)}
          </div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className={`text-2xl font-bold ${
            fiveA.engagementIncentiveScore >= 70 ? 'text-green-400' : 
            fiveA.engagementIncentiveScore >= 40 ? 'text-yellow-400' : 'text-red-400'
          }`}>
            {fiveA.engagementIncentiveScore.toFixed(0)}
          </div>
          <div className="text-xs text-gray-500">Engagement Score</div>
        </div>
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-white">
            <span className="text-green-400">{formatNumber(fiveA.usersWithBoost)}</span>
            <span className="text-gray-500 mx-1">/</span>
            <span className="text-red-400">{formatNumber(fiveA.usersWithPenalty)}</span>
          </div>
          <div className="text-xs text-gray-500">Boosted / Penalized</div>
        </div>
        <div className="bg-gradient-to-br from-red-900/50 to-red-800/30 rounded-lg p-4 text-center border border-red-700/30">
          <div className="text-2xl font-bold text-red-400">
            {(fiveA.zeroEarnersPercent || 0).toFixed(1)}%
          </div>
          <div className="text-xs text-red-500">Zero Earners</div>
          <div className="text-xs text-red-600/70 mt-1">
            {formatNumber(fiveA.zeroEarnersCount || 0)} users
          </div>
        </div>
      </div>
      
      {/* Dynamic 5A Evolution (60-Month Projection) */}
      <div className="mt-6 p-4 bg-gradient-to-r from-indigo-950/50 to-purple-950/50 rounded-lg border border-indigo-700/30">
        <h3 className="text-sm font-medium text-indigo-300 mb-4 flex items-center gap-2">
          <span>📈</span> Dynamic 5A Evolution (60-Month Projection)
        </h3>
        <p className="text-xs text-gray-400 mb-4">
          Users evolve between segments monthly based on engagement. Platform maturity increases improvement rates over time.
        </p>
        
        {/* Evolution Summary */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          {/* Month 1 vs Month 60 Multiplier */}
          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Avg Multiplier Evolution</div>
            <div className="flex items-center justify-center gap-2">
              <span className="text-lg font-bold text-orange-400">
                {(fiveA.month1AvgMultiplier || 0.6).toFixed(2)}x
              </span>
              <span className="text-gray-500">→</span>
              <span className="text-lg font-bold text-green-400">
                {(fiveA.month60AvgMultiplier || 0.95).toFixed(2)}x
              </span>
            </div>
            <div className="text-xs text-gray-600 mt-1">Month 1 → Month 60</div>
          </div>
          
          {/* Active Users Evolution */}
          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">Active Users %</div>
            <div className="flex items-center justify-center gap-2">
              <span className="text-lg font-bold text-orange-400">
                {(fiveA.month1ActivePercent || 15).toFixed(0)}%
              </span>
              <span className="text-gray-500">→</span>
              <span className="text-lg font-bold text-green-400">
                {(fiveA.month60ActivePercent || 35).toFixed(0)}%
              </span>
            </div>
            <div className="text-xs text-gray-600 mt-1">Active + Power</div>
          </div>
          
          {/* Cumulative Impacts */}
          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">5Y Growth Impact</div>
            <div className="text-xl font-bold text-blue-400">
              +{((fiveA.cumulativeGrowthBoost || 0) * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-600 mt-1">Cumulative boost</div>
          </div>
          
          <div className="bg-gray-800/50 rounded-lg p-3 text-center">
            <div className="text-xs text-gray-500 mb-1">5Y Price Impact</div>
            <div className="text-xl font-bold text-yellow-400">
              +{(fiveA.cumulativePriceImpact || 0).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-600 mt-1">Token price boost</div>
          </div>
        </div>
        
        {/* Evolution Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-green-900/30 rounded-lg p-3 text-center border border-green-700/30">
            <div className="text-2xl font-bold text-green-400">
              {formatNumber(fiveA.totalImprovedUsers || 0)}
            </div>
            <div className="text-xs text-green-500">Users Improved</div>
            <div className="text-xs text-gray-600 mt-1">
              {(fiveA.avgImprovementRate || 0).toFixed(1)}% monthly rate
            </div>
          </div>
          
          <div className="bg-orange-900/30 rounded-lg p-3 text-center border border-orange-700/30">
            <div className="text-2xl font-bold text-orange-400">
              {formatNumber(fiveA.totalDecayedUsers || 0)}
            </div>
            <div className="text-xs text-orange-500">Users Decayed</div>
            <div className="text-xs text-gray-600 mt-1">
              {(fiveA.avgDecayRate || 0).toFixed(1)}% monthly rate
            </div>
          </div>
          
          <div className="bg-red-900/30 rounded-lg p-3 text-center border border-red-700/30">
            <div className="text-2xl font-bold text-red-400">
              {formatNumber(fiveA.totalChurnedUsers || 0)}
            </div>
            <div className="text-xs text-red-500">Users Churned</div>
            <div className="text-xs text-gray-600 mt-1">Due to low 5A scores</div>
          </div>
        </div>
        
        {/* Transition Matrix Info */}
        <div className="mt-4 p-3 bg-gray-800/30 rounded-lg">
          <div className="text-xs text-gray-400 mb-2 font-medium">Monthly Transition Probabilities:</div>
          <div className="grid grid-cols-5 gap-2 text-xs">
            <div className="text-center">
              <div className="text-red-400 font-medium">Inactive</div>
              <div className="text-gray-500">25% churn</div>
              <div className="text-gray-500">5% → lurker</div>
            </div>
            <div className="text-center">
              <div className="text-gray-400 font-medium">Lurker</div>
              <div className="text-gray-500">5% churn</div>
              <div className="text-green-500">8% → casual</div>
            </div>
            <div className="text-center">
              <div className="text-blue-400 font-medium">Casual</div>
              <div className="text-gray-500">3% churn</div>
              <div className="text-green-500">12% → active</div>
            </div>
            <div className="text-center">
              <div className="text-green-400 font-medium">Active</div>
              <div className="text-gray-500">2% churn</div>
              <div className="text-green-500">5% → power</div>
            </div>
            <div className="text-center">
              <div className="text-purple-400 font-medium">Power</div>
              <div className="text-gray-500">2% churn</div>
              <div className="text-green-500">93% retain</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

