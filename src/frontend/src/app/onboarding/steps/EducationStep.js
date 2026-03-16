import OnboardingInput from '../components/OnboardingInput';

export default function EducationStep({ form, update, inputStyle }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-2">Education</h1>
      <p className="mb-8" style={{ color: '#a1a1aa' }}>
        Add your school info to include on your resume.
      </p>
      <div className="space-y-4">
        <OnboardingInput
          label="University / School"
          value={form.university}
          onChange={(value) => update('university', value)}
          placeholder="UBC Okanagan"
          inputStyle={inputStyle}
        />
        <OnboardingInput
          label="Degree / Major"
          value={form.degree_major}
          onChange={(value) => update('degree_major', value)}
          placeholder="Computer Science"
          inputStyle={inputStyle}
        />
        <div className="grid grid-cols-2 gap-4">
          <OnboardingInput
            label="City"
            value={form.education_city}
            onChange={(value) => update('education_city', value)}
            placeholder="Kelowna"
            inputStyle={inputStyle}
          />
          <OnboardingInput
            label="State / Province"
            value={form.education_state}
            onChange={(value) => update('education_state', value)}
            placeholder="BC"
            inputStyle={inputStyle}
          />
        </div>
        <OnboardingInput
          label="Expected Graduation"
          type="date"
          value={form.expected_graduation}
          onChange={(value) => update('expected_graduation', value)}
          placeholder="2026-06-15"
          inputStyle={inputStyle}
        />
      </div>
    </div>
  );
}
