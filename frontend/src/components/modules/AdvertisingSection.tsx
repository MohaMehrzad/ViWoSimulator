'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface AdvertisingSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function AdvertisingSection({ result, parameters }: AdvertisingSectionProps) {
  const { advertising, customerAcquisition } = result;

  if (!parameters.enableAdvertising) {
    return (
      <section className="space-y-8">
        <div className="bg-gray-100 rounded-2xl p-8 text-center">
          <span className="text-6xl mb-4 block">📢</span>
          <h2 className="text-2xl font-bold text-gray-600">Advertising Module Disabled</h2>
          <p className="text-gray-500 mt-2">Enable this module in the controls to see advertising analytics.</p>
        </div>
      </section>
    );
  }

  const adFormats = [
    { 
      name: 'Banner Ads', 
      cpm: parameters.bannerCPM, 
      icon: '🖼️',
      description: 'Standard display banners'
    },
    { 
      name: 'Video Ads', 
      cpm: parameters.videoCPM, 
      icon: '🎬',
      description: 'Pre-roll and mid-roll video'
    },
    { 
      name: 'Promoted Posts', 
      price: parameters.promotedPostFee, 
      icon: '📌',
      description: 'Boosted content visibility',
      isPer: 'post'
    },
  ];

  // Estimate impressions based on user count
  const estimatedMonthlyImpressions = customerAcquisition.totalUsers * 30 * 5; // 5 impressions per day per user

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">📢</span>
          <div>
            <h2 className="text-2xl font-bold">Advertising Module</h2>
            <p className="text-blue-200">Ad placements and campaign management</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(advertising.revenue)}</div>
            <div className="text-xs text-blue-200 uppercase font-semibold">Revenue</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(advertising.costs)}</div>
            <div className="text-xs text-blue-200 uppercase font-semibold">Costs</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${advertising.profit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(advertising.profit)}
            </div>
            <div className="text-xs text-blue-200 uppercase font-semibold">Profit</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{advertising.margin.toFixed(1)}%</div>
            <div className="text-xs text-blue-200 uppercase font-semibold">Margin</div>
          </div>
        </div>
      </div>

      {/* Ad Formats */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📺 Ad Formats & Pricing</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {adFormats.map((format) => (
            <div key={format.name} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
              <div className="text-center">
                <span className="text-4xl">{format.icon}</span>
                <h4 className="font-bold text-lg mt-2">{format.name}</h4>
                <div className="text-sm text-gray-500 mb-2">{format.description}</div>
                <div className="text-2xl font-bold text-gray-900">
                  {formatCurrency(format.cpm || format.price || 0)}
                </div>
                <div className="text-xs text-gray-500">
                  {format.cpm ? 'CPM (per 1,000 impressions)' : `per ${format.isPer}`}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Campaign Services */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🎯 Campaign Services</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🛠️</span>
              <div>
                <div className="font-semibold">Campaign Management</div>
                <div className="text-2xl font-bold text-blue-700">
                  {formatCurrency(parameters.campaignManagementFee)}
                </div>
                <div className="text-xs text-blue-500">per campaign</div>
              </div>
            </div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="flex items-center gap-3">
              <span className="text-2xl">📊</span>
              <div>
                <div className="font-semibold">Ad Analytics</div>
                <div className="text-2xl font-bold text-purple-700">
                  {formatCurrency(parameters.adAnalyticsFee)}
                </div>
                <div className="text-xs text-purple-500">per month</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Inventory Stats */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📈 Ad Inventory Estimates</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatNumber(estimatedMonthlyImpressions)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Monthly Impressions</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {formatNumber(customerAcquisition.totalUsers)}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Reachable Users</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-emerald-600">
              {formatCurrency(advertising.revenue / (estimatedMonthlyImpressions / 1000))}
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">Effective CPM</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-600">
              {parameters.adCPMMultiplier}x
            </div>
            <div className="text-xs text-gray-600 uppercase font-semibold">CPM Multiplier</div>
          </div>
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Revenue Breakdown</h3>
        <div className="space-y-4">
          {Object.entries(advertising.breakdown).map(([key, value]) => (
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




