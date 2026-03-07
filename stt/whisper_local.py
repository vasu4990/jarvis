"""
Whisper-based Speech-to-Text (Local)
"""

import asyncio
import structlog
import io
import soundfile as sf
from faster_whisper import WhisperModel
from utils.schemas import Utterance
from datetime import datetime

logger = structlog.get_logger(__name__)


class WhisperSTT:
    """Local speech-to-text using Whisper"""
    
    def __init__(self, config):
        self.config = config
        
        model_size = config.get("stt.model", "small")
        device = config.get("stt.device", "cuda")
        compute_type = config.get("stt.compute_type", "float16")
        
        logger.info(
            "Loading Whisper model",
            model=model_size,
            device=device,
            compute_type=compute_type
        )
        
        try:
            self.model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type
            )
            logger.info("✓ Whisper model loaded")
        except Exception as e:
            logger.error("Failed to load Whisper model", error=str(e))
            # Fallback to CPU
            logger.info("Falling back to CPU")
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            
        self.language = config.get("stt.language", "en")
        self.beam_size = config.get("stt.beam_size", 5)
        self.vad_filter = config.get("stt.vad_filter", True)
        
    async def transcribe(self, audio_data: bytes) -> Utterance:
        """
        Transcribe audio bytes to text
        
        Args:
            audio_data: Raw PCM audio bytes (16-bit, 16kHz mono)
            
        Returns:
            Utterance object with transcription
        """
        try:
            # Convert bytes to audio array
            audio_array, sample_rate = await self._bytes_to_array(audio_data)
            
            # Run transcription in executor (blocking operation)
            segments, info = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.transcribe(
                    audio_array,
                    language=self.language,
                    beam_size=self.beam_size,
                    vad_filter=self.vad_filter
                )
            )
            
            # Combine segments
            text_parts = []
            all_tokens = []
            
            for segment in segments:
                text_parts.append(segment.text.strip())
                all_tokens.extend(segment.text.split())
                
            full_text = " ".join(text_parts)
            
            logger.info(
                "Transcription complete",
                text=full_text,
                language=info.language,
                probability=round(info.language_probability, 2)
            )
            
            # Create Utterance
            utterance = Utterance(
                session_id="",  # Will be set by caller
                source="microphone",
                text=full_text,
                language=info.language,
                stt_confidence=info.language_probability,
                tokens=all_tokens,
                metadata={
                    "duration": info.duration,
                    "vad_filter": self.vad_filter
                }
            )
            
            return utterance
            
        except Exception as e:
            logger.error("Transcription failed", error=str(e), exc_info=True)
            # Return empty utterance
            return Utterance(
                session_id="",
                source="microphone",
                text="",
                stt_confidence=0.0
            )
            
    async def _bytes_to_array(self, audio_bytes: bytes):
        """Convert raw audio bytes to numpy array"""
        # PCM 16-bit, 16kHz, mono
        import numpy as np
        
        # Convert to numpy array
        audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
        
        # Convert to float32 [-1, 1]
        audio_array = audio_array.astype(np.float32) / 32768.0
        
        sample_rate = self.config.get("audio.sample_rate", 16000)
        
        return audio_array, sample_rate
