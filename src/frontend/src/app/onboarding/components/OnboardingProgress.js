export default function OnboardingProgress({ step, totalSteps }) {
  return (
    <>
      <div className="flex items-center gap-2 mb-8">
        {Array.from({ length: totalSteps }, (_, i) => (
          <div
            key={i}
            className="flex-1 h-1 rounded-full transition-all"
            style={{
              background: i < step ? '#4f7cf7' : '#27272a',
            }}
          />
        ))}
      </div>

      <p className="text-xs mb-1" style={{ color: '#71717a' }}>
        Step {step} of {totalSteps}
      </p>
    </>
  );
}
