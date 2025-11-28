'use client';

interface ModuleNavigationProps {
  activeSection: string;
  onSectionChange: (section: string) => void;
  enabledModules: {
    advertising: boolean;
    messaging: boolean;
    community: boolean;
    exchange: boolean;
  };
}

const SECTIONS = [
  { id: 'overview', label: 'Overview', icon: '📊', alwaysShow: true },
  { id: 'tokenomics', label: 'Tokenomics', icon: '🪙', alwaysShow: true },
  { id: 'identity', label: 'Identity', icon: '🆔', alwaysShow: true },
  { id: 'content', label: 'Content', icon: '📄', alwaysShow: true },
  { id: 'community', label: 'Community', icon: '👥', moduleKey: 'community' as const },
  { id: 'advertising', label: 'Advertising', icon: '📢', moduleKey: 'advertising' as const },
  { id: 'messaging', label: 'Messaging', icon: '💬', moduleKey: 'messaging' as const },
  { id: 'exchange', label: 'Exchange', icon: '💱', moduleKey: 'exchange' as const },
  { id: 'rewards', label: 'Rewards', icon: '🎁', alwaysShow: true },
  { id: 'recapture', label: 'Recapture Flow', icon: '🔄', alwaysShow: true },
  { id: 'liquidity', label: 'Liquidity', icon: '💧', alwaysShow: true },
  { id: 'staking', label: 'Staking', icon: '🔒', alwaysShow: true },
  { id: 'velocity', label: 'Velocity', icon: '⚡', alwaysShow: true },
  { id: 'summary', label: 'Summary', icon: '📈', alwaysShow: true },
];

export function ModuleNavigation({ 
  activeSection, 
  onSectionChange,
  enabledModules 
}: ModuleNavigationProps) {
  const visibleSections = SECTIONS.filter(section => {
    if (section.alwaysShow) return true;
    if (section.moduleKey) {
      return enabledModules[section.moduleKey];
    }
    return true;
  });

  return (
    <nav className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-50 shadow-sm">
      <ul className="flex flex-wrap gap-2">
        {visibleSections.map((section) => (
          <li key={section.id}>
            <button
              onClick={() => onSectionChange(section.id)}
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
    </nav>
  );
}


