'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { performIncrementalUpload, fetchUserProjects, fetchUserPortfolios, validateIncrementalFile } from '@/utils/incrementalUpload';
import Header from '@/components/Header';

export default function IncrementalUploadPage() {
  const router = useRouter();
  const { user, token, isAuthenticated } = useAuth();
  
  const [selectedFile, setSelectedFile] = useState(null);
  const [targetType, setTargetType] = useState('project'); // 'project' or 'portfolio'
  const [targetId, setTargetId] = useState('');
  const [projects, setProjects] = useState([]);
  const [portfolios, setPortfolios] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState('');
  const [error, setError] = useState('');
  const [mergeStrategy, setMergeStrategy] = useState('merge_similar'); // 'merge_similar', 'add_to_portfolio', 'create_new'

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    
    loadUserData();
  }, [isAuthenticated, router]);

  const loadUserData = async () => {
    try {
      const [userProjects, userPortfolios] = await Promise.all([
        fetchUserProjects(token),
        fetchUserPortfolios(token)
      ]);
      
      setProjects(userProjects);
      setPortfolios(userPortfolios);
    } catch (error) {
      console.error('Failed to load user data:', error);
      setError('Failed to load your existing projects and portfolios');
    }
  };

  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (!file) {
      setSelectedFile(null);
      setError('');
      return;
    }

    // Validate the file
    const validationErrors = validateIncrementalFile(file);
    if (validationErrors.length > 0) {
      setError(validationErrors.join(', '));
      setSelectedFile(null);
    } else {
      setSelectedFile(file);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile || !targetId) {
      setError('Please select a file and target');
      return;
    }

    setUploading(true);
    setProgress(0);
    setStatus('Starting incremental upload...');
    setError('');

    try {
      const result = await performIncrementalUpload(
        selectedFile,
        targetType,
        parseInt(targetId),
        mergeStrategy,
        token,
        (progress, status) => {
          setProgress(progress);
          setStatus(status);
        }
      );

      setStatus('Upload completed successfully!');
      setTimeout(() => {
        if (targetType === 'project' && result.projects && result.projects.length > 0) {
          // Get the newly created project (should be the last one in the array)
          const newProject = result.projects[result.projects.length - 1];
          router.push(`/projects/${newProject.id}`);
        } else if (targetType === 'portfolio' && result.target_portfolio_id) {
          router.push('/dashboard');
        } else {
          router.push('/dashboard');
        }
      }, 2000);

    } catch (error) {
      console.error('Upload failed:', error);
      setError(error.message || 'Upload failed');
      setStatus('');
    } finally {
      setUploading(false);
    }
  };

  const getTargetOptions = () => {
    if (targetType === 'project') {
      return projects.map(project => ({
        id: project.id,
        name: project.name,
        description: `${project.skills?.length || 0} skills identified`
      }));
    } else {
      return portfolios.map(portfolio => ({
        id: portfolio.id,
        name: portfolio.name,
        description: `${portfolio.projects?.length || 0} projects`
      }));
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-950 via-purple-950 to-gray-900 flex items-center justify-center">
        <div className="text-white text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white mx-auto mb-4"></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <>
      <Header />
      <div className="min-h-screen flex flex-col items-center justify-center p-8">
        <div className="max-w-4xl mx-auto w-full">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-white mb-4">
              Incremental Portfolio Update
            </h1>
            <p className="text-lg text-white/80 max-w-2xl mx-auto">
              Add new projects or enhance existing ones by uploading additional files
            </p>
          </div>

          <div className="bg-[var(--card-bg)] rounded-xl p-8 border border-white/10 shadow-xl">
          {error && (
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 mb-6">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* File Selection */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Select Files to Upload</h2>
            <div className="border-2 border-dashed border-white/20 rounded-lg p-6 text-center">
              <input
                type="file"
                accept=".zip"
                onChange={handleFileChange}
                className="hidden"
                id="file-upload"
                disabled={uploading}
              />
              <label
                htmlFor="file-upload"
                className="cursor-pointer flex flex-col items-center"
              >
                <svg className="w-12 h-12 text-white/60 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
                <span className="text-white/80 font-medium">
                  {selectedFile ? selectedFile.name : 'Click to select ZIP file'}
                </span>
                <span className="text-white/60 text-sm mt-2">
                  Upload additional project files to enhance your portfolio
                </span>
              </label>
            </div>
          </div>

          {/* Target Selection */}
          <div className="mb-8">
            <h2 className="text-xl font-semibold text-white mb-4">Where should we add these files?</h2>
            
            {/* Target Type */}
            <div className="mb-4">
              <label className="block text-white/80 mb-2">Target Type:</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  onClick={() => setTargetType('project')}
                  className={`p-4 rounded-lg border transition-colors ${
                    targetType === 'project'
                      ? 'border-blue-500 bg-blue-500/10 text-blue-300'
                      : 'border-white/20 bg-white/5 text-white/80 hover:bg-white/10'
                  }`}
                  disabled={uploading}
                >
                  <h3 className="font-semibold mb-1">Existing Project</h3>
                  <p className="text-sm opacity-80">Add to a specific project</p>
                </button>
                <button
                  onClick={() => setTargetType('portfolio')}
                  className={`p-4 rounded-lg border transition-colors ${
                    targetType === 'portfolio'
                      ? 'border-blue-500 bg-blue-500/10 text-blue-300'
                      : 'border-white/20 bg-white/5 text-white/80 hover:bg-white/10'
                  }`}
                  disabled={uploading}
                >
                  <h3 className="font-semibold mb-1">Portfolio</h3>
                  <p className="text-sm opacity-80">Add as new project to portfolio</p>
                </button>
              </div>
            </div>

            {/* Target Selection */}
            <div className="mb-4">
              <label className="block text-white/80 mb-2">
                Select {targetType === 'project' ? 'Project' : 'Portfolio'}:
              </label>
              <select
                value={targetId}
                onChange={(e) => setTargetId(e.target.value)}
                className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white focus:border-blue-500 focus:outline-none"
                disabled={uploading}
              >
                <option value="">Select a {targetType}...</option>
                {getTargetOptions().map(option => (
                  <option key={option.id} value={option.id} className="bg-gray-800">
                    {option.name} - {option.description}
                  </option>
                ))}
              </select>
            </div>

            {/* Merge Strategy */}
            <div>
              <label className="block text-white/80 mb-2">How should we handle similar files?</label>
              <select
                value={mergeStrategy}
                onChange={(e) => setMergeStrategy(e.target.value)}
                className="w-full p-3 rounded-lg bg-white/5 border border-white/20 text-white focus:border-blue-500 focus:outline-none"
                disabled={uploading}
              >
                <option value="merge_similar" className="bg-gray-800">
                  Merge with similar files (recommended)
                </option>
                <option value="add_to_portfolio" className="bg-gray-800">
                  Add as separate project to portfolio
                </option>
                <option value="create_new" className="bg-gray-800">
                  Create completely new project
                </option>
              </select>
              <p className="text-white/60 text-sm mt-2">
                {mergeStrategy === 'merge_similar' && 'Files will be analyzed and merged with similar existing projects'}
                {mergeStrategy === 'add_to_portfolio' && 'Files will be added as a new project in the selected portfolio'}
                {mergeStrategy === 'create_new' && 'Files will create a brand new project with a new version number'}
              </p>
            </div>
          </div>

          {/* Upload Progress */}
          {uploading && (
            <div className="mb-8">
              <h2 className="text-xl font-semibold text-white mb-4">Upload Progress</h2>
              <div className="bg-white/5 rounded-lg p-4">
                <div className="flex justify-between text-white/80 text-sm mb-2">
                  <span>{status}</span>
                  <span>{progress}%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-3">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-green-500 h-3 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4">
            <button
              onClick={() => router.back()}
              className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-lg transition-colors"
              disabled={uploading}
            >
              Cancel
            </button>
            <button
              onClick={handleUpload}
              disabled={!selectedFile || !targetId || uploading}
              className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {uploading ? 'Uploading...' : 'Start Incremental Update'}
            </button>
          </div>
        </div>
      </div>
    </div>
    </>
  );
}