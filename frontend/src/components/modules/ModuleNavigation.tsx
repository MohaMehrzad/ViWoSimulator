'use client';

import { PageTab } from '@/components/Header';

interface ModuleNavigationProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  activeTab: PageTab;
  enabledModules: {
    advertising: boolean;
    exchange: boolean;
  };
}

// Section type definition
type ModuleKey = 'advertising' | 'exchange';

interface SectionConfig {
  id: string;
  label: string;
  icon: string;
  alwaysShow?: boolean;
  moduleKey?: ModuleKey;
}

// Year 1 sections - focused on first 12 months
const YEAR1_SECTIONS: SectionConfig[] = [
  { id: 'overview', label: 'Overview', icon: '📊', alwaysShow: true },
  { id: 'prelaunch', label: 'Pre-Launch', icon: '🚀', alwaysShow: true },
  { id: 'identity', label: 'Identity', icon: '🆔', alwaysShow: true },
  { id: 'content', label: 'Content', icon: '📄', alwaysShow: true },
  { id: 'advertising', label: 'Advertising', icon: '📢', moduleKey: 'advertising' },
  { id: 'exchange', label: 'Exchange', icon: '💱', moduleKey: 'exchange' },
  { id: 'rewards', label: 'Rewards', icon: '🎁', alwaysShow: true },
  { id: 'recapture', label: 'Recapture Flow', icon: '🔄', alwaysShow: true },
  { id: 'liquidity', label: 'Liquidity', icon: '💧', alwaysShow: true },
  { id: 'staking', label: 'Staking', icon: '🔒', alwaysShow: true },
  { id: 'fiveA', label: '5A Policy', icon: '⭐', alwaysShow: true },
  { id: 'organicGrowth', label: 'Organic Growth', icon: '🌱', alwaysShow: true },
];

// 5-Year sections - focused on long-term projections
const YEAR5_SECTIONS: SectionConfig[] = [
  { id: 'overview', label: 'Overview', icon: '📈', alwaysShow: true },
  { id: 'prelaunch', label: 'Pre-Launch', icon: '🚀', alwaysShow: true },
  { id: 'tokenomics', label: 'Tokenomics', icon: '🪙', alwaysShow: true },
  { id: 'token-unlocks', label: 'Token Unlocks', icon: '📅', alwaysShow: true },
  { id: 'governance', label: 'Governance', icon: '🗳️', alwaysShow: true },
  { id: 'fiveA', label: '5A Policy', icon: '⭐', alwaysShow: true },
  { id: 'organicGrowth', label: 'Organic Growth', icon: '🌱', alwaysShow: true },
  { id: 'velocity', label: 'Velocity', icon: '⚡', alwaysShow: true },
  { id: 'token-metrics', label: 'Token Metrics', icon: '📊', alwaysShow: true },
  { id: 'future-modules', label: 'Future Modules', icon: '🔮', alwaysShow: true },
  { id: 'summary', label: 'Summary', icon: '✅', alwaysShow: true },
];

export function ModuleNavigation({ 
  activeSection, 
  onSectionChange,
  activeTab,
  enabledModules 
}: ModuleNavigationProps) {
  const sections = activeTab === 'year1' ? YEAR1_SECTIONS : YEAR5_SECTIONS;
  
  // #region agent log
  const handleSectionChange = (sectionId: string) => {
    fetch('http://127.0.0.1:7242/ingest/63e31cbd-d385-4178-b960-6e5c3301028f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'ModuleNavigation.tsx:handleSectionChange',message:'User clicked section',data:{fromSection:activeSection,toSection:sectionId,activeTab},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'D'})}).catch(()=>{});
    onSectionChange(sectionId);
  };
  // #endregion
  
  const visibleSections = sections.filter(section => {
    if (section.alwaysShow) return true;
    if (section.moduleKey) {
      return enabledModules[section.moduleKey];
    }
    return true;
  });

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4 sticky top-16 z-40 shadow-sm">
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 text-sm font-semibold text-gray-500 border-r border-gray-200 pr-4">
          <span>{activeTab === 'year1' ? '📅' : '📈'}</span>
          <span>{activeTab === 'year1' ? 'Year 1' : '5-Year'}</span>
        </div>
        <ul className="flex flex-wrap gap-2">
          {visibleSections.map((section) => (
            <li key={section.id}>
              <button
                onClick={() => handleSectionChange(section.id)}
                className={`flex items-center gap-1.5 px-4 py-2 rounded-lg font-semibold text-sm 
                           transition-all hover:-translate-y-0.5
                           ${activeSection === section.id 
                             ? 'bg-gray-900 text-white' 
                             : 'bg-gray-50 border border-gray-200 text-gray-900 hover:bg-gray-100'
                           }`}
              >
                <span>{section.icon}</span>
                {section.label}
              </button>
            </li>
          ))}
        </ul>
      </div>
    </nav>
  );
}
