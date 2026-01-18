'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProjectCard from '@/components/ProjectCard';
import ThumbnailUpload from '@/components/ThumbnailUpload';
import { initializeButtons } from '@/utils/buttonAnimation';

export default function ResultsPage() {
  const [results, setResults] = useState(null);
  const [thumbnail, setThumbnail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDebug, setShowDebug] = useState(false);
  const router = useRouter();

  useEffect(() => {
    const storedResults = sessionStorage.getItem('uploadResults');
    if (storedResults) {
      try {
        setResults(JSON.parse(storedResults));
      } catch (err) {
        console.error('Failed to parse results:', err);
      }
    }
    setLoading(false);
    initializeButtons();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary">
        <div className="text-center">
          <p className="text-2xl font-semibold text-primary">Loading...</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-primary">
        <div className="text-center">
          <p className="text-2xl font-semibold text-primary mb-4">No results found</p>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-6 py-2 bg-card text-primary rounded-lg hover:opacity-80 button-lift"
            data-block="button"
          >
            <span className="button__flair"></span>
            <span className="button__label">Back to Dashboard</span>
          </button>
        </div>
      </div>
    );
  }

  const projects = results.projects || [];
  const overall = results.overall || {};
  const overallStats = {
    total_projects: overall.totals?.projects || results.total_projects || 0,
    total_files: overall.totals?.files || results.total_files || 0,
    total_code_files: overall.totals?.code_files || results.total_code_files || 0,
    total_text_files: overall.totals?.text_files || 0,
    total_image_files: overall.totals?.image_files || 0,
    primary_languages: overall.languages || results.primary_languages || [],
    frameworks: overall.frameworks || results.frameworks || [],
    resume_skills: overall.resume_skills || results.resume_skills || [],
    classification: overall.classification || 'unknown',
    confidence: overall.confidence || 0,
    collaborative: overall.collaborative || false,
    collaborative_projects: overall.collaborative_projects || 0,
    collaboration_rate: overall.collaboration_rate || 0,
  };

  return (
    <div className="min-h-screen bg-primary p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <button
            onClick={() => router.push('/dashboard')}
            className="text-primary hover:opacity-80 font-semibold mb-4"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-4xl font-bold text-primary mb-2">Portfolio Analysis</h1>
          <p className="text-primary">Review your uploaded portfolio and add a thumbnail</p>
          <button
            onClick={() => setShowDebug(!showDebug)}
            className="mt-2 text-xs px-2 py-1 bg-card text-primary rounded hover:opacity-80"
          >
            {showDebug ? 'Hide' : 'Show'} Debug Info
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Projects */}
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Projects ({projects.length})</h2>
              <div className="space-y-4">
                {projects.length > 0 ? (
                  projects.map((project, index) => (
                    <ProjectCard key={index} project={project} index={index} />
                  ))
                ) : (
                  <div className="bg-white rounded-lg p-8 text-center text-gray-600">
                    No projects found in the uploaded files.
                  </div>
                )}
              </div>
            </div>

            {/* Overall Statistics */}
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Overall Analysis</h2>

              {/* Classification */}
              {overallStats.classification && overallStats.classification !== 'unknown' && (
                <div className="mb-6 pb-6 border-b">
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-700">
                      {overallStats.classification}
                    </span>
                    <span className="text-sm text-gray-600">
                      Confidence: {(overallStats.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-indigo-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Total Projects</p>
                  <p className="text-3xl font-bold text-indigo-600">{overallStats.total_projects}</p>
                </div>
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Total Files</p>
                  <p className="text-3xl font-bold text-blue-600">{overallStats.total_files}</p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Code Files</p>
                  <p className="text-3xl font-bold text-green-600">{overallStats.total_code_files}</p>
                </div>
                <div className="bg-yellow-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Text Files</p>
                  <p className="text-3xl font-bold text-yellow-600">{overallStats.total_text_files}</p>
                </div>
                <div className="bg-pink-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Image Files</p>
                  <p className="text-3xl font-bold text-pink-600">{overallStats.total_image_files}</p>
                </div>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Collaboration Rate</p>
                  <p className="text-3xl font-bold text-purple-600">{(overallStats.collaboration_rate * 100).toFixed(0)}%</p>
                </div>
              </div>

              {/* Primary Languages */}
              {overallStats.primary_languages.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-700 mb-3">Primary Languages</h3>
                  <div className="flex flex-wrap gap-2">
                    {overallStats.primary_languages.map((lang, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-700"
                      >
                        {lang}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Frameworks */}
              {overallStats.frameworks && overallStats.frameworks.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-gray-700 mb-3">Frameworks</h3>
                  <div className="flex flex-wrap gap-2">
                    {overallStats.frameworks.map((framework, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full text-sm font-medium bg-blue-100 text-blue-700"
                      >
                        {framework}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Resume Skills */}
              {overallStats.resume_skills && overallStats.resume_skills.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-700 mb-3">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {overallStats.resume_skills.map((skill, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full text-sm bg-gray-100 text-gray-800"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1">
            <ThumbnailUpload
              onUpload={(file, preview) => {
                setThumbnail({ file, preview });
              }}
            />
          </div>
        </div>
      </div>

      {/* Debug Info */}
      {showDebug && (
        <div className="max-w-6xl mx-auto mt-8">
          <div className="bg-gray-900 text-white rounded-lg p-4 overflow-auto max-h-96">
            <pre className="text-xs font-mono">{JSON.stringify(results, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}
