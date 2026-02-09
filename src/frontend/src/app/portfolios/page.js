'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import { getPortfolios, deletePortfolio } from '@/utils/portfolioApi';

export default function PortfoliosPage() {
  const router = useRouter();
  const { isAuthenticated, token } = useAuth();
  const [portfolios, setPortfolios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState(null);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const fetchPortfolios = async () => {
      try {
        const data = await getPortfolios(token);
        setPortfolios(data.portfolios || []);
      } catch (err) {
        console.error('Error fetching portfolios:', err);
        setError('Failed to load portfolios');
      } finally {
        setLoading(false);
      }
    };

    fetchPortfolios();
  }, [isAuthenticated, token, router]);

  const handleDelete = async (portfolioId, portfolioTitle) => {
    if (!confirm(`Are you sure you want to delete "${portfolioTitle}"? This action cannot be undone.`)) {
      return;
    }

    setDeletingId(portfolioId);
    setError('');

    try {
      await deletePortfolio(portfolioId, token);
      setPortfolios(prev => prev.filter(p => p.id !== portfolioId));
    } catch (err) {
      console.error('Error deleting portfolio:', err);
      setError(err.message || 'Failed to delete portfolio');
    } finally {
      setDeletingId(null);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
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

  if (loading) {
    return (
      <>
        <Header />
        <div className="min-h-screen flex items-center justify-center">
          <div className="flex items-center gap-3">
            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            <p className="text-white">Loading portfolios...</p>
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
          {/* Header Section */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">My Portfolios</h1>
              <p className="text-white/70">Create and manage your professional portfolios</p>
            </div>
            <Link
              href="/portfolios/new"
              className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-semibold transition-all"
              style={{ background: '#4f7cf7', color: 'white' }}
              onMouseEnter={(e) => { e.target.style.background = '#3d6ce5'; }}
              onMouseLeave={(e) => { e.target.style.background = '#4f7cf7'; }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Create New Portfolio
            </Link>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-500/10 border border-red-500 rounded-lg">
              <p className="text-red-400">{error}</p>
            </div>
          )}

          {portfolios.length === 0 ? (
            <div className="bg-[var(--card-bg)] rounded-lg p-12 text-center" style={{ border: '1px solid #27272a' }}>
              <div className="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center" style={{ background: 'rgba(79, 124, 247, 0.1)' }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-white mb-2">No Portfolios Yet</h2>
              <p className="text-white/70 mb-6 max-w-md mx-auto">
                Create your first portfolio to showcase your best projects to potential employers or clients.
              </p>
              <Link
                href="/portfolios/new"
                className="inline-flex items-center gap-2 px-6 py-3 rounded-lg text-sm font-semibold transition-all"
                style={{ background: '#4f7cf7', color: 'white' }}
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19"></line>
                  <line x1="5" y1="12" x2="19" y2="12"></line>
                </svg>
                Create Your First Portfolio
              </Link>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {portfolios.map((portfolio) => (
                <div
                  key={portfolio.id}
                  className="bg-[var(--card-bg)] rounded-lg overflow-hidden hover:bg-white/5 transition-colors group"
                  style={{ border: '1px solid #27272a' }}
                >
                  {/* Portfolio Header */}
                  <div className="p-6">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1 min-w-0">
                        <Link href={`/portfolios/${portfolio.id}`}>
                          <h3 className="text-lg font-semibold text-white truncate hover:text-blue-400 transition-colors">
                            {portfolio.title}
                          </h3>
                        </Link>
                        <p className="text-white/60 text-sm mt-1">
                          {formatDate(portfolio.created_at)}
                        </p>
                      </div>
                      {portfolio.is_public ? (
                        <span className="shrink-0 ml-2 px-2 py-1 bg-green-500/20 text-green-300 text-xs rounded-full">
                          Public
                        </span>
                      ) : (
                        <span className="shrink-0 ml-2 px-2 py-1 bg-gray-500/20 text-gray-300 text-xs rounded-full">
                          Private
                        </span>
                      )}
                    </div>

                    {portfolio.description && (
                      <p className="text-white/70 text-sm mb-4 line-clamp-2">
                        {portfolio.description}
                      </p>
                    )}

                    {/* Stats */}
                    <div className="flex items-center gap-4 mb-4">
                      <div className="flex items-center gap-1.5 text-white/60 text-sm">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
                        </svg>
                        {portfolio.project_count || 0} project{(portfolio.project_count || 0) !== 1 ? 's' : ''}
                      </div>
                      {portfolio.tone && (
                        <span className={`px-2 py-0.5 text-xs rounded ${getToneBadgeColor(portfolio.tone)}`}>
                          {portfolio.tone}
                        </span>
                      )}
                    </div>

                    {/* AI Summary Preview */}
                    {portfolio.summary && (
                      <div className="bg-white/5 rounded-lg p-3 mb-4">
                        <p className="text-white/60 text-xs line-clamp-2">
                          {portfolio.summary}
                        </p>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center gap-2 pt-4 border-t border-white/10">
                      <Link
                        href={`/portfolios/${portfolio.id}`}
                        className="flex-1 px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium text-center transition-colors"
                      >
                        View
                      </Link>
                      <Link
                        href={`/portfolios/${portfolio.id}/edit`}
                        className="px-4 py-2 rounded-lg bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors"
                      >
                        Edit
                      </Link>
                      <button
                        onClick={() => handleDelete(portfolio.id, portfolio.title)}
                        disabled={deletingId === portfolio.id}
                        className="px-4 py-2 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 text-sm font-medium transition-colors disabled:opacity-50"
                      >
                        {deletingId === portfolio.id ? '...' : 'Delete'}
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
