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
    }
  }, [isAuthenticated, token, router, params.id]);

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
        <div className="max-w-4xl mx-auto">
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

          {/* Project Header */}
          <div className="bg-[var(--card-bg)] rounded-lg p-8 mb-6">
            <div className="flex items-start justify-between mb-4">
              <div>
                <h1 className="text-3xl font-bold text-white mb-2">
                  {project.name || 'Untitled Project'}
                </h1>
                {project.project_type && (
                  <span className="inline-block px-3 py-1 text-sm font-medium bg-white/10 text-white rounded">
                    {project.project_type}
                  </span>
                )}
              </div>
            </div>

            {project.description && (
              <p className="text-white/80 mb-6">{project.description}</p>
            )}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-white/60 text-sm mb-1">Created</p>
                <p className="text-white font-medium">
                  {formatDate(project.created_at)}
                </p>
              </div>
              <div>
                <p className="text-white/60 text-sm mb-1">Last Updated</p>
                <p className="text-white font-medium">
                  {formatDate(project.updated_at)}
                </p>
              </div>
              {project.file_count !== undefined && (
                <div>
                  <p className="text-white/60 text-sm mb-1">Files</p>
                  <p className="text-white font-medium">{project.file_count}</p>
                </div>
              )}
              {project.language && (
                <div>
                  <p className="text-white/60 text-sm mb-1">Language</p>
                  <p className="text-white font-medium">{project.language}</p>
                </div>
              )}
            </div>
          </div>

          {/* Project Details */}
          {project.tags && project.tags.length > 0 && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">Tags</h2>
              <div className="flex flex-wrap gap-2">
                {project.tags.map((tag, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-white/10 text-white rounded-full text-sm"
                  >
                    {tag}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Files Section */}
          {project.files && project.files.length > 0 && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6 mb-6">
              <h2 className="text-xl font-semibold text-white mb-4">
                Files ({project.files.length})
              </h2>
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {project.files.map((file, index) => (
                  <div
                    key={index}
                    className="flex items-center justify-between p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                  >
                    <div className="flex items-center space-x-3">
                      <svg
                        className="w-5 h-5 text-white/60"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                        />
                      </svg>
                      <span className="text-white">{file.name || file}</span>
                    </div>
                    {file.size && (
                      <span className="text-white/60 text-sm">
                        {(file.size / 1024).toFixed(2)} KB
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Additional Metadata */}
          {project.metadata && (
            <div className="bg-[var(--card-bg)] rounded-lg p-6">
              <h2 className="text-xl font-semibold text-white mb-4">
                Additional Information
              </h2>
              <pre className="text-white/80 text-sm overflow-x-auto">
                {JSON.stringify(project.metadata, null, 2)}
              </pre>
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
              onClick={() => {
                if (
                  confirm('Are you sure you want to delete this project? This action cannot be undone.')
                ) {
                  // TODO: Implement delete functionality
                  console.log('Delete project:', project.id);
                  router.push('/projects');
                }
              }}
              className="px-6 py-3 bg-red-500/10 text-red-400 font-semibold rounded-lg hover:bg-red-500/20 transition-colors border border-red-500/50"
            >
              Delete Project
            </button>
          </div>
        </div>
      </div>
    </>
  );
}
