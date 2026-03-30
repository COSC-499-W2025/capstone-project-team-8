'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';

const footerLinks = [
  {
    heading: 'Product',
    links: [
      { label: 'Features', href: '#features' },
      { label: 'How It Works', href: '#how-it-works' },
      { label: 'FAQ', href: '#faq' },
    ],
  },
  {
    heading: 'Account',
    links: [
      { label: 'Login', href: '/login' },
      { label: 'Sign Up', href: '/signup' },
      { label: 'Dashboard', href: '/dashboard' },
    ],
  },
  {
    heading: 'Project',
    links: [
      { label: 'COSC 499 Capstone', href: '#' },
      { label: 'Team 8', href: '#' },
    ],
  },
];

export default function LandingFooter() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      whileInView={{ opacity: 1 }}
      viewport={{ once: true }}
      transition={{ duration: 0.5 }}
      style={{ background: '#050508', borderTop: '1px solid rgba(255,255,255,0.04)' }}
    >
      <div className="max-w-6xl mx-auto px-6 py-14">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          <div className="md:col-span-1">
            <span className="text-white font-bold text-base">Portfolio Analyzer</span>
            <p className="text-sm mt-3 leading-relaxed max-w-[240px]" style={{ color: '#d4d4d8' }}>
              A capstone project by Team 8 for COSC 499. An AI-powered portfolio builder for young professionals.
            </p>
          </div>

          {footerLinks.map((col) => (
            <div key={col.heading}>
              <h4 className="text-sm font-semibold uppercase tracking-wider text-white mb-4">{col.heading}</h4>
              <div className="flex flex-col gap-2.5">
                {col.links.map((link) => (
                  <Link
                    key={link.label}
                    href={link.href}
                    className="text-sm no-underline transition-colors hover:text-white"
                    style={{ color: '#d4d4d8' }}
                  >
                    {link.label}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="mt-12 pt-5 flex flex-col md:flex-row justify-between items-center gap-3" style={{ borderTop: '1px solid rgba(255,255,255,0.04)' }}>
          <p className="text-xs" style={{ color: '#71717a' }}>
            &copy; {new Date().getFullYear()} Team 8 Capstone Project. All rights reserved.
          </p>
        </div>
      </div>
    </motion.footer>
  );
}
