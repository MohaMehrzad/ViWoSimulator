'use client';

import { useState, useEffect } from 'react';
import { useSimulation } from '@/hooks/useSimulation';
import { ParameterControls } from '@/components/controls/ParameterControls';
import { SimulationDashboard } from '@/components/simulation/SimulationDashboard';
import { 
  ModuleNavigation, 
  OverviewSection,
  IdentitySection,
  ContentSection,
  CommunitySection,
  AdvertisingSection,
  MessagingSection,
  ExchangeSection,
  RewardsSection,
  RecaptureSection,
  LiquiditySection,
  StakingSection,
  VelocitySection,
  SummarySection
} from '@/components/modules';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { ExportButtons } from '@/components/simulation/ExportButtons';

export default function Home() {
  const simulation = useSimulation();
  const [activeSection, setActiveSection] = useState('overview');

  // Auto-run deterministic simulation when parameters change
  // Always run deterministic to keep baseline results fresh for all simulation types
  useEffect(() => {
    const timer = setTimeout(() => {
      simulation.runDeterministic().catch(console.error);
    }, 300);
    return () => clearTimeout(timer);
  }, [simulation.parameters, simulation.runDeterministic]);

  return (
    <div className="container mx-auto px-3 py-6 max-w-7xl">
      <div className="bg-white rounded-3xl shadow-lg border border-gray-200 overflow-hidden">
        {/* Header */}
        <header className="bg-gradient-to-r from-gray-900 to-gray-800 text-white p-6 relative overflow-hidden">
          <div className="absolute inset-0 opacity-10">
            <svg className="w-full h-full" viewBox="0 0 60 60">
              <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
                <path d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4z" fill="currentColor" />
              </pattern>
              <rect width="100%" height="100%" fill="url(#grid)" />
            </svg>
          </div>
          
          <div className="relative z-10">
            <h1 className="text-3xl font-extrabold tracking-tight flex items-center gap-3">
              <span className="text-2xl">◆</span>
              ViWO Protocol - Token Economy Simulator
            </h1>
            <p className="text-gray-300 mt-1">
              Interactive Economics Analysis with Monte Carlo & Agent-Based Modeling
            </p>

            {/* Header Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3 mt-6">
              <HeaderStat 
                label="Revenue Modules" 
                value={getEnabledModuleCount(simulation.parameters)} 
              />
              <HeaderStat 
                label="M1 Revenue" 
                value={simulation.activeResult ? formatCurrency(simulation.activeResult.totals.revenue) : '$0'} 
              />
              <HeaderStat 
                label="M1 Profit" 
                value={simulation.activeResult ? formatCurrency(simulation.activeResult.totals.profit) : '$0'}
                valueColor={simulation.activeResult && simulation.activeResult.totals.profit >= 0 ? 'text-emerald-400' : 'text-red-400'}
              />
              <HeaderStat 
                label="Margin" 
                value={simulation.activeResult?.totals?.margin != null ? `${simulation.activeResult.totals.margin.toFixed(1)}%` : '0%'} 
              />
              <HeaderStat 
                label="Recapture" 
                value={simulation.activeResult?.recapture?.recaptureRate != null ? `${simulation.activeResult.recapture.recaptureRate.toFixed(1)}%` : '0%'} 
              />
              <HeaderStat 
                label="Liquidity Health" 
                value={simulation.activeResult?.liquidity?.healthScore != null ? `${simulation.activeResult.liquidity.healthScore.toFixed(0)}%` : '0%'}
                valueColor={simulation.activeResult?.liquidity?.healthScore && simulation.activeResult.liquidity.healthScore >= 70 ? 'text-emerald-400' : 'text-amber-400'}
              />
              <HeaderStat 
                label="Staking APY" 
                value={simulation.activeResult?.staking?.stakingApy != null ? `${simulation.activeResult.staking.stakingApy.toFixed(1)}%` : '10%'} 
              />
              <HeaderStat 
                label="Daily Rewards" 
                value={simulation.activeResult?.rewards?.dailyRewardPool != null ? `${formatNumber(simulation.activeResult.rewards.dailyRewardPool)} VC` : '0 VC'} 
              />
            </div>
          </div>
        </header>

        {/* Controls Section */}
        <ParameterControls 
          parameters={simulation.parameters}
          onUpdateParameter={simulation.updateParameter}
          onUpdateParameters={simulation.updateParameters}
          onReset={simulation.resetParameters}
          onLoadPreset={simulation.loadPreset}
        />

        {/* Export Buttons */}
        <div className="bg-gray-800 px-6 py-4 border-b border-gray-700">
          <ExportButtons
            parameters={simulation.parameters}
            result={simulation.activeResult}
            onImportParameters={simulation.updateParameters}
          />
        </div>

        {/* Navigation */}
        <ModuleNavigation 
          activeSection={activeSection}
          onSectionChange={setActiveSection}
          enabledModules={{
            advertising: simulation.parameters.enableAdvertising,
            messaging: simulation.parameters.enableMessaging,
            community: simulation.parameters.enableCommunity,
            exchange: simulation.parameters.enableExchange,
          }}
        />

        {/* Main Content */}
        <main className="p-8">
          {/* Simulation Type Tabs */}
          <SimulationDashboard 
            simulation={simulation}
            activeSection={activeSection}
          />

          {/* Module Sections */}
          {activeSection === 'overview' && simulation.activeResult && (
            <OverviewSection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'identity' && simulation.activeResult && (
            <IdentitySection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'content' && simulation.activeResult && (
            <ContentSection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'community' && simulation.activeResult && (
            <CommunitySection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'advertising' && simulation.activeResult && (
            <AdvertisingSection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'messaging' && simulation.activeResult && (
            <MessagingSection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'exchange' && simulation.activeResult && (
            <ExchangeSection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'rewards' && simulation.activeResult && (
            <RewardsSection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'recapture' && simulation.activeResult && (
            <RecaptureSection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'liquidity' && simulation.activeResult && (
            <LiquiditySection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'staking' && simulation.activeResult && (
            <StakingSection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'velocity' && simulation.activeResult && (
            <VelocitySection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
          {activeSection === 'summary' && simulation.activeResult && (
            <SummarySection result={simulation.activeResult} parameters={simulation.parameters} />
          )}
        </main>
      </div>
    </div>
  );
}

function HeaderStat({ 
  label, 
  value, 
  valueColor = 'text-white' 
}: { 
  label: string; 
  value: string; 
  valueColor?: string;
}) {
  return (
    <div className="bg-white/10 backdrop-blur-sm border border-white/20 rounded-xl p-3 text-center">
      <div className={`text-xl font-bold ${valueColor}`}>{value}</div>
      <div className="text-xs text-gray-300 uppercase tracking-wide font-semibold mt-1">
        {label}
      </div>
    </div>
  );
}

function getEnabledModuleCount(params: { enableAdvertising: boolean; enableMessaging: boolean; enableCommunity: boolean; enableExchange: boolean }) {
  let count = 2; // Identity and Content are always enabled
  if (params.enableAdvertising) count++;
  if (params.enableMessaging) count++;
  if (params.enableCommunity) count++;
  if (params.enableExchange) count++;
  return count.toString();
}

