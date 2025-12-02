'use client';

import React from 'react';
import { SimulationResult, GameTheoryResult } from '@/types/simulation';

interface GameTheorySectionProps {
  result: SimulationResult;
}

export function GameTheorySection({ result }: GameTheorySectionProps) {
  const gameData = result.tokenMetrics?.gameTheory;

  if (!gameData) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-4">
          🎮 Game Theory Analysis
        </h2>
        <div className="text-center py-8 text-slate-400">
          <div className="text-4xl mb-3">🎲</div>
          <p>Game theory analysis not available</p>
        </div>
      </div>
    );
  }

  const strategyColors: Record<string, string> = {
    stake: 'from-emerald-400 to-teal-400',
    sell: 'from-red-400 to-orange-400',
    hold: 'from-blue-400 to-indigo-400',
  };

  const strategyIcons: Record<string, string> = {
    stake: '🔒',
    sell: '💰',
    hold: '📦',
  };

  return (
    <div className="space-y-6">
      {/* Header with Health Score */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            🎮 Game Theory Analysis
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Nash equilibrium, rational actor behavior, and strategic dynamics
          </p>
        </div>
        <div className={`px-5 py-3 rounded-xl ${
          (gameData.healthScore ?? 50) >= 70 ? 'bg-emerald-100 border border-emerald-300' :
          (gameData.healthScore ?? 50) >= 40 ? 'bg-amber-100 border border-amber-300' :
          'bg-red-100 border border-red-300'
        }`}>
          <div className={`text-3xl font-bold ${
            (gameData.healthScore ?? 50) >= 70 ? 'text-emerald-700' :
            (gameData.healthScore ?? 50) >= 40 ? 'text-amber-700' : 'text-red-700'
          }`}>
            {(gameData.healthScore ?? 50).toFixed(0)}
          </div>
          <div className="text-xs text-center">Game Health</div>
        </div>
      </div>

      {/* Nash Equilibrium - Staking vs Selling */}
      <div className="bg-gradient-to-br from-slate-50 to-indigo-50 rounded-xl border border-slate-200 p-6">
        <h3 className="font-bold text-lg text-slate-800 mb-4 flex items-center gap-2">
          ⚖️ Staking vs Selling Equilibrium
        </h3>
        <p className="text-sm text-slate-600 mb-4">
          Nash equilibrium analysis of rational token holder decisions
        </p>

        {/* Strategy Probabilities */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {['stake', 'sell', 'hold'].map(strategy => {
            const prob = strategy === 'stake' ? gameData.equilibrium?.stakeProbability :
                        strategy === 'sell' ? gameData.equilibrium?.sellProbability :
                        gameData.equilibrium?.holdProbability;
            const isDominant = gameData.equilibrium?.dominantStrategy === strategy;
            
            return (
              <div 
                key={strategy}
                className={`relative rounded-xl p-4 text-center overflow-hidden ${
                  isDominant ? 'ring-2 ring-offset-2 ring-indigo-500' : ''
                }`}
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${strategyColors[strategy]} opacity-20`} />
                <div className="relative">
                  <div className="text-3xl mb-2">{strategyIcons[strategy]}</div>
                  <div className="text-2xl font-bold text-slate-800">
                    {(prob ?? 0).toFixed(1)}%
                  </div>
                  <div className="text-sm text-slate-600 capitalize">{strategy}</div>
                  {isDominant && (
                    <div className="mt-2 px-2 py-1 bg-indigo-100 text-indigo-700 text-xs font-bold rounded-full">
                      DOMINANT
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Equilibrium Details */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <div className={`text-lg font-bold ${
              gameData.equilibrium?.isStable ? 'text-emerald-600' : 'text-amber-600'
            }`}>
              {gameData.equilibrium?.isStable ? '✅ Stable' : '⚠️ Unstable'}
            </div>
            <div className="text-xs text-slate-500">Equilibrium State</div>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-slate-700 capitalize">
              {gameData.equilibrium?.dominantStrategy ?? 'None'}
            </div>
            <div className="text-xs text-slate-500">Dominant Strategy</div>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-slate-700">
              {(gameData.equilibrium?.deviationIncentive ?? 0).toFixed(1)}
            </div>
            <div className="text-xs text-slate-500">Deviation Incentive</div>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <div className="text-lg font-bold text-emerald-600">
              {(gameData.analysis?.stakingBreakevenPriceDrop ?? 0).toFixed(1)}%
            </div>
            <div className="text-xs text-slate-500">Staking Breakeven Drop</div>
          </div>
        </div>

        {/* Analysis */}
        <div className="mt-4 p-4 bg-white/80 rounded-lg">
          <div className="text-sm font-medium text-slate-700 mb-2">Analysis</div>
          <p className="text-sm text-slate-600">{gameData.analysis?.interpretation ?? 'No analysis available'}</p>
          <div className="mt-3 p-3 bg-indigo-50 rounded-lg">
            <div className="text-xs font-medium text-indigo-700">💡 Recommendation</div>
            <p className="text-sm text-indigo-800 mt-1">{gameData.analysis?.recommendation ?? ''}</p>
          </div>
        </div>
      </div>

      {/* Strategy Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.entries(gameData.strategies ?? {}).map(([strategy, metrics]) => (
          <div key={strategy} className="bg-white rounded-xl border border-slate-200 p-4">
            <div className="flex items-center gap-2 mb-3">
              <span className="text-2xl">{strategyIcons[strategy] || '📊'}</span>
              <h4 className="font-semibold text-slate-800 capitalize">{strategy}</h4>
            </div>
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Expected Return</span>
                <span className={`font-bold ${
                  (metrics?.returnPercent ?? 0) >= 0 ? 'text-emerald-600' : 'text-red-600'
                }`}>
                  {(metrics?.returnPercent ?? 0) >= 0 ? '+' : ''}
                  {(metrics?.returnPercent ?? 0).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Risk Level</span>
                <span className="font-bold text-slate-700">
                  {(metrics?.riskPercent ?? 0).toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500">Risk-Adj. Return</span>
                <span className="font-bold text-indigo-600">
                  {(metrics?.riskAdjustedReturn ?? 0).toFixed(2)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Governance Game */}
      <div className="bg-gradient-to-br from-purple-50 to-pink-50 rounded-xl border border-purple-200 p-6">
        <h3 className="font-bold text-lg text-purple-900 mb-4 flex items-center gap-2">
          🏛️ Governance Game Dynamics
        </h3>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-white/60 rounded-lg p-3">
            <div className="text-2xl font-bold text-purple-700">
              {gameData.governanceParticipation?.rationalParticipants ?? 0}
            </div>
            <div className="text-xs text-purple-600">Rational Voters</div>
          </div>
          <div className="bg-white/60 rounded-lg p-3">
            <div className="text-2xl font-bold text-purple-700">
              {(gameData.governanceParticipation?.participationRate ?? 0).toFixed(1)}%
            </div>
            <div className="text-xs text-purple-600">Participation Rate</div>
          </div>
          <div className="bg-white/60 rounded-lg p-3">
            <div className={`text-2xl font-bold ${
              gameData.governanceParticipation?.quorumAchievable ? 'text-emerald-600' : 'text-red-600'
            }`}>
              {gameData.governanceParticipation?.quorumAchievable ? '✅ Yes' : '❌ No'}
            </div>
            <div className="text-xs text-purple-600">Quorum Achievable</div>
          </div>
          <div className="bg-white/60 rounded-lg p-3">
            <div className="text-2xl font-bold text-purple-700">
              {gameData.minCoalitionSize ?? 0}
            </div>
            <div className="text-xs text-purple-600">Min Coalition Size</div>
          </div>
        </div>

        {/* Voter Apathy */}
        <div className={`p-4 rounded-lg ${
          gameData.voterApathy?.riskLevel === 'Critical' ? 'bg-red-100 border border-red-300' :
          gameData.voterApathy?.riskLevel === 'High' ? 'bg-orange-100 border border-orange-300' :
          gameData.voterApathy?.riskLevel === 'Moderate' ? 'bg-amber-100 border border-amber-300' :
          'bg-emerald-100 border border-emerald-300'
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <div className="font-medium text-slate-800">Voter Apathy Risk</div>
              <p className="text-sm text-slate-600 mt-1">
                {gameData.voterApathy?.interpretation ?? 'Analysis pending'}
              </p>
            </div>
            <div className={`text-2xl font-bold ${
              gameData.voterApathy?.riskLevel === 'Critical' ? 'text-red-700' :
              gameData.voterApathy?.riskLevel === 'High' ? 'text-orange-700' :
              gameData.voterApathy?.riskLevel === 'Moderate' ? 'text-amber-700' : 'text-emerald-700'
            }`}>
              {(gameData.voterApathy?.apatheticRatio ?? 0).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>

      {/* Coordination Game */}
      <div className="bg-gradient-to-br from-cyan-50 to-teal-50 rounded-xl border border-cyan-200 p-6">
        <h3 className="font-bold text-lg text-cyan-900 mb-4 flex items-center gap-2">
          🤝 Coordination Game Analysis
        </h3>
        <p className="text-sm text-cyan-700 mb-4">
          {gameData.coordination?.description ?? 'Analyzing coordination dynamics...'}
        </p>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <div className="text-sm font-medium text-cyan-800">Game Type</div>
            <div className="text-lg font-bold text-cyan-700">
              {gameData.coordination?.gameType ?? 'Unknown'}
            </div>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <div className="text-sm font-medium text-cyan-800">Equilibrium</div>
            <div className="text-sm font-bold text-cyan-700">
              {gameData.coordination?.equilibrium ?? 'Mixed'}
            </div>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <div className="text-sm font-medium text-cyan-800">Coop. Probability</div>
            <div className="text-lg font-bold text-cyan-700">
              {(gameData.coordination?.cooperationProbability ?? 50).toFixed(0)}%
            </div>
          </div>
          <div className="bg-white/60 rounded-lg p-3 text-center">
            <div className="text-sm font-medium text-cyan-800">Sustainable</div>
            <div className={`text-lg font-bold ${
              gameData.cooperationSustainable ? 'text-emerald-600' : 'text-red-600'
            }`}>
              {gameData.cooperationSustainable ? '✅ Yes' : '❌ No'}
            </div>
          </div>
        </div>

        {/* Cooperation visualization */}
        <div className="bg-white/60 rounded-lg p-4">
          <div className="text-sm font-medium text-cyan-800 mb-2">Cooperation vs Defection Balance</div>
          <div className="h-4 bg-slate-200 rounded-full overflow-hidden flex">
            <div 
              className="bg-gradient-to-r from-emerald-400 to-teal-400 rounded-l-full"
              style={{ width: `${gameData.coordination?.cooperationProbability ?? 50}%` }}
            />
            <div 
              className="bg-gradient-to-r from-red-400 to-orange-400 rounded-r-full"
              style={{ width: `${100 - (gameData.coordination?.cooperationProbability ?? 50)}%` }}
            />
          </div>
          <div className="flex justify-between text-xs text-slate-500 mt-1">
            <span>🤝 Cooperate ({(gameData.coordination?.cooperationProbability ?? 50).toFixed(0)}%)</span>
            <span>({100 - (gameData.coordination?.cooperationProbability ?? 50).toFixed(0)}%) Defect 💨</span>
          </div>
        </div>
      </div>

      {/* Primary Risk */}
      {gameData.primaryRisk && gameData.primaryRisk !== 'None' && (
        <div className="bg-red-50 rounded-xl border border-red-200 p-5">
          <div className="flex items-center gap-3">
            <span className="text-3xl">⚠️</span>
            <div>
              <div className="font-bold text-red-800">Primary Risk Identified</div>
              <p className="text-sm text-red-700">{gameData.primaryRisk}</p>
            </div>
          </div>
        </div>
      )}

      {/* Recommendations */}
      {gameData.recommendations && gameData.recommendations.length > 0 && (
        <div className="bg-indigo-50 rounded-xl border border-indigo-200 p-5">
          <h3 className="font-semibold text-indigo-900 mb-3 flex items-center gap-2">
            🎯 Strategic Recommendations
          </h3>
          <ul className="space-y-2">
            {gameData.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-indigo-800">
                <span className="text-indigo-500 mt-0.5">•</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Interpretation Guide */}
      <div className="bg-slate-50 rounded-xl p-5">
        <h3 className="font-semibold text-slate-800 mb-4">📖 Game Theory Guide</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Nash Equilibrium</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• Stable: No player gains by changing</li>
              <li>• Dominant: Best regardless of others</li>
              <li>• Mixed: Random strategy optimal</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Coordination Games</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• Stag Hunt: Cooperation is risky</li>
              <li>• PD: Defection is dominant</li>
              <li>• Battle of Sexes: Multiple equilibria</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Key Metrics</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• Coop &gt;60%: Healthy ecosystem</li>
              <li>• Quorum achievable: Gov works</li>
              <li>• Stable eq: Predictable behavior</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

