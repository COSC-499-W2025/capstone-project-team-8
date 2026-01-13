'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { getCurrentUser, logout as apiLogout } from '@/utils/api';
import { initializeButtons } from '@/utils/buttonAnimation';

export default function DashboardPage() {
  const router = useRouter();
  const { isAuthenticated, token, logout, user, setCurrentUser } = useAuth();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Initialize buttons
    initializeButtons();

    // Fetch user profile
    const fetchUser = async () => {
      try {
        const data = await getCurrentUser(token);
        setCurrentUser(data.user);
      } catch (err) {
        console.log('Could not fetch user profile:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUser();
  }, [isAuthenticated, token, router, setCurrentUser]);

  const handleLogout = async () => {
    try {
      await apiLogout(token);
    } catch (err) {
      console.log('Logout error:', err);
    }
    logout();
    router.push('/');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-primary flex items-center justify-center p-8">
        <div className="text-center">
          <p className="text-text-primary">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-primary p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-primary">Dashboard</h1>
            <p className="text-primary mt-2">
              Welcome, <span className="font-semibold">{user?.username || 'User'}</span>!
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="px-6 py-2 bg-card text-primary font-semibold rounded-lg hover:opacity-80 transition-colors button-lift"
            data-block="button"
          >
            <span className="button__flair"></span>
            <span className="button__label">Logout</span>
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-card rounded-lg border border-red-500">
            <p className="text-red-400">{error}</p>
          </div>
        )}

        {/* Main Content */}
        <div className="bg-card rounded-lg p-8">
          <h2 className="text-2xl font-bold text-primary mb-8">Portfolio Management</h2>

          {/* Upload Portfolio Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Link
              href="/upload"
              className="block p-8 border border-primary rounded-lg hover:opacity-80 transition-all group"
            >
              <div className="text-4xl mb-4">📤</div>
              <h3 className="text-xl font-semibold text-primary mb-2 group-hover:opacity-80">
                Upload Portfolio
              </h3>
              <p className="text-primary">
                Upload your project files as a ZIP archive to analyze your portfolio
              </p>
            </Link>

            {/* View Projects Card */}
            <Link
              href="/results"
              className="block p-8 border border-primary rounded-lg hover:opacity-80 transition-all group"
            >
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-primary mb-2 group-hover:opacity-80">
                View Analysis
              </h3>
              <p className="text-primary">
                View the analysis results from your portfolio uploads
              </p>
            </Link>
          </div>

          {/* Profile Section */}
          <div className="mt-12 pt-8 border-t border-primary">
            <h3 className="text-lg font-semibold text-primary mb-4">Profile Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-primary opacity-75">Username</p>
                <p className="text-lg font-semibold text-primary">{user?.username || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-primary opacity-75">Email</p>
                <p className="text-lg font-semibold text-primary">
                  {user?.email || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-primary opacity-75">Account Created</p>
                <p className="text-lg font-semibold text-primary">
                  {user?.date_joined ? new Date(user.date_joined).toLocaleDateString() : 'N/A'}
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
