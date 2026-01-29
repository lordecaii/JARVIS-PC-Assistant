import os
import webbrowser
import speech_recognition as sr
import asyncio
import subprocess
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

# ================== MICROPHONE SELECTION (FILTERED) ==================

selected_microphone_index = None

def select_microphone():
    """Let user select which microphone to use - only shows actual microphones"""
    global selected_microphone_index
    
    print("\n" + "="*60)
    print("🎤 MICROPHONE SELECTION")
    print("="*60 + "\n")
    
    all_mics = sr.Microphone.list_microphone_names()
    
    if not all_mics:
        print("❌ No microphones found!")
        return False
    
    filtered_mics = []
    exclude_keywords = [
        "stereo mix", "what u hear", "wave out", "sum", "output", 
        "speakers", "headphones", "loopback", "playback"
    ]
    
    for idx, mic_name in enumerate(all_mics):
        mic_lower = mic_name.lower()
        if not any(keyword in mic_lower for keyword in exclude_keywords):
            filtered_mics.append((idx, mic_name))
    
    if not filtered_mics:
        print("❌ No input microphones found!")
        print("\nShowing all devices instead:\n")
        for i, mic_name in enumerate(all_mics):
            print(f"  [{i}] {mic_name}")
        filtered_mics = [(i, name) for i, name in enumerate(all_mics)]
    else:
        print("Available input microphones:\n")
        for i, (original_idx, mic_name) in enumerate(filtered_mics):
            print(f"  [{original_idx}] {mic_name}")
    
    print("\n" + "-"*60)
    
    while True:
        try:
            choice = input(f"\nEnter microphone number: ").strip()
            
            if choice == "":
                print("❌ Please enter a number")
                continue
            
            mic_index = int(choice)
            
            if 0 <= mic_index < len(all_mics):
                selected_microphone_index = mic_index
                print(f"\n✅ Selected: [{mic_index}] {all_mics[mic_index]}\n")
                print("="*60 + "\n")
                return True
            else:
                print(f"❌ Invalid number. Enter a valid device number.")
        
        except ValueError:
            print("❌ Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\n⛔ Cancelled")
            return False

# ================== CONVERSATION MODE ==================

conversation_mode = False
last_command_time = 0
CONVERSATION_TIMEOUT = 30

# ================== TTS - Edge TTS (CLI Method - More Reliable) ==================

pygame.mixer.init()

def speak_edge_cli(text, voice="en-GB-RyanNeural"):
    """Use edge-tts CLI command instead of Python library"""
    if not text or text.strip() == "":
        return False
    
    temp_file = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            temp_file = fp.name
        
        # Use edge-tts command line tool (more stable)
        cmd = [
            "edge-tts",
            "--voice", voice,
            "--text", text,
            "--write-media", temp_file
        ]
        
        # Run with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode != 0:
            print(f"❌ edge-tts error: {result.stderr}")
            return False
        
        if not os.path.exists(temp_file) or os.path.getsize(temp_file) == 0:
            print(f"❌ Audio file not created")
            return False
        
        # Play the audio
        pygame.mixer.music.load(temp_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        pygame.time.wait(100)
        
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ edge-tts timeout")
        return False
    except FileNotFoundError:
        print("❌ edge-tts command not found!")
        print("   Install with: pip install edge-tts")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if temp_file and os.path.exists(temp_file):
            try:
                time.sleep(0.2)
                os.remove(temp_file)
            except:
                pass

def test_edge_tts():
    """Test if edge-tts is working"""
    print("\n🔍 Testing Edge TTS...")
    print("="*60)
    
    try:
        # Check if edge-tts command exists
        result = subprocess.run(
            ["edge-tts", "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            print(f"✅ edge-tts found: {result.stdout.strip()}")
            
            # Test actual speech generation
            print("   Testing voice generation...")
            if speak_edge_cli("Hi", "en-GB-RyanNeural"):
                print("✅ Edge TTS is working!")
                print("   Voice: en-GB-RyanNeural (British Male)")
                return True
            else:
                print("❌ Voice generation failed")
                return False
        else:
            print("❌ edge-tts not working properly")
            return False
            
    except FileNotFoundError:
        print("❌ edge-tts not installed!")
        print("\n💡 Install with:")
        print("   pip uninstall edge-tts")
        print("   pip install edge-tts --upgrade")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def speak(text):
    """Main speak function using edge-tts CLI"""
    if not text or text.strip() == "":
        return
    
    print(f"🗣️ JARVIS: {text}")
    
    success = speak_edge_cli(text, "en-GB-RyanNeural")
    
    if not success:
        print("⚠️ Speech failed - continuing in text mode")

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
        if selected_microphone_index is not None:
            return sr.Microphone(device_index=selected_microphone_index)
        else:
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

# ================== MAIN LOOP ==================

def main():
    if not select_microphone():
        print("\n❌ No microphone selected. Exiting...\n")
        return
    
    print("\n" + "="*60)
    print("🤖 JARVIS - Conversation Mode Active")
    print("="*60 + "\n")
    
    # Test Edge TTS
    if not test_edge_tts():
        print("\n⚠️ WARNING: Edge TTS is not working!")
        print("   Trying to fix...")
        print("\n   Run these commands:")
        print("   1. pip uninstall edge-tts")
        print("   2. pip install edge-tts --upgrade")
        print("   3. Restart the program")
        
        response = input("\n   Continue anyway? (y/n): ").lower()
        if response != 'y':
            return
    
    print("\n" + "="*60 + "\n")
    
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
        print("\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        speak("An error occurred, sir.")
