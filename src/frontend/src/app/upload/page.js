'use client';

import { useEffect, useState, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { uploadFolder } from '@/utils/api';
import Header from '@/components/Header';
import Toast from '@/components/Toast';

export default function UploadPage() {
  const router = useRouter();
  const { isAuthenticated, token, loading: authLoading } = useAuth();
  const [selectedFile, setSelectedFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [showConsent, setShowConsent] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const fileInputRef = useRef(null);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
  }, [authLoading, isAuthenticated, router]);

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
      await uploadFolder(selectedFile, scanConsent, llmConsent, token);
      setMessage({ type: 'success', text: 'Portfolio uploaded and analysis started!' });
      setSelectedFile(null);
      
      // Redirect to results page after a short delay
      setTimeout(() => {
        router.push('/results');
      }, 2000);
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to upload portfolio' });
    } finally {
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
    <>
      <Header />
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
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
            className={`w-full max-w-md flex flex-col items-center justify-center p-8 rounded-lg border-2 border-dashed cursor-pointer transition-all ${
              isDragging
                ? 'border-blue-400 bg-blue-500/10'
                : 'border-white/30 bg-[var(--card-bg)] hover:bg-white/5'
            }`}
          >
            <img
              src="/upload.svg"
              alt="Upload"
              className="w-16 h-16 mb-6"
              style={{ filter: 'brightness(0) invert(1)' }}
            />
            
            <h2 className="text-2xl font-semibold text-white mb-4 text-center">
              Upload Your Portfolio
            </h2>
            
            <p className="text-white/60 text-center mb-6">
              Drag and drop your project folder (ZIP) here, or click to browse
            </p>
            
            <button
              type="button"
              onClick={handleUploadClick}
              className="inline-block"
              data-block="button"
            >
              <span className="button__flair"></span>
              <span className="button__label">Select File</span>
            </button>
            
            <p className="text-white/40 text-sm text-center mt-4">
              Supported formats: ZIP, RAR, 7Z, TAR, GZ
            </p>
          </div>
        ) : (
          // File Selected State
          <div className="w-full max-w-md flex flex-col items-center justify-center p-8 rounded-lg bg-[var(--card-bg)] border border-white/20">
            <div className="text-5xl mb-6">✓</div>
            
            <h2 className="text-2xl font-semibold text-white mb-4 text-center">
              Ready to Scan
            </h2>
            
            <div className="w-full bg-white/5 border border-white/10 rounded-lg p-4 mb-6">
              <p className="text-white/60 text-xs uppercase tracking-wide mb-1">Selected File</p>
              <p className="text-white font-medium break-all">{selectedFile.name}</p>
              <p className="text-white/40 text-sm mt-2">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            
            <p className="text-white/60 text-center mb-6 text-sm">
              Click "Start Scan" to analyze your portfolio and extract your skills
            </p>
            
            <div className="flex gap-3 w-full">
              <button
                onClick={clearSelection}
                className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg transition-colors"
                disabled={uploading}
              >
                Change File
              </button>
              
              <button
                onClick={handleStartScan}
                disabled={uploading}
                className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
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
            <div className="relative rounded-lg p-8 max-w-md w-full bg-[var(--card-bg)] border border-white/20 shadow-xl">
              <h3 className="text-xl font-semibold text-white mb-4">Analysis Preferences</h3>

              <p className="text-white/70 mb-6">
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
                    <p className="text-white font-medium">Scan Portfolio</p>
                    <p className="text-white/60 text-sm">
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
                    <p className="text-white font-medium">Allow LLM Analysis</p>
                    <p className="text-white/60 text-sm">
                      Use AI to generate detailed project summaries and insights
                    </p>
                  </div>
                </label>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowConsent(false)}
                  className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium rounded-lg transition-colors"
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
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
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
    </>
  );
}
