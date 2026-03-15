'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import Toast from '@/components/Toast';
import { listResumes } from '@/utils/resumeApi';
import styles from './resumes.module.css';

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
          <h1>My Resumes</h1>
          <button className={styles.btnNew} onClick={handleNewResume}>
            + Create New Resume
          </button>
        </div>

        {resumes.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No resumes yet. Create your first resume!</p>
            <button className={styles.btnCreate} onClick={handleNewResume}>
              Build Your First Resume
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
                <h3>{resume.name}</h3>
                <p className={styles.date}>
                  Updated: {new Date(resume.updated_at).toLocaleDateString()}
                </p>
                <p className={styles.meta}>
                  Theme: {resume.theme || 'classic'}
                </p>
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
