'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface IdentityBreakdown {
  tierRevenue?: number;
  transferRevenue?: number;
  saleRevenue?: number;
  monthlyTransfers?: number;
  basicUsers?: number;
  verifiedUsers?: number;
  premiumUsers?: number;
  enterpriseUsers?: number;
}

interface IdentitySectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function IdentitySection({ result, parameters }: IdentitySectionProps) {
  const { identity } = result;
  const breakdown = (identity.breakdown || {}) as IdentityBreakdown;
  
  const tiers = [
    { 
      name: 'Basic', 
      price: parameters.basicPrice, 
      icon: '🏷️',
      color: 'bg-gray-100 border-gray-300',
      features: ['Unique @handle', 'Basic profile', 'Standard support']
    },
    { 
      name: 'Verified', 
      price: parameters.verifiedPrice, 
      icon: '✅',
      color: 'bg-blue-50 border-blue-300',
      features: ['Verification badge', 'Priority support', 'Enhanced profile']
    },
    { 
      name: 'Premium', 
      price: parameters.premiumPrice, 
      icon: '⭐',
      color: 'bg-purple-50 border-purple-300',
      features: ['Custom badge colors', 'Premium analytics', 'Early access features']
    },
    { 
      name: 'Enterprise', 
      price: parameters.enterprisePrice, 
      icon: '🏢',
      color: 'bg-amber-50 border-amber-300',
      features: ['Multi-user management', 'API access', 'Dedicated support']
    },
  ];

  return (
    <section className="space-y-8">
      {/* Module Header */}
      <div className="bg-gradient-to-r from-violet-500 to-purple-600 rounded-2xl p-6 text-white">
        <div className="flex items-center gap-3 mb-4">
          <span className="text-4xl">🆔</span>
          <div>
            <h2 className="text-2xl font-bold">Identity Module</h2>
            <p className="text-violet-200">Digital identity verification and monetization</p>
          </div>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-6">
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(identity.revenue)}</div>
            <div className="text-xs text-violet-200 uppercase font-semibold">Revenue</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{formatCurrency(identity.costs)}</div>
            <div className="text-xs text-violet-200 uppercase font-semibold">Costs</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className={`text-2xl font-bold ${identity.profit >= 0 ? 'text-emerald-300' : 'text-red-300'}`}>
              {formatCurrency(identity.profit)}
            </div>
            <div className="text-xs text-violet-200 uppercase font-semibold">Profit</div>
          </div>
          <div className="bg-white/10 backdrop-blur-sm rounded-xl p-4 text-center">
            <div className="text-2xl font-bold">{identity.margin.toFixed(1)}%</div>
            <div className="text-xs text-violet-200 uppercase font-semibold">Margin</div>
          </div>
        </div>
      </div>

      {/* Pricing Tiers */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">💳 Identity Tier Pricing</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {tiers.map((tier) => (
            <div key={tier.name} className={`rounded-xl border-2 p-4 ${tier.color}`}>
              <div className="text-center mb-3">
                <span className="text-3xl">{tier.icon}</span>
                <h4 className="font-bold text-lg mt-2">{tier.name}</h4>
                <div className="text-2xl font-bold text-gray-900">{formatCurrency(tier.price)}</div>
                <div className="text-xs text-gray-500">one-time</div>
              </div>
              <ul className="space-y-2 text-sm">
                {tier.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-2">
                    <span className="text-emerald-500">✓</span>
                    {feature}
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      {/* Revenue Breakdown */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">📊 Revenue Breakdown</h3>
        
        {/* Issue #34 Fix: Added optional chaining to prevent runtime errors if breakdown is undefined */}
        {/* Revenue Sources */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200">
            <div className="text-sm text-emerald-600 mb-1">Tier Subscriptions</div>
            <div className="text-2xl font-bold text-emerald-700">{formatCurrency(breakdown.tierRevenue || 0)}</div>
            <div className="text-xs text-emerald-500">monthly recurring revenue</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
            <div className="text-sm text-blue-600 mb-1">Transfer Fee Revenue</div>
            <div className="text-2xl font-bold text-blue-700">{formatCurrency(breakdown.transferRevenue || 0)}</div>
            <div className="text-xs text-blue-500">{formatNumber(breakdown.monthlyTransfers || 0)} transfers @ {formatCurrency(parameters.transferFee)}/each</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 border border-purple-200">
            <div className="text-sm text-purple-600 mb-1">Sale Commission Revenue</div>
            <div className="text-2xl font-bold text-purple-700">{formatCurrency(breakdown.saleRevenue || 0)}</div>
            <div className="text-xs text-purple-500">{formatNumber(parameters.monthlySales)} sales @ {(parameters.saleCommission * 100).toFixed(0)}% commission</div>
          </div>
        </div>

        {/* Fee Settings */}
        <h4 className="font-semibold text-sm text-gray-500 uppercase mb-3">Fee Settings</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Transfer Fee</div>
            <div className="text-xl font-bold">{formatCurrency(parameters.transferFee)}</div>
            <div className="text-xs text-gray-500">per identity transfer</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Sale Commission</div>
            <div className="text-xl font-bold">{(parameters.saleCommission * 100).toFixed(0)}%</div>
            <div className="text-xs text-gray-500">on marketplace sales</div>
          </div>
          <div className="bg-gray-50 rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Monthly Sales</div>
            <div className="text-xl font-bold">{formatNumber(parameters.monthlySales)}</div>
            <div className="text-xs text-gray-500">estimated transactions</div>
          </div>
        </div>
      </div>

      {/* User Distribution */}
      <div className="bg-white rounded-xl border border-gray-200 p-6">
        <h3 className="font-bold text-lg mb-4">👥 User Distribution</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-gray-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-gray-700">{formatNumber(breakdown.basicUsers || 0)}</div>
            <div className="text-xs text-gray-500 uppercase font-semibold">Basic (Free)</div>
          </div>
          <div className="bg-blue-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-blue-700">{formatNumber(breakdown.verifiedUsers || 0)}</div>
            <div className="text-xs text-blue-500 uppercase font-semibold">Verified</div>
          </div>
          <div className="bg-purple-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-purple-700">{formatNumber(breakdown.premiumUsers || 0)}</div>
            <div className="text-xs text-purple-500 uppercase font-semibold">Premium</div>
          </div>
          <div className="bg-amber-50 rounded-lg p-4 text-center">
            <div className="text-2xl font-bold text-amber-700">{formatNumber(breakdown.enterpriseUsers || 0)}</div>
            <div className="text-xs text-amber-500 uppercase font-semibold">Enterprise</div>
          </div>
        </div>
      </div>
    </section>
  );
}


