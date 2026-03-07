"""
Local Text-to-Speech using Coqui TTS
"""

import asyncio
import structlog
from TTS.api import TTS
import sounddevice as sd
import numpy as np

logger = structlog.get_logger(__name__)


class LocalTTS:
    """Text-to-speech using Coqui TTS"""
    
    def __init__(self, config):
        self.config = config
        
        engine = config.get("tts.engine", "coqui")
        model_name = config.get("tts.coqui_model", "tts_models/en/ljspeech/tacotron2-DDC")
        
        if engine == "coqui":
            logger.info("Loading Coqui TTS model", model=model_name)
            try:
                self.tts = TTS(model_name)
                self.engine = "coqui"
                logger.info("✓ Coqui TTS loaded")
            except Exception as e:
                logger.error("Failed to load Coqui TTS, falling back to pyttsx3", error=str(e))
                self._init_pyttsx3()
        else:
            self._init_pyttsx3()
            
    def _init_pyttsx3(self):
        """Initialize fallback TTS engine"""
        import pyttsx3
        self.tts = pyttsx3.init()
        self.engine = "pyttsx3"
        
        # Configure voice
        voices = self.tts.getProperty('voices')
        self.tts.setProperty('voice', voices[0].id)  # Use first voice
        self.tts.setProperty('rate', 175)  # Speed
        
        logger.info("✓ pyttsx3 TTS initialized")
        
    async def speak(self, text: str):
        """
        Speak text aloud
        
        Args:
            text: Text to speak
        """
        if not text or text.strip() == "":
            logger.warning("Empty text, skipping TTS")
            return
            
        logger.info("Speaking", text_len=len(text))
        
        try:
            if self.engine == "coqui":
                await self._speak_coqui(text)
            else:
                await self._speak_pyttsx3(text)
                
        except Exception as e:
            logger.error("TTS error", error=str(e), exc_info=True)
            
    async def _speak_coqui(self, text: str):
        """Speak using Coqui TTS"""
        # Generate audio in executor (blocking operation)
        wav = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.tts.tts(text)
        )
        
        # Convert to numpy array
        audio_array = np.array(wav, dtype=np.float32)
        
        # Play audio
        sample_rate = 22050  # Coqui default
        sd.play(audio_array, sample_rate)
        sd.wait()  # Wait until playback finishes
        
    async def _speak_pyttsx3(self, text: str):
        """Speak using pyttsx3"""
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.tts.say(text) or self.tts.runAndWait()
        )
