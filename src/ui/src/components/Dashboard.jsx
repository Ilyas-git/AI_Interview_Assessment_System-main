import React, { useState, useEffect } from 'react';
import VideoRecorder from './VideoRecorder';
import VideoUploader from './VideoUploader';
import AnalysisResults from './AnalysisResults';
import { analyzeVideo, checkHealth } from '../services/api';
import { Play, RotateCcw, Check, BrainCircuit, Loader2, AlertCircle, Wifi, WifiOff } from 'lucide-react';

const Dashboard = () => {
  const [videoBlob, setVideoBlob] = useState(null);
  const [videoUrl, setVideoUrl] = useState(null);
  const [mode, setMode] = useState('record'); // 'record' or 'upload'
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [error, setError] = useState(null);
  const [backendStatus, setBackendStatus] = useState('checking'); // 'checking', 'online', 'offline'

  // Check backend health on mount
  useEffect(() => {
    const checkBackendHealth = async () => {
      const isHealthy = await checkHealth();
      setBackendStatus(isHealthy ? 'online' : 'offline');
    };
    checkBackendHealth();
    // Check every 30 seconds
    const interval = setInterval(checkBackendHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const handleVideoSet = (blobOrFile) => {
    setVideoBlob(blobOrFile);
    const url = URL.createObjectURL(blobOrFile);
    setVideoUrl(url);
    setError(null);
    setAnalysisResult(null);
  };

  const handleReset = () => {
    if (videoUrl) {
      URL.revokeObjectURL(videoUrl);
    }
    setVideoBlob(null);
    setVideoUrl(null);
    setAnalysisResult(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!videoBlob) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const result = await analyzeVideo(videoBlob);
      if (result.success) {
        setAnalysisResult(result);
      } else {
        setError('Analysis failed. Please try again.');
      }
    } catch (err) {
      console.error('Analysis error:', err);
      setError(err.message || 'Failed to analyze video. Make sure the backend server is running.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Show analysis results if available
  if (analysisResult) {
    return (
      <div className="min-h-screen p-8 flex flex-col items-center">
        <header className="w-full max-w-4xl flex justify-between items-center mb-12 glass-panel p-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-primary-color to-secondary-color rounded-lg flex items-center justify-center shadow-lg shadow-primary-color/30">
              <BrainCircuit className="text-white w-6 h-6" />
            </div>
            <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
              AI Interview Assessor
            </h1>
          </div>
          <BackendStatusBadge status={backendStatus} />
        </header>

        <AnalysisResults 
          results={analysisResult.analysis}
          transcription={analysisResult.transcription}
          onReset={handleReset}
        />
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8 flex flex-col items-center">
      <header className="w-full max-w-4xl flex justify-between items-center mb-12 glass-panel p-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-primary-color to-secondary-color rounded-lg flex items-center justify-center shadow-lg shadow-primary-color/30">
            <BrainCircuit className="text-white w-6 h-6" />
          </div>
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            AI Interview Assessor
          </h1>
        </div>
        <BackendStatusBadge status={backendStatus} />
      </header>

      <main className="w-full max-w-4xl flex flex-col items-center gap-8 animate-fade-in-up">
        {!videoUrl ? (
          <>
            <div className="flex bg-black/20 p-1 rounded-lg backdrop-blur-sm border border-white/5 mb-8">
              <button 
                onClick={() => setMode('record')}
                className={`px-6 py-2 rounded-md transition-all ${mode === 'record' ? 'bg-white/10 text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
              >
                Record Video
              </button>
              <button 
                onClick={() => setMode('upload')}
                className={`px-6 py-2 rounded-md transition-all ${mode === 'upload' ? 'bg-white/10 text-white shadow-sm' : 'text-gray-400 hover:text-white'}`}
              >
                Upload File
              </button>
            </div>

            <div className="w-full transition-all duration-300">
              {mode === 'record' ? (
                <VideoRecorder onRecordingComplete={handleVideoSet} />
              ) : (
                <VideoUploader onUpload={handleVideoSet} />
              )}
            </div>
          </>
        ) : (
          <div className="glass-panel p-8 w-full flex flex-col items-center animate-scale-in">
            <h2 className="text-xl font-semibold mb-6 flex items-center gap-2">
              <Check className="text-green-400 w-5 h-5" /> Video Ready
            </h2>
            
            <div className="w-full max-w-2xl aspect-video bg-black rounded-lg overflow-hidden shadow-2xl mb-8 border border-glass-border">
              <video src={videoUrl} controls className="w-full h-full" />
            </div>

            {error && (
              <div className="w-full max-w-2xl mb-6 p-4 bg-red-500/10 border border-red-500/30 rounded-lg flex items-center gap-3 text-red-400">
                <AlertCircle className="w-5 h-5 flex-shrink-0" />
                <p>{error}</p>
              </div>
            )}

            {backendStatus === 'offline' && (
              <div className="w-full max-w-2xl mb-6 p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg flex items-center gap-3 text-orange-400">
                <WifiOff className="w-5 h-5 flex-shrink-0" />
                <p>Backend server is offline. Please start it with: <code className="bg-black/30 px-2 py-1 rounded">python main.py</code> in the backend folder.</p>
              </div>
            )}

            <div className="flex gap-4">
              <button 
                onClick={handleReset}
                className="btn-secondary flex items-center gap-2"
                disabled={isAnalyzing}
              >
                <RotateCcw className="w-4 h-4" /> Retake
              </button>
              <button 
                onClick={handleAnalyze}
                disabled={isAnalyzing || backendStatus === 'offline'}
                className="btn-primary flex items-center gap-2 px-8 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isAnalyzing ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" /> Analyzing...
                  </>
                ) : (
                  <>
                    <BrainCircuit className="w-4 h-4" /> Analyze Response
                  </>
                )}
              </button>
            </div>

            {isAnalyzing && (
              <div className="mt-6 text-center text-gray-400">
                <p>Processing your video... This may take a moment.</p>
                <p className="text-sm mt-1">Extracting audio → Transcribing → Analyzing</p>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

const BackendStatusBadge = ({ status }) => {
  if (status === 'checking') {
    return (
      <div className="flex items-center gap-2 text-gray-400 text-sm">
        <Loader2 className="w-4 h-4 animate-spin" />
        <span>Checking backend...</span>
      </div>
    );
  }
  
  if (status === 'online') {
    return (
      <div className="flex items-center gap-2 text-green-400 text-sm">
        <Wifi className="w-4 h-4" />
        <span>Backend Online</span>
      </div>
    );
  }
  
  return (
    <div className="flex items-center gap-2 text-orange-400 text-sm">
      <WifiOff className="w-4 h-4" />
      <span>Backend Offline</span>
    </div>
  );
};

export default Dashboard;
