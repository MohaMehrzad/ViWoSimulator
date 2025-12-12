'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface PreLaunchSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function PreLaunchSection({ result, parameters }: PreLaunchSectionProps) {
  const prelaunch = result.prelaunch;
  const referral = prelaunch?.referral;
  const points = prelaunch?.points;
  const gasless = prelaunch?.gasless;
  
  // #region agent log
  fetch('http://127.0.0.1:7242/ingest/63e31cbd-d385-4178-b960-6e5c3301028f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'PreLaunchSection.tsx:init',message:'Gasless data inspection',data:{hasGasless:!!gasless,gaslessKeys:gasless?Object.keys(gasless):[],costPerTransactionUsd:gasless?.costPerTransactionUsd,budgetUtilization:gasless?.budgetUtilization},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
  // #endregion

  // Calculate overview metrics
  const totalCostUsd = prelaunch?.totalPrelaunchCostUsd || 0;
  const totalCostVcoin = prelaunch?.totalPrelaunchCostVcoin || 0;
  const referralUsers = prelaunch?.referralUsersAcquired || 0;
  const pointsTokens = prelaunch?.pointsTokensAllocated || 0;

  // Referral tier data
  const referralTiers = [
    { name: 'Starter', range: '1-10', bonus: 50, color: 'from-gray-500 to-gray-600' },
    { name: 'Builder', range: '11-50', bonus: 75, color: 'from-blue-500 to-blue-600' },
    { name: 'Ambassador', range: '51-200', bonus: 100, color: 'from-purple-500 to-purple-600' },
    { name: 'Partner', range: '200+', bonus: 150, color: 'from-amber-500 to-amber-600' },
  ];

  // Points activities
  const pointsActivities = [
    { name: 'Waitlist Signup', points: 100, max: 'Once' },
    { name: 'Social Follow', points: 25, max: 'Per platform' },
    { name: 'Daily Check-in', points: 5, max: '1/day' },
    { name: 'Invite (Joins)', points: 50, max: 'Unlimited' },
    { name: 'Invite (Verifies)', points: 100, max: 'Unlimited' },
    { name: 'Beta Testing', points: 500, max: 'Once' },
  ];

  // Gasless tiers
  const gaslessTiers = [
    { name: 'New User', free: '10', description: 'First 10 transactions' },
    { name: 'Verified', free: '50/mo', description: 'Monthly sponsored' },
    { name: 'Premium', free: 'Unlimited', description: 'Full sponsorship' },
    { name: 'Enterprise', free: 'Unlimited', description: 'Business accounts' },
  ];

  if (!prelaunch) {
    return (
      <section className="space-y-8">
        <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-2xl p-6 text-white">
          <div className="flex items-center gap-3 mb-4">
            <span className="text-4xl">🚀</span>
            <div>
              <h2 className="text-2xl font-bold">Pre-Launch Modules</h2>
              <p className="text-white/80">Referral • Points • Gasless Onboarding</p>
            </div>
          </div>
          <p className="text-white/70">Pre-launch modules are not enabled in this simulation.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 rounded-2xl p-6 text-white">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-4xl">🚀</span>
            <div>
              <h2 className="text-2xl font-bold">Pre-Launch Modules</h2>
              <p className="text-white/80">2025 Standards • Referral • Points • Gasless</p>
            </div>
          </div>
          <div className="text-right">
            <div className="text-3xl font-bold">{formatCurrency(totalCostUsd)}</div>
            <div className="text-white/70">Monthly Cost</div>
          </div>
        </div>
        
        {/* Quick Stats */}
        <div className="grid grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 rounded-xl p-4 backdrop-blur">
            <div className="text-2xl font-bold">{formatNumber(referralUsers)}</div>
            <div className="text-sm text-white/70">Referral Users</div>
          </div>
          <div className="bg-white/10 rounded-xl p-4 backdrop-blur">
            <div className="text-2xl font-bold">{formatNumber(pointsTokens)}</div>
            <div className="text-sm text-white/70">Points Pool Tokens</div>
          </div>
          <div className="bg-white/10 rounded-xl p-4 backdrop-blur">
            <div className="text-2xl font-bold">{referral?.viralCoefficient?.toFixed(2) || '0.50'}</div>
            <div className="text-sm text-white/70">Viral Coefficient</div>
          </div>
          <div className="bg-white/10 rounded-xl p-4 backdrop-blur">
            <div className="text-2xl font-bold">{formatNumber(totalCostVcoin)}</div>
            <div className="text-sm text-white/70">Cost (VCoin)</div>
          </div>
        </div>
      </div>

      {/* Referral Program Section */}
      {referral && (
        <div className="bg-gray-800/50 rounded-2xl p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">👥</span>
            <div>
              <h3 className="text-xl font-bold text-white">Referral Program</h3>
              <p className="text-gray-400">Tiered rewards for genuine user acquisition</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Tier Cards */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">Reward Tiers</h4>
              {referralTiers.map((tier) => (
                <div
                  key={tier.name}
                  className={`bg-gradient-to-r ${tier.color} rounded-xl p-4 text-white`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <div className="font-bold">{tier.name}</div>
                      <div className="text-sm text-white/70">{tier.range} referrals</div>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold">{tier.bonus} VCoin</div>
                      <div className="text-sm text-white/70">per referral</div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Metrics */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">Performance Metrics</h4>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-700/50 rounded-xl p-4">
                  <div className="text-2xl font-bold text-indigo-400">
                    {formatNumber(referral.usersWithReferrals)}
                  </div>
                  <div className="text-sm text-gray-400">Active Referrers</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-4">
                  <div className="text-2xl font-bold text-purple-400">
                    {formatNumber(referral.qualifiedReferrals)}
                  </div>
                  <div className="text-sm text-gray-400">Qualified Referrals</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-4">
                  <div className="text-2xl font-bold text-pink-400">
                    {((referral.qualificationRate ?? 0) * 100).toFixed(0)}%
                  </div>
                  <div className="text-sm text-gray-400">Qualification Rate</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-4">
                  <div className="text-2xl font-bold text-amber-400">
                    {formatNumber(referral.avgBonusPerReferrerVcoin)}
                  </div>
                  <div className="text-sm text-gray-400">Avg Bonus/Referrer</div>
                </div>
              </div>

              {/* Cost Summary */}
              <div className="bg-gray-700/30 rounded-xl p-4 mt-4">
                <div className="flex justify-between items-center">
                  <span className="text-gray-400">Monthly Referral Cost</span>
                  <span className="text-xl font-bold text-white">
                    {formatCurrency(referral.monthlyReferralCostUsd)}
                  </span>
                </div>
                <div className="flex justify-between items-center mt-2">
                  <span className="text-gray-400">Bonus Distributed</span>
                  <span className="text-lg font-medium text-indigo-400">
                    {formatNumber(referral.bonusDistributedVcoin)} VCoin
                  </span>
                </div>
              </div>

              {/* Anti-Sybil */}
              <div className="bg-red-900/20 border border-red-500/30 rounded-xl p-4">
                <div className="flex items-center gap-2 mb-2">
                  <span className="text-lg">🛡️</span>
                  <span className="font-semibold text-red-400">Anti-Sybil Protection</span>
                </div>
                <div className="text-sm text-gray-300">
                  <span className="text-red-400 font-bold">{formatNumber(referral.suspectedSybilReferrals ?? 0)}</span> suspected sybil referrals blocked ({((referral.sybilRejectionRate ?? 0) * 100).toFixed(1)}% rejection rate)
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Points System Section */}
      {points && (
        <div className="bg-gray-800/50 rounded-2xl p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">⭐</span>
            <div>
              <h3 className="text-xl font-bold text-white">Pre-Launch Points System</h3>
              <p className="text-gray-400">Points convert to tokens at TGE</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Activity Table */}
            <div>
              <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">Point Activities</h4>
              <div className="bg-gray-700/30 rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-gray-700/50">
                    <tr>
                      <th className="text-left p-3 text-gray-400 text-sm">Activity</th>
                      <th className="text-right p-3 text-gray-400 text-sm">Points</th>
                      <th className="text-right p-3 text-gray-400 text-sm">Limit</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-700">
                    {pointsActivities.map((activity) => (
                      <tr key={activity.name} className="hover:bg-gray-700/30">
                        <td className="p-3 text-white">{activity.name}</td>
                        <td className="p-3 text-right text-amber-400 font-bold">+{activity.points}</td>
                        <td className="p-3 text-right text-gray-400 text-sm">{activity.max}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Distribution Metrics */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">Token Conversion</h4>
              
              {/* Pool Info */}
              <div className="bg-gradient-to-r from-amber-500/20 to-orange-500/20 border border-amber-500/30 rounded-xl p-4">
                <div className="text-3xl font-bold text-amber-400">
                  {formatNumber(points.pointsPoolTokens)} VCoin
                </div>
                <div className="text-sm text-gray-300 mt-1">
                  Points Pool ({((points.pointsPoolPercent ?? 0) * 100).toFixed(0)}% of supply)
                </div>
                <div className="mt-3 text-sm text-gray-400">
                  Conversion Rate: <span className="text-white font-mono">{(points.tokensPerPoint ?? 0).toFixed(6)}</span> VCoin/point
                </div>
              </div>

              {/* Segment Distribution */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-lg font-bold text-white">{formatNumber(points.waitlistUsers)}</div>
                  <div className="text-xs text-gray-400">Waitlist Users</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-lg font-bold text-green-400">{formatNumber(points.participatingUsers)}</div>
                  <div className="text-xs text-gray-400">Participating</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-lg font-bold text-blue-400">{(points.avgPointsPerUser ?? 0).toFixed(0)}</div>
                  <div className="text-xs text-gray-400">Avg Points/User</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-lg font-bold text-purple-400">{formatNumber(points.avgTokensPerUser)}</div>
                  <div className="text-xs text-gray-400">Avg Tokens/User</div>
                </div>
              </div>

              {/* Top Earners */}
              <div className="bg-gray-700/30 rounded-xl p-4">
                <h5 className="text-sm font-semibold text-gray-400 mb-3">Token Distribution</h5>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Top 1% (Ambassadors)</span>
                    <span className="text-amber-400 font-bold">{formatNumber(points.top1PercentTokens)} VCoin</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Top 10% (Power Users)</span>
                    <span className="text-purple-400 font-bold">{formatNumber(points.top10PercentTokens)} VCoin</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Bottom 50% (Casual)</span>
                    <span className="text-gray-300">{formatNumber(points.bottom50PercentTokens)} VCoin</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Gasless Onboarding Section */}
      {gasless && (
        <div className="bg-gray-800/50 rounded-2xl p-6 border border-gray-700">
          <div className="flex items-center gap-3 mb-6">
            <span className="text-3xl">⛽</span>
            <div>
              <h3 className="text-xl font-bold text-white">Gasless Onboarding</h3>
              <p className="text-gray-400">Sponsored transactions for seamless UX</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-6">
            {/* Tier Cards */}
            <div className="space-y-3">
              <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">Sponsorship Tiers</h4>
              {gaslessTiers.map((tier, index) => (
                <div
                  key={tier.name}
                  className="bg-gray-700/50 rounded-xl p-4 flex justify-between items-center"
                >
                  <div>
                    <div className="font-bold text-white">{tier.name}</div>
                    <div className="text-sm text-gray-400">{tier.description}</div>
                  </div>
                  <div className="bg-emerald-500/20 text-emerald-400 px-3 py-1 rounded-full font-bold">
                    {tier.free}
                  </div>
                </div>
              ))}
            </div>

            {/* Cost Analysis */}
            <div className="space-y-4">
              <h4 className="text-sm font-semibold text-gray-400 uppercase tracking-wide">Cost Analysis</h4>
              
              {/* Budget Overview */}
              <div className="bg-gray-700/30 rounded-xl p-4">
                <div className="flex justify-between items-center mb-3">
                  <span className="text-gray-400">Monthly Budget</span>
                  <span className="text-xl font-bold text-white">
                    {formatCurrency(gasless.monthlySponsorshipBudgetUsd ?? 0)}
                  </span>
                </div>
                <div className="w-full bg-gray-600 rounded-full h-3">
                  <div 
                    className="bg-gradient-to-r from-emerald-500 to-teal-500 h-3 rounded-full transition-all"
                    style={{ width: `${Math.min((gasless.budgetUtilization ?? 0) * 100, 100)}%` }}
                  />
                </div>
                <div className="text-sm text-gray-400 mt-2">
                  {((gasless.budgetUtilization ?? 0) * 100).toFixed(1)}% utilized ({formatCurrency(gasless.totalSponsorshipCostUsd ?? 0)} spent)
                </div>
              </div>

              {/* User Breakdown */}
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-lg font-bold text-blue-400">{formatNumber(gasless.newUsers ?? 0)}</div>
                  <div className="text-xs text-gray-400">New Users</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-lg font-bold text-green-400">{formatNumber(gasless.verifiedUsers ?? 0)}</div>
                  <div className="text-xs text-gray-400">Verified Users</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-lg font-bold text-purple-400">{formatNumber(gasless.premiumUsers ?? 0)}</div>
                  <div className="text-xs text-gray-400">Premium Users</div>
                </div>
                <div className="bg-gray-700/50 rounded-xl p-3">
                  <div className="text-lg font-bold text-amber-400">{formatNumber(gasless.enterpriseUsers ?? 0)}</div>
                  <div className="text-xs text-gray-400">Enterprise</div>
                </div>
              </div>

              {/* Transaction Stats */}
              <div className="bg-emerald-900/20 border border-emerald-500/30 rounded-xl p-4">
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <div className="text-gray-400">Sponsored Transactions</div>
                    <div className="text-xl font-bold text-emerald-400">
                      {formatNumber(gasless.totalSponsoredTransactions ?? 0)}
                    </div>
                  </div>
                  <div>
                    <div className="text-gray-400">Cost per Transaction</div>
                    <div className="text-xl font-bold text-white">
                      ${(gasless.costPerTransactionUsd ?? 0).toFixed(5)}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Summary Card */}
      <div className="bg-gradient-to-r from-gray-800 to-gray-900 rounded-2xl p-6 border border-gray-700">
        <h3 className="text-lg font-bold text-white mb-4">Pre-Launch Module Summary</h3>
        <div className="grid grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-indigo-400">{formatCurrency(totalCostUsd)}</div>
            <div className="text-sm text-gray-400 mt-1">Total Monthly Cost</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-400">{formatNumber(totalCostVcoin)}</div>
            <div className="text-sm text-gray-400 mt-1">VCoin Distributed</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-pink-400">{formatNumber(referralUsers)}</div>
            <div className="text-sm text-gray-400 mt-1">Users via Referral</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-amber-400">{formatNumber(pointsTokens)}</div>
            <div className="text-sm text-gray-400 mt-1">Points Pool Tokens</div>
          </div>
        </div>
      </div>
    </section>
  );
}

