'use client';

import { useState } from 'react';
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
  // Section collapse states
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    core: true,
    creator: false,
    economic: false,
    dynamic: false,
    growth: false,
    // Revenue Modules
    identity: false,
    content: false,
    advertising: false,
    exchange: false,
    rewards: false,
    staking: false,
    liquidity: false,
    governance: false,
    // Future Modules
    vchain: false,
    marketplace: false,
    businessHub: false,
    crossPlatform: false,
  });

  const toggleSection = (section: string) => {
    setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }));
  };

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

  // Count enabled modules
  const coreModulesEnabled = [
    parameters.enableIdentity !== false,
    parameters.enableContent !== false,
    parameters.enableRewards !== false,
    parameters.enableStaking !== false,
    parameters.enableLiquidity !== false,
    parameters.enableGovernance !== false,
    parameters.enableAdvertising,
    parameters.enableExchange,
  ].filter(Boolean).length;

  const futureModulesEnabled = [
    parameters.enableVchain,
    parameters.enableMarketplace,
    parameters.enableBusinessHub,
    parameters.enableCrossPlatform,
  ].filter(Boolean).length;

  return (
    <div className="bg-gradient-to-r from-gray-800 to-gray-900 p-6 border-b border-gray-700">
      <h3 className="text-white font-bold text-lg mb-4 flex items-center gap-2">
        <span>⚙️</span> Interactive Controls
        <span className="text-xs text-gray-400 ml-2">
          ({coreModulesEnabled} core + {futureModulesEnabled} future modules enabled)
        </span>
      </h3>

      {/* Core Parameters - Always visible */}
      <CollapsibleSection
        title="Core Parameters"
        icon="💲"
        isExpanded={expandedSections.core}
        onToggle={() => toggleSection('core')}
      >
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
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
      </CollapsibleSection>

      {/* Creator Acquisition */}
      <CollapsibleSection
        title="Creator Acquisition"
        icon="👤"
        isExpanded={expandedSections.creator}
        onToggle={() => toggleSection('creator')}
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
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
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
      </CollapsibleSection>

      {/* Economic Parameters */}
      <CollapsibleSection
        title="Economic Parameters"
        icon="📊"
        isExpanded={expandedSections.economic}
        onToggle={() => toggleSection('economic')}
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <SliderInput
            label="Burn Rate (%)"
            value={parameters.burnRate * 100}
            onChange={(v) => onUpdateParameter('burnRate', v / 100)}
            min={0}
            max={25}
            step={1}
          />
          <SliderInput
            label="Buyback (% of Revenue)"
            value={parameters.buybackPercent * 100}
            onChange={(v) => onUpdateParameter('buybackPercent', v / 100)}
            min={0}
            max={25}
            step={1}
          />
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
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
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
            value={parameters.adFillRate * 100}
            onChange={(v) => onUpdateParameter('adFillRate', v / 100)}
            min={5}
            max={100}
          />
        </div>
      </CollapsibleSection>

      {/* Dynamic Reward Allocation */}
      <CollapsibleSection
        title="Dynamic Reward Allocation"
        icon="🎯"
        isExpanded={expandedSections.dynamic}
        onToggle={() => toggleSection('dynamic')}
        badge={parameters.enableDynamicAllocation !== false ? 'ON' : 'OFF'}
        badgeColor={parameters.enableDynamicAllocation !== false ? 'emerald' : 'gray'}
      >
        <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-lg p-4">
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
        </div>
      </CollapsibleSection>

      {/* Growth Scenario Projection */}
      <CollapsibleSection
        title="Growth Scenario Projection"
        icon="📈"
        isExpanded={expandedSections.growth}
        onToggle={() => toggleSection('growth')}
        badge={parameters.growthScenario || 'base'}
        badgeColor="blue"
      >
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
      </CollapsibleSection>

      {/* ==================== REVENUE MODULES ==================== */}
      <div className="mt-6 mb-3">
        <h4 className="text-gray-400 text-xs font-bold uppercase tracking-wider flex items-center gap-2">
          <span className="h-px flex-1 bg-gray-700"></span>
          Revenue Modules
          <span className="h-px flex-1 bg-gray-700"></span>
        </h4>
      </div>

      {/* Identity Module */}
      <ModuleSection
        title="Identity Module"
        icon="🆔"
        description="User verification tiers & profile marketplace"
        isExpanded={expandedSections.identity}
        onToggle={() => toggleSection('identity')}
        enabled={parameters.enableIdentity !== false}
        onEnableChange={(v) => onUpdateParameter('enableIdentity', v)}
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
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
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <NumberInput
            label="Transfer Fee ($)"
            value={parameters.transferFee}
            onChange={(v) => onUpdateParameter('transferFee', v)}
            min={0}
            max={50}
            step={1}
          />
          <SliderInput
            label="Sale Commission (%)"
            value={parameters.saleCommission * 100}
            onChange={(v) => onUpdateParameter('saleCommission', v / 100)}
            min={0}
            max={50}
          />
          <NumberInput
            label="Monthly Sales"
            value={parameters.monthlySales}
            onChange={(v) => onUpdateParameter('monthlySales', v)}
            min={0}
            max={100}
            step={1}
          />
          <NumberInput
            label="Avg Profile Price ($)"
            value={parameters.avgProfilePrice || 25}
            onChange={(v) => onUpdateParameter('avgProfilePrice', v)}
            min={5}
            max={500}
            step={5}
          />
        </div>
      </ModuleSection>

      {/* Content Module */}
      <ModuleSection
        title="Content Module"
        icon="📝"
        description="NFT minting & premium features"
        isExpanded={expandedSections.content}
        onToggle={() => toggleSection('content')}
        enabled={parameters.enableContent !== false}
        onEnableChange={(v) => onUpdateParameter('enableContent', v)}
      >
        {/* NFT Settings */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <ToggleSwitch
            label="Enable NFT Features"
            checked={parameters.enableNft || false}
            onChange={(v) => onUpdateParameter('enableNft', v)}
          />
          <NumberInput
            label="NFT Mint Fee (VCoin)"
            value={parameters.nftMintFeeVcoin}
            onChange={(v) => onUpdateParameter('nftMintFeeVcoin', v)}
            min={0}
            max={200}
            step={5}
          />
          <SliderInput
            label="NFT Mint % of Posts"
            value={(parameters.nftMintPercentage || 0.005) * 100}
            onChange={(v) => onUpdateParameter('nftMintPercentage', v / 100)}
            min={0}
            max={10}
            step={0.1}
          />
        </div>

        {/* Content Volume */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <NumberInput
            label="Premium Content Vol (VCoin)"
            value={parameters.premiumContentVolumeVcoin}
            onChange={(v) => onUpdateParameter('premiumContentVolumeVcoin', v)}
            min={0}
            max={10000}
            step={100}
          />
          <NumberInput
            label="Content Sale Vol (VCoin)"
            value={parameters.contentSaleVolumeVcoin}
            onChange={(v) => onUpdateParameter('contentSaleVolumeVcoin', v)}
            min={0}
            max={5000}
            step={50}
          />
        </div>

        {/* Dynamic Boost Post Fee */}
        <div className="bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/30 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-3">
            <span className="text-lg">🚀</span>
            <span className="text-white font-semibold text-sm">Dynamic Boost Post Fee</span>
            <span className="text-xs text-amber-400/70 ml-2">
              Scales down as platform grows
            </span>
          </div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <NumberInput
              label="Target USD"
              value={parameters.boostPostTargetUsd || 0.15}
              onChange={(v) => onUpdateParameter('boostPostTargetUsd', v)}
              min={0.01}
              max={5}
              step={0.01}
              icon="💵"
            />
            <NumberInput
              label="Min USD"
              value={parameters.boostPostMinUsd || 0.05}
              onChange={(v) => onUpdateParameter('boostPostMinUsd', v)}
              min={0.01}
              max={1}
              step={0.01}
              icon="💵"
            />
            <NumberInput
              label="Max USD"
              value={parameters.boostPostMaxUsd || 0.50}
              onChange={(v) => onUpdateParameter('boostPostMaxUsd', v)}
              min={0.05}
              max={10}
              step={0.05}
              icon="💵"
            />
            <NumberInput
              label="Scale Users"
              value={parameters.boostPostScaleUsers || 100000}
              onChange={(v) => onUpdateParameter('boostPostScaleUsers', v)}
              min={1000}
              max={10000000}
              step={10000}
            />
          </div>
          <div className="mt-2 text-xs text-gray-400 bg-black/20 rounded p-2">
            Fee starts at <strong>${parameters.boostPostTargetUsd || 0.15}</strong> and scales down to <strong>${parameters.boostPostMinUsd || 0.05}</strong> at {((parameters.boostPostScaleUsers || 100000) / 1000).toFixed(0)}K users
          </div>
        </div>

        {/* Other Premium Features */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
      </ModuleSection>

      {/* Advertising Module */}
      <ModuleSection
        title="Advertising Module"
        icon="📢"
        description="CPM ads, promoted posts & analytics"
        isExpanded={expandedSections.advertising}
        onToggle={() => toggleSection('advertising')}
        enabled={parameters.enableAdvertising}
        onEnableChange={(v) => onUpdateParameter('enableAdvertising', v)}
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <NumberInput
            label="Banner CPM ($)"
            value={parameters.bannerCPM}
            onChange={(v) => onUpdateParameter('bannerCPM', v)}
            min={0.05}
            max={20}
            step={0.25}
          />
          <NumberInput
            label="Video CPM ($)"
            value={parameters.videoCPM}
            onChange={(v) => onUpdateParameter('videoCPM', v)}
            min={0.10}
            max={50}
            step={0.5}
          />
          <NumberInput
            label="Promoted Post Fee ($)"
            value={parameters.promotedPostFee}
            onChange={(v) => onUpdateParameter('promotedPostFee', v)}
            min={0}
            max={50}
            step={0.5}
          />
          <SliderInput
            label="Ad Fill Rate (%)"
            value={parameters.adFillRate * 100}
            onChange={(v) => onUpdateParameter('adFillRate', v / 100)}
            min={5}
            max={100}
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <NumberInput
            label="Campaign Mgmt Fee ($)"
            value={parameters.campaignManagementFee}
            onChange={(v) => onUpdateParameter('campaignManagementFee', v)}
            min={0}
            max={500}
            step={10}
          />
          <NumberInput
            label="Analytics Sub Fee ($)"
            value={parameters.adAnalyticsFee}
            onChange={(v) => onUpdateParameter('adAnalyticsFee', v)}
            min={0}
            max={100}
            step={5}
          />
        </div>
      </ModuleSection>

      {/* Exchange Module */}
      <ModuleSection
        title="Exchange Module"
        icon="💱"
        description="Swap fees, withdrawals & trading"
        isExpanded={expandedSections.exchange}
        onToggle={() => toggleSection('exchange')}
        enabled={parameters.enableExchange}
        onEnableChange={(v) => onUpdateParameter('enableExchange', v)}
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <SliderInput
            label="Swap Fee (%)"
            value={parameters.exchangeSwapFeePercent * 100}
            onChange={(v) => onUpdateParameter('exchangeSwapFeePercent', v / 100)}
            min={0}
            max={5}
            step={0.1}
          />
          <NumberInput
            label="Withdrawal Fee ($)"
            value={parameters.exchangeWithdrawalFee}
            onChange={(v) => onUpdateParameter('exchangeWithdrawalFee', v)}
            min={0}
            max={50}
            step={0.5}
          />
          <SliderInput
            label="User Adoption Rate (%)"
            value={parameters.exchangeUserAdoptionRate * 100}
            onChange={(v) => onUpdateParameter('exchangeUserAdoptionRate', v / 100)}
            min={1}
            max={30}
          />
          <NumberInput
            label="Avg Monthly Volume ($)"
            value={parameters.exchangeAvgMonthlyVolume}
            onChange={(v) => onUpdateParameter('exchangeAvgMonthlyVolume', v)}
            min={0}
            max={2000}
            step={50}
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
          <NumberInput
            label="Withdrawals Per User"
            value={parameters.exchangeWithdrawalsPerUser}
            onChange={(v) => onUpdateParameter('exchangeWithdrawalsPerUser', v)}
            min={0}
            max={5}
            step={0.1}
          />
          {/* FRONT-004 FIX: Add exchangeAvgSwapSize control */}
          <NumberInput
            label="Avg Swap Size ($)"
            value={parameters.exchangeAvgSwapSize || 30}
            onChange={(v) => onUpdateParameter('exchangeAvgSwapSize', v)}
            min={10}
            max={500}
            step={5}
          />
        </div>
      </ModuleSection>

      {/* Rewards Module */}
      <ModuleSection
        title="Rewards Module"
        icon="🎁"
        description="5% platform fee on all emissions"
        isExpanded={expandedSections.rewards}
        onToggle={() => toggleSection('rewards')}
        enabled={parameters.enableRewards !== false}
        onEnableChange={(v) => onUpdateParameter('enableRewards', v)}
      >
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">💰</span>
            <div>
              <div className="text-emerald-400 font-bold">5% Platform Fee (Fixed)</div>
              <div className="text-xs text-gray-400">
                Platform takes 5% of ALL reward emissions before distribution. This is the primary revenue source.
              </div>
            </div>
          </div>
        </div>
        <div className="text-xs text-gray-400">
          See "Dynamic Reward Allocation" section above to configure emission parameters.
        </div>
      </ModuleSection>

      {/* Staking Module */}
      <ModuleSection
        title="Staking Module"
        icon="🔒"
        description="APY, protocol fees & lock periods"
        isExpanded={expandedSections.staking}
        onToggle={() => toggleSection('staking')}
        enabled={parameters.enableStaking !== false}
        onEnableChange={(v) => onUpdateParameter('enableStaking', v)}
      >
        {/* NEW: Key staking participation controls - these affect Value Accrual! */}
        <div className="bg-purple-900/30 border border-purple-500/30 rounded-lg p-3 mb-4">
          <div className="text-xs text-purple-300 mb-2 font-medium">⚡ Key Participation Settings (affects Value Accrual)</div>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <SliderInput
              label="Staking Participation (%)"
              value={(parameters.stakingParticipationRate || 0.15) * 100}
              onChange={(v) => onUpdateParameter('stakingParticipationRate', v / 100)}
              min={1}
              max={50}
            />
            <NumberInput
              label="Avg Stake Amount (VCoin)"
              value={parameters.avgStakeAmount || 2000}
              onChange={(v) => onUpdateParameter('avgStakeAmount', v)}
              min={100}
              max={100000}
              step={500}
            />
            <SliderInput
              label="Staking APY (%)"
              value={(parameters.stakingApy || 0.10) * 100}
              onChange={(v) => onUpdateParameter('stakingApy', v / 100)}
              min={0}
              max={30}
            />
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
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
          <SliderInput
            label="Protocol Fee on Rewards (%)"
            value={(parameters.stakingProtocolFee || 0.05) * 100}
            onChange={(v) => onUpdateParameter('stakingProtocolFee', v / 100)}
            min={0}
            max={20}
          />
        </div>
      </ModuleSection>

      {/* Liquidity Module */}
      <ModuleSection
        title="Liquidity Module"
        icon="💧"
        description="DEX pools, POL & health tracking"
        isExpanded={expandedSections.liquidity}
        onToggle={() => toggleSection('liquidity')}
        enabled={parameters.enableLiquidity !== false}
        onEnableChange={(v) => onUpdateParameter('enableLiquidity', v)}
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
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
      </ModuleSection>

      {/* Governance Module */}
      <ModuleSection
        title="Governance Module"
        icon="🗳️"
        description="veVCoin voting, proposals & fees"
        isExpanded={expandedSections.governance}
        onToggle={() => toggleSection('governance')}
        enabled={parameters.enableGovernance !== false}
        onEnableChange={(v) => onUpdateParameter('enableGovernance', v)}
      >
        {/* Key Participation Settings - affects Value Accrual */}
        <div className="mb-4 p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
          <div className="text-purple-400 text-xs font-bold mb-3">⚡ Key Participation Settings (affects Value Accrual)</div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <SliderInput
              label="Voting Participation (%)"
              value={(parameters.governanceParticipationRate || 0.10) * 100}
              onChange={(v) => onUpdateParameter('governanceParticipationRate', v / 100)}
              min={0}
              max={50}
            />
            <SliderInput
              label="Delegation Rate (%)"
              value={(parameters.governanceDelegationRate || 0.20) * 100}
              onChange={(v) => onUpdateParameter('governanceDelegationRate', v / 100)}
              min={0}
              max={80}
            />
            <NumberInput
              label="Avg Lock (Weeks)"
              value={parameters.governanceAvgLockWeeks || 26}
              onChange={(v) => onUpdateParameter('governanceAvgLockWeeks', v)}
              min={4}
              max={208}
              step={4}
            />
            <NumberInput
              label="Proposals/Month"
              value={parameters.governanceProposalsPerMonth || 5}
              onChange={(v) => onUpdateParameter('governanceProposalsPerMonth', v)}
              min={0}
              max={30}
              step={1}
            />
          </div>
        </div>
        
        {/* Fee Settings */}
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mb-4">
          <NumberInput
            label="Proposal Fee (VCoin)"
            value={parameters.governanceProposalFee || 100}
            onChange={(v) => onUpdateParameter('governanceProposalFee', v)}
            min={0}
            max={1000}
            step={10}
          />
          <NumberInput
            label="Badge NFT Price (VCoin)"
            value={parameters.governanceBadgePrice || 50}
            onChange={(v) => onUpdateParameter('governanceBadgePrice', v)}
            min={0}
            max={500}
            step={5}
          />
          <NumberInput
            label="Premium Gov Fee (VCoin/mo)"
            value={parameters.governancePremiumFee || 100}
            onChange={(v) => onUpdateParameter('governancePremiumFee', v)}
            min={0}
            max={500}
            step={10}
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <NumberInput
            label="Min veVCoin to Vote"
            value={parameters.governanceMinVevcoinToVote || 1}
            onChange={(v) => onUpdateParameter('governanceMinVevcoinToVote', v)}
            min={0}
            max={100}
            step={1}
          />
          <NumberInput
            label="Min veVCoin to Propose"
            value={parameters.governanceMinVevcoinToPropose || 1000}
            onChange={(v) => onUpdateParameter('governanceMinVevcoinToPropose', v)}
            min={0}
            max={100000}
            step={100}
          />
          <NumberInput
            label="Voting Period (Days)"
            value={parameters.governanceVotingPeriodDays || 7}
            onChange={(v) => onUpdateParameter('governanceVotingPeriodDays', v)}
            min={1}
            max={30}
            step={1}
          />
        </div>
      </ModuleSection>

      {/* ==================== FUTURE MODULES ==================== */}
      <div className="mt-6 mb-3">
        <h4 className="text-gray-400 text-xs font-bold uppercase tracking-wider flex items-center gap-2">
          <span className="h-px flex-1 bg-gray-700"></span>
          Future Modules (2026-2028)
          <span className="h-px flex-1 bg-gray-700"></span>
        </h4>
      </div>

      {/* VChain Module */}
      <ModuleSection
        title="VChain Network"
        icon="🔗"
        description="Cross-chain fees, bridge & enterprise API"
        launchInfo="Month 24"
        isExpanded={expandedSections.vchain}
        onToggle={() => toggleSection('vchain')}
        enabled={parameters.enableVchain || false}
        onEnableChange={(v) => onUpdateParameter('enableVchain', v)}
        accentColor="purple"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <NumberInput
            label="Launch Month"
            value={parameters.vchain?.vchainLaunchMonth || 24}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainLaunchMonth: v } as any })}
            min={12}
            max={60}
            step={1}
          />
          <SliderInput
            label="TX Fee (%)"
            value={(parameters.vchain?.vchainTxFeePercent || 0.002) * 100}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainTxFeePercent: v / 100 } as any })}
            min={0.05}
            max={1}
            step={0.05}
          />
          <SliderInput
            label="Bridge Fee (%)"
            value={(parameters.vchain?.vchainBridgeFeePercent || 0.001) * 100}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainBridgeFeePercent: v / 100 } as any })}
            min={0.01}
            max={0.5}
            step={0.01}
          />
          <SliderInput
            label="Gas Markup (%)"
            value={(parameters.vchain?.vchainGasMarkupPercent || 0.08) * 100}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainGasMarkupPercent: v / 100 } as any })}
            min={0}
            max={20}
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <NumberInput
            label="Monthly TX Vol ($M)"
            value={(parameters.vchain?.vchainMonthlyTxVolumeUsd || 25000000) / 1000000}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainMonthlyTxVolumeUsd: v * 1000000 } as any })}
            min={1}
            max={500}
            step={5}
          />
          <NumberInput
            label="Monthly Bridge Vol ($M)"
            value={(parameters.vchain?.vchainMonthlyBridgeVolumeUsd || 50000000) / 1000000}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainMonthlyBridgeVolumeUsd: v * 1000000 } as any })}
            min={1}
            max={1000}
            step={10}
          />
          <SliderInput
            label="Validator APY (%)"
            value={(parameters.vchain?.vchainValidatorApy || 0.10) * 100}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainValidatorApy: v / 100 } as any })}
            min={0}
            max={30}
          />
          <NumberInput
            label="Validators"
            value={parameters.vchain?.vchainValidatorCount || 100}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainValidatorCount: v } as any })}
            min={10}
            max={1000}
            step={10}
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <NumberInput
            label="Min Validator Stake"
            value={parameters.vchain?.vchainMinValidatorStake || 100000}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainMinValidatorStake: v } as any })}
            min={10000}
            max={1000000}
            step={10000}
          />
          <NumberInput
            label="Enterprise Clients"
            value={parameters.vchain?.vchainEnterpriseClients || 10}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainEnterpriseClients: v } as any })}
            min={0}
            max={1000}
            step={5}
          />
          <NumberInput
            label="Avg Enterprise Rev ($)"
            value={parameters.vchain?.vchainAvgEnterpriseRevenue || 5000}
            onChange={(v) => onUpdateParameters({ vchain: { ...parameters.vchain, vchainAvgEnterpriseRevenue: v } as any })}
            min={0}
            max={50000}
            step={500}
          />
        </div>
      </ModuleSection>

      {/* Marketplace Module */}
      <ModuleSection
        title="Marketplace"
        icon="🛒"
        description="Physical, digital, NFT & service commissions"
        launchInfo="Month 18"
        isExpanded={expandedSections.marketplace}
        onToggle={() => toggleSection('marketplace')}
        enabled={parameters.enableMarketplace || false}
        onEnableChange={(v) => onUpdateParameter('enableMarketplace', v)}
        accentColor="purple"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <NumberInput
            label="Launch Month"
            value={parameters.marketplace?.marketplaceLaunchMonth || 18}
            onChange={(v) => onUpdateParameters({ marketplace: { ...parameters.marketplace, marketplaceLaunchMonth: v } as any })}
            min={6}
            max={60}
            step={1}
          />
          <SliderInput
            label="Physical Commission (%)"
            value={(parameters.marketplace?.marketplacePhysicalCommission || 0.08) * 100}
            onChange={(v) => onUpdateParameters({ marketplace: { ...parameters.marketplace, marketplacePhysicalCommission: v / 100 } as any })}
            min={5}
            max={15}
          />
          <SliderInput
            label="Digital Commission (%)"
            value={(parameters.marketplace?.marketplaceDigitalCommission || 0.15) * 100}
            onChange={(v) => onUpdateParameters({ marketplace: { ...parameters.marketplace, marketplaceDigitalCommission: v / 100 } as any })}
            min={8}
            max={25}
          />
          <SliderInput
            label="NFT Commission (%)"
            value={(parameters.marketplace?.marketplaceNftCommission || 0.025) * 100}
            onChange={(v) => onUpdateParameters({ marketplace: { ...parameters.marketplace, marketplaceNftCommission: v / 100 } as any })}
            min={1}
            max={10}
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <SliderInput
            label="Service Commission (%)"
            value={(parameters.marketplace?.marketplaceServiceCommission || 0.08) * 100}
            onChange={(v) => onUpdateParameters({ marketplace: { ...parameters.marketplace, marketplaceServiceCommission: v / 100 } as any })}
            min={3}
            max={15}
          />
          <NumberInput
            label="Monthly GMV ($M)"
            value={(parameters.marketplace?.marketplaceMonthlyGmvUsd || 5000000) / 1000000}
            onChange={(v) => onUpdateParameters({ marketplace: { ...parameters.marketplace, marketplaceMonthlyGmvUsd: v * 1000000 } as any })}
            min={0.1}
            max={100}
            step={0.5}
          />
          <NumberInput
            label="Active Sellers"
            value={parameters.marketplace?.marketplaceActiveSellers || 1000}
            onChange={(v) => onUpdateParameters({ marketplace: { ...parameters.marketplace, marketplaceActiveSellers: v } as any })}
            min={0}
            max={100000}
            step={100}
          />
        </div>
      </ModuleSection>

      {/* Business Hub Module */}
      <ModuleSection
        title="Business Hub"
        icon="💼"
        description="Freelancer, funding, SaaS & academy"
        launchInfo="Month 21"
        isExpanded={expandedSections.businessHub}
        onToggle={() => toggleSection('businessHub')}
        enabled={parameters.enableBusinessHub || false}
        onEnableChange={(v) => onUpdateParameter('enableBusinessHub', v)}
        accentColor="purple"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <NumberInput
            label="Launch Month"
            value={parameters.businessHub?.businessHubLaunchMonth || 21}
            onChange={(v) => onUpdateParameters({ businessHub: { ...parameters.businessHub, businessHubLaunchMonth: v } as any })}
            min={12}
            max={60}
            step={1}
          />
          <SliderInput
            label="Freelancer Commission (%)"
            value={(parameters.businessHub?.freelancerCommissionRate || 0.12) * 100}
            onChange={(v) => onUpdateParameters({ businessHub: { ...parameters.businessHub, freelancerCommissionRate: v / 100 } as any })}
            min={8}
            max={20}
          />
          <NumberInput
            label="Monthly Freelance Vol ($K)"
            value={(parameters.businessHub?.freelancerMonthlyTransactionsUsd || 500000) / 1000}
            onChange={(v) => onUpdateParameters({ businessHub: { ...parameters.businessHub, freelancerMonthlyTransactionsUsd: v * 1000 } as any })}
            min={10}
            max={10000}
            step={50}
          />
          <NumberInput
            label="Active Freelancers"
            value={parameters.businessHub?.freelancerActiveCount || 5000}
            onChange={(v) => onUpdateParameters({ businessHub: { ...parameters.businessHub, freelancerActiveCount: v } as any })}
            min={0}
            max={100000}
            step={500}
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <NumberInput
            label="Monthly Funding Vol ($M)"
            value={(parameters.businessHub?.fundingPortalMonthlyVolume || 2000000) / 1000000}
            onChange={(v) => onUpdateParameters({ businessHub: { ...parameters.businessHub, fundingPortalMonthlyVolume: v * 1000000 } as any })}
            min={0.1}
            max={50}
            step={0.5}
          />
          <SliderInput
            label="Funding Platform Fee (%)"
            value={(parameters.businessHub?.fundingPlatformFee || 0.04) * 100}
            onChange={(v) => onUpdateParameters({ businessHub: { ...parameters.businessHub, fundingPlatformFee: v / 100 } as any })}
            min={2}
            max={10}
          />
        </div>
      </ModuleSection>

      {/* Cross-Platform Module */}
      <ModuleSection
        title="Cross-Platform"
        icon="🌐"
        description="Content sharing, renting & licensing"
        launchInfo="Month 15"
        isExpanded={expandedSections.crossPlatform}
        onToggle={() => toggleSection('crossPlatform')}
        enabled={parameters.enableCrossPlatform || false}
        onEnableChange={(v) => onUpdateParameter('enableCrossPlatform', v)}
        accentColor="purple"
      >
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
          <NumberInput
            label="Launch Month"
            value={parameters.crossPlatform?.crossPlatformLaunchMonth || 15}
            onChange={(v) => onUpdateParameters({ crossPlatform: { ...parameters.crossPlatform, crossPlatformLaunchMonth: v } as any })}
            min={6}
            max={60}
            step={1}
          />
          <SliderInput
            label="Rental Commission (%)"
            value={(parameters.crossPlatform?.crossPlatformRentalCommission || 0.15) * 100}
            onChange={(v) => onUpdateParameters({ crossPlatform: { ...parameters.crossPlatform, crossPlatformRentalCommission: v / 100 } as any })}
            min={10}
            max={25}
          />
          <NumberInput
            label="Monthly Rental Vol ($K)"
            value={(parameters.crossPlatform?.crossPlatformMonthlyRentalVolume || 500000) / 1000}
            onChange={(v) => onUpdateParameters({ crossPlatform: { ...parameters.crossPlatform, crossPlatformMonthlyRentalVolume: v * 1000 } as any })}
            min={10}
            max={10000}
            step={50}
          />
          <NumberInput
            label="Active Renters"
            value={parameters.crossPlatform?.crossPlatformActiveRenters || 5000}
            onChange={(v) => onUpdateParameters({ crossPlatform: { ...parameters.crossPlatform, crossPlatformActiveRenters: v } as any })}
            min={0}
            max={100000}
            step={500}
          />
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <NumberInput
            label="Active Owners"
            value={parameters.crossPlatform?.crossPlatformActiveOwners || 1000}
            onChange={(v) => onUpdateParameters({ crossPlatform: { ...parameters.crossPlatform, crossPlatformActiveOwners: v } as any })}
            min={0}
            max={50000}
            step={100}
          />
        </div>
      </ModuleSection>

      {/* Presets */}
      <div className="flex flex-wrap gap-3 pt-4 mt-4 border-t border-gray-700">
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

// Collapsible Section Component
function CollapsibleSection({
  title,
  icon,
  isExpanded,
  onToggle,
  children,
  badge,
  badgeColor = 'gray',
}: {
  title: string;
  icon: string;
  isExpanded: boolean;
  onToggle: () => void;
  children: React.ReactNode;
  badge?: string;
  badgeColor?: 'gray' | 'emerald' | 'purple' | 'blue' | 'amber';
}) {
  const badgeColors = {
    gray: 'bg-gray-500/30 text-gray-300',
    emerald: 'bg-emerald-500/30 text-emerald-300',
    purple: 'bg-purple-500/30 text-purple-300',
    blue: 'bg-blue-500/30 text-blue-300',
    amber: 'bg-amber-500/30 text-amber-300',
  };

  return (
    <div className="mb-3">
      <button
        onClick={onToggle}
        className="w-full flex items-center justify-between py-2.5 px-3 rounded-lg 
                   bg-white/5 hover:bg-white/10 transition-colors group"
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{icon}</span>
          <span className="text-white font-semibold text-sm">{title}</span>
          {badge && (
            <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${badgeColors[badgeColor]}`}>
              {badge}
            </span>
          )}
        </div>
        <span className={`text-gray-400 transition-transform duration-200 ${isExpanded ? 'rotate-180' : ''}`}>
          ▼
        </span>
      </button>
      {isExpanded && (
        <div className="mt-3 pl-2 animate-fadeIn">
          {children}
        </div>
      )}
    </div>
  );
}

// Module Section Component with Toggle
function ModuleSection({
  title,
  icon,
  description,
  launchInfo,
  isExpanded,
  onToggle,
  enabled,
  onEnableChange,
  children,
  accentColor = 'emerald',
}: {
  title: string;
  icon: string;
  description: string;
  launchInfo?: string;
  isExpanded: boolean;
  onToggle: () => void;
  enabled: boolean;
  onEnableChange: (enabled: boolean) => void;
  children: React.ReactNode;
  accentColor?: 'emerald' | 'purple';
}) {
  const colors = {
    emerald: {
      bg: enabled ? 'bg-emerald-500/10' : 'bg-gray-800/50',
      border: enabled ? 'border-emerald-500/30' : 'border-gray-700/50',
      toggle: enabled ? 'bg-emerald-500' : 'bg-gray-600',
      badge: 'bg-emerald-500/30 text-emerald-300',
    },
    purple: {
      bg: enabled ? 'bg-purple-500/10' : 'bg-gray-800/50',
      border: enabled ? 'border-purple-500/30' : 'border-gray-700/50',
      toggle: enabled ? 'bg-purple-500' : 'bg-gray-600',
      badge: 'bg-purple-500/30 text-purple-300',
    },
  };
  const c = colors[accentColor];

  return (
    <div className={`mb-3 rounded-lg border ${c.border} ${c.bg} transition-all`}>
      <div className="flex items-center justify-between p-3">
        <button
          onClick={onToggle}
          className="flex items-center gap-3 flex-1"
        >
          <span className="text-xl">{icon}</span>
          <div className="text-left">
            <div className="flex items-center gap-2">
              <span className="text-white font-semibold text-sm">{title}</span>
              {launchInfo && (
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${c.badge}`}>
                  {launchInfo}
                </span>
              )}
            </div>
            <div className="text-xs text-gray-400">{description}</div>
          </div>
        </button>
        <div className="flex items-center gap-3">
          <div
            onClick={(e) => {
              e.stopPropagation();
              onEnableChange(!enabled);
            }}
            className={`w-12 h-6 rounded-full transition-colors relative cursor-pointer ${c.toggle}`}
          >
            <div
              className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                enabled ? 'translate-x-7' : 'translate-x-1'
              }`}
            />
          </div>
          <button onClick={onToggle}>
            <span className={`text-gray-400 transition-transform duration-200 inline-block ${isExpanded ? 'rotate-180' : ''}`}>
              ▼
            </span>
          </button>
        </div>
      </div>
      {isExpanded && enabled && (
        <div className="px-3 pb-3 animate-fadeIn border-t border-white/10 pt-3 mt-1">
          {children}
        </div>
      )}
      {isExpanded && !enabled && (
        <div className="px-3 pb-3 text-center text-gray-500 text-sm italic">
          Enable this module to configure parameters
        </div>
      )}
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
