import { useState } from 'react'
import { Music2, Shuffle, Loader2, AlertCircle, Download } from 'lucide-react'
import { createMidi } from '../lib/api'

const KEYS = ['C','C#','D','Eb','E','F','F#','G','Ab','A','Bb','B']
const CHORD_TYPES = ['Major','Minor','Diminished','Major7','Minor7','Dominant7','Suspended4','Augmented']
const SONG_NAMES = ['Cosmic Drift','Neon Sunrise','Velvet Fog','Midnight Pulse','Glass Rain','Electric Dream','Shadow Walk','Crystal Echo','Solar Flare','Deep Current']

function dlMidi(b64: string, name: string) {
  const bin = atob(b64)
  const buf = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
  const a = document.createElement('a')
  a.href = URL.createObjectURL(new Blob([buf], { type: 'audio/midi' }))
  a.download = name; a.click()
}

export default function MIDIComposer() {
  const [key, setKey]           = useState('C')
  const [name, setName]         = useState('My Song')
  const [chords, setChords]     = useState<string[]>([])
  const [loading, setLoading]   = useState(false)
  const [result, setResult]     = useState<{ midi: string; filename: string } | null>(null)
  const [error, setError]       = useState('')

  const randChords = () =>
    setChords(Array.from({ length: 8 }, () => CHORD_TYPES[Math.floor(Math.random() * CHORD_TYPES.length)]))

  const randName = () => setName(SONG_NAMES[Math.floor(Math.random() * SONG_NAMES.length)])

  const generate = async () => {
    setLoading(true); setError(''
    )
    try {
      const d = await createMidi({ key, song_name: name, chord_progression: chords })
      setResult(d)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Generation failed')
    } finally { setLoading(false) }
  }

  return (
    <div className="p-8 max-w-2xl">
      <div className="flex items-center gap-3 mb-8">
        <div className="w-10 h-10 rounded-xl bg-cyan-600/20 border border-cyan-500/25 flex items-center justify-center">
          <Music2 size={18} className="text-cyan-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">MIDI Composer</h1>
          <p className="text-slate-500 text-sm">Generate chord progressions as MIDI files</p>
        </div>
      </div>

      <div className="glass rounded-2xl p-5 mb-5 space-y-5">
        {/* Name */}
        <div>
          <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2 block">Song Name</label>
          <div className="flex gap-2">
            <input
              value={name} onChange={e => setName(e.target.value)}
              className="flex-1 bg-white/[0.04] border border-white/[0.08] rounded-lg px-3 py-2 text-sm text-slate-200 focus:outline-none focus:border-cyan-500/40 transition-all"
            />
            <button onClick={randName} className="px-3 py-2 rounded-lg bg-white/[0.05] hover:bg-white/10 text-slate-500 hover:text-slate-200 transition-all">
              <Shuffle size={14} />
            </button>
          </div>
        </div>

        {/* Key */}
        <div>
          <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest mb-2 block">Key</label>
          <div className="flex flex-wrap gap-1.5">
            {KEYS.map(k => (
              <button key={k} onClick={() => setKey(k)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
                  key === k ? 'bg-cyan-600 text-white' : 'bg-white/[0.05] text-slate-500 hover:bg-white/10 hover:text-slate-300'
                }`}>{k}</button>
            ))}
          </div>
        </div>

        {/* Chords */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">Chord Progression</label>
            <button onClick={randChords} className="flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 transition-colors">
              <Shuffle size={12} /> Randomize
            </button>
          </div>
          {chords.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {chords.map((c, i) => (
                <div key={i} className="flex items-center gap-1 px-3 py-1.5 rounded-lg bg-cyan-500/15 border border-cyan-500/25 text-cyan-300 text-xs font-medium">
                  <span className="text-cyan-700">{i+1}.</span> {key} {c}
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-slate-600 text-center py-3">Click Randomize or leave empty for auto-generated chords</p>
          )}
        </div>
      </div>

      {error && (
        <div className="flex items-start gap-2 text-sm text-red-400 bg-red-500/10 border border-red-500/20 rounded-xl px-4 py-3 mb-4">
          <AlertCircle size={15} className="mt-0.5 flex-shrink-0" /> {error}
        </div>
      )}

      <button onClick={generate} disabled={loading}
        className="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-700 to-cyan-500 hover:from-cyan-600 hover:to-cyan-400 text-white font-semibold text-sm transition-all active:scale-[0.98] disabled:opacity-40 flex items-center justify-center gap-2"
      >
        {loading ? <><Loader2 size={16} className="animate-spin" /> Generating...</> : <><Music2 size={16} /> Generate MIDI</>}
      </button>

      {result && (
        <div className="mt-6 glass rounded-2xl p-5 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-slate-200">{result.filename}</p>
            <p className="text-xs text-slate-600 mt-0.5">MIDI file — open in DAW or notation software</p>
          </div>
          <button
            onClick={() => dlMidi(result.midi, result.filename)}
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-cyan-600/20 border border-cyan-500/30 text-cyan-300 text-sm font-medium hover:bg-cyan-600/30 transition-all"
          >
            <Download size={15} /> Download
          </button>
        </div>
      )}
    </div>
  )
}
