import { useState } from 'react'
import { Settings as Gear, Eye, EyeOff, Save, CheckCircle2, ExternalLink } from 'lucide-react'
import { type ApiKeys } from '../App'

export default function Settings({ apiKeys, onSave }: { apiKeys: ApiKeys; onSave: (k: ApiKeys) => void }) {
  const [form, setForm]           = useState(apiKeys)
  const [showR, setShowR]         = useState(false)
  const [showO, setShowO]         = useState(false)
  const [saved, setSaved]         = useState(false)

  const save = () => {
    onSave(form)
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  const Field = ({ label, hint, url, value, show, onToggle, onChange, placeholder }: {
    label: string; hint: string; url: string; value: string; show: boolean;
    onToggle: () => void; onChange: (v: string) => void; placeholder: string
  }) => (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">{label}</label>
        <a href={url} target="_blank" rel="noreferrer"
          className="flex items-center gap-1 text-[10px] text-slate-600 hover:text-slate-400 transition-colors">
          Get key <ExternalLink size={10} />
        </a>
      </div>
      <p className="text-xs text-slate-700 mb-2">{hint}</p>
      <div className="relative">
        <input
          type={show ? 'text' : 'password'}
          value={value}
          onChange={e => onChange(e.target.value)}
          placeholder={placeholder}
          className="w-full bg-white/[0.04] border border-white/[0.08] rounded-xl px-4 py-2.5 pr-11 text-sm text-slate-200 placeholder-slate-700 focus:outline-none focus:border-white/20 transition-all font-mono"
        />
        <button
          onClick={onToggle}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-600 hover:text-slate-400 transition-colors"
        >
          {show ? <EyeOff size={15} /> : <Eye size={15} />}
        </button>
      </div>
    </div>
  )

  return (
    <div className="p-8 max-w-lg">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-slate-700/30 border border-slate-600/25 flex items-center justify-center">
          <Gear size={18} className="text-slate-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Settings</h1>
          <p className="text-slate-500 text-sm">Configure API keys for AI features</p>
        </div>
      </div>

      <div className="glass rounded-2xl p-6 space-y-6">
        <Field
          label="Replicate API Key"
          hint="Used for AI audio generation (MusicGen, LoopTest)"
          url="https://replicate.com/account/api-tokens"
          value={form.replicate}
          show={showR}
          onToggle={() => setShowR(v => !v)}
          onChange={v => setForm(f => ({ ...f, replicate: v }))}
          placeholder="r8_..."
        />
        <Field
          label="OpenAI API Key"
          hint="Used for AI chat assistant and prompt randomizer"
          url="https://platform.openai.com/api-keys"
          value={form.openai}
          show={showO}
          onToggle={() => setShowO(v => !v)}
          onChange={v => setForm(f => ({ ...f, openai: v }))}
          placeholder="sk-..."
        />

        <div className="border-t border-white/[0.06] pt-5">
          <p className="text-xs text-slate-700 mb-4">
            Keys are stored locally in your browser (localStorage) and are never sent to any server other than the respective AI providers.
          </p>
          <button
            onClick={save}
            className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-600 hover:bg-brand-500 text-white text-sm font-semibold transition-all active:scale-95"
          >
            {saved ? <><CheckCircle2 size={16} /> Saved!</> : <><Save size={16} /> Save Keys</>}
          </button>
        </div>
      </div>

      {/* Feature matrix */}
      <div className="mt-6 glass rounded-2xl p-5">
        <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-4">Feature Requirements</p>
        <div className="space-y-2">
          {[
            { feature: 'AI Audio Generation', needs: 'Replicate' },
            { feature: 'Random Prompt',        needs: 'OpenAI' },
            { feature: 'AI Chat Assistant',    needs: 'OpenAI' },
            { feature: 'Effects Rack',         needs: 'None (backend)' },
            { feature: 'Sample Pack',          needs: 'None (backend)' },
            { feature: 'Drum Machine',         needs: 'None (backend)' },
            { feature: 'MIDI Composer',        needs: 'None (backend)' },
          ].map(({ feature, needs }) => (
            <div key={feature} className="flex items-center justify-between text-xs">
              <span className="text-slate-400">{feature}</span>
              <span className={`font-mono ${
                needs === 'None (backend)' ? 'text-emerald-600' :
                needs === 'Replicate' ? (form.replicate ? 'text-emerald-500' : 'text-amber-600') :
                form.openai ? 'text-emerald-500' : 'text-amber-600'
              }`}>{needs}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
