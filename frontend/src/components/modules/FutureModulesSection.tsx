'use client';

import React from 'react';
import { SimulationResult, SimulationParameters, VChainResult, MarketplaceResult, BusinessHubResult, CrossPlatformResult } from '@/types/simulation';
import { FUTURE_MODULE_DEFAULTS } from '@/lib/constants';

interface FutureModulesSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

interface ModuleCardProps {
  title: string;
  icon: string;
  enabled: boolean;
  launched: boolean;
  launchMonth: number;
  monthsUntilLaunch?: number;
  revenue: number;
  profit: number;
  margin: number;
  description: string;
  metrics?: { label: string; value: string }[];
}

function ModuleCard({
  title,
  icon,
  enabled,
  launched,
  launchMonth,
  monthsUntilLaunch,
  revenue,
  profit,
  margin,
  description,
  metrics = [],
}: ModuleCardProps) {
  const statusColor = !enabled 
    ? 'bg-gray-100 text-gray-400 border-gray-200' 
    : launched 
      ? 'bg-emerald-50 text-emerald-700 border-emerald-200'
      : 'bg-amber-50 text-amber-700 border-amber-200';
  
  const statusText = !enabled 
    ? 'Disabled' 
    : launched 
      ? 'Active' 
      : `Launches M${launchMonth}`;

  return (
    <div className={`rounded-xl border-2 p-5 transition-all ${enabled ? 'border-slate-200 bg-white' : 'border-dashed border-slate-200 bg-slate-50/50'}`}>
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <span className="text-2xl">{icon}</span>
          <div>
            <h3 className="font-semibold text-slate-800">{title}</h3>
            <p className="text-xs text-slate-500">{description}</p>
          </div>
        </div>
        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${statusColor}`}>
          {statusText}
        </span>
      </div>

      {enabled && launched && (
        <>
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <div className="text-lg font-bold text-emerald-600">
                ${revenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
              <div className="text-xs text-slate-500">Revenue</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <div className={`text-lg font-bold ${profit >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                ${profit.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
              <div className="text-xs text-slate-500">Profit</div>
            </div>
            <div className="bg-slate-50 rounded-lg p-3 text-center">
              <div className={`text-lg font-bold ${margin >= 0 ? 'text-blue-600' : 'text-red-500'}`}>
                {margin.toFixed(1)}%
              </div>
              <div className="text-xs text-slate-500">Margin</div>
            </div>
          </div>

          {metrics.length > 0 && (
            <div className="space-y-2">
              {metrics.map((metric, idx) => (
                <div key={idx} className="flex justify-between text-sm">
                  <span className="text-slate-500">{metric.label}</span>
                  <span className="font-medium text-slate-700">{metric.value}</span>
                </div>
              ))}
            </div>
          )}
        </>
      )}

      {enabled && !launched && (
        <div className="text-center py-4">
          <div className="text-3xl mb-2">⏳</div>
          <p className="text-sm text-slate-500">
            Launches in <span className="font-semibold text-amber-600">{monthsUntilLaunch} months</span>
          </p>
          <p className="text-xs text-slate-400 mt-1">
            Expected: Month {launchMonth} of simulation
          </p>
        </div>
      )}

      {!enabled && (
        <div className="text-center py-4">
          <div className="text-3xl mb-2 opacity-30">🔒</div>
          <p className="text-sm text-slate-400">Enable in parameters to simulate</p>
        </div>
      )}
    </div>
  );
}

export function FutureModulesSection({ result, parameters }: FutureModulesSectionProps) {
  const vchain = result.vchain;
  const marketplace = result.marketplace;
  const businessHub = result.businessHub;
  const crossPlatform = result.crossPlatform;

  // Get defaults for display when modules are not present
  const defaults = FUTURE_MODULE_DEFAULTS;

  // Check enabled state from parameters (primary source of truth)
  const isVchainEnabled = parameters.enableVchain || vchain?.enabled || false;
  const isMarketplaceEnabled = parameters.enableMarketplace || marketplace?.enabled || false;
  const isBusinessHubEnabled = parameters.enableBusinessHub || businessHub?.enabled || false;
  const isCrossPlatformEnabled = parameters.enableCrossPlatform || crossPlatform?.enabled || false;

  // Count enabled modules
  const enabledCount = [
    isVchainEnabled,
    isMarketplaceEnabled,
    isBusinessHubEnabled,
    isCrossPlatformEnabled,
  ].filter(Boolean).length;

  // Calculate total future revenue
  const totalFutureRevenue = 
    (vchain?.revenue || 0) +
    (marketplace?.revenue || 0) +
    (businessHub?.revenue || 0) +
    (crossPlatform?.revenue || 0);

  const totalFutureProfit = 
    (vchain?.profit || 0) +
    (marketplace?.profit || 0) +
    (businessHub?.profit || 0) +
    (crossPlatform?.profit || 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2">
            🔮 Future Modules (2026-2028)
          </h2>
          <p className="text-sm text-slate-500 mt-1">
            Planned revenue streams launching post-TGE
          </p>
        </div>
        <div className="text-right">
          <div className="text-sm text-slate-500">
            {enabledCount}/4 Enabled
          </div>
          {enabledCount > 0 && totalFutureRevenue > 0 && (
            <div className="text-lg font-bold text-emerald-600">
              +${totalFutureRevenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}/mo
            </div>
          )}
        </div>
      </div>

      {/* Summary Card (when modules are active) */}
      {enabledCount > 0 && totalFutureRevenue > 0 && (
        <div className="bg-gradient-to-r from-purple-50 to-indigo-50 rounded-xl p-5 border border-purple-100">
          <div className="flex items-center gap-4">
            <div className="bg-white rounded-full p-3 shadow-sm">
              <span className="text-2xl">📊</span>
            </div>
            <div className="flex-1">
              <h3 className="font-semibold text-slate-800">Future Modules Impact</h3>
              <p className="text-sm text-slate-600">
                Combined projected revenue from enabled future modules
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-purple-600">
                ${totalFutureRevenue.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
              <div className="text-sm text-slate-500">Monthly Revenue</div>
            </div>
            <div className="text-right">
              <div className={`text-2xl font-bold ${totalFutureProfit >= 0 ? 'text-emerald-600' : 'text-red-500'}`}>
                ${totalFutureProfit.toLocaleString(undefined, { maximumFractionDigits: 0 })}
              </div>
              <div className="text-sm text-slate-500">Monthly Profit</div>
            </div>
          </div>
        </div>
      )}

      {/* Module Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        {/* VChain */}
        <ModuleCard
          title="VChain Network"
          icon="🔗"
          enabled={isVchainEnabled}
          launched={vchain?.launched || false}
          launchMonth={vchain?.launchMonth || defaults.vchain.vchainLaunchMonth}
          monthsUntilLaunch={vchain?.monthsUntilLaunch || (defaults.vchain.vchainLaunchMonth - 1)}
          revenue={vchain?.revenue || 0}
          profit={vchain?.profit || 0}
          margin={vchain?.margin || 0}
          description="Cross-chain network for seamless blockchain interoperability"
          metrics={vchain?.launched ? [
            { label: 'Monthly TX Volume', value: `$${((vchain.monthlyTxVolume || 0) / 1_000_000).toFixed(1)}M` },
            { label: 'Bridge Volume', value: `$${((vchain.monthlyBridgeVolume || 0) / 1_000_000).toFixed(1)}M` },
            { label: 'Active Validators', value: (vchain.validatorsActive || 0).toString() },
            { label: 'Enterprise Clients', value: (vchain.activeEnterpriseClients || 0).toString() },
          ] : []}
        />

        {/* Marketplace */}
        <ModuleCard
          title="Marketplace"
          icon="🛒"
          enabled={isMarketplaceEnabled}
          launched={marketplace?.launched || false}
          launchMonth={marketplace?.launchMonth || defaults.marketplace.marketplaceLaunchMonth}
          monthsUntilLaunch={marketplace?.monthsUntilLaunch || (defaults.marketplace.marketplaceLaunchMonth - 1)}
          revenue={marketplace?.revenue || 0}
          profit={marketplace?.profit || 0}
          margin={marketplace?.margin || 0}
          description="Physical & digital goods marketplace with crypto payments"
          metrics={marketplace?.launched ? [
            { label: 'Monthly GMV', value: `$${((marketplace.monthlyGmv || 0) / 1_000_000).toFixed(1)}M` },
            { label: 'Active Sellers', value: (marketplace.activeSellers || 0).toLocaleString() },
            { label: 'Commission Revenue', value: `$${(marketplace.commissionRevenue || 0).toLocaleString()}` },
          ] : []}
        />

        {/* Business Hub */}
        <ModuleCard
          title="Business Hub"
          icon="💼"
          enabled={isBusinessHubEnabled}
          launched={businessHub?.launched || false}
          launchMonth={businessHub?.launchMonth || defaults.businessHub.businessHubLaunchMonth}
          monthsUntilLaunch={businessHub?.monthsUntilLaunch || (defaults.businessHub.businessHubLaunchMonth - 1)}
          revenue={businessHub?.revenue || 0}
          profit={businessHub?.profit || 0}
          margin={businessHub?.margin || 0}
          description="Freelancer platform, startup launchpad, and project management"
          metrics={businessHub?.launched ? [
            { label: 'Active Freelancers', value: (businessHub.activeFreelancers || 0).toLocaleString() },
            { label: 'Freelance Volume', value: `$${((businessHub.monthlyFreelanceVolume || 0) / 1_000).toFixed(0)}K` },
            { label: 'Funding Volume', value: `$${((businessHub.monthlyFundingVolume || 0) / 1_000_000).toFixed(1)}M` },
            { label: 'PM Users', value: (businessHub.pmTotalUsers || 0).toLocaleString() },
          ] : []}
        />

        {/* Cross-Platform */}
        <ModuleCard
          title="Cross-Platform"
          icon="🌐"
          enabled={isCrossPlatformEnabled}
          launched={crossPlatform?.launched || false}
          launchMonth={crossPlatform?.launchMonth || defaults.crossPlatform.crossPlatformLaunchMonth}
          monthsUntilLaunch={crossPlatform?.monthsUntilLaunch || (defaults.crossPlatform.crossPlatformLaunchMonth - 1)}
          revenue={crossPlatform?.revenue || 0}
          profit={crossPlatform?.profit || 0}
          margin={crossPlatform?.margin || 0}
          description="Content sharing, account renting, and cross-platform syndication"
          metrics={crossPlatform?.launched ? [
            { label: 'Total Subscribers', value: (crossPlatform.totalSubscribers || 0).toLocaleString() },
            { label: 'Monthly Rentals', value: `$${((crossPlatform.monthlyRentalVolume || 0) / 1_000).toFixed(0)}K` },
            { label: 'Active Renters', value: (crossPlatform.activeRenters || 0).toLocaleString() },
            { label: 'Rental Revenue', value: `$${(crossPlatform.rentalRevenue || 0).toLocaleString()}` },
          ] : []}
        />
      </div>

      {/* Timeline */}
      <div className="bg-slate-50 rounded-xl p-5">
        <h3 className="font-semibold text-slate-800 mb-4 flex items-center gap-2">
          📅 Launch Timeline
        </h3>
        <div className="relative">
          <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-slate-200"></div>
          <div className="space-y-4">
            {[
              { month: 15, name: 'Cross-Platform', icon: '🌐', desc: 'Content sharing & account renting' },
              { month: 18, name: 'Marketplace', icon: '🛒', desc: 'Physical & digital goods' },
              { month: 21, name: 'Business Hub', icon: '💼', desc: 'Freelancer & startup ecosystem' },
              { month: 24, name: 'VChain Network', icon: '🔗', desc: 'Cross-chain infrastructure' },
            ].map((item, idx) => (
              <div key={idx} className="relative pl-10">
                <div className="absolute left-2 w-4 h-4 rounded-full bg-white border-2 border-slate-300"></div>
                <div className="flex items-center gap-3">
                  <span className="text-xl">{item.icon}</span>
                  <div>
                    <div className="font-medium text-slate-700">
                      Month {item.month}: {item.name}
                    </div>
                    <div className="text-xs text-slate-500">{item.desc}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

