import { useState } from 'react'
import { Drum, Loader2, AlertCircle } from 'lucide-react'
import AudioPlayer from './AudioPlayer'
import { createDrumLoop } from '../lib/api'

export default function DrumMachine() {
  const [tempo, setTempo]           = useState(120)
  const [beats, setBeats]           = useState(16)
  const [kick, setKick]             = useState(0.3)
  const [snare, setSnare]           = useState(0.2)
  const [hihat, setHihat]           = useState(0.3)
  const [loading, setLoading]       = useState(false)
  const [audio, setAudio]           = useState<string | null>(null)
  const [error, setError]           = useState('')

  const generate = async () => {
    setLoading(true); setError('')
    try {
      const d = await createDrumLoop({
        tempo, beat_length: beats,
        kick_likelihood: kick, snare_likelihood: snare, hihat_likelihood: hihat,
      })
      setAudio(d.audio)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally { setLoading(false) }
  }

  const Slider = ({ label, value, min, max, step = 0.05, onChange, display, color }: {
    label: string; value: number; min: number; max: number; step?: number;
    onChange: (v: number) => void; display: string; color: string
  }) => (
    <div className="flex items-center gap-4">
      <span className={`text-sm font-semibold w-14 ${color}`}>{label}</span>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(+e.target.value)} className="flex-1" />
      <span className="text-xs text-slate-500 font-mono w-12 text-right">{display}</span>
    </div>
  )

  // Build deterministic-ish pattern preview from seed values
  const pattern = Array.from({ length: 16 }, (_, i) => {
    if (i % 4 === 0) return 'kick'
    if (i % 4 === 2) return 'snare'
    const seed = ((i * 7 + Math.round(hihat * 10)) % 10) / 10
    if (seed < hihat) return 'hihat'
    return 'empty'
  })

  return (
    <div className="p-8 max-w-xl">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-rose-600/20 border border-rose-500/25 flex items-center justify-center">
          <Drum size={18} className="text-rose-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Drum Machine</h1>
          <p className="text-slate-500 text-sm">Algorithmic percussion loop generator</p>
        </div>
      </div>

      <div className="glass rounded-2xl p-5 mb-5 space-y-4">
        <Slider label="Tempo" value={tempo} min={60} max={240} step={1}
          onChange={setTempo} display={`${tempo}`} color="text-slate-300" />
        <Slider label="Beats" value={beats} min={4} max={32} step={4}
          onChange={setBeats} display={`${beats}`} color="text-slate-300" />

        <div className="border-t border-white/[0.06] pt-4 space-y-3">
          <p className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest">Instrument Mix</p>
          <Slider label="Kick" value={kick} min={0} max={1} onChange={setKick}
            display={`${Math.round(kick*100)}%`} color="text-rose-400" />
          <Slider label="Snare" value={snare} min={0} max={1} onChange={setSnare}
            display={`${Math.round(snare*100)}%`} color="text-yellow-400" />
          <Slider label="Hi-Hat" value={hihat} min={0} max={1} onChange={setHihat}
            display={`${Math.round(hihat*100)}%`} color="text-cyan-400" />
        </div>

        {/* Pattern grid */}
        <div className="border-t border-white/[0.06] pt-4">
          <p className="text-[10px] font-semibold text-slate-600 uppercase tracking-widest mb-3">Pattern Preview</p>
          <div className="flex gap-1">
            {pattern.map((type, i) => (
              <div key={i} className={`flex-1 rounded h-7 transition-all ${
                type === 'kick'  ? 'bg-rose-500/70 border border-rose-500/50' :
                type === 'snare' ? 'bg-yellow-500/70 border border-yellow-500/50' :
                type === 'hihat' ? 'bg-cyan-500/40 border border-cyan-500/30' :
                'bg-white/[0.04] border border-white/[0.05]'
              }`} />
            ))}
          </div>
          <div className="flex gap-4 mt-2">
            {[['rose','Kick'],['yellow','Snare'],['cyan','Hi-Hat']].map(([c,l]) => (
              <span key={l} className="flex items-center gap-1 text-[10px] text-slate-600">
                <span className={`w-2 h-2 rounded-sm bg-${c}-500/70 inline-block`} /> {l}
              </span>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 mb-4">
          <AlertCircle size={15} className="mt-0.5 flex-shrink-0" /> {error}
        </div>
      )}

      <button onClick={generate} disabled={loading}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-rose-700 to-rose-500 hover:from-rose-600 hover:to-rose-400 text-white font-semibold text-sm transition-all active:scale-[0.98] disabled:opacity-40 flex items-center justify-center gap-2"
      >
        {loading ? <><Loader2 size={16} className="animate-spin" /> Generating...</> : <><Drum size={16} /> Generate Drum Loop</>}
      </button>

      {audio && (
        <div className="mt-6">
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-3">Generated Loop</p>
          <AudioPlayer src={audio} filename={`drumloop_${Date.now()}.wav`} accentClass="bg-rose-500" />
        </div>
      )}
    </div>
  )
}
