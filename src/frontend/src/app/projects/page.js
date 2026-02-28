'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
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

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchProjects = async () => {
      try {
        const response = await fetch(`${config.API_URL}/api/projects/`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch projects');
        }

        const data = await response.json();
        setProjects(data.projects || []);
      } catch (err) {
        console.error('Error fetching projects:', err);
        setError('Failed to load projects');
      } finally {
        setLoading(false);
      }
    };

    fetchProjects();
  }, [authLoading, isAuthenticated, token, router]);

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
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
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Previous Projects</h1>
            <p className="text-white/70">View and manage all your uploaded projects</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {projects.length === 0 ? (
            <div className="bg-[var(--card-bg)] rounded-lg p-12 text-center">
              <div className="text-6xl mb-4">📁</div>
              <h2 className="text-2xl font-semibold text-white mb-2">No Projects Yet</h2>
              <p className="text-white/70 mb-6">Start by uploading your first project</p>
              <Link
                href="/upload"
                className="inline-block px-6 py-3 bg-white text-[var(--card-bg)] font-semibold rounded-lg hover:opacity-80 transition-opacity"
              >
                Upload Project
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {projects.map((project) => (
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
                    <button
                      onClick={() => {
                        setSelectedProject(project.id);
                        setThumbnailPreview(project.thumbnail_url || null);
                      }}
                      className="absolute top-2 right-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white text-xs font-medium rounded transition-colors"
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
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:opacity-50 text-white font-medium rounded transition-colors"
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
