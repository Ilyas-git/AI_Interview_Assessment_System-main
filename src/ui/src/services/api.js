/**
 * API Service for communicating with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';

/**
 * Convert audio buffer to a standard 16-bit PCM WAV Blob
 */
function encodeWAV(samples, sampleRate = 16000) {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);

  function writeString(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
      view.setUint8(offset + i, string.charCodeAt(i));
    }
  }

  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(view, 8, 'WAVE');
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, 1, true); // Mono channel
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true); // Byte rate
  view.setUint16(32, 2, true); // Block align
  view.setUint16(34, 16, true); // Bits per sample
  writeString(view, 36, 'data');
  view.setUint32(40, samples.length * 2, true);

  let offset = 44;
  for (let i = 0; i < samples.length; i++, offset += 2) {
    const s = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7fff, true);
  }
  return buffer;
}

/**
 * Extract audio from a video/audio file and resample to 16kHz mono WAV.
 * This compresses 10-30MB video files down to ~500KB-1.5MB audio files,
 * completely bypassing Vercel's 4.5MB Serverless payload limit.
 */
async function prepareAudioPayload(fileOrBlob) {
  try {
    const arrayBuffer = await fileOrBlob.arrayBuffer();
    const AudioContextClass = window.AudioContext || window.webkitAudioContext;
    if (!AudioContextClass) return { file: fileOrBlob, filename: 'recording.webm' };

    const audioCtx = new AudioContextClass();
    const decoded = await audioCtx.decodeAudioData(arrayBuffer);

    // Resample to 16000 Hz mono using OfflineAudioContext
    const targetSampleRate = 16000;
    const targetLength = Math.ceil(decoded.duration * targetSampleRate);
    const offlineCtx = new (window.OfflineAudioContext || window.webkitOfflineAudioContext)(
      1,
      targetLength,
      targetSampleRate
    );

    const source = offlineCtx.createBufferSource();
    source.buffer = decoded;
    source.connect(offlineCtx.destination);
    source.start(0);

    const resampled = await offlineCtx.startRendering();
    const pcmData = resampled.getChannelData(0);
    const wavBuffer = encodeWAV(pcmData, targetSampleRate);
    const wavBlob = new Blob([wavBuffer], { type: 'audio/wav' });

    return { file: wavBlob, filename: 'recording.wav' };
  } catch (err) {
    console.warn('Audio extraction in browser skipped or failed, sending original file:', err);
    return { file: fileOrBlob, filename: 'recording.webm' };
  }
}

/**
 * Parse response safely without crashing on non-JSON payloads (like Vercel 413 or 504 errors)
 */
async function parseResponse(response) {
  if (!response.ok) {
    let errorDetail = `Server returned status ${response.status}`;
    try {
      const errorJson = await response.json();
      errorDetail = errorJson.detail || errorJson.message || errorDetail;
    } catch {
      const text = await response.text();
      if (text.includes('Request Entity Too Large') || response.status === 413) {
        errorDetail = 'File video terlalu besar untuk serverless (maks 4.5 MB). Coba rekam video yang lebih singkat.';
      } else {
        errorDetail = text.slice(0, 200) || errorDetail;
      }
    }
    throw new Error(errorDetail);
  }
  return response.json();
}

/**
 * Analyze a video file - full pipeline
 * @param {File|Blob} videoFile - The video file to analyze
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeVideo(videoFile) {
  const { file, filename } = await prepareAudioPayload(videoFile);
  const formData = new FormData();
  formData.append('video', file, filename);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/analyze`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok && response.status === 404) {
      response = await fetch(`${API_BASE_URL}/analyze`, {
        method: 'POST',
        body: formData,
      });
    }
  } catch {
    response = await fetch(`${API_BASE_URL}/analyze`, {
      method: 'POST',
      body: formData,
    });
  }

  return parseResponse(response);
}

/**
 * Transcribe a video file only (no NLP analysis)
 * @param {File|Blob} videoFile - The video file to transcribe
 * @returns {Promise<Object>} Transcription results
 */
export async function transcribeVideo(videoFile) {
  const { file, filename } = await prepareAudioPayload(videoFile);
  const formData = new FormData();
  formData.append('video', file, filename);

  let response;
  try {
    response = await fetch(`${API_BASE_URL}/api/transcribe`, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok && response.status === 404) {
      response = await fetch(`${API_BASE_URL}/transcribe`, {
        method: 'POST',
        body: formData,
      });
    }
  } catch {
    response = await fetch(`${API_BASE_URL}/transcribe`, {
      method: 'POST',
      body: formData,
    });
  }

  return parseResponse(response);
}

/**
 * Check if the backend API is healthy
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    let response = await fetch(`${API_BASE_URL}/api/health`);
    if (!response.ok) {
      response = await fetch(`${API_BASE_URL}/health`);
    }
    return response.ok;
  } catch {
    return false;
  }
}
