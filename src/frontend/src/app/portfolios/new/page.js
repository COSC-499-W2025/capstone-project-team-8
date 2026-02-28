'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import { createPortfolio } from '@/utils/portfolioApi';
import config from '@/config';

export default function NewPortfolioPage() {
  const router = useRouter();
  const { isAuthenticated, token, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [projects, setProjects] = useState([]);
  const [loadingProjects, setLoadingProjects] = useState(true);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    is_public: false,
    target_audience: '',
    tone: 'professional',
    generate_summary: true,
  });
  const [selectedProjects, setSelectedProjects] = useState(new Set());

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
        setLoadingProjects(false);
      }
    };

    fetchProjects();
  }, [authLoading, isAuthenticated, token, router]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const toggleProject = (projectId) => {
    setSelectedProjects(prev => {
      const next = new Set(prev);
      if (next.has(projectId)) {
        next.delete(projectId);
      } else {
        next.add(projectId);
      }
      return next;
    });
  };

  const selectAllProjects = () => {
    if (selectedProjects.size === projects.length) {
      setSelectedProjects(new Set());
    } else {
      setSelectedProjects(new Set(projects.map(p => p.id)));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.title.trim()) {
      setError('Please enter a portfolio title');
      return;
    }

    setLoading(true);

    try {
      const portfolioData = {
        ...formData,
        project_ids: Array.from(selectedProjects),
      };

      const data = await createPortfolio(portfolioData, token);
      router.push(`/portfolios/${data.portfolio.id}`);
    } catch (err) {
      console.error('Error creating portfolio:', err);
      setError(err.message || 'Failed to create portfolio');
    } finally {
      setLoading(false);
    }
  };

  if (loadingProjects) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <p className="text-white">Loading...</p>
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
          {/* Breadcrumb */}
          <div className="mb-6">
            <Link href="/portfolios" className="text-white/60 hover:text-white transition-colors text-sm">
              ← Back to Portfolios
            </Link>
          </div>

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Create New Portfolio</h1>
            <p className="text-white/70">
              Curate your best work into a professional portfolio
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Portfolio Details */}
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-[var(--card-bg)] rounded-lg p-6" style={{ border: '1px solid #27272a' }}>
                  <h2 className="text-lg font-semibold text-white mb-4">Portfolio Details</h2>
                  
                  <div className="space-y-4">
                    {/* Title */}
                    <div>
                      <label htmlFor="title" className="block text-sm font-medium mb-2 text-white">
                        Title <span className="text-red-400">*</span>
                      </label>
                      <input
                        id="title"
                        name="title"
                        type="text"
                        value={formData.title}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all"
                        style={{
                          background: 'transparent',
                          border: '1px solid #27272a',
                          color: 'white',
                        }}
                        placeholder="My Professional Portfolio"
                        disabled={loading}
                      />
                    </div>

                    {/* Description */}
                    <div>
                      <label htmlFor="description" className="block text-sm font-medium mb-2 text-white">
                        Description
                      </label>
                      <textarea
                        id="description"
                        name="description"
                        value={formData.description}
                        onChange={handleInputChange}
                        rows={3}
                        className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all resize-none"
                        style={{
                          background: 'transparent',
                          border: '1px solid #27272a',
                          color: 'white',
                        }}
                        placeholder="A showcase of my best work..."
                        disabled={loading}
                      />
                    </div>

                    {/* Target Audience */}
                    <div>
                      <label htmlFor="target_audience" className="block text-sm font-medium mb-2 text-white">
                        Target Audience
                      </label>
                      <input
                        id="target_audience"
                        name="target_audience"
                        type="text"
                        value={formData.target_audience}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all"
                        style={{
                          background: 'transparent',
                          border: '1px solid #27272a',
                          color: 'white',
                        }}
                        placeholder="e.g., Hiring managers, Tech recruiters"
                        disabled={loading}
                      />
                    </div>

                    {/* Tone */}
                    <div>
                      <label htmlFor="tone" className="block text-sm font-medium mb-2 text-white">
                        Tone
                      </label>
                      <select
                        id="tone"
                        name="tone"
                        value={formData.tone}
                        onChange={handleInputChange}
                        className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all cursor-pointer"
                        style={{
                          background: '#18181b',
                          border: '1px solid #27272a',
                          color: 'white',
                        }}
                        disabled={loading}
                      >
                        <option value="professional">Professional</option>
                        <option value="casual">Casual</option>
                        <option value="technical">Technical</option>
                        <option value="creative">Creative</option>
                      </select>
                    </div>

                    {/* Options */}
                    <div className="space-y-3 pt-2">
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="is_public"
                          checked={formData.is_public}
                          onChange={handleInputChange}
                          className="w-4 h-4 rounded"
                          disabled={loading}
                        />
                        <span className="text-sm text-white">Make portfolio public</span>
                      </label>
                      
                      <label className="flex items-center gap-3 cursor-pointer">
                        <input
                          type="checkbox"
                          name="generate_summary"
                          checked={formData.generate_summary}
                          onChange={handleInputChange}
                          className="w-4 h-4 rounded"
                          disabled={loading}
                        />
                        <div>
                          <span className="text-sm text-white">Generate AI summary</span>
                          <p className="text-xs text-white/50">Create a professional summary using AI based on selected projects</p>
                        </div>
                      </label>
                    </div>
                  </div>
                </div>

                {/* Select Projects */}
                <div className="bg-[var(--card-bg)] rounded-lg p-6" style={{ border: '1px solid #27272a' }}>
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-lg font-semibold text-white">
                      Select Projects ({selectedProjects.size} selected)
                    </h2>
                    {projects.length > 0 && (
                      <button
                        type="button"
                        onClick={selectAllProjects}
                        className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
                      >
                        {selectedProjects.size === projects.length ? 'Deselect All' : 'Select All'}
                      </button>
                    )}
                  </div>

                  {projects.length === 0 ? (
                    <div className="text-center py-8">
                      <p className="text-white/60 mb-4">No projects available</p>
                      <Link
                        href="/upload"
                        className="inline-block px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg transition-colors text-sm"
                      >
                        Upload a Project First
                      </Link>
                    </div>
                  ) : (
                    <div className="space-y-2 max-h-96 overflow-y-auto">
                      {projects.map((project) => (
                        <label
                          key={project.id}
                          className={`flex items-start gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                            selectedProjects.has(project.id)
                              ? 'bg-blue-500/20 border border-blue-500/30'
                              : 'bg-white/5 hover:bg-white/10 border border-transparent'
                          }`}
                        >
                          <input
                            type="checkbox"
                            checked={selectedProjects.has(project.id)}
                            onChange={() => toggleProject(project.id)}
                            className="mt-1 w-4 h-4 rounded"
                            disabled={loading}
                          />
                          <div className="flex-1 min-w-0">
                            <p className="text-white font-medium truncate">{project.name}</p>
                            {project.description && (
                              <p className="text-white/60 text-sm line-clamp-1">{project.description}</p>
                            )}
                            <div className="flex items-center gap-2 mt-1">
                              {project.classification_type && (
                                <span className="px-2 py-0.5 bg-blue-500/20 text-blue-300 text-xs rounded">
                                  {project.classification_type}
                                </span>
                              )}
                              {project.total_files > 0 && (
                                <span className="text-white/40 text-xs">{project.total_files} files</span>
                              )}
                            </div>
                          </div>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              {/* Sidebar */}
              <div className="lg:col-span-1">
                <div className="bg-[var(--card-bg)] rounded-lg p-6 sticky top-8" style={{ border: '1px solid #27272a' }}>
                  <h3 className="text-lg font-semibold text-white mb-4">Summary</h3>
                  
                  <div className="space-y-3 mb-6 text-sm">
                    <div className="flex justify-between">
                      <span className="text-white/60">Projects selected</span>
                      <span className="text-white font-medium">{selectedProjects.size}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Visibility</span>
                      <span className="text-white font-medium">
                        {formData.is_public ? 'Public' : 'Private'}
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">Tone</span>
                      <span className="text-white font-medium capitalize">{formData.tone}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-white/60">AI Summary</span>
                      <span className="text-white font-medium">
                        {formData.generate_summary ? 'Yes' : 'No'}
                      </span>
                    </div>
                  </div>

                  <button
                    type="submit"
                    disabled={loading || !formData.title.trim()}
                    className="w-full py-3 px-4 rounded-lg text-sm font-semibold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                    style={{ background: '#4f7cf7', color: 'white' }}
                  >
                    {loading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
                        Creating...
                      </>
                    ) : (
                      <>
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <line x1="12" y1="5" x2="12" y2="19"></line>
                          <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        Create Portfolio
                      </>
                    )}
                  </button>

                  <p className="text-white/40 text-xs mt-3 text-center">
                    {formData.generate_summary && selectedProjects.size > 0
                      ? 'AI will generate a summary based on selected projects'
                      : 'Add projects to enable AI summary generation'}
                  </p>
                </div>
              </div>
            </div>
          </form>
        </div>
      </div>
    </>
  );
}
