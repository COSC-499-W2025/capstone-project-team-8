'use client';

import { useState, useRef } from 'react';

export default function ThumbnailUpload({ onUpload }) {
  const [preview, setPreview] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (file && file.type.startsWith('image/')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setPreview(e.target.result);
        onUpload?.(file, e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

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
    const file = e.dataTransfer.files?.[0];
    if (file) handleFileSelect(file);
  };

  const handleChange = (e) => {
    const file = e.target.files?.[0];
    if (file) handleFileSelect(file);
  };

  const clearThumbnail = () => {
    setPreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onUpload?.(null, null);
  };

  return (
    <div className="rounded-lg p-6" style={{ background: '#18181b', border: '1px solid #27272a' }}>
      <h3 className="text-lg font-semibold text-white mb-4">Portfolio Thumbnail</h3>

      {preview ? (
        <div className="space-y-4">
          <div className="relative">
            <img src={preview} alt="Thumbnail preview" className="w-full h-48 object-cover rounded-lg" style={{ border: '1px solid #27272a' }} />
          </div>
          <button
            onClick={clearThumbnail}
            className="w-full px-4 py-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors"
          >
            Remove Thumbnail
          </button>
        </div>
      ) : (
        <div
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
            isDragging ? 'border-blue-400 bg-blue-500/10' : 'border-white/20 hover:border-white/40'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            onChange={handleChange}
            className="hidden"
          />

          <div>
            <p className="text-4xl mb-2">🖼️</p>
            <p className="font-semibold mb-1 text-white">Upload a thumbnail</p>
            <p className="text-sm" style={{ color: '#a1a1aa' }}>Drag and drop or click to browse</p>
          </div>
        </div>
      )}
    </div>
  );
}
