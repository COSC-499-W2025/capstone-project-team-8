import OnboardingInput from '../components/OnboardingInput';
import OnboardingTextarea from '../components/OnboardingTextarea';

export default function PersonalInfoStep({ form, update, inputStyle }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-2">Tell us about yourself</h1>
      <p className="mb-8" style={{ color: '#a1a1aa' }}>
        This helps us personalize your portfolio and resumes.
      </p>
      <div className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <OnboardingInput
            label="First Name"
            value={form.first_name}
            onChange={(value) => update('first_name', value)}
            placeholder="John"
            inputStyle={inputStyle}
          />
          <OnboardingInput
            label="Last Name"
            value={form.last_name}
            onChange={(value) => update('last_name', value)}
            placeholder="Doe"
            inputStyle={inputStyle}
          />
        </div>
        <OnboardingTextarea
          label="Bio"
          value={form.bio}
          onChange={(value) => update('bio', value)}
          placeholder="A short bio about yourself..."
          inputStyle={inputStyle}
        />
      </div>
    </div>
  );
}
