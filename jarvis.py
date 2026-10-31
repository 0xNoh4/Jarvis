import  speech_recognition as sr, webbrowser, datetime
import asyncio, edge_tts, pygame
from urllib.parse import quote_plus
import re
from pathlib import Path
import json, queue, time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from vosk import Model, KaldiRecognizer, SetLogLevel
import os, subprocess, tempfile
from google import genai
from google.genai import types


SYSTEM_PROMPT = """You are J.A.R.V.I.S., a personal AI assistant running on your user's computer, in the style of the assistant from the Iron Man films.

Personality:
- Polite, calm and professional, like a British butler, with dry, subtle wit.
- Address the user as "sir". Be confident but never arrogant.
- Occasional light humor is welcome, but never at the cost of being useful.

Rules for replies:
- Your replies are spoken aloud, so write plain conversational sentences only. No markdown, no bullet points, no emojis, no code blocks.
- Keep answers short: one to three sentences unless the user asks for detail.
- Answer the question directly first, then add extra only if it helps.
- If you don't know something, say so honestly. Never invent facts.
- You can open websites, search Google, tell the time, and create or open files on the desktop. Do not claim abilities you don't have.
- If a request is unclear, ask one short clarifying question."""

history = []   # remembers the last few messages

def clean_for_speech(text):
    text = re.sub(r"[*_`#>]", "", text)       # remove markdown symbols
    text = re.sub(r"\s+", " ", text).strip()
    return text


MODEL = "gemini-2.5-flash"

client = genai.Client()   # reads GEMINI_API_KEY from the environment automatically

chat = client.chats.create(
    model=MODEL,
    config=types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        max_output_tokens=200,
        temperature=0.7,
        thinking_config=types.ThinkingConfig(thinking_budget=0),  # faster replies
    ),
)

# ask llm "gemini"
def ask_llm(command):
    try:
        response = chat.send_message(command)
        answer = clean_for_speech(response.text or "")
        return answer or "I have no answer for that, sir."
    except Exception as e:
        print("Gemini error:", e)
        return "I'm having trouble reaching my brain, sir."

SetLogLevel(-1)
MODEL_PATH = Path(__file__).resolve().parent / "vosk-model-small-en-us-0.15"
vosk_model = Model(str(MODEL_PATH))

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

    with sd.RawInputStream(samplerate=16000, blocksize=4000, dtype="int16",channels=1, callback=callback):
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
    return ask_llm(command)


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

