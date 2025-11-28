'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface ContentSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function ContentSection({ result, parameters }: ContentSectionProps) {
  const { content } = result;
  const breakdown = content.breakdown as Record<string, number | boolean | string>;
  
  // Extract anti-bot and creator metrics
  const verifiedCreators = (breakdown.verified_creators as number) || 0;
  const stakedCreators = (breakdown.staked_creators as number) || 0;
  const freePostingCreators = (breakdown.free_posting_creators as number) || 0;
  const payingCreators = (breakdown.paying_creators as number) || 0;
  const totalCreators = (breakdown.creators as number) || 0;
  
  // Anti-bot metrics
  const excessPostsWithFee = (breakdown.excess_posts_with_fee as number) || 0;
  const antiBotFeeVcoin = (breakdown.anti_bot_fee_vcoin as number) || 0.1;
  const engagementRefundRate = (breakdown.engagement_refund_rate as number) || 80;
  const effectiveAntiBotRevenue = (breakdown.effective_anti_bot_revenue as number) || 0;
  
  // Creator earnings
  const creatorEarningsUsd = (breakdown.creator_earnings_usd as number) || 0;
  const totalTipsUsd = (breakdown.total_tips_usd as number) || 0;
  
  // Premium features
  const boostedPosts = (breakdown.boosted_posts as number) || 0;
  const boostFeesUsd = (breakdown.boost_fees_usd as number) || 0;
  const premiumDms = (breakdown.premium_dms as number) || 0;
  const premiumDmUsd = (breakdown.premium_dm_usd as number) || 0;
  const premiumReactions = (breakdown.premium_reactions as number) || 0;
  const premiumReactionUsd = (breakdown.premium_reaction_usd as number) || 0;
  
  // Posts breakdown
  const monthlyPosts = (breakdown.monthly_posts as number) || 0;
  const textPosts = (breakdown.text_posts as number) || 0;
  const imagePosts = (breakdown.image_posts as number) || 0;
  const videoPosts = (breakdown.video_posts as number) || 0;
  const nftMints = (breakdown.nft_mints as number) || 0;
  
  // Break-even check
  const isBreakEven = (breakdown.is_break_even as boolean) ?? (Math.abs(content.profit) < content.costs * 0.1);
  
  // Free posting rate
  const freePostingRate = totalCreators > 0 ? (freePostingCreators / totalCreators * 100) : 0;

  return (
    <section className="space-y-8">
      {/* Module Header - Break-Even Model */}
      <div className="bg-gradient-to-r from-pink-500 to-rose-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">📄</span>
          <div className="flex-1">
            <h2 className="text-2xl font-bold">Content Module</h2>
            <p className="text-pink-200">Break-Even Anti-Bot Model • Creators Keep 100%</p>
          </div>
          {isBreakEven && (
            <div className="bg-white/20 backdrop-blur-sm rounded-full px-4 py-2 flex items-center gap-2">
              <span className="text-lg">⚖️</span>
              <span className="text-sm font-semibold">Break-Even</span>
            </div>
          )}
        </div>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(content.revenue)}</div>
            <div className="text-xs text-pink-200 uppercase font-semibold">Revenue</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(content.costs)}</div>
            <div className="text-xs text-pink-200 uppercase font-semibold">Costs</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${content.profit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(content.profit)}
            </div>
            <div className="text-xs text-pink-200 uppercase font-semibold">Net</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{freePostingRate.toFixed(0)}%</div>
            <div className="text-xs text-pink-200 uppercase font-semibold">Free Posting</div>
          </div>
        </div>
      </div>

      {/* Break-Even Model Explainer */}
      <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl border border-purple-200 p-6">
        <div className="flex items-start gap-4">
          <div className="bg-purple-100 rounded-full p-3">
            <span className="text-2xl">💡</span>
          </div>
          <div>
            <h3 className="font-bold text-lg text-purple-900">Break-Even Anti-Bot Model</h3>
            <p className="text-purple-700 mt-1">
              This module is designed to deter bots while <strong>not penalizing real creators</strong>. 
              Platform revenue comes from the <strong>5% Reward Fee</strong>, not content fees.
            </p>
            <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-white/70 rounded-lg p-3">
                <div className="text-sm font-semibold text-purple-800">✓ Verified Users</div>
                <div className="text-xs text-purple-600">Post for FREE unlimited</div>
              </div>
              <div className="bg-white/70 rounded-lg p-3">
                <div className="text-sm font-semibold text-purple-800">✓ Staked Users</div>
                <div className="text-xs text-purple-600">Post for FREE unlimited</div>
              </div>
              <div className="bg-white/70 rounded-lg p-3">
                <div className="text-sm font-semibold text-purple-800">✓ Regular Users</div>
                <div className="text-xs text-purple-600">First 150 posts/month FREE</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Anti-Bot Statistics */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>🤖</span> Anti-Bot Metrics
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Verified Creators</div>
            <div className="text-2xl font-bold text-emerald-700">{formatNumber(verifiedCreators)}</div>
            <div className="text-xs text-emerald-500">Post FREE</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="text-sm text-blue-600 mb-1">Staked Creators</div>
            <div className="text-2xl font-bold text-blue-700">{formatNumber(stakedCreators)}</div>
            <div className="text-xs text-blue-500">Post FREE</div>
          </div>
          <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
            <div className="text-sm text-amber-600 mb-1">Excess Posts Flagged</div>
            <div className="text-2xl font-bold text-amber-700">{formatNumber(excessPostsWithFee)}</div>
            <div className="text-xs text-amber-500">Anti-bot fee: {antiBotFeeVcoin} VCoin</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="text-sm text-purple-600 mb-1">Engagement Refund</div>
            <div className="text-2xl font-bold text-purple-700">{engagementRefundRate}%</div>
            <div className="text-xs text-purple-500">Returned to real users</div>
          </div>
        </div>
      </div>

      {/* Creator Earnings (100% to Creators) */}
      <div className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-xl p-6 text-white">
        <h3 className="font-bold text-lg mb-4 flex items-center gap-2">
          <span>💰</span> Creator Earnings (Creators Keep 100%)
        </h3>
        <p className="text-emerald-100 text-sm mb-4">
          No platform fee on creator earnings. Revenue comes from 5% Reward Fee instead.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="text-sm text-emerald-200 mb-1">Total Creator Earnings</div>
            <div className="text-2xl font-bold">{formatCurrency(creatorEarningsUsd)}</div>
            <div className="text-xs text-emerald-200">100% goes to creators</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="text-sm text-emerald-200 mb-1">Tips Received</div>
            <div className="text-2xl font-bold">{formatCurrency(totalTipsUsd)}</div>
            <div className="text-xs text-emerald-200">Fan tips to creators</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-lg p-4">
            <div className="text-sm text-emerald-200 mb-1">Platform Creator Fee</div>
            <div className="text-2xl font-bold">0%</div>
            <div className="text-xs text-emerald-200">✓ Removed - creators keep all</div>
          </div>
        </div>
      </div>

      {/* Post Activity */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📝 Post Activity</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
            <span className="text-3xl">📝</span>
            <div className="text-xl font-bold mt-2">{formatNumber(textPosts)}</div>
            <div className="text-xs text-gray-500">Text Posts</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
            <span className="text-3xl">🖼️</span>
            <div className="text-xl font-bold mt-2">{formatNumber(imagePosts)}</div>
            <div className="text-xs text-gray-500">Image Posts</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
            <span className="text-3xl">🎬</span>
            <div className="text-xl font-bold mt-2">{formatNumber(videoPosts)}</div>
            <div className="text-xs text-gray-500">Video Posts</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center border border-gray-200">
            <span className="text-3xl">🎨</span>
            <div className="text-xl font-bold mt-2">{formatNumber(nftMints)}</div>
            <div className="text-xs text-gray-500">NFT Mints</div>
          </div>
          <div className="bg-pink-50 rounded-lg p-4 text-center border border-pink-200">
            <span className="text-3xl">📊</span>
            <div className="text-xl font-bold mt-2 text-pink-700">{formatNumber(monthlyPosts)}</div>
            <div className="text-xs text-pink-500">Total Monthly</div>
          </div>
        </div>
      </div>

      {/* Optional Premium Features */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">✨ Optional Premium Features (User Choice)</h3>
        <p className="text-gray-600 text-sm mb-4">
          These features are optional - users choose to pay for extra visibility and engagement.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-4 border border-amber-200">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">🚀</span>
              <div className="text-sm font-semibold text-amber-700">Boosted Posts</div>
            </div>
            <div className="text-2xl font-bold text-amber-800">{formatNumber(boostedPosts)}</div>
            <div className="text-xs text-amber-600">Revenue: {formatCurrency(boostFeesUsd)}</div>
            <div className="text-xs text-amber-500 mt-1">5 VCoin per boost</div>
          </div>
          <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">💬</span>
              <div className="text-sm font-semibold text-blue-700">Premium DMs</div>
            </div>
            <div className="text-2xl font-bold text-blue-800">{formatNumber(premiumDms)}</div>
            <div className="text-xs text-blue-600">Revenue: {formatCurrency(premiumDmUsd)}</div>
            <div className="text-xs text-blue-500 mt-1">2 VCoin per DM to non-followers</div>
          </div>
          <div className="bg-gradient-to-br from-pink-50 to-rose-50 rounded-lg p-4 border border-rose-200">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">❤️</span>
              <div className="text-sm font-semibold text-rose-700">Premium Reactions</div>
            </div>
            <div className="text-2xl font-bold text-rose-800">{formatNumber(premiumReactions)}</div>
            <div className="text-xs text-rose-600">Revenue: {formatCurrency(premiumReactionUsd)}</div>
            <div className="text-xs text-rose-500 mt-1">1 VCoin per special reaction</div>
          </div>
        </div>
      </div>

      {/* Revenue vs 5% Reward Fee Comparison */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-xl p-6 text-white">
        <h3 className="font-bold text-lg mb-4">📈 Revenue Model Comparison</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white/5 rounded-lg p-4 border border-white/10">
            <div className="text-gray-400 text-sm mb-2">Content Module (Break-Even)</div>
            <div className={`text-3xl font-bold ${content.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {formatCurrency(content.profit)}
            </div>
            <div className="text-xs text-gray-400 mt-1">
              Designed to deter bots, not generate profit
            </div>
          </div>
          <div className="bg-emerald-500/20 rounded-lg p-4 border border-emerald-500/30">
            <div className="text-emerald-300 text-sm mb-2">5% Reward Fee (Primary Revenue)</div>
            <div className="text-3xl font-bold text-emerald-400">
              {formatCurrency(result.rewards.platformFeeUsd)}
            </div>
            <div className="text-xs text-emerald-300 mt-1">
              Calculated daily, taken before distribution
            </div>
          </div>
        </div>
        <p className="text-gray-400 text-xs mt-4 italic">
          The 5% Reward Fee is the platform's primary revenue source. Content fees only deter spam.
        </p>
      </div>
    </section>
  );
}
