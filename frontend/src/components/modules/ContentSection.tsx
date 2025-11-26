'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface ContentSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function ContentSection({ result, parameters }: ContentSectionProps) {
  const { content } = result;
  
  const contentTypes = [
    { 
      name: 'Text Posts', 
      fee: parameters.textPostFeeVcoin, 
      icon: '📝',
      color: 'text-blue-500'
    },
    { 
      name: 'Image Posts', 
      fee: parameters.imagePostFeeVcoin, 
      icon: '🖼️',
      color: 'text-pink-500'
    },
    { 
      name: 'Video Posts', 
      fee: parameters.videoPostFeeVcoin, 
      icon: '🎬',
      color: 'text-purple-500'
    },
    { 
      name: 'NFT Mints', 
      fee: parameters.nftMintFeeVcoin, 
      icon: '🎨',
      color: 'text-amber-500'
    },
  ];

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-pink-500 to-rose-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">📄</span>
          <div>
            <h2 className="text-2xl font-bold">Content Module</h2>
            <p className="text-pink-200">Content creation fees and marketplace</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(content.revenue)}</div>
            <div className="text-xs text-pink-200 uppercase font-semibold">Revenue</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(content.costs)}</div>
            <div className="text-xs text-pink-200 uppercase font-semibold">Costs</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${content.profit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(content.profit)}
            </div>
            <div className="text-xs text-pink-200 uppercase font-semibold">Profit</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{content.margin.toFixed(1)}%</div>
            <div className="text-xs text-pink-200 uppercase font-semibold">Margin</div>
          </div>
        </div>
      </div>

      {/* Content Fees */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💰 Content Creation Fees (VCoin)</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {contentTypes.map((type) => (
            <div key={type.name} className="bg-gray-50 rounded-xl p-4 text-center border border-gray-200">
              <span className={`text-4xl ${type.color}`}>{type.icon}</span>
              <h4 className="font-semibold mt-2">{type.name}</h4>
              <div className="text-2xl font-bold text-gray-900 mt-1">
                {type.fee} <span className="text-sm text-gray-500">VCoin</span>
              </div>
              <div className="text-xs text-gray-500 mt-1">
                ≈ {formatCurrency(type.fee * parameters.tokenPrice)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Marketplace Stats */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">🏪 Marketplace Activity</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="text-sm text-purple-600 mb-1">Premium Content Volume</div>
            <div className="text-2xl font-bold text-purple-700">
              {formatNumber(parameters.premiumContentVolumeVcoin)} VCoin
            </div>
            <div className="text-xs text-purple-500">
              {formatCurrency(parameters.premiumContentVolumeVcoin * parameters.tokenPrice)} value
            </div>
          </div>
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Content Sale Volume</div>
            <div className="text-2xl font-bold text-emerald-700">
              {formatNumber(parameters.contentSaleVolumeVcoin)} VCoin
            </div>
            <div className="text-xs text-emerald-500">
              {formatCurrency(parameters.contentSaleVolumeVcoin * parameters.tokenPrice)} value
            </div>
          </div>
          <div className="bg-amber-50 rounded-lg p-4 border border-amber-200">
            <div className="text-sm text-amber-600 mb-1">Sale Commission</div>
            <div className="text-2xl font-bold text-amber-700">
              {(parameters.contentSaleCommission * 100).toFixed(0)}%
            </div>
            <div className="text-xs text-amber-500">on all marketplace sales</div>
          </div>
        </div>
      </div>

      {/* User Activity */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">👥 User Activity</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Posts Per User</div>
            <div className="text-xl font-bold">{parameters.postsPerUser}</div>
            <div className="text-xs text-gray-500">monthly average</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Total Users</div>
            <div className="text-xl font-bold">{formatNumber(result.customerAcquisition.totalUsers)}</div>
            <div className="text-xs text-gray-500">active monthly</div>
          </div>
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Revenue Breakdown</h3>
        <div className="space-y-4">
          {Object.entries(content.breakdown).map(([key, value]) => (
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


