from datetime import datetime
from pydub.generators import Sine, Square, Sawtooth, Triangle, Pulse, WhiteNoise
from tkinter import simpledialog, messagebox
from tkinter import ttk
from tkinter import Button, Label, StringVar, filedialog
import pygame
import json
import os
import replicate
import requests
import tkinter as tk
import openai
import threading
from midiutil import MIDIFile
import random
from pydub import AudioSegment
from pydub.playback import play
from pedalboard import Pedalboard, Chorus, Reverb
from pedalboard.io import AudioFile
from pedalboard import Pedalboard, Compressor, Distortion, Reverb


#=========================================================================================================
#=========================================================================================================

# g l o b a l

#=========================================================================================================
#=========================================================================================================

# a p i

def save_api_keys(replicate_key, openai_key):
    with open("api_keys.json", "w") as f:
        json.dump({"replicate_api_key": replicate_key, "openai_api_key": openai_key}, f)

def load_api_keys():
    try:
        with open("api_keys.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_api_keys():
    replicate_key = simpledialog.askstring("Input", "Enter your Replicate API Key:")
    openai_key = simpledialog.askstring("Input", "Enter your OpenAI API Key:")
    return replicate_key, openai_key


#=========================================================================================================
#=========================================================================================================

# G P T   R A N D O M I Z E

def threaded_generate_random_prompt():
    openai.api_key = load_api_keys().get('openai_api_key', '')
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Pick between 1-3 percussive instruments, 1-3 world instruments, 1-3 other  instruments, 1-3 niche genres, a tempo, and a song key, and list them in one sentence. No non-numerical characters except for commas"}
    ]
    try:
        res = openai.ChatCompletion.create(model="gpt-4", messages=messages, max_tokens=100, temperature=1)
        generated_text = res['choices'][0]['message']['content'].strip()
        text_input.delete("1.0", "end")
        text_input.insert("1.0", generated_text)
    except Exception as e:
        print(f"Error: {e}")

def generate_random_prompt():
    threading.Thread(target=threaded_generate_random_prompt).start()

text_input = tk.Text()
#=========================================================================================================
#=========================================================================================================

# C H A T    G P T

def get_gpt_response(user_message):
    openai.api_key = load_api_keys().get('openai_api_key', '')
    if not openai.api_key:
        return "Error: OpenAI API key not found."

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": user_message}
    ]

    try:
        res = openai.ChatCompletion.create(model="gpt-4", messages=messages, max_tokens=100, temperature=1)
        return res['choices'][0]['message']['content']
    except Exception as e:
        return f"Error: {e}"


def send_message():
    user_message = user_input.get()
    chat_display.config(state=tk.NORMAL)
    chat_display.insert(tk.END, "You: " + user_message + '\n')

    def threaded_gpt_response():
        gpt_response = get_gpt_response(user_message)
        chat_display.insert(tk.END, "GPT-4: " + gpt_response + '\n')
        chat_display.config(state=tk.DISABLED)

    threading.Thread(target=threaded_gpt_response).start()
    user_input.delete(0, tk.END)


# Example Tkinter widget initialization
user_input = tk.Entry()
chat_display = tk.Text()


#=========================================================================================================
#=========================================================================================================

# P L A Y B A C K     A N D    T R A N S P O R T

class MusicPlayer:
    def __init__(self, window):
        Load = Button(window, text='Load', width=3, font=('Times', 12), command=self.load)
        Play = Button(window, text='Play', width=3, font=('Times', 12), command=self.play)
        Pause = Button(window, text='Pause', width=3, font=('Times', 12), command=self.pause)
        Stop = Button(window, text='Stop', width=3, font=('Times', 12), command=self.stop)

        Load.grid(row=0, column=0)
        Play.grid(row=0, column=1)
        Pause.grid(row=0, column=2)
        Stop.grid(row=0, column=3)

        self.music_file = False
        self.playing_state = False

        self.track_time = StringVar()
        self.track_time.set('00:00')
        self.time_display = Label(window, textvariable=self.track_time, width=5, font=('Times', 12))
        self.time_display.grid(row=1, column=1)

    def load(self):
        self.music_file = filedialog.askopenfilename()

    def play(self):
        if self.music_file:
            pygame.mixer.init()
            pygame.mixer.music.load(self.music_file)
            pygame.mixer.music.play()
            self.update_time()

    def pause(self):
        if not self.playing_state:
            pygame.mixer.music.pause()
            self.playing_state = True
        else:
            pygame.mixer.music.unpause()
            self.playing_state = False

    def stop(self):
        pygame.mixer.music.stop()

    def update_time(self):
        if pygame.mixer.music.get_busy():
            time = pygame.mixer.music.get_pos() // 1000
            mins = time // 60
            secs = time % 60
            self.track_time.set(f'{mins:02d}:{secs:02d}')
            root.after(1000, self.update_time)


#=========================================================================================================
#=========================================================================================================

# A U D I O   U T I L I T I E S

# Global variables for the first part
audio = None
file_path = None

# Global variables for the second part
audio_data = None
processed_audio = None
samplerate = None
num_channels = None

# General Audio Functions
def load_audio_general():
    global audio, file_path
    file_path = filedialog.askopenfilename()
    if file_path:
        audio = AudioSegment.from_file(file_path, format="wav")


def save_audio(suffix):
    global audio, file_path
    if audio and file_path:
        base_name, ext = os.path.splitext(file_path)
        new_file_path = f"{base_name}_{suffix}{ext}"
        audio.export(new_file_path, format="wav")
        print(f"Saved as {new_file_path}")

def normalize():
    global audio
    if audio:
        audio = audio.normalize()
        print("Normalized")
        save_audio('normalized')

def stereo_to_mono():
    global audio
    if audio:
        audio = audio.set_channels(1)
        print("Converted to Mono")
        save_audio('stereotomono')

# Function to convert mono to stereo
def mono_to_stereo():
    global audio
    if audio:
        audio = audio.set_channels(2)
        print("Converted to Stereo")
        save_audio('monotostereo')

# Function to reverse audio
def reverse_audio():
    global audio
    if audio:
        audio = audio.reverse()
        print("Reversed")
        save_audio('reversed')

def adjust_gain(value):
    global audio
    if audio:
        audio = audio._spawn(audio.raw_data, overrides={
           "frame_rate": int(audio.frame_rate * float(value))
        }).set_frame_rate(audio.frame_rate)
        print(f"Gain adjusted to: {value}")
def change_bit_rate(event):
    global audio
    selected_bit_rate = bit_rate_combo.get()
    if audio:
        if selected_bit_rate == '16':
            audio = audio.set_sample_width(2)
        elif selected_bit_rate == '24':
            audio = audio.set_sample_width(3)
        elif selected_bit_rate == '32':
            audio = audio.set_sample_width(4)
        print(f"Bit rate changed to {selected_bit_rate} bits")
        save_audio(f'bitrate{selected_bit_rate}')

def change_sample_rate(event):
    global audio
    if audio:
        selected_sample_rate = sample_rate_combo.get()
        audio = audio.set_frame_rate(int(selected_sample_rate))
        print(f"Sample rate changed to {selected_sample_rate} Hz")
        save_audio(f'samplerate{selected_sample_rate}')

def adjust_fade_in(value):
    global audio
    if audio:
        audio = audio.fade_in(int(value))
        print(f"Fade-in time set to: {value} ms")
        save_audio(f'fadein{value}')

def adjust_fade_out(value):
    global audio
    if audio:
        audio = audio.fade_out(int(value))
        print(f"Fade-out time set to: {value} ms")
        save_audio(f'fadeout{value}')

def adjust_level(value):
    global audio
    if audio:
        # Implement your level adjustment logic here
        print(f"Level adjusted to: {value}")
        save_audio(f'level{value}')

def create_audio_frame(master):
    audio_frame = tk.Frame(master, relief='groove', borderwidth=5)
    audio_frame.grid(row=0, column=1, padx=10, pady=10)

    tk.Button(audio_frame, text='Load Audio', command=load_audio).grid(row=0, column=0, columnspan=2)

    # Normalize and Reverse buttons on the same row
    tk.Button(audio_frame, text='Normalize', command=normalize).grid(row=1, column=0)
    tk.Button(audio_frame, text='Reverse Audio', command=reverse_audio).grid(row=1, column=1)

    # Stereo and Mono buttons on the same row
    tk.Button(audio_frame, text='Stereo to Mono', command=stereo_to_mono).grid(row=2, column=0)
    tk.Button(audio_frame, text='Mono to Stereo', command=mono_to_stereo).grid(row=2, column=1)

    # Bit rate and Sample rate dropdowns on the same row
    bit_rate_combo = ttk.Combobox(audio_frame, values=["16", "24", "32"])
    bit_rate_combo.bind("<<ComboboxSelected>>", change_bit_rate)
    bit_rate_combo.grid(row=3, column=0)

    sample_rate_combo = ttk.Combobox(audio_frame, values=["44100", "48000", "96000"])
    sample_rate_combo.bind("<<ComboboxSelected>>", change_sample_rate)
    sample_rate_combo.grid(row=3, column=1)

    # Level adjustment slider
    tk.Scale(audio_frame, from_=0, to=100, orient='horizontal', label='Level',
             command=adjust_level).grid(row=4, column=0, columnspan=2)

    # Fade in/out sliders on the same row
    tk.Scale(audio_frame, from_=0, to=10000, orient='horizontal', label='Fade In',
             command=adjust_fade_in).grid(row=5, column=0)

    tk.Scale(audio_frame, from_=0, to=10000, orient='horizontal', label='Fade Out',
             command=adjust_fade_out).grid(row=5, column=1)

    return audio_frame

#=========================================================================================================
#=========================================================================================================

# U T I L I T Y     E F F E C T S


# Functions related to Pedalboard and basic audio IO
def load_audio():
    filepath = filedialog.askopenfilename(title="Select an audio file",
                                          filetypes=[("WAV files", "*.wav"),
                                                     ("All files", "*.*")])
    if not filepath:
        return

    with AudioFile(filepath) as f:
        global audio_data, samplerate, num_channels
        audio_data = f.read(f.frames)
        samplerate = f.samplerate
        num_channels = f.num_channels

def process_audio():
    if audio_data is None:
        print("No audio data loaded.")
        return

    board = Pedalboard([Chorus(), Reverb(room_size=0.25)])
    global processed_audio
    processed_audio = board(audio_data, samplerate, reset=False)

def save_audio():
    if processed_audio is None:
        print("No processed audio to save.")
        return

    filepath = filedialog.asksaveasfilename(defaultextension=".wav",
                                            filetypes=[("WAV files", "*.wav"),
                                                       ("All files", "*.*")])
    if not filepath:
        return

    with AudioFile(filepath, 'w', samplerate, num_channels) as f:
        f.write(processed_audio)

# Functions related to PyDub effects
def apply_effects():
    global audio_data
    audio = AudioSegment._spawn(audio_data, num_channels=num_channels, sample_width=2, frame_rate=samplerate)
    if reverb_var.get():
        audio = apply_reverb(audio)
    if chorus_var.get():
        audio = apply_chorus(audio)
    if delay_var.get():
        audio = apply_delay(audio)
    if flanger_var.get():
        audio = apply_flanger(audio)
    if distortion_var.get():
        audio = apply_distortion(audio)
    play(audio)

def apply_reverb(audio):
    return audio.overlay(audio._spawn(audio.raw_data, shift=500), gain_during_overlay=-10)

def apply_chorus(audio):
    return audio.overlay(audio._spawn(audio.raw_data, shift=150)).overlay(audio._spawn(audio.raw_data, shift=300))

def apply_delay(audio):
    silence = AudioSegment.silent(duration=1000)
    return audio + silence + audio

def apply_flanger(audio):
    flanger = audio._spawn(audio.raw_data, shift=50)
    return (audio + flanger)

def apply_distortion(audio):
    return audio.apply_gain(20).limiter(gain=10)


#=========================================================================================================
#=========================================================================================================


# T E X T   T O   A U D I O

def download_file(url, filename):
    r = requests.get(url, allow_redirects=True)
    open(filename, 'wb').write(r.content)

def threaded_generate_music(input_audio_file=None, duration=8, continuation=False):
    global model_dropdown  # Declare it as global
    selected_model = model_dropdown.get()  # Get the selected model from the dropdown

    input_text = text_input.get("1.0", "end-1c")
    api_keys = load_api_keys()
    if api_keys:
        os.environ["REPLICATE_API_TOKEN"] = api_keys.get('replicate_api_key', '')

    # Create input dictionary
    model_input = {
        "prompt": input_text,
        "duration": 20
    }

    # Run the selected model
    if selected_model == 'meta/musicgen':
        model_id = "meta/musicgen:7a76a8258b23fae65c5a22debb8841d1d7e816b75c2f24218cd2bd8573787906"
    else:
        model_id = "allenhung1025/looptest:0de4a5f14b9120ce02c590eb9cf6c94841569fafbc4be7ab37436ce738bcf49f"

    output = replicate.run(model_id, input=model_input)

    download_url = output  # Assuming output is a string that is a URL

    # Get current timestamp and format it
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

    # Create a filename using the text input and timestamp
    sanitized_input_text = "".join(e for e in input_text if e.isalnum())
    filename = f"{sanitized_input_text[:30]}_{timestamp}.wav"

    print(f"Downloading from {download_url}...")
    download_file(download_url, filename)
    print(f"Download complete: saved as {filename}")

# Function to generate music using the replicate API
def generate_music(input_audio_file=None, duration=8, continuation=False):
    generate_thread = threading.Thread(target=threaded_generate_music, args=(input_audio_file, duration, continuation))
    generate_thread.start()

OUTPUT_DIR = "random_sounds"

#====================================================================================
#====================================================================================

# A L G O R I T H M I C    E F F E C T S
def add_delay(segment):
    delayed = segment
    for _ in range(random.randint(1, 3)):
        delayed = delayed.overlay(segment, gain_during_overlay=random.randint(-15, -1))
    return delayed._spawn(b"\0" * int(44.1 * random.randint(50, 700)))

def apply_stutter(segment):
    s_point, d_ms = random.randint(0, len(segment) - 150), random.randint(10, 200)
    stutter_piece = segment[s_point:s_point + d_ms]
    return sum([stutter_piece] * random.randint(1, 15))

def apply_arpeggio(frequency, generator):
    step, steps = random.choice([50, 75, 100, 125]), random.randint(3, 8)
    dur = random.randint(50, 200)
    return sum([generator(frequency + i * step).to_audio_segment(dur) for i in range(steps)])

def randomized_arpeggiation(base_freq, steps, dur):
    gen_choice, steps = random.choice([Sine, Square, Sawtooth, Triangle, Pulse]), random.sample(steps, len(steps))
    return sum([gen_choice(base_freq * step).to_audio_segment(dur) for step in steps])

def makeshift_echo(sound, delay_time, decay_factor):
    delay = AudioSegment.silent(delay_time)
    delayed = sound.overlay(sound + decay_factor, position=delay_time)
    return sound + delay + delayed

def makeshift_reverb(sound, num=5, delay=30, decay=-5):
    for _ in range(num):
        sound = makeshift_echo(sound, delay, decay)
        delay, decay = int(delay * 1.2), decay - 2.5
    return sound

#=========================================================================================================
#=========================================================================================================

# A L G O R I T H M I C    C O M P O S I T I O N

# generate
def generate_random_sound(filename, randomness_factor=0.5, max_duration=6000):  # <-- Add max_duration parameter here

    generators = [Sine, Square, Sawtooth, Triangle, Pulse]
    gen_choice = random.choice(generators)

    # Random frequency between 50Hz and 880Hz
    freq = random.randint(50, 600)

    # Random duration between 0.4s and 3s in milliseconds
    duration = random.randint(400, 3000)

    # Generate the first sound
    sound1 = gen_choice(freq).to_audio_segment(duration=duration)

    # With a probability dictated by randomness_factor, generate a second sound and concatenate
    sound = sound1
    if random.random() < randomness_factor:
        max_duration2 = max_duration - duration
        if max_duration2 > 400:
            duration2 = random.randint(400, max_duration2)
            gen_choice2 = random.choice(generators)
            freq2 = random.randint(50, 880)
            sound2 = gen_choice2(freq2).to_audio_segment(duration=duration2)
            sound += sound2

    # Random frequency between 400Hz and 900Hz
    freq = random.randint(50, 880)

    # Random duration between 0.4s and 6s in milliseconds
    duration = random.randint(400, 3000)

    # Generate the first sound
    sound1 = gen_choice(freq).to_audio_segment(duration=duration)

    # With a 50% probability, generate a second sound and concatenate
    sound = sound1
    if random.random() > 0.8:
        max_duration2 = 1000 - duration
        if max_duration2 > 400:
            duration2 = random.randint(400, max_duration2)
            gen_choice2 = random.choice(generators)
            freq2 = random.randint(400, 900)
            sound2 = gen_choice2(freq2).to_audio_segment(duration=duration2)
            sound += sound2

    # Apply random effects
    if random.random() > (0.7 - randomness_factor/2):
        sound = sound + sound.reverse()

    if random.random() > (0.6 - randomness_factor/2):
        sound = add_delay(sound)

    if random.random() > (0.7 - randomness_factor/2):
        sound = apply_stutter(sound)

    if random.random() > (0.6 - randomness_factor/2):
        sound = apply_arpeggio(freq, gen_choice)

    if random.random() < (0.5 - randomness_factor/2):
        speed_change = random.uniform(1.1, 1.5)
        if len(sound) > 150:
            sound = sound.speedup(playback_speed=speed_change)
        else:
            sound = sound.speedup(playback_speed=speed_change, chunk_size=int(len(sound)/2))

    if random.random() > (0.6 - randomness_factor/2):
        sound = sound.fade_in(duration=1000)

    if random.random() > (0.6 - randomness_factor/2):
        sound = sound.fade_out(duration=1000)

    if random.random() > (0.6 - randomness_factor/2):
        sound = sound.invert_phase()

    if random.random() > (0.6 - randomness_factor/2):
        cutoff = random.choice([300, 500, 1000, 2000])
        filter_choice = random.choice(['highpass', 'lowpass'])
        if filter_choice == 'highpass':
            sound = sound.high_pass_filter(cutoff)
        else:
            sound = sound.low_pass_filter(cutoff)

    if random.random() > (0.5 - randomness_factor/2):
        steps = [1, 9/8, 5/4, 3/2]
        duration_per_step = random.randint(100, 500)
        sound += randomized_arpeggiation(freq, steps, duration_per_step)

    if random.random() > (0.7 - randomness_factor/2):
        delay_time = random.randint(100, 500)
        decay_factor = random.uniform(-2, -5)
        sound += makeshift_echo(sound, delay_time, decay_factor)

    if random.random() > (0.7 - randomness_factor/2):
        sound += makeshift_reverb(sound)

    # At the end, before exporting:
    if len(sound) > max_duration:
        sound = sound[:max_duration]  # Trim to desired length. You can also add a fade out for smoother ending.

    sound.export(filename, format="wav")

#=========================================================================================================
#=========================================================================================================

# A L G O R I T H M I C    P E R C U S S I O N

class DrumLoopGenerator:
    def __init__(self, tempo=120, beat_length=16, max_duration=40000):  # Updated beat_length to 16 for 4 bars
        self.tempo = tempo
        self.beat_length = beat_length
        self.max_duration = max_duration

        # Mapping of drum sound generators and their likelihoods
        self.drum_generators = {
            'kick': {'func': self._generate_kick, 'likelihood': 0.2, 'volume': 5},  # Increased volume for kick
            'snare': {'func': self._generate_snare, 'likelihood': 0.2, 'volume': 0},
            'hihat': {'func': self._generate_hihat, 'likelihood': 0.2, 'volume': 0},
            'tom': {'func': self._generate_tom, 'likelihood': 0.1, 'volume': 0},
            'silence': {'func': self._generate_silence, 'likelihood': 0.2, 'volume': 0}
        }

    def _generate_sound(self, freq_range, noise=False, pitch_factor=0.8):  # Lowered the pitch
        freq = random.uniform(*freq_range) * pitch_factor
        duration = 100
        sound = Sine(freq).to_audio_segment(duration=duration)
        if noise:
            sound += WhiteNoise().to_audio_segment(duration=duration)
        return sound

    def _generate_kick(self):
        sound = self._generate_sound((40, 80))
        return sound + self.drum_generators['kick']['volume']  # Increased volume

    def _generate_snare(self):
        return self._generate_sound((600, 2000), noise=True)

    def _generate_hihat(self):
        return WhiteNoise().to_audio_segment(duration=25)

    def _generate_tom(self):
        freq_range = random.choice([(100, 150), (150, 250), (250, 350)])
        return self._generate_sound(freq_range)

    def _generate_silence(self):
        return AudioSegment.silent(duration=100)

    def _randomly_apply_effects(self, sound):
        # More modular and dynamic effects application
        effects = [self._apply_reverb, self._apply_echo]
        for effect in effects:
            if random.random() < 0.5:
                sound = effect(sound)
        return sound

    def _apply_reverb(self, sound):
        # Placeholder reverb effect
        return sound + sound.reverse()

    def _apply_echo(self, sound):
        # Placeholder echo effect
        return sound + sound.overlay(sound)

    def generate_loop(self, filename):
        beat_duration = 60000 / self.tempo
        choices = list(self.drum_generators.keys())

        loop = sum(
            self.drum_generators['kick']['func']() if i % 4 == 0 else  # Make the kick fall on 4/4
            self.drum_generators[random.choices(choices, [v['likelihood'] for v in self.drum_generators.values()])[0]][
                'func']()
            if random.random() < 0.8 else AudioSegment.silent(duration=beat_duration)
            for i in range(self.beat_length)
        )[:self.max_duration]

        # Removed fades for seamless looping

        # Generate a timestamp-based filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"drumloop_{timestamp}.wav"

        loop.export(unique_filename, format="wav")


#=========================================================================================================
#=========================================================================================================


# S O U N D   P A C K    S A V E

def main(num_sounds, prefix, randomness_factor=0.5, max_duration=6000):  # <-- Add max_duration parameter here

    # Generate a timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create a new directory inside OUTPUT_DIR with "sound pack [timestamp]" as the name
    new_output_dir = os.path.join(OUTPUT_DIR, f"sound pack {timestamp}")

    if not os.path.exists(new_output_dir):
        os.makedirs(new_output_dir)

    for i in range(num_sounds):
        output_file = os.path.join(new_output_dir, f"{prefix}_{i}.wav")
        generate_random_sound(output_file, randomness_factor, max_duration)  # <-- pass max_duration here
        print(f"Generated {output_file}")

#=========================================================================================================
#=========================================================================================================


# m i d i    m a k e r
class SongGeneratorGUI:
    def __init__(self, root):
        self.root = root
        self.chord_progression = []


        # Create the GUI elements
        self.key_label = tk.Label(root, text="Select Key:")
        self.key_label.pack()

        self.key_var = tk.StringVar(root)
        self.key_var.set("C")  # Default key is C
        self.key_option_menu = tk.OptionMenu(root, self.key_var, *keys)
        self.key_option_menu.pack()

        self.song_name_entry = tk.Entry(root)
        self.song_name_entry.pack()

        self.randomize_text_button = tk.Button(root, text="Randomize Text", command=self.randomize_text)
        self.randomize_text_button.pack()

        self.randomize_chords_button = tk.Button(root, text="Randomize Chords", command=self.randomize_chords)
        self.randomize_chords_button.pack()

        self.generate_button = tk.Button(root, text="Generate", command=self.generate_song)
        self.generate_button.pack()

    def generate_song(self):
        try:
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            new_folder = f"random_midi_{timestamp}"
            os.makedirs(new_folder, exist_ok=True)

            song_name = self.song_name_entry.get().strip()
            if not song_name:
                return

            key = self.key_var.get()
            scale = scales.get(key, [])
            midi = MIDIFile(1)

            midi.addTrackName(track=0, time=0, trackName=song_name)
            midi.addTempo(track=0, time=0, tempo=120)

            time = 0

            for chord_name in self.chord_progression:
                chord_notes = chords.get(chord_name, [])
                for note_index in chord_notes:
                    note = (note_index + scale[0]) % 12
                    midi.addNote(track=0, channel=0, pitch=note, time=time, duration=1, volume=100)
                time += 0.5  # Advance time for the next chord

            filename = f"{song_name.replace(' ', '_').lower()}.mid"
            filepath = os.path.join(new_folder, filename)
            with open(filepath, "wb") as output_file:
                midi.writeFile(output_file)
        except Exception as e:
            print(f"Error: {e}")

    def randomize_text(self):
        randomized_name = random.choice(song_names_list)
        self.song_name_entry.delete(0, tk.END)
        self.song_name_entry.insert(0, randomized_name)

    def randomize_chords(self):
        chord_names = list(chords.keys())
        self.chord_progression = [random.choice(chord_names) for _ in range(8)]

    def run(self):
        self.root.mainloop()


def get_chord_notes(chord_name, key, scale):
    root_note = notes[key]
    root_index = scale.index(root_note)

    chord_notes = []
    for step in chords[chord_name]:
        note_index = (root_index + step) % len(scale)
        chord_notes.append(scale[note_index])

    return chord_notes


notes = {
    "C": "C",
    "C#": "C#",
    "Db": "C#",
    "D": "D",
    "D#": "D#",
    "Eb": "D#",
    "E": "E",
    "F": "F",
    "F#": "F#",
    "Gb": "F#",
    "G": "G",
    "G#": "G#",
    "Ab": "G#",
    "A": "A",
    "A#": "A#",
    "Bb": "A#",
    "B": "B"
}

keys = ['C', 'C#', 'Db', 'D', 'D#', 'Eb', 'E', 'F', 'F#', 'Gb', 'G', 'G#', 'Ab', 'A', 'A#', 'Bb', 'B']


scales = {
    "C": [0, 2, 4, 5, 7, 9, 11],
    "C#": [1, 3, 5, 6, 8, 10, 0],
    "Db": [1, 3, 5, 6, 8, 10, 0],
    "D": [2, 4, 6, 7, 9, 11, 1],
    "D#": [3, 5, 7, 8, 10, 0, 2],
    "Eb": [3, 5, 7, 8, 10, 0, 2],
    "E": [4, 6, 8, 9, 11, 1, 3],
    "F": [5, 7, 9, 10, 0, 2, 4],
    "F#": [6, 8, 10, 11, 1, 3, 5],
    "Gb": [6, 8, 10, 11, 1, 3, 5],
    "G": [7, 9, 11, 0, 2, 4, 6],
    "G#": [8, 10, 0, 1, 3, 5, 7],
    "Ab": [8, 10, 0, 1, 3, 5, 7],
    "A": [9, 11, 1, 2, 4, 6, 8],
    "A#": [10, 0, 2, 3, 5, 7, 9],
    "Bb": [10, 0, 2, 3, 5, 7, 9],
    "B": [11, 1, 3, 4, 6, 8, 10]
}

chords = {
    "Major": [0, 4, 7],
    "Minor": [0, 3, 7],
    "Diminished": [0, 3, 6],
    "Augmented": [0, 4, 8],
    "Suspended2": [0, 2, 7],
    "Suspended4": [0, 5, 7],
    "Major7": [0, 4, 7, 11],
    "Minor7": [0, 3, 7, 10],
    "Dominant7": [0, 4, 7, 10],
    "Diminished7": [0, 3, 6, 9],
    "HalfDiminished7": [0, 3, 6, 10],
    "Augmented7": [0, 4, 8, 10],
    "Sixth": [0, 4, 7, 9],
    "MinorSixth": [0, 3, 7, 9],
}

# Comprehensive Extended Chord Progressions with 10 Options per Section
chord_progressions = {
    "Intro": [
        ["Minor", "Minor7"], ["Major", "Major7"], ["Minor", "Minor"], ["Diminished", "Minor"],
        ["Major", "Add9"], ["Minor", "Minor7"], ["Major", "Major"], ["Major", "Dominant7"],
        ["Minor", "Minor6"], ["Major", "Major7"]
    ],
    "Verse": [
        ["Minor", "Minor"], ["Major7", "Dominant7"], ["Minor", "Minor6"], ["Minor", "Minor"],
        ["Major", "Add9"], ["Minor", "Minor7"], ["Major", "Major"], ["Major", "Dominant7"],
        ["Minor", "Minor6"], ["Major", "Major7"]
    ],
    "PreChorus": [
        ["Major", "Major"], ["Minor", "Minor"], ["Major", "Major7"], ["Major", "Major"],
        ["Minor", "Minor"], ["Major7", "Dominant7"], ["Minor", "Minor6"], ["Minor", "Minor"],
        ["Major", "Add9"], ["Minor", "Minor7"]
    ],
    "Chorus": [
        ["Major", "Add9"], ["Minor", "Minor7"], ["Major", "Major"], ["Major", "Dominant7"],
        ["Minor", "Minor"], ["Major7", "Dominant7"], ["Minor", "Minor6"], ["Minor", "Minor"],
        ["Major", "Add9"], ["Minor", "Minor7"]
    ],
    "PostChorus": [
        ["Major", "Major"], ["Major", "Add9"], ["Minor", "Minor"], ["Major", "Major"],
        ["Minor", "Minor"], ["Major7", "Dominant7"], ["Minor", "Minor6"], ["Minor", "Minor"],
        ["Major", "Add9"], ["Minor", "Minor7"]
    ],
    "Bridge": [
        ["Minor7", "Minor"], ["Minor", "Minor"], ["Major", "Major7"], ["Diminished", "HalfDiminished7"],
        ["Major", "Add9"], ["Minor", "Minor7"], ["Major", "Major"], ["Major", "Dominant7"],
        ["Minor", "Minor6"], ["Major", "Major7"]
    ],
    "Breakdown": [
        ["Major", "Major"], ["Minor", "Minor"], ["Diminished", "Minor"], ["Augmented", "Major"],
        ["Minor", "Minor"], ["Major7", "Dominant7"], ["Minor", "Minor6"], ["Minor", "Minor"],
        ["Major", "Add9"], ["Minor", "Minor7"]
    ],
    "Outro": [
        ["Minor", "Minor"], ["Minor", "Minor6"], ["Major7", "Major"], ["Minor", "Diminished"],
        ["Major", "Add9"], ["Minor", "Minor7"], ["Major", "Major"], ["Major", "Dominant7"],
        ["Minor", "Minor6"], ["Major", "Major7"]
    ],
    "AltOutro": [
        ["Major", "Major"], ["Major7", "Major"], ["Minor", "Minor7"], ["Diminished", "HalfDiminished7"],
        ["Major", "Add9"], ["Minor", "Minor7"], ["Major", "Major"], ["Major", "Dominant7"],
        ["Minor", "Minor6"], ["Major", "Major7"]
    ]
}


song_structures = [
    ["Intro"],
    ["Verse"],
    ["Chorus"],
    ["Verse"],
    ["Chorus"],
    ["Bridge"],
    ["Chorus", "Chorus"],
    ["Outro"]
]

song_names_list = [
    "Cosmic Spaghetti",
    "Temporal Jiggle",
    "Electric Moonwalk",
    "Limbo of Laughter",
    "Funky Chicken Fandango",
    "Whiskey Tango Foxtrot",
    "Cat Meme Cathedral",
    "The Subtle Art of Not Giving a Meow",
    "Cereal Killer Diaries",
    "The Yawning Chasm of Adulthood"

]


#=========================================================================================================
#=========================================================================================================
#=========================================================================================================
#=========================================================================================================

# G U I

# G U I

# G U I

#=========================================================================================================
#=========================================================================================================
#=========================================================================================================


def start_gui():
    global model_dropdown  # Declare it as global
    root = tk.Tk()
    root.title("Soundstorm")

    # Add the audio frame at row 2, column 0
    create_audio_frame(root)

    # Create a frame with a thin border
    frame = tk.Frame(root, bd=1, relief="solid")  # bd is the border width, relief specifies the border type

    # Place your widgets inside the frame
    ttk.Label(frame, text="What sort of song or sound do you want to hear? ").pack(pady=5)
    global text_input
    text_input = tk.Text(frame, height=3, width=30)
    text_input.pack(pady=5)

    # Create and pack the model dropdown
    model_choices = ['meta/musicgen', 'allenhung1025/looptest']
    model_dropdown = ttk.Combobox(frame, values=model_choices)
    model_dropdown.set(model_choices[0])  # Default choice
    model_dropdown.pack(pady=5)

    # Add a new button to trigger random GPT prompt
    gpt_button = tk.Button(frame, text="Random GPT Prompt", command=generate_random_prompt)
    gpt_button.pack(pady=5)

    generate_button = ttk.Button(frame, text="Generate AI Audio", command=generate_music)
    generate_button.pack(pady=5)

    frame.grid(row=0, column=0, padx=5, pady=5)

    # ========================================================================================================
    # ========================================================================================================

    # p l a y b a c k   f r a m e

    music_frame = tk.Frame(root)
    music_frame.grid(row=0, column=3)

    # Initialize MusicPlayer with the frame
    player = MusicPlayer(music_frame)

    # ========================================================================================================
    # ========================================================================================================

    # A L G O R I T H M I C    C O M P O S I T I O N   g u i

    # Combined Sound FX and Save Settings Frame
    combined_fx_save_frame = tk.LabelFrame(root, text="Algorithmic Composition", padx=10, pady=10)
    combined_fx_save_frame.grid(row=1, column=1, padx=5, pady=5)

    # How many files
    tk.Label(combined_fx_save_frame, text="How many files?").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
    num_sounds_entry = tk.Entry(combined_fx_save_frame)
    num_sounds_entry.grid(row=0, column=1, padx=5, pady=5)
    num_sounds_entry.insert(0, "8")

    # Max Duration
    tk.Label(combined_fx_save_frame, text="Max duration (in milliseconds):").grid(row=1, column=0, sticky=tk.W, padx=5,
                                                                                  pady=5)
    length_slider = tk.Scale(combined_fx_save_frame, from_=400, to=6000, resolution=100, orient=tk.HORIZONTAL)
    length_slider.grid(row=1, column=1, padx=5, pady=5)
    length_slider.set(6000)

    # Randomness Factor
    tk.Label(combined_fx_save_frame, text="How random?").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
    randomness_slider = tk.Scale(combined_fx_save_frame, from_=0, to=1, resolution=0.01, orient=tk.HORIZONTAL)
    randomness_slider.grid(row=2, column=1, padx=5, pady=5)
    randomness_slider.set(0.5)

    # File name prefix
    tk.Label(combined_fx_save_frame, text="File name prefix:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
    prefix_entry = tk.Entry(combined_fx_save_frame)
    prefix_entry.grid(row=3, column=1, padx=5, pady=5)
    prefix_entry.insert(0, "sound")

    def on_generate():
        try:
            num_sounds = int(num_sounds_entry.get())
            prefix = prefix_entry.get()
            randomness_factor = randomness_slider.get()
            max_duration = length_slider.get()
            main(num_sounds, prefix, randomness_factor)  # Updated main call
            messagebox.showinfo("Success", "Sounds generated successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    # Generate Randomly Coded Audio Button
    generate_btn = tk.Button(combined_fx_save_frame, text="Code Audio", command=on_generate)
    generate_btn.grid(row=4, columnspan=2, pady=5)  # Placing it on the next available row in the grid

    # ========================================================================================================
    # ========================================================================================================

    # Initialize DrumLoopGenerator within the frame
    drum_loop_gen = DrumLoopGenerator()

    # Function to update DrumLoopGenerator parameters based on user input
    def update_drum_loop_parameters():
        drum_loop_gen.tempo = int(tempo_slider.get())
        drum_loop_gen.beat_length = int(beat_length_slider.get())
        update_instrument_parameters('kick', kick_likelihood_slider, kick_volume_slider)
        update_instrument_parameters('snare', snare_likelihood_slider, snare_volume_slider)
        update_instrument_parameters('hihat', hihat_likelihood_slider, hihat_volume_slider)
        status_label.config(text="Parameters Updated!")

    def update_instrument_parameters(instrument, likelihood_slider, volume_slider):
        drum_loop_gen.drum_generators[instrument]['likelihood'] = likelihood_slider.get()
        drum_loop_gen.drum_generators[instrument]['volume'] = volume_slider.get()

    # Function to trigger drum loop generation
    def on_generate_drum_loop():
        drum_loop_gen.generate_loop("drum_loop.wav")
        status_label.config(text="Drum Loop Generated!")

    # DrumLoopGenerator Frame
    drum_loop_frame = tk.Frame(root, relief='groove', borderwidth=2)
    drum_loop_frame.grid(row=1, column=2, padx=4, pady=4)

    # DrumLoopGenerator Label
    tk.Label(drum_loop_frame, text="Drum Loop Generator").grid(row=0, columnspan=2)

    # User Customization for Drum Loop Parameters
    tk.Label(drum_loop_frame, text="Customize Parameters").grid(row=1, columnspan=2)

    # Kick likelihood and volume sliders
    tk.Label(drum_loop_frame, text="Kick").grid(row=2, column=0)
    kick_likelihood_slider = tk.Scale(drum_loop_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal')
    kick_likelihood_slider.grid(row=2, column=1)
    kick_likelihood_slider.set(0.3)
    kick_volume_slider = tk.Scale(drum_loop_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal')
    kick_volume_slider.grid(row=2, column=2)
    kick_volume_slider.set(0.5)

    # Snare likelihood and volume sliders
    tk.Label(drum_loop_frame, text="Snare").grid(row=3, column=0)
    snare_likelihood_slider = tk.Scale(drum_loop_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal')
    snare_likelihood_slider.grid(row=3, column=1)
    snare_likelihood_slider.set(0.2)
    snare_volume_slider = tk.Scale(drum_loop_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal')
    snare_volume_slider.grid(row=3, column=2)
    snare_volume_slider.set(0.5)

    # Hihat likelihood and volume sliders
    tk.Label(drum_loop_frame, text="Hihat").grid(row=4, column=0)
    hihat_likelihood_slider = tk.Scale(drum_loop_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal')
    hihat_likelihood_slider.grid(row=4, column=1)
    hihat_likelihood_slider.set(0.2)
    hihat_volume_slider = tk.Scale(drum_loop_frame, from_=0.0, to=1.0, resolution=0.1, orient='horizontal')
    hihat_volume_slider.grid(row=4, column=2)
    hihat_volume_slider.set(0.5)

    # Tempo
    tk.Label(drum_loop_frame, text="Tempo").grid(row=5, column=0)
    tempo_slider = tk.Scale(drum_loop_frame, from_=60, to=240, orient='horizontal')
    tempo_slider.grid(row=5, column=1, columnspan=2)
    tempo_slider.set(120)

    # Beat Length
    tk.Label(drum_loop_frame, text="Beat Length").grid(row=6, column=0)
    beat_length_slider = tk.Scale(drum_loop_frame, from_=1, to=32, orient='horizontal')
    beat_length_slider.grid(row=6, column=1, columnspan=2)
    beat_length_slider.set(16)

    # Button to update parameters
    update_parameters_button = tk.Button(drum_loop_frame, text="Update Parameters", command=update_drum_loop_parameters)
    update_parameters_button.grid(row=7, columnspan=2)

    # Status label
    status_label = tk.Label(drum_loop_frame, text="")
    status_label.grid(row=9, columnspan=2)

    # DrumLoopGenerator Button to trigger generation (Only one button)
    drum_loop_button = tk.Button(drum_loop_frame, text="Generate Drum Loop", command=on_generate_drum_loop)
    drum_loop_button.grid(row=8, columnspan=2)



    # ========================================================================================================
    # ========================================================================================================

    # New Audio Effects Frame with a thin border
    audio_effects_frame = tk.Frame(root, bd=1,
                                   relief="solid")  # bd is the border width, relief specifies the border type
    audio_effects_frame.grid(row=0, column=2, padx=10, pady=10)

    # Declare variables for check buttons if not already done
    reverb_var = tk.IntVar()
    chorus_var = tk.IntVar()
    delay_var = tk.IntVar()
    flanger_var = tk.IntVar()
    distortion_var = tk.IntVar()

    load_button = ttk.Button(audio_effects_frame, text="Load Audio", command=load_audio)
    load_button.grid(column=0, row=0)

    reverb_check = ttk.Checkbutton(audio_effects_frame, text='Reverb', variable=reverb_var)
    reverb_check.grid(column=0, row=1, sticky=tk.W)

    chorus_check = ttk.Checkbutton(audio_effects_frame, text='Chorus', variable=chorus_var)
    chorus_check.grid(column=0, row=2, sticky=tk.W)

    delay_check = ttk.Checkbutton(audio_effects_frame, text='Delay', variable=delay_var)
    delay_check.grid(column=0, row=3, sticky=tk.W)

    flanger_check = ttk.Checkbutton(audio_effects_frame, text='Flanger', variable=flanger_var)
    flanger_check.grid(column=0, row=4, sticky=tk.W)

    distortion_check = ttk.Checkbutton(audio_effects_frame, text='Distortion', variable=distortion_var)
    distortion_check.grid(column=0, row=5, sticky=tk.W)

    # apply_button = ttk.Button(audio_effects_frame, text="Apply PyDub Effects", command=apply_effects)
    # apply_button.grid(column=0, row=6)

    process_button = ttk.Button(audio_effects_frame, text="Process Audio with Pedalboard", command=process_audio)
    process_button.grid(column=0, row=6)

    save_button = ttk.Button(audio_effects_frame, text="Save Audio", command=save_audio)
    save_button.grid(column=0, row=7)

    # m i d i    m a k e r   G U I

    song_generator_frame = tk.Frame(root, relief='groove', borderwidth=2)
    song_generator_frame.grid(row=1, column=0, padx=5, pady=5)
    song_generator = SongGeneratorGUI(song_generator_frame)

    # ========================================================================================================
    # ========================================================================================================

# C H A T   G U I


    chat_frame = tk.LabelFrame(root, text="ChatGPT")
    chat_frame.grid(row=1, column=3, padx=5, pady=5)

        # Text widget for chat display
    global chat_display
    chat_display = tk.Text(chat_frame, width=30, height=20, wrap=tk.WORD, state=tk.DISABLED)
    chat_display.pack(pady=5)

        # Entry widget for user input
    global user_input
    user_input = tk.Entry(chat_frame, width=20)
    user_input.pack(pady=5)

        # Button for sending message
    send_button = tk.Button(chat_frame, text="Send", command=send_message)
    send_button.pack(pady=5)



    root.mainloop()



if __name__ == "__main__":
    start_gui()
