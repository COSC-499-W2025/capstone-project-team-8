import OnboardingInput from '../components/OnboardingInput';

export default function OnlinePresenceStep({ form, update, inputStyle, linkedinUrlInvalid = false }) {
  return (
    <div>
      <h1 className="text-2xl font-semibold text-white mb-2">Your online presence</h1>
      <p className="mb-8" style={{ color: '#a1a1aa' }}>
        Connect your profiles so we can link them in your portfolio.
      </p>
      <div className="space-y-4">
        <OnboardingInput
          label="GitHub Username"
          value={form.github_username}
          onChange={(value) => update('github_username', value)}
          placeholder="octocat"
          inputStyle={inputStyle}
        />
        <OnboardingInput
          label="LinkedIn URL"
          value={form.linkedin_url}
          onChange={(value) => update('linkedin_url', value)}
          placeholder="https://linkedin.com/in/you"
          inputStyle={inputStyle}
        />
        {linkedinUrlInvalid && (
          <p className="text-sm" style={{ color: '#fca5a5', marginTop: '-0.5rem' }}>
            Must be a valid LinkedIn URL
          </p>
        )}
        <OnboardingInput
          label="Portfolio URL"
          value={form.portfolio_url}
          onChange={(value) => update('portfolio_url', value)}
          placeholder="https://yoursite.com"
          inputStyle={inputStyle}
        />
        <OnboardingInput
          label="Twitter / X Username"
          value={form.twitter_username}
          onChange={(value) => update('twitter_username', value)}
          placeholder="handle"
          inputStyle={inputStyle}
        />
      </div>
    </div>
  );
}
