'use client';

import Link from 'next/link';

export default function LandingHeader() {
  return (
    <header
      className="w-full sticky top-0 z-50"
      style={{
        background: 'rgba(9, 9, 11, 0.85)',
        backdropFilter: 'blur(16px)',
        borderBottom: '1px solid #27272a',
      }}
    >
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">

        {/* Nav links */}
        <nav className="hidden md:flex items-center gap-8">
          <Link href="#features" className="text-sm no-underline transition-colors" style={{ color: '#a1a1aa' }}>
            Features
          </Link>
          <Link href="#how-it-works" className="text-sm no-underline transition-colors" style={{ color: '#a1a1aa' }}>
            How It Works
          </Link>
        </nav>

        {/* CTA */}
        <div className="flex items-center gap-3">
          <Link
            href="/login"
            className="text-sm font-medium no-underline transition-colors px-4 py-2 rounded-lg"
            style={{ color: '#a1a1aa' }}
          >
            Login
          </Link>
          <Link
            href="/signup"
            className="text-sm font-medium no-underline px-5 py-2 rounded-lg transition-all"
            style={{
              background: '#4f7cf7',
              color: 'white',
            }}
          >
            Get Started
          </Link>
        </div>
      </div>
    </header>
  );
}
