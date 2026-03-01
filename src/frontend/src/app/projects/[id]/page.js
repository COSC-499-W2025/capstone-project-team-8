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
          <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden mb-6 border border-white/5">

            {/* Top meta bar */}
            <div className="flex items-center justify-between px-5 py-2 border-b border-white/10 bg-white/[0.02]">
              <span className="text-[11px] uppercase tracking-widest text-white/40 font-medium flex items-center gap-2">
                Project Record
                {project.classification_type && (
                  <> · Classification: <span className="text-blue-400">{project.classification_type}</span></>
                )}
                {project.project_tag && (
                  <span className="ml-2 px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded text-[10px] font-bold tracking-widest uppercase">{project.project_tag}</span>
                )}
              </span>
              <div className="flex items-center gap-4 text-[11px] uppercase tracking-widest text-white/40">
                <span>Ref. {params.id}_Updated</span>
                {project.git_repository && <span>Version Control · Git</span>}
                <span className="flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 inline-block"></span>
                  Active
                </span>
              </div>
            </div>

            {/* Main title */}
            <div className="px-5 pt-5 pb-4">
              <h1 className="text-4xl font-black uppercase tracking-tight text-white leading-none">
                {project.name || 'Untitled Project'}&nbsp;
                <span className="text-blue-400">#{params.id}</span>
              </h1>
            </div>

            {/* Stats bar */}
            <div className="flex flex-wrap items-center gap-0 border-t border-b border-white/10 text-[11px] uppercase tracking-widest">
              {[
                { label: 'First Commit', value: project.first_commit_date ? new Date(project.first_commit_date * 1000).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) : 'N/A' },
                { label: 'Total Files', value: project.total_files ?? 0 },
                { label: 'Contributors', value: project.contributors?.length ?? 0 },
                { label: 'Commits', value: project.contributors?.reduce((s, c) => s + (c.commits || 0), 0) || 0 },
                { label: 'Code Files', value: project.files?.code?.length ?? 0 },
              ].map((stat, i) => (
                <div key={i} className="flex items-center">
                  <div className="px-5 py-2.5">
                    <span className="text-white/40">{stat.label}&nbsp;</span>
                    <span className="text-white font-bold">{stat.value}</span>
                  </div>
                  <span className="text-white/10 select-none">|</span>
                </div>
              ))}
            </div>

            {/* Big 3 stats */}
            <div className="grid grid-cols-1 sm:grid-cols-3 divide-y sm:divide-y-0 sm:divide-x divide-white/10">
              {/* Total Commits */}
              <div className="px-6 py-6">
                <p className="text-6xl font-black text-white leading-none mb-1">
                  {project.contributors?.reduce((s, c) => s + (c.commits || 0), 0) || 0}
                </p>
                <p className="text-[11px] uppercase tracking-widest text-white/50 font-semibold">Total Commits</p>
                {project.contributors && project.contributors.length > 0 && (
                  <p className="text-xs text-blue-400 mt-1">across {project.contributors.length} contributor{project.contributors.length !== 1 ? 's' : ''}</p>
                )}
              </div>

              {/* Managed Files */}
              <div className="px-6 py-6">
                <p className="text-6xl font-black text-white leading-none mb-1">{project.total_files || 0}</p>
                <p className="text-[11px] uppercase tracking-widest text-white/50 font-semibold">Managed Files</p>
                <p className="text-xs text-blue-400 mt-1">
                  {project.files?.code?.length ?? 0} code
                  {project.files?.content?.length ? ` · ${project.files.content.length} content` : ''}
                  {project.files?.image?.length ? ` · ${project.files.image.length} image${project.files.image.length !== 1 ? 's' : ''}` : ''}
                </p>
              </div>

              {/* Classification Confidence */}
              <div className="px-6 py-6">
                <div className="flex items-end gap-1 leading-none mb-1">
                  <p className="text-6xl font-black text-white">
                    {project.classification_confidence ? (project.classification_confidence * 100).toFixed(0) : '—'}
                  </p>
                  {project.classification_confidence && (
                    <span className="text-blue-400 text-2xl font-bold mb-1">%</span>
                  )}
                </div>
                <p className="text-[11px] uppercase tracking-widest text-white/50 font-semibold">Classification Confidence</p>
                {project.classification_confidence && (
                  <div className="mt-2 flex items-center gap-2">
                    <div className="flex-1 bg-white/10 rounded-sm h-1.5">
                      <div
                        className="bg-blue-500 h-1.5 rounded-sm transition-all"
                        style={{ width: `${(project.classification_confidence * 100).toFixed(0)}%` }}
                      />
                    </div>
                    <span className="text-white/50 text-[11px]">{(project.classification_confidence * 100).toFixed(1)}</span>
                  </div>
                )}
              </div>
            </div>

            {/* Contributor distribution bar */}
            {project.contributors && project.contributors.length > 0 && (() => {
              const total = project.contributors.reduce((s, c) => s + (c.commits || 0), 0);
              return (
                <div className="px-5 py-4 border-t border-white/10">
                  <p className="text-xs uppercase tracking-widest text-white/70 mb-2 font-black">Commit Distribution by Contributor</p>
                  <div className="flex w-full h-5 rounded-sm overflow-hidden gap-px">
                    {project.contributors.map((c, i) => {
                      const pct = total > 0 ? ((c.commits || 0) / total) * 100 : 0;
                      return (
                        <div
                          key={i}
                          title={`${c.name}: ${pct.toFixed(1)}%`}
                          style={{ width: `${pct}%` }}
                          className="flex items-center justify-center overflow-hidden bg-white"
                        >
                          {pct > 8 && (
                            <span className="text-[11px] font-black text-black uppercase tracking-widest truncate px-1 drop-shadow">
                              {c.name?.split(' ')[0]?.[0] || '?'} · {pct.toFixed(1)}%
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })()}
          </div>

          {/* Mobile Eval Card + Actions */}
          <div className="lg:hidden mb-6">
            {renderEvalCard()}
            <div className="flex flex-col gap-2 mt-3">
              <Link
                href="/results"
                className="w-full text-center px-4 py-2.5 bg-white text-[var(--card-bg)] text-xs font-black uppercase tracking-widest rounded hover:opacity-80 transition-opacity"
              >
                Generate Resume
              </Link>
              <button
                onClick={handleDeleteProject}
                disabled={deleting}
                className="w-full px-4 py-2.5 bg-red-500/10 text-red-400 text-xs font-black uppercase tracking-widest rounded hover:bg-red-500/20 transition-colors border border-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {deleting ? 'Deleting...' : 'Delete Project'}
              </button>
            </div>
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

          {/* Contributors Section */}
          {project.contributors && project.contributors.length > 0 && (
            <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden mb-6 border border-white/5">
              {/* Header */}
              <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between">
                <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">Contributors</span>
                <span className="text-[11px] uppercase tracking-widest text-white/30">{project.contributors.length} total</span>
              </div>
              {/* Column headers */}
              <div className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-x-4 px-5 py-1.5 border-b border-white/5 text-[10px] uppercase tracking-widest text-white/25 font-bold">
                <span>Name</span>
                <span className="text-right w-10">%</span>
                <span className="text-right w-16">Commits</span>
                <span className="text-right w-20">Added</span>
                <span className="text-right w-20">Deleted</span>
              </div>
              {/* Rows */}
              {project.contributors.map((contributor, index) => (
                <div
                  key={index}
                  className="grid grid-cols-[1fr_auto_auto_auto_auto] gap-x-4 px-5 py-2.5 border-b border-white/5 last:border-0 hover:bg-white/[0.02] transition-colors items-center"
                >
                  <div className="min-w-0">
                    <p className="text-white text-sm font-bold truncate">{contributor.name}</p>
                    <p className="text-white/30 text-[10px] truncate">{contributor.email?.split(',')[0]}</p>
                  </div>
                  <div className="w-10 text-right">
                    <span className="text-white font-black text-sm">{contributor.percent_of_commits.toFixed(1)}<span className="text-white/40 text-[10px]">%</span></span>
                  </div>
                  <div className="w-16 text-right">
                    <span className="text-white/70 text-xs font-mono">{contributor.commits.toLocaleString()}</span>
                  </div>
                  <div className="w-20 text-right">
                    <span className="text-green-400/70 text-xs font-mono">+{contributor.lines_added?.toLocaleString() ?? 0}</span>
                  </div>
                  <div className="w-20 text-right">
                    <span className="text-red-400/70 text-xs font-mono">-{contributor.lines_deleted?.toLocaleString() ?? 0}</span>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Resume Bullet Points */}
          {project.resume_bullet_points && project.resume_bullet_points.length > 0 && (
            <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden mb-6 border border-white/5">
              <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between">
                <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">Resume Highlights</span>
                <span className="text-[11px] uppercase tracking-widest text-white/30">{project.resume_bullet_points.length} items</span>
              </div>
              <div className="divide-y divide-white/5 max-h-80 overflow-y-auto">
                {project.resume_bullet_points.map((point, index) => (
                  <div key={index} className="flex items-start gap-3 px-5 py-2 hover:bg-white/[0.02] transition-colors">
                    <span className="text-white/20 text-[10px] font-mono mt-0.5 w-5 shrink-0 text-right">{String(index + 1).padStart(2, '0')}</span>
                    <span className="text-white/70 text-xs leading-relaxed">{point}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Files Section */}
          {project.files && Object.keys(project.files).some(key => project.files[key].length > 0) && (
            <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden mb-6 border border-white/5">
              {/* Header */}
              <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between">
                <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">Files</span>
                <span className="text-[11px] uppercase tracking-widest text-white/30">{project.total_files || 0} total</span>
              </div>

              {/* Sub-sections */}
              {[
                { key: 'code', label: 'Code Files' },
                { key: 'content', label: 'Content Files' },
                { key: 'image', label: 'Image Files' },
              ].map(({ key, label }) => project.files[key] && project.files[key].length > 0 && (
                <div key={key} className="mt-3 mx-3 mb-0 rounded-md overflow-hidden border border-white/10 last:mb-3">
                  {/* Sub-header */}
                  <div className="px-4 py-2 border-b border-blue-500/20 bg-blue-500/[0.04] flex items-center justify-between text-blue-400/70">
                    <span className="text-[10px] uppercase tracking-widest font-black">{label}</span>
                    <span className="text-[10px] opacity-60">{project.files[key].length} file{project.files[key].length !== 1 ? 's' : ''}</span>
                  </div>
                  {/* Column headers */}
                  <div className="grid grid-cols-[1fr_auto_auto_auto] gap-x-4 px-4 py-1 border-b border-white/5 text-[10px] uppercase tracking-widest text-white/20 font-bold">
                    <span>Filename</span>
                    <span className="w-12 text-right">Ext</span>
                    <span className="w-16 text-right">Size</span>
                    <span className="w-16 text-right">Lines</span>
                  </div>
                  {/* Rows */}
                  <div className="divide-y divide-white/5 max-h-64 overflow-y-auto">
                    {project.files[key].map((file, index) => (
                      <div key={index} className="grid grid-cols-[1fr_auto_auto_auto] gap-x-4 px-4 py-2 hover:bg-white/[0.02] transition-colors items-center">
                        <span className="text-white/70 text-xs font-mono truncate">{file.filename}</span>
                        <span className="w-12 text-right text-[10px] text-white/30 font-mono">{file.file_extension || '—'}</span>
                        <span className="w-16 text-right text-[10px] text-white/40 font-mono">
                          {file.file_size_bytes ? (file.file_size_bytes / 1024).toFixed(1) + ' KB' : '—'}
                        </span>
                        <span className="w-16 text-right text-[10px] text-white/40 font-mono">
                          {file.line_count != null ? file.line_count.toLocaleString() : '—'}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          )}


          </div>

          {/* Sticky Evaluation Sidebar - Right (desktop only) */}
          <div className="hidden lg:flex flex-col gap-3 w-72 shrink-0 sticky top-24">
            {renderEvalCard()}
            <Link
              href="/results"
              className="w-full text-center px-4 py-2.5 bg-white text-[var(--card-bg)] text-xs font-black uppercase tracking-widest rounded hover:opacity-80 transition-opacity"
            >
              Generate Resume
            </Link>
            <button
              onClick={handleDeleteProject}
              disabled={deleting}
              className="w-full px-4 py-2.5 bg-red-500/10 text-red-400 text-xs font-black uppercase tracking-widest rounded hover:bg-red-500/20 transition-colors border border-red-500/50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {deleting ? 'Deleting...' : 'Delete Project'}
            </button>
          </div>
          </div>
        </div>
      </div>
    </>
  );
}
