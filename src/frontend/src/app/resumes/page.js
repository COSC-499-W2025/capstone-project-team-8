'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import Toast from '@/components/Toast';
import { listResumes } from '@/utils/resumeApi';
import styles from './resumes.module.css';

function parseBullets(content) {
  if (!content) return [];

  return content
    .split('\n')
    .map((line) => line.replace(/^[•\-]\s*/, '').trim())
    .filter(Boolean);
}

function ResumeCardPreview({ resume }) {
  const content = resume.content || {};
  const sections = content.sections || {};
  const skills = (sections.skills || []).map((skill) => skill.title).filter(Boolean).slice(0, 6);
  const previewSections = [
    {
      label: 'Education',
      items: (sections.education || []).slice(0, 1).map((item) => ({
        title: item.title,
        subtitle: item.company || item.degree_type,
        detail: item.duration,
        bullets: parseBullets(item.content).slice(0, 1),
      })),
    },
    {
      label: 'Experience',
      items: (sections.experience || []).slice(0, 1).map((item) => ({
        title: item.title,
        subtitle: item.company,
        detail: item.duration,
        bullets: parseBullets(item.content).slice(0, 2),
      })),
    },
    {
      label: 'Projects',
      items: (sections.projects || []).slice(0, 2).map((item) => ({
        title: item.title,
        subtitle: item.company,
        detail: item.duration,
        bullets: parseBullets(item.content).slice(0, 2),
      })),
    },
  ].filter((section) => section.items.length > 0);

  return (
    <div className={styles.previewShell}>
      <div className={styles.previewPaper} data-theme={resume.theme || 'classic'}>
        <div className={styles.previewName}>{content.name || resume.name || 'Your Name'}</div>
        <div className={styles.previewContact}>
          {[content.email, content.phone, content.location].filter(Boolean).join(' | ') || 'Contact details'}
        </div>

        {sections.summary && (
          <div className={styles.previewBlock}>
            <div className={styles.previewHeading}>Summary</div>
            <p className={styles.previewSummary}>{sections.summary}</p>
          </div>
        )}

        {previewSections.map((section) => (
          <div key={section.label} className={styles.previewBlock}>
            <div className={styles.previewHeading}>{section.label}</div>
            {section.items.map((item, index) => (
              <div key={`${section.label}-${index}-${item.title || 'item'}-${item.detail || ''}`} className={styles.previewEntry}>
                <div className={styles.previewEntryTop}>
                  <span className={styles.previewEntryTitle}>{item.title || section.label}</span>
                  {item.detail && <span className={styles.previewEntryDate}>{item.detail}</span>}
                </div>
                {item.subtitle && <div className={styles.previewEntrySubtitle}>{item.subtitle}</div>}
                {item.bullets.map((bullet, bulletIndex) => (
                  <div key={`${section.label}-${index}-bullet-${bulletIndex}`} className={styles.previewBullet}>
                    • {bullet}
                  </div>
                ))}
              </div>
            ))}
          </div>
        ))}

        {skills.length > 0 && (
          <div className={styles.previewBlock}>
            <div className={styles.previewHeading}>Skills</div>
            <div className={styles.previewSkills}>{skills.join(' • ')}</div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function ResumesListPage() {
  const router = useRouter();
  const { isAuthenticated, token, loading: authLoading, refreshAccessToken } = useAuth();
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [resumes, setResumes] = useState([]);

  useEffect(() => {
    if (authLoading) return;
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const loadResumes = async () => {
      try {
        let activeToken = token;
        let data;
        try {
          data = await listResumes(activeToken);
        } catch (err) {
          if (err.message?.includes('401')) {
            activeToken = await refreshAccessToken();
            if (!activeToken) throw new Error('Session expired. Please log in again.');
            data = await listResumes(activeToken);
          } else {
            throw err;
          }
        }
        setResumes(Array.isArray(data) ? data : []);
      } catch (err) {
        console.error('Load resumes error:', err);
        setMessage({ type: 'error', text: err.message || 'Failed to load resumes.' });
      } finally {
        setLoading(false);
      }
    };

    loadResumes();
  }, [authLoading, isAuthenticated, token, router, refreshAccessToken]);

  const handleNewResume = () => {
    router.push('/resume');
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <Header />
        <div className={styles.loading}>Loading resumes...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <Header />
      {message.text && (
        <Toast
          message={message.text}
          type={message.type}
          onClose={() => setMessage({ type: '', text: '' })}
        />
      )}
      
      <div className={styles.content}>
        <div className={styles.header}>
          <div>
            <h1>My Resumes</h1>
            <p className={styles.subtitle}>Create and manage your saved resumes</p>
          </div>
          <button className={styles.btnNew} onClick={handleNewResume}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <line x1="12" y1="5" x2="12" y2="19"></line>
              <line x1="5" y1="12" x2="19" y2="12"></line>
            </svg>
            Create New Resume
          </button>
        </div>

        {resumes.length === 0 ? (
          <div className={styles.emptyState}>
            <div className={styles.emptyIcon}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="#4f7cf7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <line x1="16" y1="13" x2="8" y2="13"></line>
                <line x1="16" y1="17" x2="8" y2="17"></line>
                <line x1="10" y1="9" x2="8" y2="9"></line>
              </svg>
            </div>
            <h2>No Resumes Yet</h2>
            <p>Create your first resume to save tailored versions you can revisit, edit, and export later.</p>
            <button className={styles.btnCreate} onClick={handleNewResume}>
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
                <line x1="12" y1="5" x2="12" y2="19"></line>
                <line x1="5" y1="12" x2="19" y2="12"></line>
              </svg>
              Create Your First Resume
            </button>
          </div>
        ) : (
          <div className={styles.resumesList}>
            {resumes.map((resume) => (
              <button
                key={resume.id}
                className={styles.resumeCard}
                onClick={() => router.push(`/resume/${resume.id}`)}
                type="button"
              >
                <ResumeCardPreview resume={resume} />
                <h3>{resume.name}</h3>
                <p className={styles.date}>
                  Updated: {new Date(resume.updated_at).toLocaleDateString()}
                </p>
                <div className={styles.metaRow}>
                  <span className={styles.themeBadge}>{resume.theme || 'classic'}</span>
                </div>
                <div className={styles.actions}>
                  <span className={styles.actionChip}>
                    Edit
                  </span>
                  <span className={styles.actionChip}>
                    {resume.content?.sections?.projects?.length || 0} projects
                  </span>
                </div>
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
