'use client';

import React from 'react';
import { SimulationResult, GovernanceResult } from '@/types/simulation';

interface GovernanceSectionProps {
  result: SimulationResult;
}

export function GovernanceSection({ result }: GovernanceSectionProps) {
  const governance = result.governance;
  const fiveA = result.fiveA;
  
  // 5A Impact
  const fiveAEnabled = fiveA?.enabled || false;
  const fiveAGovBoost = fiveA?.governancePowerBoostAvg || 0;

  if (!governance) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-4">
          🗳️ Governance (veVCoin)
        </h2>
        <div className="text-center py-8 text-slate-400">
          <div className="text-4xl mb-3">🔒</div>
          <p>Governance data not available</p>
          <p className="text-sm">Requires staking to be active</p>
        </div>
      </div>
    );
  }

  // Safely access with defaults
  const totalVevcoinSupply = governance.totalVevcoinSupply ?? 0;
  const totalVevcoinSupplyUsd = governance.totalVevcoinSupplyUsd ?? 0;
  const avgBoostMultiplier = governance.avgBoostMultiplier ?? 1;
  const avgLockWeeks = governance.avgLockWeeks ?? 0;
  const activeVoters = governance.activeVoters ?? 0;
  const votingParticipationRate = governance.votingParticipationRate ?? 0;
  const activeVotingPower = governance.activeVotingPower ?? 0;
  const eligibleProposers = governance.eligibleProposers ?? 0;
  const expectedMonthlyProposals = governance.expectedMonthlyProposals ?? 0;
  const votingPowerConcentration = governance.votingPowerConcentration ?? 0;
  const decentralizationScore = governance.decentralizationScore ?? 0;
  const vevcoinOfCirculatingPercent = governance.vevcoinOfCirculatingPercent ?? 0;
  const revenue = governance.revenue ?? 0;
  
  // NEW-MED-002 FIX: Delegation metrics
  const delegators = governance.delegators ?? 0;
  const delegatedVotingPower = governance.delegatedVotingPower ?? 0;
  const delegationRate = governance.delegationRate ?? 0;
  const totalParticipants = governance.totalParticipants ?? activeVoters;
  const effectiveParticipationRate = governance.effectiveParticipationRate ?? votingParticipationRate;

  // Tier distribution
  const tierData = governance.tierDistribution || {};
  const totalTierUsers = Object.values(tierData).reduce((a: number, b: unknown) => a + (typeof b === 'number' ? b : 0), 0);

  // Health indicator
  const healthScore = governance.governanceHealthScore ?? 0;
  const healthColor = healthScore >= 70 ? 'text-emerald-500' : healthScore >= 40 ? 'text-amber-500' : 'text-red-500';
  const healthBg = healthScore >= 70 ? 'bg-emerald-50' : healthScore >= 40 ? 'bg-amber-50' : 'bg-red-50';

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div>
            <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
              🗳️ Governance (veVCoin)
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Vote-escrowed VCoin governance metrics
            </p>
          </div>
          {/* 5A Badge */}
          {fiveAEnabled && fiveAGovBoost > 0 && (
            <div className="bg-yellow-100 border border-yellow-200 rounded-lg px-3 py-1.5">
              <div className="flex items-center gap-1.5">
                <span>⭐</span>
                <span className="font-semibold text-sm text-yellow-700">+{fiveAGovBoost.toFixed(1)}% Power</span>
              </div>
            </div>
          )}
        </div>
        <div className={`px-4 py-2 rounded-lg ${healthBg}`}>
          <div className={`text-2xl font-bold ${healthColor}`}>
            {healthScore.toFixed(0)}
          </div>
          <div className="text-xs text-slate-500">Health Score</div>
        </div>
      </div>

      {/* veVCoin Overview */}
      <div className="bg-gradient-to-r from-violet-50 to-purple-50 rounded-xl p-5 border border-violet-100">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-violet-600">
              {(totalVevcoinSupply / 1_000_000).toFixed(2)}M
            </div>
            <div className="text-xs text-slate-500">Total veVCoin</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-violet-600">
              ${(totalVevcoinSupplyUsd / 1_000).toFixed(0)}K
            </div>
            <div className="text-xs text-slate-500">veVCoin Value</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {avgBoostMultiplier.toFixed(2)}x
            </div>
            <div className="text-xs text-slate-500">Avg Boost</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">
              {avgLockWeeks} weeks
            </div>
            <div className="text-xs text-slate-500">Avg Lock</div>
          </div>
        </div>
      </div>

      {/* Key Metrics - Updated grid for delegation section */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Participation - Updated with delegation */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
            👥 Participation
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-500">Direct Voters</span>
              <span className="font-medium">{activeVoters.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Direct Voting Rate</span>
              <span className="font-medium">{votingParticipationRate.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Voting Power</span>
              <span className="font-medium">{(activeVotingPower / 1_000_000).toFixed(2)}M</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Eligible Proposers</span>
              <span className="font-medium">{eligibleProposers}</span>
            </div>
          </div>
        </div>
        
        {/* NEW-MED-002 FIX: Delegation Section */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
            🤝 Delegation
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-500">Delegators</span>
              <span className="font-medium">{delegators.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Delegation Rate</span>
              <span className="font-medium">{delegationRate.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Delegated Power</span>
              <span className="font-medium">{(delegatedVotingPower / 1_000_000).toFixed(2)}M</span>
            </div>
            <div className="flex justify-between border-t border-slate-100 pt-2 mt-2">
              <span className="text-slate-700 font-medium">Total Participants</span>
              <span className="font-bold text-violet-600">{totalParticipants.toLocaleString()}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-700 font-medium">Effective Rate</span>
              <span className="font-bold text-violet-600">{effectiveParticipationRate.toFixed(1)}%</span>
            </div>
          </div>
        </div>

        {/* Proposals */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
            📝 Proposals
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-500">Expected/Month</span>
              <span className="font-medium">{expectedMonthlyProposals}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Min to Vote</span>
              <span className="font-medium">1 veVCoin</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Min to Propose</span>
              <span className="font-medium">1,000 veVCoin</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Fast Track</span>
              <span className="font-medium">10,000 veVCoin</span>
            </div>
          </div>
        </div>

        {/* Decentralization */}
        <div className="bg-white rounded-xl border border-slate-200 p-5">
          <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
            ⚖️ Decentralization
          </h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-slate-500">Concentration</span>
              <span className="font-medium">{votingPowerConcentration.toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">Decentralization Score</span>
              <span className={`font-medium ${decentralizationScore >= 50 ? 'text-emerald-600' : 'text-amber-600'}`}>
                {decentralizationScore.toFixed(1)}/100
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-500">veVCoin % of Supply</span>
              <span className="font-medium">{vevcoinOfCirculatingPercent.toFixed(2)}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Tier Distribution */}
      <div className="bg-white rounded-xl border border-slate-200 p-5">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          🏆 Governance Tiers
        </h3>
        <div className="grid grid-cols-3 gap-4">
          {[
            { key: 'community', name: 'Community', icon: '👥', desc: '1-999 veVCoin', color: 'bg-slate-100' },
            { key: 'delegate', name: 'Delegate', icon: '🎯', desc: '1,000-9,999 veVCoin', color: 'bg-blue-50' },
            { key: 'council', name: 'Council', icon: '👑', desc: '10,000+ veVCoin', color: 'bg-purple-50' },
          ].map((tier) => {
            const count = tierData[tier.key] || 0;
            const percent = totalTierUsers > 0 ? (count / totalTierUsers) * 100 : 0;
            return (
              <div key={tier.key} className={`${tier.color} rounded-lg p-4 text-center`}>
                <div className="text-2xl mb-2">{tier.icon}</div>
                <div className="font-semibold text-slate-800">{tier.name}</div>
                <div className="text-xs text-slate-500 mb-2">{tier.desc}</div>
                <div className="text-xl font-bold text-slate-700">{count.toLocaleString()}</div>
                <div className="text-xs text-slate-500">{percent.toFixed(1)}%</div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Voting Power Formula */}
      <div className="bg-slate-50 rounded-xl p-5">
        <h3 className="font-semibold text-slate-800 mb-3 flex items-center gap-2">
          📐 veVCoin Formula
        </h3>
        <div className="bg-white rounded-lg p-4 font-mono text-sm">
          <div className="text-slate-600">
            <span className="text-purple-600">veVCoin</span> = VCoin × <span className="text-blue-600">boost</span>
          </div>
          <div className="text-slate-500 mt-2">
            <span className="text-blue-600">boost</span> = 1 + (4 - 1) × (lockWeeks - 1) / (208 - 1)
          </div>
          <div className="text-xs text-slate-400 mt-2">
            Lock 1 week = 1x boost | Lock 208 weeks (4 years) = 4x boost
          </div>
        </div>
      </div>

      {/* Revenue (if any) */}
      {revenue > 0 && (
        <div className="bg-emerald-50 rounded-xl p-5 border border-emerald-100">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-emerald-800">Governance Revenue</h3>
              <p className="text-sm text-emerald-600">From proposal fees, badges, and premium features</p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-emerald-600">
                ${revenue.toLocaleString()}
              </div>
              <div className="text-xs text-emerald-500">Monthly</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

