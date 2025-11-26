'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface VelocitySectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function VelocitySection({ result, parameters }: VelocitySectionProps) {
  const { recapture, rewards, customerAcquisition } = result;

  // Calculate velocity metrics
  const totalCirculating = 100000000; // 100M assumed circulating supply
  const monthlyTransactions = recapture.totalRevenueSourceVcoin || 0;
  const velocity = totalCirculating > 0 ? (monthlyTransactions * 12) / totalCirculating : 0;
  
  // Transaction breakdown estimates
  const contentTransactions = parameters.postsPerUser * customerAcquisition.totalUsers * 0.1;
  const identityTransactions = parameters.monthlySales;
  const rewardDistributions = customerAcquisition.totalUsers * 0.6; // 60% claim rewards

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">⚡</span>
          <div>
            <h2 className="text-2xl font-bold">Token Velocity</h2>
            <p className="text-yellow-200">Transaction frequency and token turnover</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{velocity.toFixed(2)}</div>
            <div className="text-xs text-yellow-200 uppercase font-semibold">Annual Velocity</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatNumber(monthlyTransactions)}</div>
            <div className="text-xs text-yellow-200 uppercase font-semibold">Monthly TXs (VCoin)</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{velocity > 0 ? (12 / velocity).toFixed(1) : '∞'} mo</div>
            <div className="text-xs text-yellow-200 uppercase font-semibold">Avg Hold Time</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(monthlyTransactions * parameters.tokenPrice)}</div>
            <div className="text-xs text-yellow-200 uppercase font-semibold">Monthly Volume $</div>
          </div>
        </div>
      </div>

      {/* Velocity Explanation */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📚 What is Token Velocity?</h3>
        <div className="bg-gray-50 rounded-lg p-4 text-gray-700">
          <p className="mb-3">
            <strong>Token Velocity</strong> measures how quickly tokens change hands. It's calculated as:
          </p>
          <div className="bg-white rounded-lg p-4 text-center font-mono border border-gray-200 mb-3">
            Velocity = (Transaction Volume × 12) / Circulating Supply
          </div>
          <ul className="space-y-2 text-sm">
            <li>• <strong>Low velocity ({"<"}2):</strong> Tokens are held long-term (good for price)</li>
            <li>• <strong>Medium velocity (2-5):</strong> Balanced utility and holding</li>
            <li>• <strong>High velocity ({">"}5):</strong> Tokens move quickly (more utility-focused)</li>
          </ul>
        </div>
      </div>

      {/* Transaction Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Transaction Sources</h3>
        <div className="space-y-4">
          <div>
            <div className="flex justify-between mb-2">
              <span className="font-medium flex items-center gap-2">
                <span>📄</span> Content Transactions
              </span>
              <span className="font-semibold">{formatNumber(contentTransactions)}</span>
            </div>
            <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-pink-500"
                style={{ width: `${monthlyTransactions > 0 ? (contentTransactions / monthlyTransactions) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="font-medium flex items-center gap-2">
                <span>🆔</span> Identity Transactions
              </span>
              <span className="font-semibold">{formatNumber(identityTransactions)}</span>
            </div>
            <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-violet-500"
                style={{ width: `${monthlyTransactions > 0 ? (identityTransactions / monthlyTransactions) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="font-medium flex items-center gap-2">
                <span>🎁</span> Reward Distributions
              </span>
              <span className="font-semibold">{formatNumber(rewardDistributions)}</span>
            </div>
            <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-amber-500"
                style={{ width: `${monthlyTransactions > 0 ? (rewardDistributions / monthlyTransactions) * 100 : 0}%` }}
              ></div>
            </div>
          </div>
          <div>
            <div className="flex justify-between mb-2">
              <span className="font-medium flex items-center gap-2">
                <span>🔄</span> Other (Transfers, Trades)
              </span>
              <span className="font-semibold">
                {formatNumber(Math.max(0, monthlyTransactions - contentTransactions - identityTransactions - rewardDistributions))}
              </span>
            </div>
            <div className="h-4 bg-gray-100 rounded-full overflow-hidden">
              <div 
                className="h-full bg-gray-500"
                style={{ width: `${monthlyTransactions > 0 ? Math.max(0, 100 - ((contentTransactions + identityTransactions + rewardDistributions) / monthlyTransactions) * 100) : 0}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Velocity Factors */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🎛️ Velocity Control Mechanisms</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Velocity Reducers */}
          <div className="border border-emerald-200 rounded-lg p-4 bg-emerald-50">
            <h4 className="font-semibold text-emerald-700 mb-3 flex items-center gap-2">
              <span>🐢</span> Velocity Reducers (Price Support)
            </h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center justify-between">
                <span>Staking Lock-ups</span>
                <span className="font-semibold text-emerald-600">{formatNumber(recapture.staking)} VCoin</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Token Burns</span>
                <span className="font-semibold text-emerald-600">{formatNumber(recapture.burns)} VCoin</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Treasury Holdings</span>
                <span className="font-semibold text-emerald-600">{formatNumber(recapture.treasury)} VCoin</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Vesting Schedules</span>
                <span className="font-semibold text-emerald-600">Active</span>
              </li>
            </ul>
          </div>

          {/* Velocity Increasers */}
          <div className="border border-amber-200 rounded-lg p-4 bg-amber-50">
            <h4 className="font-semibold text-amber-700 mb-3 flex items-center gap-2">
              <span>🐇</span> Velocity Drivers (Utility)
            </h4>
            <ul className="space-y-2 text-sm">
              <li className="flex items-center justify-between">
                <span>Content Creation Fees</span>
                <span className="font-semibold text-amber-600">Active</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Identity Purchases</span>
                <span className="font-semibold text-amber-600">Active</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Marketplace Transactions</span>
                <span className="font-semibold text-amber-600">Active</span>
              </li>
              <li className="flex items-center justify-between">
                <span>Reward Claims</span>
                <span className="font-semibold text-amber-600">{formatNumber(rewards.monthlyEmission)}/mo</span>
              </li>
            </ul>
          </div>
        </div>
      </div>

      {/* Velocity Health */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🏥 Velocity Health Assessment</h3>
        <div className={`rounded-xl p-6 ${
          velocity >= 2 && velocity <= 5 
            ? 'bg-emerald-50 border border-emerald-200' 
            : velocity < 2 
              ? 'bg-blue-50 border border-blue-200'
              : 'bg-amber-50 border border-amber-200'
        }`}>
          <div className="flex items-center gap-4">
            <div className="text-4xl">
              {velocity >= 2 && velocity <= 5 ? '✅' : velocity < 2 ? '💎' : '⚡'}
            </div>
            <div>
              <div className={`font-bold text-lg ${
                velocity >= 2 && velocity <= 5 
                  ? 'text-emerald-700' 
                  : velocity < 2 
                    ? 'text-blue-700'
                    : 'text-amber-700'
              }`}>
                {velocity >= 2 && velocity <= 5 
                  ? 'Optimal Velocity' 
                  : velocity < 2 
                    ? 'Store of Value Mode'
                    : 'High Utility Mode'}
              </div>
              <div className="text-sm text-gray-600">
                {velocity >= 2 && velocity <= 5 
                  ? 'Good balance between utility and holding incentives' 
                  : velocity < 2 
                    ? 'Tokens are being held long-term - may need more utility features'
                    : 'High transaction volume - consider adding more holding incentives'}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}


