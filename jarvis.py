import ollama, speech_recognition as sr, webbrowser, datetime
import asyncio, edge_tts, pygame
from urllib.parse import quote_plus
import re
from pathlib import Path
import json, queue, time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from vosk import Model, KaldiRecognizer, SetLogLevel

SetLogLevel(-1)
vosk_model = Model("vosk-model-small-en-us-0.15")

def get_desktop():
    return Path("/home/noh4/Desktop")

def create_file(name):
    name = name.strip().replace(" dot ", ".")          # "notes dot txt" -> "notes.txt"
    name = re.sub(r'[<>:"/\\|?*]', "", name)            # remove characters Windows doesn't allow
    name = name.replace(" ", "_")
    if not name:
        return "I didn't catch the file name."
    if "." not in name:
        name += ".txt"                                   # default type
    path = get_desktop() / name
    if path.exists():
        return f"A file called {name} already exists on your desktop."
    path.touch()
    return f"Done. I created {name} on your desktop."


# funtion to speak (jarvis is talking ...)
pygame.mixer.init()
VOICE = "en-GB-RyanNeural"   # British male, very Jarvis-like

async def _generate(text):
    await edge_tts.Communicate(text, VOICE).save("reply.mp3")

def speak(text):
    """Speaks. If you say 'Jarvis' while it talks, it stops and returns
    your next sentence. Returns None if not interrupted."""
    print("Jarvis:", text)
    asyncio.run(_generate(text))
    pygame.mixer.music.load("reply.mp3")
    pygame.mixer.music.play()

    # only listens for the word "jarvis", ignores everything else
    rec = KaldiRecognizer(vosk_model, 16000, '["jarvis", "[unk]"]')
    q = queue.Queue()

    def callback(indata, frames, t, status):
        q.put(bytes(indata))

    woke = False
    command = None

    with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype="int16",
                           channels=1, callback=callback):
        # Phase 1: wait for the word "jarvis" while audio plays
        while pygame.mixer.music.get_busy():
            try:
                data = q.get(timeout=0.1)
            except queue.Empty:
                continue
            if rec.AcceptWaveform(data):
                heard = json.loads(rec.Result()).get("text", "")
            else:
                heard = json.loads(rec.PartialResult()).get("partial", "")
            if "jarvis" in heard:
                woke = True
                pygame.mixer.music.stop()
                break

        # Phase 2: record your command in the same stream (no lost words)
        if woke:
            print("(interrupted)")
            frames, silent, started = [], 0, False
            t0 = time.time()
            while time.time() - t0 < 10:
                try:
                    data = q.get(timeout=0.5)
                except queue.Empty:
                    continue
                frames.append(data)
                vol = np.sqrt(np.mean((np.frombuffer(data, np.int16) / 32768) ** 2))
                if vol > 0.02:
                    started, silent = True, 0
                else:
                    silent += 1
                if started and silent >= 4:      # ~1 second of silence
                    break
                if not started and time.time() - t0 > 4:
                    break                         # you said nothing
            command = transcribe_bytes(frames) if frames else ""

    pygame.mixer.music.unload()
    return command   # None = not interrupted, "" = interrupted but no command

def transcribe_bytes(frames):
    audio = np.frombuffer(b"".join(frames), dtype=np.int16)
    write("temp.wav", 16000, audio)
    r = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        data = r.record(source)
    try:
        return r.recognize_google(data)
    except Exception:
        return ""

# function to listen (I'm talking ...)
def listen():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        audio = r.listen(source)
    try:
        return r.recognize_google(audio)
    except Exception:
        return ""

# the Brain (The Orders You Have To Do) -- CHANGEABLE
def handle(command):
    c = command.lower()

    if "time" in c:
        return datetime.datetime.now().strftime("It is %I:%M %p")
    if "open youtube" in c:
        webbrowser.open("https://youtube.com")
        return "Opening YouTube"
    if "open claude" in c:
        webbrowser.open("https://claude.ai/new")
        return "Opening claude"
    if "search for" in c:
        query = c.replace("search for", "").strip()
        webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
        return f"Searching for {query}"
    # create file
    m = re.search(r"(?:create|make)\s+(?:a\s+)?file\s+(?:called|named|with name)?\s*(.+)", c)
    if m:
        return create_file(m.group(1))
        
    # Turn OFF
    if "off" in c:
        return "good bye sir"

    # otherwise, ask the LLM
    reply = ollama.chat(model="llama3.2:1b", messages=[
        {"role": "system", "content": "You are Jarvis, a witty, concise assistant."},
        {"role": "user", "content": command}])
    return reply["message"]["content"]


# Launch
speak("Online and ready sir.")
heard = None

while True:
    if heard is not None:            # you interrupted with "Jarvis"
        cmd, direct = heard, True
        heard = None
    else:
        cmd, direct = listen(), False

    if direct and not cmd:           # said "Jarvis" but no command
        heard = speak("Yes, sir?")
        continue
    if not cmd:
        continue

    if direct or "jarvis" in cmd.lower():
        text = cmd.lower().replace("jarvis", "").strip()
        heard = speak(handle(text))

        if "off" in text:
            exit()

