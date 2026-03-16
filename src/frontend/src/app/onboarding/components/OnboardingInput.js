export default function OnboardingInput({
  label,
  value,
  onChange,
  placeholder,
  type = 'text',
  inputStyle,
}) {
  return (
    <div>
      <label className="block text-sm font-medium mb-2 text-white">{label}</label>
      <input
        type={type}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-3 py-2 rounded-md text-sm focus:outline-none transition-all"
        style={inputStyle}
        placeholder={placeholder}
      />
    </div>
  );
}
