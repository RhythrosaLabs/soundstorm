import { useState } from 'react'
import { Package, Loader2, AlertCircle, Download, ChevronDown, ChevronUp } from 'lucide-react'
import AudioPlayer from './AudioPlayer'
import { createSamplePack } from '../lib/api'

function b64ToBlob(b64: string) {
  const bin = atob(b64)
  const buf = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
  return new Blob([buf], { type: 'audio/wav' })
}

export default function SamplePack() {
  const [numSounds, setNumSounds]   = useState(8)
  const [prefix, setPrefix]         = useState('sound')
  const [randomness, setRandomness] = useState(0.5)
  const [maxDur, setMaxDur]         = useState(3000)
  const [loading, setLoading]       = useState(false)
  const [sounds, setSounds]         = useState<Array<{ name: string; audio: string }>>([])
  const [expanded, setExpanded]     = useState<number | null>(null)
  const [error, setError]           = useState('')

  const generate = async () => {
    setLoading(true); setError(''); setSounds([])
    try {
      const d = await createSamplePack({ num_sounds: numSounds, prefix, randomness, max_duration: maxDur })
      setSounds(d.sounds)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally { setLoading(false) }
  }

  const downloadAll = () =>
    sounds.forEach(({ name, audio }) => {
      const a = document.createElement('a')
      a.href = URL.createObjectURL(b64ToBlob(audio))
      a.download = name; a.click()
    })

  const Slider = ({ label, value, min, max, step, onChange, fmt }: {
    label: string; value: number; min: number; max: number; step: number;
    onChange: (v: number) => void; fmt: (v: number) => string
  }) => (
    <div>
      <div className="flex justify-between mb-2">
        <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">{label}</label>
        <span className="text-[10px] font-mono text-amber-400">{fmt(value)}</span>
      </div>
      <input type="range" min={min} max={max} step={step} value={value}
        onChange={e => onChange(+e.target.value)} className="w-full" />
    </div>
  )

  return (
    <div className="p-8 max-w-2xl">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-amber-600/20 border border-amber-500/25 flex items-center justify-center">
          <Package size={18} className="text-amber-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Sample Pack Creator</h1>
          <p className="text-slate-500 text-sm">Algorithmically generate audio libraries</p>
        </div>
      </div>

      <div className="glass rounded-2xl p-5 mb-5 space-y-5">
        <div className="grid grid-cols-2 gap-5">
          <Slider label="Sounds" value={numSounds} min={1} max={16} step={1}
            onChange={setNumSounds} fmt={v => `${v}`} />
          <Slider label="Max Duration" value={maxDur} min={400} max={6000} step={100}
            onChange={setMaxDur} fmt={v => `${(v/1000).toFixed(1)}s`} />
          <Slider label="Randomness" value={randomness} min={0} max={1} step={0.01}
            onChange={setRandomness} fmt={v => `${(v*100).toFixed(0)}%`} />
          <div>
            <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2 block">File Prefix</label>
            <input
              value={prefix} onChange={e => setPrefix(e.target.value)}
              className="w-full bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-1.5 text-sm text-slate-200 focus:outline-none focus:border-amber-500/40 transition-all"
            />
          </div>
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 mb-4">
          <AlertCircle size={15} className="mt-0.5 flex-shrink-0" /> {error}
        </div>
      )}

      <button onClick={generate} disabled={loading}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-amber-700 to-amber-500 hover:from-amber-600 hover:to-amber-400 text-white font-semibold text-sm transition-all active:scale-[0.98] disabled:opacity-40 flex items-center justify-center gap-2 mb-6"
      >
        {loading
          ? <><Loader2 size={16} className="animate-spin" /> Generating {numSounds} sounds...</>
          : <><Package size={16} /> Generate Sample Pack</>}
      </button>

      {sounds.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">{sounds.length} sounds ready</p>
            <button onClick={downloadAll} className="flex items-center gap-1 text-xs text-amber-400 hover:text-amber-300 transition-colors">
              <Download size={12} /> Download All
            </button>
          </div>
          <div className="space-y-1.5">
            {sounds.map((s, i) => (
              <div key={i} className="glass rounded-xl overflow-hidden">
                <button
                  onClick={() => setExpanded(expanded === i ? null : i)}
                  className="w-full flex items-center gap-3 px-4 py-3 text-left hover:bg-white/[0.02] transition-colors"
                >
                  <div className="w-6 h-6 rounded-md bg-amber-500/20 flex items-center justify-center flex-shrink-0 text-xs font-mono text-amber-400">{i+1}</div>
                  <span className="text-sm text-slate-300 flex-1">{s.name}</span>
                  {expanded === i ? <ChevronUp size={14} className="text-slate-600" /> : <ChevronDown size={14} className="text-slate-600" />}
                </button>
                {expanded === i && (
                  <div className="px-4 pb-4">
                    <AudioPlayer src={s.audio} filename={s.name} accentClass="bg-amber-500" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
