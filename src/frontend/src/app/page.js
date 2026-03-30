'use client';

import LandingHeader from '@/components/LandingHeader';
import LandingFooter from '@/components/LandingFooter';
import HeroSection from '@/components/landing/HeroSection';
import FeaturesSection from '@/components/landing/FeaturesSection';
import HowItWorks from '@/components/landing/HowItWorks';
import FAQSection from '@/components/landing/FAQSection';
import CTASection from '@/components/landing/CTASection';

export default function Home() {
  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#09090b' }}>
      <LandingHeader />

      <main className="pt-16">
        <HeroSection />
        <FeaturesSection />
        <HowItWorks />
        <FAQSection />
        <CTASection />
      </main>

      <LandingFooter />
    </div>
  );
}
