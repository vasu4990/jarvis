"""
Audio capture with VAD (Voice Activity Detection)
"""

import asyncio
import pyaudio
import numpy as np
import webrtcvad
import structlog
from collections import deque
from typing import Optional

logger = structlog.get_logger(__name__)


class AudioCapture:
    """Captures audio from microphone with VAD"""
    
    def __init__(self, config):
        self.config = config
        self.sample_rate = config.get("audio.sample_rate", 16000)
        self.channels = config.get("audio.channels", 1)
        self.chunk_duration_ms = config.get("audio.chunk_duration_ms", 30)
        self.silence_timeout_ms = config.get("audio.silence_timeout_ms", 1500)
        self.vad_aggressiveness = config.get("audio.vad_aggressiveness", 3)
        
        # Calculate chunk size
        self.chunk_size = int(self.sample_rate * self.chunk_duration_ms / 1000)
        
        # Initialize PyAudio
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.is_muted = False
        
        # Initialize VAD
        self.vad = webrtcvad.Vad(self.vad_aggressiveness)
        
        logger.info(
            "Audio capture initialized",
            sample_rate=self.sample_rate,
            chunk_size=self.chunk_size,
            vad_level=self.vad_aggressiveness
        )
        
    def start_stream(self):
        """Open audio stream"""
        if self.stream and self.stream.is_active():
            return
            
        device_index = self.config.get("audio.device_index")
        
        self.stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=self.chunk_size
        )
        
        logger.info("Audio stream opened")
        
    def stop_stream(self):
        """Close audio stream"""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            logger.info("Audio stream closed")
            
    async def record_until_silence(self) -> Optional[bytes]:
        """
        Record audio until silence detected
        Returns: Raw audio bytes (PCM 16-bit)
        """
        if self.is_muted:
            logger.warning("Cannot record - microphone is muted")
            return None
            
        try:
            self.start_stream()
            
            # Buffer for audio frames
            frames = []
            voiced_frames = deque(maxlen=30)  # Keep last 30 frames for smoothing
            
            # State tracking
            is_speech = False
            silence_frames = 0
            max_silence_frames = int(self.silence_timeout_ms / self.chunk_duration_ms)
            
            logger.info("Recording started", timeout_ms=self.silence_timeout_ms)
            
            while True:
                # Read chunk
                data = await asyncio.get_event_loop().run_in_executor(
                    None,
                    self.stream.read,
                    self.chunk_size,
                    False  # Don't throw on overflow
                )
                
                frames.append(data)
                
                # Check if voice detected
                is_voice = self.vad.is_speech(data, self.sample_rate)
                voiced_frames.append(is_voice)
                
                # Count recent voice frames
                recent_voice_count = sum(voiced_frames)
                
                if recent_voice_count > 15:  # More than half recent frames have voice
                    is_speech = True
                    silence_frames = 0
                else:
                    if is_speech:
                        silence_frames += 1
                        
                # Stop if silence threshold reached
                if is_speech and silence_frames > max_silence_frames:
                    logger.info("Silence detected, stopping recording")
                    break
                    
                # Safety limit - max 30 seconds
                if len(frames) > (30 * 1000 / self.chunk_duration_ms):
                    logger.warning("Max recording duration reached")
                    break
                    
                await asyncio.sleep(0.001)  # Yield control
                
            self.stop_stream()
            
            if not is_speech:
                logger.info("No speech detected in recording")
                return None
                
            # Combine all frames
            audio_data = b''.join(frames)
            duration_sec = len(frames) * self.chunk_duration_ms / 1000
            
            logger.info(
                "Recording complete",
                duration_sec=round(duration_sec, 2),
                size_kb=round(len(audio_data) / 1024, 2)
            )
            
            return audio_data
            
        except Exception as e:
            logger.error("Recording error", error=str(e), exc_info=True)
            self.stop_stream()
            return None
            
    def toggle_mute(self):
        """Toggle microphone mute"""
        self.is_muted = not self.is_muted
        logger.info("Microphone muted" if self.is_muted else "Microphone unmuted")
        
    def stop(self):
        """Cleanup resources"""
        self.stop_stream()
        self.audio.terminate()
        logger.info("Audio capture stopped")
