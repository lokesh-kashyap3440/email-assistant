import { Inbox, Settings, Wrench, Github } from 'lucide-react'

type Page = 'inbox' | 'config' | 'setup'

interface NavbarProps {
  currentPage: Page
  onNavigate: (page: Page) => void
}

const navItems: { id: Page; label: string; icon: typeof Inbox }[] = [
  { id: 'inbox', label: 'Inbox', icon: Inbox },
  { id: 'config', label: 'Config', icon: Settings },
  { id: 'setup', label: 'Setup', icon: Wrench },
]

export function Navbar({ currentPage, onNavigate }: NavbarProps) {
  return (
    <aside className="w-60 h-screen bg-gray-900 border-r border-gray-800 flex flex-col shrink-0">
      <div className="p-5 border-b border-gray-800">
        <h1 className="text-lg font-bold text-gray-100 flex items-center gap-2">
          <span className="text-accent">◆</span>
          Email Assistant
        </h1>
      </div>

      <nav className="flex-1 p-3 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = currentPage === item.id
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? 'bg-accent/10 text-accent'
                  : 'text-gray-400 hover:text-gray-200 hover:bg-gray-800'
              }`}
            >
              <Icon size={18} />
              {item.label}
            </button>
          )
        })}
      </nav>

      <div className="p-3 border-t border-gray-800">
        <a
          href="https://github.com/anomalyco/opencode"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors"
        >
          <Github size={16} />
          GitHub
        </a>
      </div>
    </aside>
  )
}
