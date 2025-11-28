'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface RecaptureSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function RecaptureSection({ result, parameters }: RecaptureSectionProps) {
  const { recapture, rewards } = result;

  const recaptureFlows = [
    { 
      name: 'Burns', 
      amount: recapture.burns, 
      icon: '🔥', 
      color: 'bg-red-500',
      description: 'Destroyed from collected fees',
      rate: parameters.burnRate,
      rateLabel: 'Burn Rate'
    },
    { 
      name: 'Buybacks', 
      amount: recapture.buybacks, 
      icon: '💰', 
      color: 'bg-purple-500',
      description: `Bought from market ($${(recapture.buybackUsdSpent || 0).toLocaleString()} spent)`,
      rate: parameters.buybackPercent,
      rateLabel: '% of Revenue'
    },
    { 
      name: 'Staking', 
      amount: recapture.staking, 
      icon: '🔒', 
      color: 'bg-blue-500',
      description: 'Tokens locked in staking',
      rate: null,
      rateLabel: null
    },
    { 
      name: 'Treasury', 
      amount: recapture.treasury, 
      icon: '🏦', 
      color: 'bg-amber-500',
      description: 'Tokens held in protocol treasury',
      rate: null,
      rateLabel: null
    },
  ];

  const netEmission = rewards.monthlyEmission - recapture.totalRecaptured;
  const isDeflationary = netEmission < 0;

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-cyan-500 to-blue-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">🔄</span>
          <div>
            <h2 className="text-2xl font-bold">Recapture Flow</h2>
            <p className="text-cyan-200">Token emission and recapture mechanisms</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatNumber(rewards.monthlyEmission)}</div>
            <div className="text-xs text-cyan-200 uppercase font-semibold">Monthly Emission</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatNumber(recapture.totalRecaptured)}</div>
            <div className="text-xs text-cyan-200 uppercase font-semibold">Total Recaptured</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${recapture.recaptureRate >= 100 ? 'text-emerald-300' : 'text-amber-300'}`}>
              {recapture.recaptureRate.toFixed(1)}%
            </div>
            <div className="text-xs text-cyan-200 uppercase font-semibold">Recapture Rate</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${isDeflationary ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatNumber(Math.abs(netEmission))}
            </div>
            <div className="text-xs text-cyan-200 uppercase font-semibold">
              {isDeflationary ? 'Net Deflationary' : 'Net Inflation'}
            </div>
          </div>
        </div>
      </div>

      {/* Flow Visualization */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Recapture Flow Breakdown</h3>
        
        {/* Emission Bar */}
        <div className="mb-6">
          <div className="flex justify-between text-sm mb-2">
            <span className="font-semibold">Monthly Emission</span>
            <span>{formatNumber(rewards.monthlyEmission)} VCoin</span>
          </div>
          <div className="h-12 bg-gray-100 rounded-lg overflow-hidden flex">
            {recaptureFlows.map((flow) => {
              const percent = (flow.amount / rewards.monthlyEmission) * 100;
              if (percent < 0.5) return null;
              return (
                <div 
                  key={flow.name}
                  className={`${flow.color} flex items-center justify-center text-white text-xs font-bold transition-all hover:brightness-110`}
                  style={{ width: `${percent}%` }}
                  title={`${flow.name}: ${formatNumber(flow.amount)} VCoin (${percent.toFixed(1)}%)`}
                >
                  {percent > 5 && `${percent.toFixed(0)}%`}
                </div>
              );
            })}
            <div 
              className="bg-gray-400 flex items-center justify-center text-white text-xs font-bold flex-1"
              title={`Net Circulation: ${formatNumber(netEmission)} VCoin`}
            >
              Net
            </div>
          </div>
        </div>

        {/* Flow Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {recaptureFlows.map((flow) => (
            <div key={flow.name} className="bg-gray-50 rounded-lg p-4 border border-gray-200">
              <div className="flex items-center gap-2 mb-2">
                <div className={`w-8 h-8 ${flow.color} rounded-lg flex items-center justify-center text-white`}>
                  {flow.icon}
                </div>
                <span className="font-semibold">{flow.name}</span>
              </div>
              <div className="text-2xl font-bold text-gray-900">
                {formatNumber(flow.amount)}
              </div>
              <div className="text-xs text-gray-500 mb-2">
                {formatCurrency(flow.amount * parameters.tokenPrice)}
              </div>
              <div className="text-xs text-gray-600">{flow.description}</div>
              {flow.rate !== null && (
                <div className="mt-2 text-xs bg-gray-200 rounded px-2 py-1 inline-block">
                  {flow.rateLabel}: {(flow.rate * 100).toFixed(0)}%
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Revenue Sources */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💵 Revenue Sources (VCoin)</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Total Revenue VCoin</div>
            <div className="text-2xl font-bold text-emerald-700">
              {formatNumber(recapture.totalRevenueSourceVcoin)}
            </div>
            <div className="text-xs text-emerald-500">
              {formatCurrency(recapture.totalRevenueSourceVcoin * parameters.tokenPrice)}
            </div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="text-sm text-blue-600 mb-1">Transaction Fees</div>
            <div className="text-2xl font-bold text-blue-700">
              {formatCurrency(recapture.totalTransactionFeesUsd)}
            </div>
            <div className="text-xs text-blue-500">
              Collected from platform transactions
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="text-sm text-purple-600 mb-1">Royalties</div>
            <div className="text-2xl font-bold text-purple-700">
              {formatCurrency(recapture.totalRoyaltiesUsd)}
            </div>
            <div className="text-xs text-purple-500">
              From content sales and NFTs
            </div>
          </div>
        </div>
      </div>

      {/* Health Indicator */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🏥 Token Health Status</h3>
        <div className={`rounded-xl p-6 ${
          recapture.recaptureRate >= 100 
            ? 'bg-emerald-50 border border-emerald-200' 
            : recapture.recaptureRate >= 80 
              ? 'bg-amber-50 border border-amber-200'
              : 'bg-red-50 border border-red-200'
        }`}>
          <div className="flex items-center gap-4">
            <div className="text-4xl">
              {recapture.recaptureRate >= 100 ? '✅' : recapture.recaptureRate >= 80 ? '⚠️' : '🚨'}
            </div>
            <div>
              <div className={`font-bold text-lg ${
                recapture.recaptureRate >= 100 
                  ? 'text-emerald-700' 
                  : recapture.recaptureRate >= 80 
                    ? 'text-amber-700'
                    : 'text-red-700'
              }`}>
                {recapture.recaptureRate >= 100 
                  ? 'Deflationary Economy' 
                  : recapture.recaptureRate >= 80 
                    ? 'Near-Neutral Economy'
                    : 'Inflationary Warning'}
              </div>
              <div className="text-sm text-gray-600">
                {recapture.recaptureRate >= 100 
                  ? `${formatNumber(Math.abs(netEmission))} VCoin removed from circulation monthly` 
                  : recapture.recaptureRate >= 80 
                    ? 'Economy is close to sustainable levels'
                    : `${formatNumber(netEmission)} VCoin added to circulation monthly`}
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}


