'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import { getPortfolio, deletePortfolio, removeProjectFromPortfolio, updatePortfolio } from '@/utils/portfolioApi';

export default function PortfolioDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { isAuthenticated, token, user } = useAuth();
  const [portfolio, setPortfolio] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [removingProjectId, setRemovingProjectId] = useState(null);
  const [regeneratingSummary, setRegeneratingSummary] = useState(false);

  const portfolioId = params.id;

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        const data = await getPortfolio(portfolioId, token);
        setPortfolio(data);
      } catch (err) {
        console.error('Error fetching portfolio:', err);
        setError(err.message || 'Failed to load portfolio');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, [portfolioId, token]);

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${portfolio.title}"? This action cannot be undone.`)) {
      return;
    }

    try {
      await deletePortfolio(portfolioId, token);
      router.push('/portfolios');
    } catch (err) {
      console.error('Error deleting portfolio:', err);
      setError(err.message || 'Failed to delete portfolio');
    }
  };

  const handleRemoveProject = async (projectId, projectName) => {
    if (!confirm(`Remove "${projectName}" from this portfolio?`)) {
      return;
    }

    setRemovingProjectId(projectId);
    setError('');

    try {
      await removeProjectFromPortfolio(portfolioId, projectId, token);
      setPortfolio(prev => ({
        ...prev,
        projects: prev.projects.filter(p => p.project.id !== projectId),
        project_count: prev.project_count - 1,
      }));
    } catch (err) {
      console.error('Error removing project:', err);
      setError(err.message || 'Failed to remove project');
    } finally {
      setRemovingProjectId(null);
    }
  };

  const handleRegenerateSummary = async () => {
    setRegeneratingSummary(true);
    setError('');

    try {
      const data = await updatePortfolio(portfolioId, { regenerate_summary: true }, token);
      setPortfolio(data.portfolio);
    } catch (err) {
      console.error('Error regenerating summary:', err);
      setError(err.message || 'Failed to regenerate summary');
    } finally {
      setRegeneratingSummary(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  };

  const getToneBadgeColor = (tone) => {
    const colors = {
      professional: 'bg-blue-500/30 text-blue-200',
      casual: 'bg-green-500/30 text-green-200',
      technical: 'bg-purple-500/30 text-purple-200',
      creative: 'bg-orange-500/30 text-orange-200',
    };
    return colors[tone] || 'bg-gray-500/30 text-gray-200';
  };

  const isOwner = user && portfolio && portfolio.user_id === user.id;

  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <p className="text-white">Loading portfolio...</p>
          </div>
        </div>
      </>
    );
  }

  if (portfolio && portfolio.is_private) {
    return (
      <>
        <Header />
        <div className="min-h-screen p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-[var(--card-bg)] rounded-lg p-8 text-center" style={{ border: '1px solid #27272a' }}>
              <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ background: 'rgba(79, 124, 247, 0.1)' }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">Private Portfolio</h2>
              <p className="text-white/60 mb-1">
                <span className="font-medium text-white">{portfolio.portfolio_title}</span>
              </p>
              {portfolio.owner && (
                <p className="text-white/50 text-sm mb-6">by {portfolio.owner}</p>
              )}
              <p className="text-white/50 text-sm mb-6">
                The owner has set this portfolio to private. It is not available for public viewing.
              </p>
              <Link
                href="/portfolios"
                className="inline-block px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                Back to Portfolios
              </Link>
            </div>
          </div>
        </div>
      </>
    );
  }

  if (error && !portfolio) {
    return (
      <>
        <Header />
        <div className="min-h-screen p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 text-center">
              <h2 className="text-xl font-semibold text-red-400 mb-2">Error Loading Portfolio</h2>
              <p className="text-red-300 mb-4">{error}</p>
              <Link
                href="/portfolios"
                className="inline-block px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors"
              >
                Back to Portfolios
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
        <div className="max-w-5xl mx-auto">
          {/* Breadcrumb */}
          <div className="mb-6">
            <Link href="/portfolios" className="text-white/60 hover:text-white transition-colors text-sm">
              ← Back to Portfolios
            </Link>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {/* Portfolio Header */}
          <div className="bg-[var(--card-bg)] rounded-lg p-8 mb-6" style={{ border: '1px solid #27272a' }}>
            <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-4">
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  <h1 className="text-3xl font-bold text-white">{portfolio.title}</h1>
                  {portfolio.is_public ? (
                    <span className="px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full">
                      Public
                    </span>
                  ) : (
                    <span className="px-2 py-1 bg-gray-500/20 text-gray-300 text-xs rounded-full">
                      Private
                    </span>
                  )}
                </div>
                {portfolio.description && (
                  <p className="text-white/70 mb-4">{portfolio.description}</p>
                )}
                <div className="flex flex-wrap items-center gap-4 text-sm text-white/60">
                  <span>Created {formatDate(portfolio.created_at)}</span>
                  {portfolio.updated_at && portfolio.updated_at !== portfolio.created_at && (
                    <span>Updated {formatDate(portfolio.updated_at)}</span>
                  )}
                  {portfolio.tone && (
                    <span className={`px-2 py-0.5 rounded ${getToneBadgeColor(portfolio.tone)}`}>
                      {portfolio.tone}
                    </span>
                  )}
                  {portfolio.target_audience && (
                    <span>For: {portfolio.target_audience}</span>
                  )}
                </div>
              </div>

              {isOwner && (
                <div className="flex items-center gap-2">
                  <Link
                    href={`/portfolios/${portfolioId}/edit`}
                    className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
                  >
                    Edit
                  </Link>
                  <button
                    onClick={handleDelete}
                    className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 text-sm font-medium transition-colors"
                  >
                    Delete
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* AI Summary Section */}
          {(portfolio.summary || isOwner) && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6" style={{ border: '1px solid #27272a' }}>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="3" />
                    <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
                  </svg>
                  AI-Generated Summary
                </h2>
                {isOwner && (
                  <button
                    onClick={handleRegenerateSummary}
                    disabled={regeneratingSummary}
                    className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm transition-colors disabled:opacity-50 flex items-center gap-2"
                  >
                    {regeneratingSummary ? (
                      <>
                        <div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Regenerating...
                      </>
                    ) : (
                      <>
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M23 4v6h-6"></path>
                          <path d="M1 20v-6h6"></path>
                          <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
                        </svg>
                        Regenerate
                      </>
                    )}
                  </button>
                )}
              </div>
              {portfolio.summary ? (
                <div className="prose prose-invert max-w-none">
                  <p className="text-white/80 whitespace-pre-wrap">{portfolio.summary}</p>
                </div>
              ) : (
                <p className="text-white/50 italic">No summary generated yet. Click "Regenerate" to create one.</p>
              )}
              {portfolio.summary_generated_at && (
                <p className="text-white/40 text-xs mt-3">
                  Generated: {formatDate(portfolio.summary_generated_at)}
                </p>
              )}
            </div>
          )}

          {/* Projects Section */}
          <div className="bg-[var(--card-bg)] rounded-lg p-6" style={{ border: '1px solid #27272a' }}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-semibold text-white">
                Projects ({portfolio.project_count || portfolio.projects?.length || 0})
              </h2>
              {isOwner && (
                <Link
                  href={`/portfolios/${portfolioId}/edit`}
                  className="px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm transition-colors flex items-center gap-2"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="12" y1="5" x2="12" y2="19"></line>
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                  Add Projects
                </Link>
              )}
            </div>

            {portfolio.projects && portfolio.projects.length > 0 ? (
              <div className="space-y-4">
                {portfolio.projects.map((portfolioProject, index) => {
                  const project = portfolioProject.project;
                  return (
                    <div
                      key={project.id}
                      className="bg-white/5 rounded-lg p-4 hover:bg-white/10 transition-colors group"
                    >
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-3 mb-2">
                            <span className="text-white/40 text-sm font-mono">#{index + 1}</span>
                            <Link 
                              href={`/projects/${project.id}`}
                              className="text-lg font-semibold text-white hover:text-blue-400 transition-colors truncate"
                            >
                              {project.name}
                            </Link>
                            {portfolioProject.featured && (
                              <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-300 text-xs rounded">
                                Featured
                              </span>
                            )}
                          </div>
                          {project.description && (
                            <p className="text-white/60 text-sm mb-2 line-clamp-2">
                              {project.description}
                            </p>
                          )}
                          {portfolioProject.notes && (
                            <p className="text-white/50 text-sm italic">
                              Note: {portfolioProject.notes}
                            </p>
                          )}
                          <div className="flex flex-wrap items-center gap-3 mt-2 text-xs text-white/50">
                            {project.classification_type && (
                              <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 rounded">
                                {project.classification_type}
                              </span>
                            )}
                            {project.total_files > 0 && (
                              <span>{project.total_files} files</span>
                            )}
                          </div>
                        </div>
                        {isOwner && (
                          <button
                            onClick={() => handleRemoveProject(project.id, project.name)}
                            disabled={removingProjectId === project.id}
                            className="shrink-0 px-3 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 text-xs transition-colors opacity-0 group-hover:opacity-100 disabled:opacity-50"
                          >
                            {removingProjectId === project.id ? '...' : 'Remove'}
                          </button>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center" style={{ background: 'rgba(79, 124, 247, 0.1)' }}>
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                  </svg>
                </div>
                <p className="text-white/60 mb-4">No projects in this portfolio yet</p>
                {isOwner && (
                  <Link
                    href={`/portfolios/${portfolioId}/edit`}
                    className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors"
                    style={{ background: '#4f7cf7', color: 'white' }}
                  >
                    Add Your First Project
                  </Link>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
