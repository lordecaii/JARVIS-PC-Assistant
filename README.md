# JARVIS - Personal PC Assistant

# JARVIS - Personal PC Assistant (English)

This project is a fully English-speaking local JARVIS assistant powered by **Microsoft Edge TTS** (British English male voice) and **Google Speech-to-Text**. It wakes up with the wake-word "jarvis", then enters a 30-second conversation mode where you can give commands without repeating the wake-word. Each new command resets the timer.

Created by: **Lordecai**

## Features

- **English speech output** (using en-GB-RyanNeural voice – British accent)
- Wake-word detection: "jarvis", "jarvi", "jarv", "jar", "ja"
- **Conversation mode**: After saying "Jarvis", you have 30 seconds to issue commands without repeating the wake-word
  - Every new command resets the 30-second timer
  - After 30 seconds of silence, the mode turns off
- Supported commands:
  - Open applications (`open brave`, `start spotify`, `launch vscode`, `open browser`, etc.)
  - Open websites (`open youtube`, `open google`, `open wikipedia`)
  - Play songs (`play x song`, `play the song Back In Black`)
  - Wikipedia queries (`tell me about x`, `what is x`, `who is x`)
  - Time & date (`what time is it`, `what's today's date`)
  - General questions via OpenAI (`gpt-4o-mini` model, short & concise answers)
  - Shut down the assistant (`shutdown`, `close jarvis`, `turn off`)

## Requirements

- Python 3.8+
- Windows (application paths are Windows-specific)
- **Optional** — To use AI features: Obtain an API key from OpenAI and add some credit balance to your account

### Required Libraries

```bash
pip install speechrecognition edge-tts pygame wikipedia openai python-dotenv
Microsoft Edge must be installed on your system (required for TTS).

OpenAI API Key
Create an .env file inside the folder. Replace the placeholder with the actual key you received from OpenAI:
textOPENAI_API_KEY=sk-proj-XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
Get your key at: https://platform.openai.com/account/api-keys

Installation
Clone the repository or download the files:
Bashgit clone <repo-url>
cd jarvis
Add your OpenAI API key to the .env file (as shown above).
Install all dependencies at once by opening a terminal ( CMD / PowerShell ) in the project folder and running:
pip install -r requirements.txt

Usage
Make sure your microphone is on and working.
Say "Jarvis" → it replies "Listening, sir."
Then within 30 seconds you can give commands such as:

"Open browser"
"Start Spotify"
"Open YouTube"
"Tell me about Malibu"
"What time is it"
"Play the song: Back In Black"
"What is Minamata disease"
"Shut down system" or "shut down" or "close"

If you remain silent for 30 seconds, you need to say "Jarvis" again to wake it up.
Every command given within those 30 seconds resets the timer back to 30 seconds.
Customization

Voice: Change the VOICE variable (e.g. another English voice: en-GB-ThomasNeural)
Applications: Add new programs to the APPS dictionary
Wake-words: Add more entries to the WAKE_WORDS list
Timeout: Modify CONVERSATION_TIMEOUT = 30 (in seconds)
AI model: Replace gpt-4o-mini with gpt-4o or another model

Known Issues

If microphone sensitivity is low, decrease recognizer.energy_threshold (currently set to 4000 in the code)
Google Speech-to-Text may sometimes struggle with accents → language="en-US" is configured
Without an OpenAI API key, only basic (non-AI) commands will work

Feel free to fork, contribute, report bugs, or request new features.
