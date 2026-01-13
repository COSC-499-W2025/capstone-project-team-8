'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { getCurrentUser, logout as apiLogout } from '@/utils/api';

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
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-8">
        <div className="text-center">
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-gray-800">Dashboard</h1>
            <p className="text-gray-600 mt-2">
              Welcome, <span className="font-semibold">{user?.username || 'User'}</span>!
            </p>
          </div>
          <button
            onClick={handleLogout}
            className="px-6 py-2 bg-red-600 text-white font-semibold rounded-lg hover:bg-red-700 transition-colors"
          >
            Logout
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Main Content */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-800 mb-8">Portfolio Management</h2>

          {/* Upload Portfolio Card */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <Link
              href="/upload"
              className="block p-8 border-2 border-indigo-200 rounded-lg hover:border-indigo-600 hover:shadow-lg transition-all group"
            >
              <div className="text-4xl mb-4">📤</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2 group-hover:text-indigo-600">
                Upload Portfolio
              </h3>
              <p className="text-gray-600">
                Upload your project files as a ZIP archive to analyze your portfolio
              </p>
            </Link>

            {/* View Projects Card */}
            <Link
              href="/results"
              className="block p-8 border-2 border-purple-200 rounded-lg hover:border-purple-600 hover:shadow-lg transition-all group"
            >
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-semibold text-gray-800 mb-2 group-hover:text-purple-600">
                View Analysis
              </h3>
              <p className="text-gray-600">
                View the analysis results from your portfolio uploads
              </p>
            </Link>
          </div>

          {/* Profile Section */}
          <div className="mt-12 pt-8 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Profile Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600">Username</p>
                <p className="text-lg font-semibold text-gray-800">{user?.username || 'N/A'}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Email</p>
                <p className="text-lg font-semibold text-gray-800">
                  {user?.email || 'N/A'}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Account Created</p>
                <p className="text-lg font-semibold text-gray-800">
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
