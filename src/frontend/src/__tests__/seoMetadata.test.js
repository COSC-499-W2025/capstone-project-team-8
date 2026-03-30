const path = require('path');
const fs = require('fs');

const APP_DIR = path.resolve(__dirname, '../app');

const routes = [
  { name: 'Root', layoutPath: 'layout.js', isRoot: true },
  { name: 'Dashboard', layoutPath: 'dashboard/layout.js' },
  { name: 'Login', layoutPath: 'login/layout.js' },
  { name: 'Signup', layoutPath: 'signup/layout.js' },
  { name: 'Onboarding', layoutPath: 'onboarding/layout.js' },
  { name: 'Profile', layoutPath: 'profile/layout.js' },
  { name: 'Upload', layoutPath: 'upload/layout.js' },
  { name: 'Projects', layoutPath: 'projects/layout.js' },
  { name: 'Portfolios', layoutPath: 'portfolios/layout.js' },
  { name: 'Portfolio Detail', layoutPath: 'portfolios/[id]/layout.js' },
  { name: 'Portfolio Edit', layoutPath: 'portfolios/[id]/edit/layout.js' },
  { name: 'New Portfolio', layoutPath: 'portfolios/new/layout.js' },
  { name: 'Resumes', layoutPath: 'resumes/layout.js' },
  { name: 'Resume Editor', layoutPath: 'resume/layout.js' },
  { name: 'Results', layoutPath: 'results/layout.js' },
];

function extractMetadata(content) {
  const match = content.match(/export\s+const\s+metadata\s*=\s*(\{[\s\S]*?\n\};?)/);
  if (!match) return null;
  try {
    return new Function(`return ${match[1].replace(/;$/, '')}`)();
  } catch {
    return null;
  }
}

describe('SEO metadata', () => {
  routes.forEach(({ name, layoutPath, isRoot }) => {
    const fullPath = path.join(APP_DIR, layoutPath);

    test(`${name} — layout.js exists`, () => {
      expect(fs.existsSync(fullPath)).toBe(true);
    });

    test(`${name} — exports metadata with title`, () => {
      const content = fs.readFileSync(fullPath, 'utf-8');
      const metadata = extractMetadata(content);
      expect(metadata).not.toBeNull();

      if (isRoot) {
        expect(metadata.title).toBeDefined();
        expect(metadata.title.template).toContain('Portfolio Analyzer');
        expect(metadata.title.default).toBeTruthy();
      } else {
        expect(typeof metadata.title).toBe('string');
        expect(metadata.title.length).toBeGreaterThan(0);
      }
    });

    test(`${name} — exports metadata with description`, () => {
      const content = fs.readFileSync(fullPath, 'utf-8');
      const metadata = extractMetadata(content);
      expect(metadata).not.toBeNull();
      expect(typeof metadata.description).toBe('string');
      expect(metadata.description.length).toBeGreaterThan(10);
    });
  });
});
