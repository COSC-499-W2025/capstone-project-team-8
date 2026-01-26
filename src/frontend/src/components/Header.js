'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { useState, useEffect, useRef } from 'react';

export default function Header() {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsDropdownOpen(false);
      }
    }

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    router.push('/login');
    setIsDropdownOpen(false);
  };

  const navLinks = [
    { href: '/dashboard', label: 'Dashboard' },
    { href: '/upload', label: 'Upload' },
    { href: '/incremental-upload', label: 'Update Portfolio' },
    { href: '/resume', label: 'Build Resume' },
    { href: '/projects', label: 'Previous Projects' },
  ];

  const isActive = (href) => pathname === href || pathname.startsWith(href + '/');

  return (
    <header className="bg-[var(--card-bg)] shadow-lg sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo/Brand */}
          <Link href="/dashboard" className="text-xl font-bold text-white hover:opacity-80 transition-opacity">
            Portfolio Analyzer
          </Link>

          {/* Navigation Links */}
          <nav className="hidden md:flex items-center space-x-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  isActive(link.href)
                    ? 'bg-white/10 text-white font-semibold'
                    : 'text-white/80 hover:bg-white/5 hover:text-white'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Account Dropdown */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-white/5 transition-colors"
            >
              <div className="w-8 h-8 rounded-full bg-white/10 flex items-center justify-center overflow-hidden">
                {user?.profile_image_url ? (
                  <img 
                    src={user.profile_image_url} 
                    alt={user?.username}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <span className="text-white font-semibold text-sm">
                    {user?.username?.[0]?.toUpperCase() || 'U'}
                  </span>
                )}
              </div>
              <span className="hidden sm:block text-white">{user?.username || 'User'}</span>
              <svg
                className={`w-4 h-4 text-white transition-transform ${
                  isDropdownOpen ? 'rotate-180' : ''
                }`}
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute right-0 mt-2 w-56 bg-[var(--card-bg)] rounded-lg shadow-xl border border-white/10 overflow-hidden">
                <div className="px-4 py-3 border-b border-white/10">
                  <p className="text-sm text-white/60">Signed in as</p>
                  <p className="text-sm font-semibold text-white truncate">{user?.email || user?.username}</p>
                </div>
                
                <div className="py-2">
                  <Link
                    href="/profile"
                    onClick={() => setIsDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-white hover:bg-white/5 transition-colors"
                  >
                    Profile Settings
                  </Link>
                  <Link
                    href="/dashboard"
                    onClick={() => setIsDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-white hover:bg-white/5 transition-colors md:hidden"
                  >
                    Dashboard
                  </Link>
                  <Link
                    href="/upload"
                    onClick={() => setIsDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-white hover:bg-white/5 transition-colors md:hidden"
                  >
                    Upload
                  </Link>
                  <Link
                    href="/incremental-upload"
                    onClick={() => setIsDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-white hover:bg-white/5 transition-colors md:hidden"
                  >
                    Update Portfolio
                  </Link>
                  <Link
                    href="/results"
                    onClick={() => setIsDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-white hover:bg-white/5 transition-colors md:hidden"
                  >
                    Build Resume
                  </Link>
                  <Link
                    href="/projects"
                    onClick={() => setIsDropdownOpen(false)}
                    className="block px-4 py-2 text-sm text-white hover:bg-white/5 transition-colors md:hidden"
                  >
                    Previous Projects
                  </Link>
                </div>

                <div className="border-t border-white/10 py-2">
                  <button
                    onClick={handleLogout}
                    className="block w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-white/5 transition-colors"
                  >
                    Sign Out
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}
