import { useState, useRef, useEffect } from 'react'
import { Play, Pause, Download } from 'lucide-react'

interface Props {
  src: string        // base64-encoded WAV
  filename?: string
  accentClass?: string
}

function b64ToUrl(b64: string): string {
  const bin = atob(b64)
  const buf = new Uint8Array(bin.length)
  for (let i = 0; i < bin.length; i++) buf[i] = bin.charCodeAt(i)
  return URL.createObjectURL(new Blob([buf], { type: 'audio/wav' }))
}

export default function AudioPlayer({ src, filename = 'audio.wav', accentClass = 'bg-brand-500' }: Props) {
  const [playing, setPlaying] = useState(false)
  const [progress, setProgress] = useState(0)
  const [duration, setDuration] = useState(0)
  const audioRef = useRef<HTMLAudioElement>(null)
  const urlRef = useRef('')

  useEffect(() => {
    const url = b64ToUrl(src)
    urlRef.current = url
    if (audioRef.current) { audioRef.current.src = url; audioRef.current.load() }
    setPlaying(false)
    setProgress(0)
    return () => URL.revokeObjectURL(url)
  }, [src])

  const toggle = () => {
    if (!audioRef.current) return
    if (playing) { audioRef.current.pause() } else { audioRef.current.play() }
    setPlaying(p => !p)
  }

  const download = () => {
    const a = document.createElement('a')
    a.href = urlRef.current; a.download = filename; a.click()
  }

  const fmt = (s: number) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`
  const pct = duration > 0 ? (progress / duration) * 100 : 0

  // static waveform heights for visual
  const bars = [4, 8, 14, 10, 18, 12, 20, 9, 16, 11, 19, 8, 15, 12, 7, 17, 10, 20, 8, 13]

  return (
    <div className="glass rounded-xl p-4">
      <audio
        ref={audioRef}
        onTimeUpdate={e => setProgress(e.currentTarget.currentTime)}
        onDurationChange={e => setDuration(e.currentTarget.duration)}
        onEnded={() => setPlaying(false)}
      />

      {/* Waveform */}
      <div className="flex items-end gap-[2px] h-10 mb-3">
        {bars.map((h, i) => (
          <div
            key={i}
            className={`flex-1 rounded-full ${playing ? accentClass + ' wave-bar opacity-90' : 'bg-white/15'}`}
            style={{
              height: playing ? `${h}px` : `${Math.max(3, h * 0.5)}px`,
              animationDelay: playing ? `${i * 0.06}s` : undefined,
            }}
          />
        ))}
      </div>

      {/* Progress */}
      <div className="h-1 bg-white/10 rounded-full mb-3 cursor-pointer" onClick={e => {
        if (!audioRef.current || !duration) return
        const rect = e.currentTarget.getBoundingClientRect()
        const pct = (e.clientX - rect.left) / rect.width
        audioRef.current.currentTime = pct * duration
      }}>
        <div className={`h-full ${accentClass} rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>

      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={toggle}
            className={`w-8 h-8 rounded-full ${accentClass} hover:opacity-80 flex items-center justify-center transition-all active:scale-95`}
          >
            {playing ? <Pause size={14} /> : <Play size={14} className="ml-0.5" />}
          </button>
          <span className="text-xs text-slate-500 tabular-nums">{fmt(progress)} / {fmt(duration)}</span>
        </div>
        <button onClick={download} className="flex items-center gap-1 text-xs text-slate-500 hover:text-slate-300 transition-colors">
          <Download size={12} /> Save
        </button>
      </div>
    </div>
  )
}
