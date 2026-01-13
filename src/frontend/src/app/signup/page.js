'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/AuthContext';
import { signup } from '@/utils/api';
import { initializeButtons } from '@/utils/buttonAnimation';

export default function SignupPage() {
  const router = useRouter();
  const { login: authLogin } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
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
      if (!username || !email || !password || !confirmPassword) {
        throw new Error('Please fill in all fields');
      }

      if (password !== confirmPassword) {
        throw new Error('Passwords do not match');
      }

      if (password.length < 8) {
        throw new Error('Password must be at least 8 characters');
      }

      const data = await signup(username, password, email, confirmPassword);
      authLogin(data.access, data.refresh);
      router.push('/dashboard');
    } catch (err) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-primary flex items-center justify-center p-8">
      <div className="max-w-md w-full fade-in">
        <div className="glow-box rounded-lg p-8">
          <h1 className="text-3xl font-bold mb-2 text-primary">Sign Up</h1>
          <p className="mb-8 text-primary">Create a new account</p>

          {error && (
            <div className="mb-4 p-4 rounded-lg" style={{ background: 'rgba(220, 38, 38, 0.1)', borderLeft: '3px solid #dc2626' }}>
              <p style={{ color: '#ff6b6b' }}>{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="username" className="block text-sm font-medium mb-1 text-primary" style={{ fontFamily: 'Lato, sans-serif' }}>
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
                placeholder="Choose a username"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium mb-1 text-primary" style={{ fontFamily: 'Lato, sans-serif' }}>
                Email
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-900"
                style={{ 
                  background: 'rgba(135, 251, 255, 0.1)',
                  border: '1px solid rgba(135, 251, 255, 0.2)',
                  color: 'white'
                }}
                placeholder="Enter your email"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium mb-1 text-primary" style={{ fontFamily: 'Lato, sans-serif' }}>
                Password
              </label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-900"
                style={{ 
                  background: 'rgba(135, 251, 255, 0.1)',
                  border: '1px solid rgba(135, 251, 255, 0.2)',
                  color: 'white'
                }}
                placeholder="Enter your password (min 8 chars)"
                disabled={loading}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium mb-1 text-primary" style={{ fontFamily: 'Lato, sans-serif' }}>
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className="w-full px-4 py-2 rounded-lg focus:outline-none focus:ring-2 transition-all text-gray-900"
                style={{ 
                  background: 'rgba(135, 251, 255, 0.1)',
                  border: '1px solid rgba(135, 251, 255, 0.2)',
                  color: 'white'
                }}
                placeholder="Confirm your password"
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
              <span className="button__label">{loading ? 'Creating account...' : 'Sign Up'}</span>
            </button>
          </form>

          <div className="mt-6 pt-6" style={{ borderTop: '1px solid rgba(255, 255, 255, 0.1)' }}>
            <p className="text-center text-primary">
              Already have an account?{' '}
              <Link href="/login" className="font-semibold transition-colors text-primary" style={{ textDecoration: 'underline' }}>
                Login
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
