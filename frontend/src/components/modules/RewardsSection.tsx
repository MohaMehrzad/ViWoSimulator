'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface RewardsSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function RewardsSection({ result, parameters }: RewardsSectionProps) {
  const { rewards, fiveA } = result;
  
  // 5A Impact indicator
  const fiveAEnabled = fiveA?.enabled || false;
  const fiveAMultiplier = fiveA?.avgCompoundMultiplier || 1.0;
  const fiveARedistribution = fiveA?.rewardRedistributionPercent || 0;

  const rewardCategories = [
    {
      category: 'Content Creation',
      items: [
        { name: 'Text Post', points: parameters.textPostPoints, icon: '📝' },
        { name: 'Image Post', points: parameters.imagePostPoints, icon: '🖼️' },
        { name: 'Audio Post', points: parameters.audioPostPoints, icon: '🎵' },
        { name: 'Short Video', points: parameters.shortVideoPoints, icon: '📱' },
        { name: 'Video Post', points: parameters.postVideosPoints, icon: '🎬' },
        { name: 'Music', points: parameters.musicPoints, icon: '🎶' },
        { name: 'Podcast', points: parameters.podcastPoints, icon: '🎙️' },
        { name: 'Audiobook', points: parameters.audioBookPoints, icon: '📚' },
      ]
    },
    {
      category: 'Engagement',
      items: [
        { name: 'Like', points: parameters.likePoints, icon: '❤️' },
        { name: 'Comment', points: parameters.commentPoints, icon: '💬' },
        { name: 'Share', points: parameters.sharePoints, icon: '🔄' },
        { name: 'Follow', points: parameters.followPoints, icon: '👥' },
      ]
    }
  ];

  const multipliers = [
    { name: 'High Quality Content', value: parameters.highQualityMultiplier, color: 'bg-emerald-100 text-emerald-700' },
    { name: 'Verified User', value: parameters.verifiedMultiplier, color: 'bg-blue-100 text-blue-700' },
    { name: 'Premium Member', value: parameters.premiumMultiplier, color: 'bg-purple-100 text-purple-700' },
  ];

  // Daily emission calculations
  const dailyGrossEmission = rewards.grossMonthlyEmission / 30;
  const dailyPlatformFee = rewards.platformFeeVcoin / 30;
  const dailyNetEmission = rewards.monthlyEmission / 30;
  const dailyPlatformFeeUsd = rewards.platformFeeUsd / 30;

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-amber-500 to-orange-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">🎁</span>
          <div className="flex-1">
            <h2 className="text-2xl font-bold">Rewards Module</h2>
            <p className="text-amber-200">Token emission and reward distribution</p>
          </div>
          {fiveAEnabled && (
            <div className="text-right bg-yellow-400/20 px-3 py-2 rounded-lg">
              <div className="text-lg font-bold text-yellow-200">⭐ 5A Active</div>
              <div className="text-xs text-yellow-300">
                {fiveARedistribution.toFixed(1)}% redistributed | Avg {fiveAMultiplier.toFixed(2)}x
              </div>
            </div>
          )}
          <div className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 flex items-center gap-2">
            <span className="text-lg">💰</span>
            <span className="text-sm font-semibold">5% Platform Fee</span>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatNumber(rewards.grossMonthlyEmission)}</div>
            <div className="text-xs text-amber-200 uppercase font-semibold">Gross Emission</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatNumber(rewards.monthlyEmission)}</div>
            <div className="text-xs text-amber-200 uppercase font-semibold">Net to Users (95%)</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatNumber(rewards.dailyEmission)}</div>
            <div className="text-xs text-amber-200 uppercase font-semibold">Daily Emission</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{rewards.allocationPercent.toFixed(1)}%</div>
            <div className="text-xs text-amber-200 uppercase font-semibold">Allocation Rate</div>
          </div>
        </div>
      </div>

      {/* PRIMARY REVENUE - 5% Platform Fee */}
      <div className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">💵</span>
          <div className="flex-1">
            <h3 className="text-xl font-bold">5% Platform Fee - PRIMARY REVENUE</h3>
            <p className="text-emerald-200">Calculated DAILY, taken BEFORE user distribution</p>
          </div>
        </div>
        
        {/* Daily Fee Flow */}
        <div className="bg-white/10 backdrop-blur-sm rounded-xl p-6 mb-4">
          <h4 className="text-sm font-semibold text-emerald-200 mb-4 text-center">
            📅 DAILY FEE CALCULATION (Before Every Distribution)
          </h4>
          <div className="flex flex-col md:flex-row items-center justify-center gap-4">
            <div className="text-center">
              <div className="text-sm text-emerald-200">Daily Gross</div>
              <div className="text-xl font-bold">{formatNumber(dailyGrossEmission)}</div>
              <div className="text-xs text-emerald-300">VCoin/day</div>
            </div>
            
            <div className="text-2xl">→</div>
            
            <div className="text-center bg-white/20 rounded-lg p-3 border-2 border-white/30">
              <div className="text-sm font-semibold text-yellow-200">5% FIRST</div>
              <div className="text-xl font-bold text-yellow-100">{formatNumber(dailyPlatformFee)}</div>
              <div className="text-xs text-yellow-200">{formatCurrency(dailyPlatformFeeUsd)}/day</div>
            </div>
            
            <div className="text-2xl">→</div>
            
            <div className="text-center">
              <div className="text-sm text-emerald-200">Users (95%)</div>
              <div className="text-xl font-bold">{formatNumber(dailyNetEmission)}</div>
              <div className="text-xs text-emerald-300">VCoin/day</div>
            </div>
          </div>
        </div>
        
        {/* Revenue Summary */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
            <div className="text-sm text-emerald-200 mb-1">Daily Platform Fee</div>
            <div className="text-2xl font-bold">{formatCurrency(dailyPlatformFeeUsd)}</div>
            <div className="text-xs text-emerald-300">{formatNumber(dailyPlatformFee)} VCoin</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center border-2 border-white/30">
            <div className="text-sm text-emerald-200 mb-1">Monthly Platform Fee</div>
            <div className="text-3xl font-bold">{formatCurrency(rewards.platformFeeUsd)}</div>
            <div className="text-xs text-emerald-300">{formatNumber(rewards.platformFeeVcoin)} VCoin</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4 text-center">
            <div className="text-sm text-emerald-200 mb-1">Annual Platform Fee</div>
            <div className="text-2xl font-bold">{formatCurrency(rewards.platformFeeUsd * 12)}</div>
            <div className="text-xs text-emerald-300">Projected yearly</div>
          </div>
        </div>
        
        <div className="mt-4 bg-white/10 rounded-lg p-3">
          <p className="text-sm text-emerald-100 text-center">
            <strong>How it works:</strong> Every day, the smart contract calculates the daily emission, 
            takes 5% for the platform treasury <strong>FIRST</strong>, then distributes the remaining 95% 
            to creators and consumers based on the reward algorithm.
          </p>
        </div>
      </div>

      {/* Dynamic Allocation Status (NEW - Nov 2025) */}
      {rewards.isDynamicAllocation && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl border border-purple-200 p-6">
          <h3 className="font-bold text-lg mb-4 text-purple-900">🎯 Dynamic Reward Allocation</h3>
          <p className="text-sm text-purple-700 mb-4">
            Reward allocation automatically scales with user growth using a logarithmic formula.
            This ensures sustainable tokenomics while incentivizing early adoption.
          </p>
          
          {/* Dynamic Allocation Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-4">
            <div className="bg-white rounded-lg p-4 text-center border border-purple-200">
              <div className="text-2xl font-bold text-purple-600">
                {((rewards.dynamicAllocationPercent || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-purple-500 uppercase font-semibold">Current Allocation</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border border-indigo-200">
              <div className="text-2xl font-bold text-indigo-600">
                {((rewards.growthFactor || 0) * 100).toFixed(1)}%
              </div>
              <div className="text-xs text-indigo-500 uppercase font-semibold">Growth Factor</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border border-blue-200">
              <div className="text-2xl font-bold text-blue-600">
                {formatNumber(rewards.perUserMonthlyVcoin || 0)}
              </div>
              <div className="text-xs text-blue-500 uppercase font-semibold">VCoin/User/Month</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border border-emerald-200">
              <div className="text-2xl font-bold text-emerald-600">
                {formatCurrency(rewards.perUserMonthlyUsd || 0)}
              </div>
              <div className="text-xs text-emerald-500 uppercase font-semibold">USD/User/Month</div>
            </div>
            <div className="bg-white rounded-lg p-4 text-center border border-gray-200">
              <div className="text-2xl font-bold text-gray-700">
                {formatNumber(rewards.effectiveUsers || 0)}
              </div>
              <div className="text-xs text-gray-500 uppercase font-semibold">Active Users</div>
            </div>
          </div>
          
          {/* Growth Progress Bar */}
          <div className="bg-white rounded-lg p-4 border border-purple-200">
            <div className="flex justify-between text-xs text-gray-600 mb-2">
              <span>5% (Min)</span>
              <span>Current: {((rewards.dynamicAllocationPercent || 0) * 100).toFixed(1)}%</span>
              <span>90% (Max)</span>
            </div>
            <div className="h-4 bg-gray-200 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gradient-to-r from-purple-500 to-indigo-500 transition-all duration-500"
                style={{ width: `${((rewards.growthFactor || 0) * 100)}%` }}
              />
            </div>
            <div className="mt-2 text-xs text-gray-500 text-center">
              Growth Progress: {((rewards.growthFactor || 0) * 100).toFixed(1)}% toward maximum allocation
            </div>
          </div>
          
          {/* Cap Warning */}
          {rewards.allocationCapped && (
            <div className="mt-4 bg-amber-50 border border-amber-300 rounded-lg p-3 flex items-center gap-2">
              <span className="text-amber-500">⚠️</span>
              <span className="text-sm text-amber-700">
                Per-user reward cap applied to prevent inflation. Allocation reduced to maintain sustainable per-user rewards.
              </span>
            </div>
          )}
        </div>
      )}
      
      {/* Static Allocation Notice (when dynamic is disabled) */}
      {!rewards.isDynamicAllocation && (
        <div className="bg-gray-50 rounded-xl border border-gray-200 p-6">
          <h3 className="font-bold text-lg mb-2 text-gray-700">📊 Static Allocation Mode</h3>
          <p className="text-sm text-gray-600">
            Using fixed reward allocation of {rewards.allocationPercent}%. Enable Dynamic Allocation in controls 
            for automatic scaling based on user growth.
          </p>
        </div>
      )}

      {/* Fee Flow Visualization (Detailed) */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🔄 Complete Fee Flow</h3>
        
        <div className="bg-gradient-to-r from-amber-50 to-emerald-50 rounded-xl p-6 border border-amber-200">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            {/* Gross Emission */}
            <div className="text-center flex-1">
              <div className="bg-amber-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">📦</span>
              </div>
              <div className="text-sm text-gray-600 mb-1">Gross Emission</div>
              <div className="text-2xl font-bold text-amber-600">{formatNumber(rewards.grossMonthlyEmission)}</div>
              <div className="text-xs text-gray-500">{formatCurrency(rewards.grossEmissionUsd)}</div>
            </div>
            
            {/* Arrow */}
            <div className="text-2xl text-gray-400 rotate-90 md:rotate-0">→</div>
            
            {/* Platform Fee */}
            <div className="text-center flex-1 bg-emerald-100 rounded-lg p-4 border-2 border-emerald-400 shadow-md">
              <div className="bg-emerald-200 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">🏦</span>
              </div>
              <div className="text-sm text-emerald-700 font-semibold mb-1">5% Platform Fee</div>
              <div className="text-2xl font-bold text-emerald-700">{formatNumber(rewards.platformFeeVcoin)}</div>
              <div className="text-sm text-emerald-600 font-semibold">{formatCurrency(rewards.platformFeeUsd)}</div>
              <div className="text-xs text-emerald-500 mt-1">→ Platform Treasury</div>
            </div>
            
            {/* Arrow */}
            <div className="text-2xl text-gray-400 rotate-90 md:rotate-0">→</div>
            
            {/* Net to Users */}
            <div className="text-center flex-1">
              <div className="bg-blue-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-2">
                <span className="text-2xl">👥</span>
              </div>
              <div className="text-sm text-gray-600 mb-1">Net to Users (95%)</div>
              <div className="text-2xl font-bold text-blue-600">{formatNumber(rewards.monthlyEmission)}</div>
              <div className="text-xs text-gray-500">{formatCurrency(rewards.emissionUsd)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Daily Limits */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">⏰ Daily Limits</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-gray-900">{parameters.maxPostsPerDay}</div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Max Posts/Day</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-gray-900">{parameters.maxLikesPerDay}</div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Max Likes/Day</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-gray-900">{parameters.maxCommentsPerDay}</div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Max Comments/Day</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-3xl font-bold text-emerald-600">{formatCurrency(parameters.maxDailyRewardUSD)}</div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Max Daily Reward</div>
          </div>
        </div>
      </div>

      {/* Reward Points */}
      {rewardCategories.map((category) => (
        <div key={category.category} className="bg-white rounded-xl border border-gray-200 p-6">
          <h3 className="font-bold text-lg mb-4">🏆 {category.category} Rewards</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {category.items.map((item) => (
              <div key={item.name} className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
                <span className="text-2xl">{item.icon}</span>
                <div className="font-semibold text-sm mt-2">{item.name}</div>
                <div className="text-2xl font-bold text-amber-600 mt-1">
                  {item.points} <span className="text-xs text-gray-500">pts</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}

      {/* Multipliers */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">✨ Reward Multipliers</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {multipliers.map((mult) => (
            <div key={mult.name} className={`rounded-lg p-4 text-center ${mult.color}`}>
              <div className="font-semibold">{mult.name}</div>
              <div className="text-3xl font-bold mt-2">{mult.value}x</div>
            </div>
          ))}
        </div>
      </div>

      {/* Decay Rates */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📉 Engagement Decay</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <div className="text-sm text-red-600 mb-1">7-Day Decay</div>
            {/* Issue #33 Fix: Removed * 100 - day7Decay is already in percentage (40 = 40%) */}
            <div className="text-2xl font-bold text-red-700">{parameters.day7Decay.toFixed(0)}%</div>
            <div className="text-xs text-red-500">of original points retained</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <div className="text-sm text-red-600 mb-1">30-Day Decay</div>
            {/* Issue #33 Fix: Removed * 100 - day30Decay is already in percentage (8 = 8%) */}
            <div className="text-2xl font-bold text-red-700">{parameters.day30Decay.toFixed(0)}%</div>
            <div className="text-xs text-red-500">of original points retained</div>
          </div>
        </div>
      </div>

      {/* Operational Costs */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💸 Operational Costs</h3>
        <div className="bg-red-50 rounded-lg p-6 border border-red-200">
          <div className="text-center">
            <div className="text-sm text-red-600 mb-2">Monthly Reward System Costs</div>
            <div className="text-4xl font-bold text-red-700">{formatCurrency(rewards.opCosts)}</div>
            <div className="text-xs text-red-500 mt-2">
              Solana transaction costs + Infrastructure overhead
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
