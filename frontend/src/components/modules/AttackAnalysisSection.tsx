'use client';

import React, { useState } from 'react';
import { SimulationResult, AttackAnalysisResult, AttackScenarioDetail } from '@/types/simulation';

interface AttackAnalysisSectionProps {
  result: SimulationResult;
}

export function AttackAnalysisSection({ result }: AttackAnalysisSectionProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const attackData = result.tokenMetrics?.attackAnalysis;

  if (!attackData) {
    return (
      <div className="bg-white rounded-xl border border-slate-200 p-6">
        <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-4">
          🛡️ Attack Analysis
        </h2>
        <div className="text-center py-8 text-slate-400">
          <div className="text-4xl mb-3">🔒</div>
          <p>Attack analysis not available</p>
        </div>
      </div>
    );
  }

  const riskColors: Record<string, string> = {
    emerald: 'bg-emerald-100 text-emerald-800 border-emerald-300',
    amber: 'bg-amber-100 text-amber-800 border-amber-300',
    orange: 'bg-orange-100 text-orange-800 border-orange-300',
    red: 'bg-red-100 text-red-800 border-red-300',
    gray: 'bg-slate-100 text-slate-800 border-slate-300',
  };

  const severityColors: Record<string, string> = {
    low: 'bg-emerald-100 text-emerald-700 border-emerald-300',
    medium: 'bg-amber-100 text-amber-700 border-amber-300',
    high: 'bg-orange-100 text-orange-700 border-orange-300',
    critical: 'bg-red-100 text-red-700 border-red-300',
  };

  const categoryIcons: Record<string, string> = {
    flash_loan: '⚡',
    sandwich: '🥪',
    mev: '🔄',
    rug_pull: '🚨',
    oracle: '🔮',
    governance: '🏛️',
  };

  const categoryNames: Record<string, string> = {
    flash_loan: 'Flash Loan',
    sandwich: 'Sandwich/MEV',
    mev: 'MEV Extraction',
    rug_pull: 'Rug Pull',
    oracle: 'Oracle',
    governance: 'Governance',
  };

  // Get unique categories
  const categories = ['all', ...new Set(attackData.scenarios.map(s => s.category))];
  
  // Filter scenarios by category
  const filteredScenarios = selectedCategory === 'all' 
    ? attackData.scenarios 
    : attackData.scenarios.filter(s => s.category === selectedCategory);

  // Group by severity
  const criticalCount = attackData.scenarios.filter(s => s.severity === 'critical').length;
  const highCount = attackData.scenarios.filter(s => s.severity === 'high').length;

  return (
    <div className="space-y-6">
      {/* Header with Vulnerability Score */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            🛡️ Economic Attack Analysis
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            DeFi attack vector simulation and vulnerability assessment
          </p>
        </div>
        <div className={`px-5 py-3 rounded-xl border ${riskColors[attackData.riskColor || 'gray']}`}>
          <div className="text-3xl font-bold">
            {(attackData.vulnerabilityScore ?? 50).toFixed(0)}
          </div>
          <div className="text-xs text-center">{attackData.riskLevel ?? 'Unknown'} Risk</div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <div className="bg-red-50 rounded-xl p-4 border border-red-200">
          <div className="text-2xl font-bold text-red-700">{criticalCount}</div>
          <div className="text-sm text-red-600">Critical Vulnerabilities</div>
        </div>
        <div className="bg-orange-50 rounded-xl p-4 border border-orange-200">
          <div className="text-2xl font-bold text-orange-700">{highCount}</div>
          <div className="text-sm text-orange-600">High Risk</div>
        </div>
        <div className="bg-slate-50 rounded-xl p-4 border border-slate-200">
          <div className="text-2xl font-bold text-slate-700">
            ${((attackData.totalPotentialLossUsd ?? 0) / 1_000_000).toFixed(1)}M
          </div>
          <div className="text-sm text-slate-600">Total Exposure</div>
        </div>
        <div className="bg-blue-50 rounded-xl p-4 border border-blue-200">
          <div className="text-2xl font-bold text-blue-700">
            {(attackData.liquidityRatio ?? 0).toFixed(1)}%
          </div>
          <div className="text-sm text-blue-600">Liquidity Ratio</div>
        </div>
        <div className="bg-purple-50 rounded-xl p-4 border border-purple-200">
          <div className="text-2xl font-bold text-purple-700">
            {attackData.scenarios?.length ?? 0}
          </div>
          <div className="text-sm text-purple-600">Scenarios Analyzed</div>
        </div>
      </div>

      {/* Security Features */}
      <div className="bg-gradient-to-br from-slate-50 to-blue-50 rounded-xl border border-slate-200 p-5">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          🔐 Security Features Status
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className={`p-3 rounded-lg ${
            attackData.securityFeatures?.hasTimelock 
              ? 'bg-emerald-100 border border-emerald-300' 
              : 'bg-red-100 border border-red-300'
          }`}>
            <div className="flex items-center gap-2 mb-1">
              {attackData.securityFeatures?.hasTimelock ? '✅' : '❌'}
              <span className="font-medium">Timelock</span>
            </div>
            <div className="text-xs text-slate-600">
              {attackData.securityFeatures?.hasTimelock 
                ? `${attackData.securityFeatures?.timelockDelayHours ?? 0}h delay` 
                : 'Not implemented'}
            </div>
          </div>
          <div className={`p-3 rounded-lg ${
            attackData.securityFeatures?.hasMultisig 
              ? 'bg-emerald-100 border border-emerald-300' 
              : 'bg-red-100 border border-red-300'
          }`}>
            <div className="flex items-center gap-2 mb-1">
              {attackData.securityFeatures?.hasMultisig ? '✅' : '❌'}
              <span className="font-medium">Multisig</span>
            </div>
            <div className="text-xs text-slate-600">
              {attackData.securityFeatures?.hasMultisig 
                ? `${attackData.securityFeatures?.multisigThreshold ?? 0}/X threshold` 
                : 'Not implemented'}
            </div>
          </div>
          <div className="p-3 rounded-lg bg-blue-100 border border-blue-300">
            <div className="flex items-center gap-2 mb-1">
              🔮
              <span className="font-medium">Oracle</span>
            </div>
            <div className="text-xs text-slate-600 capitalize">
              {attackData.securityFeatures?.oracleType ?? 'Unknown'}
            </div>
          </div>
          <div className="p-3 rounded-lg bg-slate-100 border border-slate-300">
            <div className="flex items-center gap-2 mb-1">
              💰
              <span className="font-medium">Market Cap</span>
            </div>
            <div className="text-xs text-slate-600">
              ${((attackData.marketCap ?? 0) / 1_000_000).toFixed(1)}M
            </div>
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="flex flex-wrap gap-2">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setSelectedCategory(cat)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${
              selectedCategory === cat
                ? 'bg-slate-800 text-white'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
            }`}
          >
            {cat === 'all' ? '📋 All Scenarios' : `${categoryIcons[cat] || '🔹'} ${categoryNames[cat] || cat}`}
          </button>
        ))}
      </div>

      {/* Attack Scenarios List */}
      <div className="space-y-4">
        {filteredScenarios.map((scenario, idx) => (
          <AttackScenarioCard key={idx} scenario={scenario} />
        ))}
        
        {filteredScenarios.length === 0 && (
          <div className="text-center py-8 text-slate-400">
            <div className="text-4xl mb-3">✅</div>
            <p>No scenarios in this category</p>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {attackData.recommendations && attackData.recommendations.length > 0 && (
        <div className="bg-gradient-to-br from-indigo-50 to-purple-50 rounded-xl border border-indigo-200 p-5">
          <h3 className="font-bold text-indigo-900 mb-4 flex items-center gap-2">
            🛡️ Security Recommendations
          </h3>
          <ul className="space-y-3">
            {attackData.recommendations.map((rec, idx) => (
              <li key={idx} className="flex items-start gap-3 text-sm text-indigo-800 bg-white/60 rounded-lg p-3">
                <span className="text-indigo-500 mt-0.5">→</span>
                <span>{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Interpretation Guide */}
      <div className="bg-slate-50 rounded-xl p-5">
        <h3 className="font-semibold text-slate-800 mb-4">📖 Attack Analysis Guide</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Vulnerability Score</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• <span className="text-emerald-600">0-30:</span> Well protected</li>
              <li>• <span className="text-amber-600">30-50:</span> Moderate risk</li>
              <li>• <span className="text-orange-600">50-70:</span> High exposure</li>
              <li>• <span className="text-red-600">70+:</span> Critical vulnerabilities</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Attack Categories</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• ⚡ Flash Loan: Borrow-attack-repay</li>
              <li>• 🥪 Sandwich: Front/back-running</li>
              <li>• 🔄 MEV: Validator extraction</li>
              <li>• 🔮 Oracle: Price manipulation</li>
            </ul>
          </div>
          <div>
            <h4 className="font-medium text-slate-700 mb-2">Key Protections</h4>
            <ul className="space-y-1 text-slate-500">
              <li>• 48-72h timelock for governance</li>
              <li>• 3/5+ multisig for admin</li>
              <li>• Chainlink/Pyth oracles</li>
              <li>• Circuit breakers</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

function AttackScenarioCard({ scenario }: { scenario: AttackScenarioDetail }) {
  const [expanded, setExpanded] = useState(false);

  const severityColors: Record<string, string> = {
    low: 'bg-emerald-100 text-emerald-700 border-emerald-300',
    medium: 'bg-amber-100 text-amber-700 border-amber-300',
    high: 'bg-orange-100 text-orange-700 border-orange-300',
    critical: 'bg-red-100 text-red-700 border-red-300',
  };

  const categoryIcons: Record<string, string> = {
    flash_loan: '⚡',
    sandwich: '🥪',
    mev: '🔄',
    rug_pull: '🚨',
    oracle: '🔮',
    governance: '🏛️',
  };

  return (
    <div className={`rounded-xl border overflow-hidden transition-all ${
      scenario.severity === 'critical' ? 'border-red-300 bg-red-50' :
      scenario.severity === 'high' ? 'border-orange-300 bg-orange-50' :
      scenario.severity === 'medium' ? 'border-amber-300 bg-amber-50' :
      'border-slate-200 bg-white'
    }`}>
      <div 
        className="p-4 cursor-pointer"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{categoryIcons[scenario.category] || '🔹'}</span>
            <div>
              <h4 className="font-semibold text-slate-800">{scenario.name}</h4>
              <p className="text-sm text-slate-600">{scenario.description}</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <span className={`px-3 py-1 rounded-full text-xs font-bold border ${
              severityColors[scenario.severity] || severityColors.low
            }`}>
              {(scenario.severity ?? 'low').toUpperCase()}
            </span>
            <span className="text-slate-400">{expanded ? '▲' : '▼'}</span>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="flex gap-4 mt-3 text-sm">
          <div>
            <span className="text-slate-500">Loss: </span>
            <span className={`font-bold ${
              (scenario.potentialLossUsd ?? 0) > 100000 ? 'text-red-600' : 'text-slate-700'
            }`}>
              ${((scenario.potentialLossUsd ?? 0) / 1000).toFixed(0)}K
            </span>
          </div>
          <div>
            <span className="text-slate-500">Probability: </span>
            <span className="font-bold text-slate-700">{((scenario.probability ?? 0) * 100).toFixed(1)}%</span>
          </div>
          <div>
            <span className="text-slate-500">Mitigation: </span>
            <span className={`font-bold ${
              (scenario.mitigationEffectiveness ?? 0) >= 70 ? 'text-emerald-600' :
              (scenario.mitigationEffectiveness ?? 0) >= 40 ? 'text-amber-600' : 'text-red-600'
            }`}>
              {(scenario.mitigationEffectiveness ?? 0).toFixed(0)}%
            </span>
          </div>
        </div>
      </div>

      {/* Expanded Details */}
      {expanded && (
        <div className="border-t border-slate-200 p-4 bg-white/80">
          <div className="mb-4">
            <h5 className="font-medium text-slate-700 mb-2">Attack Vector</h5>
            <p className="text-sm text-slate-600 bg-slate-50 p-3 rounded-lg">
              {scenario.attackVector || 'Not specified'}
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="text-slate-500">Potential Loss</div>
              <div className="font-bold text-red-600">
                ${((scenario.potentialLossUsd ?? 0) / 1000).toFixed(0)}K
              </div>
              <div className="text-xs text-slate-400">
                {(scenario.potentialLossPercent ?? 0).toFixed(2)}% of MC
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="text-slate-500">Recovery Time</div>
              <div className="font-bold text-slate-700">
                {scenario.recoveryTimeDays ?? 0} days
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="text-slate-500">Required Capital</div>
              <div className="font-bold text-slate-700">
                {(scenario.requiredCapital ?? 0) === 0 
                  ? 'None (Flash Loan)' 
                  : `$${((scenario.requiredCapital ?? 0) / 1000).toFixed(0)}K`}
              </div>
            </div>
            <div className="p-3 bg-slate-50 rounded-lg">
              <div className="text-slate-500">Complexity</div>
              <div className="font-bold text-slate-700 capitalize">
                {scenario.complexity ?? 'Medium'}
              </div>
            </div>
          </div>

          {/* Mitigation Progress */}
          <div className="mt-4">
            <div className="flex justify-between text-sm mb-1">
              <span className="text-slate-600">Mitigation Effectiveness</span>
              <span className={`font-bold ${
                (scenario.mitigationEffectiveness ?? 0) >= 70 ? 'text-emerald-600' :
                (scenario.mitigationEffectiveness ?? 0) >= 40 ? 'text-amber-600' : 'text-red-600'
              }`}>
                {(scenario.mitigationEffectiveness ?? 0).toFixed(0)}%
              </span>
            </div>
            <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${
                  (scenario.mitigationEffectiveness ?? 0) >= 70 ? 'bg-emerald-400' :
                  (scenario.mitigationEffectiveness ?? 0) >= 40 ? 'bg-amber-400' : 'bg-red-400'
                }`}
                style={{ width: `${scenario.mitigationEffectiveness ?? 0}%` }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

