export default function OnboardingActions({
  step,
  totalSteps,
  loading,
  onBack,
  onNext,
  onSubmit,
}) {
  return (
    <div className="flex items-center justify-between mt-8">
      {step > 1 ? (
        <button
          onClick={onBack}
          className="px-4 py-2 rounded-md text-sm font-medium transition-all"
          style={{ color: '#a1a1aa', background: 'transparent' }}
          onMouseEnter={(e) => {
            e.target.style.color = 'white';
          }}
          onMouseLeave={(e) => {
            e.target.style.color = '#a1a1aa';
          }}
        >
          Back
        </button>
      ) : (
        <div />
      )}

      {step < totalSteps ? (
        <button
          onClick={onNext}
          className="px-6 py-2 rounded-md text-sm font-medium transition-all"
          style={{ background: '#4f7cf7', color: 'white' }}
        >
          Continue
        </button>
      ) : step === totalSteps ? (
        // For the last step (upload), show "Skip Upload" instead of "Finish"
        <button
          onClick={onSubmit}
          disabled={loading}
          className="px-6 py-2 rounded-md text-sm font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ background: '#4f7cf7', color: 'white' }}
        >
          {loading ? 'Saving...' : 'Skip Upload'}
        </button>
      ) : null}
    </div>
  );
}
