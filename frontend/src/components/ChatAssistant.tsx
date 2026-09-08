import { useState, useRef, useEffect } from 'react'
import { MessageSquare, Send, Loader2, Bot, User } from 'lucide-react'
import { sendChat } from '../lib/api'
import { type ApiKeys } from '../App'

interface Msg { role: 'user' | 'assistant'; content: string; ts: Date }

export default function ChatAssistant({ apiKeys }: { apiKeys: ApiKeys }) {
  const [msgs, setMsgs]     = useState<Msg[]>([{
    role: 'assistant',
    content: "Hi! I'm your AI music production assistant powered by GPT-4o. Ask me anything about music theory, sound design, mixing, mastering, or creative direction.",
    ts: new Date(),
  }])
  const [input, setInput]   = useState('')
  const [loading, setLoad]  = useState(false)
  const bottomRef           = useRef<HTMLDivElement>(null)
  const textRef             = useRef<HTMLTextAreaElement>(null)

  useEffect(() => { bottomRef.current?.scrollIntoView({ behavior: 'smooth' }) }, [msgs])

  const send = async () => {
    const text = input.trim()
    if (!text || loading) return

    if (!apiKeys.openai) {
      setMsgs(p => [...p, { role: 'assistant', content: 'Please add your OpenAI API key in Settings.', ts: new Date() }])
      return
    }

    setMsgs(p => [...p, { role: 'user', content: text, ts: new Date() }])
    setInput(''); setLoad(true)
    if (textRef.current) textRef.current.style.height = 'auto'

    try {
      const d = await sendChat(text, apiKeys.openai)
      setMsgs(p => [...p, { role: 'assistant', content: d.response, ts: new Date() }])
    } catch (e) {
      setMsgs(p => [...p, { role: 'assistant', content: `Error: ${e instanceof Error ? e.message : 'Something went wrong'}`, ts: new Date() }])
    } finally { setLoad(false) }
  }

  const onKey = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  const autoResize = () => {
    if (!textRef.current) return
    textRef.current.style.height = 'auto'
    textRef.current.style.height = `${Math.min(textRef.current.scrollHeight, 120)}px`
  }

  const fmt = (d: Date) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="flex items-center gap-3 p-8 pb-4 flex-shrink-0">
        <div className="w-10 h-10 rounded-xl bg-violet-600/20 border border-violet-500/25 flex items-center justify-center">
          <MessageSquare size={18} className="text-violet-400" />
        </div>
        <div>
          <h1 className="text-xl font-bold text-white">AI Music Assistant</h1>
          <p className="text-slate-500 text-sm">Powered by GPT-4o</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-8 space-y-4 pb-4">
        {msgs.map((m, i) => (
          <div key={i} className={`flex gap-3 ${m.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-7 h-7 rounded-full flex items-center justify-center flex-shrink-0 mt-0.5 ${
              m.role === 'assistant' ? 'bg-violet-600/20 border border-violet-500/30' : 'bg-brand-600/20 border border-brand-500/30'
            }`}>
              {m.role === 'assistant'
                ? <Bot size={13} className="text-violet-400" />
                : <User size={13} className="text-brand-400" />}
            </div>
            <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-sm ${
              m.role === 'user'
                ? 'bg-brand-600/20 border border-brand-500/20 text-slate-200 rounded-tr-sm'
                : 'glass text-slate-200 rounded-tl-sm'
            }`}>
              <p className="leading-relaxed whitespace-pre-wrap">{m.content}</p>
              <p className="text-[10px] text-slate-700 mt-1.5">{fmt(m.ts)}</p>
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-7 h-7 rounded-full bg-violet-600/20 border border-violet-500/30 flex items-center justify-center">
              <Bot size={13} className="text-violet-400" />
            </div>
            <div className="glass rounded-2xl rounded-tl-sm px-4 py-3 flex gap-1 items-center">
              {[0,150,300].map(d => (
                <div key={d} className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce" style={{ animationDelay: `${d}ms` }} />
              ))}
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div className="flex-shrink-0 p-8 pt-3">
        <div className="glass rounded-2xl flex items-end gap-3 p-3">
          <textarea
            ref={textRef}
            value={input}
            onChange={e => { setInput(e.target.value); autoResize() }}
            onKeyDown={onKey}
            placeholder="Ask about music theory, sound design, production tips..."
            rows={1}
            className="flex-1 bg-transparent text-sm text-slate-200 placeholder-slate-700 resize-none focus:outline-none leading-relaxed min-h-[24px]"
          />
          <button
            onClick={send}
            disabled={loading || !input.trim()}
            className="w-8 h-8 rounded-xl bg-violet-600 hover:bg-violet-500 flex items-center justify-center transition-all active:scale-95 disabled:opacity-40 flex-shrink-0"
          >
            {loading ? <Loader2 size={14} className="animate-spin" /> : <Send size={14} />}
          </button>
        </div>
        <p className="text-[10px] text-slate-700 text-center mt-2">Enter to send · Shift+Enter for new line</p>
      </div>
    </div>
  )
}
