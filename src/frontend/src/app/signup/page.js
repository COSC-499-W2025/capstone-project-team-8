'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import { useAuth } from '@/context/AuthContext';
import { signup } from '@/utils/api';
import { initializeButtons } from '@/utils/buttonAnimation';

export default function SignupPage() {
  const router = useRouter();
  const { login: authLogin, isAuthenticated, loading: authLoading } = useAuth();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!authLoading && isAuthenticated) {
      router.push('/dashboard');
      return;
    }
    initializeButtons();
  }, [authLoading, isAuthenticated, router]);

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
      router.push('/onboarding');
    } catch (err) {
      setError(err.message || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side - Signup form */}
      <div className="w-full lg:w-1/2 flex flex-col" style={{ background: '#09090b' }}>

        {/* Form area */}
        <div className="flex-1 flex items-center justify-center px-8 pb-8">
          <div className="w-full max-w-sm">
            <h1 className="text-2xl font-semibold text-white mb-2">Create an account</h1>
            <p className="mb-8" style={{ color: '#a1a1aa' }}>
              Enter your details below to create your account
            </p>

            {error && (
              <div className="mb-4 px-4 py-3 rounded-md" style={{ background: 'rgba(220, 38, 38, 0.15)', border: '1px solid rgba(220, 38, 38, 0.3)' }}>
                <p className="text-sm" style={{ color: '#fca5a5' }}>{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label htmlFor="username" className="block text-sm font-medium mb-2 text-white">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all"
                  style={{
                    background: 'transparent',
                    border: '1px solid #27272a',
                    color: 'white',
                  }}
                  placeholder="Choose a username"
                  disabled={loading}
                />
              </div>

              <div>
                <label htmlFor="email" className="block text-sm font-medium mb-2 text-white">
                  Email
                </label>
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all"
                  style={{
                    background: 'transparent',
                    border: '1px solid #27272a',
                    color: 'white',
                  }}
                  placeholder="m@example.com"
                  disabled={loading}
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-sm font-medium mb-2 text-white">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all"
                  style={{
                    background: 'transparent',
                    border: '1px solid #27272a',
                    color: 'white',
                  }}
                  placeholder="Min 8 characters"
                  disabled={loading}
                />
              </div>

              <div>
                <label htmlFor="confirmPassword" className="block text-sm font-medium mb-2 text-white">
                  Confirm Password
                </label>
                <input
                  id="confirmPassword"
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all"
                  style={{
                    background: 'transparent',
                    border: '1px solid #27272a',
                    color: 'white',
                  }}
                  placeholder="Confirm your password"
                  disabled={loading}
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full py-2 px-4 rounded-md text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                style={{
                  background: '#fafafa',
                  color: '#09090b',
                }}
                onMouseEnter={(e) => { e.target.style.background = '#e4e4e7'; }}
                onMouseLeave={(e) => { e.target.style.background = '#fafafa'; }}
              >
                {loading ? 'Creating account...' : 'Sign Up'}
              </button>
            </form>

            {/* Login link */}
            <p className="text-center text-sm mt-6" style={{ color: '#a1a1aa' }}>
              Already have an account?{' '}
              <Link
                href="/login"
                className="font-medium transition-colors no-underline"
                style={{ color: 'white', textDecoration: 'underline', textUnderlineOffset: '4px' }}
              >
                Login
              </Link>
            </p>
          </div>
        </div>
      </div>

      {/* Right side - Background image */}
      <div className="hidden lg:block lg:w-1/2 relative overflow-hidden">
        <Image
          src="/images/signup.jpg"
          alt="Sign up background"
          fill
          className="object-cover"
          priority
        />
      </div>
    </div>
  );
}
