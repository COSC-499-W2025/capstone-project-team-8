'use client';

import { motion } from 'framer-motion';

const steps = [
  {
    num: '01',
    title: 'Upload your code',
    description: 'Drag and drop your project folder or ZIP file. We handle the rest.',
  },
  {
    num: '02',
    title: 'AI analyzes your work',
    description: 'Our system scans your codebase, identifies technologies, and extracts key contributions.',
  },
  {
    num: '03',
    title: 'Get your portfolio',
    description: 'Download a polished resume and portfolio showcasing your best work.',
  },
];

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.15 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.55, ease: 'easeOut' } },
};

export default function HowItWorks() {
  return (
    <section id="how-it-works" className="px-6 py-28" style={{ background: '#050508' }}>
      <div className="max-w-5xl mx-auto">
        <motion.div
          className="text-center mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl md:text-3xl font-bold mb-3" style={{ color: 'white' }}>
            How it works
          </h2>
          <p className="text-[15px] max-w-md mx-auto" style={{ color: '#d4d4d8' }}>
            Three simple steps to your professional portfolio.
          </p>
        </motion.div>

        <motion.div
          className="grid md:grid-cols-3 gap-5"
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-60px' }}
        >
          {steps.map((step, i) => (
            <motion.div
              key={step.num}
              variants={fadeUp}
              className="relative rounded-2xl p-7 flex flex-col"
              style={{ background: '#0c0e13', border: '1px solid rgba(255,255,255,0.05)' }}
            >
              <span
                className="text-[40px] font-bold leading-none mb-5"
                style={{ color: '#4f7cf7' }}
              >
                {step.num}
              </span>
              <h3 className="text-base font-semibold mb-2" style={{ color: 'white' }}>
                {step.title}
              </h3>
              <p className="text-[15px] leading-relaxed" style={{ color: '#d4d4d8' }}>
                {step.description}
              </p>

              {i < steps.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -right-3 w-6 h-px" style={{ background: 'rgba(255,255,255,0.06)' }} />
              )}
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
