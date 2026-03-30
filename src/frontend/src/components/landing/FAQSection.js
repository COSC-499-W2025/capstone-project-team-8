'use client';

import { motion } from 'framer-motion';
import FAQItem from './FAQItem';

const faqs = [
  {
    question: 'What file types and project formats are supported?',
    answer:
      'We support ZIP files, folders. Our analyzer works with all major languages and frameworks including JavaScript, Python, Java, C++, React, Django, and many more.',
  },
  {
    question: 'How does the AI analysis work?',
    answer:
      'Our engine scans your codebase to detect languages, frameworks, and libraries. It then analyzes your code structure, identifies key contributions, and generates a comprehensive summary of your skills and experience.',
  },
  {
    question: 'Is my code kept private and secure?',
    answer:
      'Absolutely. Your uploaded code is processed securely and never shared with third parties. You control the visibility of your portfolio. You can keep it private or share it with a unique public link.',
  },
  {
    question: 'Can I customize my generated portfolio and resume?',
    answer:
      'Yes! After generation, you can edit your portfolio summary, reorder projects, adjust descriptions, and choose which skills to highlight before sharing or downloading.',
  },
  {
    question: 'Is Portfolio Analyzer free to use?',
    answer:
      'Portfolio Analyzer is a free capstone project built by Team 8. You can upload projects, generate portfolios, and share them at no cost.',
  },
];

const stagger = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.06 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 12 },
  visible: { opacity: 1, y: 0, transition: { duration: 0.35, ease: 'easeOut' } },
};

export default function FAQSection() {
  return (
    <section id="faq" className="px-6 py-28" style={{ background: '#09090b' }}>
      <div className="max-w-3xl mx-auto">
        <motion.div
          className="mb-12"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
        >
          <h2 className="text-2xl md:text-3xl font-bold mb-3" style={{ color: 'white' }}>
            Questions?{' '}
            <span style={{ color: '#a1a1aa' }}>We&apos;re here to help.</span>
          </h2>
        </motion.div>

        <motion.div
          className="flex flex-col"
          variants={stagger}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: '-40px' }}
        >
          {faqs.map((faq) => (
            <motion.div key={faq.question} variants={fadeUp}>
              <FAQItem question={faq.question} answer={faq.answer} />
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
