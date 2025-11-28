'use client';

import { SimulationParameters, Preset, GrowthScenario, MarketCondition } from '@/types/simulation';
import { PRESETS } from '@/lib/constants';
import { formatCurrency } from '@/lib/utils';
import { GrowthScenarioSelector } from './GrowthScenarioSelector';

interface ParameterControlsProps {
  parameters: SimulationParameters;
  onUpdateParameter: <K extends keyof SimulationParameters>(key: K, value: SimulationParameters[K]) => void;
  onUpdateParameters: (updates: Partial<SimulationParameters>) => void;
  onReset: () => void;
  onLoadPreset: (preset: Partial<SimulationParameters>) => void;
}

export function ParameterControls({
  parameters,
  onUpdateParameter,
  onUpdateParameters,
  onReset,
  onLoadPreset,
}: ParameterControlsProps) {
  // Calculate derived values
  const totalCreatorCost = 
    parameters.highQualityCreatorsNeeded * parameters.highQualityCreatorCAC +
    parameters.midLevelCreatorsNeeded * parameters.midLevelCreatorCAC;
  
  const consumerBudget = Math.max(0, parameters.marketingBudget - totalCreatorCost);
  
  const totalPercent = parameters.northAmericaBudgetPercent + parameters.globalLowIncomeBudgetPercent;
  const normalizedNA = totalPercent > 0 ? parameters.northAmericaBudgetPercent / totalPercent : 0.5;
  const normalizedGlobal = totalPercent > 0 ? parameters.globalLowIncomeBudgetPercent / totalPercent : 0.5;
  
  const naBudget = consumerBudget * normalizedNA;
  const globalBudget = consumerBudget * normalizedGlobal;
  
  const naUsers = parameters.cacNorthAmericaConsumer > 0 ? Math.floor(naBudget / parameters.cacNorthAmericaConsumer) : 0;
  const globalUsers = parameters.cacGlobalLowIncomeConsumer > 0 ? Math.floor(globalBudget / parameters.cacGlobalLowIncomeConsumer) : 0;
  
  const totalCreators = parameters.highQualityCreatorsNeeded + parameters.midLevelCreatorsNeeded;
  const totalUsers = totalCreators + naUsers + globalUsers;
  
  const blendedCAC = totalUsers > 0 ? parameters.marketingBudget / totalUsers : 0;

  return (
    <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-6 border-b border-gray-700">
      <h3 className="text-white font-bold text-lg mb-4 flex items-center gap-2">
        <span>⚙️</span> Interactive Controls
      </h3>

      {/* Core Parameters */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <NumberInput
          label="VCoin Token Price (USD)"
          value={parameters.tokenPrice}
          onChange={(v) => onUpdateParameter('tokenPrice', v)}
          min={0.001}
          max={1}
          step={0.01}
          icon="💲"
        />
        <NumberInput
          label="Marketing Budget (USD/Year)"
          value={parameters.marketingBudget}
          onChange={(v) => onUpdateParameter('marketingBudget', v)}
          min={0}
          max={10000000}
          step={5000}
          icon="💰"
        />
        <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3">
          <div className="text-xs text-gray-300 mb-1">Calculated Users</div>
          <div className="text-2xl font-bold text-blue-400">{totalUsers.toLocaleString()}</div>
        </div>
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3">
          <div className="text-xs text-gray-300 mb-1">Blended CAC</div>
          <div className="text-2xl font-bold text-emerald-400">{formatCurrency(blendedCAC, 2)}</div>
        </div>
      </div>

      {/* Creator Acquisition */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>👤</span> Creator Acquisition
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <NumberInput
          label="HQ Creator CAC ($)"
          value={parameters.highQualityCreatorCAC}
          onChange={(v) => onUpdateParameter('highQualityCreatorCAC', v)}
          min={0}
          step={100}
        />
        <NumberInput
          label="HQ Creators Needed"
          value={parameters.highQualityCreatorsNeeded}
          onChange={(v) => onUpdateParameter('highQualityCreatorsNeeded', v)}
          min={0}
          step={1}
        />
        <NumberInput
          label="Mid-Level Creator CAC ($)"
          value={parameters.midLevelCreatorCAC}
          onChange={(v) => onUpdateParameter('midLevelCreatorCAC', v)}
          min={0}
          step={25}
        />
        <NumberInput
          label="Mid-Level Creators Needed"
          value={parameters.midLevelCreatorsNeeded}
          onChange={(v) => onUpdateParameter('midLevelCreatorsNeeded', v)}
          min={0}
          step={5}
        />
      </div>

      {/* Consumer Acquisition */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <NumberInput
          label="North America Budget (%)"
          value={parameters.northAmericaBudgetPercent * 100}
          onChange={(v) => onUpdateParameter('northAmericaBudgetPercent', v / 100)}
          min={0}
          max={100}
          step={5}
        />
        <NumberInput
          label="Global Low Income Budget (%)"
          value={parameters.globalLowIncomeBudgetPercent * 100}
          onChange={(v) => onUpdateParameter('globalLowIncomeBudgetPercent', v / 100)}
          min={0}
          max={100}
          step={5}
        />
        <NumberInput
          label="NA Consumer CAC ($)"
          value={parameters.cacNorthAmericaConsumer}
          onChange={(v) => onUpdateParameter('cacNorthAmericaConsumer', v)}
          min={1}
          step={5}
        />
        <NumberInput
          label="Global Consumer CAC ($)"
          value={parameters.cacGlobalLowIncomeConsumer}
          onChange={(v) => onUpdateParameter('cacGlobalLowIncomeConsumer', v)}
          min={1}
          step={1}
        />
      </div>

      {/* Economic Parameters */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>📊</span> Economic Parameters
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <SliderInput
          label="Burn Rate (%)"
          value={parameters.burnRate * 100}
          onChange={(v) => onUpdateParameter('burnRate', v / 100)}
          min={0}
          max={50}
        />
        <SliderInput
          label="Buyback (%)"
          value={parameters.buybackPercent * 100}
          onChange={(v) => onUpdateParameter('buybackPercent', v / 100)}
          min={0}
          max={50}
        />
        {/* Show static slider only when dynamic allocation is disabled */}
        {parameters.enableDynamicAllocation === false ? (
          <SliderInput
            label="Daily Reward Allocation (%)"
            value={parameters.rewardAllocationPercent * 100}
            onChange={(v) => onUpdateParameter('rewardAllocationPercent', v / 100)}
            min={5}
            max={90}
          />
        ) : (
          <div className="bg-purple-500/20 border border-purple-500/40 rounded-lg p-3">
            <div className="text-xs text-purple-300 mb-1">Reward Allocation</div>
            <div className="text-lg font-bold text-purple-400">Dynamic</div>
            <div className="text-xs text-purple-400/70">5-90% based on users</div>
          </div>
        )}
        <SliderInput
          label="Paid Tier Conversion (%)"
          value={parameters.verificationRate * 100}
          onChange={(v) => onUpdateParameter('verificationRate', v / 100)}
          min={1}
          max={20}
        />
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-6">
        {/* Issue #16 Fix: Changed min from 1 to 0.1 to allow fractional posts per user */}
        <SliderInput
          label="Posts per User/Month"
          value={parameters.postsPerUser}
          onChange={(v) => onUpdateParameter('postsPerUser', v)}
          min={0.1}
          max={20}
          step={0.1}
          showPercent={false}
        />
        <SliderInput
          label="Ad Fill Rate (%)"
          value={parameters.adCPMMultiplier * 100}
          onChange={(v) => onUpdateParameter('adCPMMultiplier', v / 100)}
          min={5}
          max={100}
        />
      </div>

      {/* Dynamic Reward Allocation (NEW - Nov 2025) */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>🎯</span> Dynamic Reward Allocation
      </h4>
      <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-lg p-4 mb-6">
        <div className="flex items-center gap-3 mb-4">
          <ToggleSwitch
            label="Enable Dynamic Allocation"
            checked={parameters.enableDynamicAllocation !== false}
            onChange={(v) => onUpdateParameter('enableDynamicAllocation', v)}
          />
          <span className="text-xs text-gray-400">
            Automatically scales reward allocation (5-90%) based on user growth
          </span>
        </div>
        {(parameters.enableDynamicAllocation !== false) && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <NumberInput
              label="Initial Users"
              value={parameters.initialUsersForAllocation || 1000}
              onChange={(v) => onUpdateParameter('initialUsersForAllocation', v)}
              min={100}
              max={100000}
              step={100}
            />
            <NumberInput
              label="Target Users (Max Alloc)"
              value={parameters.targetUsersForMaxAllocation || 1000000}
              onChange={(v) => onUpdateParameter('targetUsersForMaxAllocation', v)}
              min={10000}
              max={100000000}
              step={10000}
            />
            <NumberInput
              label="Max Per-User USD/Month"
              value={parameters.maxPerUserMonthlyUsd || 50}
              onChange={(v) => onUpdateParameter('maxPerUserMonthlyUsd', v)}
              min={1}
              max={500}
              step={5}
              icon="💵"
            />
            <NumberInput
              label="Min Per-User USD/Month"
              value={parameters.minPerUserMonthlyUsd || 0.10}
              onChange={(v) => onUpdateParameter('minPerUserMonthlyUsd', v)}
              min={0.01}
              max={10}
              step={0.1}
              icon="💵"
            />
          </div>
        )}
        {(parameters.enableDynamicAllocation !== false) && (
          <div className="mt-3 text-xs text-gray-400 bg-black/20 rounded p-2">
            <strong>Formula:</strong> allocation = 5% + 85% × ln(users/{parameters.initialUsersForAllocation || 1000}) / ln({((parameters.targetUsersForMaxAllocation || 1000000) / 1000).toFixed(0)}K/{(parameters.initialUsersForAllocation || 1000) / 1000}K)
            <br />
            <strong>Safety:</strong> Per-user reward capped at ${parameters.maxPerUserMonthlyUsd || 50}/month to prevent inflation
          </div>
        )}
      </div>

      {/* Module Toggles */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>🔧</span> Module Toggles
      </h4>
      <div className="flex flex-wrap gap-4 mb-6">
        <ToggleSwitch
          label="Community Module"
          checked={parameters.enableCommunity}
          onChange={(v) => onUpdateParameter('enableCommunity', v)}
        />
        <ToggleSwitch
          label="Advertising Module"
          checked={parameters.enableAdvertising}
          onChange={(v) => onUpdateParameter('enableAdvertising', v)}
        />
        <ToggleSwitch
          label="Messaging Module"
          checked={parameters.enableMessaging}
          onChange={(v) => onUpdateParameter('enableMessaging', v)}
        />
        <ToggleSwitch
          label="NFT Features"
          checked={parameters.enableNft || false}
          onChange={(v) => onUpdateParameter('enableNft', v)}
        />
      </div>

      {/* Liquidity Parameters (NEW) */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>💧</span> Liquidity Parameters
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <NumberInput
          label="Initial Liquidity ($)"
          value={parameters.initialLiquidityUsd || 500000}
          onChange={(v) => onUpdateParameter('initialLiquidityUsd', v)}
          min={10000}
          max={10000000}
          step={10000}
          icon="💰"
        />
        <SliderInput
          label="Protocol Owned Liquidity (%)"
          value={(parameters.protocolOwnedLiquidity || 0.70) * 100}
          onChange={(v) => onUpdateParameter('protocolOwnedLiquidity', v / 100)}
          min={0}
          max={100}
        />
        <NumberInput
          label="Lock Period (Months)"
          value={parameters.liquidityLockMonths || 24}
          onChange={(v) => onUpdateParameter('liquidityLockMonths', v)}
          min={6}
          max={60}
          step={6}
        />
        <SliderInput
          label="Target Liquidity Ratio (%)"
          value={(parameters.targetLiquidityRatio || 0.15) * 100}
          onChange={(v) => onUpdateParameter('targetLiquidityRatio', v / 100)}
          min={5}
          max={50}
        />
      </div>

      {/* Staking Parameters (NEW) */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>🔒</span> Staking Parameters
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <SliderInput
          label="Staking APY (%)"
          value={(parameters.stakingApy || 0.10) * 100}
          onChange={(v) => onUpdateParameter('stakingApy', v / 100)}
          min={0}
          max={30}
        />
        <SliderInput
          label="Staker Fee Discount (%)"
          value={(parameters.stakerFeeDiscount || 0.30) * 100}
          onChange={(v) => onUpdateParameter('stakerFeeDiscount', v / 100)}
          min={0}
          max={50}
        />
        <NumberInput
          label="Min Stake Amount (VCoin)"
          value={parameters.minStakeAmount || 100}
          onChange={(v) => onUpdateParameter('minStakeAmount', v)}
          min={0}
          max={10000}
          step={100}
        />
        <NumberInput
          label="Stake Lock (Days)"
          value={parameters.stakeLockDays || 30}
          onChange={(v) => onUpdateParameter('stakeLockDays', v)}
          min={0}
          max={365}
          step={7}
        />
      </div>

      {/* Creator Economy Parameters (NEW) */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>🎨</span> Creator Economy
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <SliderInput
          label="Platform Creator Fee (%)"
          value={(parameters.platformCreatorFee || 0.05) * 100}
          onChange={(v) => onUpdateParameter('platformCreatorFee', v / 100)}
          min={0}
          max={20}
        />
        <NumberInput
          label="Boost Post Fee (VCoin)"
          value={parameters.boostPostFeeVcoin || 5}
          onChange={(v) => onUpdateParameter('boostPostFeeVcoin', v)}
          min={0}
          max={50}
          step={1}
        />
        <NumberInput
          label="Premium DM Fee (VCoin)"
          value={parameters.premiumDmFeeVcoin || 2}
          onChange={(v) => onUpdateParameter('premiumDmFeeVcoin', v)}
          min={0}
          max={20}
          step={1}
        />
        <NumberInput
          label="Premium Reaction Fee (VCoin)"
          value={parameters.premiumReactionFeeVcoin || 1}
          onChange={(v) => onUpdateParameter('premiumReactionFeeVcoin', v)}
          min={0}
          max={10}
          step={0.5}
        />
      </div>

      {/* Growth Scenario Projection (NEW - Nov 2025) */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>📈</span> Growth Scenario Projection
      </h4>
      <div className="mb-6">
        <GrowthScenarioSelector
          scenario={(parameters.growthScenario || 'base') as GrowthScenario}
          marketCondition={(parameters.marketCondition || 'bull') as MarketCondition}
          calculatedUsers={totalUsers}
          enableFomoEvents={parameters.enableFomoEvents !== false}
          useGrowthScenarios={parameters.useGrowthScenarios || false}
          onScenarioChange={(v) => onUpdateParameter('growthScenario', v)}
          onMarketConditionChange={(v) => onUpdateParameter('marketCondition', v)}
          onFomoEventsChange={(v) => onUpdateParameter('enableFomoEvents', v)}
          onUseGrowthScenariosChange={(v) => onUpdateParameter('useGrowthScenarios', v)}
        />
      </div>

      {/* Identity Pricing */}
      <h4 className="text-white font-semibold mb-3 flex items-center gap-2">
        <span>🆔</span> Identity Module Pricing
      </h4>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <NumberInput
          label="Basic Tier ($)"
          value={parameters.basicPrice}
          onChange={(v) => onUpdateParameter('basicPrice', v)}
          min={0}
          max={10}
          step={0.5}
        />
        <NumberInput
          label="Verified Tier ($)"
          value={parameters.verifiedPrice}
          onChange={(v) => onUpdateParameter('verifiedPrice', v)}
          min={0}
          max={50}
          step={1}
        />
        <NumberInput
          label="Premium Tier ($)"
          value={parameters.premiumPrice}
          onChange={(v) => onUpdateParameter('premiumPrice', v)}
          min={0}
          max={100}
          step={1}
        />
        <NumberInput
          label="Enterprise Tier ($)"
          value={parameters.enterprisePrice}
          onChange={(v) => onUpdateParameter('enterprisePrice', v)}
          min={0}
          max={500}
          step={5}
        />
      </div>

      {/* Presets */}
      <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-700">
        {PRESETS.map((preset) => (
          <button
            key={preset.name}
            onClick={() => onLoadPreset(preset.parameters)}
            className="px-4 py-2 rounded-lg font-semibold text-sm border-2 border-white/30 
                       bg-white/10 text-white hover:bg-white hover:text-gray-900 
                       transition-all hover:-translate-y-0.5"
          >
            {preset.icon} {preset.label}
          </button>
        ))}
        <button
          onClick={onReset}
          className="px-4 py-2 rounded-lg font-semibold text-sm border-2 border-amber-500/50 
                     bg-amber-500/20 text-amber-400 hover:bg-amber-500 hover:text-white 
                     transition-all hover:-translate-y-0.5"
        >
          🔄 Reset to Defaults
        </button>
      </div>
    </div>
  );
}

// Input Components
function NumberInput({
  label,
  value,
  onChange,
  min,
  max,
  step,
  icon,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  icon?: string;
}) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-300 mb-1.5">
        {icon && <span className="mr-1">{icon}</span>}
        {label}
      </label>
      <input
        type="number"
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value) || 0)}
        min={min}
        max={max}
        step={step}
        className="w-full px-3 py-2 border border-gray-600 rounded-lg text-sm font-semibold 
                   bg-white/95 text-gray-900 transition-all focus:outline-none focus:border-white 
                   focus:ring-2 focus:ring-white/20"
      />
    </div>
  );
}

function SliderInput({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  showPercent = true,
}: {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  showPercent?: boolean;
}) {
  return (
    <div>
      <label className="block text-xs font-semibold text-gray-300 mb-1.5">{label}</label>
      <input
        type="range"
        value={value}
        // Issue #29 Fix: Add fallback to min if parseFloat returns NaN
        onChange={(e) => onChange(parseFloat(e.target.value) || min)}
        min={min}
        max={max}
        step={step}
        className="w-full h-2 rounded-full bg-gray-600 appearance-none cursor-pointer
                   [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 
                   [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full 
                   [&::-webkit-slider-thumb]:bg-white [&::-webkit-slider-thumb]:shadow-md
                   [&::-webkit-slider-thumb]:cursor-pointer"
      />
      <div className="mt-1 px-3 py-1 bg-white/20 rounded text-white text-sm font-bold inline-block">
        {value.toFixed(showPercent && value % 1 !== 0 ? 1 : 0)}{showPercent ? '%' : ''}
      </div>
    </div>
  );
}

function ToggleSwitch({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (checked: boolean) => void;
}) {
  return (
    <label className="flex items-center gap-3 cursor-pointer select-none">
      <div
        onClick={() => onChange(!checked)}
        className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer
                   ${checked ? 'bg-emerald-500' : 'bg-gray-600'}`}
      >
        <div
          className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform
                     ${checked ? 'translate-x-7' : 'translate-x-1'}`}
        />
      </div>
      <span className="text-white font-semibold text-sm">{label}</span>
    </label>
  );
}


