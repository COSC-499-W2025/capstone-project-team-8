'use client';

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';

export default function CTASection() {
  return (
    <section className="px-6 py-28" style={{ background: '#050508' }}>
      <motion.div
        className="relative max-w-5xl mx-auto text-center py-20 px-8 rounded-3xl overflow-hidden"
        initial={{ opacity: 0, y: 30 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        transition={{ duration: 0.6, ease: 'easeOut' }}
      >
        {/* Background image */}
        <Image
          src="https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80"
          alt="Technology background"
          fill
          className="object-cover"
          style={{ opacity: 0.15 }}
        />
        <div className="absolute inset-0" style={{ background: 'linear-gradient(135deg, rgba(12,16,32,0.92) 0%, rgba(10,13,21,0.95) 100%)' }} />
        <div className="absolute inset-0" style={{ border: '1px solid rgba(79,124,247,0.1)', borderRadius: '1.5rem' }} />
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[500px] h-[250px] opacity-20 blur-[100px]" style={{ background: 'radial-gradient(circle, #4f7cf7, transparent 70%)' }} />

        <div className="relative z-10">
          <h2 className="text-3xl md:text-4xl font-bold mb-4 leading-tight" style={{ color: 'white' }}>
            Build a professional portfolio{' '}
            <span style={{ color: '#4f7cf7' }}>in a few clicks.</span>
          </h2>
          <p className="text-[15px] mb-10 max-w-md mx-auto" style={{ color: '#d4d4d8' }}>
            Upload your projects, get intelligent analysis, and generate professional
            portfolios and resumes.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3">
            <Link
              href="/signup"
              className="group px-7 py-3 rounded-full text-sm font-semibold no-underline transition-all inline-flex items-center gap-2 hover:brightness-110"
              style={{ background: '#4f7cf7', color: 'white' }}
            >
              Get Started
              <svg className="w-4 h-4 transition-transform group-hover:translate-x-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14" /><path d="m12 5 7 7-7 7" />
              </svg>
            </Link>
            <Link
              href="/login"
              className="px-7 py-3 rounded-full text-sm font-semibold no-underline transition-all hover:bg-white/[0.04]"
              style={{ color: 'white', border: '1px solid rgba(255,255,255,0.1)' }}
            >
              Login to Account
            </Link>
          </div>
        </div>
      </motion.div>
    </section>
  );
}
