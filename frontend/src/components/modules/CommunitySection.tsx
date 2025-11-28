'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface CommunitySectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function CommunitySection({ result, parameters }: CommunitySectionProps) {
  const { community } = result;

  const tiers = [
    { 
      name: 'Small Community', 
      price: parameters.smallCommunityFee, 
      icon: '👥',
      members: '< 1,000',
      color: 'bg-emerald-50 border-emerald-300'
    },
    { 
      name: 'Medium Community', 
      price: parameters.mediumCommunityFee, 
      icon: '🏘️',
      members: '1K - 10K',
      color: 'bg-blue-50 border-blue-300'
    },
    { 
      name: 'Large Community', 
      price: parameters.largeCommunityFee, 
      icon: '🏙️',
      members: '10K - 100K',
      color: 'bg-purple-50 border-purple-300'
    },
    { 
      name: 'Enterprise', 
      price: parameters.enterpriseCommunityFee, 
      icon: '🌐',
      members: '100K+',
      color: 'bg-amber-50 border-amber-300'
    },
  ];

  if (!parameters.enableCommunity) {
    return (
      <section className="space-y-8">
        <div className="bg-gray-100 rounded-2xl p-8 text-center">
          <span className="text-6xl mb-4 block">👥</span>
          <h2 className="text-2xl font-bold text-gray-600">Community Module Disabled</h2>
          <p className="text-gray-500 mt-2">Enable this module in the controls to see community analytics.</p>
        </div>
      </section>
    );
  }

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-emerald-500 to-teal-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">👥</span>
          <div>
            <h2 className="text-2xl font-bold">Community Module</h2>
            <p className="text-emerald-200">Community creation and management fees</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(community.revenue)}</div>
            <div className="text-xs text-emerald-200 uppercase font-semibold">Revenue</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(community.costs)}</div>
            <div className="text-xs text-emerald-200 uppercase font-semibold">Costs</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${community.profit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(community.profit)}
            </div>
            <div className="text-xs text-emerald-200 uppercase font-semibold">Profit</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{community.margin.toFixed(1)}%</div>
            <div className="text-xs text-emerald-200 uppercase font-semibold">Margin</div>
          </div>
        </div>
      </div>

      {/* Community Tiers */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🏠 Community Hosting Tiers</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {tiers.map((tier) => (
            <div key={tier.name} className={`rounded-xl border-2 p-4 ${tier.color}`}>
              <div className="text-center mb-3">
                <span className="text-3xl">{tier.icon}</span>
                <h4 className="font-bold text-lg mt-2">{tier.name}</h4>
                <div className="text-sm text-gray-500">{tier.members} members</div>
                <div className="text-2xl font-bold text-gray-900 mt-2">
                  {formatCurrency(tier.price)}
                </div>
                <div className="text-xs text-gray-500">per month</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Additional Services */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🛠️ Additional Services</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="text-2xl mb-2">🎉</div>
            <div className="font-semibold">Event Hosting</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">
              {formatCurrency(parameters.eventHostingFee)}
            </div>
            <div className="text-xs text-gray-500">per event</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="text-2xl mb-2">✅</div>
            <div className="font-semibold">Verification</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">
              {formatCurrency(parameters.communityVerificationFee)}
            </div>
            <div className="text-xs text-gray-500">one-time</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="text-2xl mb-2">📊</div>
            <div className="font-semibold">Analytics</div>
            <div className="text-2xl font-bold text-gray-900 mt-1">
              {formatCurrency(parameters.communityAnalyticsFee)}
            </div>
            <div className="text-xs text-gray-500">per month</div>
          </div>
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Revenue Breakdown</h3>
        <div className="space-y-4">
          {Object.entries(community.breakdown).map(([key, value]) => (
            <div key={key} className="flex items-center justify-between py-2 border-b border-gray-100 last:border-0">
              <span className="text-gray-600 capitalize">{key.replace(/_/g, ' ')}</span>
              <span className="font-semibold">{formatCurrency(value)}</span>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}




