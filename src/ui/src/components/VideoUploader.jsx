import React, { useRef, useState } from 'react';
import { Upload, FileVideo, CheckCircle } from 'lucide-react';

const VideoUploader = ({ onUpload }) => {
  const fileInputRef = useRef(null);
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState(null);

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('video/')) {
      handleFile(files[0]);
    }
  };

  const handleFileChange = (e) => {
    const files = e.target.files;
    if (files.length > 0) {
      handleFile(files[0]);
    }
  };

  const handleFile = (file) => {
    setFileName(file.name);
    onUpload(file);
  };

  return (
    <div 
      className={`glass-panel p-8 flex flex-col items-center justify-center w-full max-w-2xl mx-auto border-2 border-dashed transition-all cursor-pointer
        ${isDragging ? 'border-primary-color bg-white/5' : 'border-glass-border'}
        ${fileName ? 'border-green-500/50' : ''}
      `}
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      onClick={() => fileInputRef.current.click()}
    >
      <input 
        type="file" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        accept="video/*" 
        className="hidden" 
      />
      
      {fileName ? (
        <div className="text-center animate-fade-in">
          <div className="w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4 text-green-400">
            <CheckCircle className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-semibold text-green-400 mb-1">Video Selected</h3>
          <p className="text-sm text-gray-400">{fileName}</p>
          <p className="text-xs text-gray-500 mt-4">Click to change file</p>
        </div>
      ) : (
        <div className="text-center">
          <div className={`w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-4 transition-colors ${isDragging ? 'bg-primary-color/20 text-primary-color' : 'bg-white/5 text-gray-400'}`}>
            <Upload className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-semibold mb-2">Upload Video</h3>
          <p className="text-sm text-gray-400 mb-4">Drag & drop or click to browse</p>
          <p className="text-xs text-gray-500">Supports MP4, WebM, MOV</p>
        </div>
      )}
    </div>
  );
};

export default VideoUploader;
