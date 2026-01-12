'use client';

import { useState, useRef } from 'react';
import { useRouter } from 'next/navigation';

export default function UploadPage() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scanConsent, setScanConsent] = useState(false);
  const [llmConsent, setLlmConsent] = useState(false);
  const fileInputRef = useRef(null);
  const router = useRouter();

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
      const formData = new FormData();
      formData.append('file', file);
      formData.append('consent_scan', scanConsent ? 'true' : 'false');
      formData.append('consent_send_llm', llmConsent ? 'true' : 'false');

      const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://capstone_backend:8000';
      const response = await fetch(`${backendUrl}/api/upload-folder/`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      const data = await response.json();
      
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
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-2xl mx-auto">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">Upload Portfolio</h1>
          <p className="text-gray-600 mb-8">Upload your project files as a ZIP archive</p>

          {/* Upload Area */}
          <div
            onDragOver={handleDragOver}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              file ? 'border-green-500 bg-green-50' : 'border-gray-300 hover:border-indigo-500'
            }`}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip"
              onChange={handleFileChange}
              className="hidden"
            />

            <div className="text-gray-600">
              {file ? (
                <>
                  <p className="text-lg font-semibold text-green-600">{file.name}</p>
                  <p className="text-sm text-gray-500">
                    {(file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </>
              ) : (
                <>
                  <p className="text-lg font-semibold mb-2">Drag and drop your ZIP file</p>
                  <p className="text-sm">or click to browse</p>
                </>
              )}
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-600">
              {error}
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
                className="mt-1 w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <label htmlFor="scan-consent" className="text-sm text-gray-700">
                <span className="font-semibold">Scan Consent:</span> I consent to scan my portfolio for code analysis, file structure, and contribution metrics.
              </label>
            </div>

            <div className="flex items-start space-x-3">
              <input
                id="llm-consent"
                type="checkbox"
                checked={llmConsent}
                onChange={(e) => setLlmConsent(e.target.checked)}
                className="mt-1 w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <label htmlFor="llm-consent" className="text-sm text-gray-700">
                <span className="font-semibold">LLM Processing:</span> I consent to use AI/LLM models for advanced analysis and summary generation of my portfolio.
              </label>
            </div>
          </div>

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!file || loading || !scanConsent}
            className={`w-full mt-8 py-3 px-4 rounded-lg font-semibold transition-colors ${
              !file || loading || !scanConsent
                ? 'bg-gray-300 text-gray-600 cursor-not-allowed'
                : 'bg-indigo-600 text-white hover:bg-indigo-700'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <span className="animate-spin mr-2">⏳</span>
                Uploading...
              </span>
            ) : (
              'Upload Portfolio'
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
