'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { login } from '@/utils/api';
import { initializeButtons } from '@/utils/buttonAnimation';

export default function LoginPage() {
  const router = useRouter();
  const { login: authLogin } = useAuth();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    initializeButtons();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      if (!username || !password) {
        throw new Error('Please fill in all fields');
      }

      const data = await login(username, password);
      authLogin(data.access, data.refresh);
      router.push('/dashboard');
    } catch (err) {
      setError(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-primary flex items-center justify-center p-8">
      <div className="max-w-md w-full fade-in">
        <div className="glow-box rounded-lg p-8">
          <h1 className="text-3xl font-bold mb-2 text-primary">Login</h1>
          <p className="mb-8 text-primary">Sign in to your account</p>

          {error && (
            <div className="mb-4 p-4 rounded-lg" style={{ background: 'rgba(220, 38, 38, 0.1)', borderLeft: '3px solid #dc2626' }}>
              <p style={{ color: '#ff6b6b' }}>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium mb-1 text-primary">
                Username
              </label>
              <input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-900"
                style={{ 
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  color: 'white'
                }}
                placeholder="Enter your username"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1 text-primary">
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-900"
                style={{ 
                  background: 'rgba(255, 255, 255, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)',
                  color: 'white'
                }}
                placeholder="Enter your password"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full font-semibold button-lift disabled:opacity-50 disabled:cursor-not-allowed"
              data-block="button"
            >
              <span className="button__flair"></span>
              <span className="button__label">{loading ? 'Logging in...' : 'Login'}</span>
            </button>
          </form>

          <div className="mt-6 pt-6" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <p className="text-center text-primary">
              Don't have an account?{' '}
              <Link href="/signup" className="font-semibold transition-colors text-primary" style={{ textDecoration: 'underline' }}>
                Sign up
              </Link>
            </p>
          </div>

          <div className="mt-4">
            <Link
              href="/"
              className="text-center block text-sm transition-colors text-primary"
            >
              Back to home
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
