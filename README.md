# J.A.R.V.I.S. Voice Assistant

A free, voice-controlled AI assistant inspired by Iron Man's J.A.R.V.I.S., built in Python.
It listens to your voice, thinks with Google's Gemini AI, and answers with a natural-sounding voice.
You can interrupt it mid-sentence by saying **"Jarvis"**.

Everything uses free tools (including the free Gemini API tier), so it costs $0 to build and run.

> ⚠️ **Important: this project is configured for one specific PC.**
> The "create file" command saves files to a hardcoded Desktop path: `/home/user/Desktop`.
> On any other computer you must change that path first. See [Changing the Desktop path](#changing-the-desktop-path).

---

## Features

- Voice input using speech recognition
- AI brain powered by the **Gemini API** (free tier), with a Jarvis personality and short conversation memory
- Natural text-to-speech using **edge-tts**
- Interrupt Jarvis while it talks by saying "Jarvis" (offline word detection with **Vosk**)
- Built-in commands:
  - Tell the time
  - Open YouTube
  - Search Google
  - Create a file on the Desktop
  - Open a file from the Desktop by saying its name
- Easy to extend with your own commands

---

## Requirements

### Operating system
- Linux (tested on a Debian/Ubuntu-based system)

### Software
- Python 3.10 or newer
- A free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
- A working microphone and speakers (headphones are strongly recommended, see [Tips](#tips))
- An internet connection (needed by the Gemini API, `edge-tts` for the voice, and Google speech recognition)

### System packages (Linux)
```bash
sudo apt install libportaudio2 portaudio19-dev python3-venv wget unzip xdg-utils
```

### Python packages
Listed in `requirements.txt`:

| Package | Purpose |
|---|---|
| `google-genai` | Talk to the Gemini API |
| `SpeechRecognition` | Convert your speech to text |
| `sounddevice` | Record from the microphone |
| `numpy` | Audio processing |
| `scipy` | Save audio as WAV files |
| `vosk` | Offline detection of the word "Jarvis" |
| `edge-tts` | Natural text-to-speech voice |
| `pygame` | Play the generated voice audio |

### Models
- **Gemini model:** `gemini-2.5-flash` (used through the API, nothing to download)
- **Vosk model:** `vosk-model-small-en-us-0.15` (small English model, already included in the repo as an unzipped folder)

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

### 3. Get a Gemini API key and save it
1. Go to https://aistudio.google.com/apikey, sign in with Google and click **Create API key**.
2. Save the key as an environment variable (never write it inside the code):
```bash
echo 'export GEMINI_API_KEY="paste-your-key-here"' >> ~/.bashrc
source ~/.bashrc
```
3. Check that it is set: `echo $GEMINI_API_KEY` should print your key.

### 4. Vosk model (already included)
The Vosk model is already included in this repository as the folder `vosk-model-small-en-us-0.15`, so there is nothing to download or unzip. Just make sure the folder stays next to `jarvis.py`:
```bash
ls
```
You should see both `jarvis.py` and `vosk-model-small-en-us-0.15`.

> If the folder is missing, you can download it from the official source and unzip it in the project folder:
> ```bash
> wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
> unzip vosk-model-small-en-us-0.15.zip
> ```

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
    return Path("/home/user/Desktop")
```

This path belongs to the original author's PC, so **it will not work on your computer unless your username is also `user`.**

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
| "Jarvis, open file notes" | Opens `notes.txt` from your Desktop folder with the default app |
| "Jarvis, tell me a joke" | Any other question goes to the AI model |

**Interrupting:** while Jarvis is talking, say "Jarvis". It stops immediately and listens to your next sentence, with no need to repeat the wake word.

**Opening files:** Jarvis searches your Desktop folder for the name you say. Say the extension ("notes dot md") if several files share a name.

**File creation rules:**
- Spaces in names become underscores (`my project` becomes `my_project.txt`)
- If you give no extension, `.txt` is used
- Existing files are never overwritten

---

## Configuration

| Setting | Where | Default |
|---|---|---|
| Gemini model | `MODEL` variable | `gemini-2.5-flash` |
| Jarvis personality | `SYSTEM_PROMPT` variable | Polite British-butler style, short spoken answers |
| Max reply length | `max_output_tokens` | 200 |
| Voice | `VOICE` variable | `en-GB-RyanNeural` |
| Desktop / output folder | `get_desktop()` | `/home/user/Desktop` |
| Listening time | `listen(seconds=5)` | 5 seconds |
| Vosk model folder | `Model("vosk-model-small-en-us-0.15")` | same folder as `jarvis.py` |

To list all available voices: `edge-tts --list-voices`

### API key safety
Jarvis reads the key from the `GEMINI_API_KEY` environment variable. **Never write your key directly in the code or upload it to GitHub.** If you leak it by mistake, delete it at https://aistudio.google.com/apikey and create a new one.

---

## Tips

- **Use headphones.** With speakers, the microphone can hear Jarvis's own voice and confuse the "Jarvis" detection.
- Say "Jarvis" clearly and a bit louder than normal when interrupting.
- If replies are slow, keep `max_output_tokens` low and `thinking_budget=0`. If you hit the free limit, try `gemini-2.5-flash-lite`.

---

## Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError` | Activate the virtual environment (`source ~/jarvis-env/bin/activate`) and run `pip install -r requirements.txt` |
| `externally-managed-environment` | You are outside the virtual environment. Activate it first. |
| `sounddevice` or PortAudio error | `sudo apt install libportaudio2 portaudio19-dev` |
| Vosk error: folder does not contain model files | Make sure the folder `vosk-model-small-en-us-0.15` is next to `jarvis.py` (step 4) |
| `No module named 'google'` | Install the right package inside your virtual environment: `pip install google-genai` (not `google-generativeai`) |
| API key not found | Run `echo $GEMINI_API_KEY`. If empty, repeat step 3 and start Jarvis from that terminal |
| `429` or quota error | You reached the free tier limit. Wait, or use `gemini-2.5-flash-lite` |
| "Model not found" | Model names change. Check https://ai.google.dev/gemini-api/docs/models and update `MODEL` |
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
└── vosk-model-small-en-us-0.15/   # Vosk speech model (included in the repo)
```

---

## Known limitations

- Built and tested for one Linux PC. The Desktop path is hardcoded (see above).
- Needs internet for the AI (Gemini API), the voice (edge-tts) and speech recognition (Google).
- The free Gemini tier has usage limits.
- Interrupting works best with headphones.

---

## Contributing

Pull requests and ideas are welcome. Feel free to add new commands to `handle()`.

## License

Add a license of your choice (for example MIT) by creating a `LICENSE` file.
