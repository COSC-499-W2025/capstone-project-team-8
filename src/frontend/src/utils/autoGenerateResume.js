/**
 * Auto-Generate Resume Utility
 *
 * Analyses a user's projects and skills, then selects the best items
 * to populate a complete resume automatically.
 *
 * Selection strategy:
 *   - Projects ranked by: bullet-point count, skill diversity, recency
 *   - Skills  ranked by: frequency across projects (de-duplicated)
 *   - Top N projects included with all their bullet points
 *   - Education & personal info carried through from the existing data
 */

// ─── Defaults ────────────────────────────────────────────────────────────────

const MAX_PROJECTS = 4;
const MAX_SKILLS = 15;
const MAX_BULLETS_PER_PROJECT = 5;
const MS_PER_YEAR = 1000 * 60 * 60 * 24 * 365;

const normalizeTimestamp = (value) => {
  if (value === null || value === undefined || value === '') return null;

  const parsed = typeof value === 'number' ? new Date(value * 1000) : new Date(value);
  const time = parsed.getTime();
  return Number.isNaN(time) ? null : time;
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

/**
 * Score a single project so we can rank them.
 *   bulletWeight × bulletCount  +  skillWeight × uniqueSkillCount  +  recencyBonus
 *
 * @param {object} project – raw project from the API
 * @returns {number}
 */
export function scoreProject(project) {
  const bulletCount = (project.resume_bullet_points || []).length;
  const languageCount = (project.languages || []).length;
  const frameworkCount = (project.frameworks || []).length;
  const resumeSkillCount = (project.resume_skills || []).length;
  const skillCount = languageCount + frameworkCount;

  // Recency: projects with a more-recent created_at get a small bonus (0-10 pts)
  let recencyBonus = 0;
  const latestActivity = Math.max(
    normalizeTimestamp(project.last_updated) || 0,
    normalizeTimestamp(project.created_at) || 0,
    normalizeTimestamp(project.first_commit_date) || 0,
  );
  if (latestActivity > 0) {
    const ageMs = Date.now() - latestActivity;
    const ageYears = ageMs / MS_PER_YEAR;
    recencyBonus = Math.max(0, 10 - ageYears * 2);
  }

  return bulletCount * 3 + (skillCount + resumeSkillCount) * 2 + recencyBonus;
}

/**
 * Rank & pick the top projects.
 *
 * @param {Array} projects – all user projects
 * @param {number} max – how many to keep (default MAX_PROJECTS)
 * @returns {Array} sorted top projects (best first)
 */
export function selectTopProjects(projects, max = MAX_PROJECTS) {
  if (!Array.isArray(projects) || projects.length === 0) return [];

  return [...projects]
    .map((p) => ({ ...p, _score: scoreProject(p) }))
    .sort((a, b) => b._score - a._score)
    .slice(0, max);
}

/**
 * Aggregate skills (languages + frameworks) across given projects and
 * return the most common ones, de-duplicated by name (case-insensitive).
 *
 * @param {Array} projects
 * @param {object} [aggregatedSkills] – optional { languages: [], frameworks: [] } from /api/skills/
 * @param {number} max
 * @returns {Array<{id: string, title: string}>}
 */
export function selectTopSkills(projects, aggregatedSkills, max = MAX_SKILLS) {
  const freq = {};
  const preferredName = {};

  const trackSkill = (skillLike, count = 1) => {
    const rawName = typeof skillLike === 'string' ? skillLike : skillLike?.name;
    if (!rawName) return;

    const normalized = rawName.trim();
    if (!normalized) return;

    const key = normalized.toLowerCase();
    freq[key] = (freq[key] || 0) + count;

    // Keep the most descriptive (usually title-cased) variant for display.
    if (!preferredName[key] || normalized.length > preferredName[key].length) {
      preferredName[key] = normalized;
    }
  };

  // Count from per-project data
  (projects || []).forEach((p) => {
    [...(p.languages || []), ...(p.frameworks || []), ...(p.resume_skills || [])]
      .forEach((s) => trackSkill(s));
  });

  // Merge aggregated skills endpoint data (which includes project_count)
  if (aggregatedSkills) {
    [...(aggregatedSkills.languages || []), ...(aggregatedSkills.frameworks || []), ...(aggregatedSkills.resume_skills || [])]
      .forEach((s) => {
        const rawName = typeof s === 'string' ? s : s?.name;
        if (!rawName) return;

        const normalized = rawName.trim();
        if (!normalized) return;

        const key = normalized.toLowerCase();
        const count = typeof s?.project_count === 'number' ? s.project_count : 1;
        freq[key] = Math.max(freq[key] || 0, count);
        if (!preferredName[key] || normalized.length > preferredName[key].length) {
          preferredName[key] = normalized;
        }
      });
  }

  return Object.entries(freq)
    .sort(([, a], [, b]) => b - a)
    .slice(0, max)
    .map(([name], idx) => ({
      id: `auto-skill-${idx}`,
      title: preferredName[name] || name,
    }));
}

const deriveFallbackBullets = (project, maxBullets) => {
  const techList = [
    ...(project.languages || []).map((l) => l.name).filter(Boolean),
    ...(project.frameworks || []).map((f) => f.name).filter(Boolean),
    ...(project.resume_skills || []).map((s) => (typeof s === 'string' ? s : s?.name)).filter(Boolean),
  ];

  const uniqueTech = [...new Set(techList)].slice(0, 5);
  const bullets = [];

  if (uniqueTech.length > 0) {
    bullets.push(`Built and delivered features using ${uniqueTech.join(', ')}`);
  }

  if (project.classification_type) {
    bullets.push(`Developed a ${project.classification_type.toLowerCase()} project from concept to implementation`);
  }

  bullets.push('Collaborated on implementation, debugging, and iterative improvements');
  return bullets.slice(0, Math.max(1, maxBullets));
};

const buildAutoSummary = (topProjects, skills) => {
  if (!topProjects?.length) {
    return 'Motivated software developer with hands-on experience building practical projects and continuously learning new technologies.';
  }

  const projectCount = topProjects.length;
  const topSkills = (skills || []).slice(0, 4).map((s) => s.title).filter(Boolean);
  const domains = [...new Set((topProjects || []).map((p) => p.classification_type).filter(Boolean))]
    .slice(0, 3)
    .join(', ');

  const skillsText = topSkills.length ? ` with experience in ${topSkills.join(', ')}` : '';
  const domainText = domains ? ` across ${domains}` : '';

  return `Project-focused developer with ${projectCount} showcased projects${skillsText}${domainText}. Proven ability to ship maintainable solutions and communicate impact clearly.`;
};

/**
 * Build project section entries from selected projects.
 *
 * @param {Array} topProjects
 * @param {number} maxBullets – per project
 * @returns {Array} entries matching the resume sections.projects shape
 */
export function buildProjectEntries(topProjects, maxBullets = MAX_BULLETS_PER_PROJECT) {
  return (topProjects || []).map((p, idx) => {
    const selectedBullets = (p.resume_bullet_points || []).slice(0, maxBullets);
    const bullets = selectedBullets.length > 0
      ? selectedBullets
      : deriveFallbackBullets(p, maxBullets);
    const content = bullets.map((b) => `• ${b}`).join('\n');

    // Build a date range string
    let duration = '';
    if (p.first_commit_date || p.created_at) {
      const start = p.first_commit_date || p.created_at;
      const end = p.created_at || p.first_commit_date;
      const fmt = (ts) => {
        if (!ts) return 'Present';
        const d = typeof ts === 'number' ? new Date(ts * 1000) : new Date(ts);
        return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short' });
      };
      const s = fmt(start);
      const e = fmt(end);
      duration = s === e ? s : `${s} - ${e}`;
    }

    // Technologies string from languages + frameworks
    const techs = [
      ...(p.languages || []).map((l) => l.name),
      ...(p.frameworks || []).map((f) => f.name),
    ].join(', ');

    return {
      id: p.id ? `auto-project-${p.id}` : `auto-project-${idx}`,
      title: p.name || 'Untitled Project',
      company: techs,
      duration,
      content,
    };
  });
}

// ─── Main entry point ────────────────────────────────────────────────────────

/**
 * Generate a complete resume data object automatically.
 *
 * @param {object}  opts
 * @param {object}  opts.currentResumeData – existing resumeData (for personal info, education)
 * @param {Array}   opts.projects          – all user projects from the API
 * @param {object}  [opts.aggregatedSkills] – response from /api/skills/
 * @param {object}  [opts.limits]          – { maxProjects, maxSkills, maxBullets }
 * @returns {object} a fully-formed resumeData object ready to be set as state
 */
export function autoGenerateResume({
  currentResumeData,
  projects,
  aggregatedSkills,
  limits = {},
}) {
  const maxProjects = limits.maxProjects ?? MAX_PROJECTS;
  const maxSkills = limits.maxSkills ?? MAX_SKILLS;
  const maxBullets = limits.maxBullets ?? MAX_BULLETS_PER_PROJECT;

  const topProjects = selectTopProjects(projects, maxProjects);
  const skills = selectTopSkills(topProjects, aggregatedSkills, maxSkills);
  const projectEntries = buildProjectEntries(topProjects, maxBullets);

  // Carry forward personal info & education from the current state
  const base = currentResumeData || {};
  const existingSections = base.sections || {};
  const summary = existingSections.summary?.trim()
    ? existingSections.summary
    : buildAutoSummary(topProjects, skills);

  return {
    name: base.name || '',
    email: base.email || '',
    phone: base.phone || '',
    github_url: base.github_url || '',
    portfolio_url: base.portfolio_url || '',
    linkedin_url: base.linkedin_url || '',
    location: base.location || '',
    sections: {
      summary,
      education: existingSections.education || [],
      experience: existingSections.experience || [],
      projects: projectEntries,
      skills,
      certifications: existingSections.certifications || [],
    },
  };
}
