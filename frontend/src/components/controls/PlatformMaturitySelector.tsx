'use client';

import React from 'react';
import { PlatformMaturity } from '@/types/simulation';
import { MATURITY_ADJUSTMENTS } from '@/lib/constants';

interface PlatformMaturitySelectorProps {
  value: PlatformMaturity;
  onChange: (maturity: PlatformMaturity) => void;
  autoAdjust: boolean;
  onAutoAdjustChange: (autoAdjust: boolean) => void;
}

const MATURITY_TIERS: { id: PlatformMaturity; name: string; icon: string; description: string }[] = [
  {
    id: 'launch',
    name: 'Launch Phase',
    icon: '🚀',
    description: '0-6 months: New platform, building brand recognition',
  },
  {
    id: 'growing',
    name: 'Growth Phase',
    icon: '📈',
    description: '6-18 months: Gaining traction, improving metrics',
  },
  {
    id: 'established',
    name: 'Established',
    icon: '🏢',
    description: '18+ months: Mature platform with industry-standard rates',
  },
];

export const PlatformMaturitySelector: React.FC<PlatformMaturitySelectorProps> = ({
  value,
  onChange,
  autoAdjust,
  onAutoAdjustChange,
}) => {
  const currentAdjustments = MATURITY_ADJUSTMENTS[value];

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="text-xl">🎯</span>
          Platform Maturity
        </h3>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={autoAdjust}
            onChange={(e) => onAutoAdjustChange(e.target.checked)}
            className="w-4 h-4 rounded border-slate-600 bg-slate-700 text-emerald-500 focus:ring-emerald-500"
          />
          <span className="text-sm text-slate-300">Auto-adjust parameters</span>
        </label>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-4">
        {MATURITY_TIERS.map((tier) => (
          <button
            key={tier.id}
            onClick={() => onChange(tier.id)}
            className={`
              p-3 rounded-lg border-2 transition-all text-left
              ${value === tier.id
                ? 'border-emerald-500 bg-emerald-500/10'
                : 'border-slate-600 bg-slate-700/50 hover:border-slate-500'
              }
            `}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xl">{tier.icon}</span>
              <span className={`font-medium ${value === tier.id ? 'text-emerald-400' : 'text-white'}`}>
                {tier.name}
              </span>
            </div>
            <p className="text-xs text-slate-400">{tier.description}</p>
          </button>
        ))}
      </div>

      {autoAdjust && (
        <div className="bg-slate-700/50 rounded-lg p-3 border border-slate-600">
          <h4 className="text-sm font-medium text-slate-300 mb-2">
            Parameter Adjustments for {MATURITY_TIERS.find(t => t.id === value)?.name}:
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-2 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Conversion Rate:</span>
              <span className="text-emerald-400">{(currentAdjustments.conversionRate * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Ad Fill Rate:</span>
              <span className="text-emerald-400">{(currentAdjustments.adFillRate * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Banner CPM:</span>
              <span className="text-emerald-400">${currentAdjustments.bannerCpm.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Video CPM:</span>
              <span className="text-emerald-400">${currentAdjustments.videoCpm.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Creator %:</span>
              <span className="text-emerald-400">{(currentAdjustments.creatorPercentage * 100).toFixed(0)}%</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">CAC Multiplier:</span>
              <span className="text-amber-400">{currentAdjustments.cacMultiplier}x</span>
            </div>
          </div>
        </div>
      )}

      <p className="text-xs text-slate-500 mt-3">
        Platform maturity affects realistic expectations for CAC, conversion rates, CPM, and more.
        Based on 2024-2025 industry benchmarks.
      </p>
    </div>
  );
};

export default PlatformMaturitySelector;

