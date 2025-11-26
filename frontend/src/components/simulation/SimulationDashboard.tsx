'use client';

import { useState } from 'react';
import { SimulationType, PercentileKey, SimulationResult, MonteCarloResult, AgentBasedResult } from '@/types/simulation';
import { formatNumber } from '@/lib/utils';

interface SimulationDashboardProps {
  simulation: {
    simulationType: SimulationType;
    isLoading: boolean;
    error: string | null;
    progress: number;
    result: SimulationResult | null;
    monteCarloResult: MonteCarloResult | null;
    agentBasedResult: AgentBasedResult | null;
    selectedPercentile: PercentileKey;
    setSimulationType: (type: SimulationType) => void;
    setSelectedPercentile: (percentile: PercentileKey) => void;
    runDeterministic: () => Promise<SimulationResult | void>;
    runMonteCarlo: (iterations: number) => Promise<MonteCarloResult | void>;
    runAgentBased: (agentCount: number, duration: number) => Promise<AgentBasedResult | void>;
    cancelSimulation: () => void;
  };
  activeSection: string;
}

export function SimulationDashboard({ simulation, activeSection }: SimulationDashboardProps) {
  const [mcIterations, setMcIterations] = useState(1000);
  const [abAgentCount, setAbAgentCount] = useState(1000);
  const [abDuration, setAbDuration] = useState(12);

  const handleRunMonteCarlo = () => {
    simulation.runMonteCarlo(mcIterations);
  };

  const handleRunAgentBased = () => {
    simulation.runAgentBased(abAgentCount, abDuration);
  };

  return (
    <div className="mb-8">
      {/* Simulation Type Tabs */}
      <div className="flex gap-2 mb-6">
        <SimulationTab
          active={simulation.simulationType === 'deterministic'}
          onClick={() => simulation.setSimulationType('deterministic')}
          icon="🎯"
          label="Deterministic"
          description="Real-time calculations"
        />
        <SimulationTab
          active={simulation.simulationType === 'monte_carlo'}
          onClick={() => simulation.setSimulationType('monte_carlo')}
          icon="🎲"
          label="Monte Carlo"
          description="Probability analysis"
        />
        <SimulationTab
          active={simulation.simulationType === 'agent_based'}
          onClick={() => simulation.setSimulationType('agent_based')}
          icon="🤖"
          label="Agent-Based"
          description="User behavior simulation"
        />
      </div>

      {/* Simulation Controls */}
      {simulation.simulationType === 'monte_carlo' && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 border border-purple-200 rounded-xl p-6 mb-6">
          <h3 className="font-bold text-lg text-purple-900 mb-4">
            🎲 Monte Carlo Simulation
          </h3>
          <p className="text-purple-700 text-sm mb-4">
            Run thousands of simulations with randomized parameters to understand the 
            probability distribution of outcomes.
          </p>
          
          <div className="flex items-end gap-4">
            <div>
              <label className="block text-sm font-semibold text-purple-800 mb-1">
                Iterations
              </label>
              <input
                type="number"
                value={mcIterations}
                onChange={(e) => setMcIterations(parseInt(e.target.value) || 100)}
                min={100}
                max={10000}
                step={100}
                className="px-3 py-2 border border-purple-300 rounded-lg w-32 font-semibold"
              />
            </div>
            
            <button
              onClick={handleRunMonteCarlo}
              disabled={simulation.isLoading}
              className="px-6 py-2 bg-purple-600 text-white rounded-lg font-semibold 
                       hover:bg-purple-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {simulation.isLoading ? 'Running...' : 'Run Simulation'}
            </button>
            
            {simulation.isLoading && (
              <button
                onClick={simulation.cancelSimulation}
                className="px-4 py-2 bg-red-500 text-white rounded-lg font-semibold 
                         hover:bg-red-600 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
          
          {simulation.isLoading && (
            <div className="mt-4">
              <div className="flex justify-between text-sm text-purple-700 mb-1">
                <span>Progress</span>
                <span>{simulation.progress.toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-purple-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-600 transition-all duration-300"
                  style={{ width: `${simulation.progress}%` }}
                />
              </div>
            </div>
          )}

          {simulation.monteCarloResult && (
            <MonteCarloResults 
              result={simulation.monteCarloResult} 
              selectedPercentile={simulation.selectedPercentile}
              onSelectPercentile={simulation.setSelectedPercentile}
            />
          )}
        </div>
      )}

      {simulation.simulationType === 'agent_based' && (
        <div className="bg-gradient-to-r from-cyan-50 to-teal-50 border border-cyan-200 rounded-xl p-6 mb-6">
          <h3 className="font-bold text-lg text-cyan-900 mb-4">
            🤖 Agent-Based Simulation
          </h3>
          <p className="text-cyan-700 text-sm mb-4">
            Simulate individual user behaviors including creators, consumers, whales, and bots 
            to model realistic market dynamics.
          </p>
          
          <div className="flex items-end gap-4 flex-wrap">
            <div>
              <label className="block text-sm font-semibold text-cyan-800 mb-1">
                Agent Count
              </label>
              <input
                type="number"
                value={abAgentCount}
                onChange={(e) => setAbAgentCount(parseInt(e.target.value) || 100)}
                min={100}
                max={10000}
                step={100}
                className="px-3 py-2 border border-cyan-300 rounded-lg w-32 font-semibold"
              />
            </div>
            
            <div>
              <label className="block text-sm font-semibold text-cyan-800 mb-1">
                Duration (Months)
              </label>
              <input
                type="number"
                value={abDuration}
                onChange={(e) => setAbDuration(parseInt(e.target.value) || 1)}
                min={1}
                max={60}
                className="px-3 py-2 border border-cyan-300 rounded-lg w-24 font-semibold"
              />
            </div>
            
            <button
              onClick={handleRunAgentBased}
              disabled={simulation.isLoading}
              className="px-6 py-2 bg-cyan-600 text-white rounded-lg font-semibold 
                       hover:bg-cyan-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {simulation.isLoading ? 'Running...' : 'Run Simulation'}
            </button>
            
            {simulation.isLoading && (
              <button
                onClick={simulation.cancelSimulation}
                className="px-4 py-2 bg-red-500 text-white rounded-lg font-semibold 
                         hover:bg-red-600 transition-colors"
              >
                Cancel
              </button>
            )}
          </div>
          
          {simulation.isLoading && (
            <div className="mt-4">
              <div className="flex justify-between text-sm text-cyan-700 mb-1">
                <span>Progress</span>
                <span>{simulation.progress.toFixed(1)}%</span>
              </div>
              <div className="h-2 bg-cyan-200 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-cyan-600 transition-all duration-300"
                  style={{ width: `${simulation.progress}%` }}
                />
              </div>
            </div>
          )}

          {simulation.agentBasedResult && (
            <AgentBasedResults result={simulation.agentBasedResult} />
          )}
        </div>
      )}

      {/* Error Display */}
      {simulation.error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 text-red-700">
            <span>❌</span>
            <strong>Error:</strong> {simulation.error}
          </div>
        </div>
      )}
    </div>
  );
}

function SimulationTab({
  active,
  onClick,
  icon,
  label,
  description,
}: {
  active: boolean;
  onClick: () => void;
  icon: string;
  label: string;
  description: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 p-4 rounded-xl border-2 transition-all text-left
                 ${active 
                   ? 'border-gray-900 bg-gray-900 text-white' 
                   : 'border-gray-200 bg-white text-gray-900 hover:border-gray-300'
                 }`}
    >
      <div className="flex items-center gap-2 font-bold">
        <span>{icon}</span>
        {label}
      </div>
      <div className={`text-xs mt-1 ${active ? 'text-gray-300' : 'text-gray-500'}`}>
        {description}
      </div>
    </button>
  );
}

function MonteCarloResults({ 
  result, 
  selectedPercentile,
  onSelectPercentile 
}: { 
  result: any;
  selectedPercentile: PercentileKey;
  onSelectPercentile: (percentile: PercentileKey) => void;
}) {
  if (!result) return null;

  return (
    <div className="mt-6 pt-6 border-t border-purple-200">
      <div className="flex items-center justify-between mb-4">
        <h4 className="font-bold text-purple-900">Results ({result.iterations} iterations)</h4>
        <div className="text-sm text-purple-700">
          Click a scenario to view in modules below
        </div>
      </div>
      
      <div className="grid grid-cols-3 gap-4 mb-4">
        <ResultCard
          label="5th Percentile (Pessimistic)"
          revenue={result.percentiles.p5.totals.revenue}
          profit={result.percentiles.p5.totals.profit}
          color="red"
          selected={selectedPercentile === 'p5'}
          onClick={() => onSelectPercentile('p5')}
        />
        <ResultCard
          label="50th Percentile (Median)"
          revenue={result.percentiles.p50.totals.revenue}
          profit={result.percentiles.p50.totals.profit}
          color="amber"
          selected={selectedPercentile === 'p50'}
          onClick={() => onSelectPercentile('p50')}
        />
        <ResultCard
          label="95th Percentile (Optimistic)"
          revenue={result.percentiles.p95.totals.revenue}
          profit={result.percentiles.p95.totals.profit}
          color="emerald"
          selected={selectedPercentile === 'p95'}
          onClick={() => onSelectPercentile('p95')}
        />
      </div>

      <div className="bg-white rounded-lg p-4">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Mean Revenue</div>
            <div className="font-bold">${formatNumber(result.statistics.mean.revenue)}</div>
            <div className="text-gray-500 text-xs">±${formatNumber(result.statistics.std.revenue)}</div>
          </div>
          <div>
            <div className="text-gray-600">Mean Profit</div>
            <div className="font-bold">${formatNumber(result.statistics.mean.profit)}</div>
            <div className="text-gray-500 text-xs">±${formatNumber(result.statistics.std.profit)}</div>
          </div>
          <div>
            <div className="text-gray-600">Mean Recapture</div>
            <div className="font-bold">{result.statistics.mean.recaptureRate.toFixed(1)}%</div>
            <div className="text-gray-500 text-xs">±{result.statistics.std.recaptureRate.toFixed(1)}%</div>
          </div>
        </div>
      </div>
    </div>
  );
}

function AgentBasedResults({ result }: { result: any }) {
  if (!result) return null;

  // Safely access nested properties with defaults
  const agentBreakdown = result.agentBreakdown || {};
  const systemMetrics = result.systemMetrics || {};

  return (
    <div className="mt-6 pt-6 border-t border-cyan-200">
      <h4 className="font-bold text-cyan-900 mb-4">Simulation Results ({result.totalAgents || 0} agents)</h4>
      
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div className="bg-white rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-cyan-700">
            {agentBreakdown.creator || 0}
          </div>
          <div className="text-xs text-gray-600">Creators</div>
        </div>
        <div className="bg-white rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-cyan-600">
            {agentBreakdown.consumer || 0}
          </div>
          <div className="text-xs text-gray-600">Consumers</div>
        </div>
        <div className="bg-white rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-purple-600">
            {agentBreakdown.whale || 0}
          </div>
          <div className="text-xs text-gray-600">Whales</div>
        </div>
        <div className="bg-white rounded-lg p-3 text-center">
          <div className="text-2xl font-bold text-red-600">
            {result.flaggedBots || 0}
          </div>
          <div className="text-xs text-gray-600">Flagged Bots</div>
        </div>
      </div>

      <div className="bg-white rounded-lg p-4">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <div className="text-gray-600">Total Rewards Distributed</div>
            <div className="font-bold">{formatNumber(systemMetrics.totalRewardsDistributed || 0)} VCoin</div>
          </div>
          <div>
            <div className="text-gray-600">Total Recaptured</div>
            <div className="font-bold">{formatNumber(systemMetrics.totalRecaptured || 0)} VCoin</div>
          </div>
          <div>
            <div className="text-gray-600">Net Circulation</div>
            <div className="font-bold">{formatNumber(systemMetrics.netCirculation || 0)} VCoin</div>
          </div>
        </div>
        
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="text-gray-600 mb-2">Market Dynamics</div>
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div>
              <span className="text-emerald-600 font-bold">
                Buy: {(result.marketDynamics?.buyPressure || 0).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className="text-red-600 font-bold">
                Sell: {(result.marketDynamics?.sellPressure || 0).toFixed(1)}%
              </span>
            </div>
            <div>
              <span className={(result.marketDynamics?.priceImpact || 0) >= 0 ? 'text-emerald-600' : 'text-red-600'}>
                Price Impact: {(result.marketDynamics?.priceImpact || 0) >= 0 ? '+' : ''}
                {(result.marketDynamics?.priceImpact || 0).toFixed(2)}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function ResultCard({
  label,
  revenue,
  profit,
  color,
  selected = false,
  onClick,
}: {
  label: string;
  revenue: number;
  profit: number;
  color: 'red' | 'amber' | 'emerald';
  selected?: boolean;
  onClick?: () => void;
}) {
  const colorClasses = {
    red: selected ? 'bg-red-100 border-red-500 ring-2 ring-red-300' : 'bg-red-50 border-red-200 hover:border-red-400',
    amber: selected ? 'bg-amber-100 border-amber-500 ring-2 ring-amber-300' : 'bg-amber-50 border-amber-200 hover:border-amber-400',
    emerald: selected ? 'bg-emerald-100 border-emerald-500 ring-2 ring-emerald-300' : 'bg-emerald-50 border-emerald-200 hover:border-emerald-400',
  };

  return (
    <button 
      onClick={onClick}
      className={`${colorClasses[color]} border rounded-lg p-3 text-left transition-all cursor-pointer w-full`}
    >
      <div className="text-xs text-gray-600 mb-2 flex items-center justify-between">
        <span>{label}</span>
        {selected && <span className="text-purple-600 font-semibold">Active</span>}
      </div>
      <div className="font-bold">${formatNumber(revenue)}</div>
      <div className={`text-sm ${profit >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
        Profit: ${formatNumber(profit)}
      </div>
    </button>
  );
}

