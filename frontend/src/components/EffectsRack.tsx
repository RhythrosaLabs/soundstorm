import { useState, useRef } from 'react'
import { Sliders, Upload, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react'
import AudioPlayer from './AudioPlayer'
import { applyEffects } from '../lib/api'

const EFFECTS = [
  { key: 'reverb',      label: 'Reverb',      desc: 'Spatial room ambience' },
  { key: 'chorus',      label: 'Chorus',      desc: 'Lush doubling effect' },
  { key: 'compressor',  label: 'Compressor',  desc: 'Dynamic range control' },
  { key: 'distortion',  label: 'Distortion',  desc: 'Harmonic saturation' },
]

export default function EffectsRack() {
  const [file, setFile]       = useState<File | null>(null)
  const [effects, setEffects] = useState<Record<string, boolean>>({})
  const [loading, setLoading] = useState(false)
  const [audio, setAudio]     = useState<string | null>(null)
  const [error, setError]     = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const toggle = (k: string) => setEffects(p => ({ ...p, [k]: !p[k] }))

  const process = async () => {
    if (!file || !Object.values(effects).some(Boolean)) {
      setError('Load a file and select at least one effect')
      return
    }
    setLoading(true); setError('')
    try {
      const d = await applyEffects(file, effects)
      setAudio(d.audio)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Processing failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="p-8 max-w-xl">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-emerald-600/20 border border-emerald-500/25 flex items-center justify-center">
          <Sliders size={18} className="text-emerald-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">Effects Rack</h1>
          <p className="text-slate-500 text-sm">Studio-grade processing via Pedalboard</p>
        </div>
      </div>

      {/* Drop zone */}
      <div
        onClick={() => inputRef.current?.click()}
        className={`glass rounded-2xl p-8 mb-5 text-center cursor-pointer transition-all border-dashed border-2 ${
          file ? 'border-emerald-500/40' : 'border-white/[0.06] hover:border-white/[0.12]'
        }`}
      >
        <input ref={inputRef} type="file" accept="audio/*" className="hidden"
          onChange={e => { setFile(e.target.files?.[0] ?? null); setAudio(null) }} />
        {file ? (
          <div className="flex flex-col items-center gap-2">
            <CheckCircle2 size={22} className="text-emerald-400" />
            <p className="text-sm font-medium text-slate-200">{file.name}</p>
            <p className="text-xs text-slate-600">{(file.size / 1024).toFixed(1)} KB · click to change</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2">
            <Upload size={22} className="text-slate-600" />
            <p className="text-sm text-slate-500">Drop an audio file or click to browse</p>
            <p className="text-xs text-slate-700">WAV · MP3 · FLAC · OGG</p>
          </div>
        )}
      </div>

      {/* Effects grid */}
      <div className="grid grid-cols-2 gap-2.5 mb-5">
        {EFFECTS.map(({ key, label, desc }) => (
          <button
            key={key}
            onClick={() => toggle(key)}
            className={`glass rounded-xl p-4 text-left transition-all ${
              effects[key]
                ? 'border-emerald-500/40 bg-emerald-500/10'
                : 'hover:border-white/12 hover:bg-white/[0.02]'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className={`text-sm font-semibold ${effects[key] ? 'text-emerald-300' : 'text-slate-300'}`}>{label}</span>
              <div className={`w-3.5 h-3.5 rounded-full border-2 transition-all ${
                effects[key] ? 'bg-emerald-500 border-emerald-500' : 'border-slate-600'
              }`} />
            </div>
            <p className="text-xs text-slate-600">{desc}</p>
          </button>
        ))}
      </div>

      {error && (
        <div className="flex items-start gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 mb-4">
          <AlertCircle size={15} className="mt-0.5 flex-shrink-0" /> {error}
        </div>
      )}

      <button
        onClick={process}
        disabled={loading || !file}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-emerald-700 to-emerald-500 hover:from-emerald-600 hover:to-emerald-400 text-white font-semibold text-sm transition-all active:scale-[0.98] disabled:opacity-40 flex items-center justify-center gap-2"
      >
        {loading ? <><Loader2 size={16} className="animate-spin" /> Processing...</> : <><Sliders size={16} /> Process Audio</>}
      </button>

      {audio && (
        <div className="mt-6">
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-3">Processed Output</p>
          <AudioPlayer src={audio} filename={`processed_${Date.now()}.wav`} accentClass="bg-emerald-500" />
        </div>
      )}
    </div>
  )
}
