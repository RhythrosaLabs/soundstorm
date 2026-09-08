from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os, io, random, tempfile, base64, json
from datetime import datetime
import replicate
import openai
from pydub import AudioSegment
from pydub.generators import Sine, Square, Sawtooth, Triangle, Pulse, WhiteNoise
from pedalboard import Pedalboard, Chorus, Reverb, Compressor, Distortion
from pedalboard.io import AudioFile as PedalboardAudioFile
from midiutil import MIDIFile
import requests

app = FastAPI(title="SoundStorm API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Models ────────────────────────────────────────────────────────────────────

class GenerateRequest(BaseModel):
    prompt: str
    model: str = "meta/musicgen"
    duration: int = 20
    api_key: str

class ChatRequest(BaseModel):
    message: str
    api_key: str

class RandomPromptRequest(BaseModel):
    api_key: str

class SamplePackRequest(BaseModel):
    num_sounds: int = 8
    prefix: str = "sound"
    randomness: float = 0.5
    max_duration: int = 6000

class DrumLoopRequest(BaseModel):
    tempo: int = 120
    beat_length: int = 16
    kick_likelihood: float = 0.3
    snare_likelihood: float = 0.2
    hihat_likelihood: float = 0.3

class MIDIRequest(BaseModel):
    key: str = "C"
    song_name: str = "My Song"
    chord_progression: List[str] = []


# ── Audio utilities ───────────────────────────────────────────────────────────

def audio_to_base64(audio: AudioSegment) -> str:
    buf = io.BytesIO()
    audio.export(buf, format="wav")
    buf.seek(0)
    return base64.b64encode(buf.read()).decode()

def add_delay(segment: AudioSegment) -> AudioSegment:
    for _ in range(random.randint(1, 3)):
        segment = segment.overlay(segment, gain_during_overlay=random.randint(-15, -1))
    return segment

def apply_stutter(segment: AudioSegment) -> AudioSegment:
    if len(segment) < 300:
        return segment
    s_point = random.randint(0, max(0, len(segment) - 150))
    d_ms = random.randint(10, min(200, len(segment) - s_point))
    piece = segment[s_point:s_point + d_ms]
    return sum([piece] * random.randint(1, 5))  # type: ignore

def makeshift_echo(sound: AudioSegment, delay_ms: int, decay: float) -> AudioSegment:
    silence = AudioSegment.silent(duration=delay_ms)
    delayed = sound.overlay(sound + decay, position=delay_ms)
    return sound + silence + delayed

def generate_random_sound(randomness: float = 0.5, max_duration: int = 6000) -> AudioSegment:
    generators = [Sine, Square, Sawtooth, Triangle, Pulse]
    gen = random.choice(generators)
    freq = random.randint(50, 880)
    dur = random.randint(400, min(3000, max_duration))
    sound = gen(freq).to_audio_segment(duration=dur)

    if random.random() < randomness and len(sound) < max_duration - 400:
        gen2 = random.choice(generators)
        freq2 = random.randint(50, 880)
        dur2 = random.randint(400, min(max_duration - len(sound), 3000))
        sound += gen2(freq2).to_audio_segment(duration=dur2)

    if random.random() > 0.7:
        sound = sound + sound.reverse()
    if random.random() > 0.6:
        sound = add_delay(sound)
    if random.random() > 0.7 and len(sound) > 300:
        sound = apply_stutter(sound)
    if random.random() > 0.6:
        cutoff = random.choice([300, 500, 1000, 2000])
        if random.random() > 0.5:
            sound = sound.high_pass_filter(cutoff)
        else:
            sound = sound.low_pass_filter(cutoff)
    if len(sound) > 500:
        fade = min(200, len(sound) // 4)
        sound = sound.fade_in(fade).fade_out(fade)
    if random.random() > 0.7:
        sound = makeshift_echo(sound, random.randint(100, 400), -4.0)
    if len(sound) > max_duration:
        sound = sound[:max_duration]

    return sound.set_channels(2).set_frame_rate(44100)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "2.0.0"}


@app.post("/api/generate")
async def generate_audio(req: GenerateRequest):
    try:
        os.environ["REPLICATE_API_TOKEN"] = req.api_key
        model_map = {
            "meta/musicgen": "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906",
            "allenhung1025/looptest": "allenhung1025/looptest:0de4a5f14b9120ce02c590eb9cf6c94841569fafbc4be7ab37436ce738bcf49f",
        }
        model_id = model_map.get(req.model, model_map["meta/musicgen"])
        output = replicate.run(model_id, input={"prompt": req.prompt, "duration": req.duration})
        url = output if isinstance(output, str) else str(output)
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        audio = AudioSegment.from_file(io.BytesIO(r.content))
        return {"audio": audio_to_base64(audio), "format": "wav"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/effects")
async def apply_effects(
    file: UploadFile = File(...),
    effects: str = Form("{}"),
):
    try:
        effects_dict = json.loads(effects)
        content = await file.read()

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_in:
            tmp_in.write(content)
            tmp_path = tmp_in.name

        chain = []
        if effects_dict.get("compressor"): chain.append(Compressor(threshold_db=-20, ratio=4))
        if effects_dict.get("reverb"): chain.append(Reverb(room_size=0.5))
        if effects_dict.get("chorus"): chain.append(Chorus())
        if effects_dict.get("distortion"): chain.append(Distortion(drive_db=20))

        if not chain:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail="Select at least one effect")

        with PedalboardAudioFile(tmp_path) as f:
            audio_data = f.read(f.frames)
            sr = f.samplerate
            channels = f.num_channels

        processed = Pedalboard(chain)(audio_data, sr)

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_out:
            out_path = tmp_out.name

        with PedalboardAudioFile(out_path, "w", sr, channels) as f:
            f.write(processed)

        with open(out_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode()

        os.unlink(tmp_path)
        os.unlink(out_path)
        return {"audio": audio_b64, "format": "wav"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/sample-pack")
async def create_sample_pack(req: SamplePackRequest):
    try:
        sounds = []
        for i in range(min(req.num_sounds, 16)):
            sound = generate_random_sound(req.randomness, req.max_duration)
            sounds.append({"name": f"{req.prefix}_{i+1:02d}.wav", "audio": audio_to_base64(sound)})
        return {"sounds": sounds}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/drum-loop")
async def create_drum_loop(req: DrumLoopRequest):
    try:
        beat_ms = int(60000 / req.tempo)

        def kick() -> AudioSegment:
            return (Sine(60).to_audio_segment(duration=80) + 5).fade_out(60)

        def snare() -> AudioSegment:
            return (WhiteNoise().to_audio_segment(duration=60) +
                    Sine(900).to_audio_segment(duration=30)).fade_out(50)

        def hihat() -> AudioSegment:
            return (WhiteNoise().to_audio_segment(duration=20) - 3).fade_out(15)

        def silence() -> AudioSegment:
            return AudioSegment.silent(duration=beat_ms)

        loop = AudioSegment.silent(duration=0)
        for i in range(req.beat_length):
            if i % 4 == 0:
                loop += kick()
            elif i % 4 == 2:
                loop += snare()
            elif random.random() < req.hihat_likelihood:
                loop += hihat()
            else:
                loop += silence()

        loop = loop.set_channels(2).set_frame_rate(44100)
        return {"audio": audio_to_base64(loop), "format": "wav"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


SCALES = {
    "C": [0,2,4,5,7,9,11], "C#": [1,3,5,6,8,10,0], "D": [2,4,6,7,9,11,1],
    "Eb": [3,5,7,8,10,0,2], "E": [4,6,8,9,11,1,3], "F": [5,7,9,10,0,2,4],
    "F#": [6,8,10,11,1,3,5], "G": [7,9,11,0,2,4,6], "Ab": [8,10,0,1,3,5,7],
    "A": [9,11,1,2,4,6,8], "Bb": [10,0,2,3,5,7,9], "B": [11,1,3,4,6,8,10],
}
CHORDS = {
    "Major": [0,4,7], "Minor": [0,3,7], "Diminished": [0,3,6],
    "Major7": [0,4,7,11], "Minor7": [0,3,7,10], "Dominant7": [0,4,7,10],
    "Suspended4": [0,5,7], "Augmented": [0,4,8],
}


@app.post("/api/midi")
async def create_midi(req: MIDIRequest):
    try:
        midi = MIDIFile(1)
        midi.addTrackName(0, 0, req.song_name)
        midi.addTempo(0, 0, 120)
        scale = SCALES.get(req.key, SCALES["C"])
        chords = req.chord_progression if req.chord_progression else [
            random.choice(list(CHORDS.keys())) for _ in range(8)
        ]
        time = 0
        for chord_name in chords:
            intervals = CHORDS.get(chord_name, [0, 4, 7])
            for interval in intervals:
                note = 60 + (scale[0] + interval) % 12
                midi.addNote(0, 0, note, time, 1, 80)
            time += 1
        buf = io.BytesIO()
        midi.writeFile(buf)
        buf.seek(0)
        filename = f"{req.song_name.replace(' ', '_').lower()}.mid"
        return {"midi": base64.b64encode(buf.read()).decode(), "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/chat")
async def chat(req: ChatRequest):
    try:
        client = openai.OpenAI(api_key=req.api_key)
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a knowledgeable music production assistant. Help with music theory, sound design, production techniques, and creative direction. Be concise and practical."},
                {"role": "user", "content": req.message},
            ],
            max_tokens=400,
        )
        return {"response": res.choices[0].message.content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/random-prompt")
async def random_prompt(req: RandomPromptRequest):
    try:
        client = openai.OpenAI(api_key=req.api_key)
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a creative music prompt generator. Generate vivid, specific prompts."},
                {"role": "user", "content": "Generate one creative audio/music generation prompt in 1-2 sentences. Include genre, mood, instruments, and tempo. Be inventive."},
            ],
            max_tokens=120,
        )
        return {"prompt": res.choices[0].message.content.strip()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
