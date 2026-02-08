'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import Toast from '@/components/Toast';
import styles from './resumes.module.css';

export default function ResumesListPage() {
  const router = useRouter();
  const { isAuthenticated, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [resumes, setResumes] = useState([]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Note: This endpoint would need to be added to the backend
    // For now, we'll show a placeholder
    setLoading(false);
  }, [isAuthenticated, token, router]);

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
      <Toast message={message} />
      
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
            {resumes.map(resume => (
              <div key={resume.id} className={styles.resumeCard}>
                <h3>{resume.name}</h3>
                <p className={styles.date}>
                  Updated: {new Date(resume.updated_at).toLocaleDateString()}
                </p>
                <div className={styles.actions}>
                  <button onClick={() => router.push(`/resume/${resume.id}`)}>
                    Edit
                  </button>
                  <button>Download</button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
