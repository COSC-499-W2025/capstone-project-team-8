'use client';

import { useEffect, useState, useCallback, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import { isNewProject, getNewProjects } from '@/utils/newProjectsSession';
import config from '@/config';

export default function ProjectsPage() {
  const router = useRouter();
  const { isAuthenticated, token, loading: authLoading } = useAuth();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploadingThumbnail, setUploadingThumbnail] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [thumbnailPreview, setThumbnailPreview] = useState(null);
  const [deletingProject, setDeletingProject] = useState(null);
  const [evaluations, setEvaluations] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all');
  const [sortBy, setSortBy] = useState('newest');
  const [newProjects, setNewProjects] = useState([]);

  const fetchProjects = useCallback(async (q = '') => {
    if (!token) return;
    setLoading(true);
    try {
      const url = new URL(`${config.API_URL}/api/projects/`);
      if (q) url.searchParams.set('q', q);
      const response = await fetch(url.toString(), {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      if (!response.ok) throw new Error('Failed to fetch projects');
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (err) {
      console.error('Error fetching projects:', err);
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Debounce search — wait after user stops typing before hitting the API
  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    const timer = setTimeout(() => fetchProjects(searchQuery), 500);
    return () => clearTimeout(timer);
  }, [authLoading, isAuthenticated, router, fetchProjects, searchQuery]);

  // Check sessionStorage for new projects
  useEffect(() => {
    const checkNewProjects = () => {
      const stored = getNewProjects();
      console.log('New projects from sessionStorage:', stored);
      setNewProjects(stored);
    };
    
    checkNewProjects();
    // Also check whenever we come back to the page
    window.addEventListener('focus', checkNewProjects);
    return () => window.removeEventListener('focus', checkNewProjects);
  }, []);

  // Fetch evaluations
  useEffect(() => {
    if (!isAuthenticated || !token) return;
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
        console.log('Evaluations not available');
      }
    };
    fetchEvaluations();
  }, [isAuthenticated, token]);

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

  const getEvalForProject = (projectId) => {
    return evaluations.find(e => e.project_id === projectId);
  };

  // Collect unique classification types from loaded projects for the dropdown
  const classificationTypes = useMemo(() => {
    const types = [...new Set(projects.map(p => p.classification_type).filter(Boolean))];
    return types.sort();
  }, [projects]);

  // Client-side type filter + sort (search is handled server-side via ?q=)
  const filteredProjects = useMemo(() => {
    let result = projects;
    if (typeFilter !== 'all') {
      result = result.filter(p => p.classification_type === typeFilter);
    }
    if (sortBy === 'newest') return [...result].sort((a, b) => (b.created_at || 0) - (a.created_at || 0));
    if (sortBy === 'oldest') return [...result].sort((a, b) => (a.created_at || 0) - (b.created_at || 0));
    if (sortBy === 'name') return [...result].sort((a, b) => (a.name || '').localeCompare(b.name || ''));
    if (sortBy === 'files') return [...result].sort((a, b) => (b.total_files || 0) - (a.total_files || 0));
    if (sortBy === 'grade') {
      return [...result].sort((a, b) => {
        const ea = getEvalForProject(a.id);
        const eb = getEvalForProject(b.id);
        return (eb?.overall_score || 0) - (ea?.overall_score || 0);
      });
    }
    return result;
  }, [projects, typeFilter, sortBy, evaluations]);

  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A';
    // Handle both Unix timestamps (numbers) and date strings
    const date = typeof timestamp === 'number' ? new Date(timestamp * 1000) : new Date(timestamp);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleThumbnailChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setThumbnailPreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleDeleteProject = async (projectId, projectName) => {
    if (!confirm(`Are you sure you want to delete "${projectName}"? This action cannot be undone.`)) {
      return;
    }

    setDeletingProject(projectId);
    setError('');

    try {
      const response = await fetch(`${config.API_URL}/api/projects/${projectId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete project');
      }

      // Remove project from state
      setProjects(prev => prev.filter(p => p.id !== projectId));
    } catch (err) {
      console.error('Error deleting project:', err);
      setError(err.message || 'Failed to delete project');
    } finally {
      setDeletingProject(null);
    }
  };

  const handleThumbnailUpload = async (projectId) => {
    const fileInput = document.querySelector(`input[type="file"][data-project-id="${projectId}"]`);
    const file = fileInput?.files?.[0];

    if (!file) {
      setError('Please select an image');
      return;
    }

    setUploadingThumbnail(projectId);
    setError('');

    try {
      const formData = new FormData();
      formData.append('thumbnail', file);

      const response = await fetch(`${config.API_URL}/api/projects/${projectId}/thumbnail/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        const text = await response.text();
        let errorMessage = 'Failed to upload thumbnail';
        try {
          const errorData = JSON.parse(text);
          errorMessage = errorData.detail || errorMessage;
        } catch (e) {
          if (text.includes('<!DOCTYPE') || text.includes('<html')) {
            errorMessage = 'API endpoint not found';
          }
        }
        throw new Error(errorMessage);
      }

      const data = await response.json();
      // Update project in list with new thumbnail
      setProjects(prev => prev.map(p => 
        p.id === projectId ? { ...p, thumbnail_url: data.project.thumbnail_url } : p
      ));
      setSelectedProject(null);
      setThumbnailPreview(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploadingThumbnail(null);
    }
  };

  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <p className="text-white">Loading projects...</p>
        </div>
      </>
    );
  }

  return (
    <>
      <Header />
      <div className="min-h-screen p-8">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-white mb-1">Previous Projects</h1>
            <p className="text-white/70">View and manage all your uploaded projects</p>
          </div>

          {/* Search + Filter bar */}
          <div className="flex flex-col sm:flex-row gap-3 mb-6">
            {/* Search input */}
            <div className="relative flex-1">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 text-white/30" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              <input
                type="text"
                placeholder="Search projects..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-9 pr-4 py-2 rounded-lg bg-[var(--card-bg)] border border-white/10 text-white placeholder-white/30 text-sm focus:outline-none focus:border-white/30 transition-colors"
              />
              {searchQuery && (
                <button onClick={() => setSearchQuery('')} className="absolute right-3 top-1/2 -translate-y-1/2 text-white/30 hover:text-white/60 transition-colors">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 6 6 18M6 6l12 12"/></svg>
                </button>
              )}
            </div>

            {/* Type filter */}
            <select
              value={typeFilter}
              onChange={e => setTypeFilter(e.target.value)}
              className="px-3 py-2 rounded-lg border border-white/10 text-sm focus:outline-none focus:border-white/30 transition-colors"
              style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}
            >
              <option value="all" style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}>All Types</option>
              {classificationTypes.map(t => (
                <option key={t} value={t} style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>
              ))}
            </select>

            {/* Sort */}
            <select
              value={sortBy}
              onChange={e => setSortBy(e.target.value)}
              className="px-3 py-2 rounded-lg border border-white/10 text-sm focus:outline-none focus:border-white/30 transition-colors"
              style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}
            >
              <option value="newest" style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}>Newest First</option>
              <option value="oldest" style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}>Oldest First</option>
              <option value="name" style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}>Name A–Z</option>
              <option value="files" style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}>Most Files</option>
              <option value="grade" style={{ backgroundColor: '#1a1a2e', color: '#ffffff' }}>Highest Grade</option>
            </select>
          </div>

          {/* Result count */}
          {!loading && projects.length > 0 && (
            <p className="text-white/40 text-xs mb-4">
              {filteredProjects.length === projects.length
                ? `${projects.length} project${projects.length !== 1 ? 's' : ''}`
                : `${filteredProjects.length} of ${projects.length} projects`}
            </p>
          )}

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {projects.length === 0 && !loading ? (
            <div className="bg-[var(--card-bg)] rounded-lg p-12 text-center">
              <div className="text-6xl mb-4">📁</div>
              <h2 className="text-2xl font-semibold text-white mb-2">No Projects Yet</h2>
              <p className="text-white/70 mb-6">Start by uploading your first project</p>
              <Link
                href="/upload"
                className="inline-block px-6 py-3 font-semibold rounded-lg hover:opacity-90 transition-opacity text-white"
                style={{ background: '#4f7cf7' }}
              >
                Upload Project
              </Link>
            </div>
          ) : filteredProjects.length === 0 && !loading ? (
            <div className="bg-[var(--card-bg)] rounded-lg p-10 text-center">
              <svg className="mx-auto mb-3 text-white/20" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/></svg>
              <p className="text-white/60 text-sm">No projects match your search</p>
              <button onClick={() => { setSearchQuery(''); setTypeFilter('all'); }} className="mt-3 text-blue-400 text-xs hover:underline">Clear filters</button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {filteredProjects.map((project) => (
                <div
                  key={project.id}
                  className="bg-[var(--card-bg)] rounded-lg overflow-hidden hover:bg-white/5 transition-colors"
                >
                  {/* Project Thumbnail */}
                  <div className="relative h-40 bg-gradient-to-br from-blue-500/20 to-purple-500/20">
                    {project.thumbnail_url ? (
                      <img
                        src={project.thumbnail_url}
                        alt={project.name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <span className="text-4xl">📁</span>
                      </div>
                    )}
                    {/* Grade Badge */}
                    {getEvalForProject(project.id) && (
                      <div className={`absolute top-2 right-2 px-2 py-1 rounded text-xs font-bold border ${getGradeColor(getEvalForProject(project.id).overall_score)}`}>
                        {getGrade(getEvalForProject(project.id).overall_score)} · {getEvalForProject(project.id).overall_score.toFixed(0)}%
                      </div>
                    )}
                    {/* New Badge */}
                    {newProjects.includes(parseInt(project.id, 10)) && (
                      <div className="absolute top-2 left-2 px-3 py-1 rounded text-xs font-bold bg-gradient-to-r from-green-500 to-emerald-500 text-white border border-green-400/50">
                        ✨ New
                      </div>
                    )}
                    <button
                      onClick={() => {
                        setSelectedProject(project.id);
                        setThumbnailPreview(project.thumbnail_url || null);
                      }}
                      className="absolute top-2 right-2 px-3 py-1 text-white text-xs font-medium rounded transition-colors"
                      style={{ background: '#4f7cf7' }}
                    >
                      {project.thumbnail_url ? 'Change' : 'Add'} Thumbnail
                    </button>
                  </div>

                  {/* Project Content */}
                  <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <h3 className="text-lg font-semibold text-white mb-1 truncate">
                        {project.name || 'Untitled Project'}
                      </h3>
                      {project.project_type && (
                        <span className="inline-block px-2 py-1 text-xs font-medium bg-white/10 text-white rounded">
                          {project.project_type}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Quality Score Bar */}
                  {getEvalForProject(project.id) && (() => {
                    const ev = getEvalForProject(project.id);
                    return (
                      <div className="mb-3">
                        <div className="flex justify-between items-center mb-1">
                          <span className="text-white/50 text-xs">Quality Score</span>
                          <span className="text-white/80 text-xs font-semibold">{ev.overall_score.toFixed(0)}%</span>
                        </div>
                        <div className="w-full bg-white/10 rounded-full h-1.5">
                          <div
                            className={`h-1.5 rounded-full transition-all ${getBarColor(ev.overall_score)}`}
                            style={{ width: `${Math.min(ev.overall_score, 100)}%` }}
                          />
                        </div>
                      </div>
                    );
                  })()}

                  {project.description && (
                    <p className="text-white/70 text-sm mb-4 line-clamp-3">
                      {project.description}
                    </p>
                  )}

                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-xs text-white/60">
                      <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <span>Created: {formatDate(project.created_at)}</span>
                    </div>
                    {project.updated_at && (
                      <div className="flex items-center text-xs text-white/60">
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        <span>Updated: {formatDate(project.updated_at)}</span>
                      </div>
                    )}
                    {project.file_count !== undefined && (
                      <div className="flex items-center text-xs text-white/60">
                        <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                        <span>{project.file_count} files</span>
                      </div>
                    )}
                  </div>

                  {project.tags && project.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-4">
                      {project.tags.slice(0, 3).map((tag, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-xs bg-white/5 text-white/80 rounded"
                        >
                          {tag}
                        </span>
                      ))}
                      {project.tags.length > 3 && (
                        <span className="px-2 py-1 text-xs bg-white/5 text-white/80 rounded">
                          +{project.tags.length - 3} more
                        </span>
                      )}
                    </div>
                  )}

                  <div className="flex gap-2">
                    <Link
                      href={`/projects/${project.id}`}
                      className="flex-1 px-4 py-2 bg-white/10 text-white text-center text-sm font-medium rounded-lg hover:bg-white/20 transition-colors"
                    >
                      View Details
                    </Link>
                    <Link
                      href={`/upload?project_id=${project.id}`}
                      className="flex-1 px-4 py-2 bg-blue-500/20 text-blue-300 text-center text-sm font-medium rounded-lg hover:bg-blue-500/30 transition-colors"
                      title="Upload new files to add to this project"
                    >
                      Update
                    </Link>
                    <button
                      onClick={() => handleDeleteProject(project.id, project.name)}
                      disabled={deletingProject === project.id}
                      className="px-4 py-2 bg-red-500/10 text-red-400 text-sm font-medium rounded-lg hover:bg-red-500/20 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {deletingProject === project.id ? 'Deleting...' : 'Delete'}
                    </button>
                  </div>
                </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Thumbnail Upload Modal */}
        {selectedProject && (
          <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
            <div className="bg-[var(--card-bg)] rounded-lg p-6 max-w-md w-full">
              <h2 className="text-xl font-semibold text-white mb-4">
                {projects.find(p => p.id === selectedProject)?.name}
              </h2>
              
              <div className="mb-6">
                <div className="h-40 rounded-lg bg-gradient-to-br from-blue-500/20 to-purple-500/20 flex items-center justify-center overflow-hidden mb-4">
                  {thumbnailPreview ? (
                    <img
                      src={thumbnailPreview}
                      alt="Preview"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <span className="text-4xl">📁</span>
                  )}
                </div>

                <label className="block text-white/80 text-sm font-medium mb-2">
                  Choose Image
                </label>
                <input
                  type="file"
                  data-project-id={selectedProject}
                  accept="image/*"
                  onChange={handleThumbnailChange}
                  className="w-full px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white focus:outline-none focus:border-white/30 transition-colors"
                />
                <p className="text-white/60 text-xs mt-2">Supported formats: JPG, PNG, GIF. Max size: 5MB</p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => {
                    setSelectedProject(null);
                    setThumbnailPreview(null);
                  }}
                  className="flex-1 px-4 py-2 bg-white/10 hover:bg-white/20 text-white font-medium rounded transition-colors"
                >
                  Cancel
                </button>
                <button
                  onClick={() => handleThumbnailUpload(selectedProject)}
                  disabled={uploadingThumbnail === selectedProject || !thumbnailPreview || !document.querySelector(`input[type="file"][data-project-id="${selectedProject}"]`)?.files?.length}
                  className="flex-1 px-4 py-2 disabled:opacity-50 text-white font-medium rounded transition-colors"
                  style={{ background: '#4f7cf7' }}
                >
                  {uploadingThumbnail === selectedProject ? 'Uploading...' : 'Upload'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}