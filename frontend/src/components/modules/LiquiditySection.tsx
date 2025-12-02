'use client';

import { SimulationResult, SimulationParameters, SolanaPoolInfo } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface LiquiditySectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function LiquiditySection({ result, parameters }: LiquiditySectionProps) {
  // Get liquidity data from result (new backend module) or calculate fallback
  const liquidity = result.liquidity;
  
  // Fallback calculations if liquidity module not available
  const initialLiquidity = liquidity?.initialLiquidity || parameters.initialLiquidityUsd || 500000;
  const protocolOwnedPercent = liquidity?.protocolOwnedPercent || (parameters.protocolOwnedLiquidity || 0.70) * 100;
  const healthScore = liquidity?.healthScore || 0;
  const healthStatus = liquidity?.healthStatus || 'Unknown';
  const healthColor = liquidity?.healthColor || 'gray';
  const healthIcon = liquidity?.healthIcon || '❓';
  
  // Solana-specific data
  const network = liquidity?.network || 'solana';
  const primaryDex = liquidity?.primaryDex || 'raydium_clmm';
  const concentrationFactor = liquidity?.concentrationFactor || 4;  // FIX NEW-HIGH-001: Backend default is 4.0
  const effectiveLiquidity = liquidity?.effectiveLiquidity || initialLiquidity * concentrationFactor;
  // NEW-LOW-001 FIX: Properly type pools array with SolanaPoolInfo
  const pools: SolanaPoolInfo[] = liquidity?.pools || [];
  const jupiterEnabled = liquidity?.jupiterEnabled !== false;
  const estimatedLpEarnings = liquidity?.estimatedLpEarnings || 0;
  
  // Slippage data
  const slippage1k = liquidity?.slippage1k || 0;
  const slippage5k = liquidity?.slippage5k || 0;
  const slippage10k = liquidity?.slippage10k || 0;
  const slippage50k = liquidity?.slippage50k || 0;
  const slippage100k = liquidity?.slippage100k || 0;
  
  // Market dynamics
  const buyPressure = liquidity?.buyPressureUsd || 0;
  const sellPressure = liquidity?.sellPressureUsd || 0;
  const netPressure = liquidity?.netPressureUsd || 0;
  const pressureRatio = liquidity?.pressureRatio || 1;
  
  // Pool info
  const poolCount = liquidity?.poolCount || 1;
  const lockMonths = liquidity?.lockMonths || parameters.liquidityLockMonths || 24;
  const liquidityRatio = liquidity?.liquidityRatio || 0;
  const marketCap = liquidity?.marketCap || 0;
  
  // Target metrics
  const meets70Target = liquidity?.meets70Target || healthScore >= 70;
  const recommendedLiquidity = liquidity?.recommendedLiquidity || 0;

  // Color classes based on health
  const healthColorClasses = {
    emerald: 'from-emerald-500 to-teal-600',
    amber: 'from-amber-500 to-orange-600',
    orange: 'from-orange-500 to-red-500',
    red: 'from-red-500 to-rose-600',
    gray: 'from-gray-500 to-gray-600',
  };

  const gradientClass = healthColorClasses[healthColor as keyof typeof healthColorClasses] || healthColorClasses.gray;

  return (
    <section className="space-y-8">
      {/* Module Header with Health Score */}
      <div className={`bg-gradient-to-r ${gradientClass} rounded-2xl p-6 text-white`}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <span className="text-4xl">💧</span>
            <div>
              <h2 className="text-2xl font-bold">Liquidity Health</h2>
              <p className="text-white/80">Solana DEX Pools • Jupiter Aggregation</p>
            </div>
            {/* Solana Badge */}
            <div className="bg-white/20 backdrop-blur-sm rounded-lg px-3 py-1">
              <div className="flex items-center gap-2">
                <span className="text-lg">◎</span>
                <span className="font-semibold text-sm">Solana</span>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold">{healthScore.toFixed(0)}</div>
            <div className="text-lg font-semibold flex items-center justify-end gap-2">
              <span>{healthIcon}</span>
              <span>{healthStatus}</span>
            </div>
          </div>
        </div>
        
        {/* Health Score Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm mb-1">
            <span>Health Score</span>
            <span>{healthScore.toFixed(1)}%</span>
          </div>
          <div className="h-4 bg-black/20 rounded-full overflow-hidden">
            <div 
              className="h-full bg-white/90 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(healthScore, 100)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs mt-1 text-white/60">
            <span>0</span>
            <span className="text-white/80">Target: 70</span>
            <span>100</span>
          </div>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(initialLiquidity)}</div>
            <div className="text-xs text-white/80 uppercase font-semibold">Total Liquidity</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{protocolOwnedPercent.toFixed(0)}%</div>
            <div className="text-xs text-white/80 uppercase font-semibold">Protocol Owned</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{liquidityRatio.toFixed(1)}%</div>
            <div className="text-xs text-white/80 uppercase font-semibold">Liquidity Ratio</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{poolCount}</div>
            <div className="text-xs text-white/80 uppercase font-semibold">Liquidity Pools</div>
          </div>
        </div>
      </div>

      {/* Health Score Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Health Score Breakdown</h3>
        <div className="space-y-4">
          <ScoreComponent
            label="Liquidity Ratio (40% weight)"
            value={liquidityRatio}
            target={20}
            description="Liquidity/Market Cap ratio"
            score={Math.min(liquidityRatio / 20, 1) * 40}
          />
          <ScoreComponent
            label="Slippage Score (30% weight)"
            value={slippage10k}
            target={2}
            description="Slippage on $10K trade"
            score={Math.max(0, 1 - slippage10k / 2) * 30}
            isInverse
          />
          <ScoreComponent
            label="Protocol Owned (20% weight)"
            value={protocolOwnedPercent}
            target={100}
            description="POL percentage"
            score={(protocolOwnedPercent / 100) * 20}
          />
          <ScoreComponent
            label="Pool Diversity (10% weight)"
            value={poolCount}
            target={3}
            description="Number of pools"
            score={Math.min(poolCount / 3, 1) * 10}
            isCount
          />
        </div>
      </div>

      {/* Slippage Calculator */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📉 Slippage Calculator</h3>
        <p className="text-gray-600 text-sm mb-4">
          Estimated slippage for different trade sizes based on current liquidity of {formatCurrency(initialLiquidity)}.
        </p>
        <div className="grid grid-cols-5 gap-4">
          <SlippageCard amount="$1K" slippage={slippage1k} />
          <SlippageCard amount="$5K" slippage={slippage5k} />
          <SlippageCard amount="$10K" slippage={slippage10k} isHighlighted />
          <SlippageCard amount="$50K" slippage={slippage50k} />
          <SlippageCard amount="$100K" slippage={slippage100k} />
        </div>
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="text-sm text-blue-700">
            <strong>Target:</strong> {"<"}1% slippage on $10K trades for healthy liquidity.
            {slippage10k > 1 && (
              <span className="text-amber-600 ml-2">
                ⚠️ Current slippage is above target. Consider adding more liquidity.
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Market Pressure Analysis */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">⚖️ Market Pressure Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-emerald-500 rounded-full"></span>
              <span className="font-semibold text-emerald-600">Buy Pressure</span>
            </div>
            <div className="text-2xl font-bold">{formatCurrency(buyPressure)}</div>
            <div className="text-sm text-gray-500">Monthly buy volume</div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 bg-red-500 rounded-full"></span>
              <span className="font-semibold text-red-600">Sell Pressure</span>
            </div>
            <div className="text-2xl font-bold">{formatCurrency(sellPressure)}</div>
            <div className="text-sm text-gray-500">Monthly sell volume</div>
          </div>
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className={`w-3 h-3 rounded-full ${netPressure >= 0 ? 'bg-emerald-500' : 'bg-red-500'}`}></span>
              <span className={`font-semibold ${netPressure >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                Net Pressure
              </span>
            </div>
            <div className={`text-2xl font-bold ${netPressure >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
              {netPressure >= 0 ? '+' : ''}{formatCurrency(netPressure)}
            </div>
            <div className="text-sm text-gray-500">
              {pressureRatio.toFixed(2)}x buy/sell ratio
            </div>
          </div>
        </div>
        
        {/* Pressure Bar */}
        <div className="mt-6">
          <div className="h-6 bg-gray-100 rounded-full overflow-hidden flex">
            <div 
              className="bg-emerald-500 flex items-center justify-center text-white text-xs font-bold"
              style={{ width: `${(pressureRatio / (pressureRatio + 1)) * 100}%` }}
            >
              Buy
            </div>
            <div 
              className="bg-red-500 flex-1 flex items-center justify-center text-white text-xs font-bold"
            >
              Sell
            </div>
          </div>
        </div>
      </div>

      {/* Solana DEX Pools */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🏊 Solana Liquidity Pools</h3>
        
        {/* Pool Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {pools.length > 0 ? pools.map((pool: any, idx: number) => (
            <div key={idx} className="bg-gradient-to-br from-purple-50 to-indigo-50 rounded-lg p-4 border border-purple-200">
              <div className="flex items-center justify-between mb-2">
                <span className="font-bold text-purple-800">{pool.name}</span>
                <span className="text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded">
                  {pool.dex?.replace('_', ' ').toUpperCase() || 'RAYDIUM'}
                </span>
              </div>
              <div className="space-y-1 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-600">Type:</span>
                  <span className="font-medium">{pool.type?.replace('_', ' ') || 'CLMM'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Fee Tier:</span>
                  <span className="font-medium">{((pool.feeTier || 0.003) * 100).toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Share:</span>
                  <span className="font-medium">{((pool.share || 0) * 100).toFixed(0)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">TVL:</span>
                  <span className="font-medium">{formatCurrency(pool.liquidityUsd || 0)}</span>
                </div>
              </div>
            </div>
          )) : (
            <>
              <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-4 border border-blue-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-blue-800">VCoin/USDC</span>
                  <span className="text-xs bg-blue-200 text-blue-700 px-2 py-1 rounded">RAYDIUM CLMM</span>
                </div>
                <div className="text-sm text-blue-600">Primary trading pair</div>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-lg p-4 border border-purple-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-purple-800">VCoin/SOL</span>
                  <span className="text-xs bg-purple-200 text-purple-700 px-2 py-1 rounded">ORCA WHIRLPOOL</span>
                </div>
                <div className="text-sm text-purple-600">Secondary pair</div>
              </div>
              <div className="bg-gradient-to-br from-amber-50 to-orange-50 rounded-lg p-4 border border-amber-200">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-bold text-amber-800">VCoin/USDT</span>
                  <span className="text-xs bg-amber-200 text-amber-700 px-2 py-1 rounded">METEORA</span>
                </div>
                <div className="text-sm text-amber-600">Dynamic fees</div>
              </div>
            </>
          )}
        </div>
        
        {/* CLMM Concentration Factor */}
        <div className="bg-gradient-to-r from-emerald-50 to-teal-50 rounded-lg p-4 border border-emerald-200">
          <div className="flex items-center gap-3">
            <span className="text-2xl">⚡</span>
            <div className="flex-1">
              <div className="font-semibold text-emerald-800">Concentrated Liquidity (CLMM)</div>
              <div className="text-sm text-emerald-600">
                {concentrationFactor}x capital efficiency • Effective liquidity: {formatCurrency(effectiveLiquidity)}
              </div>
            </div>
            {jupiterEnabled && (
              <div className="text-right">
                <div className="text-sm font-semibold text-emerald-700">Jupiter Enabled</div>
                <div className="text-xs text-emerald-500">Best execution routing</div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Pool Distribution */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Ownership & Configuration</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold mb-3">Ownership Breakdown</h4>
            <div className="space-y-3">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-blue-600 font-medium">Protocol Owned (POL)</span>
                  <span>{protocolOwnedPercent.toFixed(0)}%</span>
                </div>
                <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500"
                    style={{ width: `${protocolOwnedPercent}%` }}
                  />
                </div>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-purple-600 font-medium">Community LP</span>
                  <span>{(100 - protocolOwnedPercent).toFixed(0)}%</span>
                </div>
                <div className="h-3 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-purple-500"
                    style={{ width: `${100 - protocolOwnedPercent}%` }}
                  />
                </div>
              </div>
            </div>
            
            {/* LP Earnings Estimate */}
            {estimatedLpEarnings > 0 && (
              <div className="mt-4 p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                <div className="text-sm text-emerald-700">
                  <strong>Est. LP Earnings:</strong> {formatCurrency(estimatedLpEarnings)}/month from fees
                </div>
              </div>
            )}
          </div>
          
          <div>
            <h4 className="font-semibold mb-3">Pool Configuration</h4>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Lock Period</span>
                <span className="font-semibold">{lockMonths} months</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Market Cap</span>
                <span className="font-semibold">{formatCurrency(marketCap)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Recommended Liquidity</span>
                <span className="font-semibold">{formatCurrency(recommendedLiquidity)}</span>
              </div>
              <div className="flex justify-between py-2 border-b border-gray-100">
                <span className="text-gray-600">Primary DEX</span>
                <span className="font-semibold">{primaryDex.replace('_', ' ').toUpperCase()}</span>
              </div>
              <div className="flex justify-between py-2">
                <span className="text-gray-600">Current vs Recommended</span>
                <span className={`font-semibold ${initialLiquidity >= recommendedLiquidity ? 'text-emerald-600' : 'text-amber-600'}`}>
                  {((initialLiquidity / recommendedLiquidity) * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Recommendations */}
      {!meets70Target && (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <span className="text-2xl">⚠️</span>
            <div>
              <h3 className="font-bold text-amber-800 mb-2">Liquidity Health Below Target</h3>
              <ul className="space-y-2 text-sm text-amber-700">
                {liquidityRatio < 14 && (
                  <li>• Increase liquidity to achieve 14%+ liquidity ratio</li>
                )}
                {slippage10k > 1 && (
                  <li>• Add more liquidity to reduce slippage below 1%</li>
                )}
                {protocolOwnedPercent < 60 && (
                  <li>• Increase protocol-owned liquidity to 60%+</li>
                )}
                {poolCount < 2 && (
                  <li>• Add additional liquidity pools for diversity</li>
                )}
                <li>
                  • <strong>Recommended:</strong> Add {formatCurrency(Math.max(0, recommendedLiquidity - initialLiquidity))} more liquidity
                </li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {meets70Target && (
        <div className="bg-emerald-50 border border-emerald-200 rounded-xl p-6">
          <div className="flex items-start gap-3">
            <span className="text-2xl">✅</span>
            <div>
              <h3 className="font-bold text-emerald-800 mb-2">Healthy Liquidity</h3>
              <p className="text-sm text-emerald-700">
                Your liquidity health score meets the 70% target. Continue monitoring slippage 
                and market pressure to maintain healthy trading conditions.
              </p>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}

// Helper Components
function ScoreComponent({
  label,
  value,
  target,
  description,
  score,
  maxScore = 40,  // NEW-MED-006 FIX: Accept maxScore prop instead of hardcoded /40
  isInverse = false,
  isCount = false,
}: {
  label: string;
  value: number;
  target: number;
  description: string;
  score: number;
  maxScore?: number;  // NEW-MED-006 FIX: Different components have different weights
  isInverse?: boolean;
  isCount?: boolean;
}) {
  const percentage = isCount 
    ? Math.min((value / target) * 100, 100)
    : isInverse 
      ? Math.max(0, (1 - value / target) * 100)
      : Math.min((value / target) * 100, 100);

  return (
    <div>
      <div className="flex justify-between mb-1">
        <span className="text-sm font-medium">{label}</span>
        <span className="text-sm font-bold">{score.toFixed(1)}/{maxScore}</span>
      </div>
      <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className={`h-full ${percentage >= 70 ? 'bg-emerald-500' : percentage >= 40 ? 'bg-amber-500' : 'bg-red-500'}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <div className="text-xs text-gray-500 mt-1">
        {description}: {isCount ? value : `${value.toFixed(2)}%`} 
        (target: {isInverse ? '<' : ''}{isCount ? target : `${target}%`})
      </div>
    </div>
  );
}

function SlippageCard({
  amount,
  slippage,
  isHighlighted = false,
}: {
  amount: string;
  slippage: number;
  isHighlighted?: boolean;
}) {
  const getSlippageColor = (s: number) => {
    if (s < 0.5) return 'text-emerald-600 bg-emerald-50 border-emerald-200';
    if (s < 1) return 'text-amber-600 bg-amber-50 border-amber-200';
    if (s < 2) return 'text-orange-600 bg-orange-50 border-orange-200';
    return 'text-red-600 bg-red-50 border-red-200';
  };

  return (
    <div className={`rounded-lg p-3 border text-center ${getSlippageColor(slippage)} ${isHighlighted ? 'ring-2 ring-blue-400' : ''}`}>
      <div className="text-xs font-semibold mb-1">{amount}</div>
      <div className="text-lg font-bold">{slippage.toFixed(2)}%</div>
      {isHighlighted && <div className="text-xs mt-1">Target</div>}
    </div>
  );
}
