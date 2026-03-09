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
  const skillCount = languageCount + frameworkCount;

  // Recency: projects with a more-recent created_at get a small bonus (0-10 pts)
  let recencyBonus = 0;
  if (project.created_at) {
    const ageMs = Date.now() - new Date(project.created_at).getTime();
    const ageYears = ageMs / (1000 * 60 * 60 * 24 * 365);
    recencyBonus = Math.max(0, 10 - ageYears * 2);
  }

  return bulletCount * 3 + skillCount * 2 + recencyBonus;
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

  // Count from per-project data
  (projects || []).forEach((p) => {
    [...(p.languages || []), ...(p.frameworks || [])].forEach((s) => {
      const key = s.name.toLowerCase();
      freq[key] = (freq[key] || 0) + 1;
    });
  });

  // Merge aggregated skills endpoint data (which includes project_count)
  if (aggregatedSkills) {
    [...(aggregatedSkills.languages || []), ...(aggregatedSkills.frameworks || [])].forEach((s) => {
      const key = s.name.toLowerCase();
      // keep the higher number between our count and the endpoint's project_count
      freq[key] = Math.max(freq[key] || 0, s.project_count || 0);
    });
  }

  return Object.entries(freq)
    .sort(([, a], [, b]) => b - a)
    .slice(0, max)
    .map(([name], idx) => ({
      id: `auto-skill-${idx}`,
      title: name.charAt(0).toUpperCase() + name.slice(1), // capitalize
    }));
}

/**
 * Build project section entries from selected projects.
 *
 * @param {Array} topProjects
 * @param {number} maxBullets – per project
 * @returns {Array} entries matching the resume sections.projects shape
 */
export function buildProjectEntries(topProjects, maxBullets = MAX_BULLETS_PER_PROJECT) {
  return (topProjects || []).map((p, idx) => {
    const bullets = (p.resume_bullet_points || []).slice(0, maxBullets);
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
      id: Date.now() + idx,
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

  return {
    name: base.name || '',
    email: base.email || '',
    phone: base.phone || '',
    github_url: base.github_url || '',
    portfolio_url: base.portfolio_url || '',
    linkedin_url: base.linkedin_url || '',
    location: base.location || '',
    sections: {
      summary: existingSections.summary || '',
      education: existingSections.education || [],
      experience: existingSections.experience || [],
      projects: projectEntries,
      skills,
      certifications: existingSections.certifications || [],
    },
  };
}
