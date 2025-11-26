'use client';

import React from 'react';
import { GrowthScenario, MarketCondition } from '@/types/simulation';
import { GROWTH_SCENARIOS, MARKET_CONDITIONS, GROWTH_SCENARIO_SUMMARY } from '@/lib/constants';

interface GrowthScenarioSelectorProps {
  scenario: GrowthScenario;
  marketCondition: MarketCondition;
  calculatedUsers: number;  // Calculated from marketing budget
  enableFomoEvents: boolean;
  useGrowthScenarios: boolean;
  onScenarioChange: (scenario: GrowthScenario) => void;
  onMarketConditionChange: (condition: MarketCondition) => void;
  onFomoEventsChange: (enabled: boolean) => void;
  onUseGrowthScenariosChange: (enabled: boolean) => void;
}

const SCENARIO_ICONS: Record<GrowthScenario, string> = {
  conservative: '🐢',
  base: '⚖️',
  bullish: '🚀',
};

const SCENARIO_COLORS: Record<GrowthScenario, { bg: string; border: string; text: string }> = {
  conservative: { bg: 'bg-blue-900/20', border: 'border-blue-500', text: 'text-blue-400' },
  base: { bg: 'bg-purple-900/20', border: 'border-purple-500', text: 'text-purple-400' },
  bullish: { bg: 'bg-emerald-900/20', border: 'border-emerald-500', text: 'text-emerald-400' },
};

const MARKET_ICONS: Record<MarketCondition, string> = {
  bear: '📉',
  neutral: '➡️',
  bull: '📈',
};

const MARKET_COLORS: Record<MarketCondition, { bg: string; text: string }> = {
  bear: { bg: 'bg-red-900/30', text: 'text-red-400' },
  neutral: { bg: 'bg-slate-700/50', text: 'text-slate-300' },
  bull: { bg: 'bg-green-900/30', text: 'text-green-400' },
};

export const GrowthScenarioSelector: React.FC<GrowthScenarioSelectorProps> = ({
  scenario,
  marketCondition,
  calculatedUsers,
  enableFomoEvents,
  useGrowthScenarios,
  onScenarioChange,
  onMarketConditionChange,
  onFomoEventsChange,
  onUseGrowthScenariosChange,
}) => {
  const selectedScenario = GROWTH_SCENARIOS[scenario];
  const selectedMarket = MARKET_CONDITIONS[marketCondition];
  
  // Calculate projected Month 1 users based on marketing users + scenario multipliers
  const scenarioMultiplier = selectedScenario.month1FomoMultiplier * selectedMarket.fomoMultiplier;
  const projectedMonth1Users = Math.round(calculatedUsers * scenarioMultiplier * 0.3);

  return (
    <div className="space-y-4">
      {/* Master Toggle */}
      <div className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg border border-slate-700">
        <div>
          <h4 className="text-sm font-semibold text-white">Growth Scenario Projections</h4>
          <p className="text-xs text-slate-400 mt-0.5">
            Use scenario-based growth instead of CAC-based calculations
          </p>
        </div>
        <button
          onClick={() => onUseGrowthScenariosChange(!useGrowthScenarios)}
          className={`relative w-12 h-6 rounded-full transition-colors ${
            useGrowthScenarios ? 'bg-emerald-500' : 'bg-slate-600'
          }`}
        >
          <span
            className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white transition-transform ${
              useGrowthScenarios ? 'translate-x-6' : 'translate-x-0'
            }`}
          />
        </button>
      </div>

      {useGrowthScenarios && (
        <>
          {/* Scenario Cards */}
          <div className="grid grid-cols-3 gap-2">
            {(['conservative', 'base', 'bullish'] as GrowthScenario[]).map((s) => {
              const config = GROWTH_SCENARIOS[s];
              const summary = GROWTH_SCENARIO_SUMMARY[s];
              const colors = SCENARIO_COLORS[s];
              const isSelected = scenario === s;

              return (
                <button
                  key={s}
                  onClick={() => onScenarioChange(s)}
                  className={`p-3 rounded-lg border-2 transition-all text-left ${
                    isSelected
                      ? `${colors.bg} ${colors.border}`
                      : 'bg-slate-800/30 border-slate-700 hover:border-slate-600'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">{SCENARIO_ICONS[s]}</span>
                    <span className={`font-semibold text-sm ${isSelected ? colors.text : 'text-slate-300'}`}>
                      {config.name}
                    </span>
                  </div>
                  <div className="space-y-1 text-xs">
                    <div className="flex justify-between">
                      <span className="text-slate-500">Month 1:</span>
                      <span className="text-slate-300">{summary.month1Users}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Month 12:</span>
                      <span className={isSelected ? colors.text : 'text-slate-300'}>{summary.month12Mau}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-500">Price:</span>
                      <span className="text-amber-400">{summary.tokenPriceChange}</span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>

          {/* Scenario Description */}
          <div className={`p-3 rounded-lg ${SCENARIO_COLORS[scenario].bg} border ${SCENARIO_COLORS[scenario].border}`}>
            <p className="text-xs text-slate-300">{selectedScenario.description}</p>
          </div>

          {/* Market Condition Toggle */}
          <div className="space-y-2">
            <label className="text-xs font-medium text-slate-400">Market Condition</label>
            <div className="grid grid-cols-3 gap-2">
              {(['bear', 'neutral', 'bull'] as MarketCondition[]).map((m) => {
                const config = MARKET_CONDITIONS[m];
                const colors = MARKET_COLORS[m];
                const isSelected = marketCondition === m;

                return (
                  <button
                    key={m}
                    onClick={() => onMarketConditionChange(m)}
                    className={`p-2 rounded-lg border transition-all ${
                      isSelected
                        ? `${colors.bg} border-slate-500 ${colors.text}`
                        : 'bg-slate-800/30 border-slate-700 text-slate-400 hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-center justify-center gap-1.5">
                      <span className="text-sm">{MARKET_ICONS[m]}</span>
                      <span className="text-xs font-medium">{config.name.split(' ')[0]}</span>
                    </div>
                    {isSelected && (
                      <div className="text-[10px] mt-1 opacity-75">
                        {config.growthMultiplier}x growth
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Market Condition Impact */}
          <div className="grid grid-cols-4 gap-2 text-xs">
            <div className="p-2 bg-slate-800/50 rounded text-center">
              <div className="text-slate-500 mb-1">Growth</div>
              <div className={MARKET_COLORS[marketCondition].text}>
                {selectedMarket.growthMultiplier}x
              </div>
            </div>
            <div className="p-2 bg-slate-800/50 rounded text-center">
              <div className="text-slate-500 mb-1">Retention</div>
              <div className={MARKET_COLORS[marketCondition].text}>
                {selectedMarket.retentionMultiplier}x
              </div>
            </div>
            <div className="p-2 bg-slate-800/50 rounded text-center">
              <div className="text-slate-500 mb-1">Price</div>
              <div className={MARKET_COLORS[marketCondition].text}>
                {selectedMarket.priceMultiplier}x
              </div>
            </div>
            <div className="p-2 bg-slate-800/50 rounded text-center">
              <div className="text-slate-500 mb-1">CAC</div>
              <div className={marketCondition === 'bull' ? 'text-green-400' : marketCondition === 'bear' ? 'text-red-400' : 'text-slate-300'}>
                {selectedMarket.cacMultiplier}x
              </div>
            </div>
          </div>

          {/* Base Users from Marketing Budget */}
          <div className="p-3 bg-slate-800/50 rounded-lg border border-slate-600">
            <div className="flex justify-between items-center mb-2">
              <span className="text-xs font-medium text-slate-400">Base Users (from Marketing)</span>
              <span className="text-lg font-bold text-blue-400">{calculatedUsers.toLocaleString()}</span>
            </div>
            <p className="text-[10px] text-slate-500">
              Calculated from your marketing budget and CAC settings. Growth scenarios apply multipliers to this base.
            </p>
          </div>

          {/* FOMO Events Toggle */}
          <div className="flex items-center justify-between p-2 bg-slate-800/30 rounded-lg">
            <div>
              <span className="text-xs font-medium text-slate-300">FOMO Events</span>
              <span className="text-xs text-slate-500 ml-2">
                ({selectedScenario.fomoEvents.length} scheduled)
              </span>
            </div>
            <button
              onClick={() => onFomoEventsChange(!enableFomoEvents)}
              className={`relative w-10 h-5 rounded-full transition-colors ${
                enableFomoEvents ? 'bg-amber-500' : 'bg-slate-600'
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-4 h-4 rounded-full bg-white transition-transform ${
                  enableFomoEvents ? 'translate-x-5' : 'translate-x-0'
                }`}
              />
            </button>
          </div>

          {/* Scenario Key Metrics */}
          <div className="p-3 bg-slate-800/30 rounded-lg border border-slate-700">
            <h5 className="text-xs font-semibold text-slate-400 mb-2">Scenario Metrics</h5>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="flex justify-between">
                <span className="text-slate-500">Waitlist Conversion:</span>
                <span className="text-emerald-400">{(selectedScenario.waitlistConversionRate * 100).toFixed(0)}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Month 1 FOMO:</span>
                <span className="text-amber-400">{selectedScenario.month1FomoMultiplier}x</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Viral Coefficient:</span>
                <span className="text-purple-400">{selectedScenario.viralCoefficient}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-500">Month 1 Retention:</span>
                <span className="text-blue-400">{(selectedScenario.month1Retention * 100).toFixed(0)}%</span>
              </div>
            </div>
          </div>

          {/* Projected Outcomes */}
          <div className="p-3 bg-gradient-to-br from-emerald-900/20 to-purple-900/20 rounded-lg border border-emerald-800/30">
            <h5 className="text-xs font-semibold text-emerald-400 mb-2">📊 Projected Outcomes (12 months)</h5>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <div className="text-xs text-slate-500">Month 1 Users</div>
                <div className="text-lg font-bold text-white">
                  {projectedMonth1Users.toLocaleString()}
                </div>
                <div className="text-[10px] text-slate-500">
                  {calculatedUsers.toLocaleString()} × {scenarioMultiplier.toFixed(1)}x × 0.3
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-500">Token Price (End)</div>
                <div className="text-lg font-bold text-amber-400">
                  ${(0.03 * selectedScenario.tokenPriceEndMultiplier * selectedMarket.priceMultiplier).toFixed(3)}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default GrowthScenarioSelector;

