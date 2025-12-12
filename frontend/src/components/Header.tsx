'use client';

export type PageTab = 'year1' | 'year5';

interface HeaderProps {
  activeTab: PageTab;
  onTabChange: (tab: PageTab) => void;
}

export function Header({ activeTab, onTabChange }: HeaderProps) {
  // #region agent log
  const handleTabChange = (tab: PageTab) => {
    fetch('http://127.0.0.1:7242/ingest/63e31cbd-d385-4178-b960-6e5c3301028f',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'Header.tsx:handleTabChange',message:'User clicked tab',data:{fromTab:activeTab,toTab:tab},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'C'})}).catch(()=>{});
    onTabChange(tab);
  };
  // #endregion
  
  return (
    <header className="bg-gradient-to-r from-slate-900 via-indigo-950 to-slate-900 text-white sticky top-0 z-50 shadow-xl">
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          {/* Logo and Title */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-cyan-400 to-indigo-500 rounded-xl flex items-center justify-center shadow-lg">
              <span className="text-xl font-black">◆</span>
            </div>
            <div>
              <h1 className="text-xl font-bold tracking-tight">
                ViWO Protocol
              </h1>
              <p className="text-xs text-indigo-300 -mt-0.5">Token Economy Simulator</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex items-center gap-1 bg-white/10 backdrop-blur-sm rounded-xl p-1">
            <TabButton
              active={activeTab === 'year1'}
              onClick={() => handleTabChange('year1')}
              icon="📅"
              label="Year 1"
              description="First 12 months"
            />
            <TabButton
              active={activeTab === 'year5'}
              onClick={() => handleTabChange('year5')}
              icon="📈"
              label="5-Year"
              description="Long-term projection"
            />
          </nav>
        </div>
      </div>
    </header>
  );
}

function TabButton({
  active,
  onClick,
  icon,
  label,
  description,
}: {
  active: boolean;
  onClick: () => void;
  icon: string;
  label: string;
  description: string;
}) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg font-semibold text-sm transition-all flex items-center gap-2
                 ${active 
                   ? 'bg-white text-slate-900 shadow-lg' 
                   : 'text-white/80 hover:bg-white/10 hover:text-white'
                 }`}
    >
      <span className="text-lg">{icon}</span>
      <div className="text-left">
        <div className="font-bold">{label}</div>
        <div className={`text-xs ${active ? 'text-slate-500' : 'text-white/60'}`}>
          {description}
        </div>
      </div>
    </button>
  );
}

export default Header;

