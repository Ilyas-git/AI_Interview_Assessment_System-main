/**
 * API Service for communicating with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL ?? '';

/**
 * Analyze a video file - full pipeline
 * @param {File|Blob} videoFile - The video file to analyze
 * @returns {Promise<Object>} Analysis results
 */
export async function analyzeVideo(videoFile) {
  const formData = new FormData();
  formData.append('video', videoFile, 'recording.webm');

  const response = await fetch(`${API_BASE_URL}/api/analyze`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to analyze video');
  }

  return response.json();
}

/**
 * Transcribe a video file only (no NLP analysis)
 * @param {File|Blob} videoFile - The video file to transcribe
 * @returns {Promise<Object>} Transcription results
 */
export async function transcribeVideo(videoFile) {
  const formData = new FormData();
  formData.append('video', videoFile, 'recording.webm');

  const response = await fetch(`${API_BASE_URL}/api/transcribe`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to transcribe video');
  }

  return response.json();
}

/**
 * Check if the backend API is healthy
 * @returns {Promise<boolean>}
 */
export async function checkHealth() {
  try {
    const response = await fetch(`${API_BASE_URL}/api/health`);
    return response.ok;
  } catch {
    return false;
  }
}
