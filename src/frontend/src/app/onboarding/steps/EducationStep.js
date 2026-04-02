import { useEffect } from 'react';
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

  const educations = form.educations || [];

  // Start with one empty education block if none exist
  useEffect(() => {
    if (educations.length === 0) {
      addEducation();
    }
  }, []);

  const addEducation = () => {
    update('educations', [
      ...educations,
      {
        id: Date.now() + Math.random(),
        university: '',
        degree_major: '',
        education_city: '',
        education_state: '',
        expected_graduation: '',
      }
    ]);
  };

  const updateEducation = (id, field, value) => {
    update(
      'educations',
      educations.map((edu) => (edu.id === id ? { ...edu, [field]: value } : edu))
    );
  };

  const removeEducation = (id) => {
    update('educations', educations.filter((edu) => edu.id !== id));
  };

  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-2">Education</h1>
      <p className="mb-4" style={{ color: '#a1a1aa' }}>
        Add your school info to include on your resume.
      </p>

      <div className="space-y-6">
        {educations.map((edu, index) => (
          <div key={edu.id} className="p-4 rounded-lg bg-white/5 border border-white/10 relative">
            <button
              onClick={() => removeEducation(edu.id)}
              className="absolute top-2 right-2 p-2 text-white/40 hover:text-white/80 transition"
              title="Remove"
            >
              ✕
            </button>
            <h3 className="text-sm font-medium text-white/80 mb-4 tracking-wide uppercase">
              Education #{index + 1}
            </h3>
            <div className="space-y-4">
              <OnboardingInput
                label="University / School"
                value={edu.university}
                onChange={(value) => updateEducation(edu.id, 'university', value)}
                placeholder="UBC Okanagan"
                inputStyle={inputStyle}
              />
              <OnboardingInput
                label="Degree / Major"
                value={edu.degree_major}
                onChange={(value) => updateEducation(edu.id, 'degree_major', value)}
                placeholder="Computer Science"
                inputStyle={inputStyle}
              />
              <div className="grid grid-cols-2 gap-4">
                <OnboardingInput
                  label="City"
                  value={edu.education_city}
                  onChange={(value) => updateEducation(edu.id, 'education_city', value)}
                  placeholder="Kelowna"
                  inputStyle={inputStyle}
                />
                <OnboardingInput
                  label="State / Province"
                  value={edu.education_state}
                  onChange={(value) => updateEducation(edu.id, 'education_state', value)}
                  placeholder="BC"
                  inputStyle={inputStyle}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2 text-white">Expected Graduation</label>
                <input
                  type="date"
                  value={edu.expected_graduation}
                  onChange={(e) => updateEducation(edu.id, 'expected_graduation', normalizeGraduationDate(e.target.value))}
                  onInput={(e) => updateEducation(edu.id, 'expected_graduation', normalizeGraduationDate(e.target.value))}
                  min="0001-01-01"
                  max="9999-12-31"
                  className={`w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all ${edu.expected_graduation ? 'date-input-filled' : 'date-input-empty'}`}
                  style={inputStyle}
                />
              </div>
            </div>
          </div>
        ))}
      </div>

      <button
        type="button"
        onClick={addEducation}
        className="mt-6 w-full py-3 border border-dashed border-white/20 rounded-lg text-white/60 hover:text-white hover:border-white/40 hover:bg-white/5 transition flex items-center justify-center font-medium"
      >
        + Add {educations.length > 0 ? 'Another ' : ''}Education
      </button>
    </div>
  );
}
