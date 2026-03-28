'use client';

import { useState, useRef } from 'react';
import LoadingAnimation from '@/components/LoadingAnimation';
import Toast from '@/components/Toast';
import { uploadFolder } from '@/utils/api';
import { addNewProjects, clearNewProjects } from '@/utils/newProjectsSession';
import config from '@/config';

export default function ProjectUploadStep({ token, onUploadComplete = () => {} }) {
  const fileInputRef = useRef(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showConsent, setShowConsent] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    const files = e.dataTransfer.files;
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files.length > 0) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleStartScan = () => {
    if (!selectedFile) {
      setMessage({ type: 'error', text: 'Please select a file first' });
      return;
    }
    setShowConsent(true);
  };

  const handleConfirmUpload = async (scanConsent, llmConsent) => {
    setShowConsent(false);
    setUploading(true);
    setMessage({ type: '', text: '' });

    try {
      clearNewProjects();
      
      // Fetch projects BEFORE upload to compare
      let projectsBeforeUpload = [];
      try {
        const beforeResponse = await fetch(`${config.API_URL}/api/projects/`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (beforeResponse.ok) {
          const beforeData = await beforeResponse.json();
          projectsBeforeUpload = (beforeData.projects || []).map(p => p.id);
        }
      } catch (err) {
        console.error('Error fetching projects before upload:', err);
      }
      
      // Perform the upload
      const response = await uploadFolder(selectedFile, scanConsent, llmConsent, token, null);
      console.log('Upload response:', response);
      
      // Wait a moment for backend to process
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Fetch projects AFTER upload to identify new ones
      let newProjectIds = [];
      try {
        const afterResponse = await fetch(`${config.API_URL}/api/projects/`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (afterResponse.ok) {
          const afterData = await afterResponse.json();
          const projectsAfterUpload = (afterData.projects || []).map(p => p.id);
          newProjectIds = projectsAfterUpload.filter(id => !projectsBeforeUpload.includes(id));
          
          if (newProjectIds.length > 0) {
            addNewProjects(newProjectIds);
          }
        }
      } catch (err) {
        console.error('Error fetching projects after upload:', err);
      }
      
      setMessage({ type: 'success', text: '✓ Your first project has been uploaded!' });
      setSelectedFile(null);
      
      // Call the callback after a short delay
      setTimeout(() => {
        onUploadComplete();
      }, 1500);
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to upload portfolio' });
      setUploading(false);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div>
      {/* Loading State Overlay */}
      {uploading && (
        <div className="fixed inset-0 flex flex-col items-center justify-center z-50 bg-black/60 backdrop-blur-sm">
          <div className="bg-[#18181b] border border-white/20 rounded-lg p-12 max-w-md w-full mx-4 text-center shadow-2xl">
            <h2 className="text-2xl font-semibold text-white mb-2">Analyzing Your Portfolio</h2>
            <p className="text-white/60 mb-8 text-sm">Extracting skills, frameworks, and technologies...</p>
            
            <div className="mb-8">
              <LoadingAnimation />
            </div>
            
            <p className="text-white/40 text-xs">This may take a few moments</p>
          </div>
        </div>
      )}

      <div>
        <h1 className="text-2xl font-semibold text-white mb-2">Upload your first project</h1>
        <p className="mb-8" style={{ color: '#a1a1aa' }}>
          Get started by uploading a project to extract your skills and experience.
        </p>

        <input
          ref={fileInputRef}
          type="file"
          onChange={handleFileSelect}
          accept=".zip,.rar,.7z,.tar,.gz"
          className="hidden"
        />

        {!selectedFile ? (
          // Upload Zone
          <div
            onClick={handleUploadClick}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            className={`w-full flex flex-col items-center justify-center p-8 rounded-lg border-2 border-dashed cursor-pointer transition-all ${
              isDragging
                ? 'border-blue-400 bg-blue-500/10'
                : 'border-white/30 bg-white/5 hover:bg-white/10'
            }`}
          >
            <img
              src="/upload.svg"
              alt="Upload"
              className="w-12 h-12 mb-4"
              style={{ filter: 'brightness(0) invert(1)' }}
            />
            
            <h3 className="text-lg font-semibold text-white mb-2 text-center">
              Drag and drop your project
            </h3>
            
            <p className="text-white/60 text-center mb-4 text-sm">
              or click to browse your computer
            </p>
            
            <button
              type="button"
              onClick={handleUploadClick}
              className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors text-sm"
              disabled={uploading}
            >
              Select File
            </button>
            
            <p className="text-white/40 text-xs text-center mt-4">
              ZIP, RAR, 7Z, TAR, GZ
            </p>
          </div>
        ) : (
          // File Selected State
          <div className="w-full flex flex-col items-center justify-center p-6 rounded-lg bg-white/5 border border-white/20">
            <div className="text-4xl mb-4">✓</div>
            
            <h3 className="text-lg font-semibold text-white mb-3 text-center">
              Ready to Analyze
            </h3>
            
            <div className="w-full bg-white/5 border border-white/10 rounded-lg p-3 mb-4">
              <p className="text-white/60 text-xs uppercase tracking-wide mb-1">Selected File</p>
              <p className="text-white font-medium break-all text-sm">{selectedFile.name}</p>
              <p className="text-white/40 text-xs mt-1">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            
            <div className="flex gap-2 w-full">
              <button
                onClick={clearSelection}
                className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium rounded-lg transition-colors text-sm"
                disabled={uploading}
              >
                Change File
              </button>
              
              <button
                onClick={handleStartScan}
                disabled={uploading}
                className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed text-sm"
              >
                {uploading ? 'Scanning...' : 'Start Scan'}
              </button>
            </div>
          </div>
        )}

        {/* Consent Modal */}
        {showConsent && (
          <div className="fixed inset-0 flex items-center justify-center z-50 p-4">
            {/* Backdrop */}
            <div
              className="absolute inset-0 bg-black/50"
              onClick={() => setShowConsent(false)}
            />

            {/* Modal */}
            <div className="relative rounded-lg p-8 max-w-md w-full bg-[#18181b] border border-white/20 shadow-xl">
              <h3 className="text-xl font-semibold text-white mb-4">Analysis Preferences</h3>

              <p className="text-white/70 mb-6 text-sm">
                Please confirm how you'd like us to analyze your portfolio:
              </p>

              <div className="space-y-4 mb-6">
                <label className="flex items-start gap-3 cursor-pointer p-3 rounded-lg hover:bg-white/5 transition-colors">
                  <input
                    type="checkbox"
                    defaultChecked
                    className="mt-1 w-4 h-4 rounded accent-blue-500"
                  />
                  <div>
                    <p className="text-white font-medium text-sm">Scan Portfolio</p>
                    <p className="text-white/60 text-xs">
                      Extract skills, frameworks, and technologies from your projects
                    </p>
                  </div>
                </label>

                <label className="flex items-start gap-3 cursor-pointer p-3 rounded-lg hover:bg-white/5 transition-colors">
                  <input
                    type="checkbox"
                    defaultChecked
                    id="llm-consent"
                    className="mt-1 w-4 h-4 rounded accent-blue-500"
                  />
                  <div>
                    <p className="text-white font-medium text-sm">Allow LLM Analysis</p>
                    <p className="text-white/60 text-xs">
                      Use AI to generate detailed project summaries and insights
                    </p>
                  </div>
                </label>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowConsent(false)}
                  className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium rounded-lg transition-colors text-sm"
                >
                  Cancel
                </button>
                <button
                  onClick={() => {
                    const scanConsent = true;
                    const llmCheckbox = document.getElementById('llm-consent');
                    const llmConsent = llmCheckbox?.checked || false;
                    handleConfirmUpload(scanConsent, llmConsent);
                  }}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors text-sm"
                >
                  Start Analysis
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Toast Notification */}
        {message.text && (
          <Toast
            message={message.text}
            type={message.type}
            onClose={() => setMessage({ type: '', text: '' })}
          />
        )}
      </div>
    </div>
  );
}
