'use client';

import { useEffect, useState } from 'react';
import { useRouter, useParams } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import { getPortfolio, updatePortfolio, addProjectToPortfolio, removeProjectFromPortfolio, reorderPortfolioProjects } from '@/utils/portfolioApi';
import config from '@/config';

export default function EditPortfolioPage() {
  const router = useRouter();
  const params = useParams();
  const { isAuthenticated, token, loading: authLoading } = useAuth();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [portfolio, setPortfolio] = useState(null);
  const [allProjects, setAllProjects] = useState([]);

  // Form state
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    is_public: false,
    target_audience: '',
    tone: 'professional',
  });
  const [portfolioProjects, setPortfolioProjects] = useState([]);
  const [availableProjects, setAvailableProjects] = useState([]);

  const portfolioId = params.id;

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchData = async () => {
      try {
        // Fetch portfolio and all projects in parallel
        const [portfolioData, projectsResponse] = await Promise.all([
          getPortfolio(portfolioId, token),
          fetch(`${config.API_URL}/api/projects/`, {
            headers: { 'Authorization': `Bearer ${token}` },
          }),
        ]);

        if (!projectsResponse.ok) {
          throw new Error('Failed to fetch projects');
        }

        const projectsData = await projectsResponse.json();
        const allUserProjects = projectsData.projects || [];

        setPortfolio(portfolioData);
        setAllProjects(allUserProjects);

        // Set form data from portfolio
        setFormData({
          title: portfolioData.title || '',
          description: portfolioData.description || '',
          is_public: portfolioData.is_public || false,
          target_audience: portfolioData.target_audience || '',
          tone: portfolioData.tone || 'professional',
        });

        // Extract portfolio project IDs
        const portfolioProjectIds = new Set(
          (portfolioData.projects || []).map(pp => pp.project.id)
        );
        setPortfolioProjects(portfolioData.projects || []);

        // Filter available projects (not already in portfolio)
        setAvailableProjects(
          allUserProjects.filter(p => !portfolioProjectIds.has(p.id))
        );
      } catch (err) {
        console.error('Error fetching data:', err);
        setError(err.message || 'Failed to load portfolio');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [authLoading, isAuthenticated, token, portfolioId, router]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSave = async (regenerateSummary = false) => {
    setError('');
    setSuccess('');
    setSaving(true);

    try {
      const updateData = {
        ...formData,
        regenerate_summary: regenerateSummary,
      };

      const data = await updatePortfolio(portfolioId, updateData, token);
      setPortfolio(data.portfolio);
      setSuccess(regenerateSummary ? 'Portfolio updated and summary regenerated!' : 'Portfolio updated successfully!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      console.error('Error updating portfolio:', err);
      setError(err.message || 'Failed to update portfolio');
    } finally {
      setSaving(false);
    }
  };

  const handleAddProject = async (projectId) => {
    setError('');

    try {
      await addProjectToPortfolio(portfolioId, { project_id: projectId }, token);
      
      // Move project from available to portfolio
      const project = availableProjects.find(p => p.id === projectId);
      if (project) {
        setAvailableProjects(prev => prev.filter(p => p.id !== projectId));
        setPortfolioProjects(prev => [
          ...prev,
          { project, notes: '', featured: false, order: prev.length }
        ]);
      }
    } catch (err) {
      console.error('Error adding project:', err);
      setError(err.message || 'Failed to add project');
    }
  };

  const handleRemoveProject = async (projectId) => {
    setError('');

    try {
      await removeProjectFromPortfolio(portfolioId, projectId, token);
      
      // Move project from portfolio to available
      const portfolioProject = portfolioProjects.find(pp => pp.project.id === projectId);
      if (portfolioProject) {
        setPortfolioProjects(prev => prev.filter(pp => pp.project.id !== projectId));
        setAvailableProjects(prev => [...prev, portfolioProject.project]);
      }
    } catch (err) {
      console.error('Error removing project:', err);
      setError(err.message || 'Failed to remove project');
    }
  };

  const moveProject = async (index, direction) => {
    const newIndex = index + direction;
    if (newIndex < 0 || newIndex >= portfolioProjects.length) return;

    const newProjects = [...portfolioProjects];
    [newProjects[index], newProjects[newIndex]] = [newProjects[newIndex], newProjects[index]];
    setPortfolioProjects(newProjects);

    // Save new order to backend
    try {
      await reorderPortfolioProjects(
        portfolioId,
        newProjects.map(pp => pp.project.id),
        token
      );
    } catch (err) {
      console.error('Error reordering projects:', err);
      setError(err.message || 'Failed to save project order');
      // Revert on error
      setPortfolioProjects(portfolioProjects);
    }
  };

  if (loading) {
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

  if (!portfolio) {
    return (
      <>
        <Header />
        <div className="min-h-screen p-8">
          <div className="max-w-4xl mx-auto">
            <div className="bg-red-500/10 border border-red-500 rounded-lg p-6 text-center">
              <h2 className="text-xl font-semibold text-red-400 mb-2">Portfolio Not Found</h2>
              <p className="text-red-300 mb-4">{error || 'The portfolio could not be loaded.'}</p>
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
            <Link href={`/portfolios/${portfolioId}`} className="text-white/60 hover:text-white transition-colors text-sm">
              ← Back to Portfolio
            </Link>
          </div>

          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Edit Portfolio</h1>
            <p className="text-white/70">Update your portfolio details and manage projects</p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-green-500/10 border border-green-500 rounded-lg">
              <p className="text-green-400">{success}</p>
            </div>
          )}

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Portfolio Details */}
            <div className="lg:col-span-2 space-y-6">
              <div className="bg-[var(--card-bg)] rounded-lg p-6" style={{ border: '1px solid #27272a' }}>
                <h2 className="text-lg font-semibold text-white mb-4">Portfolio Details</h2>
                
                <div className="space-y-4">
                  {/* Title */}
                  <div>
                    <label htmlFor="title" className="block text-sm font-medium mb-2 text-white">
                      Title
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
                      disabled={saving}
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
                      disabled={saving}
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
                      disabled={saving}
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
                      disabled={saving}
                    >
                      <option value="professional">Professional</option>
                      <option value="casual">Casual</option>
                      <option value="technical">Technical</option>
                      <option value="creative">Creative</option>
                    </select>
                  </div>

                  {/* Public checkbox */}
                  <label className="flex items-center gap-3 cursor-pointer pt-2">
                    <input
                      type="checkbox"
                      name="is_public"
                      checked={formData.is_public}
                      onChange={handleInputChange}
                      className="w-4 h-4 rounded"
                      disabled={saving}
                    />
                    <span className="text-sm text-white">Make portfolio public</span>
                  </label>
                </div>

                {/* Save buttons */}
                <div className="flex items-center gap-3 mt-6 pt-4 border-t border-white/10">
                  <button
                    onClick={() => handleSave(false)}
                    disabled={saving}
                    className="px-4 py-2 rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
                    style={{ background: '#4f7cf7', color: 'white' }}
                  >
                    {saving ? 'Saving...' : 'Save Changes'}
                  </button>
                  <button
                    onClick={() => handleSave(true)}
                    disabled={saving}
                    className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors disabled:opacity-50"
                  >
                    Save & Regenerate Summary
                  </button>
                </div>
              </div>

              {/* Portfolio Projects */}
              <div className="bg-[var(--card-bg)] rounded-lg p-6" style={{ border: '1px solid #27272a' }}>
                <h2 className="text-lg font-semibold text-white mb-4">
                  Portfolio Projects ({portfolioProjects.length})
                </h2>

                {portfolioProjects.length === 0 ? (
                  <p className="text-white/50 text-sm">No projects in this portfolio. Add some from the list below.</p>
                ) : (
                  <div className="space-y-2">
                    {portfolioProjects.map((pp, index) => (
                      <div
                        key={pp.project.id}
                        className="flex items-center gap-3 p-3 bg-white/5 rounded-lg group"
                      >
                        <div className="flex flex-col gap-1">
                          <button
                            onClick={() => moveProject(index, -1)}
                            disabled={index === 0}
                            className="p-1 hover:bg-white/10 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                          >
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M18 15l-6-6-6 6"/>
                            </svg>
                          </button>
                          <button
                            onClick={() => moveProject(index, 1)}
                            disabled={index === portfolioProjects.length - 1}
                            className="p-1 hover:bg-white/10 rounded disabled:opacity-30 disabled:cursor-not-allowed"
                          >
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                              <path d="M6 9l6 6 6-6"/>
                            </svg>
                          </button>
                        </div>
                        <span className="text-white/40 text-sm font-mono w-6">#{index + 1}</span>
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-medium truncate">{pp.project.name}</p>
                          {pp.project.classification_type && (
                            <span className="text-xs text-white/50">{pp.project.classification_type}</span>
                          )}
                        </div>
                        <button
                          onClick={() => handleRemoveProject(pp.project.id)}
                          className="px-2 py-1 bg-red-500/20 hover:bg-red-500/30 text-red-300 text-xs rounded transition-colors opacity-0 group-hover:opacity-100"
                        >
                          Remove
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Available Projects */}
              <div className="bg-[var(--card-bg)] rounded-lg p-6" style={{ border: '1px solid #27272a' }}>
                <h2 className="text-lg font-semibold text-white mb-4">
                  Add Projects ({availableProjects.length} available)
                </h2>

                {availableProjects.length === 0 ? (
                  <p className="text-white/50 text-sm">
                    All your projects are already in this portfolio.
                  </p>
                ) : (
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {availableProjects.map((project) => (
                      <div
                        key={project.id}
                        className="flex items-center justify-between gap-3 p-3 bg-white/5 hover:bg-white/10 rounded-lg transition-colors"
                      >
                        <div className="flex-1 min-w-0">
                          <p className="text-white font-medium truncate">{project.name}</p>
                          {project.classification_type && (
                            <span className="text-xs text-white/50">{project.classification_type}</span>
                          )}
                        </div>
                        <button
                          onClick={() => handleAddProject(project.id)}
                          className="px-3 py-1.5 bg-blue-500/20 hover:bg-blue-500/30 text-blue-300 text-xs rounded transition-colors"
                        >
                          Add
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-[var(--card-bg)] rounded-lg p-6 sticky top-8" style={{ border: '1px solid #27272a' }}>
                <h3 className="text-lg font-semibold text-white mb-4">Current Summary</h3>
                
                {portfolio.summary ? (
                  <div className="text-white/70 text-sm whitespace-pre-wrap mb-4 max-h-64 overflow-y-auto">
                    {portfolio.summary}
                  </div>
                ) : (
                  <p className="text-white/50 text-sm italic mb-4">
                    No summary generated yet.
                  </p>
                )}

                {portfolio.summary_generated_at && (
                  <p className="text-white/40 text-xs mb-4">
                    Last generated: {new Date(portfolio.summary_generated_at).toLocaleDateString()}
                  </p>
                )}

                <div className="pt-4 border-t border-white/10">
                  <Link
                    href={`/portfolios/${portfolioId}`}
                    className="block w-full py-2 px-4 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium text-center transition-colors"
                  >
                    View Portfolio
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
