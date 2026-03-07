# 🎤 Realistic Voice Command System
# No LLMs, no agents, no BS - just reliable automation

import speech_recognition as sr
import pyttsx3
import subprocess
import json
from pathlib import Path

class SimpleVoiceAssistant:
    """
    Brutally simple voice command system that actually works.
    No AI hype - just speech recognition + keyword matching + actions.
    """
    
    def __init__(self):
        # Speech recognition
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-speech
        self.tts = pyttsx3.init()
        self.tts.setProperty('rate', 175)
        
        # Load command mappings
        self.commands = self.load_commands()
        
        print("✅ Simple Voice Assistant Ready")
        print("Commands:")
        for cmd in self.commands.keys():
            print(f"  - {cmd}")
    
    def load_commands(self):
        """Load simple command mappings"""
        return {
            # Browser
            "open chrome": {"action": "open", "target": "chrome"},
            "open firefox": {"action": "open", "target": "firefox"},
            "open edge": {"action": "open", "target": "msedge"},
            
            # Apps
            "open notepad": {"action": "open", "target": "notepad"},
            "open calculator": {"action": "open", "target": "calc"},
            "open explorer": {"action": "open", "target": "explorer"},
            
            # System
            "what time": {"action": "time"},
            "volume up": {"action": "volume", "value": "+5"},
            "volume down": {"action": "volume", "value": "-5"},
            "mute": {"action": "volume", "value": "0"},
            
            # Custom (add your own!)
            "open youtube": {"action": "url", "target": "https://youtube.com"},
            "open github": {"action": "url", "target": "https://github.com"},
        }
    
    def listen(self):
        """Listen for voice command"""
        with self.microphone as source:
            print("\n🎤 Listening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("🔄 Processing...")
                
                # Use Whisper (better than Google)
                text = self.recognizer.recognize_whisper(audio, model="base")
                
                print(f"📝 You said: {text}")
                return text.lower()
                
            except sr.WaitTimeoutError:
                print("⏱️ No speech detected")
                return None
            except sr.UnknownValueError:
                print("❌ Could not understand")
                return None
            except Exception as e:
                print(f"❌ Error: {e}")
                return None
    
    def execute(self, text):
        """Execute matched command"""
        if not text:
            return
        
        # Exact match first
        if text in self.commands:
            cmd = self.commands[text]
            self._do_action(cmd)
            return True
        
        # Fuzzy match (contains keyword)
        for phrase, cmd in self.commands.items():
            if phrase in text or text in phrase:
                print(f"✓ Matched: {phrase}")
                self._do_action(cmd)
                return True
        
        print(f"❌ Unknown command: {text}")
        self.speak("I don't know that command")
        return False
    
    def _do_action(self, cmd):
        """Actually execute the action"""
        action = cmd["action"]
        
        try:
            if action == "open":
                # Open application
                app = cmd["target"]
                subprocess.Popen(app, shell=True)
                self.speak(f"Opening {app}")
                print(f"✅ Opened: {app}")
                
            elif action == "url":
                # Open URL in default browser
                url = cmd["target"]
                subprocess.Popen(f'start {url}', shell=True)
                self.speak("Opening")
                print(f"✅ Opened: {url}")
                
            elif action == "time":
                # Tell time
                from datetime import datetime
                now = datetime.now()
                time_str = now.strftime("%I:%M %p")
                self.speak(f"It's {time_str}")
                print(f"🕐 {time_str}")
                
            elif action == "volume":
                # Adjust volume (Windows)
                value = cmd["value"]
                if value == "0":
                    subprocess.run("nircmd mutesysvolume 1", shell=True)
                    self.speak("Muted")
                else:
                    subprocess.run(f"nircmd changesysvolume {int(value)*655}", shell=True)
                    self.speak("Done")
                
        except Exception as e:
            print(f"❌ Execution error: {e}")
            self.speak("Command failed")
    
    def speak(self, text):
        """Speak response"""
        self.tts.say(text)
        self.tts.runAndWait()
    
    def run(self):
        """Main loop"""
        print("\n" + "="*50)
        print("🎤 SIMPLE VOICE ASSISTANT")
        print("="*50)
        print("\nPress Ctrl+C to exit")
        print("Say a command...\n")
        
        try:
            while True:
                text = self.listen()
                if text:
                    self.execute(text)
                    
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")


if __name__ == "__main__":
    assistant = SimpleVoiceAssistant()
    assistant.run()
