'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { uploadFolder } from '@/utils/api';
import { initializeButtons } from '@/utils/buttonAnimation';
import Header from '@/components/Header';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scanConsent, setScanConsent] = useState(false);
  const [llmConsent, setLlmConsent] = useState(false);
  const fileInputRef = useRef(null);
  const router = useRouter();
  const { isAuthenticated, token } = useAuth();

  useEffect(() => {
    initializeButtons();
  }, []);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file');
      return;
    }

    if (!scanConsent) {
      setError('Please accept scan consent to continue');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await uploadFolder(file, scanConsent, llmConsent, token || null);
      
      // Store results in sessionStorage to pass to results page
      sessionStorage.setItem('uploadResults', JSON.stringify(data));
      
      // Redirect to results page
      router.push('/results');
    } catch (err) {
      setError(err.message || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    const droppedFile = e.dataTransfer.files?.[0];
    if (droppedFile) {
      setFile(droppedFile);
      setError(null);
    }
  };

  return (
    <>
      <Header />
      <div className="min-h-screen bg-primary p-8">
        <div className="max-w-2xl mx-auto fade-in">
          <div className="glow-box rounded-lg p-8">
            <h1 className="text-4xl font-bold mb-2 text-primary">Upload Portfolio</h1>
            <p className="mb-8 text-primary">Upload your project files as a ZIP archive</p>

            {isAuthenticated && (
              <div className="mb-6 p-4 rounded-lg" style={{ 
                background: 'rgba(34, 197, 94, 0.1)',
                borderLeft: '3px solid #22c55e'
              }}>
                <p style={{ color: '#86efac' }}>
                  ✓ You are authenticated. Your uploads will be saved to your account.
                </p>
              </div>
            )}

          {/* Upload Area */}
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className="border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all button-lift"
            style={{
              borderColor: file ? 'white' : 'rgba(255, 255, 255, 0.2)',
              background: file ? 'rgba(255, 255, 255, 0.1)' : 'rgba(255, 255, 255, 0.05)',
            }}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip"
              onChange={handleFileChange}
              className="hidden"
            />

            <div className="text-primary">
              {file ? (
                <>
                  <p className="text-lg font-semibold text-primary">{file.name}</p>
                  <p className="text-sm text-primary">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </>
              ) : (
                <>
                  <p className="text-lg font-semibold mb-2" style={{ fontFamily: 'Lato, sans-serif' }}>Drag and drop your ZIP file</p>
                  <p className="text-sm text-primary">or click to browse</p>
                </>
              )}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 rounded-lg" style={{ 
              background: 'rgba(220, 38, 38, 0.1)',
              borderLeft: '3px solid #dc2626'
            }}>
              <p style={{ color: '#ff6b6b' }}>{error}</p>
            </div>
          )}

          {/* Consent Checkboxes */}
          <div className="mt-6 space-y-4">
            <div className="flex items-start space-x-3">
              <input
                id="scan-consent"
                type="checkbox"
                checked={scanConsent}
                onChange={(e) => setScanConsent(e.target.checked)}
                className="mt-1 w-4 h-4 rounded accent-cyan-400"
              />
              <label htmlFor="scan-consent" className="text-sm text-primary">
                <span className="font-semibold" style={{ fontFamily: 'Lato, sans-serif' }}>Scan Consent:</span> I consent to scan my portfolio for code analysis, file structure, and contribution metrics.
              </label>
            </div>

            <div className="flex items-start space-x-3">
              <input
                id="llm-consent"
                type="checkbox"
                checked={llmConsent}
                onChange={(e) => setLlmConsent(e.target.checked)}
                className="mt-1 w-4 h-4 rounded accent-cyan-400"
              />
              <label htmlFor="llm-consent" className="text-sm text-primary">
                <span className="font-semibold" style={{ fontFamily: 'Lato, sans-serif' }}>LLM Processing:</span> I consent to use AI/LLM models for advanced analysis and summary generation of my portfolio.
              </label>
            </div>
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!file || loading || !scanConsent}
            className="w-full mt-8 font-semibold button-lift disabled:opacity-40 disabled:cursor-not-allowed"
            data-block="button"
          >
            <span className="button__flair"></span>
            <span className="button__label">
              {loading ? (
                <span className="flex items-center justify-center">
                  <span className="animate-spin mr-2">⏳</span>
                  Uploading...
                </span>
              ) : (
                'Upload Portfolio'
              )}
            </span>
          </button>
        </div>
      </div>
    </div>
    </>
  );
}
