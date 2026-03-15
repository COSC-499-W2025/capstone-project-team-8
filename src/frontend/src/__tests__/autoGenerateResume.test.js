/**
 * Tests for autoGenerateResume utility
 *
 * Following TDD: these tests define the expected behaviour of the
 * auto-generate feature before the UI integration.
 */

import {
  scoreProject,
  selectTopProjects,
  selectTopSkills,
  buildProjectEntries,
  autoGenerateResume,
} from '@/utils/autoGenerateResume';

// ─── Fixtures ────────────────────────────────────────────────────────────────

const makeProject = (overrides = {}) => ({
  id: 1,
  name: 'Test Project',
  classification_type: 'Software',
  languages: [],
  frameworks: [],
  resume_bullet_points: [],
  created_at: '2025-06-01T00:00:00Z',
  first_commit_date: null,
  ...overrides,
});

const projectA = makeProject({
  id: 1,
  name: 'Full-Stack App',
  languages: [{ id: 1, name: 'Python' }, { id: 2, name: 'JavaScript' }],
  frameworks: [{ id: 10, name: 'React' }, { id: 11, name: 'Django' }],
  resume_bullet_points: [
    'Built a REST API serving 10k requests/day',
    'Implemented JWT authentication',
    'Designed responsive UI with React',
  ],
  created_at: '2025-09-01T00:00:00Z',
});

const projectB = makeProject({
  id: 2,
  name: 'Data Pipeline',
  languages: [{ id: 3, name: 'Python' }, { id: 4, name: 'SQL' }],
  frameworks: [{ id: 12, name: 'Pandas' }],
  resume_bullet_points: [
    'Processed 2M records with Pandas pipeline',
    'Automated ETL workflow',
  ],
  created_at: '2025-07-01T00:00:00Z',
});

const projectC = makeProject({
  id: 3,
  name: 'Old Side Project',
  languages: [{ id: 5, name: 'Java' }],
  frameworks: [],
  resume_bullet_points: ['Simple CLI tool'],
  created_at: '2020-01-01T00:00:00Z',
});

const projectD = makeProject({
  id: 4,
  name: 'Mobile App',
  languages: [{ id: 6, name: 'TypeScript' }, { id: 2, name: 'JavaScript' }],
  frameworks: [{ id: 13, name: 'React Native' }],
  resume_bullet_points: [
    'Cross-platform mobile application',
    'Push notifications integration',
    'Offline data sync',
    'Unit and integration tests',
  ],
  created_at: '2025-11-01T00:00:00Z',
});

const projectE = makeProject({
  id: 5,
  name: 'Empty Project',
  languages: [],
  frameworks: [],
  resume_bullet_points: [],
  created_at: '2025-10-01T00:00:00Z',
});

const allProjects = [projectA, projectB, projectC, projectD, projectE];

const aggregatedSkills = {
  languages: [
    { name: 'Python', project_count: 3 },
    { name: 'JavaScript', project_count: 2 },
    { name: 'TypeScript', project_count: 1 },
    { name: 'SQL', project_count: 1 },
    { name: 'Java', project_count: 1 },
  ],
  frameworks: [
    { name: 'React', project_count: 2 },
    { name: 'Django', project_count: 1 },
    { name: 'Pandas', project_count: 1 },
    { name: 'React Native', project_count: 1 },
  ],
};

const baseResumeData = {
  name: 'Jane Doe',
  email: 'jane@example.com',
  phone: '+11234567890',
  github_url: 'https://github.com/janedoe',
  portfolio_url: '',
  linkedin_url: 'https://linkedin.com/in/janedoe',
  location: 'Vancouver, BC',
  sections: {
    summary: '',
    education: [
      {
        id: 1,
        title: 'UBC',
        degree_type: 'B.Sc.',
        company: 'Computer Science',
        duration: 'Graduating 2026',
        content: '',
      },
    ],
    experience: [],
    projects: [],
    skills: [],
    certifications: [],
  },
};

// ─── scoreProject ────────────────────────────────────────────────────────────

describe('scoreProject', () => {
  test('empty project scores low', () => {
    const score = scoreProject(projectE);
    expect(score).toBeLessThan(15);
  });

  test('project with many bullets & skills scores higher', () => {
    const scoreA = scoreProject(projectA);
    const scoreE = scoreProject(projectE);
    expect(scoreA).toBeGreaterThan(scoreE);
  });

  test('more recent project gets recency bonus', () => {
    const recent = makeProject({ created_at: new Date().toISOString() });
    const old = makeProject({ created_at: '2015-01-01T00:00:00Z' });
    expect(scoreProject(recent)).toBeGreaterThan(scoreProject(old));
  });

  test('handles missing created_at gracefully', () => {
    const p = makeProject({ created_at: null });
    expect(() => scoreProject(p)).not.toThrow();
  });

  test('bullets count more than skills', () => {
    const bulletHeavy = makeProject({
      resume_bullet_points: ['a', 'b', 'c', 'd'],
      languages: [],
      created_at: null,
    });
    const skillHeavy = makeProject({
      resume_bullet_points: [],
      languages: [{ id: 1, name: 'A' }, { id: 2, name: 'B' }, { id: 3, name: 'C' }, { id: 4, name: 'D' }],
      created_at: null,
    });
    expect(scoreProject(bulletHeavy)).toBeGreaterThan(scoreProject(skillHeavy));
  });
});

// ─── selectTopProjects ───────────────────────────────────────────────────────

describe('selectTopProjects', () => {
  test('returns empty array for empty input', () => {
    expect(selectTopProjects([])).toEqual([]);
    expect(selectTopProjects(null)).toEqual([]);
    expect(selectTopProjects(undefined)).toEqual([]);
  });

  test('returns at most max projects', () => {
    const result = selectTopProjects(allProjects, 2);
    expect(result).toHaveLength(2);
  });

  test('returns all projects when fewer than max', () => {
    const result = selectTopProjects([projectA], 4);
    expect(result).toHaveLength(1);
  });

  test('best projects appear first', () => {
    const result = selectTopProjects(allProjects, 3);
    const names = result.map((p) => p.name);
    // projectE (empty) should NOT be in the top 3
    expect(names).not.toContain('Empty Project');
  });

  test('projects have a _score property', () => {
    const result = selectTopProjects(allProjects, 2);
    result.forEach((p) => {
      expect(typeof p._score).toBe('number');
    });
  });

  test('sorted in descending score order', () => {
    const result = selectTopProjects(allProjects, 5);
    for (let i = 1; i < result.length; i++) {
      expect(result[i - 1]._score).toBeGreaterThanOrEqual(result[i]._score);
    }
  });
});

// ─── selectTopSkills ─────────────────────────────────────────────────────────

describe('selectTopSkills', () => {
  test('returns empty for no projects', () => {
    expect(selectTopSkills([], null)).toEqual([]);
  });

  test('de-duplicates skills by name (case-insensitive)', () => {
    const projects = [
      makeProject({
        languages: [{ id: 1, name: 'Python' }],
        frameworks: [{ id: 10, name: 'python' }],
      }),
    ];
    const result = selectTopSkills(projects, null, 10);
    const titles = result.map((s) => s.title.toLowerCase());
    const unique = new Set(titles);
    expect(unique.size).toBe(titles.length);
  });

  test('most frequent skills appear first', () => {
    const result = selectTopSkills(allProjects, aggregatedSkills, 3);
    // Python appears in 3 projects → should be first
    expect(result[0].title.toLowerCase()).toBe('python');
  });

  test('respects max limit', () => {
    const result = selectTopSkills(allProjects, aggregatedSkills, 3);
    expect(result.length).toBeLessThanOrEqual(3);
  });

  test('each skill has id and title', () => {
    const result = selectTopSkills(allProjects, aggregatedSkills);
    result.forEach((s) => {
      expect(s).toHaveProperty('id');
      expect(s).toHaveProperty('title');
      expect(typeof s.title).toBe('string');
      expect(s.title.length).toBeGreaterThan(0);
    });
  });

  test('capitalizes skill names', () => {
    const projects = [makeProject({ languages: [{ id: 1, name: 'python' }] })];
    const result = selectTopSkills(projects, null);
    expect(result[0].title).toBe('Python');
  });

  test('works without aggregatedSkills', () => {
    const result = selectTopSkills([projectA], null);
    expect(result.length).toBeGreaterThan(0);
  });

  test('merges aggregated skills that are not in projects', () => {
    const agg = {
      languages: [{ name: 'Rust', project_count: 5 }],
      frameworks: [],
    };
    const result = selectTopSkills([], agg, 5);
    expect(result.map((s) => s.title.toLowerCase())).toContain('rust');
  });
});

// ─── buildProjectEntries ─────────────────────────────────────────────────────

describe('buildProjectEntries', () => {
  test('returns empty array for no projects', () => {
    expect(buildProjectEntries([])).toEqual([]);
    expect(buildProjectEntries(null)).toEqual([]);
  });

  test('creates entries with correct shape', () => {
    const entries = buildProjectEntries([projectA]);
    expect(entries).toHaveLength(1);
    const entry = entries[0];
    expect(entry).toHaveProperty('id');
    expect(entry).toHaveProperty('title', 'Full-Stack App');
    expect(entry).toHaveProperty('company'); // technologies
    expect(entry).toHaveProperty('duration');
    expect(entry).toHaveProperty('content');
  });

  test('limits bullet points per project', () => {
    const manyBullets = makeProject({
      resume_bullet_points: ['a', 'b', 'c', 'd', 'e', 'f', 'g'],
    });
    const entries = buildProjectEntries([manyBullets], 3);
    const bulletCount = entries[0].content.split('\n').filter(Boolean).length;
    expect(bulletCount).toBe(3);
  });

  test('formats bullets with bullet character', () => {
    const entries = buildProjectEntries([projectA]);
    const lines = entries[0].content.split('\n');
    lines.forEach((line) => {
      expect(line.startsWith('• ')).toBe(true);
    });
  });

  test('includes technologies in company field', () => {
    const entries = buildProjectEntries([projectA]);
    expect(entries[0].company).toContain('Python');
    expect(entries[0].company).toContain('React');
  });

  test('handles project with no bullet points', () => {
    const entries = buildProjectEntries([projectE]);
    expect(entries[0].content).toBe('');
  });

  test('handles project with no dates', () => {
    const p = makeProject({ created_at: null, first_commit_date: null });
    const entries = buildProjectEntries([p]);
    expect(entries[0].duration).toBe('');
  });
});

// ─── autoGenerateResume (integration) ────────────────────────────────────────

describe('autoGenerateResume', () => {
  test('returns a complete resume data object', () => {
    const result = autoGenerateResume({
      currentResumeData: baseResumeData,
      projects: allProjects,
      aggregatedSkills,
    });

    // Personal info carried through
    expect(result.name).toBe('Jane Doe');
    expect(result.email).toBe('jane@example.com');
    expect(result.phone).toBe('+11234567890');
    expect(result.location).toBe('Vancouver, BC');

    // Sections present
    expect(result.sections).toBeDefined();
    expect(result.sections.projects.length).toBeGreaterThan(0);
    expect(result.sections.skills.length).toBeGreaterThan(0);
  });

  test('preserves existing education', () => {
    const result = autoGenerateResume({
      currentResumeData: baseResumeData,
      projects: allProjects,
    });
    expect(result.sections.education).toEqual(baseResumeData.sections.education);
  });

  test('preserves existing experience', () => {
    const dataWithExp = {
      ...baseResumeData,
      sections: {
        ...baseResumeData.sections,
        experience: [{ id: 99, title: 'SWE Intern', company: 'Acme', duration: '2024', content: '• Did things' }],
      },
    };
    const result = autoGenerateResume({
      currentResumeData: dataWithExp,
      projects: allProjects,
    });
    expect(result.sections.experience).toEqual(dataWithExp.sections.experience);
  });

  test('respects custom limits', () => {
    const result = autoGenerateResume({
      currentResumeData: baseResumeData,
      projects: allProjects,
      aggregatedSkills,
      limits: { maxProjects: 1, maxSkills: 3, maxBullets: 2 },
    });
    expect(result.sections.projects).toHaveLength(1);
    expect(result.sections.skills.length).toBeLessThanOrEqual(3);
    // max 2 bullets per project
    const bulletCount = result.sections.projects[0].content.split('\n').filter(Boolean).length;
    expect(bulletCount).toBeLessThanOrEqual(2);
  });

  test('works with empty projects', () => {
    const result = autoGenerateResume({
      currentResumeData: baseResumeData,
      projects: [],
    });
    expect(result.sections.projects).toEqual([]);
    expect(result.sections.skills).toEqual([]);
    expect(result.name).toBe('Jane Doe');
  });

  test('works with no currentResumeData', () => {
    const result = autoGenerateResume({
      currentResumeData: null,
      projects: allProjects,
      aggregatedSkills,
    });
    expect(result.name).toBe('');
    expect(result.sections.projects.length).toBeGreaterThan(0);
  });

  test('auto-generated projects have all required fields', () => {
    const result = autoGenerateResume({
      currentResumeData: baseResumeData,
      projects: allProjects,
    });
    result.sections.projects.forEach((p) => {
      expect(p).toHaveProperty('id');
      expect(p).toHaveProperty('title');
      expect(p).toHaveProperty('company');
      expect(p).toHaveProperty('duration');
      expect(p).toHaveProperty('content');
    });
  });

  test('does not include empty project in top selections', () => {
    const result = autoGenerateResume({
      currentResumeData: baseResumeData,
      projects: allProjects,
      limits: { maxProjects: 3 },
    });
    const projectNames = result.sections.projects.map((p) => p.title);
    expect(projectNames).not.toContain('Empty Project');
  });

  test('skill titles are capitalized', () => {
    const result = autoGenerateResume({
      currentResumeData: baseResumeData,
      projects: allProjects,
      aggregatedSkills,
    });
    result.sections.skills.forEach((s) => {
      expect(s.title[0]).toBe(s.title[0].toUpperCase());
    });
  });
});
