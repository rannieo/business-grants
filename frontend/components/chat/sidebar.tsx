type NavItem = { icon: string; label: string }

const NAV_ITEMS: NavItem[] = [
  { icon: 'history', label: 'History' },
  { icon: 'bookmark', label: 'Saved Grants' },
  { icon: 'gavel', label: 'Directives' },
  { icon: 'settings', label: 'Settings' },
]

export default function Sidebar() {
  return (
    <aside
      className="hidden md:flex flex-col w-64 shrink-0 h-screen sticky top-0"
      style={{
        background: 'linear-gradient(135deg, #041635 0%, #1b2b4b 100%)',
      }}
    >
      {/* Logo area */}
      <div className="px-6 pt-8 pb-6 border-b border-white/10">
        <div className="flex items-center gap-3">
          <span
            className="material-symbols-rounded text-[#89f5e7] text-2xl"
          >
            account_balance
          </span>
          <span
            className="text-white text-sm font-semibold tracking-wide leading-tight"
            style={{ fontFamily: 'var(--font-display)' }}
          >
            Institutional<br />Portal
          </span>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex-1 px-3 py-6 space-y-1">
        {NAV_ITEMS.map((item) => (
          <button
            key={item.label}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-white/60 hover:text-white hover:bg-white/10 transition-colors duration-200 text-sm text-left"
          >
            <span className="material-symbols-rounded text-xl">{item.icon}</span>
            {item.label}
          </button>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-white/10">
        <div className="flex items-center gap-2">
          <span className="material-symbols-rounded text-[#89f5e7] text-base">smart_toy</span>
          <span className="text-white/40 text-xs">Grant Advisor v1</span>
        </div>
      </div>
    </aside>
  )
}
