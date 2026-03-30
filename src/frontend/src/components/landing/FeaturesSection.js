'use client';

import Image from 'next/image';
import { motion } from 'framer-motion';

const fadeUp = {
  hidden: { opacity: 0, y: 28 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: 'easeOut' } },
};

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.1 } },
};

const features = [
  {
    title: 'Project Planning',
    description: 'Upload ZIP files or folders containing your code. We support git repositories and all major project types.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
      </svg>
    ),
  },
  {
    title: 'AI Analysis',
    description: 'Our AI scans your codebase to detect languages, frameworks, and skills — then summarizes your contributions.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="3" /><path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
      </svg>
    ),
  },
  {
    title: 'Resume Generation',
    description: 'Create tailored, professional resumes from your analyzed projects with a single click.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" />
      </svg>
    ),
  },
  {
    title: 'Skills Timeline',
    description: 'Visualize your growth with an interactive timeline that maps every skill to when you first used it.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
      </svg>
    ),
  },
  {
    title: 'Portfolio Sharing',
    description: 'Get a unique public link to share your portfolio with recruiters, peers, or embed it anywhere.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="18" cy="5" r="3" /><circle cx="6" cy="12" r="3" /><circle cx="18" cy="19" r="3" /><line x1="8.59" y1="13.51" x2="15.42" y2="17.49" /><line x1="15.41" y1="6.51" x2="8.59" y2="10.49" />
      </svg>
    ),
  },
  {
    title: 'Quality Scoring',
    description: 'Receive an AI-generated quality score for every project, with actionable suggestions to improve.',
    icon: (
      <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
      </svg>
    ),
  },
];

export default function FeaturesSection() {
  return (
    <section id="features" className="px-6 py-28" style={{ background: '#09090b' }}>
      <div className="max-w-6xl mx-auto">
        {/* Top: Large highlight card with image + 2 small cards */}
        <motion.div
          className="grid lg:grid-cols-5 gap-5 mb-5"
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-80px' }}
        >
          {/* Large highlight card — spans 3 cols */}
          <motion.div
            variants={fadeUp}
            className="lg:col-span-3 relative rounded-2xl overflow-hidden flex flex-col"
            style={{ background: 'linear-gradient(135deg, #111318 0%, #0d0f14 100%)', border: '1px solid rgba(255,255,255,0.06)' }}
          >
            <div className="p-8 md:p-10 flex-1">
              <p className="text-xs font-medium uppercase tracking-widest mb-4" style={{ color: '#4f7cf7' }}>
                Overview
              </p>
              <h2 className="text-2xl md:text-3xl font-bold leading-tight mb-3" style={{ color: 'white' }}>
                Designed with an intuitive experience developers love.
              </h2>
              <p className="text-[15px] leading-relaxed max-w-md" style={{ color: '#d4d4d8' }}>
                Upload your projects and let our algorithm do the heavy lifting such as detecting skills, summarizing contributions, and building your portfolio automatically.
              </p>
            </div>
            <div className="relative h-[200px] overflow-hidden">
              <Image
                src="/images/demophoto.PNG"
                alt="Analytics dashboard interface"
                fill
                className="object-cover object-top"
                style={{ opacity: 0.8 }}
              />
              <div className="absolute inset-0" style={{ background: 'linear-gradient(to bottom, #111318 0%, transparent 50%)' }} />
            </div>
          </motion.div>

          {/* Two stacked cards on the right — spans 2 cols */}
          <div className="lg:col-span-2 flex flex-col gap-5">
            <motion.div
              variants={fadeUp}
              className="flex-1 rounded-2xl overflow-hidden"
              style={{ background: '#111318', border: '1px solid rgba(255,255,255,0.06)' }}
            >
              <div className="relative h-[100px] overflow-hidden">
                <Image
                  src="https://images.unsplash.com/photo-1555066931-4365d14bab8c?w=600&q=80"
                  alt="Code editor with syntax highlighting"
                  fill
                  className="object-cover"
                  style={{ opacity: 0.4 }}
                />
                <div className="absolute inset-0" style={{ background: 'linear-gradient(to top, #111318, transparent)' }} />
              </div>
              <div className="p-6">
                <h3 className="text-[15px] font-semibold mb-1.5" style={{ color: 'white' }}>Easy Integration</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#d4d4d8' }}>
                  Works with any project structure! You can just drag and drop your files or paste a repository link.
                </p>
              </div>
            </motion.div>

            <motion.div
              variants={fadeUp}
              className="flex-1 rounded-2xl overflow-hidden"
              style={{ background: '#111318', border: '1px solid rgba(255,255,255,0.06)' }}
            >
              <div className="relative h-[100px] overflow-hidden">
                <Image
                  src="https://images.unsplash.com/photo-1695668548342-c0c1ad479aee?w=800&q=80"
                  alt="A rack of servers in a server room"
                  fill
                  className="object-cover"
                  style={{ opacity: 0.4 }}
                />
                <div className="absolute inset-0" style={{ background: 'linear-gradient(to top, #111318, transparent)' }} />
              </div>
              <div className="p-6">
                <h3 className="text-[15px] font-semibold mb-1.5" style={{ color: 'white' }}>Secure & Private</h3>
                <p className="text-sm leading-relaxed" style={{ color: '#d4d4d8' }}>
                  Your code is processed securely and never shared. You control portfolio visibility.
                </p>
              </div>
            </motion.div>
          </div>
        </motion.div>

        {/* Section header */}
        <motion.div
          className="text-center mt-24 mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl md:text-3xl font-bold mb-3" style={{ color: 'white' }}>
            Everything you need to showcase your work
          </h2>
          <p className="text-[15px] max-w-md mx-auto" style={{ color: '#d4d4d8' }}>
            Analyze, generate, and share all from one place.
          </p>
        </motion.div>

        {/* 6-card grid */}
        <motion.div
          className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4"
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
        >
          {features.map((f) => (
            <motion.div
              key={f.title}
              variants={fadeUp}
              className="group rounded-2xl p-6 transition-all duration-300"
              style={{ background: '#111318', border: '1px solid rgba(255,255,255,0.04)' }}
              whileHover={{ borderColor: 'rgba(79,124,247,0.2)', y: -2 }}
            >
              <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-4" style={{ background: 'rgba(79,124,247,0.06)' }}>
                {f.icon}
              </div>
              <h3 className="text-[15px] font-semibold mb-1.5" style={{ color: 'white' }}>{f.title}</h3>
              <p className="text-sm leading-relaxed" style={{ color: '#d4d4d8' }}>{f.description}</p>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
