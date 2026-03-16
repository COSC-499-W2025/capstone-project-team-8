export default function OnboardingTextarea({
  label,
  value,
  onChange,
  placeholder,
  inputStyle,
}) {
  return (
    <div>
      <label className="block text-sm font-medium mb-2 text-white">{label}</label>
      <textarea
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all resize-none"
        style={{ ...inputStyle, minHeight: '80px' }}
        placeholder={placeholder}
        rows={3}
      />
    </div>
  );
}
