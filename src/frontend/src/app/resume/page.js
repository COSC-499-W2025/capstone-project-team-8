'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import Toast from '@/components/Toast';
import { getCurrentUser } from '@/utils/api';
import {
  getProjects,
  getSkills,
  generateRenderCVPdf,
  downloadRenderCVYaml,
  generateResume,
  updateResume,
  getResume,
} from '@/utils/resumeApi';
import { getProjectDateRange } from '@/utils/resumeCleanup';
import { autoGenerateResume } from '@/utils/autoGenerateResume';
import ProjectsPanel from '@/components/resume/ProjectsPanel';
import styles from './resume-new.module.css';

// ─── Helpers ────────────────────────────────────────────────────────────────

const THEMES = [
  { value: 'classic', label: 'Classic' },
  { value: 'sb2nov', label: 'SB2Nov' },
  { value: 'moderncv', label: 'ModernCV' },
  { value: 'engineeringclassic', label: 'Engineering Classic' },
];

const EMPTY_RESUME = {
  name: '',
  email: '',
  phone: '',
  github_url: '',
  portfolio_url: '',
  linkedin_url: '',
  location: '',
  sections: {
    summary: '',
    education: [],
    experience: [],
    projects: [],
    skills: [],
    certifications: [],
  },
};

function parseContent(content) {
  if (!content) return [];
  return content
    .split('\n')
    .map((l) => l.replace(/^[•\-]\s*/, '').trim())
    .filter(Boolean);
}

function buildContent(bullets) {
  return bullets.map((b) => `• ${b}`).join('\n');
}

// ─── Sub-components ──────────────────────────────────────────────────────────

function SectionHeader({ title, onAdd, addLabel = '+ Add', collapsed, onToggle }) {
  return (
    <div className={styles.sectionHeader}>
      <button className={styles.collapseBtn} onClick={onToggle} type="button">
        {collapsed ? '▶' : '▼'} <span>{title}</span>
      </button>
      {onAdd && (
        <button className={styles.addBtn} onClick={onAdd} type="button">
          {addLabel}
        </button>
      )}
    </div>
  );
}

function BulletList({ content, onChange }) {
  // Local state keeps empty bullets alive while the user types.
  // parseContent (which filters empties) is only used for initialisation
  // and for syncing when content changes from outside.
  const parseRaw = (str) => {
    if (!str) return [];
    return str.split('\n').map((l) => l.replace(/^[•\-]\s*/, '').trim());
  };

  const [bullets, setBullets] = useState(() => parseRaw(content));
  const lastEmitted = useRef(content);

  // Sync inward only when the prop changed externally (not from our own emit)
  useEffect(() => {
    if (content !== lastEmitted.current) {
      lastEmitted.current = content;
      setBullets(parseRaw(content));
    }
  }, [content]);

  const emit = (next) => {
    const str = next.map((b) => `• ${b}`).join('\n');
    lastEmitted.current = str;
    onChange(str);
  };

  const updateBullet = (i, val) => {
    const next = [...bullets];
    next[i] = val;
    setBullets(next);
    emit(next);
  };

  const removeBullet = (i) => {
    const next = bullets.filter((_, idx) => idx !== i);
    setBullets(next);
    emit(next);
  };

  const addBullet = () => {
    const next = [...bullets, ''];
    setBullets(next);
    emit(next);
  };

  return (
    <div className={styles.bulletList}>
      {bullets.map((b, i) => (
        <div key={i} className={styles.bulletRow}>
          <span className={styles.bulletDot}>•</span>
          <input
            className={styles.bulletInput}
            value={b}
            onChange={(e) => updateBullet(i, e.target.value)}
            placeholder="Bullet point..."
            autoFocus={b === '' && i === bullets.length - 1}
          />
          <button
            className={styles.removeBulletBtn}
            onClick={() => removeBullet(i)}
            type="button"
            title="Remove bullet"
          >
            ×
          </button>
        </div>
      ))}
      <button className={styles.addBulletBtn} onClick={addBullet} type="button">
        + bullet
      </button>
    </div>
  );
}

function EntryCard({ item, onUpdate, onRemove, fields }) {
  return (
    <div className={styles.entryCard}>
      <div className={styles.entryCardHeader}>
        <div className={styles.entryFields}>
          {fields.map((f) =>
            f.type === 'select' ? (
              <select
                key={f.key}
                className={styles.entryInput}
                value={item[f.key] || ''}
                onChange={(e) => onUpdate({ ...item, [f.key]: e.target.value })}
              >
                <option value="">{f.placeholder}</option>
                {(f.options || []).map((opt) => (
                  <option key={opt} value={opt}>{opt}</option>
                ))}
              </select>
            ) : (
              <input
                key={f.key}
                className={styles.entryInput}
                value={item[f.key] || ''}
                onChange={(e) => onUpdate({ ...item, [f.key]: e.target.value })}
                placeholder={f.placeholder}
              />
            )
          )}
        </div>
        <button className={styles.removeEntryBtn} onClick={onRemove} type="button" title="Remove">
          ×
        </button>
      </div>
      {item.content !== undefined && (
        <BulletList
          content={item.content}
          onChange={(c) => onUpdate({ ...item, content: c })}
        />
      )}
    </div>
  );
}

// ─── Live Preview ────────────────────────────────────────────────────────────

function ResumePreview({ resumeData }) {
  const sec = resumeData.sections || {};

  const parseB = (content) => {
    if (!content) return [];
    return content
      .split('\n')
      .map((l) => l.replace(/^[•\-]\s*/, '').trim())
      .filter(Boolean);
  };

  return (
    <div className={styles.previewScroll}>
      <div className={styles.previewPaper}>
        <div className={styles.previewName}>{resumeData.name || 'Your Name'}</div>
        <div className={styles.previewContact}>
          {[resumeData.email, resumeData.phone, resumeData.location]
            .filter(Boolean)
            .join(' | ')}
        </div>

        {sec.education?.length > 0 && (
          <div className={styles.previewSection}>
            <div className={styles.previewSectionTitle}>EDUCATION</div>
            {sec.education.map((e) => (
              <div key={e.id} className={styles.previewEntry}>
                <div className={styles.previewRow}>
                  <strong>{e.title}</strong>
                  <span className={styles.previewDate}>{e.duration}</span>
                </div>
                {(e.degree_type || e.company) && (
                  <div className={styles.previewSub}>
                    {e.degree_type && e.company
                      ? `${e.degree_type} in ${e.company}`
                      : e.degree_type || e.company}
                  </div>
                )}
                {parseB(e.content).map((b, i) => (
                  <div key={i} className={styles.previewBullet}>• {b}</div>
                ))}
              </div>
            ))}
          </div>
        )}

        {sec.experience?.length > 0 && (
          <div className={styles.previewSection}>
            <div className={styles.previewSectionTitle}>EXPERIENCE</div>
            {sec.experience.map((e) => (
              <div key={e.id} className={styles.previewEntry}>
                <div className={styles.previewRow}>
                  <strong>{e.title}</strong>
                  <span className={styles.previewDate}>{e.duration}</span>
                </div>
                {e.company && <div className={styles.previewSub}>{e.company}</div>}
                {parseB(e.content).map((b, i) => (
                  <div key={i} className={styles.previewBullet}>• {b}</div>
                ))}
              </div>
            ))}
          </div>
        )}

        {sec.projects?.length > 0 && (
          <div className={styles.previewSection}>
            <div className={styles.previewSectionTitle}>PROJECTS</div>
            {sec.projects.map((e) => (
              <div key={e.id} className={styles.previewEntry}>
                <div className={styles.previewRow}>
                  <strong>{e.title}</strong>
                  <span className={styles.previewDate}>{e.duration}</span>
                </div>
                {e.company && <div className={styles.previewSub}>{e.company}</div>}
                {parseB(e.content).map((b, i) => (
                  <div key={i} className={styles.previewBullet}>• {b}</div>
                ))}
              </div>
            ))}
          </div>
        )}

        {sec.skills?.filter((s) => s.title).length > 0 && (
          <div className={styles.previewSection}>
            <div className={styles.previewSectionTitle}>SKILLS</div>
            <div className={styles.previewSkills}>
              {sec.skills.map((s) => s.title).filter(Boolean).join(' • ')}
            </div>
          </div>
        )}

        {sec.certifications?.length > 0 && (
          <div className={styles.previewSection}>
            <div className={styles.previewSectionTitle}>CERTIFICATIONS</div>
            {sec.certifications.map((e) => (
              <div key={e.id} className={styles.previewEntry}>
                <div className={styles.previewRow}>
                  <strong>{e.title}</strong>
                  <span className={styles.previewDate}>{e.duration}</span>
                </div>
                {e.company && <div className={styles.previewSub}>{e.company}</div>}
                {parseB(e.content).map((b, i) => (
                  <div key={i} className={styles.previewBullet}>• {b}</div>
                ))}
              </div>
            ))}
          </div>
        )}

        {!sec.education?.length &&
          !sec.experience?.length &&
          !sec.projects?.length &&
          !sec.skills?.filter((s) => s.title).length && (
            <p className={styles.previewEmpty}>
              Fill in your info to see a preview here.
            </p>
          )}
      </div>
    </div>
  );
}

// ─── Page ────────────────────────────────────────────────────────────────────

function mergeResumeData(baseResume, savedResume) {
  const savedContent = savedResume?.content || {};
  const savedSections = savedContent.sections || {};

  return {
    ...baseResume,
    ...savedContent,
    sections: {
      ...baseResume.sections,
      ...savedSections,
      education: savedSections.education || baseResume.sections.education,
      experience: savedSections.experience || baseResume.sections.experience,
      projects: savedSections.projects || baseResume.sections.projects,
      skills: savedSections.skills || baseResume.sections.skills,
      certifications: savedSections.certifications || baseResume.sections.certifications,
      summary: savedSections.summary ?? baseResume.sections.summary,
    },
  };
}

export default function ResumeNewPage({ resumeId = null }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, token, refreshAccessToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [saving, setSaving] = useState(false);
  const [autoGenerating, setAutoGenerating] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [theme, setTheme] = useState('classic');
  const [currentResumeId, setCurrentResumeId] = useState(
    resumeId ? Number.parseInt(resumeId, 10) : null
  );

  // Track if we've done initial load (to avoid marking first load as unsaved changes)
  const initialLoadRef = useRef(true);
  // Store skills data for auto-generate
  const [aggregatedSkills, setAggregatedSkills] = useState(null);

  // Collapsed state for each form section
  const [collapsed, setCollapsed] = useState({
    personal: false,
    education: false,
    experience: false,
    projects: false,
    skills: false,
    certifications: true,
  });

  const toggleSection = (key) =>
    setCollapsed((prev) => ({ ...prev, [key]: !prev[key] }));

  const openSection = (key) =>
    setCollapsed((prev) => ({ ...prev, [key]: false }));

  // Undo / Redo
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const historyRef = useRef(null);

  // Main state
  const [projects, setProjects] = useState([]);
  const [selectedProjects, setSelectedProjects] = useState(new Set());
  const [resumeData, setResumeData] = useState(EMPTY_RESUME);

  // Panel widths (px)
  const [sidebarWidth, setSidebarWidth] = useState(300);
  const [previewWidth, setPreviewWidth] = useState(400);
  const draggingRef = useRef(null);

  const startDrag = useCallback((which) => (e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startSidebar = sidebarWidth;
    const startPreview = previewWidth;
    draggingRef.current = which;

    const onMove = (ev) => {
      const dx = ev.clientX - startX;
      if (which === 'left') {
        setSidebarWidth(Math.max(160, Math.min(520, startSidebar + dx)));
      } else {
        setPreviewWidth(Math.max(200, Math.min(660, startPreview - dx)));
      }
    };
    const onUp = () => {
      draggingRef.current = null;
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
    };
    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
  }, [sidebarWidth, previewWidth]);

  // ── history helpers ──────────────────────────────────────────────────────

  const pushToHistory = useCallback(
    (data) => {
      const newHistory = history.slice(0, historyIndex + 1);
      newHistory.push(JSON.parse(JSON.stringify(data)));
      setHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);
      historyRef.current = data;
    },
    [history, historyIndex]
  );

  const undo = useCallback(() => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setHistoryIndex(newIndex);
      setResumeData(JSON.parse(JSON.stringify(history[newIndex])));
    }
  }, [history, historyIndex]);

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setHistoryIndex(newIndex);
      setResumeData(JSON.parse(JSON.stringify(history[newIndex])));
    }
  }, [history, historyIndex]);

  // Keyboard undo/redo
  useEffect(() => {
    const handler = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'z' && !e.shiftKey) {
        e.preventDefault();
        undo();
      }
      if (
        (e.ctrlKey || e.metaKey) &&
        (e.key === 'y' || (e.shiftKey && e.key === 'z'))
      ) {
        e.preventDefault();
        redo();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [undo, redo]);

  // ── init ─────────────────────────────────────────────────────────────────

  useEffect(() => {
    if (!isAuthenticated) { router.push('/login'); return; }
    if (!token) return;

    const init = async () => {
      try {
        const [userData, projectsData, skillsData] = await Promise.all([
          getCurrentUser(token),
          getProjects(token),
          getSkills(token).catch(() => ({ languages: [], frameworks: [] })),
        ]);

        const u = userData.user || {};
        const firstName = u.first_name || '';
        const lastName = u.last_name || '';
        const fullName =
          firstName && lastName
            ? `${firstName} ${lastName}`
            : firstName || lastName || 'Your Name';

        const city = u.education_city || u.city || '';
        const state = u.education_state || u.state || '';
        const country = u.country || '';
        const location =
          city && state
            ? `${city}, ${state}`
            : city || state || country || '';

        const contactInfo = {
          name: fullName,
          email: u.email || '',
          phone: u.phone || '',
          github_url: u.github_username ? `https://github.com/${u.github_username}` : '',
          portfolio_url: u.portfolio_url || '',
          linkedin_url: u.linkedin_url || '',
          location,
        };

        const projectsList = Array.isArray(projectsData)
          ? projectsData
          : projectsData.projects || projectsData.results || [];
        setProjects(projectsList);

        // Build pre-populated skills from the skills endpoint
        // Store aggregated skills for auto-generate feature
        setAggregatedSkills(skillsData);

        const allSkills = [
          ...(skillsData.languages || []).map((l) => ({ id: `lang-${l.name}`, title: l.name })),
          ...(skillsData.frameworks || []).map((f) => ({ id: `fw-${f.name}`, title: f.name })),
        ];

        // Build pre-populated education entry
        const education = [];
        if (u.university || u.degree_major) {
          education.push({
            id: Date.now(),
            title: u.university || 'University',
            degree_type: '',
            company: u.degree_major || '',
            duration: (() => {
              const gradYear = u.graduation_year || u.expected_graduation;
              return gradYear ? `Graduating ${gradYear}` : '';
            })(),
            content: '',
          });
        }

        const initial = {
          ...contactInfo,
          sections: {
            summary: '',
            education,
            experience: [],
            projects: [],
            skills: allSkills,
            certifications: [],
          },
        };

        if (resumeId) {
          const savedResume = await getResume(token, resumeId);
          const mergedResume = mergeResumeData(initial, savedResume);
          const initialHistory = [mergedResume];
          setResumeData(mergedResume);
          setHistory(initialHistory);
          setHistoryIndex(0);
          setCurrentResumeId(savedResume.id);
          setTheme(savedResume.theme || 'classic');
          return;
        }

        const draftKey = 'resumeBuilderCurrentDraft';
        const draftsKey = 'resumeBuilderDrafts';
        const currentDraftId = typeof window !== 'undefined'
          ? window.localStorage.getItem(draftKey)
          : null;
        const allDrafts = typeof window !== 'undefined'
          ? JSON.parse(window.localStorage.getItem(draftsKey) || '{}')
          : {};
        const draft = currentDraftId ? allDrafts[currentDraftId]?.content : null;
        if (draft && draft.sections) {
          const draftSkillTitles = new Set((draft.sections.skills || []).map((s) => s.title));
          const newSkills = allSkills.filter((s) => !draftSkillTitles.has(s.title));
          const mergedDraft = newSkills.length
            ? { ...draft, sections: { ...draft.sections, skills: [...draft.sections.skills, ...newSkills] } }
            : draft;
          setResumeData(mergedDraft);
          const initialHistory = [mergedDraft];
          setHistory(initialHistory);
          setHistoryIndex(0);
        } else {
          setResumeData(initial);
          const initialHistory = [initial];
          setHistory(initialHistory);
          setHistoryIndex(0);
        }
      } catch (err) {
        console.error('Init error:', err);
        setMessage({ type: 'error', text: 'Failed to load resume data.' });
      } finally {
        setLoading(false);
        // Mark initial load as complete after a short delay
        setTimeout(() => {
          initialLoadRef.current = false;
        }, 100);
      }
    };

    init();
  }, [isAuthenticated, token, router, resumeId]);

  // Auto-save draft
  useEffect(() => {
    if (!loading && !currentResumeId && resumeData.name && typeof window !== 'undefined') {
      const drafts = JSON.parse(window.localStorage.getItem('resumeBuilderDrafts') || '{}');
      const draftId = window.localStorage.getItem('resumeBuilderCurrentDraft') || Date.now().toString();
      drafts[draftId] = {
        id: Number.parseInt(draftId, 10),
        name: 'current',
        content: resumeData,
        savedAt: new Date().toISOString(),
      };
      window.localStorage.setItem('resumeBuilderDrafts', JSON.stringify(drafts));
      window.localStorage.setItem('resumeBuilderCurrentDraft', draftId);
    }
  }, [resumeData, loading, currentResumeId]);

  // ── section helpers ──────────────────────────────────────────────────────

  const updateSection = (sectionType, newItems) => {
    const updated = {
      ...resumeData,
      sections: { ...resumeData.sections, [sectionType]: newItems },
    };
    setResumeData(updated);
    pushToHistory(updated);
  };

  const addEntry = (sectionType, extra = {}) => {
    const newItem = {
      id: Date.now(),
      title: '',
      company: '',
      duration: '',
      content: '',
      ...(sectionType === 'education' ? { degree_type: '' } : {}),
      ...extra,
    };
    const items = [...(resumeData.sections[sectionType] || []), newItem];
    updateSection(sectionType, items);
    openSection(sectionType);
  };

  const updateEntry = (sectionType, updatedItem) => {
    const items = (resumeData.sections[sectionType] || []).map((i) =>
      i.id === updatedItem.id ? updatedItem : i
    );
    updateSection(sectionType, items);
  };

  const removeEntry = (sectionType, id) => {
    const items = (resumeData.sections[sectionType] || []).filter((i) => i.id !== id);
    updateSection(sectionType, items);
  };

  const updatePersonal = (field, value) => {
    const updated = { ...resumeData, [field]: value };
    setResumeData(updated);
  };

  const flushPersonal = () => pushToHistory(resumeData);

  /** Coerce a raw phone string to E.164 format (+1XXXXXXXXXX for NA numbers). */
  const normalizePhone = (raw) => {
    if (!raw) return '';
    const digits = raw.replace(/\D/g, '');
    if (!digits) return '';
    if (digits.length === 10) return `+1${digits}`;
    if (digits.length === 11 && digits[0] === '1') return `+${digits}`;
    // already has country code (more than 11 digits treated as-is with +)
    return `+${digits}`;
  };

  const handlePhoneBlur = () => {
    const normalized = normalizePhone(resumeData.phone);
    const updated = { ...resumeData, phone: normalized };
    setResumeData(updated);
    pushToHistory(updated);
  };

  // ── drag and drop ────────────────────────────────────────────────────────

  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDropSkill = (e) => {
    e.preventDefault();
    try {
      const data = JSON.parse(e.dataTransfer.getData('application/json'));
      if (data.type !== 'skill') return;

      const timestamp = Date.now();
      if (data.projectName) {
        const existingIndex = (resumeData.sections.projects || []).findIndex(
          (p) => p.company === data.projectName
        );
        const dateRange = getProjectDateRange(
          data.projectFirstCommitDate,
          data.projectLastCommitDate
        );
        let updatedProjects;
        if (existingIndex >= 0) {
          updatedProjects = [...(resumeData.sections.projects || [])];
          const entry = updatedProjects[existingIndex];
          updatedProjects[existingIndex] = {
            ...entry,
            content: `${entry.content}\n• ${data.item.title}`,
          };
        } else {
          updatedProjects = [
            ...(resumeData.sections.projects || []),
            {
              id: timestamp,
              title: data.item.title,
              company: data.projectName,
              duration: dateRange,
              content: `• ${data.item.title}`,
            },
          ];
        }
        const updated = {
          ...resumeData,
          sections: { ...resumeData.sections, projects: updatedProjects },
        };
        setResumeData(updated);
        pushToHistory(updated);
        openSection('projects');
      } else {
        const newSkill = { id: timestamp, title: data.item.title };
        const updated = {
          ...resumeData,
          sections: {
            ...resumeData.sections,
            skills: [...(resumeData.sections.skills || []), newSkill],
          },
        };
        setResumeData(updated);
        pushToHistory(updated);
        openSection('skills');
      }
    } catch (err) {
      console.error('Drop skill error:', err);
    }
  };

  const handleDropExperience = (e) => {
    e.preventDefault();
    try {
      const data = JSON.parse(e.dataTransfer.getData('application/json'));
      if (data.type !== 'bullet') return;

      const projectName = data.projectName || 'Project Work';
      const dateRange = getProjectDateRange(
        data.projectFirstCommitDate,
        data.projectLastCommitDate
      );
      const existingIndex = (resumeData.sections.projects || []).findIndex(
        (p) => p.title === projectName
      );
      let updatedProjects;
      if (existingIndex >= 0) {
        updatedProjects = [...(resumeData.sections.projects || [])];
        const entry = updatedProjects[existingIndex];
        updatedProjects[existingIndex] = {
          ...entry,
          content: `${entry.content}\n• ${data.item.content}`,
        };
      } else {
        updatedProjects = [
          ...(resumeData.sections.projects || []),
          {
            id: Date.now(),
            title: projectName,
            company: '',
            duration: dateRange,
            content: `• ${data.item.content}`,
          },
        ];
      }
      const updated = {
        ...resumeData,
        sections: { ...resumeData.sections, projects: updatedProjects },
      };
      setResumeData(updated);
      pushToHistory(updated);
      openSection('projects');
    } catch (err) {
      console.error('Drop bullet error:', err);
    }
  };

  const handleQuickAdd = (item, type) => {
    const timestamp = Date.now();
    if (type === 'skill') {
      if (item.projectName) {
        const project = projects.find((p) => p.id === item.projectId);
        const dateRange = project
          ? getProjectDateRange(project.first_commit_date, project.last_commit_date)
          : 'Present';
        const existingIndex = (resumeData.sections.projects || []).findIndex(
          (p) => p.company === item.projectName
        );
        let updatedProjects;
        if (existingIndex >= 0) {
          updatedProjects = [...(resumeData.sections.projects || [])];
          const entry = updatedProjects[existingIndex];
          updatedProjects[existingIndex] = {
            ...entry,
            content: `${entry.content}\n• ${item.title}`,
          };
        } else {
          updatedProjects = [
            ...(resumeData.sections.projects || []),
            {
              id: timestamp,
              title: item.title,
              company: item.projectName,
              duration: dateRange,
              content: `• ${item.title}`,
            },
          ];
        }
        const updated = {
          ...resumeData,
          sections: { ...resumeData.sections, projects: updatedProjects },
        };
        setResumeData(updated);
        pushToHistory(updated);
        openSection('projects');
      } else {
        const newSkill = { id: timestamp, title: item.title };
        const updated = {
          ...resumeData,
          sections: {
            ...resumeData.sections,
            skills: [...(resumeData.sections.skills || []), newSkill],
          },
        };
        setResumeData(updated);
        pushToHistory(updated);
        openSection('skills');
      }
    } else if (type === 'bullet') {
      const project = projects.find((p) => p.id === item.projectId);
      const projectName = item.projectName || 'Project Work';
      const dateRange = project
        ? getProjectDateRange(project.first_commit_date, project.last_commit_date)
        : 'Present';
      const existingIndex = (resumeData.sections.projects || []).findIndex(
        (p) => p.title === projectName
      );
      let updatedProjects;
      if (existingIndex >= 0) {
        updatedProjects = [...(resumeData.sections.projects || [])];
        const entry = updatedProjects[existingIndex];
        updatedProjects[existingIndex] = {
          ...entry,
          content: `${entry.content}\n• ${item.content}`,
        };
      } else {
        updatedProjects = [
          ...(resumeData.sections.projects || []),
          {
            id: Date.now(),
            title: projectName,
            company: '',
            duration: dateRange,
            content: `• ${item.content}`,
          },
        ];
      }
      const updated = {
        ...resumeData,
        sections: { ...resumeData.sections, projects: updatedProjects },
      };
      setResumeData(updated);
      pushToHistory(updated);
      openSection('projects');
    }
  };

  const addProjectBullet = (projectId) => {
    const project = projects.find((p) => p.id === projectId);
    if (!project) return;
    const projectItem = {
      id: Date.now(),
      title: project.name,
      company: project.classification_type || 'Project',
      duration: '',
      content: (project.resume_bullet_points || []).join('\n'),
    };
    const updated = {
      ...resumeData,
      sections: {
        ...resumeData.sections,
        projects: [...(resumeData.sections.projects || []), projectItem],
      },
    };
    setResumeData(updated);
    pushToHistory(updated);
    setSelectedProjects((prev) => new Set(prev).add(projectId));
    openSection('projects');
  };

  // ── Auto-generate handler ────────────────────────────────────────────────

  const handleAutoGenerate = useCallback(() => {
    setAutoGenerating(true);
    // Small delay so the overlay renders before the synchronous work
    setTimeout(() => {
      try {
        const generated = autoGenerateResume({
          currentResumeData: resumeData,
          projects,
          aggregatedSkills,
        });
        setResumeData(generated);
        pushToHistory(generated);

        // Open the sections that were populated
        setCollapsed((prev) => ({
          ...prev,
          projects: false,
          skills: false,
        }));

        setMessage({ type: 'success', text: 'Resume auto-generated! Review and tweak, then pick a theme and generate PDF.' });
      } catch (err) {
        console.error('Auto-generate error:', err);
        setMessage({ type: 'error', text: 'Failed to auto-generate resume.' });
      } finally {
        setAutoGenerating(false);
      }
    }, 100);
  }, [resumeData, projects, aggregatedSkills, pushToHistory]);

  // ── PDF generation ───────────────────────────────────────────────────────

  const handleGeneratePDF = async () => {
    setGenerating(true);
    setMessage({ type: '', text: '' });
    try {
      let activeToken = token;
      try {
        await generateRenderCVPdf(activeToken, resumeData, theme);
      } catch (err) {
        if (err.message?.includes('401')) {
          activeToken = await refreshAccessToken();
          if (!activeToken) throw new Error('Session expired. Please log in again.');
          await generateRenderCVPdf(activeToken, resumeData, theme);
        } else {
          throw err;
        }
      }
      setMessage({ type: 'success', text: 'PDF downloaded!' });
    } catch (err) {
      console.error('PDF generation error:', err);
      setMessage({ type: 'error', text: err.message || 'Failed to generate PDF.' });
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadYAML = async () => {
    try {
      let activeToken = token;
      try {
        await downloadRenderCVYaml(activeToken, resumeData, theme);
      } catch (err) {
        if (err.message?.includes('401')) {
          activeToken = await refreshAccessToken();
          if (!activeToken) throw new Error('Session expired. Please log in again.');
          await downloadRenderCVYaml(activeToken, resumeData, theme);
        } else {
          throw err;
        }
      }
    } catch (err) {
      setMessage({ type: 'error', text: err.message || 'Failed to download YAML.' });
    }
  };

  const handleSaveResume = async () => {
    setSaving(true);
    setMessage({ type: '', text: '' });

    const resumeName = (resumeData.name || '').trim() || 'Untitled Resume';

    try {
      let activeToken = token;
      let savedResume;

      try {
        savedResume = currentResumeId
          ? await updateResume(activeToken, currentResumeId, resumeName, resumeData, theme)
          : await generateResume(activeToken, resumeName, resumeData, theme);
      } catch (err) {
        if (err.message?.includes('401')) {
          activeToken = await refreshAccessToken();
          if (!activeToken) throw new Error('Session expired. Please log in again.');
          savedResume = currentResumeId
            ? await updateResume(activeToken, currentResumeId, resumeName, resumeData, theme)
            : await generateResume(activeToken, resumeName, resumeData, theme);
        } else {
          throw err;
        }
      }

      setCurrentResumeId(savedResume.id);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem('resumeBuilderCurrentDraft');
      }
      setMessage({
        type: 'success',
        text: currentResumeId ? 'Resume updated.' : 'Resume saved.',
      });

      if (!currentResumeId) {
        router.replace(`/resume/${savedResume.id}`);
      }
    } catch (err) {
      console.error('Save resume error:', err);
      setMessage({ type: 'error', text: err.message || 'Failed to save resume.' });
    } finally {
      setSaving(false);
    }
  };

  // ── render ───────────────────────────────────────────────────────────────

  if (loading) {
    return (
      <div className={styles.page}>
        <Header />
        <div className={styles.loadingContainer}>
          <div className={styles.spinner} />
          <p>Loading resume builder…</p>
        </div>
      </div>
    );
  }

  const sec = resumeData.sections;

  return (
    <div className={styles.page}>
      <Header />
      {message.text && (
        <Toast
          message={message.text}
          type={message.type}
          onClose={() => setMessage({ type: '', text: '' })}
        />
      )}

      {/* Auto-Generate Overlay */}
      {autoGenerating && (
        <div className={styles.autoGenerateOverlay}>
          <div className={styles.autoGenerateModal}>
            <div className={styles.autoGenerateSpinner} />
            <h2>Building Your Resume</h2>
            <p>Selecting top projects and skills…</p>
          </div>
        </div>
      )}

      <div className={styles.layout}>
        {/* ── Left: Projects Panel ── */}
        <aside className={styles.sidebar} key="sidebar" style={{ width: sidebarWidth }}>
          <ProjectsPanel
            projects={projects}
            onAddItem={handleQuickAdd}
          />
        </aside>

        {/* drag handle: sidebar ↔ editor */}
        <div
          className={styles.dragHandle}
          onMouseDown={startDrag('left')}
          title="Drag to resize"
        />

        {/* ── Center: Form Editor ── */}
        <main
          className={styles.editor}
          onDragOver={handleDragOver}
          onDrop={(e) => {
            try {
              const data = JSON.parse(e.dataTransfer.getData('application/json'));
              if (data.type === 'skill') handleDropSkill(e);
              else handleDropExperience(e);
            } catch { handleDropExperience(e); }
          }}
        >
          {/* Toolbar */}
          <div className={styles.toolbar}>
            <div className={styles.toolbarLeft}>
              <button
                className={styles.autoGenerateBtn}
                onClick={handleAutoGenerate}
                disabled={autoGenerating || projects.length === 0}
                title="Automatically pick the best projects and skills for your resume"
              >
                {autoGenerating ? (
                  <>
                    <span className={styles.btnSpinner} /> Generating…
                  </>
                ) : (
                  '✨ Auto-Generate'
                )}
              </button>
              <button
                className={styles.toolbarBtn}
                onClick={undo}
                disabled={historyIndex <= 0}
                title="Undo (Ctrl+Z)"
              >
                ↩ Undo
              </button>
              <button
                className={styles.toolbarBtn}
                onClick={redo}
                disabled={historyIndex >= history.length - 1}
                title="Redo (Ctrl+Y)"
              >
                ↪ Redo
              </button>
            </div>
            <div className={styles.toolbarRight}>
              <label className={styles.themeLabel}>Theme:</label>
              <select
                className={styles.themeSelect}
                value={theme}
                onChange={(e) => setTheme(e.target.value)}
              >
                {THEMES.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
              <button
                className={styles.yamlBtn}
                onClick={handleDownloadYAML}
                title="Download RenderCV YAML"
              >
                ↓ YAML
              </button>
              <button
                className={`${styles.saveBtn} ${saving ? styles.saving : ''}`}
                onClick={handleSaveResume}
                disabled={saving}
                type="button"
              >
                {saving ? (
                  <>
                    <span className={styles.btnSpinner} /> Saving…
                  </>
                ) : (
                  currentResumeId ? 'Save Changes' : 'Save Resume'
                )}
              </button>
              <button
                className={`${styles.generateBtn} ${generating ? styles.generating : ''}`}
                onClick={handleGeneratePDF}
                disabled={generating}
              >
                {generating ? (
                  <>
                    <span className={styles.btnSpinner} /> Generating…
                  </>
                ) : (
                  '⬇ Generate PDF'
                )}
              </button>
            </div>
          </div>

          {/* Personal Info */}
          <section className={styles.formSection}>
            <SectionHeader
              title="Personal Info"
              collapsed={collapsed.personal}
              onToggle={() => toggleSection('personal')}
            />
            {!collapsed.personal && (
              <div className={styles.personalGrid}>
                {[
                  { key: 'name', placeholder: 'Full Name' },
                  { key: 'email', placeholder: 'Email' },
                  { key: 'phone', placeholder: 'Phone (e.g. 1234567890)' },
                  { key: 'location', placeholder: 'City, State' },
                  { key: 'github_url', placeholder: 'GitHub URL' },
                  { key: 'linkedin_url', placeholder: 'LinkedIn URL' },
                  { key: 'portfolio_url', placeholder: 'Portfolio URL' },
                ].map(({ key, placeholder }) => (
                  <input
                    key={key}
                    type={key === 'phone' ? 'tel' : 'text'}
                    className={styles.personalInput}
                    value={resumeData[key] || ''}
                    onChange={(e) => {
                      if (key === 'phone') {
                        // only allow digits, +, spaces, dashes, parens
                        const val = e.target.value.replace(/[^\d+\s()\-]/g, '');
                        updatePersonal('phone', val);
                      } else {
                        updatePersonal(key, e.target.value);
                      }
                    }}
                    onBlur={key === 'phone' ? handlePhoneBlur : flushPersonal}
                    placeholder={placeholder}
                  />
                ))}
              </div>
            )}
          </section>

          {/* Education */}
          <section className={styles.formSection}>
            <SectionHeader
              title="Education"
              collapsed={collapsed.education}
              onToggle={() => toggleSection('education')}
              onAdd={() => addEntry('education')}
            />
            {!collapsed.education && sec.education.length === 0 && (
              <p className={styles.emptyHint}>No education entries yet — click + Add</p>
            )}
            {!collapsed.education &&
              sec.education.map((item) => (
                <EntryCard
                  key={item.id}
                  item={item}
                  onUpdate={(u) => updateEntry('education', u)}
                  onRemove={() => removeEntry('education', item.id)}
                  fields={[
                    { key: 'title', placeholder: 'School / University' },
                    {
                      key: 'degree_type',
                      placeholder: 'Degree Type',
                      type: 'select',
                      options: ['B.Sc.', 'B.A.', 'B.Eng.', 'B.Com.', 'M.Sc.', 'M.A.', 'M.Eng.', 'MBA', 'Ph.D.', 'J.D.', 'M.D.'],
                    },
                    { key: 'company', placeholder: 'Major / Field of Study' },
                    { key: 'duration', placeholder: 'Date Range' },
                  ]}
                />
              ))}
          </section>

          {/* Experience */}
          <section className={styles.formSection}>
            <SectionHeader
              title="Experience"
              collapsed={collapsed.experience}
              onToggle={() => toggleSection('experience')}
              onAdd={() => addEntry('experience')}
            />
            {!collapsed.experience && sec.experience.length === 0 && (
              <p className={styles.emptyHint}>No experience entries yet — click + Add</p>
            )}
            {!collapsed.experience &&
              sec.experience.map((item) => (
                <EntryCard
                  key={item.id}
                  item={item}
                  onUpdate={(u) => updateEntry('experience', u)}
                  onRemove={() => removeEntry('experience', item.id)}
                  fields={[
                    { key: 'title', placeholder: 'Job Title' },
                    { key: 'company', placeholder: 'Company' },
                    { key: 'duration', placeholder: 'Date Range' },
                  ]}
                />
              ))}
          </section>

          {/* Projects (drop zone) */}
          <section className={styles.formSection}>
            <SectionHeader
              title="Projects"
              collapsed={collapsed.projects}
              onToggle={() => toggleSection('projects')}
              onAdd={() => addEntry('projects')}
            />
            {!collapsed.projects && (
              <>
                {sec.projects.length === 0 && (
                  <p className={styles.emptyHint}>
                    No projects yet — drag items from the left panel or click + Add
                  </p>
                )}
                {sec.projects.map((item) => (
                  <EntryCard
                    key={item.id}
                    item={item}
                    onUpdate={(u) => updateEntry('projects', u)}
                    onRemove={() => removeEntry('projects', item.id)}
                    fields={[
                      { key: 'title', placeholder: 'Project Name' },
                      { key: 'company', placeholder: 'Technologies Used' },
                      { key: 'duration', placeholder: 'Date Range' },
                    ]}
                  />
                ))}
              </>
            )}
          </section>

          {/* Skills */}
          <section className={styles.formSection}>
            <SectionHeader
              title="Skills"
              collapsed={collapsed.skills}
              onToggle={() => toggleSection('skills')}
              onAdd={() => {
                const newSkill = { id: Date.now(), title: '' };
                const updated = {
                  ...resumeData,
                  sections: {
                    ...sec,
                    skills: [...sec.skills, newSkill],
                  },
                };
                setResumeData(updated);
                pushToHistory(updated);
              }}
            />
            {!collapsed.skills && sec.skills.length === 0 && (
              <p className={styles.emptyHint}>No skills yet — drag from the panel or click + Add</p>
            )}
            {!collapsed.skills && (
              <div className={styles.skillsGrid}>
                {sec.skills.map((skill) => (
                  <div key={skill.id} className={styles.skillChip}>
                    <input
                      className={styles.skillInput}
                      value={skill.title || ''}
                      onChange={(e) => {
                        const items = sec.skills.map((s) =>
                          s.id === skill.id ? { ...s, title: e.target.value } : s
                        );
                        setResumeData((prev) => ({
                          ...prev,
                          sections: { ...prev.sections, skills: items },
                        }));
                      }}
                      onBlur={flushPersonal}
                      placeholder="Skill"
                    />
                    <button
                      className={styles.removeSkillBtn}
                      onClick={() => removeEntry('skills', skill.id)}
                      type="button"
                    >
                      ×
                    </button>
                  </div>
                ))}
              </div>
            )}
          </section>

          {/* Certifications */}
          <section className={styles.formSection}>
            <SectionHeader
              title="Certifications"
              collapsed={collapsed.certifications}
              onToggle={() => toggleSection('certifications')}
              onAdd={() => addEntry('certifications')}
            />
            {!collapsed.certifications && sec.certifications.length === 0 && (
              <p className={styles.emptyHint}>No certifications yet — click + Add</p>
            )}
            {!collapsed.certifications &&
              sec.certifications.map((item) => (
                <EntryCard
                  key={item.id}
                  item={item}
                  onUpdate={(u) => updateEntry('certifications', u)}
                  onRemove={() => removeEntry('certifications', item.id)}
                  fields={[
                    { key: 'title', placeholder: 'Certification Name' },
                    { key: 'company', placeholder: 'Issuing Organization' },
                    { key: 'duration', placeholder: 'Date' },
                  ]}
                />
              ))}
          </section>
        </main>

        {/* drag handle: editor ↔ preview */}
        <div
          className={`${styles.dragHandle} ${styles.previewHandle}`}
          onMouseDown={startDrag('right')}
          title="Drag to resize"
        />

        {/* ── Right: Live Preview ── */}
        <aside className={styles.previewPanel} style={{ width: previewWidth }}>
          <div className={styles.previewHeader}>Preview</div>
          <ResumePreview resumeData={resumeData} />
        </aside>
      </div>
    </div>
  );
}
