import React, { useState, useRef, useEffect } from 'react';
import { Video, Mic, Square, Play, RotateCcw, Save } from 'lucide-react';

const VideoRecorder = ({ onRecordingComplete }) => {
  const videoRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedChunks, setRecordedChunks] = useState([]);
  const [stream, setStream] = useState(null);
  const [error, setError] = useState(null);
  const [timer, setTimer] = useState(0);

  useEffect(() => {
    let interval;
    if (isRecording) {
      interval = setInterval(() => {
        setTimer((prev) => prev + 1);
      }, 1000);
    } else {
      setTimer(0);
    }
    return () => clearInterval(interval);
  }, [isRecording]);

  const startCamera = async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      setStream(mediaStream);
      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
      }
      setError(null);
    } catch (err) {
      console.error("Error accessing camera:", err);
      setError("Could not access camera/microphone. Please check permissions.");
    }
  };

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
  };

  const startRecording = () => {
    if (!stream) return;
    setRecordedChunks([]);
    const mediaRecorder = new MediaRecorder(stream);
    mediaRecorderRef.current = mediaRecorder;

    mediaRecorder.ondataavailable = (event) => {
      if (event.data.size > 0) {
        setRecordedChunks((prev) => [...prev, event.data]);
      }
    };

    mediaRecorder.onstop = () => {
      // Handle stop if needed immediately
    };

    mediaRecorder.start();
    setIsRecording(true);
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  useEffect(() => {
    if (!isRecording && recordedChunks.length > 0) {
      const blob = new Blob(recordedChunks, { type: 'video/webm' });
      onRecordingComplete(blob);
    }
  }, [recordedChunks, isRecording, onRecordingComplete]);

  useEffect(() => {
    startCamera();
    return () => stopCamera();
  }, []);

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="glass-panel p-6 flex flex-col items-center justify-center w-full max-w-2xl mx-auto">
      <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
        <Video className="w-5 h-5 text-primary-color" /> Record Your Answer
      </h2>
      
      <div className="relative w-full aspect-video bg-black rounded-lg overflow-hidden mb-4 border border-glass-border shadow-lg">
        {error ? (
          <div className="absolute inset-0 flex items-center justify-center text-red-400 p-4 text-center">
            {error}
          </div>
        ) : (
          <video 
            ref={videoRef} 
            autoPlay 
            muted 
            className="w-full h-full object-cover transform scale-x-[-1]" 
          />
        )}
        
        {isRecording && (
          <div className="absolute top-4 right-4 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-mono animate-pulse flex items-center gap-2">
            <div className="w-2 h-2 bg-white rounded-full"></div>
            REC {formatTime(timer)}
          </div>
        )}
      </div>

      <div className="flex gap-4">
        {!isRecording ? (
          <button 
            onClick={startRecording} 
            disabled={!stream}
            className="btn-primary flex items-center gap-2"
          >
            <Mic className="w-4 h-4" /> Start Recording
          </button>
        ) : (
          <button 
            onClick={stopRecording} 
            className="bg-red-500 hover:bg-red-600 text-white px-6 py-3 rounded-lg font-semibold flex items-center gap-2 transition-all"
          >
            <Square className="w-4 h-4 fill-current" /> Stop Recording
          </button>
        )}
      </div>
    </div>
  );
};

export default VideoRecorder;
