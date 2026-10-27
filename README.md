# J.A.R.V.I.S. Voice Assistant

A free, voice-controlled AI assistant inspired by Iron Man's J.A.R.V.I.S., built in Python.
It listens to your voice, thinks with a local language model (Ollama), and answers with a natural-sounding voice.
You can interrupt it mid-sentence by saying **"Jarvis"**.

Everything uses free tools, so it costs $0 to build and run.

> ⚠️ **Important: this project is configured for one specific PC.**
> The "create file" command saves files to a hardcoded Desktop path: `/home/noh4/Desktop`.
> On any other computer you must change that path first. See [Changing the Desktop path](#changing-the-desktop-path).

---

## Features

- Voice input using speech recognition
- AI brain powered by **Ollama** (local and private). Gemini or Groq can be used instead.
- Natural text-to-speech using **edge-tts**
- Interrupt Jarvis while it talks by saying "Jarvis" (offline word detection with **Vosk**)
- Built-in commands:
  - Tell the time
  - Open YouTube
  - Search Google
  - Create a file on the Desktop
- Easy to extend with your own commands

---

## Requirements

### Operating system
- Linux (tested on a Debian/Ubuntu-based system)

### Software
- Python 3.10 or newer
- [Ollama](https://ollama.com) installed and running
- A working microphone and speakers (headphones are strongly recommended, see [Tips](#tips))
- An internet connection (needed by `edge-tts` for the voice and by Google speech recognition)

### System packages (Linux)
```bash
sudo apt install libportaudio2 portaudio19-dev python3-venv wget unzip xdg-utils
```

### Python packages
Listed in `requirements.txt`:

| Package | Purpose |
|---|---|
| `ollama` | Talk to the local language model |
| `SpeechRecognition` | Convert your speech to text |
| `sounddevice` | Record from the microphone |
| `numpy` | Audio processing |
| `scipy` | Save audio as WAV files |
| `vosk` | Offline detection of the word "Jarvis" |
| `edge-tts` | Natural text-to-speech voice |
| `pygame` | Play the generated voice audio |

### Models
- **Ollama model:** `llama3.2` (about 2 GB). On a weak PC use `llama3.2:1b`.
- **Vosk model:** `vosk-model-small-en-us-0.15` (small English model, included in the repo as a zip file)

---

## Installation

### 1. Clone the repository
```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

### 2. Create a virtual environment and install packages
```bash
python3 -m venv ~/jarvis-env
source ~/jarvis-env/bin/activate
pip install -r requirements.txt
```

### 3. Download the Ollama model
```bash
ollama pull llama3.2
```
Check that it works with `ollama run llama3.2`, then type `/bye` to exit.

### 4. Unzip the Vosk model
The Vosk model is already included in this repository as `vosk-model-small-en-us-0.15.zip`. Unzip it inside the project folder (the model folder must be next to `jarvis.py`):
```bash
unzip vosk-model-small-en-us-0.15.zip
```
After unzipping you should see a folder called `vosk-model-small-en-us-0.15` next to `jarvis.py`.

> If the zip is missing, you can download it from the official source:
> `wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip`

### 5. Check your Desktop path
Open `jarvis.py` and make sure `get_desktop()` points to your own Desktop. See the next section.

### 6. Run
```bash
source ~/jarvis-env/bin/activate
python jarvis.py
```
Jarvis says "Online and ready, sir." when it starts.

---

## Changing the Desktop path

The file-creation feature uses this function in `jarvis.py`:

```python
def get_desktop():
    return Path("/home/noh4/Desktop")
```

This path belongs to the original author's PC, so **it will not work on your computer unless your username is also `noh4`.**

**Option 1: automatic (works for any Linux user).** Replace the function with:
```python
def get_desktop():
    return Path.home() / "Desktop"
```

**Option 2: custom folder.** Put any folder you like:
```python
def get_desktop():
    return Path("/home/your-username/Documents")
```

If your system uses a different language, the Desktop folder may have another name (for example `Bureau` or `Escritorio`). Use Option 2 in that case.

---

## Usage

Say the word "Jarvis" followed by your command:

| You say | What happens |
|---|---|
| "Jarvis, what time is it" | Tells you the current time |
| "Jarvis, open YouTube" | Opens YouTube in your browser |
| "Jarvis, search for python tutorials" | Opens Google results for "python tutorials" |
| "Jarvis, create a file called notes" | Creates `notes.txt` in your Desktop folder |
| "Jarvis, create a file called report dot py" | Creates `report.py` |
| "Jarvis, tell me a joke" | Any other question goes to the AI model |

**Interrupting:** while Jarvis is talking, say "Jarvis". It stops immediately and listens to your next sentence, with no need to repeat the wake word.

**File creation rules:**
- Spaces in names become underscores (`my project` becomes `my_project.txt`)
- If you give no extension, `.txt` is used
- Existing files are never overwritten

---

## Configuration

| Setting | Where | Default |
|---|---|---|
| Ollama model | `model="llama3.2"` in `handle()` | `llama3.2` |
| Voice | `VOICE` variable | `en-GB-RyanNeural` |
| Desktop / output folder | `get_desktop()` | `/home/noh4/Desktop` |
| Listening time | `listen(seconds=5)` | 5 seconds |
| Vosk model folder | `Model("vosk-model-small-en-us-0.15")` | same folder as `jarvis.py` |

To list all available voices: `edge-tts --list-voices`

### Using Gemini or Groq instead of Ollama
Get a free API key, and store it in an environment variable. **Never write your key directly in the code or upload it to GitHub.**
```bash
export GEMINI_API_KEY="your-key"
```
Then read it in Python with `os.environ["GEMINI_API_KEY"]`.

---

## Tips

- **Use headphones.** With speakers, the microphone can hear Jarvis's own voice and confuse the "Jarvis" detection.
- Say "Jarvis" clearly and a bit louder than normal when interrupting.
- If replies are slow, use the smaller model: `ollama pull llama3.2:1b` and change the model name in the code.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Activate the virtual environment (`source ~/jarvis-env/bin/activate`) and run `pip install -r requirements.txt` |
| `externally-managed-environment` | You are outside the virtual environment. Activate it first. |
| `sounddevice` or PortAudio error | `sudo apt install libportaudio2 portaudio19-dev` |
| Vosk error: folder does not contain model files | Unzip `vosk-model-small-en-us-0.15.zip` in the project folder (step 4) |
| Ollama connection error | Make sure Ollama is running (`ollama serve`) |
| Jarvis does not hear you | Set the correct microphone as the default input in your system sound settings |
| File not created on Desktop | Fix the path in `get_desktop()` |
| Browser does not open | `sudo apt install xdg-utils` |

---

## Project structure

```
.
├── jarvis.py           # main program
├── requirements.txt    # Python dependencies
├── .gitignore
├── README.md
├── vosk-model-small-en-us-0.15.zip   # Vosk model (included in the repo)
└── vosk-model-small-en-us-0.15/      # created when you unzip the model (not in the repo)
```

---

## Known limitations

- Built and tested for one Linux PC. The Desktop path is hardcoded (see above).
- Needs internet for the voice (edge-tts) and speech recognition (Google).
- Interrupting works best with headphones.

---

## Contributing

Pull requests and ideas are welcome. Feel free to add new commands to `handle()`.

## License

Add a license of your choice (for example MIT) by creating a `LICENSE` file.
