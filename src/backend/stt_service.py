"""
Speech-to-Text Service using Groq Whisper Cloud (whisper-large-v3-turbo)
Lightweight, ultra-fast (~1s), serverless-friendly (0 MB local model weight)
"""
import os
import io
from pathlib import Path
from dotenv import load_dotenv

# Automatically load .env file if available
for p in [Path.cwd() / ".env", Path(__file__).resolve().parent.parent / ".env", Path(__file__).resolve().parent.parent.parent / ".env"]:
    if p.exists():
        load_dotenv(dotenv_path=p)
        break

from groq import Groq

# Initial prompt guiding Whisper to identify technical ML terminology accurately
TECHNICAL_PROMPT = (
    "This is a technical machine-learning interview. "
    "The conversation includes terms like TensorFlow, Keras, PyTorch, CNN, "
    "RNN, LSTM, Transformer, Conv2D, MaxPooling2D, MobileNet, EfficientNet, VGG16, "
    "training pipeline, data preprocessing, SMOTE, epochs, validation accuracy, "
    "loss function, learning rate, model evaluation, overfitting, underfitting, "
    "precision, recall, F1 score, Adam optimizer."
)


def get_groq_client() -> Groq:
    """Initialize Groq client with API key from environment"""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY belum diset! Silakan dapatkan API Key gratis di https://console.groq.com/keys "
            "dan tambahkan ke Environment Variables di Vercel (atau file .env saat dijalankan di lokal)."
        )
    return Groq(api_key=api_key)


def transcribe_video(video_input, filename: str = "recording.webm") -> dict:
    """
    Transcribe video/audio to text using Groq Whisper Cloud API.
    Supports raw bytes, file-like objects, or file paths.
    Returns:
        dict: {
            "text": str,
            "segments": [{"start": float, "end": float, "text": str}],
            "language": str,
            "language_probability": float
        }
    """
    client = get_groq_client()

    # Normalize input to (filename, BytesIO, mime_type) tuple
    if isinstance(video_input, (bytes, bytearray)):
        file_tuple = (filename, io.BytesIO(video_input), "video/webm")
    elif isinstance(video_input, str):
        with open(video_input, "rb") as f:
            file_tuple = (filename, io.BytesIO(f.read()), "video/webm")
    elif hasattr(video_input, "read"):
        data = video_input.read()
        file_tuple = (filename, io.BytesIO(data), "video/webm")
    else:
        raise ValueError("Format input video tidak didukung")

    # Send to Groq Whisper API (whisper-large-v3-turbo)
    transcription = client.audio.transcriptions.create(
        file=file_tuple,
        model="whisper-large-v3-turbo",
        prompt=TECHNICAL_PROMPT,
        response_format="verbose_json",
        timestamp_granularities=["segment"],
        language="en",
        temperature=0.0
    )

    # Format segment timestamps to match existing frontend expectations
    text_segments = []
    if hasattr(transcription, "segments") and transcription.segments:
        for seg in transcription.segments:
            if isinstance(seg, dict):
                text_segments.append({
                    "start": seg.get("start", 0),
                    "end": seg.get("end", 0),
                    "text": seg.get("text", "").strip()
                })
            else:
                text_segments.append({
                    "start": getattr(seg, "start", 0),
                    "end": getattr(seg, "end", 0),
                    "text": getattr(seg, "text", "").strip()
                })

    full_text = getattr(transcription, "text", "") or ""
    language = getattr(transcription, "language", "en") or "en"

    return {
        "text": full_text.strip(),
        "segments": text_segments,
        "language": language,
        "language_probability": 1.0
    }
