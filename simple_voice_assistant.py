"""Minimal Windows voice-command automation utility.

This module intentionally uses explicit command mappings rather than presenting
keyword automation as general-purpose intelligence.
"""

from __future__ import annotations

import subprocess
from datetime import datetime
from typing import Any

import pyttsx3
import speech_recognition as sr


class SimpleVoiceAssistant:
    """Speech-to-command loop for a small set of explicit Windows actions."""

    def __init__(self) -> None:
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()

        self.tts = pyttsx3.init()
        self.tts.setProperty("rate", 175)

        self.commands = self.load_commands()

        print("Simple Voice Assistant ready")
        print("Commands:")
        for command in self.commands:
            print(f"  - {command}")

    @staticmethod
    def load_commands() -> dict[str, dict[str, Any]]:
        """Return the explicit phrase-to-action mapping."""
        return {
            "open chrome": {"action": "open", "target": "chrome"},
            "open firefox": {"action": "open", "target": "firefox"},
            "open edge": {"action": "open", "target": "msedge"},
            "open notepad": {"action": "open", "target": "notepad"},
            "open calculator": {"action": "open", "target": "calc"},
            "open explorer": {"action": "open", "target": "explorer"},
            "what time": {"action": "time"},
            "volume up": {"action": "volume", "value": "+5"},
            "volume down": {"action": "volume", "value": "-5"},
            "mute": {"action": "volume", "value": "0"},
            "open youtube": {
                "action": "url",
                "target": "https://youtube.com",
            },
            "open github": {
                "action": "url",
                "target": "https://github.com",
            },
        }

    def listen(self) -> str | None:
        """Capture one short utterance and transcribe it with Whisper."""
        with self.microphone as source:
            print("\nListening...")
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=5,
                    phrase_time_limit=5,
                )
                print("Processing...")
                text = self.recognizer.recognize_whisper(audio, model="base")
                print(f"Recognized: {text}")
                return text.lower()
            except sr.WaitTimeoutError:
                print("No speech detected")
            except sr.UnknownValueError:
                print("Speech was not understood")
            except Exception as exc:
                print(f"Speech recognition error: {exc}")

        return None

    def execute(self, text: str | None) -> bool:
        """Match one transcribed phrase to a configured action."""
        if not text:
            return False

        if text in self.commands:
            self._do_action(self.commands[text])
            return True

        for phrase, command in self.commands.items():
            if phrase in text or text in phrase:
                print(f"Matched command: {phrase}")
                self._do_action(command)
                return True

        print(f"Unknown command: {text}")
        self.speak("I don't know that command")
        return False

    def _do_action(self, command: dict[str, Any]) -> None:
        """Execute one trusted action from the static command map."""
        action = command["action"]

        try:
            if action == "open":
                application = command["target"]
                subprocess.Popen(application, shell=True)
                self.speak(f"Opening {application}")
                print(f"Opened: {application}")

            elif action == "url":
                url = command["target"]
                subprocess.Popen(f"start {url}", shell=True)
                self.speak("Opening")
                print(f"Opened: {url}")

            elif action == "time":
                time_string = datetime.now().strftime("%I:%M %p")
                self.speak(f"It's {time_string}")
                print(time_string)

            elif action == "volume":
                value = command["value"]
                if value == "0":
                    subprocess.run(
                        "nircmd mutesysvolume 1",
                        shell=True,
                        check=False,
                    )
                    self.speak("Muted")
                else:
                    delta = int(value) * 655
                    subprocess.run(
                        f"nircmd changesysvolume {delta}",
                        shell=True,
                        check=False,
                    )
                    self.speak("Done")

        except Exception as exc:
            print(f"Command execution error: {exc}")
            self.speak("Command failed")

    def speak(self, text: str) -> None:
        """Speak a short response."""
        self.tts.say(text)
        self.tts.runAndWait()

    def run(self) -> None:
        """Run the voice-command loop until interrupted."""
        print("\n" + "=" * 50)
        print("SIMPLE VOICE ASSISTANT")
        print("=" * 50)
        print("\nPress Ctrl+C to exit")

        try:
            while True:
                text = self.listen()
                if text:
                    self.execute(text)
        except KeyboardInterrupt:
            print("\nExiting voice assistant")


if __name__ == "__main__":
    SimpleVoiceAssistant().run()
