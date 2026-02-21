'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import { updateUserProfile } from '@/utils/api';

const TOTAL_STEPS = 3;

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
      setStep(step + 1);
    }
  };

  const handleBack = () => {
    if (step > 1) {
      setStep(step - 1);
    }
  };

  const handleSubmit = async () => {
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
      router.push('/dashboard');
    } catch (err) {
      setError(err.message || 'Failed to save profile');
      setLoading(false);
    }
  };

  const inputStyle = {
    background: 'transparent',
    border: '1px solid #27272a',
    color: 'white',
  };

  const renderInput = (label, field, placeholder, type = 'text') => (
    <div>
      <label className="block text-sm font-medium mb-2 text-white">{label}</label>
      <input
        type={type}
        value={form[field]}
        onChange={(e) => update(field, e.target.value)}
        className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all"
        style={inputStyle}
        placeholder={placeholder}
      />
    </div>
  );

  const renderTextarea = (label, field, placeholder) => (
    <div>
      <label className="block text-sm font-medium mb-2 text-white">{label}</label>
      <textarea
        value={form[field]}
        onChange={(e) => update(field, e.target.value)}
        className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all resize-none"
        style={{ ...inputStyle, minHeight: '80px' }}
        placeholder={placeholder}
        rows={3}
      />
    </div>
  );

  return (
    <div
      className="min-h-screen flex items-center justify-center px-4"
      style={{ background: '#09090b' }}
    >
      <div className="w-full max-w-md">
        {/* Progress bar */}
        <div className="flex items-center gap-2 mb-8">
          {Array.from({ length: TOTAL_STEPS }, (_, i) => (
            <div
              key={i}
              className="flex-1 h-1 rounded-full transition-all"
              style={{
                background: i < step ? '#4f7cf7' : '#27272a',
              }}
            />
          ))}
        </div>

        {/* Step indicator */}
        <p className="text-xs mb-1" style={{ color: '#71717a' }}>
          Step {step} of {TOTAL_STEPS}
        </p>

        {/* Step 1: Personal Info */}
        {step === 1 && (
          <div>
            <h1 className="text-2xl font-semibold text-white mb-2">
              Tell us about yourself
            </h1>
            <p className="mb-8" style={{ color: '#a1a1aa' }}>
              This helps us personalize your portfolio and resumes.
            </p>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                {renderInput('First Name', 'first_name', 'John')}
                {renderInput('Last Name', 'last_name', 'Doe')}
              </div>
              {renderTextarea('Bio', 'bio', 'A short bio about yourself...')}
            </div>
          </div>
        )}

        {/* Step 2: Social & Links */}
        {step === 2 && (
          <div>
            <h1 className="text-2xl font-semibold text-white mb-2">
              Your online presence
            </h1>
            <p className="mb-8" style={{ color: '#a1a1aa' }}>
              Connect your profiles so we can link them in your portfolio.
            </p>
            <div className="space-y-4">
              {renderInput('GitHub Username', 'github_username', 'octocat')}
              {renderInput('LinkedIn URL', 'linkedin_url', 'https://linkedin.com/in/you')}
              {renderInput('Portfolio URL', 'portfolio_url', 'https://yoursite.com')}
              {renderInput('Twitter / X Username', 'twitter_username', 'handle')}
            </div>
          </div>
        )}

        {/* Step 3: Education */}
        {step === 3 && (
          <div>
            <h1 className="text-2xl font-semibold text-white mb-2">
              Education
            </h1>
            <p className="mb-8" style={{ color: '#a1a1aa' }}>
              Add your school info to include on your resume.
            </p>
            <div className="space-y-4">
              {renderInput('University / School', 'university', 'UBC Okanagan')}
              {renderInput('Degree / Major', 'degree_major', 'Computer Science')}
              <div className="grid grid-cols-2 gap-4">
                {renderInput('City', 'education_city', 'Kelowna')}
                {renderInput('State / Province', 'education_state', 'BC')}
              </div>
              {renderInput('Expected Graduation', 'expected_graduation', '2026-06-15', 'date')}
            </div>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="mt-4 px-4 py-3 rounded-md" style={{ background: 'rgba(220, 38, 38, 0.15)', border: '1px solid rgba(220, 38, 38, 0.3)' }}>
            <p className="text-sm" style={{ color: '#fca5a5' }}>{error}</p>
          </div>
        )}

        {/* Buttons */}
        <div className="flex items-center justify-between mt-8">
          {step > 1 ? (
            <button
              onClick={handleBack}
              className="px-4 py-2 rounded-md text-sm font-medium transition-all"
              style={{ color: '#a1a1aa', background: 'transparent' }}
              onMouseEnter={(e) => { e.target.style.color = 'white'; }}
              onMouseLeave={(e) => { e.target.style.color = '#a1a1aa'; }}
            >
              Back
            </button>
          ) : (
            <div />
          )}

          {step < TOTAL_STEPS ? (
            <button
              onClick={handleNext}
              className="px-6 py-2 rounded-md text-sm font-medium transition-all"
              style={{ background: '#4f7cf7', color: 'white' }}
            >
              Continue
            </button>
          ) : (
            <button
              onClick={handleSubmit}
              disabled={loading}
              className="px-6 py-2 rounded-md text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              style={{ background: '#4f7cf7', color: 'white' }}
            >
              {loading ? 'Saving...' : 'Finish'}
            </button>
          )}
        </div>

        {/* Skip */}
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
      </div>
    </div>
  );
}
