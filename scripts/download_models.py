"""
Model download script for JARVIS
Downloads required models on first run
"""

import os
import sys
from pathlib import Path

print("=" * 60)
print("JARVIS Model Downloader")
print("=" * 60)

# Create models directory
models_dir = Path("models")
models_dir.mkdir(exist_ok=True)

print("\n📦 Downloading models...\n")

# 1. Download Whisper model
print("1️⃣ Downloading Whisper STT model (small)...")
try:
    import whisper
    model = whisper.load_model("small", download_root=str(models_dir))
    print("   ✓ Whisper model downloaded\n")
except Exception as e:
    print(f"   ⚠️ Whisper download failed: {e}")
    print("   Will download on first use.\n")

# 2. Download sentence-transformers embedding model
print("2️⃣ Downloading embedding model (MiniLM-L6)...")
try:
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(
        "sentence-transformers/all-MiniLM-L6-v2",
        cache_folder=str(models_dir / "embeddings")
    )
    print("   ✓ Embedding model downloaded\n")
except Exception as e:
    print(f"   ⚠️ Embedding download failed: {e}")
    print("   Will download on first use.\n")

# 3. Download Coqui TTS model
print("3️⃣ Downloading TTS model (optional)...")
try:
    from TTS.api import TTS
    tts = TTS("tts_models/en/ljspeech/tacotron2-DDC")
    print("   ✓ TTS model downloaded\n")
except Exception as e:
    print(f"   ⚠️ TTS download failed: {e}")
    print("   Will fall back to pyttsx3.\n")

# 4. Install Playwright browsers
print("4️⃣ Installing Playwright browsers...")
try:
    import subprocess
    result = subprocess.run(
        ["playwright", "install", "chromium"],
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        print("   ✓ Playwright browsers installed\n")
    else:
        print(f"   ⚠️ Playwright install had issues: {result.stderr}\n")
except Exception as e:
    print(f"   ⚠️ Playwright install failed: {e}")
    print("   Run manually: playwright install chromium\n")

print("=" * 60)
print("✓ Model download complete!")
print("=" * 60)
print("\nNext steps:")
print("1. Copy config.example.yaml to config.yaml")
print("2. Edit config.yaml with your API keys")
print("3. Run: python app/main.py")
print()
