'use client';

import { useState, useEffect, useMemo } from 'react';
import { useSimulation } from '@/hooks/useSimulation';
import { Header, PageTab } from '@/components/Header';
import { ParameterControls } from '@/components/controls/ParameterControls';
import { SimulationDashboard } from '@/components/simulation/SimulationDashboard';
import { GROWTH_SCENARIOS, MARKET_CONDITIONS } from '@/lib/constants';
import { 
  ModuleNavigation, 
  OverviewSection,
  Year1Overview,
  Year5Overview,
  TokenomicsSection,
  IdentitySection,
  ContentSection,
  AdvertisingSection,
  ExchangeSection,
  RewardsSection,
  RecaptureSection,
  LiquiditySection,
  StakingSection,
  GovernanceSection,
  VelocitySection,
  TokenMetricsSection,
  FutureModulesSection,
  SummarySection,
  PreLaunchSection,
  TokenUnlocksSection,
  FiveAPolicySection,
} from '@/components/modules';
import { calculate5YearProjections } from '@/components/modules/Year5Overview';
import { formatNumber, formatCurrency } from '@/lib/utils';
import { ExportButtons } from '@/components/simulation/ExportButtons';
import { SaveDefaultButton } from '@/components/SaveDefaultButton';

export default function Home() {
  const simulation = useSimulation();
  const [activeTab, setActiveTab] = useState<PageTab>('year1');
  const [activeSection, setActiveSection] = useState('overview');

  // Calculate 5-year projection stats for header (uses same function as Year5Overview)
  const fiveYearStats = useMemo(() => {
    if (!simulation.activeResult) return null;
    
    const scenario = (simulation.parameters.growthScenario || 'base') as keyof typeof GROWTH_SCENARIOS;
    const marketCondition = (simulation.parameters.marketCondition || 'bull') as keyof typeof MARKET_CONDITIONS;
    const scenarioConfig = GROWTH_SCENARIOS[scenario];
    const marketConfig = MARKET_CONDITIONS[marketCondition];
    
    const projections = calculate5YearProjections(
      simulation.activeResult,
      scenarioConfig,
      marketConfig,
      simulation.parameters.tokenPrice,
      simulation.parameters
    );
    
    const totalRevenue = projections.reduce((s, y) => s + y.totalRevenue, 0);
    const totalProfit = projections.reduce((s, y) => s + y.totalProfit, 0);
    const endUsers = projections[4].endUsers;
    const tokenPriceMultiplier = projections[4].tokenPriceEnd / simulation.parameters.tokenPrice;
    
    return {
      totalRevenue,
      totalProfit,
      endUsers,
      tokenPriceMultiplier,
      treasury: totalProfit * 0.15,
    };
  }, [simulation.activeResult, simulation.parameters]);

  // Reset active section and auto-toggle future modules when switching tabs
  useEffect(() => {
    if (activeTab === 'year1') {
      // Default to overview for Year 1
      if (!YEAR1_SECTIONS.includes(activeSection)) {
        setActiveSection('overview');
      }
      // Disable future modules when switching to Year 1
      simulation.updateParameters({
        enableVchain: false,
        enableMarketplace: false,
        enableBusinessHub: false,
        enableCrossPlatform: false,
      });
    } else {
      // Default to overview for 5-Year
      if (!YEAR5_SECTIONS.includes(activeSection)) {
        setActiveSection('overview');
      }
      // Enable future modules when switching to Year 5
      simulation.updateParameters({
        enableVchain: true,
        enableMarketplace: true,
        enableBusinessHub: true,
        enableCrossPlatform: true,
        useGrowthScenarios: true, // Also enable growth scenarios for 5-year view
      });
    }
  }, [activeTab]);

  // Auto-run deterministic simulation when parameters change or after initialization
  useEffect(() => {
    // Don't run until saved defaults are loaded (or attempted to load)
    if (!simulation.isInitialized) {
      return;
    }
    
    const timer = setTimeout(() => {
      simulation.runDeterministic().catch(console.error);
    }, 300);
    return () => clearTimeout(timer);
  }, [simulation.parameters, simulation.isInitialized, simulation.runDeterministic]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-100 to-indigo-100">
      {/* Persistent Header with Tab Navigation */}
      <Header activeTab={activeTab} onTabChange={setActiveTab} />

      <div className="container mx-auto px-3 py-6 max-w-7xl">
        <div className="bg-white rounded-3xl shadow-lg border border-gray-200 overflow-hidden">
          {/* Stats Bar */}
          <div className="bg-gradient-to-r from-gray-900 to-gray-800 text-white p-4 relative overflow-hidden">
            <div className="absolute inset-0 opacity-10">
              <svg className="w-full h-full" viewBox="0 0 60 60">
                <pattern id="grid" width="60" height="60" patternUnits="userSpaceOnUse">
                  <path d="M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4z" fill="currentColor" />
                </pattern>
                <rect width="100%" height="100%" fill="url(#grid)" />
              </svg>
            </div>
            
            <div className="relative z-10">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">
                    {activeTab === 'year1' ? '📅' : '📈'}
                  </span>
                  <div>
                    <h2 className="text-xl font-bold">
                      {activeTab === 'year1' ? 'Year 1 Projections' : '5-Year Projections'}
                    </h2>
                    <p className="text-sm text-gray-400">
                      {activeTab === 'year1' 
                        ? 'First 12 months analysis with Monte Carlo & Agent-Based modeling' 
                        : 'Long-term growth scenarios with market cycle analysis'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Header Stats - Different for Year 1 vs 5-Year */}
              {activeTab === 'year1' ? (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
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
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
                  <HeaderStat 
                    label="Future Modules" 
                    value="4/4" 
                    valueColor="text-purple-400"
                  />
                  <HeaderStat 
                    label="5Y Revenue" 
                    value={fiveYearStats ? `$${(fiveYearStats.totalRevenue / 1000000).toFixed(2)}M` : '$0'} 
                  />
                  <HeaderStat 
                    label="5Y Profit" 
                    value={fiveYearStats ? `$${(fiveYearStats.totalProfit / 1000000).toFixed(2)}M` : '$0'}
                    valueColor="text-emerald-400"
                  />
                  <HeaderStat 
                    label="Y5 Users" 
                    value={fiveYearStats ? formatNumber(fiveYearStats.endUsers) : '0'} 
                  />
                  <HeaderStat 
                    label="Price Growth" 
                    value={fiveYearStats ? `${fiveYearStats.tokenPriceMultiplier.toFixed(1)}x` : '1.0x'}
                    valueColor="text-amber-400"
                  />
                  <HeaderStat 
                    label="Market Cycle" 
                    value="Bull → Bear"
                  />
                  <HeaderStat 
                    label="Treasury (5Y)" 
                    value={fiveYearStats ? `$${(fiveYearStats.treasury / 1000000).toFixed(2)}M` : '$0'} 
                    valueColor="text-emerald-400"
                  />
                  <HeaderStat 
                    label="Avg Margin" 
                    value="75%" 
                  />
                </div>
              )}
            </div>
          </div>

          {/* Parameter Controls */}
          <ParameterControls 
            parameters={simulation.parameters}
            onUpdateParameter={simulation.updateParameter}
            onUpdateParameters={simulation.updateParameters}
            onReset={simulation.resetParameters}
            onLoadPreset={simulation.loadPreset}
          />

          {/* Export Buttons */}
          <div className="bg-gray-800 px-6 py-4 border-t border-gray-700">
            <ExportButtons
              parameters={simulation.parameters}
              result={simulation.activeResult}
              onImportParameters={simulation.updateParameters}
            />
          </div>

          {/* Navigation - Section-specific based on active tab */}
          <ModuleNavigation 
            activeSection={activeSection}
            onSectionChange={setActiveSection}
            activeTab={activeTab}
            enabledModules={{
              advertising: simulation.parameters.enableAdvertising,
              exchange: simulation.parameters.enableExchange,
            }}
          />

          {/* Main Content */}
          <main className="p-8">
            {/* Simulation Type Tabs - Only show on Year 1 page */}
            {activeTab === 'year1' && (
              <SimulationDashboard 
                simulation={simulation}
                activeSection={activeSection}
              />
            )}

            {/* Year 1 Sections */}
            {activeTab === 'year1' && (
              <>
                {activeSection === 'overview' && simulation.activeResult && (
                  <Year1Overview result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'prelaunch' && simulation.activeResult && (
                  <PreLaunchSection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'identity' && simulation.activeResult && (
                  <IdentitySection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'content' && simulation.activeResult && (
                  <ContentSection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'advertising' && simulation.activeResult && (
                  <AdvertisingSection result={simulation.activeResult} parameters={simulation.parameters} />
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
                {activeSection === 'fiveA' && simulation.activeResult && (
                  <FiveAPolicySection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
              </>
            )}

            {/* 5-Year Sections */}
            {activeTab === 'year5' && (
              <>
                {activeSection === 'overview' && simulation.activeResult && (
                  <Year5Overview result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'prelaunch' && simulation.activeResult && (
                  <PreLaunchSection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'tokenomics' && (
                  <TokenomicsSection parameters={simulation.parameters} />
                )}
                {activeSection === 'token-unlocks' && simulation.activeResult && (
                  <TokenUnlocksSection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'governance' && simulation.activeResult && (
                  <GovernanceSection result={simulation.activeResult} />
                )}
                {activeSection === 'velocity' && simulation.activeResult && (
                  <VelocitySection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'token-metrics' && simulation.activeResult && (
                  <TokenMetricsSection result={simulation.activeResult} />
                )}
                {activeSection === 'future-modules' && simulation.activeResult && (
                  <FutureModulesSection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'summary' && simulation.activeResult && (
                  <SummarySection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
                {activeSection === 'fiveA' && simulation.activeResult && (
                  <FiveAPolicySection result={simulation.activeResult} parameters={simulation.parameters} />
                )}
              </>
            )}
          </main>
        </div>
      </div>

      {/* Floating Save Button */}
      <SaveDefaultButton 
        parameters={simulation.parameters}
        onLoadSavedDefaults={simulation.updateParameters}
      />
    </div>
  );
}

// Sections for Year 1 page
const YEAR1_SECTIONS = [
  'overview', 'prelaunch', 'identity', 'content', 'advertising', 'exchange', 
  'rewards', 'recapture', 'liquidity', 'staking'
];

// Sections for 5-Year page
const YEAR5_SECTIONS = [
  'overview', 'prelaunch', 'tokenomics', 'governance', 'velocity', 'token-metrics', 'future-modules', 'summary'
];

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

function getEnabledModuleCount(params: { enableAdvertising: boolean; enableExchange: boolean }) {
  let count = 2; // Identity and Content are always enabled
  if (params.enableAdvertising) count++;
  if (params.enableExchange) count++;
  return count.toString();
}
