import { useState } from 'react'
import { Wand2, Shuffle, Loader2, AlertCircle } from 'lucide-react'
import AudioPlayer from './AudioPlayer'
import { generateAudio, getRandomPrompt } from '../lib/api'
import { type ApiKeys } from '../App'

const MODELS = [
  { value: 'meta/musicgen',          label: 'MusicGen · Meta AI' },
  { value: 'allenhung1025/looptest', label: 'LoopTest · Loop Optimized' },
]
const DURATIONS = [8, 15, 20, 30]

export default function AIGenerator({ apiKeys }: { apiKeys: ApiKeys }) {
  const [prompt, setPrompt]       = useState('')
  const [model, setModel]         = useState(MODELS[0].value)
  const [duration, setDuration]   = useState(20)
  const [loading, setLoading]     = useState(false)
  const [randLoad, setRandLoad]   = useState(false)
  const [audio, setAudio]         = useState<string | null>(null)
  const [error, setError]         = useState('')

  const generate = async () => {
    if (!prompt.trim()) return
    if (!apiKeys.replicate) { setError('Add your Replicate API key in Settings'); return }
    setLoading(true); setError(''); setAudio(null)
    try {
      const d = await generateAudio(prompt, model, duration, apiKeys.replicate)
      setAudio(d.audio)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally { setLoading(false) }
  }

  const randomize = async () => {
    if (!apiKeys.openai) { setError('Add your OpenAI API key in Settings'); return }
    setRandLoad(true); setError('')
    try {
      const d = await getRandomPrompt(apiKeys.openai)
      setPrompt(d.prompt)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Prompt generation failed')
    } finally { setRandLoad(false) }
  }

  return (
    <div className="p-8 max-w-2xl">
      {/* Header */}
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-brand-600/20 border border-brand-500/25 flex items-center justify-center">
          <Wand2 size={18} className="text-brand-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">AI Audio Generator</h1>
          <p className="text-slate-500 text-sm">Text-to-audio via Replicate AI models</p>
        </div>
      </div>

      {/* Prompt card */}
      <div className="glass rounded-2xl p-5 mb-4">
        <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2 block">Prompt</label>
        <textarea
          value={prompt}
          onChange={e => setPrompt(e.target.value)}
          rows={4}
          placeholder="A lo-fi hip-hop beat with jazzy piano, warm bass, and soft vinyl crackle at 85 BPM..."
          className="w-full bg-transparent text-sm text-slate-200 placeholder-slate-700 resize-none focus:outline-none leading-relaxed"
        />
        <button
          onClick={randomize}
          disabled={randLoad}
          className="flex items-center gap-1.5 text-xs text-brand-400 hover:text-brand-300 transition-colors mt-2 disabled:opacity-40"
        >
          {randLoad ? <Loader2 size={12} className="animate-spin" /> : <Shuffle size={12} />}
          Randomize with GPT-4o
        </button>
      </div>

      {/* Model + Duration */}
      <div className="grid grid-cols-2 gap-3 mb-5">
        <div className="glass rounded-xl p-4">
          <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2 block">Model</label>
          <select
            value={model}
            onChange={e => setModel(e.target.value)}
            className="w-full bg-transparent text-sm text-slate-300 focus:outline-none cursor-pointer"
          >
            {MODELS.map(m => <option key={m.value} value={m.value} className="bg-[#111118]">{m.label}</option>)}
          </select>
        </div>
        <div className="glass rounded-xl p-4">
          <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2.5 block">Duration</label>
          <div className="flex gap-1.5">
            {DURATIONS.map(d => (
              <button
                key={d}
                onClick={() => setDuration(d)}
                className={`flex-1 py-1 rounded-lg text-xs font-semibold transition-all ${
                  duration === d ? 'bg-brand-600 text-white' : 'bg-white/[0.06] text-slate-500 hover:bg-white/10 hover:text-slate-300'
                }`}
              >{d}s</button>
            ))}
          </div>
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 mb-4">
          <AlertCircle size={15} className="mt-0.5 flex-shrink-0" /> {error}
        </div>
      )}

      <button
        onClick={generate}
        disabled={loading || !prompt.trim()}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-brand-700 to-brand-500 hover:from-brand-600 hover:to-brand-400 text-white font-semibold text-sm transition-all active:scale-[0.98] disabled:opacity-40 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-brand-900/30"
      >
        {loading
          ? <><Loader2 size={16} className="animate-spin" /> Generating... (may take ~30s)</>
          : <><Wand2 size={16} /> Generate Audio</>}
      </button>

      {audio && (
        <div className="mt-6">
          <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-3">Output</p>
          <AudioPlayer src={audio} filename={`soundstorm_${Date.now()}.wav`} accentClass="bg-brand-500" />
        </div>
      )}
    </div>
  )
}
