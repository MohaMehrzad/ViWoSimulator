'use client';

import { SimulationResult, SimulationParameters } from '@/types/simulation';
import { formatNumber, formatCurrency } from '@/lib/utils';

interface OrganicGrowthSectionProps {
  result: SimulationResult;
  parameters: SimulationParameters;
}

export function OrganicGrowthSection({ result, parameters }: OrganicGrowthSectionProps) {
  const organicGrowth = result.organicGrowth;
  
  // If organic growth is not enabled or not available, show disabled state
  if (!organicGrowth || !organicGrowth.enabled) {
    return (
      <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
        <div className="flex items-center gap-3 mb-4">
          <div className="text-3xl">🌱</div>
          <div>
            <h2 className="text-xl font-bold text-white">Organic User Growth</h2>
            <span className="px-2 py-1 bg-gray-700 text-gray-400 text-xs rounded ml-2">Disabled</span>
          </div>
        </div>
        <p className="text-gray-500">
          Enable organic user growth to model natural acquisition through word-of-mouth, app store discovery,
          network effects, social sharing, and content virality. Based on industry benchmarks: 2-5% (conservative),
          5-10% (base), 10-15% (bullish) monthly organic growth.
        </p>
      </div>
    );
  }
  
  const totalOrganicUsers = organicGrowth.totalOrganicUsers || 0;
  const organicPercent = organicGrowth.organicPercentOfTotal || 0;
  
  // Calculate percentages for breakdown
  const womPercent = totalOrganicUsers > 0 ? (organicGrowth.wordOfMouthUsers / totalOrganicUsers) * 100 : 0;
  const appStorePercent = totalOrganicUsers > 0 ? (organicGrowth.appStoreDiscoveryUsers / totalOrganicUsers) * 100 : 0;
  const networkPercent = totalOrganicUsers > 0 ? (organicGrowth.networkEffectUsers / totalOrganicUsers) * 100 : 0;
  const socialPercent = totalOrganicUsers > 0 ? (organicGrowth.socialSharingUsers / totalOrganicUsers) * 100 : 0;
  const viralPercent = totalOrganicUsers > 0 ? (organicGrowth.contentViralityUsers / totalOrganicUsers) * 100 : 0;
  
  return (
    <div className="bg-gray-900 rounded-xl p-6 border border-gray-800">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className="text-3xl">🌱</div>
          <div>
            <h2 className="text-xl font-bold text-white">Organic User Growth</h2>
            <p className="text-sm text-gray-400">
              {formatNumber(totalOrganicUsers)} users | {organicPercent.toFixed(1)}% of total
            </p>
          </div>
          <span className="px-2 py-1 bg-green-700 text-green-200 text-xs rounded font-semibold">Active</span>
        </div>
        <div className="text-right">
          <div className="text-3xl font-bold text-green-400">
            {formatNumber(totalOrganicUsers)}
          </div>
          <div className="text-sm text-gray-400">Organic Users</div>
        </div>
      </div>
      
      {/* Overview Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-blue-400">
            {(organicGrowth.effectiveKFactor || 0).toFixed(2)}
          </div>
          <div className="text-xs text-gray-500">Effective K-Factor</div>
          <div className="text-xs text-gray-600 mt-1">Viral coefficient</div>
        </div>
        
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-purple-400">
            {((organicGrowth.averageMonthlyGrowthRate || 0) * 100).toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">Avg Monthly Growth</div>
          <div className="text-xs text-gray-600 mt-1">Organic rate</div>
        </div>
        
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-yellow-400">
            {(organicGrowth.networkEffectMultiplier || 1.0).toFixed(2)}x
          </div>
          <div className="text-xs text-gray-500">Network Effect</div>
          <div className="text-xs text-gray-600 mt-1">Scale multiplier</div>
        </div>
        
        <div className="bg-gray-800/50 rounded-lg p-4 text-center">
          <div className="text-xl font-bold text-green-400">
            {organicPercent.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500">Of Total Users</div>
          <div className="text-xs text-gray-600 mt-1">Organic share</div>
        </div>
      </div>
      
      {/* Source Breakdown */}
      <div className="mb-6">
        <h3 className="text-sm font-medium text-gray-400 mb-3">Acquisition Sources</h3>
        <div className="space-y-2">
          {/* Word of Mouth */}
          <div className="flex items-center gap-3">
            <div className="w-32 text-sm text-gray-400">💬 Word-of-Mouth</div>
            <div className="flex-1">
              <div className="h-8 bg-gray-700 rounded-lg overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-400 flex items-center px-3"
                  style={{ width: `${womPercent}%` }}
                >
                  <span className="text-xs font-semibold text-white">
                    {formatNumber(organicGrowth.wordOfMouthUsers)} ({womPercent.toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          {/* App Store Discovery */}
          <div className="flex items-center gap-3">
            <div className="w-32 text-sm text-gray-400">📱 App Store</div>
            <div className="flex-1">
              <div className="h-8 bg-gray-700 rounded-lg overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-purple-500 to-purple-400 flex items-center px-3"
                  style={{ width: `${appStorePercent}%` }}
                >
                  <span className="text-xs font-semibold text-white">
                    {formatNumber(organicGrowth.appStoreDiscoveryUsers)} ({appStorePercent.toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Network Effects */}
          <div className="flex items-center gap-3">
            <div className="w-32 text-sm text-gray-400">🔗 Network Effect</div>
            <div className="flex-1">
              <div className="h-8 bg-gray-700 rounded-lg overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-yellow-500 to-yellow-400 flex items-center px-3"
                  style={{ width: `${networkPercent}%` }}
                >
                  <span className="text-xs font-semibold text-white">
                    {formatNumber(organicGrowth.networkEffectUsers)} ({networkPercent.toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Social Sharing */}
          <div className="flex items-center gap-3">
            <div className="w-32 text-sm text-gray-400">🔄 Social Sharing</div>
            <div className="flex-1">
              <div className="h-8 bg-gray-700 rounded-lg overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-green-400 flex items-center px-3"
                  style={{ width: `${socialPercent}%` }}
                >
                  <span className="text-xs font-semibold text-white">
                    {formatNumber(organicGrowth.socialSharingUsers)} ({socialPercent.toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          {/* Content Virality */}
          <div className="flex items-center gap-3">
            <div className="w-32 text-sm text-gray-400">🚀 Viral Content</div>
            <div className="flex-1">
              <div className="h-8 bg-gray-700 rounded-lg overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-pink-500 to-pink-400 flex items-center px-3"
                  style={{ width: `${viralPercent}%` }}
                >
                  <span className="text-xs font-semibold text-white">
                    {formatNumber(organicGrowth.contentViralityUsers)} ({viralPercent.toFixed(1)}%)
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Growth Mechanics */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Growth Mechanics</h3>
          <div className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Referral Participation:</span>
              <span className="text-white font-semibold">
                {((organicGrowth.actualReferralParticipation || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Social Sharing Rate:</span>
              <span className="text-white font-semibold">
                {((organicGrowth.actualSharingParticipation || 0) * 100).toFixed(1)}%
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Dampening Factor:</span>
              <span className="text-white font-semibold">
                {(organicGrowth.dampeningFactor || 1.0).toFixed(2)}
              </span>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-800/50 rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-400 mb-3">Modifiers Applied</h3>
          <div className="space-y-2 text-sm">
            <div className="flex items-center justify-between">
              <span className="text-gray-500">Early Stage Boost:</span>
              <span className={`font-semibold ${organicGrowth.earlyStageBoostApplied ? 'text-green-400' : 'text-gray-600'}`}>
                {organicGrowth.earlyStageBoostApplied ? '✓ Active' : '✗ Inactive'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-500">Maturity Dampening:</span>
              <span className={`font-semibold ${organicGrowth.maturityDampeningApplied ? 'text-orange-400' : 'text-gray-600'}`}>
                {organicGrowth.maturityDampeningApplied ? '✓ Active' : '✗ Inactive'}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-500">Seasonal Adjustments:</span>
              <span className={`font-semibold ${organicGrowth.seasonalAdjustmentsApplied ? 'text-blue-400' : 'text-gray-600'}`}>
                {organicGrowth.seasonalAdjustmentsApplied ? '✓ Active' : '✗ Inactive'}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      {/* Research Benchmarks - ENHANCED FOR SOCIAL PLATFORMS */}
      <div className="p-4 bg-gradient-to-r from-blue-950/50 to-purple-950/50 rounded-lg border border-blue-700/30">
        <h3 className="text-sm font-medium text-blue-300 mb-3 flex items-center gap-2">
          <span>📊</span> Industry Benchmarks - Social/Crypto Platforms
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs mb-3">
          <div>
            <div className="text-gray-400">K-Factor Range</div>
            <div className="text-white font-semibold">0.25 - 0.60</div>
            <div className="text-gray-600">Social platforms (WhatsApp: 0.6+)</div>
          </div>
          <div>
            <div className="text-gray-400">Monthly Growth</div>
            <div className="text-white font-semibold">5% - 15%</div>
            <div className="text-gray-600">Compounding monthly!</div>
          </div>
          <div>
            <div className="text-gray-400">Referral Rate</div>
            <div className="text-white font-semibold">15% - 25%</div>
            <div className="text-gray-600">Social platforms higher</div>
          </div>
          <div>
            <div className="text-gray-400">App Store Organic</div>
            <div className="text-white font-semibold">1% - 3%</div>
            <div className="text-gray-600">Scales with reviews</div>
          </div>
        </div>
        
        {/* Realistic Expectations */}
        <div className="p-3 bg-yellow-900/30 border border-yellow-700/50 rounded-lg">
          <div className="text-sm font-semibold text-yellow-300 mb-2">🎯 Realistic Organic Growth Trajectory</div>
          <div className="grid grid-cols-3 gap-3 text-xs">
            <div>
              <div className="text-gray-400">Year 1</div>
              <div className="text-white font-bold">20-40% organic</div>
              <div className="text-gray-600">Building network</div>
            </div>
            <div>
              <div className="text-gray-400">Years 2-3</div>
              <div className="text-white font-bold">50-70% organic</div>
              <div className="text-gray-600">Network effects kick in</div>
            </div>
            <div>
              <div className="text-gray-400">Years 4-5</div>
              <div className="text-white font-bold">70-90% organic</div>
              <div className="text-gray-600">Mature platform dominance</div>
            </div>
          </div>
        </div>
        
        <div className="mt-3 text-xs text-gray-500">
          Sources: WhatsApp/Instagram growth data, App Annie/data.ai (2024-2025), Y Combinator metrics, Crypto app benchmarks
        </div>
      </div>
    </div>
  );
}
