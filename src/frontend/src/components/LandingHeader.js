'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';

export default function LandingHeader() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const navLinks = [
    { label: 'Features', href: '#features' },
    { label: 'How It Works', href: '#how-it-works' },
    { label: 'FAQ', href: '#faq' },
  ];

  return (
    <motion.header
      className="w-full fixed top-0 z-50 transition-all duration-300"
      style={{
        background: scrolled ? 'rgba(9, 9, 11, 0.95)' : 'transparent',
        backdropFilter: scrolled ? 'blur(16px)' : 'none',
        borderBottom: scrolled ? '1px solid rgba(255,255,255,0.04)' : '1px solid transparent',
      }}
      initial={{ y: -80 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, ease: 'easeOut' }}
    >
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link href="/" className="text-white font-bold text-lg no-underline tracking-tight">
          Portfolio Analyzer
        </Link>

        <nav className="hidden md:flex items-center gap-8">
          {navLinks.map((link) => (
            <a
              key={link.href}
              href={link.href}
              className="text-[13px] no-underline transition-colors hover:text-white"
              style={{ color: '#71717a' }}
            >
              {link.label}
            </a>
          ))}
        </nav>

        <div className="hidden md:flex items-center gap-3">
          <Link
            href="/login"
            className="text-[13px] font-medium no-underline transition-colors px-4 py-2 rounded-full hover:text-white"
            style={{ color: '#a1a1aa' }}
          >
            Login
          </Link>
          <Link
            href="/signup"
            className="text-[13px] font-medium no-underline px-5 py-2 rounded-full transition-all hover:brightness-110"
            style={{ background: '#4f7cf7', color: 'white' }}
          >
            Get Started
          </Link>
        </div>

        <button
          className="md:hidden flex flex-col gap-1.5 p-2 cursor-pointer"
          style={{ background: 'transparent', border: 'none' }}
          onClick={() => setMobileOpen((v) => !v)}
          aria-label="Toggle menu"
        >
          <span className="block w-5 h-0.5 transition-all" style={{ background: '#a1a1aa', transform: mobileOpen ? 'rotate(45deg) translateY(4px)' : 'none' }} />
          <span className="block w-5 h-0.5 transition-all" style={{ background: '#a1a1aa', opacity: mobileOpen ? 0 : 1 }} />
          <span className="block w-5 h-0.5 transition-all" style={{ background: '#a1a1aa', transform: mobileOpen ? 'rotate(-45deg) translateY(-4px)' : 'none' }} />
        </button>
      </div>

      {mobileOpen && (
        <motion.div
          className="md:hidden px-6 pb-6 flex flex-col gap-4"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          style={{ background: 'rgba(9,9,11,0.98)' }}
        >
          {navLinks.map((link) => (
            <a key={link.href} href={link.href} className="text-sm no-underline py-2" style={{ color: '#a1a1aa' }} onClick={() => setMobileOpen(false)}>
              {link.label}
            </a>
          ))}
          <div className="flex flex-col gap-2 pt-2" style={{ borderTop: '1px solid rgba(255,255,255,0.06)' }}>
            <Link href="/login" className="text-sm no-underline py-2" style={{ color: '#a1a1aa' }}>Login</Link>
            <Link href="/signup" className="text-sm font-medium no-underline px-5 py-2.5 rounded-full text-center" style={{ background: '#4f7cf7', color: 'white' }}>
              Get Started
            </Link>
          </div>
        </motion.div>
      )}
    </motion.header>
  );
}
