'use client';

import React from 'react';
import { RetentionModelType } from '@/types/simulation';
import { CONFIG } from '@/lib/constants';

interface RetentionModelSelectorProps {
  modelType: RetentionModelType;
  onModelTypeChange: (model: RetentionModelType) => void;
  platformAge: number;
  onPlatformAgeChange: (age: number) => void;
  applyRetention: boolean;
  onApplyRetentionChange: (apply: boolean) => void;
}

const RETENTION_MODELS: { id: RetentionModelType; name: string; icon: string; description: string }[] = [
  {
    id: 'social_app',
    name: 'Social App',
    icon: '📱',
    description: 'Standard social media retention (Instagram/TikTok-like)',
  },
  {
    id: 'crypto_app',
    name: 'Crypto App',
    icon: '🪙',
    description: 'Lower retention due to market volatility',
  },
  {
    id: 'gaming',
    name: 'Gaming',
    icon: '🎮',
    description: 'Variable retention with engagement spikes',
  },
  {
    id: 'utility',
    name: 'Utility',
    icon: '⚙️',
    description: 'Higher retention for essential tools',
  },
];

export const RetentionModelSelector: React.FC<RetentionModelSelectorProps> = ({
  modelType,
  onModelTypeChange,
  platformAge,
  onPlatformAgeChange,
  applyRetention,
  onApplyRetentionChange,
}) => {
  const currentCurve = CONFIG.RETENTION_CURVES[modelType] || CONFIG.RETENTION_CURVES.social_app;

  return (
    <div className="bg-slate-800/50 rounded-lg p-4 border border-slate-700">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <span className="text-xl">📉</span>
          Retention Model
        </h3>
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={applyRetention}
            onChange={(e) => onApplyRetentionChange(e.target.checked)}
            className="w-4 h-4 rounded border-slate-600 bg-slate-700 text-emerald-500 focus:ring-emerald-500"
          />
          <span className="text-sm text-slate-300">Apply retention</span>
        </label>
      </div>

      {applyRetention && (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-2 mb-4">
            {RETENTION_MODELS.map((model) => (
              <button
                key={model.id}
                onClick={() => onModelTypeChange(model.id)}
                className={`
                  p-2 rounded-lg border transition-all text-left
                  ${modelType === model.id
                    ? 'border-emerald-500 bg-emerald-500/10'
                    : 'border-slate-600 bg-slate-700/50 hover:border-slate-500'
                  }
                `}
              >
                <div className="flex items-center gap-1 mb-1">
                  <span>{model.icon}</span>
                  <span className={`text-sm font-medium ${modelType === model.id ? 'text-emerald-400' : 'text-white'}`}>
                    {model.name}
                  </span>
                </div>
                <p className="text-xs text-slate-400 line-clamp-2">{model.description}</p>
              </button>
            ))}
          </div>

          <div className="mb-4">
            <label className="flex items-center justify-between text-sm text-slate-300 mb-2">
              <span>Platform Age (months)</span>
              <span className="text-emerald-400 font-mono">{platformAge}</span>
            </label>
            <input
              type="range"
              min={1}
              max={60}
              value={platformAge}
              onChange={(e) => onPlatformAgeChange(parseInt(e.target.value))}
              className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>1 month</span>
              <span>5 years</span>
            </div>
          </div>

          <div className="bg-slate-700/50 rounded-lg p-3 border border-slate-600">
            <h4 className="text-sm font-medium text-slate-300 mb-2">Retention Curve Preview:</h4>
            <div className="flex items-end gap-1 h-16">
              {Object.entries(currentCurve).map(([month, rate]) => (
                <div key={month} className="flex-1 flex flex-col items-center">
                  <div
                    className="w-full bg-emerald-500/70 rounded-t"
                    style={{ height: `${rate * 100 * 2.5}px` }}
                  />
                  <span className="text-[10px] text-slate-500 mt-1">M{month}</span>
                </div>
              ))}
            </div>
            <div className="grid grid-cols-4 gap-2 mt-3 text-xs">
              {Object.entries(currentCurve).map(([month, rate]) => (
                <div key={month} className="text-center">
                  <span className="text-slate-400">Month {month}:</span>
                  <span className="text-emerald-400 ml-1">{(rate * 100).toFixed(0)}%</span>
                </div>
              ))}
            </div>
          </div>
        </>
      )}

      {!applyRetention && (
        <p className="text-sm text-amber-400/80 bg-amber-500/10 p-3 rounded-lg border border-amber-500/30">
          ⚠️ Without retention modeling, user counts will be inflated by 5-10x.
          Industry data shows only 3-4% of acquired users remain active after 12 months.
        </p>
      )}

      <p className="text-xs text-slate-500 mt-3">
        Retention curves based on App Annie, AppsFlyer, and Adjust 2024 benchmarks.
      </p>
    </div>
  );
};

export default RetentionModelSelector;

