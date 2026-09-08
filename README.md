<div align="center">

# ⚡ SoundStorm v2

**The AI audio studio — now as a gorgeous web app**

![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)
![React](https://img.shields.io/badge/React-61DAFB?style=flat&logo=react&logoColor=black)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat&logo=fastapi&logoColor=white)
![Tailwind](https://img.shields.io/badge/Tailwind-06B6D4?style=flat&logo=tailwindcss&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

</div>

---

SoundStorm v2 is a full-stack web application that brings the power of AI audio generation, studio-grade effects, algorithmic composition, and GPT-4o chat into a sleek, modern browser interface.

## ✨ Features

| Module | Description |
|---|---|
| **AI Generator** | Text-to-audio via MusicGen & LoopTest on Replicate |
| **Effects Rack** | Reverb, Chorus, Compressor, Distortion via Pedalboard |
| **Sample Pack** | Batch algorithmic sound generation |
| **Drum Machine** | Procedural percussion loops |
| **MIDI Composer** | Chord progression → downloadable MIDI |
| **AI Chat** | GPT-4o music production assistant |

## 🚀 Quick Start

### With Docker Compose (recommended)

```bash
git clone https://github.com/RhythrosaLabs/soundstorm
cd soundstorm
docker-compose up
```

Open `http://localhost:5173` and add your API keys in Settings.

### Manual

**Backend:**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 🔑 API Keys

| Key | Used For | Where to get |
|---|---|---|
| Replicate | AI audio generation | [replicate.com](https://replicate.com/account/api-tokens) |
| OpenAI | Chat + prompt randomizer | [platform.openai.com](https://platform.openai.com/api-keys) |

Keys are stored locally in your browser — never sent anywhere except the respective AI providers.

## 🛠️ Stack

- **Frontend:** React 18 + TypeScript + Vite + Tailwind CSS
- **Backend:** FastAPI + Python
- **Audio:** Pedalboard (Spotify) + pydub + midiutil
- **AI:** Replicate (MusicGen) + OpenAI (GPT-4o)

## 📄 License

MIT — Made with ❤️ by [RhythrosaLabs](https://github.com/RhythrosaLabs)
