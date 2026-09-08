import { type Section } from '../App'
import { Wand2, Sliders, Package, Drum, Music2, MessageSquare, Settings as Gear, Zap } from 'lucide-react'
import clsx from 'clsx'

interface Props {
  section: Section
  onNavigate: (s: Section) => void
  children: React.ReactNode
}

const NAV: { id: Section; icon: React.ElementType; label: string; color: string }[] = [
  { id: 'generate', icon: Wand2,         label: 'AI Generate',    color: 'text-brand-400' },
  { id: 'effects',  icon: Sliders,       label: 'Effects Rack',   color: 'text-emerald-400' },
  { id: 'samples',  icon: Package,       label: 'Sample Pack',    color: 'text-amber-400' },
  { id: 'drums',    icon: Drum,          label: 'Drum Machine',   color: 'text-rose-400' },
  { id: 'midi',     icon: Music2,        label: 'MIDI Composer',  color: 'text-cyan-400' },
  { id: 'chat',     icon: MessageSquare, label: 'AI Assistant',   color: 'text-violet-400' },
  { id: 'settings', icon: Gear,          label: 'Settings',       color: 'text-slate-400' },
]

export default function Layout({ section, onNavigate, children }: Props) {
  return (
    <div className="flex h-screen overflow-hidden bg-[#050508]">
      {/* Sidebar */}
      <aside className="w-[200px] flex-shrink-0 flex flex-col border-r border-white/[0.06] bg-[#07070e]">
        {/* Brand */}
        <div className="flex items-center gap-2.5 px-4 py-5 border-b border-white/[0.06]">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-brand-500 to-brand-700 flex items-center justify-center shadow-lg shadow-brand-900/40">
            <Zap size={15} className="text-white" fill="white" />
          </div>
          <div>
            <div className="font-bold text-[13px] tracking-tight text-white leading-none">SoundStorm</div>
            <div className="text-[9px] text-brand-400 font-semibold tracking-widest uppercase mt-0.5">AI Studio</div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 p-2.5 space-y-0.5 overflow-y-auto">
          {NAV.map(({ id, icon: Icon, label, color }) => (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              className={clsx(
                'w-full flex items-center gap-2.5 px-3 py-2.5 rounded-xl text-[13px] font-medium transition-all text-left',
                section === id
                  ? 'bg-white/[0.07] text-white border border-white/[0.09]'
                  : 'text-slate-500 hover:text-slate-300 hover:bg-white/[0.03]'
              )}
            >
              <Icon size={15} className={section === id ? color : undefined} />
              {label}
            </button>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-white/[0.06]">
          <div className="text-[10px] text-slate-700 text-center font-medium">v2.0 · Web Edition</div>
        </div>
      </aside>

      {/* Content */}
      <main className="flex-1 overflow-y-auto">
        {children}
      </main>
    </div>
  )
}
