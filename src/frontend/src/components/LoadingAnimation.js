'use client';

import { motion } from 'framer-motion';

export default function LoadingAnimation() {
  const dotVariants = {
    hidden: { opacity: 0 },
    visible: (custom) => ({
      opacity: 1,
      transition: {
        delay: custom * 0.1,
      },
    }),
    animate: (custom) => ({
      y: [-30, 0, -30],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        repeatType: 'mirror',
        ease: 'easeInOut',
        delay: custom * 0.2,
      },
    }),
  };

  return (
    <div className="flex justify-center items-center gap-2.5">
      {[0, 1, 2].map((index) => (
        <motion.div
          key={index}
          custom={index}
          variants={dotVariants}
          initial="hidden"
          animate={['visible', 'animate']}
          className="w-5 h-5 rounded-full bg-gradient-to-r from-blue-400 to-blue-600"
          style={{ willChange: 'transform' }}
        />
      ))}
    </div>
  );
}
