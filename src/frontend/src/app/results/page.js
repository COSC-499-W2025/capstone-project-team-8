'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import ProjectCard from '@/components/ProjectCard';
import ThumbnailUpload from '@/components/ThumbnailUpload';
import { initializeButtons } from '@/utils/buttonAnimation';
import Header from '@/components/Header';
import { useAuth } from '@/context/AuthContext';
import config from '@/config';

export default function ResultsPage() {
  const [results, setResults] = useState(null);
  const [thumbnail, setThumbnail] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showDebug, setShowDebug] = useState(false);
  const [evaluations, setEvaluations] = useState([]);
  const router = useRouter();
  const { token } = useAuth();

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

  // Fetch evaluations after results are loaded
  useEffect(() => {
    if (!results || !token) return;
    const fetchEvaluations = async () => {
      try {
        const response = await fetch(`${config.API_URL}/api/evaluations/`, {
          headers: { 'Authorization': `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setEvaluations(data.evaluations || []);
        }
      } catch (err) {
        console.log('Evaluations not available:', err);
      }
    };
    fetchEvaluations();
  }, [results, token]);

  const getGrade = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  const getGradeColor = (grade) => {
    if (grade === 'A') return 'text-green-600 bg-green-50';
    if (grade === 'B') return 'text-blue-600 bg-blue-50';
    if (grade === 'C') return 'text-yellow-600 bg-yellow-50';
    if (grade === 'D') return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  const getBarColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center" style={{ background: '#09090b' }}>
          <div className="text-center">
            <p className="text-2xl font-semibold text-white">Loading...</p>
          </div>
        </div>
      </>
    );
  }

  if (!results) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center" style={{ background: '#09090b' }}>
          <div className="text-center">
            <p className="text-2xl font-semibold text-white mb-4">No results found</p>
            <button
              onClick={() => router.push('/dashboard')}
              className="px-6 py-2 rounded-lg hover:opacity-80 text-sm font-medium transition-all"
              style={{ background: '#4f7cf7', color: 'white' }}
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </>
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
    <>
      <Header />
      <div className="min-h-screen p-8" style={{ background: '#09090b' }}>
        <div className="max-w-6xl mx-auto">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">Portfolio Analysis</h1>
            <p style={{ color: '#a1a1aa' }}>Review your uploaded portfolio and add a thumbnail</p>
            <button
              onClick={() => setShowDebug(!showDebug)}
              className="mt-2 text-xs px-2 py-1 rounded hover:opacity-80"
              style={{ background: '#18181b', color: '#a1a1aa', border: '1px solid #27272a' }}
            >
              {showDebug ? 'Hide' : 'Show'} Debug Info
            </button>
          </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Projects */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-4">Projects ({projects.length})</h2>
              <div className="space-y-4">
                {projects.length > 0 ? (
                  projects.map((project, index) => (
                    <ProjectCard key={index} project={project} index={index} />
                  ))
                ) : (
                  <div className="rounded-lg p-8 text-center" style={{ background: '#18181b', color: '#a1a1aa', border: '1px solid #27272a' }}>
                    No projects found in the uploaded files.
                  </div>
                )}
              </div>
            </div>

            {/* Overall Statistics */}
            <div className="rounded-lg p-6" style={{ background: '#18181b', border: '1px solid #27272a' }}>
              <h2 className="text-2xl font-bold text-white mb-4">Overall Analysis</h2>

              {/* Classification */}
              {overallStats.classification && overallStats.classification !== 'unknown' && (
                <div className="mb-6 pb-6" style={{ borderBottom: '1px solid #27272a' }}>
                  <div className="flex items-center gap-3 mb-2">
                    <span className="px-3 py-1 rounded-full text-sm font-medium" style={{ background: 'rgba(79, 124, 247, 0.15)', color: '#7ba4f7' }}>
                      {overallStats.classification}
                    </span>
                    <span className="text-sm" style={{ color: '#a1a1aa' }}>
                      Confidence: {(overallStats.confidence * 100).toFixed(0)}%
                    </span>
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="rounded-lg p-4" style={{ background: 'rgba(79, 124, 247, 0.08)', border: '1px solid rgba(79, 124, 247, 0.15)' }}>
                  <p className="text-sm" style={{ color: '#a1a1aa' }}>Total Projects</p>
                  <p className="text-3xl font-bold" style={{ color: '#7ba4f7' }}>{overallStats.total_projects}</p>
                </div>
                <div className="rounded-lg p-4" style={{ background: 'rgba(59, 130, 246, 0.08)', border: '1px solid rgba(59, 130, 246, 0.15)' }}>
                  <p className="text-sm" style={{ color: '#a1a1aa' }}>Total Files</p>
                  <p className="text-3xl font-bold" style={{ color: '#60a5fa' }}>{overallStats.total_files}</p>
                </div>
                <div className="rounded-lg p-4" style={{ background: 'rgba(34, 197, 94, 0.08)', border: '1px solid rgba(34, 197, 94, 0.15)' }}>
                  <p className="text-sm" style={{ color: '#a1a1aa' }}>Code Files</p>
                  <p className="text-3xl font-bold" style={{ color: '#4ade80' }}>{overallStats.total_code_files}</p>
                </div>
                <div className="rounded-lg p-4" style={{ background: 'rgba(234, 179, 8, 0.08)', border: '1px solid rgba(234, 179, 8, 0.15)' }}>
                  <p className="text-sm" style={{ color: '#a1a1aa' }}>Text Files</p>
                  <p className="text-3xl font-bold" style={{ color: '#facc15' }}>{overallStats.total_text_files}</p>
                </div>
                <div className="rounded-lg p-4" style={{ background: 'rgba(236, 72, 153, 0.08)', border: '1px solid rgba(236, 72, 153, 0.15)' }}>
                  <p className="text-sm" style={{ color: '#a1a1aa' }}>Image Files</p>
                  <p className="text-3xl font-bold" style={{ color: '#f472b6' }}>{overallStats.total_image_files}</p>
                </div>
                <div className="rounded-lg p-4" style={{ background: 'rgba(168, 85, 247, 0.08)', border: '1px solid rgba(168, 85, 247, 0.15)' }}>
                  <p className="text-sm" style={{ color: '#a1a1aa' }}>Collaboration Rate</p>
                  <p className="text-3xl font-bold" style={{ color: '#c084fc' }}>{(overallStats.collaboration_rate * 100).toFixed(0)}%</p>
                </div>
              </div>

              {/* Primary Languages */}
              {overallStats.primary_languages.length > 0 && (
                <div className="mb-6">
                  <h3 className="font-semibold text-white mb-3">Primary Languages</h3>
                  <div className="flex flex-wrap gap-2">
                    {overallStats.primary_languages.map((lang, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full text-sm font-medium"
                        style={{ background: 'rgba(79, 124, 247, 0.15)', color: '#7ba4f7' }}
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
                  <h3 className="font-semibold text-white mb-3">Frameworks</h3>
                  <div className="flex flex-wrap gap-2">
                    {overallStats.frameworks.map((framework, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full text-sm font-medium"
                        style={{ background: 'rgba(59, 130, 246, 0.15)', color: '#60a5fa' }}
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
                  <h3 className="font-semibold text-white mb-3">Skills</h3>
                  <div className="flex flex-wrap gap-2">
                    {overallStats.resume_skills.map((skill, index) => (
                      <span
                        key={index}
                        className="px-3 py-1 rounded-full text-sm"
                        style={{ background: 'rgba(255, 255, 255, 0.05)', color: '#a1a1aa', border: '1px solid #27272a' }}
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
          <div className="lg:col-span-1 space-y-6">
            <ThumbnailUpload
              onUpload={(file, preview) => {
                setThumbnail({ file, preview });
              }}
            />

            {/* Quality Evaluations */}
            {evaluations.length > 0 && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="font-bold text-gray-800 mb-4">Quality Scores</h3>
                <div className="space-y-4">
                  {evaluations.map((ev) => {
                    const grade = getGrade(ev.overall_score);
                    return (
                      <div key={ev.id} className="border border-gray-100 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-semibold text-gray-800 truncate">{ev.project_name}</p>
                            <p className="text-xs text-gray-500">{ev.language}</p>
                          </div>
                          <div className={`flex items-center gap-1 px-2 py-1 rounded text-sm font-bold ${getGradeColor(grade)}`}>
                            <span>{grade}</span>
                            <span className="text-xs font-normal">{ev.overall_score.toFixed(0)}%</span>
                          </div>
                        </div>
                        {/* Mini category bars */}
                        {ev.category_scores && (
                          <div className="space-y-1">
                            {Object.entries(ev.category_scores).slice(0, 4).map(([cat, score]) => (
                              <div key={cat} className="flex items-center gap-2">
                                <span className="text-xs text-gray-500 w-20 truncate capitalize">{cat.replace(/_/g, ' ')}</span>
                                <div className="flex-1 bg-gray-100 rounded-full h-1.5">
                                  <div
                                    className={`h-1.5 rounded-full ${getBarColor(score)}`}
                                    style={{ width: `${Math.min(score, 100)}%` }}
                                  />
                                </div>
                                <span className="text-xs text-gray-500 w-8 text-right">{score.toFixed(0)}%</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Debug Info */}
      {showDebug && (
        <div className="max-w-6xl mx-auto mt-8">
          <div className="rounded-lg p-4 overflow-auto max-h-96" style={{ background: '#18181b', border: '1px solid #27272a' }}>
            <pre className="text-xs font-mono text-white/70">{JSON.stringify(results, null, 2)}</pre>
          </div>
        </div>
      )}
      </div>
    </>
  );
}
