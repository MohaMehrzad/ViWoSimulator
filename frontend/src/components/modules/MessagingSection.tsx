'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface MessagingSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function MessagingSection({ result, parameters }: MessagingSectionProps) {
  const { messaging } = result;

  if (!parameters.enableMessaging) {
    return (
      <section className="space-y-8">
        <div className="bg-gray-100 rounded-2xl p-8 text-center">
          <span className="text-6xl mb-4 block">💬</span>
          <h2 className="text-2xl font-bold text-gray-600">Messaging Module Disabled</h2>
          <p className="text-gray-500 mt-2">Enable this module in the controls to see messaging analytics.</p>
        </div>
      </section>
    );
  }

  const messagingFeatures = [
    { 
      name: 'Encrypted DMs', 
      price: parameters.encryptedDMFee, 
      icon: '🔒',
      description: 'End-to-end encrypted direct messages',
      period: 'per month'
    },
    { 
      name: 'Group Chats', 
      price: parameters.groupChatFee, 
      icon: '👥',
      description: 'Private group conversations',
      period: 'per month'
    },
    { 
      name: 'File Transfer', 
      price: parameters.fileTransferFee, 
      icon: '📁',
      description: 'Large file sharing capability',
      period: 'per GB'
    },
    { 
      name: 'Voice Calls', 
      price: parameters.voiceCallFee, 
      icon: '📞',
      description: 'Voice and video calling',
      period: 'per minute'
    },
    { 
      name: 'Message Storage', 
      price: parameters.messageStorageFee, 
      icon: '💾',
      description: 'Extended message history',
      period: 'per month'
    },
    { 
      name: 'Premium Messaging', 
      price: parameters.messagingPremiumFee, 
      icon: '⭐',
      description: 'All features bundled',
      period: 'per month'
    },
  ];

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-cyan-500 to-teal-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">💬</span>
          <div>
            <h2 className="text-2xl font-bold">Messaging Module</h2>
            <p className="text-cyan-200">Private communication and premium features</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(messaging.revenue)}</div>
            <div className="text-xs text-cyan-200 uppercase font-semibold">Revenue</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(messaging.costs)}</div>
            <div className="text-xs text-cyan-200 uppercase font-semibold">Costs</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${messaging.profit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(messaging.profit)}
            </div>
            <div className="text-xs text-cyan-200 uppercase font-semibold">Profit</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{messaging.margin.toFixed(1)}%</div>
            <div className="text-xs text-cyan-200 uppercase font-semibold">Margin</div>
          </div>
        </div>
      </div>

      {/* Messaging Features */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📱 Messaging Features & Pricing</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {messagingFeatures.map((feature) => (
            <div key={feature.name} className="bg-gray-50 rounded-xl p-4 border border-gray-200">
              <div className="flex items-start gap-3">
                <span className="text-3xl">{feature.icon}</span>
                <div className="flex-1">
                  <h4 className="font-bold">{feature.name}</h4>
                  <div className="text-sm text-gray-500 mb-2">{feature.description}</div>
                  <div className="text-xl font-bold text-gray-900">
                    {formatCurrency(feature.price)}
                  </div>
                  <div className="text-xs text-gray-500">{feature.period}</div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Premium Bundle */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">⭐ Premium Bundle</h3>
        <div className="bg-gradient-to-r from-cyan-50 to-teal-50 rounded-xl p-6 border-2 border-cyan-200">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <div>
              <h4 className="text-xl font-bold text-cyan-800">Messaging Premium</h4>
              <p className="text-cyan-600">All messaging features in one subscription</p>
              <ul className="mt-3 space-y-1 text-sm text-cyan-700">
                <li>✓ Unlimited encrypted DMs</li>
                <li>✓ Unlimited group chats</li>
                <li>✓ 10GB file transfer/month</li>
                <li>✓ Voice & video calls</li>
                <li>✓ Extended message history</li>
              </ul>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold text-cyan-800">
                {formatCurrency(parameters.messagingPremiumFee)}
              </div>
              <div className="text-sm text-cyan-600">per month</div>
            </div>
          </div>
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Revenue Breakdown</h3>
        <div className="space-y-4">
          {Object.entries(messaging.breakdown).map(([key, value]) => (
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




