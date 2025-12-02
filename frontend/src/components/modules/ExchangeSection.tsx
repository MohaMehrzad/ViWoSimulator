'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface ExchangeSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function ExchangeSection({ result, parameters }: ExchangeSectionProps) {
  const { exchange } = result;
  
  // Solana-specific data from breakdown
  const network = exchange.breakdown.network || 'solana';
  const dexAggregator = exchange.breakdown.dexAggregator || 'jupiter_v6';
  const totalSolanaTxs = exchange.breakdown.totalSolanaTxs || 0;
  const totalSolanaFeesUsd = exchange.breakdown.totalSolanaFeesUsd || 0;
  const solanaSavings = exchange.breakdown.solanaSavings || 0;
  
  // NEW-MED-004 FIX: Loss-leader detection
  const isLossLeader = exchange.breakdown.isLossLeader || exchange.margin < 10;
  const strategicNote = exchange.breakdown.strategicNote as string | undefined;

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-teal-500 to-cyan-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">💱</span>
          <div>
            <h2 className="text-2xl font-bold">Exchange / Wallet Module</h2>
            <p className="text-teal-200">Powered by Solana • Jupiter DEX Aggregator</p>
          </div>
          {/* Solana Badge */}
          <div className="ml-auto bg-white/20 backdrop-blur-sm rounded-lg px-3 py-1">
            <div className="flex items-center gap-2">
              <span className="text-lg">◎</span>
              <span className="font-semibold text-sm">Solana</span>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(exchange.revenue)}</div>
            <div className="text-xs text-teal-200 uppercase font-semibold">Revenue</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(exchange.costs)}</div>
            <div className="text-xs text-teal-200 uppercase font-semibold">Costs</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${exchange.profit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(exchange.profit)}
            </div>
            <div className="text-xs text-teal-200 uppercase font-semibold">Profit</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{exchange.margin.toFixed(1)}%</div>
            <div className="text-xs text-teal-200 uppercase font-semibold">Margin</div>
          </div>
        </div>
      </div>

      {/* Loss-Leader Warning - NEW-MED-004 FIX */}
      {isLossLeader && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 flex items-start gap-3">
          <span className="text-2xl">⚠️</span>
          <div>
            <div className="font-semibold text-amber-800">Loss-Leader Strategy Detected</div>
            <div className="text-sm text-amber-700">
              {strategicNote || (
                <>
                  Exchange module is operating with a margin below 10% ({exchange.margin.toFixed(1)}%). 
                  This may be intentional as a user acquisition strategy - subsidized trading 
                  helps attract users who generate revenue through other platform features.
                </>
              )}
            </div>
          </div>
        </div>
      )}
      
      {/* Solana Network Info */}
      <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <span className="text-purple-500 text-2xl">◎</span>
          <div className="flex-1">
            <strong className="text-purple-800">Solana Network Integration (November 2025)</strong>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
              <div className="text-center">
                <div className="text-lg font-bold text-purple-700">~$0.00025</div>
                <div className="text-xs text-purple-500">Per Transaction</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-purple-700">400ms</div>
                <div className="text-xs text-purple-500">Block Time</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-purple-700">Jupiter v6</div>
                <div className="text-xs text-purple-500">DEX Aggregator</div>
              </div>
              <div className="text-center">
                <div className="text-lg font-bold text-purple-700">20+</div>
                <div className="text-xs text-purple-500">DEXs Integrated</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* What This Covers */}
      <div className="bg-gradient-to-r from-teal-50 to-cyan-50 border border-teal-200 rounded-xl p-4">
        <div className="flex items-start gap-3">
          <span className="text-teal-500 text-xl">ℹ️</span>
          <div>
            <strong className="text-teal-800">What&apos;s Included:</strong>
            <span className="text-teal-700 ml-1">
              Fees from users swapping tokens via Jupiter aggregator (routes through Raydium, Orca, Meteora, Phoenix) 
              and withdrawing to external wallets. All operations on Solana mainnet-beta.
            </span>
          </div>
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💰 Revenue Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Swap Fee Revenue */}
          <div className="bg-emerald-50 rounded-xl p-5 border border-emerald-200">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">🔄</span>
              <h4 className="font-bold text-emerald-800">Swap/Exchange Fees</h4>
            </div>
            <div className="text-3xl font-bold text-emerald-700 mb-2">
              {formatCurrency(exchange.breakdown.swapFeeRevenue || 0)}
            </div>
            <div className="space-y-1 text-sm text-emerald-600">
              <div className="flex justify-between">
                <span>Fee Rate:</span>
                <span className="font-semibold">{(parameters.exchangeSwapFeePercent * 100).toFixed(2)}%</span>
              </div>
              <div className="flex justify-between">
                <span>Total Volume:</span>
                <span className="font-semibold">{formatCurrency(exchange.breakdown.totalTradingVolume || 0)}</span>
              </div>
            </div>
          </div>

          {/* Withdrawal Fee Revenue */}
          <div className="bg-blue-50 rounded-xl p-5 border border-blue-200">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">📤</span>
              <h4 className="font-bold text-blue-800">Withdrawal Fees</h4>
            </div>
            <div className="text-3xl font-bold text-blue-700 mb-2">
              {formatCurrency(exchange.breakdown.withdrawalFeeRevenue || 0)}
            </div>
            <div className="space-y-1 text-sm text-blue-600">
              <div className="flex justify-between">
                <span>Fee per Withdrawal:</span>
                <span className="font-semibold">{formatCurrency(parameters.exchangeWithdrawalFee)}</span>
              </div>
              <div className="flex justify-between">
                <span>Total Withdrawals:</span>
                <span className="font-semibold">{formatNumber(exchange.breakdown.totalWithdrawals || 0)}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* User Metrics */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">👥 User Metrics</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatNumber(exchange.breakdown.activeExchangeUsers || 0)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Active Exchange Users</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-teal-600">
              {(parameters.exchangeUserAdoptionRate * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Adoption Rate</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatCurrency(parameters.exchangeAvgMonthlyVolume)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Avg Volume/User</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {parameters.exchangeWithdrawalsPerUser.toFixed(1)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Withdrawals/User</div>
          </div>
        </div>
      </div>

      {/* Fee Settings */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">⚙️ Fee Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-teal-50 rounded-lg p-4 border border-teal-200">
            <div className="text-sm text-teal-600 mb-1">Swap/Exchange Fee</div>
            <div className="text-2xl font-bold text-teal-700">{(parameters.exchangeSwapFeePercent * 100).toFixed(2)}%</div>
            <div className="text-xs text-teal-500">Competitive with Binance (0.1%) & Coinbase (0.6%)</div>
          </div>
          <div className="bg-cyan-50 rounded-lg p-4 border border-cyan-200">
            <div className="text-sm text-cyan-600 mb-1">Withdrawal Fee</div>
            <div className="text-2xl font-bold text-cyan-700">{formatCurrency(parameters.exchangeWithdrawalFee)}</div>
            <div className="text-xs text-cyan-500">Flat fee per crypto withdrawal</div>
          </div>
        </div>
      </div>

      {/* Cost Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💸 Cost Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <div className="text-sm text-red-600 mb-1">Infrastructure</div>
            <div className="text-xl font-bold text-red-700">{formatCurrency(exchange.breakdown.infrastructureCost || 0)}</div>
            <div className="text-xs text-red-500">Helius RPC, servers</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <div className="text-sm text-red-600 mb-1">Solana Fees</div>
            <div className="text-xl font-bold text-red-700">{formatCurrency(exchange.breakdown.blockchainCosts || 0)}</div>
            <div className="text-xs text-red-500">~$0.00025 per transaction</div>
          </div>
          <div className="bg-red-50 rounded-lg p-4 border border-red-200">
            <div className="text-sm text-red-600 mb-1">Liquidity Costs</div>
            <div className="text-xl font-bold text-red-700">{formatCurrency(exchange.breakdown.liquidityCosts || 0)}</div>
            <div className="text-xs text-red-500">DEX fees + slippage</div>
          </div>
        </div>
      </div>

      {/* Solana Cost Savings */}
      <div className="bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border border-emerald-200 p-6">
        <h3 className="font-bold text-lg mb-4 text-emerald-800">🌿 Solana Cost Advantage</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-3xl font-bold text-emerald-600">
              {formatNumber(totalSolanaTxs)}
            </div>
            <div className="text-sm text-emerald-700">Monthly Transactions</div>
            <div className="text-xs text-emerald-500 mt-1">All on Solana</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-emerald-600">
              {formatCurrency(totalSolanaFeesUsd)}
            </div>
            <div className="text-sm text-emerald-700">Total Solana Fees</div>
            <div className="text-xs text-emerald-500 mt-1">At $0.00025/tx</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-emerald-600">
              {formatCurrency(solanaSavings)}
            </div>
            <div className="text-sm text-emerald-700">Savings vs Ethereum</div>
            <div className="text-xs text-emerald-500 mt-1">At ~$2.50/tx on ETH</div>
          </div>
        </div>
        <div className="mt-4 p-3 bg-emerald-100/50 rounded-lg">
          <div className="text-sm text-emerald-700">
            <strong>Why Solana?</strong> Ultra-low fees (~$0.00025 vs $2-50 on Ethereum), 
            400ms block time, and Jupiter aggregates 20+ DEXs for best execution.
          </div>
        </div>
      </div>

      {/* Annual Projection */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📅 Annual Projection</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Annual Revenue</div>
            <div className="text-2xl font-bold text-emerald-700">{formatCurrency(exchange.revenue * 12)}</div>
          </div>
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Annual Profit</div>
            <div className="text-2xl font-bold text-emerald-700">{formatCurrency(exchange.profit * 12)}</div>
          </div>
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Annual Trading Volume</div>
            <div className="text-2xl font-bold text-emerald-700">{formatCurrency((Number(exchange.breakdown.totalTradingVolume) || 0) * 12)}</div>
          </div>
        </div>
      </div>
    </section>
  );
}

