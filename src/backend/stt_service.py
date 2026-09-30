"""
Speech-to-Text Service using Faster Whisper
Extracted from notebook: Speech_To_Text.ipynb
"""
import os
import tempfile
import numpy as np
import av
import soundfile as sf
import librosa
import noisereduce as nr
from scipy.signal import butter, sosfilt
from faster_whisper import WhisperModel
import torch

# Initialize model globally (loaded once)
_model = None

def get_whisper_model():
    """Get or initialize the Whisper model"""
    global _model
    if _model is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute = "float16" if device == "cuda" else "int8"
        print(f"Loading Whisper model on {device}...")
        _model = WhisperModel("small.en", device=device, compute_type=compute)
        print("Whisper model loaded successfully!")
    return _model


def highpass_filter(audio: np.ndarray, sr: int, cutoff: int = 80) -> np.ndarray:
    """Apply highpass filter to remove low frequency rumble"""
    sos = butter(4, cutoff, btype='highpass', fs=sr, output='sos')
    return sosfilt(sos, audio)


def extract_audio_from_video(video_path: str) -> tuple[np.ndarray, int]:
    """
    Extract audio from video file using PyAV
    Returns: (audio_array, sample_rate)
    """
    container = av.open(video_path)
    try:
        audio_stream = next((s for s in container.streams if s.type == 'audio'), None)
        if audio_stream is None:
            raise ValueError("No audio stream found in video file")
        
        samples = []
        sample_rate = audio_stream.rate
        
        for frame in container.decode(audio_stream):
            pcm = frame.to_ndarray().astype(np.float32)
            # Convert to mono
            if pcm.ndim > 1:
                pcm = pcm.mean(axis=0)
            samples.append(pcm)
    finally:
        container.close()
    
    if not samples:
        raise ValueError("No audio found in video file")
    
    audio = np.concatenate(samples)
    return audio, sample_rate


def preprocess_audio(audio: np.ndarray, original_sr: int) -> np.ndarray:
    """
    Preprocess audio: resample, filter, denoise, normalize
    """
    # Convert to mono if needed
    audio = librosa.to_mono(audio)
    
    # Resample to 16kHz
    audio = librosa.resample(audio, orig_sr=original_sr, target_sr=16000)
    
    # Apply highpass filter
    audio = highpass_filter(audio, 16000, cutoff=80)
    
    # Check SNR and apply noise reduction if needed
    rms = np.sqrt(np.mean(audio**2))
    if rms < 0.03:
        audio = nr.reduce_noise(y=audio, sr=16000, prop_decrease=0.04)
    
    # Normalize RMS to around -18 dB
    rms = np.sqrt(np.mean(audio**2))
    audio = audio / (rms + 1e-8) * 0.1
    
    return audio


def transcribe_audio(audio: np.ndarray) -> dict:
    """
    Transcribe preprocessed audio using Whisper
    Returns dict with text and segments
    """
    model = get_whisper_model()
    
    # Pass 16kHz float32 audio array directly to avoid PyAV metadata_errors incompatibility
    audio_data = audio.astype(np.float32)
    
    segments, info = model.transcribe(
        audio_data,
        language="en",
        beam_size=1,
        temperature=0.0,
        condition_on_previous_text=False,
        initial_prompt=(
            "This is a technical machine-learning interview. "
            "The conversation includes terms like TensorFlow, Keras, CNN, "
            "Conv2D, MaxPooling2D, MobileNet, EfficientNet, VGG16, "
            "training pipeline, data preprocessing, SMOTE, epochs, "
            "validation accuracy, loss function, learning rate, model evaluation."
        )
    )
    
    # Collect segments
    text_segments = []
    full_text = ""
    for segment in segments:
        text_segments.append({
            "start": segment.start,
            "end": segment.end,
            "text": segment.text.strip()
        })
        full_text += segment.text + " "
    
    return {
        "text": full_text.strip(),
        "segments": text_segments,
        "language": info.language,
        "language_probability": info.language_probability
    }


def transcribe_video(video_path: str) -> dict:
    """
    Full pipeline: video → audio → preprocessing → transcription
    """
    # Extract audio
    audio, sr = extract_audio_from_video(video_path)
    
    # Preprocess
    audio = preprocess_audio(audio, sr)
    
    # Transcribe
    result = transcribe_audio(audio)
    
    return result
