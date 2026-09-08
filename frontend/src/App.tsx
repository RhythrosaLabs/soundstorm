import { useState } from 'react'
import Layout from './components/Layout'
import AIGenerator from './components/AIGenerator'
import EffectsRack from './components/EffectsRack'
import SamplePack from './components/SamplePack'
import DrumMachine from './components/DrumMachine'
import MIDIComposer from './components/MIDIComposer'
import ChatAssistant from './components/ChatAssistant'
import Settings from './components/Settings'

export type Section = 'generate' | 'effects' | 'samples' | 'drums' | 'midi' | 'chat' | 'settings'

export interface ApiKeys {
  replicate: string
  openai: string
}

export default function App() {
  const [section, setSection] = useState<Section>('generate')
  const [apiKeys, setApiKeys] = useState<ApiKeys>(() => {
    try {
      const stored = localStorage.getItem('soundstorm_keys')
      return stored ? JSON.parse(stored) : { replicate: '', openai: '' }
    } catch {
      return { replicate: '', openai: '' }
    }
  })

  const saveKeys = (keys: ApiKeys) => {
    setApiKeys(keys)
    localStorage.setItem('soundstorm_keys', JSON.stringify(keys))
  }

  const renderSection = () => {
    switch (section) {
      case 'generate': return <AIGenerator apiKeys={apiKeys} />
      case 'effects':  return <EffectsRack />
      case 'samples':  return <SamplePack />
      case 'drums':    return <DrumMachine />
      case 'midi':     return <MIDIComposer />
      case 'chat':     return <ChatAssistant apiKeys={apiKeys} />
      case 'settings': return <Settings apiKeys={apiKeys} onSave={saveKeys} />
    }
  }

  return (
    <Layout section={section} onNavigate={setSection}>
      {renderSection()}
    </Layout>
  )
}
