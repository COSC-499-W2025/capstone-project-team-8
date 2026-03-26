import OnboardingInput from '../components/OnboardingInput';

export default function EducationStep({ form, update, inputStyle }) {
  const normalizeGraduationDate = (value) => {
    if (!value) return value;
    const parts = value.split('-');
    if (parts.length !== 3) return value;

    const [year, month, day] = parts;
    if (year.length > 4) {
      return `${year.slice(0, 4)}-${month}-${day}`;
    }
    return value;
  };

  const handleGraduationChange = (e) => {
    const normalizedValue = normalizeGraduationDate(e.target.value);
    update('expected_graduation', normalizedValue);
  };

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
        <div>
          <label className="block text-sm font-medium mb-2 text-white">Expected Graduation</label>
          <input
            type="date"
            value={form.expected_graduation}
            onChange={handleGraduationChange}
            onInput={handleGraduationChange}
            min="0001-01-01"
            max="9999-12-31"
            className={`w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all ${form.expected_graduation ? 'date-input-filled' : 'date-input-empty'}`}
            style={inputStyle}
          />
        </div>
      </div>
    </div>
  );
}
