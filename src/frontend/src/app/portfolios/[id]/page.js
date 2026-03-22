'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import PortfolioActivityHeatmap from '@/components/PortfolioActivityHeatmap';
import config from '@/config';
import { getPortfolio, getPortfolioById, deletePortfolio, removeProjectFromPortfolio, updatePortfolio, generateResumeFromPortfolio, getPortfolioStats } from '@/utils/portfolioApi';

export default function PortfolioDetailPage() {
  const router = useRouter();
  const params = useParams();
  const { isAuthenticated, token, user } = useAuth();
  const [portfolio, setPortfolio] = useState(null);
  const [ownerProfile, setOwnerProfile] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [removingProjectId, setRemovingProjectId] = useState(null);
  const [regeneratingSummary, setRegeneratingSummary] = useState(false);
  const [generatingResume, setGeneratingResume] = useState(false);
  const [shareCopied, setShareCopied] = useState(false);

  const portfolioSlug = params.id;

  useEffect(() => {
    const fetchPortfolio = async () => {
      try {
        let data;
        try {
          data = await getPortfolio(portfolioSlug, token);
        } catch (slugError) {
          if (/^\d+$/.test(portfolioSlug)) {
            data = await getPortfolioById(Number(portfolioSlug), token);
            if (data?.slug) {
              router.replace(`/portfolios/${data.slug}`);
            }
          } else {
            throw slugError;
          }
        }

        setPortfolio(data);

        // Fetch owner public profile
        if (data.user_username) {
          try {
            const profileRes = await fetch(`${config.API_URL}/api/users/${data.user_username}/`);
            if (profileRes.ok) {
              const profileData = await profileRes.json();
              setOwnerProfile(profileData.user);
            }
          } catch (e) { /* ignore */ }
        }

        // Fetch portfolio stats
        try {
          const statsData = await getPortfolioStats(portfolioSlug, token);
          setStats(statsData);
        } catch (e) { /* ignore */ }
      } catch (err) {
        console.error('Error fetching portfolio:', err);
        setError(err.message || 'Failed to load portfolio');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolio();
  }, [portfolioSlug, token]);

  const handleDelete = async () => {
    if (!confirm(`Are you sure you want to delete "${portfolio.title}"? This action cannot be undone.`)) return;
    try {
      await deletePortfolio(portfolio.id, token);
      router.push('/portfolios');
    } catch (err) {
      setError(err.message || 'Failed to delete portfolio');
    }
  };

  const handleRemoveProject = async (projectId, projectName) => {
    if (!confirm(`Remove "${projectName}" from this portfolio?`)) return;
    setRemovingProjectId(projectId);
    setError('');
    try {
      await removeProjectFromPortfolio(portfolio.id, projectId, token);
      setPortfolio(prev => ({
        ...prev,
        projects: prev.projects.filter(p => p.project.id !== projectId),
        project_count: prev.project_count - 1,
      }));
    } catch (err) {
      setError(err.message || 'Failed to remove project');
    } finally {
      setRemovingProjectId(null);
    }
  };

  const handleRegenerateSummary = async () => {
    setRegeneratingSummary(true);
    setError('');
    try {
      const data = await updatePortfolio(portfolio.id, { regenerate_summary: true }, token);
      setPortfolio(data.portfolio);
    } catch (err) {
      setError(err.message || 'Failed to regenerate summary');
    } finally {
      setRegeneratingSummary(false);
    }
  };

  const handleGenerateResume = async () => {
    setGeneratingResume(true);
    setError('');

    try {
      const data = await generateResumeFromPortfolio(portfolio.id, token);
      // Redirect to resume page with the new resume ID
      router.push(`/resume?resume_id=${data.resume_id}`);
    } catch (err) {
      console.error('Error generating resume:', err);
      setError(err.message || 'Failed to generate resume');
      setGeneratingResume(false);
    }
  };

  const handleCopyShareLink = async () => {
    if (!portfolio?.slug) return;

    const shareUrl = `${window.location.origin}/portfolios/${portfolio.slug}`;
    try {
      if (navigator?.clipboard?.writeText) {
        await navigator.clipboard.writeText(shareUrl);
      } else {
        const textArea = document.createElement('textarea');
        textArea.value = shareUrl;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
      }
      setShareCopied(true);
      setTimeout(() => setShareCopied(false), 2000);
    } catch (err) {
      setError('Failed to copy share link');
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  };

  const isOwner = user && portfolio && (Number(portfolio.user_id) === Number(user.id) || (portfolio.user_username && user.username && portfolio.user_username === user.username));
  const profile = ownerProfile || {};
  const displayName = [profile.first_name, profile.last_name].filter(Boolean).join(' ') || portfolio?.user_username || 'User';
  const initials = displayName.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  const location = [profile.education_city, profile.education_state].filter(Boolean).join(', ');

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
            <div className="bg-[var(--card-bg)] rounded-lg p-8 text-center border border-white/5">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center bg-blue-500/10">
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
                  <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">Private Portfolio</h2>
              <p className="text-white/60 mb-1"><span className="font-medium text-white">{portfolio.portfolio_title}</span></p>
              {portfolio.owner && <p className="text-white/50 text-sm mb-6">by {portfolio.owner}</p>}
              <p className="text-white/50 text-sm mb-6">The owner has set this portfolio to private.</p>
              <Link href="/portfolios" className="inline-block px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors">Back to Portfolios</Link>
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
              <Link href="/portfolios" className="inline-block px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors">Back to Portfolios</Link>
            </div>
          </div>
        </div>
      </>
    );
  }

  const allLanguages = Array.isArray(stats?.languages) ? stats.languages.sort((a, b) => (b.lines_of_code || 0) - (a.lines_of_code || 0)) : [];
  const allFrameworks = Array.isArray(stats?.frameworks) ? stats.frameworks.sort((a, b) => (b.project_count || 0) - (a.project_count || 0)) : [];

  return (
    <>
      <Header />
      <div className="min-h-screen pb-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6">

          {/* ====== BANNER + PROFILE HEADER (LinkedIn-style) ====== */}
          <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden border border-white/5 mt-6 mb-4">
            {/* Cover banner */}
            <div className="h-36 sm:h-48 relative" style={{ background: 'linear-gradient(135deg, #1a3a5c 0%, #0f2027 40%, #203a43 70%, #2c5364 100%)' }}>
              {isOwner && (
                <div className="absolute top-3 right-3 flex items-center gap-2">
                  <Link href={`/portfolios/${portfolio.slug}/edit`} className="px-3 py-1.5 rounded bg-black/40 hover:bg-black/60 text-white text-xs font-medium transition-colors backdrop-blur-sm">Edit Portfolio</Link>
                </div>
              )}
            </div>

            {/* Profile info area */}
            <div className="relative px-6 pb-5 pt-20">
              {/* Avatar overlapping banner */}
              <div className="absolute -top-16 left-6">
                {profile.profile_image_url ? (
                  <img src={profile.profile_image_url} alt={displayName} className="w-32 h-32 rounded-full border-4 border-[var(--card-bg)] object-cover bg-white/10" />
                ) : (
                  <div className="w-32 h-32 rounded-full border-4 border-[var(--card-bg)] bg-white flex items-center justify-center">
                    <span className="text-3xl font-black text-black">{initials}</span>
                  </div>
                )}
              </div>

              {/* Right-side actions (below banner, aligned right) */}
              <div className="absolute top-3 right-6 flex gap-2">
                {isOwner && (
                  <>
                    <button onClick={handleCopyShareLink} className="px-4 py-1.5 rounded-full border border-emerald-400/50 text-emerald-300 text-xs font-bold hover:bg-emerald-400/10 transition-colors">
                      {shareCopied ? 'Copied!' : 'Copy Share Link'}
                    </button>
                    <Link href="/profile" className="px-4 py-1.5 rounded-full border border-blue-400 text-blue-400 text-xs font-bold hover:bg-blue-400/10 transition-colors">Edit Profile</Link>
                    <button onClick={handleDelete} className="px-4 py-1.5 rounded-full border border-red-400/50 text-red-400 text-xs font-bold hover:bg-red-400/10 transition-colors">Delete</button>
                  </>
                )}
              </div>

              {/* Name + headline */}
              <div>
                <div className="flex items-center gap-3 flex-wrap">
                  <h1 className="text-2xl font-black text-white">{displayName}</h1>
                  {portfolio.is_public ? (
                    <span className="px-2 py-0.5 bg-green-500/20 text-green-300 text-[10px] font-bold uppercase tracking-wider rounded-full">Public</span>
                  ) : (
                    <span className="px-2 py-0.5 bg-gray-500/20 text-gray-400 text-[10px] font-bold uppercase tracking-wider rounded-full">Private</span>
                  )}
                </div>

                {/* Headline / bio */}
                {profile.bio ? (
                  <p className="text-white/70 text-sm mt-1">{profile.bio}</p>
                ) : portfolio.description ? (
                  <p className="text-white/70 text-sm mt-1">{portfolio.description}</p>
                ) : null}

                {/* University + degree */}
                {(profile.university || profile.degree_major) && (
                  <p className="text-white/50 text-sm mt-1">
                    {profile.degree_major && <span>{profile.degree_major}</span>}
                    {profile.degree_major && profile.university && <span> @ </span>}
                    {profile.university && <span className="font-medium text-white/60">{profile.university}</span>}
                  </p>
                )}

                {/* Location + links row */}
                <div className="flex flex-wrap items-center gap-x-4 gap-y-1 mt-2 text-xs text-white/40">
                  {location && (
                    <span className="flex items-center gap-1">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                      {location}
                    </span>
                  )}
                  {stats && (
                    <span>{stats.total_projects || portfolio.project_count || 0} projects</span>
                  )}
                </div>

                {/* Social links */}
                <div className="flex flex-wrap items-center gap-3 mt-3">
                  {profile.github_username && (
                    <a href={`https://github.com/${profile.github_username}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 transition-colors">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                      {profile.github_username}
                    </a>
                  )}
                  {profile.linkedin_url && (
                    <a href={profile.linkedin_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 transition-colors">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                      LinkedIn
                    </a>
                  )}
                  {profile.portfolio_url && (
                    <a href={profile.portfolio_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 transition-colors">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10"/><path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>
                      Website
                    </a>
                  )}
                  {profile.twitter_username && (
                    <a href={`https://x.com/${profile.twitter_username}`} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1.5 text-xs text-blue-400 hover:text-blue-300 transition-colors">
                      <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                      @{profile.twitter_username}
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>

          {error && (
            <div className="mb-4 p-4 bg-red-500/10 border border-red-500 rounded-lg">
              <p className="text-red-400 text-sm">{error}</p>
            </div>
          )}

          {/* ====== MAIN CONTENT: 2-column layout ====== */}
          <div className="flex flex-col lg:flex-row gap-4 items-start">

            {/* LEFT COLUMN (main) */}
            <div className="flex-1 min-w-0 space-y-4">

              {/* ---- ABOUT SECTION ---- */}
              {(portfolio.summary || isOwner) && (
                <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden border border-white/5">
                  <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between">
                    <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">About</span>
                    {isOwner && (
                      <button
                        onClick={handleRegenerateSummary}
                        disabled={regeneratingSummary}
                        className="flex items-center gap-1.5 text-[11px] text-white/40 hover:text-white/70 transition-colors disabled:opacity-50"
                      >
                        {regeneratingSummary ? (
                          <><div className="w-3 h-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></div> Regenerating...</>
                        ) : (
                          <><svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M23 4v6h-6"/><path d="M1 20v-6h6"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"/></svg> Regenerate</>
                        )}
                      </button>
                    )}
                  </div>
                  <div className="px-5 py-4">
                    {portfolio.summary ? (
                      <p className="text-white/70 text-sm leading-relaxed whitespace-pre-wrap">{portfolio.summary}</p>
                    ) : (
                      <p className="text-white/40 text-sm italic">No summary generated yet. Click &quot;Regenerate&quot; to create one.</p>
                    )}
                    {portfolio.summary_generated_at && (
                      <p className="text-white/25 text-[10px] mt-3">AI-generated · {formatDate(portfolio.summary_generated_at)}</p>
                    )}
                  </div>
                </div>
              )}

              {/* ---- ACTIVITY HEATMAP SECTION ---- */}
              <PortfolioActivityHeatmap portfolioId={portfolio.id} token={token} />

              {/* ---- PROJECTS / EXPERIENCE SECTION ---- */}
              <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden border border-white/5">
                <div className="px-5 py-3 border-b border-white/10 flex items-center justify-between">
                  <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">
                    Projects
                    <span className="ml-2 text-white/30">{portfolio.project_count || portfolio.projects?.length || 0}</span>
                  </span>
                  {isOwner && (
                    <Link href={`/portfolios/${portfolio.slug}/edit`} className="flex items-center gap-1 text-[11px] text-white/40 hover:text-white/70 transition-colors">
                      <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
                      Add
                    </Link>
                  )}
                </div>

                {portfolio.projects && portfolio.projects.length > 0 ? (
                  <div className="divide-y divide-white/5">
                    {portfolio.projects.map((portfolioProject, index) => {
                      const project = portfolioProject.project;
                      return (
                        <div key={project.id} className="px-5 py-4 hover:bg-white/[0.02] transition-colors group">
                          <div className="flex items-start gap-4">
                            {/* Project icon */}
                            <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center shrink-0 mt-0.5">
                              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                              </svg>
                            </div>

                            <div className="flex-1 min-w-0">
                              <div className="flex items-center gap-2 flex-wrap">
                                <Link href={`/projects/${project.id}`} className="text-sm font-bold text-white hover:text-blue-400 transition-colors">
                                  {project.name}
                                </Link>
                                {portfolioProject.featured && (
                                  <span className="px-1.5 py-0.5 bg-yellow-500/20 text-yellow-300 text-[9px] font-bold uppercase rounded">Featured</span>
                                )}
                              </div>
                              {project.classification_type && (
                                <p className="text-white/40 text-xs mt-0.5">{project.classification_type}</p>
                              )}
                              {project.description && (
                                <p className="text-white/50 text-xs mt-1 line-clamp-2">{project.description}</p>
                              )}
                              {portfolioProject.notes && (
                                <p className="text-white/40 text-xs mt-1 italic">&ldquo;{portfolioProject.notes}&rdquo;</p>
                              )}
                              <div className="flex flex-wrap items-center gap-2 mt-2">
                                {project.total_files > 0 && (
                                  <span className="px-1.5 py-0.5 bg-white/5 text-white/40 text-[10px] rounded">{project.total_files} files</span>
                                )}
                              </div>
                            </div>

                            {isOwner && (
                              <button
                                onClick={() => handleRemoveProject(project.id, project.name)}
                                disabled={removingProjectId === project.id}
                                className="shrink-0 px-2 py-1 rounded bg-red-500/10 hover:bg-red-500/20 text-red-400 text-[10px] font-bold opacity-0 group-hover:opacity-100 transition-all disabled:opacity-50"
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
                  <div className="text-center py-10 px-5">
                    <div className="w-12 h-12 mx-auto mb-3 rounded-full flex items-center justify-center bg-blue-500/10">
                      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                      </svg>
                    </div>
                    <p className="text-white/50 text-sm mb-3">No projects yet</p>
                    {isOwner && (
                      <Link href={`/portfolios/${portfolio.slug}/edit`} className="inline-flex items-center gap-2 px-4 py-2 rounded-lg text-xs font-bold transition-colors bg-blue-500 text-white hover:bg-blue-600">
                        Add Your First Project
                      </Link>
                    )}
                  </div>
                )}
              </div>

              {/* ---- SKILLS SECTION (from portfolio stats) ---- */}
              {(allLanguages.length > 0 || allFrameworks.length > 0) && (
                <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden border border-white/5">
                  <div className="px-5 py-3 border-b border-white/10">
                    <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">Skills</span>
                  </div>
                  <div className="px-5 py-4">
                    {allLanguages.length > 0 && (
                      <div className="mb-4">
                        <p className="text-[10px] uppercase tracking-wider text-white/30 font-bold mb-2">Languages</p>
                        <div className="flex flex-wrap gap-1.5">
                          {allLanguages.map((lang) => (
                            <span key={lang.language} className="px-2.5 py-1 bg-blue-500/10 text-blue-300 text-xs rounded-full border border-blue-500/20 font-medium">
                              {lang.language}
                              {lang.lines_of_code > 0 && <span className="text-white/30 ml-1 text-[10px]">{lang.lines_of_code.toLocaleString()} lines</span>}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                    {allFrameworks.length > 0 && (
                      <div>
                        <p className="text-[10px] uppercase tracking-wider text-white/30 font-bold mb-2">Frameworks & Tools</p>
                        <div className="flex flex-wrap gap-1.5">
                          {allFrameworks.map((fw) => (
                            <span key={fw.framework} className="px-2.5 py-1 bg-purple-500/10 text-purple-300 text-xs rounded-full border border-purple-500/20 font-medium">
                              {fw.framework}
                              {fw.project_count > 1 && <span className="text-white/30 ml-1 text-[10px]">{fw.project_count} projects</span>}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* ---- EDUCATION SECTION ---- */}
              {(profile.university || profile.degree_major) && (
                <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden border border-white/5">
                  <div className="px-5 py-3 border-b border-white/10">
                    <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">Education</span>
                  </div>
                  <div className="px-5 py-4 flex items-start gap-4">
                    <div className="w-12 h-12 rounded-lg bg-white/5 flex items-center justify-center shrink-0">
                      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M22 10v6M2 10l10-5 10 5-10 5z"/>
                        <path d="M6 12v5c0 1.1 2.7 2 6 2s6-.9 6-2v-5"/>
                      </svg>
                    </div>
                    <div>
                      {profile.university && <p className="text-sm font-bold text-white">{profile.university}</p>}
                      {profile.degree_major && <p className="text-xs text-white/50 mt-0.5">{profile.degree_major}</p>}
                      {location && <p className="text-xs text-white/40 mt-0.5">{location}</p>}
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* RIGHT SIDEBAR */}
            <div className="w-full lg:w-72 shrink-0 space-y-4 lg:sticky lg:top-24">

              {/* Portfolio Info Card */}
              <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden border border-white/5">
                <div className="px-4 py-3 border-b border-white/10">
                  <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">Portfolio Info</span>
                </div>
                <div className="px-4 py-3 space-y-2.5">
                  <div>
                    <p className="text-[10px] uppercase tracking-wider text-white/30">Title</p>
                    <p className="text-sm text-white font-medium">{portfolio.title}</p>
                  </div>
                  {portfolio.description && (
                    <div>
                      <p className="text-[10px] uppercase tracking-wider text-white/30">Description</p>
                      <p className="text-xs text-white/60">{portfolio.description}</p>
                    </div>
                  )}
                  <div className="flex justify-between text-xs">
                    <span className="text-white/30">Created</span>
                    <span className="text-white/60">{formatDate(portfolio.created_at)}</span>
                  </div>
                  {portfolio.updated_at && portfolio.updated_at !== portfolio.created_at && (
                    <div className="flex justify-between text-xs">
                      <span className="text-white/30">Updated</span>
                      <span className="text-white/60">{formatDate(portfolio.updated_at)}</span>
                    </div>
                  )}
                </div>
              </div>

              {/* Stats Card */}
              {stats && (
                <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden border border-white/5">
                  <div className="px-4 py-3 border-b border-white/10">
                    <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">Statistics</span>
                  </div>
                  <div className="px-4 py-3 space-y-2">
                    {[
                      { label: 'Projects', value: stats.total_projects },
                      { label: 'Total Files', value: stats.total_files },
                      { label: 'Code Files', value: stats.code_files_count },
                      { label: 'Lines of Code', value: stats.total_lines_of_code?.toLocaleString() },
                      { label: 'Total Commits', value: stats.total_commits },
                      { label: 'Contributors', value: stats.total_contributors },
                    ].filter(s => s.value != null && s.value !== 0).map((stat) => (
                      <div key={stat.label} className="flex justify-between text-xs">
                        <span className="text-white/40">{stat.label}</span>
                        <span className="text-white font-bold">{stat.value}</span>
                      </div>
                    ))}
                    {stats.date_range_start && (
                      <div className="pt-2 border-t border-white/5">
                        <p className="text-[10px] uppercase tracking-wider text-white/30 mb-1">Active Period</p>
                        <p className="text-xs text-white/50">
                          {new Date(stats.date_range_start).toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
                          {' — '}
                          {stats.date_range_end ? new Date(stats.date_range_end).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'Present'}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Generate Resume Card */}
              {isOwner && (
                <div className="bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-lg overflow-hidden border border-blue-500/30">
                  <div className="px-4 py-3 border-b border-blue-500/20">
                    <span className="text-[11px] uppercase tracking-widest text-blue-300 font-black">Quick Actions</span>
                  </div>
                  <div className="px-4 py-4">
                    <p className="text-xs text-white/60 mb-3">Generate a resume populated with all your portfolio projects, languages, and skills.</p>
                    <button
                      onClick={handleGenerateResume}
                      disabled={generatingResume}
                      className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg text-sm font-bold transition-all bg-blue-500 text-white hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {generatingResume ? (
                        <>
                          <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                          <span>Generating...</span>
                        </>
                      ) : (
                        <>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                            <polyline points="14 2 14 8 20 8"/>
                            <line x1="16" y1="13" x2="8" y2="13"/>
                            <line x1="16" y1="17" x2="8" y2="17"/>
                            <polyline points="10 9 9 9 8 9"/>
                          </svg>
                          <span>Generate Resume</span>
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}

              {/* Language Breakdown Bar */}
              {allLanguages.length > 0 && (
                <div className="bg-[var(--card-bg)] rounded-lg overflow-hidden border border-white/5">
                  <div className="px-4 py-3 border-b border-white/10">
                    <span className="text-[11px] uppercase tracking-widest text-white/50 font-black">Languages</span>
                  </div>
                  <div className="px-4 py-3">
                    {(() => {
                      const totalLines = allLanguages.reduce((s, l) => s + (l.lines_of_code || 0), 0);
                      const langColors = ['#4f7cf7', '#22d3ee', '#a78bfa', '#f472b6', '#fbbf24', '#34d399', '#fb923c', '#94a3b8'];
                      if (totalLines === 0) return <p className="text-white/30 text-xs">No language data available</p>;
                      return (
                        <>
                          <div className="flex w-full h-2.5 rounded-full overflow-hidden gap-0.5 mb-3">
                            {allLanguages.slice(0, 8).map((lang, i) => (
                              <div key={lang.language} style={{ width: `${(lang.lines_of_code / totalLines * 100)}%`, backgroundColor: langColors[i % langColors.length] }} className="h-full rounded-sm first:rounded-l-full last:rounded-r-full" title={`${lang.language}: ${(lang.lines_of_code / totalLines * 100).toFixed(1)}%`} />
                            ))}
                          </div>
                          <div className="space-y-1.5">
                            {allLanguages.slice(0, 8).map((lang, i) => (
                              <div key={lang.language} className="flex items-center justify-between text-xs">
                                <div className="flex items-center gap-2">
                                  <div className="w-2 h-2 rounded-full" style={{ backgroundColor: langColors[i % langColors.length] }} />
                                  <span className="text-white/60">{lang.language}</span>
                                </div>
                                <span className="text-white/40">{(lang.lines_of_code / totalLines * 100).toFixed(1)}%</span>
                              </div>
                            ))}
                          </div>
                        </>
                      );
                    })()}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
