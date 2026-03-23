'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { updateUserProfile } from '@/utils/api';
import OnboardingProgress from './components/OnboardingProgress';
import OnboardingActions from './components/OnboardingActions';
import PersonalInfoStep from './steps/PersonalInfoStep';
import OnlinePresenceStep from './steps/OnlinePresenceStep';
import EducationStep from './steps/EducationStep';
import ProjectUploadStep from './steps/ProjectUploadStep';

const TOTAL_STEPS = 4;

export default function OnboardingPage() {
  const router = useRouter();
  const { token } = useAuth();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    bio: '',
    github_username: '',
    linkedin_url: '',
    portfolio_url: '',
    twitter_username: '',
    university: '',
    degree_major: '',
    education_city: '',
    education_state: '',
    expected_graduation: '',
  });

  const update = (field, value) => {
    setForm((prev) => ({ ...prev, [field]: value }));
  };

  const handleSkip = () => {
    router.push('/dashboard');
  };

  const handleNext = () => {
    if (step < TOTAL_STEPS) {
      // Save profile data before moving to upload step
      if (step === 3) {
        handleSubmit('next');
      } else {
        setStep(step + 1);
      }
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async (action = 'finish') => {
    setLoading(true);
    setError('');
    try {
      // Filter out empty strings
      const profileData = {};
      Object.entries(form).forEach(([key, value]) => {
        if (value.trim() !== '') {
          profileData[key] = value.trim();
        }
      });

      if (Object.keys(profileData).length > 0) {
        await updateUserProfile(profileData, token);
      }
      
      // If moving to next step (upload), don't redirect yet
      if (action === 'next') {
        setStep(step + 1);
        setLoading(false);
      } else {
        // Finishing onboarding without upload
        router.push('/dashboard');
      }
    } catch (err) {
      setError(err.message || 'Failed to save profile');
      setLoading(false);
    }
  };

  const handleUploadComplete = () => {
    // Redirect to dashboard after successful upload
    router.push('/dashboard');
  };

  const inputStyle = {
    background: 'transparent',
    border: '1px solid #27272a',
    color: 'white',
  };

  const renderStep = () => {
    if (step === 1) {
      return <PersonalInfoStep form={form} update={update} inputStyle={inputStyle} />;
    }

    if (step === 2) {
      return <OnlinePresenceStep form={form} update={update} inputStyle={inputStyle} />;
    }

    if (step === 3) {
      return <EducationStep form={form} update={update} inputStyle={inputStyle} />;
    }

    return <ProjectUploadStep token={token} onUploadComplete={handleUploadComplete} />;
  };

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: '#09090b' }}
    >
      <div className="w-full max-w-md">
        <OnboardingProgress step={step} totalSteps={TOTAL_STEPS} />
        {renderStep()}

        {/* Error */}
        {error && (
          <div className="mt-4 px-4 py-3 rounded-md" style={{ background: 'rgba(220, 38, 38, 0.15)', border: '1px solid rgba(220, 38, 38, 0.3)' }}>
            <p className="text-sm" style={{ color: '#fca5a5' }}>{error}</p>
          </div>
        )}

        <OnboardingActions
          step={step}
          totalSteps={TOTAL_STEPS}
          loading={loading}
          onBack={handleBack}
          onNext={handleNext}
          onSubmit={handleSubmit}
        />

        {/* Skip - Hidden on upload step */}
        {step !== TOTAL_STEPS && (
          <div className="text-center mt-6">
            <button
              onClick={handleSkip}
              className="text-xs transition-colors bg-transparent border-none cursor-pointer"
              style={{ color: '#52525b' }}
              onMouseEnter={(e) => { e.target.style.color = '#a1a1aa'; }}
              onMouseLeave={(e) => { e.target.style.color = '#52525b'; }}
            >
              Skip for now
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
