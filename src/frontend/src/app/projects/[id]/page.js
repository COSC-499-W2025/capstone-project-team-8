'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import config from '@/config';

export default function ProjectDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { isAuthenticated, token } = useAuth();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deleting, setDeleting] = useState(false);
  const [evaluation, setEvaluation] = useState(null);
  const [evalLoading, setEvalLoading] = useState(false);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchProject = async () => {
      try {
        const response = await fetch(
          `${config.API_URL}/api/projects/${params.id}/`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          throw new Error('Failed to fetch project');
        }

        const data = await response.json();
        setProject(data);
      } catch (err) {
        console.error('Error fetching project:', err);
        setError('Failed to load project details');
      } finally {
        setLoading(false);
      }
    };

    if (params.id) {
      fetchProject();
      fetchEvaluation();
    }
  }, [isAuthenticated, token, router, params.id]);

  const fetchEvaluation = async () => {
    setEvalLoading(true);
    try {
      const response = await fetch(
        `${config.API_URL}/api/evaluations/project/${params.id}/`,
        {
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (response.ok) {
        const data = await response.json();
        // Use first evaluation if available
        if (data.evaluations && data.evaluations.length > 0) {
          setEvaluation(data.evaluations[0]);
        }
      }
    } catch (err) {
      console.log('No evaluation data available');
    } finally {
      setEvalLoading(false);
    }
  };

  const getGrade = (score) => {
    if (score >= 90) return 'A';
    if (score >= 80) return 'B';
    if (score >= 70) return 'C';
    if (score >= 60) return 'D';
    return 'F';
  };

  const getGradeColor = (score) => {
    if (score >= 90) return 'text-green-400 bg-green-500/20 border-green-500/30';
    if (score >= 80) return 'text-blue-400 bg-blue-500/20 border-blue-500/30';
    if (score >= 70) return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/30';
    if (score >= 60) return 'text-orange-400 bg-orange-500/20 border-orange-500/30';
    return 'text-red-400 bg-red-500/20 border-red-500/30';
  };

  const getBarColor = (score) => {
    if (score >= 90) return 'bg-green-500';
    if (score >= 80) return 'bg-blue-500';
    if (score >= 70) return 'bg-yellow-500';
    if (score >= 60) return 'bg-orange-500';
    return 'bg-red-500';
  };

  const renderEvalCard = () => {
    if (!evaluation) return null;
    const ev = evaluation;
    const cats = ev.category_scores || {};
    const strengths = Object.entries(cats).filter(([, v]) => v >= 50).sort((a, b) => b[1] - a[1]);
    const improvements = Object.entries(cats).filter(([, v]) => v < 50).sort((a, b) => a[1] - b[1]);
    const evidence = ev.evidence || {};
    const grade = getGrade(ev.overall_score);
    const catLabel = (key) => key.replace(/_/g, ' ');
    const barColor = (val) => {
      if (val >= 70) return '#4ade80';
      if (val >= 45) return '#facc15';
      return '#f87171';
    };

    return (
      <div className="bg-[var(--card-bg)] rounded-lg border border-white/5 overflow-hidden">
        <div className="px-4 pt-4 pb-3 border-b border-white/5">
          <div className="flex items-center justify-between mb-1">
            <span className="text-[11px] uppercase tracking-wider text-white/40">Quality Eval</span>
            <span className="text-[11px] text-white/30">{ev.language}</span>
          </div>
          <div className="flex items-center justify-between">
            <p className="text-sm text-white/80 truncate pr-2">{project?.name || 'Project'}</p>
            <div className="flex items-center gap-2 shrink-0">
              <span style={{ color: barColor(ev.overall_score) }} className="text-2xl font-bold leading-none">{grade}</span>
              <span className="text-white/50 text-xs">{ev.overall_score.toFixed(1)}%</span>
            </div>
          </div>
        </div>
        <div className="px-4 py-3 space-y-2">
          {Object.entries(cats).sort((a, b) => b[1] - a[1]).map(([cat, val]) => (
            <div key={cat}>
              <div className="flex items-center justify-between mb-0.5">
                <span className="text-[11px] text-white/50 capitalize">{catLabel(cat)}</span>
                <span className="text-[11px] text-white/40">{Math.round(val)}%</span>
              </div>
              <div className="w-full bg-white/5 rounded-sm h-1.5">
                <div className="h-1.5 rounded-sm transition-all" style={{ width: `${Math.min(val, 100)}%`, backgroundColor: barColor(val) }} />
              </div>
            </div>
          ))}
        </div>
        {(strengths.length > 0 || improvements.length > 0) && (
          <div className="px-4 py-3 border-t border-white/5">
            <div className="grid grid-cols-2 gap-3">
              {strengths.length > 0 && (
                <div>
                  <span className="text-[10px] uppercase tracking-wider text-white/30 block mb-1">Strengths</span>
                  {strengths.slice(0, 3).map(([cat]) => (
                    <p key={cat} className="text-[11px] text-white/60 capitalize leading-relaxed">{catLabel(cat)}</p>
                  ))}
                </div>
              )}
              {improvements.length > 0 && (
                <div>
                  <span className="text-[10px] uppercase tracking-wider text-white/30 block mb-1">Improve</span>
                  {improvements.slice(0, 3).map(([cat]) => (
                    <p key={cat} className="text-[11px] text-white/60 capitalize leading-relaxed">{catLabel(cat)}</p>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
        {Object.keys(evidence).length > 0 && (
          <div className="px-4 py-3 border-t border-white/5">
            <span className="text-[10px] uppercase tracking-wider text-white/30 block mb-2">Evidence</span>
            <div className="flex flex-wrap gap-1">
              {Object.entries(evidence).filter(([, v]) => v === true || (typeof v === 'number' && v > 0)).slice(0, 10).map(([key, val]) => (
                <span key={key} className="px-1.5 py-0.5 text-[10px] bg-white/5 text-white/50 rounded">
                  {typeof val === 'number' ? `${val} ${key.replace(/_/g, ' ').replace('count', '').trim()}` : key.replace(/^has_|^uses_|^is_/g, '').replace(/_/g, ' ')}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  const handleDeleteProject = async () => {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return;
    }

    setDeleting(true);
    setError('');

    try {
      const response = await fetch(`${config.API_URL}/api/projects/${params.id}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete project');
      }

      // Navigate back to projects list
      router.push('/projects');
    } catch (err) {
      console.error('Error deleting project:', err);
      setError(err.message || 'Failed to delete project');
      setDeleting(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-white">Loading project...</p>
        </div>
      </>
    );
  }

  if (error || !project) {
    return (
      <>
        <Header />
        <div className="min-h-screen p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-6">
              <p className="text-red-400">{error || 'Project not found'}</p>
              <Link
                href="/projects"
                className="inline-block mt-4 text-white hover:opacity-80"
              >
                ← Back to Projects
              </Link>
            </div>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          {/* Back Button */}
          <Link
            href="/projects"
            className="inline-flex items-center text-white hover:opacity-80 mb-6"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M10 19l-7-7m0 0l7-7m-7 7h18"
              />
            </svg>
            Back to Projects
          </Link>

          <div className="flex flex-col lg:flex-row gap-6 items-start">
          {/* Main Content - Left */}
          <div className="flex-1 min-w-0">

          {/* Project Header */}
          <div className="bg-[var(--card-bg)] rounded-lg p-8 mb-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  {project.name || 'Untitled Project'}
                </h1>
                {project.classification_type && (
                  <span className="inline-block px-3 py-1 text-sm font-medium bg-blue-500/20 text-blue-200 rounded">
                    {project.classification_type}
                  </span>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-white/60 text-sm mb-1">Created</p>
                <p className="text-white font-medium">
                  {project.created_at ? formatDate(new Date(project.created_at * 1000)) : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">First Commit</p>
                <p className="text-white font-medium">
                  {project.first_commit_date ? formatDate(new Date(project.first_commit_date * 1000)) : 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Total Files</p>
                <p className="text-white font-medium">{project.total_files || 0}</p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Git Repository</p>
                <p className="text-white font-medium">
                  {project.git_repository ? '✓ Yes' : '✗ No'}
                </p>
              </div>
            </div>

            {project.classification_confidence && (
              <div className="mt-4 pt-4 border-t border-white/10">
                <p className="text-white/60 text-sm mb-2">Classification Confidence</p>
                <div className="flex items-center gap-2">
                  <div className="flex-1 bg-white/10 rounded-full h-2">
                    <div
                      className="bg-green-500 h-2 rounded-full transition-all"
                      style={{ width: `${(project.classification_confidence * 100).toFixed(0)}%` }}
                    />
                  </div>
                  <span className="text-white font-bold">
                    {(project.classification_confidence * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Mobile Eval Card - right after header */}
          <div className="lg:hidden mb-6">
            {renderEvalCard()}
          </div>

          {/* Evaluation Metrics - removed inline, now in sidebar */}
          {evalLoading && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6 animate-pulse">
              <div className="h-6 bg-white/10 rounded w-48 mb-4"></div>
              <div className="space-y-3">
                <div className="h-3 bg-white/10 rounded"></div>
                <div className="h-3 bg-white/10 rounded w-3/4"></div>
              </div>
            </div>
          )}

          {/* Tags Section */}
          {project.project_tag && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Project Tag</h2>
              <span className="inline-block px-4 py-2 bg-blue-500/20 text-blue-200 rounded-full text-sm font-medium">
                {project.project_tag}
              </span>
            </div>
          )}

          {/* Contributors Section */}
          {project.contributors && project.contributors.length > 0 && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">
                Contributors ({project.contributors.length})
              </h2>
              <div className="space-y-3">
                {project.contributors.map((contributor, index) => (
                  <div
                    key={index}
                    className="p-4 bg-white/5 rounded-lg"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div>
                        <p className="text-white font-semibold">{contributor.name}</p>
                        <p className="text-white/60 text-sm">{contributor.email}</p>
                      </div>
                      <span className="text-sm font-bold bg-blue-500/20 text-blue-200 px-3 py-1 rounded">
                        {contributor.percent_of_commits.toFixed(1)}%
                      </span>
                    </div>
                    <div className="grid grid-cols-3 gap-2 text-xs text-white/60">
                      <div>💬 {contributor.commits} commits</div>
                      <div>➕ {contributor.lines_added} lines added</div>
                      <div>➖ {contributor.lines_deleted} lines deleted</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Resume Bullet Points */}
          {project.resume_bullet_points && project.resume_bullet_points.length > 0 && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Resume Highlights</h2>
              <ul className="space-y-2">
                {project.resume_bullet_points.map((point, index) => (
                  <li key={index} className="flex items-start gap-3 text-white/80">
                    <span className="text-blue-400 mt-1">•</span>
                    <span>{point}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Files Section */}
          {project.files && Object.keys(project.files).some(key => project.files[key].length > 0) && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">
                Files ({project.total_files || 0})
              </h2>
              
              {/* Code Files */}
              {project.files.code && project.files.code.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-white/80 text-sm font-semibold mb-3 uppercase tracking-wide">Code Files ({project.files.code.length})</h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {project.files.code.map((file, index) => (
                      <div
                        key={index}
                        className="p-4 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                      >
                        <div className="flex items-start justify-between mb-2">
                          <span className="text-white font-medium">{file.filename}</span>
                          <span className="text-white/60 text-xs bg-white/10 px-2 py-1 rounded">
                            {file.file_extension}
                          </span>
                        </div>
                        <div className="grid grid-cols-3 gap-2 text-xs text-white/60">
                          <div>📄 {file.file_size_bytes ? (file.file_size_bytes / 1024).toFixed(2) + ' KB' : 'N/A'}</div>
                          <div>📝 {file.line_count || 0} lines</div>
                          <div>🔤 {file.character_count || 0} chars</div>
                        </div>
                        {file.content_preview && (
                          <div className="mt-2 p-2 bg-white/5 rounded text-xs text-white/50 font-mono overflow-x-auto">
                            {file.content_preview}...
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Content Files */}
              {project.files.content && project.files.content.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-white/80 text-sm font-semibold mb-3 uppercase tracking-wide">Content Files ({project.files.content.length})</h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {project.files.content.map((file, index) => (
                      <div
                        key={index}
                        className="p-3 bg-white/5 rounded-lg flex items-center justify-between hover:bg-white/10 transition-colors"
                      >
                        <div>
                          <span className="text-white">{file.filename}</span>
                          <span className="text-white/60 text-xs ml-2">({file.file_extension})</span>
                        </div>
                        <span className="text-white/60 text-sm">{file.file_size_bytes ? (file.file_size_bytes / 1024).toFixed(2) + ' KB' : 'N/A'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Image Files */}
              {project.files.image && project.files.image.length > 0 && (
                <div className="mb-6">
                  <h3 className="text-white/80 text-sm font-semibold mb-3 uppercase tracking-wide">Image Files ({project.files.image.length})</h3>
                  <div className="space-y-2 max-h-96 overflow-y-auto">
                    {project.files.image.map((file, index) => (
                      <div
                        key={index}
                        className="p-3 bg-white/5 rounded-lg flex items-center justify-between hover:bg-white/10 transition-colors"
                      >
                        <div>
                          <span className="text-white">{file.filename}</span>
                          <span className="text-white/60 text-xs ml-2">({file.file_extension})</span>
                        </div>
                        <span className="text-white/60 text-sm">🖼️ {file.file_size_bytes ? (file.file_size_bytes / 1024).toFixed(2) + ' KB' : 'N/A'}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Additional Info */}
          {project.project_root_path && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Project Information</h2>
              <div className="space-y-3">
                <div>
                  <p className="text-white/60 text-sm mb-1">Root Path</p>
                  <p className="text-white/80 font-mono text-sm break-all">{project.project_root_path}</p>
                </div>
                {project.classification_type && (
                  <div>
                    <p className="text-white/60 text-sm mb-1">Classification</p>
                    <p className="text-white">{project.classification_type}</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="mt-6 flex gap-4">
            <Link
              href="/results"
              className="px-6 py-3 bg-white text-[var(--card-bg)] font-semibold rounded-lg hover:opacity-80 transition-opacity"
            >
              Generate Resume
            </Link>
            <button
              onClick={handleDeleteProject}
              disabled={deleting}
              className="px-6 py-3 bg-red-500/10 text-red-400 font-semibold rounded-lg hover:bg-red-500/20 transition-colors border border-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {deleting ? 'Deleting...' : 'Delete Project'}
            </button>
          </div>
          </div>

          {/* Sticky Evaluation Sidebar - Right (desktop only) */}
          <div className="hidden lg:block w-72 shrink-0 sticky top-24">
            {renderEvalCard()}
          </div>
          </div>
        </div>
      </div>
    </>
  );
}
