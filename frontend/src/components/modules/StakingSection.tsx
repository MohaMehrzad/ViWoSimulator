'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface StakingSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function StakingSection({ result, parameters }: StakingSectionProps) {
  // Get staking data from result (new backend module) or calculate fallback
  const staking = result.staking;
  const fiveA = result.fiveA;
  
  // 5A Impact
  const fiveAEnabled = fiveA?.enabled || false;
  const fiveAApyBoost = fiveA?.stakingApyBoostAvg || 0;
  
  // Fallback values if staking module not available
  const stakingApy = staking?.stakingApy || (parameters.stakingApy || 0.07) * 100;
  const stakerFeeDiscount = staking?.stakerFeeDiscount || (parameters.stakerFeeDiscount || 0.30) * 100;
  const minStakeAmount = staking?.minStakeAmount || parameters.minStakeAmount || 100;
  const lockDays = staking?.lockDays || parameters.stakeLockDays || 30;
  
  // Solana-specific data
  const network = staking?.network || 'solana';
  const programType = staking?.programType || 'spl_token_staking';
  const rewardFrequency = staking?.rewardFrequency || 'per_block';
  const autoCompoundEnabled = staking?.autoCompoundEnabled !== false;
  const dailyCompoundApy = staking?.dailyCompoundApy || stakingApy * 1.05;
  const instantUnstakeAvailable = staking?.instantUnstakeAvailable !== false;
  const instantUnstakePenalty = staking?.instantUnstakePenalty || 2;
  const cooldownDays = staking?.cooldownDays || 2;
  const solanaSavings = staking?.solanaSavings || 0;
  
  // Participation metrics
  const stakersCount = staking?.stakersCount || 0;
  const participationRate = staking?.participationRate || 0;
  const avgStakeAmount = staking?.avgStakeAmount || 0;
  
  // Totals
  const totalStaked = staking?.totalStaked || 0;
  const totalStakedUsd = staking?.totalStakedUsd || 0;
  const stakingRatio = staking?.stakingRatio || 0;
  
  // Rewards
  const totalMonthlyRewards = staking?.totalMonthlyRewards || 0;
  const totalMonthlyRewardsUsd = staking?.totalMonthlyRewardsUsd || 0;
  const rewardsPerStaker = staking?.rewardsPerStaker || 0;
  const rewardsPerStakerUsd = staking?.rewardsPerStakerUsd || 0;
  const effectiveMonthlyYield = staking?.effectiveMonthlyYield || 0;
  
  // Tier distribution
  const tierDistribution = staking?.tierDistribution || {
    bronze: 0,
    silver: 0,
    gold: 0,
    platinum: 0,
  };
  
  // Platform impact
  const totalFeeSavingsUsd = staking?.totalFeeSavingsUsd || 0;
  const lockedSupplyPercent = staking?.lockedSupplyPercent || 0;
  const reducedSellPressureUsd = staking?.reducedSellPressureUsd || 0;
  
  // Health
  const stakingStatus = staking?.stakingStatus || 'Unknown';
  const isHealthy = staking?.isHealthy || false;
  
  // Annual projections
  const annualRewardsTotal = staking?.annualRewardsTotal || 0;
  const annualRewardsUsd = staking?.annualRewardsUsd || 0;
  
  // Platform Revenue from Staking (NEW)
  const stakingRevenue = staking?.revenue || 0;
  const stakingCosts = staking?.costs || 0;
  const stakingProfit = staking?.profit || 0;
  const stakingMargin = staking?.margin || 0;
  const protocolFeeFromRewardsUsd = staking?.protocolFeeFromRewardsUsd || 0;
  const unstakePenaltyUsd = staking?.unstakePenaltyUsd || 0;
  const txFeeRevenueUsd = staking?.txFeeRevenueUsd || 0;
  
  // NEW-HIGH-003 & NEW-MED-005 FIX: Funding source and early unstake tracking
  const rewardFundingSource = staking?.rewardFundingSource || 'emission_allocation';
  const rewardFundingDetails = staking?.rewardFundingDetails;
  const rewardsExceedModuleIncome = staking?.rewardsExceedModuleIncome || false;
  const sustainabilityWarning = staking?.sustainabilityWarning;
  
  // Early unstake metrics
  const earlyUnstakeRate = staking?.earlyUnstakeRate || 0;
  const earlyUnstakersCount = staking?.earlyUnstakersCount || 0;
  const expectedEarlyUnstakeRewardLoss = staking?.expectedEarlyUnstakeRewardLoss || 0;
  
  // Dynamic Staking Cap (December 2025 Budget Constraint)
  const stakingCap = staking?.stakingCap || 0;
  const stakingAtCapacity = staking?.stakingAtCapacity || false;
  const stakingCapacityPercent = staking?.stakingCapacityPercent || 0;

  // Status colors
  const statusColors = {
    'Healthy': { bg: 'from-emerald-500 to-teal-600', text: 'text-emerald-400' },
    'Moderate': { bg: 'from-amber-500 to-orange-600', text: 'text-amber-400' },
    'Low': { bg: 'from-red-500 to-rose-600', text: 'text-red-400' },
    'Unknown': { bg: 'from-gray-500 to-gray-600', text: 'text-gray-400' },
  };
  
  const currentStatus = statusColors[stakingStatus as keyof typeof statusColors] || statusColors.Unknown;

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className={`bg-gradient-to-r ${currentStatus.bg} rounded-2xl p-6 text-white`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🔒</span>
            <div>
              <h2 className="text-2xl font-bold">Staking Module</h2>
              <p className="text-white/80">Solana SPL Token Staking • {rewardFrequency === 'per_block' ? 'Per-Block Rewards' : 'Per-Epoch Rewards'}</p>
            </div>
            {/* Solana Badge */}
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-3 py-1">
              <div className="flex items-center gap-2">
                <span className="text-lg">◎</span>
                <span className="font-semibold text-sm">Solana</span>
              </div>
            </div>
            {/* 5A Badge */}
            {fiveAEnabled && fiveAApyBoost > 0 && (
              <div className="bg-yellow-400/20 backdrop-blur-sm rounded-lg px-3 py-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg">⭐</span>
                  <span className="font-semibold text-sm">+{fiveAApyBoost.toFixed(1)}% APY Boost</span>
                </div>
              </div>
            )}
            {/* Staking Capacity Badge */}
            {stakingCap > 0 && (
              <div className={`backdrop-blur-sm rounded-lg px-3 py-1 ${stakingAtCapacity ? 'bg-red-500/30' : 'bg-white/20'}`}>
                <div className="flex items-center gap-2">
                  <span className="text-lg">{stakingAtCapacity ? '⚠️' : '📊'}</span>
                  <span className="font-semibold text-sm">
                    {stakingAtCapacity ? 'At Capacity' : `${stakingCapacityPercent.toFixed(0)}% Capacity`}
                  </span>
                </div>
              </div>
            )}
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold">{stakingApy.toFixed(1)}%</div>
            <div className="text-lg font-semibold">APY</div>
            {autoCompoundEnabled && (
              <div className="text-xs text-white/70">Auto-compound: {dailyCompoundApy.toFixed(1)}%</div>
            )}
          </div>
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatNumber(totalStaked)}</div>
            <div className="text-xs text-white/80 uppercase font-semibold">VCoin Staked</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(totalStakedUsd)}</div>
            <div className="text-xs text-white/80 uppercase font-semibold">Value Locked</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{stakersCount.toLocaleString()}</div>
            <div className="text-xs text-white/80 uppercase font-semibold">Stakers</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{participationRate.toFixed(1)}%</div>
            <div className="text-xs text-white/80 uppercase font-semibold">Participation</div>
          </div>
        </div>
      </div>

      {/* Sustainability Warning - NEW-HIGH-003 FIX */}
      {sustainabilityWarning && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-start gap-3">
          <span className="text-2xl">🚨</span>
          <div>
            <div className="font-semibold text-red-800">Sustainability Warning</div>
            <div className="text-sm text-red-700">{sustainabilityWarning}</div>
          </div>
        </div>
      )}
      
      {/* Reward Funding Source Info - NEW-HIGH-003 FIX */}
      <div className="bg-blue-50 border border-blue-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <span className="text-2xl">ℹ️</span>
          <div>
            <div className="font-semibold text-blue-800 flex items-center gap-2">
              Reward Funding: {rewardFundingSource === 'emission_allocation' ? 'Emission Allocation' : rewardFundingSource}
              {rewardsExceedModuleIncome && (
                <span className="bg-amber-100 text-amber-700 text-xs px-2 py-0.5 rounded">Subsidized</span>
              )}
            </div>
            <div className="text-sm text-blue-700 mt-1">
              {rewardFundingDetails || 
                'Staking rewards are funded from the 35% Ecosystem & Rewards allocation (350M VCoin over 60 months). Protocol fee (5%) on rewards provides partial offset.'}
            </div>
          </div>
        </div>
      </div>
      
      {/* Platform Revenue from Staking */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💵 Platform Revenue from Staking</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
          <div className="bg-emerald-50 rounded-lg p-4 text-center border border-emerald-200">
            <div className="text-2xl font-bold text-emerald-600">{formatCurrency(stakingRevenue)}</div>
            <div className="text-xs text-emerald-500 uppercase font-semibold">Revenue</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 text-center border border-red-200">
            <div className="text-2xl font-bold text-red-600">{formatCurrency(stakingCosts)}</div>
            <div className="text-xs text-red-500 uppercase font-semibold">Costs</div>
          </div>
          <div className={`rounded-lg p-4 text-center border ${stakingProfit >= 0 ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'}`}>
            <div className={`text-2xl font-bold ${stakingProfit >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {formatCurrency(stakingProfit)}
            </div>
            <div className={`text-xs uppercase font-semibold ${stakingProfit >= 0 ? 'text-green-500' : 'text-red-500'}`}>Profit</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 text-center border border-blue-200">
            <div className="text-2xl font-bold text-blue-600">{stakingMargin.toFixed(1)}%</div>
            <div className="text-xs text-blue-500 uppercase font-semibold">Margin</div>
          </div>
        </div>
        
        {/* Revenue Breakdown */}
        <div className="bg-gray-50 rounded-lg p-4">
          <h4 className="font-semibold text-gray-700 mb-3">Revenue Sources</h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                <span className="text-sm text-gray-600">Protocol Fee (5% of rewards)</span>
              </div>
              <span className="font-semibold text-emerald-600">{formatCurrency(protocolFeeFromRewardsUsd)}</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-amber-500"></span>
                <span className="text-sm text-gray-600">Early Unstake Penalties (2%)</span>
              </div>
              <span className="font-semibold text-amber-600">{formatCurrency(unstakePenaltyUsd)}</span>
            </div>
            <div className="flex justify-between items-center">
              <div className="flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                <span className="text-sm text-gray-600">Transaction Fees</span>
              </div>
              <span className="font-semibold text-blue-600">{formatCurrency(txFeeRevenueUsd)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Solana Staking Features */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-6">
        <h3 className="font-bold text-lg mb-4 text-purple-800">◎ Solana Staking Features</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-700">~400ms</div>
            <div className="text-xs text-purple-500">Reward Updates</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-700">$0.00025</div>
            <div className="text-xs text-purple-500">Per Transaction</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-700">{cooldownDays} Days</div>
            <div className="text-xs text-purple-500">Unstake Cooldown</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-emerald-700">
              {instantUnstakeAvailable ? 'Yes' : 'No'}
            </div>
            <div className="text-xs text-purple-500">Instant Unstake ({instantUnstakePenalty}% fee)</div>
          </div>
        </div>
        <div className="mt-4 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white/50 rounded-lg p-3">
            <div className="text-sm font-semibold text-purple-700">Program Type</div>
            <div className="text-xs text-purple-600">{programType} (Anchor Framework)</div>
          </div>
          <div className="bg-white/50 rounded-lg p-3">
            <div className="text-sm font-semibold text-purple-700">Reward Distribution</div>
            <div className="text-xs text-purple-600">{rewardFrequency === 'per_block' ? 'Every block (~400ms)' : 'Per epoch (~2 days)'}</div>
          </div>
        </div>
      </div>

      {/* Staking Configuration */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">⚙️ Staking Configuration</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="text-sm text-blue-600 mb-1">Base APY</div>
            <div className="text-2xl font-bold text-blue-700">{stakingApy.toFixed(1)}%</div>
            <div className="text-xs text-blue-500">Annual yield</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="text-sm text-purple-600 mb-1">Fee Discount</div>
            <div className="text-2xl font-bold text-purple-700">{stakerFeeDiscount.toFixed(0)}%</div>
            <div className="text-xs text-purple-500">For stakers</div>
          </div>
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Min Stake</div>
            <div className="text-2xl font-bold text-emerald-700">{formatNumber(minStakeAmount)}</div>
            <div className="text-xs text-emerald-500">VCoin minimum</div>
          </div>
          <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
            <div className="text-sm text-amber-600 mb-1">Lock Period</div>
            <div className="text-2xl font-bold text-amber-700">{lockDays}</div>
            <div className="text-xs text-amber-500">Days minimum</div>
          </div>
        </div>
        
        {/* Auto-compound info */}
        {autoCompoundEnabled && (
          <div className="mt-4 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
            <div className="flex items-center gap-2">
              <span className="text-emerald-500">✨</span>
              <div className="text-sm text-emerald-700">
                <strong>Auto-Compound Enabled:</strong> Rewards automatically compound for {dailyCompoundApy.toFixed(1)}% effective APY (+{(dailyCompoundApy - stakingApy).toFixed(2)}% boost)
              </div>
            </div>
          </div>
        )}
        
        {/* Budget Constraint - Dynamic Staking Cap */}
        {stakingCap > 0 && (
          <div className={`mt-4 p-4 rounded-lg border ${stakingAtCapacity ? 'bg-red-50 border-red-200' : 'bg-slate-50 border-slate-200'}`}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2">
                <span className="text-lg">{stakingAtCapacity ? '⚠️' : '📊'}</span>
                <span className={`font-semibold ${stakingAtCapacity ? 'text-red-700' : 'text-slate-700'}`}>
                  Budget-Constrained Staking Cap
                </span>
              </div>
              <span className={`text-sm font-medium ${stakingAtCapacity ? 'text-red-600' : 'text-slate-600'}`}>
                {stakingCapacityPercent.toFixed(1)}% utilized
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2 mb-2">
              <div 
                className={`h-2 rounded-full transition-all ${stakingAtCapacity ? 'bg-red-500' : stakingCapacityPercent > 80 ? 'bg-amber-500' : 'bg-emerald-500'}`}
                style={{ width: `${Math.min(stakingCapacityPercent, 100)}%` }}
              />
            </div>
            <div className="flex justify-between text-xs text-slate-500">
              <span>Staked: {formatNumber(totalStaked)} VCoin</span>
              <span>Cap: {formatNumber(stakingCap)} VCoin</span>
            </div>
            {stakingAtCapacity && (
              <div className="mt-2 text-xs text-red-600">
                <strong>At Capacity:</strong> New staking is limited. Existing stakers continue earning {stakingApy.toFixed(1)}% APY.
              </div>
            )}
          </div>
        )}
      </div>

      {/* Early Unstake Metrics - NEW-MED-005 FIX */}
      {(earlyUnstakeRate > 0 || earlyUnstakersCount > 0) && (
        <div className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-bold text-lg mb-4">⏰ Early Unstake Tracking</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-amber-50 rounded-lg p-4 border border-amber-200 text-center">
              <div className="text-2xl font-bold text-amber-700">{earlyUnstakeRate.toFixed(1)}%</div>
              <div className="text-xs text-amber-500 uppercase font-semibold">Early Unstake Rate</div>
            </div>
            <div className="bg-amber-50 rounded-lg p-4 border border-amber-200 text-center">
              <div className="text-2xl font-bold text-amber-700">{earlyUnstakersCount.toLocaleString()}</div>
              <div className="text-xs text-amber-500 uppercase font-semibold">Early Unstakers</div>
            </div>
            <div className="bg-amber-50 rounded-lg p-4 border border-amber-200 text-center">
              <div className="text-2xl font-bold text-amber-700">{formatNumber(expectedEarlyUnstakeRewardLoss)}</div>
              <div className="text-xs text-amber-500 uppercase font-semibold">Lost Rewards (VCoin)</div>
            </div>
          </div>
          <div className="mt-3 text-sm text-gray-600 bg-gray-50 rounded-lg p-3">
            <strong>Note:</strong> Early unstakers forfeit their pending rewards and pay a {instantUnstakePenalty}% penalty. 
            This forfeited value stays in the reward pool, benefiting long-term stakers.
          </div>
        </div>
      )}
      
      {/* Staking Tiers */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🏆 Staking Tiers</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <TierCard 
            name="Bronze"
            minStake={100}
            feeDiscount={10}
            bonus={0}
            count={tierDistribution.bronze}
            color="amber"
          />
          <TierCard 
            name="Silver"
            minStake={1000}
            feeDiscount={20}
            bonus={1}
            count={tierDistribution.silver}
            color="gray"
          />
          <TierCard 
            name="Gold"
            minStake={10000}
            feeDiscount={30}
            bonus={2}
            count={tierDistribution.gold}
            color="yellow"
          />
          <TierCard 
            name="Platinum"
            minStake={100000}
            feeDiscount={50}
            bonus={3}
            count={tierDistribution.platinum}
            color="purple"
          />
        </div>
        <div className="mt-4 p-3 bg-gray-50 rounded-lg text-sm text-gray-600">
          <strong>Tier Benefits:</strong> Higher tiers unlock better fee discounts, APY bonuses, and increased governance voting power.
        </div>
      </div>

      {/* Rewards Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💰 Rewards Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold mb-3">Monthly Rewards</h4>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Total Pool Rewards</span>
                <span className="font-semibold">{formatNumber(totalMonthlyRewards)} VCoin</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">USD Value</span>
                <span className="font-semibold">{formatCurrency(totalMonthlyRewardsUsd)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Per Staker (Avg)</span>
                <span className="font-semibold">{formatNumber(rewardsPerStaker)} VCoin</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-600">Per Staker USD</span>
                <span className="font-semibold text-emerald-600">{formatCurrency(rewardsPerStakerUsd)}</span>
              </div>
            </div>
          </div>
          
          <div>
            <h4 className="font-semibold mb-3">Annual Projections</h4>
            <div className="space-y-3">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Annual Rewards</span>
                <span className="font-semibold">{formatNumber(annualRewardsTotal)} VCoin</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Annual USD Value</span>
                <span className="font-semibold">{formatCurrency(annualRewardsUsd)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Effective Monthly Yield</span>
                <span className="font-semibold">{effectiveMonthlyYield.toFixed(2)}%</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-600">Average Stake</span>
                <span className="font-semibold">{formatNumber(avgStakeAmount)} VCoin</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Platform Impact */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📈 Platform Impact</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{lockedSupplyPercent.toFixed(2)}%</div>
            <div className="text-sm text-gray-600 mt-1">Supply Locked</div>
            <div className="text-xs text-gray-400">Reduces circulating supply</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-emerald-600">{formatCurrency(reducedSellPressureUsd)}</div>
            <div className="text-sm text-gray-600 mt-1">Reduced Sell Pressure</div>
            <div className="text-xs text-gray-400">Monthly sell reduction</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{formatCurrency(totalFeeSavingsUsd)}</div>
            <div className="text-sm text-gray-600 mt-1">Total Fee Savings</div>
            <div className="text-xs text-gray-400">Staker discounts/month</div>
          </div>
        </div>
        
        {/* Staking Ratio Bar */}
        <div className="mt-6">
          <div className="flex justify-between mb-1">
            <span className="text-sm text-gray-600">Staking Ratio</span>
            <span className="text-sm font-semibold">{stakingRatio.toFixed(2)}% of circulating supply</span>
          </div>
          <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
            <div 
              className={`h-full ${stakingRatio >= 10 ? 'bg-emerald-500' : stakingRatio >= 5 ? 'bg-amber-500' : 'bg-red-500'}`}
              style={{ width: `${Math.min(stakingRatio * 5, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>0%</span>
            <span className="text-emerald-600">Target: 10%+</span>
            <span>20%</span>
          </div>
        </div>
      </div>

      {/* Health Status */}
      <div className={`rounded-xl p-6 ${isHealthy ? 'bg-emerald-50 border border-emerald-200' : 'bg-amber-50 border border-amber-200'}`}>
        <div className="flex items-start gap-3">
          <span className="text-2xl">{isHealthy ? '✅' : '⚠️'}</span>
          <div>
            <h3 className={`font-bold ${isHealthy ? 'text-emerald-800' : 'text-amber-800'} mb-2`}>
              Staking Health: {stakingStatus}
            </h3>
            <p className={`text-sm ${isHealthy ? 'text-emerald-700' : 'text-amber-700'}`}>
              {isHealthy 
                ? `Healthy staking participation at ${participationRate.toFixed(1)}%. The staking program is effectively reducing sell pressure and rewarding loyal token holders.`
                : `Staking participation is at ${participationRate.toFixed(1)}%. Consider increasing APY or promoting staking benefits to improve participation.`
              }
            </p>
            {!isHealthy && (
              <ul className={`mt-3 space-y-1 text-sm ${isHealthy ? 'text-emerald-700' : 'text-amber-700'}`}>
                <li>• Target: 10%+ participation rate</li>
                <li>• Consider APY boost campaigns</li>
                <li>• Promote fee discount benefits</li>
              </ul>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}

// Helper Component
function TierCard({
  name,
  minStake,
  feeDiscount,
  bonus,
  count,
  color,
}: {
  name: string;
  minStake: number;
  feeDiscount: number;
  bonus: number;
  count: number;
  color: string;
}) {
  const colorClasses = {
    amber: 'bg-amber-100 border-amber-300 text-amber-800',
    gray: 'bg-gray-100 border-gray-300 text-gray-800',
    yellow: 'bg-yellow-100 border-yellow-400 text-yellow-800',
    purple: 'bg-purple-100 border-purple-300 text-purple-800',
  };

  return (
    <div className={`rounded-lg p-4 border-2 ${colorClasses[color as keyof typeof colorClasses]}`}>
      <div className="font-bold text-lg mb-2">{name}</div>
      <div className="space-y-1 text-sm">
        <div className="flex justify-between">
          <span>Min Stake:</span>
          <span className="font-semibold">{formatNumber(minStake)}</span>
        </div>
        <div className="flex justify-between">
          <span>Fee Discount:</span>
          <span className="font-semibold">{feeDiscount}%</span>
        </div>
        <div className="flex justify-between">
          <span>APY Bonus:</span>
          <span className="font-semibold">+{bonus}%</span>
        </div>
      </div>
      <div className="mt-3 pt-2 border-t border-current/20 text-center">
        <span className="font-bold text-lg">{count.toLocaleString()}</span>
        <span className="text-xs ml-1">stakers</span>
      </div>
    </div>
  );
}

