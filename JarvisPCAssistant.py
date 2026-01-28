import os
import webbrowser
import speech_recognition as sr
import edge_tts
import asyncio
import pygame
import wikipedia
from openai import OpenAI
import tempfile
import time
from dotenv import load_dotenv

load_dotenv()

# ================== SETTINGS ==================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

WAKE_WORDS = ["jarvis", "jarvi", "jarv", "jar", "ja"]

VOICE = "en-GB-RyanNeural"  # Best British English male neural voice for Jarvis-like tone

APPS = {
    "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "spotify": r"C:\Users\PC\AppData\Roaming\Spotify\Spotify.exe",
    "discord": r"C:\Users\PC\AppData\Local\Discord\Update.exe --processStart Discord.exe",
    "notepad": "notepad.exe",
    "vscode": r"C:\Users\PC\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "code editor": r"C:\Users\PC\AppData\Local\Programs\Microsoft VS Code\Code.exe",
    "browser": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
    "steam": r"C:\Program Files (x86)\Steam\Steam.exe",
    "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
}

WORD_REPLACEMENTS = {
    "google": ["google", "gugle", "googol"],
    "youtube": ["youtube", "youtoob", "yutuub"],
    "spotify": ["spotify", "spotifai"],
    "discord": ["discord", "diskord"],
    "brave": ["brave", "breyv"],
    "vscode": ["vscode", "visual studio code", "vs code"],
    "wikipedia": ["wikipedia", "wiki"],
}

# ================== CONVERSATION MODE ==================

conversation_mode = False
last_command_time = 0
CONVERSATION_TIMEOUT = 30  # seconds

# ================== TTS - Edge TTS ==================

pygame.mixer.init()

async def create_speech_async(text, output_file, voice):
    try:
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_file)
        return True
    except Exception as e:
        print(f"❌ TTS Creation Error: {e}")
        return False

def speak(text):
    if not text or text.strip() == "":
        return
    
    print(f"🗣️ JARVIS: {text}")
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_file = fp.name
        
        success = asyncio.run(create_speech_async(text, temp_file, VOICE))
        
        if not success:
            print("❌ Failed to generate speech!")
            return
        
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
            print(f"❌ Speech file not created: {temp_file}")
            return
        
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.time.wait(100)
        
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
        except Exception as e:
            print(f"⚠️ Error deleting file (non-critical): {e}")
            
    except Exception as e:
        print(f"❌ Speech playback error: {e}")
        import traceback
        traceback.print_exc()

# ================== OPENAI ==================

client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def ai_answer(prompt):
    if not client:
        return "API key not configured, sir."
    
    try:
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are JARVIS, a helpful AI assistant. Respond in English, keep answers short and concise (max 2-3 sentences). Always provide accurate, reliable, and evidence-based information. If unsure or don't know, say 'I don't know' or cite a source. Do not make up information from Wikipedia or general knowledge."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=150,
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI Error: {e}")
        return "Unable to reach the AI module at the moment, sir."

# ================== SPEECH-TO-TEXT ==================

recognizer = sr.Recognizer()
recognizer.energy_threshold = 4000
recognizer.dynamic_energy_threshold = True
recognizer.pause_threshold = 0.8

def get_microphone():
    try:
        return sr.Microphone()
    except Exception as e:
        print(f"Microphone error: {e}")
        return None

def normalize_text(text):
    text = text.lower().strip()
    
    for english_word, variants in WORD_REPLACEMENTS.items():
        for variant in variants:
            if variant in text:
                text = text.replace(variant, english_word)
    
    return text

def check_wake_word(text):
    text = text.lower()
    for wake_word in WAKE_WORDS:
        if wake_word in text:
            return True
    return False

def listen(timeout=5, phrase_time_limit=10):
    mic = get_microphone()
    if not mic:
        return ""
    
    try:
        with mic as source:
            print("🎤 Listening...")
            recognizer.adjust_for_ambient_noise(source, duration=0.3)
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        
        print("🔄 Processing...")
        text = recognizer.recognize_google(audio, language="en-US").lower()
        normalized = normalize_text(text)
        
        print(f"📝 Heard: {text}")
        if text != normalized:
            print(f"📝 Normalized: {normalized}")
        
        return normalized
        
    except sr.WaitTimeoutError:
        print("⏱️ Timeout")
        return ""
    except sr.UnknownValueError:
        print("❌ Could not understand")
        return ""
    except Exception as e:
        print(f"❌ Error: {e}")
        return ""

# ================== COMMANDS ==================

def open_app(text):
    text = text.lower()
    
    for prefix in ["open", "start", "launch", "run"]:
        text = text.replace(prefix, "").strip()
    
    for name, path in APPS.items():
        if name in text:
            try:
                os.startfile(path)
                speak(f"Opening {name}, sir.")
                return True
            except Exception as e:
                speak(f"Error opening {name}, sir.")
                return False
    return False

def open_site(text):
    if "youtube" in text:
        webbrowser.open("https://youtube.com")
        speak("Opening YouTube, sir.")
        return True
    if "google" in text:
        webbrowser.open("https://google.com")
        speak("Opening Google, sir.")
        return True
    if "wikipedia" in text:
        webbrowser.open("https://wikipedia.org")
        speak("Opening Wikipedia, sir.")
        return True
    return False

def play_song(text):
    trigger_words = ["play", "song", "music", "listen to", "the song"]
    
    if any(word in text for word in trigger_words):
        query = text
        for word in trigger_words:
            query = query.replace(word, "")
        
        query = query.strip()
        
        if query:
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            speak(f"Playing '{query}' on YouTube, sir.")
            return True
    return False

def wiki_search(text):
    trigger_words = ["wikipedia", "tell me about", "what is", "who is", "about", "search"]
    
    if any(word in text for word in trigger_words):
        query = text
        for word in trigger_words + ["search", "look up", "info"]:
            query = query.replace(word, "")
        
        query = query.strip()
        
        if query and len(query) > 2:
            try:
                wikipedia.set_lang("en")
                result = wikipedia.summary(query, sentences=2)
                speak(result)
                return True
            except:
                speak("Could not find information on that topic, sir.")
                return True
    return False

def handle_time(text):
    if "time" in text or "what time" in text:
        from datetime import datetime
        now = datetime.now()
        speak(f"The time is {now.hour:02d}:{now.minute:02d}, sir.")
        return True
    return False

def handle_date(text):
    if "date" in text or "today" in text:
        from datetime import datetime
        now = datetime.now()
        month_names = ["", "January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        speak(f"Today is {month_names[now.month]} {now.day}, {now.year}, sir.")
        return True
    return False

# ================== VOICE TEST FUNCTION ==================

async def test_voice():
    print("\n" + "="*60)
    print("🔊 VOICE TEST IN PROGRESS...")
    print("="*60 + "\n")
    
    print(f"Current voice: {VOICE}")
    
    try:
        voices = await edge_tts.list_voices()
        english_voices = [v for v in voices if v["Locale"].startswith("en-")]
        
        print("\nAvailable English voices:")
        for v in english_voices:
            emoji = "👨" if v["Gender"] == "Male" else "👩"
            marker = "✓ IN USE" if v["ShortName"] == VOICE else ""
            print(f"{emoji} {v['ShortName']} ({v['Gender']}) {marker}")
    except Exception as e:
        print(f"Could not list voices: {e}")
    
    print("\n" + "="*60 + "\n")

# ================== MAIN LOOP ==================

def main():
    print("\n" + "="*60)
    print("🤖 JARVIS - Conversation Mode Active")
    print("="*60 + "\n")
    
    try:
        asyncio.run(test_voice())
    except Exception as e:
        print(f"⚠️ Voice test failed: {e}")
    
    speak("Jarvis online, sir.")
    global conversation_mode, last_command_time
    running = True
    
    while running:
        if conversation_mode and (time.time() - last_command_time > CONVERSATION_TIMEOUT):
            conversation_mode = False
            print("→ 30 seconds of silence → Conversation mode deactivated")

        heard = listen(timeout=10, phrase_time_limit=5)
        
        if not heard:
            continue
        
        if check_wake_word(heard):
            speak("Listening, sir.")
            conversation_mode = True
            last_command_time = time.time()
            continue
        
        if not conversation_mode:
            continue
        
        command = heard
        last_command_time = time.time()
        
        print(f"\n{'='*50}")
        print(f"💬 COMMAND: {command}")
        print(f"{'='*50}\n")
        
        if "shut down system" in command or "close" in command or "turn off" in command or "shut down" in command:
            speak("System is shutting down, sir.")
            running = False
            break
        
        if "test" in command and "voice" in command:
            speak("This is a voice test. Can you hear me, sir?")
            continue
        
        handled = False
        
        if handle_date(command): handled = True
        elif handle_time(command): handled = True
        elif "open" in command or "start" in command or "launch" in command:
            if open_app(command): handled = True
        elif any(word in command for word in ["youtube", "google", "wikipedia"]):
            if open_site(command): handled = True
        elif play_song(command): handled = True
        elif wiki_search(command): handled = True
        
        if not handled and client:
            answer = ai_answer(command)
            speak(answer)
        elif not handled:
            speak("I didn't understand that command, sir.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Shutting down program...")
        speak("Shutting down.")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        speak("An error occurred, sir.")