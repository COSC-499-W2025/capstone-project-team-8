'use client';

import Link from 'next/link';
import Image from 'next/image';
import { motion } from 'framer-motion';

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.12, delayChildren: 0.1 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.65, ease: [0.25, 0.46, 0.45, 0.94] } },
};

export default function HeroSection() {
  return (
    <section className="relative flex flex-col items-center text-center px-6 pt-32 pb-16 overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0">
        <div className="absolute inset-0" style={{ background: 'radial-gradient(ellipse 80% 60% at 50% 40%, rgba(79,124,247,0.12) 0%, transparent 70%)' }} />
        <div className="absolute top-[20%] right-[15%] w-[350px] h-[350px] rounded-full opacity-[0.07] blur-[100px]" style={{ background: '#7c3aed' }} />
        <div className="absolute bottom-[20%] left-[10%] w-[250px] h-[250px] rounded-full opacity-[0.06] blur-[80px]" style={{ background: '#06b6d4' }} />
        <div
          className="absolute inset-0 opacity-[0.025]"
          style={{
            backgroundImage: 'linear-gradient(rgba(255,255,255,0.08) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.08) 1px, transparent 1px)',
            backgroundSize: '64px 64px',
          }}
        />
      </div>

      <motion.div
        className="relative z-10 max-w-3xl mx-auto"
        variants={stagger}
        initial="hidden"
        animate="visible"
      >
        <motion.div variants={fadeUp} className="mb-6">
          <span
            className="inline-block px-4 py-1.5 rounded-full text-[11px] font-medium uppercase tracking-widest"
            style={{ background: 'rgba(79,124,247,0.06)', color: '#7ba4f7', border: '1px solid rgba(79,124,247,0.1)' }}
          >
            AI-Powered Portfolio Analysis
          </span>
        </motion.div>

        <motion.h1
          variants={fadeUp}
          className="text-[clamp(2.5rem,6vw,4.5rem)] font-bold leading-[1.08] tracking-tight mb-6"
          style={{ color: 'white' }}
        >
          Build a professional portfolio{' '}
          <span style={{ color: '#4f7cf7' }}>in a few clicks.</span>
        </motion.h1>

        <motion.p
          variants={fadeUp}
          className="text-base md:text-lg mb-10 max-w-xl mx-auto leading-relaxed"
          style={{ color: '#d4d4d8' }}
        >
          Upload your projects, get intelligent analysis, and generate professional
          portfolios and resumes.
        </motion.p>

        <motion.div
          variants={fadeUp}
          className="flex flex-col sm:flex-row items-center justify-center gap-3"
        >
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
          <a
            href="#how-it-works"
            className="px-7 py-3 rounded-full text-sm font-semibold no-underline transition-all hover:bg-white/[0.04]"
            style={{ color: 'white', border: '1px solid rgba(255,255,255,0.1)' }}
          >
            See How It Works
          </a>
        </motion.div>
      </motion.div>
    </section>
  );
}
