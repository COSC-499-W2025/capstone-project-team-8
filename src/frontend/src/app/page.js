'use client';

import Link from "next/link";
import Image from "next/image";
import LandingHeader from "@/components/LandingHeader";
import LandingFooter from "@/components/LandingFooter";

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#09090b' }}>
      <LandingHeader />

      {/* Hero Section */}
      <section className="relative flex-1 flex flex-col items-center justify-center text-center px-6 py-32 overflow-hidden">
        {/* Background image */}
        <div className="absolute inset-0 opacity-30" style={{ transform: 'rotate(0deg) scale(1.4)' }}>
          <Image
            src="/images/landing.jpg"
            alt="Background"
            fill
            className="object-cover"
            priority
          />
        </div>

        <div className="relative z-10 max-w-3xl mx-auto">
          <div
            className="inline-block px-4 py-1.5 rounded-full text-xs font-medium mb-6"
            style={{ background: 'rgba(79, 124, 247, 0.1)', color: '#7ba4f7', border: '1px solid rgba(79, 124, 247, 0.15)' }}
          >
            AI-Powered Portfolio Analysis
          </div>

          <h1
            className="text-5xl md:text-6xl font-bold mb-6 leading-tight"
            style={{ color: 'white' }}
          >
            Build a professional portfolio{' '}
            <span style={{ color: '#4f7cf7' }}>in a few clicks.</span>
          </h1>

          <p
            className="text-lg mb-10 max-w-xl mx-auto leading-relaxed"
            style={{ color: '#a1a1aa' }}
          >
            Upload your projects, get intelligent analysis, and generate professional
            portfolios and resumes.
          </p>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/signup"
              className="px-8 py-3 rounded-lg text-sm font-semibold no-underline transition-all inline-flex items-center gap-2"
              style={{ background: '#4f7cf7', color: 'white' }}
            >
              Get Started
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14" /><path d="m12 5 7 7-7 7" />
              </svg>
            </Link>
            <Link
              href="/login"
              className="px-8 py-3 rounded-lg text-sm font-semibold no-underline transition-all"
              style={{ background: 'transparent', color: 'white', border: '1px solid #27272a' }}
            >
              Login to Account
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="px-6 py-24" style={{ background: '#09090b' }}>
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4" style={{ color: 'white' }}>
              Everything you need
            </h2>
            <p className="text-base max-w-md mx-auto" style={{ color: '#a1a1aa' }}>
              Analyze, generate, and showcase your work with powerful tools.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div
              className="p-6 rounded-xl transition-all"
              style={{ background: '#18181b', border: '1px solid #27272a' }}
            >
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
                style={{ background: 'rgba(79, 124, 247, 0.1)' }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
                  <polyline points="17 8 12 3 7 8" />
                  <line x1="12" y1="3" x2="12" y2="15" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2" style={{ color: 'white' }}>Upload Projects</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#a1a1aa' }}>
                Upload ZIP files or folders containing your code. We support git repositories and all major project types.
              </p>
            </div>

            {/* Feature 2 */}
            <div
              className="p-6 rounded-xl transition-all"
              style={{ background: '#18181b', border: '1px solid #27272a' }}
            >
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
                style={{ background: 'rgba(79, 124, 247, 0.1)' }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="3" />
                  <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2" style={{ color: 'white' }}>AI Analysis</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#a1a1aa' }}>
                Our AI analyzes your codebase to extract skills, contributions, and project insights automatically.
              </p>
            </div>

            {/* Feature 3 */}
            <div
              className="p-6 rounded-xl transition-all"
              style={{ background: '#18181b', border: '1px solid #27272a' }}
            >
              <div
                className="w-10 h-10 rounded-lg flex items-center justify-center mb-4"
                style={{ background: 'rgba(79, 124, 247, 0.1)' }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                  <polyline points="14 2 14 8 20 8" />
                  <line x1="16" y1="13" x2="8" y2="13" />
                  <line x1="16" y1="17" x2="8" y2="17" />
                </svg>
              </div>
              <h3 className="text-lg font-semibold mb-2" style={{ color: 'white' }}>Generate Resumes</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#a1a1aa' }}>
                Create tailored resumes and portfolios from your analyzed projects with one click.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="px-6 py-24" style={{ background: '#0a0a0a' }}>
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold mb-4" style={{ color: 'white' }}>
              How it works
            </h2>
            <p className="text-base max-w-md mx-auto" style={{ color: '#a1a1aa' }}>
              Three simple steps to your professional portfolio.
            </p>
          </div>

          <div className="flex flex-col gap-8">
            {[
              { step: '01', title: 'Upload your code', desc: 'Drag and drop your project folder or ZIP file. We handle the rest.' },
              { step: '02', title: 'AI analyzes your work', desc: 'Our system scans your codebase, identifies technologies, and extracts key contributions.' },
              { step: '03', title: 'Get your portfolio', desc: 'Download a polished resume and portfolio showcasing your best work.' },
            ].map((item) => (
              <div
                key={item.step}
                className="flex items-start gap-6 p-6 rounded-xl"
                style={{ background: '#18181b', border: '1px solid #27272a' }}
              >
                <span className="text-2xl font-bold shrink-0" style={{ color: '#4f7cf7' }}>{item.step}</span>
                <div>
                  <h3 className="text-base font-semibold mb-1" style={{ color: 'white' }}>{item.title}</h3>
                  <p className="text-sm" style={{ color: '#a1a1aa' }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom CTA */}
          <div className="text-center mt-16">
            <Link
              href="/signup"
              className="inline-flex items-center gap-2 px-8 py-3 rounded-lg text-sm font-semibold no-underline transition-all"
              style={{ background: '#4f7cf7', color: 'white' }}
            >
              Start Building Your Portfolio
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14" /><path d="m12 5 7 7-7 7" />
              </svg>
            </Link>
          </div>
        </div>
      </section>

      <LandingFooter />
    </div>
  );
}
