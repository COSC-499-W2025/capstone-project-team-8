'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import Toast from '@/components/Toast';
import { 
  getResumeTemplates, 
  getProjects, 
  generateLatexResume,
  generateResume,
  getResumePreview
} from '@/utils/resumeApi';
import { 
  saveDraft, 
  getDraft, 
  getCurrentDraft,
  clearCurrentDraft 
} from '@/utils/draftStorage';
import ResumeTemplate from '@/components/resume/ResumeTemplate';
import styles from './resume.module.css';

export default function ResumePage() {
  const router = useRouter();
  const { isAuthenticated, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Main state
  const [templates, setTemplates] = useState([]);
  const [templateIndex, setTemplateIndex] = useState(0);
  const [projects, setProjects] = useState([]);
  const [resumeData, setResumeData] = useState({
    name: 'John Anderson',
    sections: {
      summary: 'Results-driven professional with 5+ years of experience in software development and project management. Proven track record of delivering high-impact solutions and leading cross-functional teams to success.',
      experience: [
        {
          id: 1,
          title: 'Senior Software Engineer',
          company: 'Tech Solutions Inc.',
          duration: 'Jan 2022 - Present',
          content: 'Led development of microservices architecture serving 2M+ users. Reduced API latency by 40% through optimization. Mentored team of 5 junior developers.'
        },
        {
          id: 2,
          title: 'Software Developer',
          company: 'Digital Systems Ltd.',
          duration: 'Jun 2019 - Dec 2021',
          content: 'Built and maintained full-stack applications using React and Django. Implemented CI/CD pipeline reducing deployment time by 60%. Collaborated with product team on feature design.'
        }
      ],
      projects: [],
      skills: [
        { id: 1, title: 'Python' },
        { id: 2, title: 'JavaScript/React' },
        { id: 3, title: 'Django' },
        { id: 4, title: 'REST APIs' },
        { id: 5, title: 'PostgreSQL' },
        { id: 6, title: 'Docker' }
      ],
      education: [
        {
          id: 1,
          title: 'Bachelor of Science in Computer Science',
          company: 'State University',
          duration: '2015 - 2019',
          content: 'GPA: 3.8/4.0. Dean\'s List all semesters.'
        }
      ],
      certifications: [
        {
          id: 1,
          title: 'AWS Solutions Architect Associate',
          company: 'Amazon Web Services',
          duration: '2021',
          content: 'Certified in cloud architecture and AWS services.'
        }
      ]
    }
  });

  // UI state
  const [editingPath, setEditingPath] = useState(null);
  const [showProjectMenu, setShowProjectMenu] = useState(false);
  const [selectedProjects, setSelectedProjects] = useState(new Set());

  const currentTemplate = templates[templateIndex] || null;

  // Initialize page
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    const initializeResumePage = async () => {
      try {
        const [templatesData, projectsData] = await Promise.all([
          getResumeTemplates(token),
          getProjects(token),
        ]);

        // Handle templates
        const templatesList = templatesData.templates || templatesData || [];
        setTemplates(Array.isArray(templatesList) ? templatesList : []);
        
        // Handle projects - ensure it's an array with all details
        const projectsList = Array.isArray(projectsData) 
          ? projectsData 
          : (projectsData.results || []);
        setProjects(projectsList);

        // Load saved draft or set default
        const savedDraft = getCurrentDraft();
        if (savedDraft && savedDraft.resumeData) {
          setResumeData(savedDraft.resumeData);
        }

        // Don't show success message on initial load
      } catch (err) {
        console.error('Error initializing resume page:', err);
        setMessage({ 
          type: 'error', 
          text: 'Failed to load templates or projects' 
        });
      } finally {
        setLoading(false);
      }
    };

    initializeResumePage();
  }, [isAuthenticated, token, router]);

  // Navigation
  const nextTemplate = useCallback(() => {
    setTemplateIndex((prev) => (prev + 1) % templates.length);
  }, [templates.length]);

  const prevTemplate = useCallback(() => {
    setTemplateIndex((prev) => (prev - 1 + templates.length) % templates.length);
  }, [templates.length]);

  // Editing functions
  const updateResumeData = (path, value) => {
    setResumeData(prev => {
      const newData = JSON.parse(JSON.stringify(prev));
      const keys = path.split('.');
      let current = newData;
      
      for (let i = 0; i < keys.length - 1; i++) {
        if (!current[keys[i]]) current[keys[i]] = {};
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newData;
    });

    // Auto-save draft
    saveDraft({ resumeData });
  };

  const addSection = (sectionType) => {
    const newSection = {
      id: Date.now(),
      title: '',
      content: ''
    };

    setResumeData(prev => ({
      ...prev,
      sections: {
        ...prev.sections,
        [sectionType]: [...(prev.sections[sectionType] || []), newSection]
      }
    }));
  };

  const removeSection = (sectionType, id) => {
    setResumeData(prev => ({
      ...prev,
      sections: {
        ...prev.sections,
        [sectionType]: prev.sections[sectionType].filter(item => item.id !== id)
      }
    }));
  };

  const addProjectBullet = (projectId) => {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    const projectItem = {
      id: Date.now(),
      name: project.name,
      bullets: project.resume_bullet_points || []
    };

    setResumeData(prev => ({
      ...prev,
      sections: {
        ...prev.sections,
        projects: [...prev.sections.projects, projectItem]
      }
    }));

    setSelectedProjects(prev => new Set(prev).add(projectId));
  };

  const exportPDF = async () => {
    try {
      const html2pdf = (await import('html2pdf.js')).default;
      
      // Wait a moment to ensure all changes are rendered
      await new Promise(resolve => setTimeout(resolve, 100));
      
      const element = document.getElementById('resume-preview');
      
      if (!element) {
        setMessage({ type: 'error', text: 'Resume not found' });
        return;
      }
      
      // Create a clone of the element to avoid modifying the original
      const clone = element.cloneNode(true);
      
      // Remove max-height constraint from the clone
      const wrapper = clone.querySelector('[style*="max-height"]');
      if (wrapper) {
        wrapper.style.maxHeight = 'none';
        wrapper.style.overflow = 'visible';
      }
      
      const options = {
        margin: [8, 8, 8, 8],
        filename: `${resumeData.name || 'resume'}.pdf`,
        image: { type: 'jpeg', quality: 1 },
        html2canvas: { 
          scale: 2,
          useCORS: true,
          logging: false,
          backgroundColor: '#ffffff',
          allowTaint: true,
          windowHeight: clone.scrollHeight || 2000
        },
        jsPDF: { 
          orientation: 'portrait', 
          unit: 'mm', 
          format: 'a4'
        },
        pagebreak: { 
          mode: ['avoid-all', 'css', 'legacy'] 
        }
      };
      
      const pdf = html2pdf().set(options);
      await pdf.from(clone).save();
    } catch (err) {
      console.error('PDF export error:', err);
      setMessage({ type: 'error', text: 'Failed to export PDF' });
    }
  };

  const exportLatex = async () => {
    try {
      const response = await generateLatexResume(token, resumeData);
      const blob = new Blob([response], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `${resumeData.name || 'resume'}.tex`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setMessage({ type: 'success', text: 'LaTeX exported successfully' });
    } catch (err) {
      console.error('LaTeX export error:', err);
      setMessage({ type: 'error', text: 'Failed to export LaTeX' });
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <Header />
        <div className={styles.loadingContainer}>
          <p>Loading resume builder...</p>
        </div>
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

      <div className={styles.resumePageContainer}>
        {/* Side Panel - Left */}
        <div className={styles.sidePanel}>
          <div className={styles.sidePanelHeader}>
            <h3>Template Switcher</h3>
          </div>
          <div className={styles.templateNav}>
            <button onClick={prevTemplate} className={styles.navButton}>← Previous</button>
            <div className={styles.templateName}>{currentTemplate?.name || 'Select Template'}</div>
            <button onClick={nextTemplate} className={styles.navButton}>Next →</button>
          </div>
        </div>

        {/* Main Resume Editor - Center */}
        <div className={styles.mainResume}>
          <div className={styles.resumeEditorWrapper} id="resume-preview">
            <ResumeTemplate
              template={currentTemplate}
              data={resumeData}
              onEdit={updateResumeData}
              onAddSection={addSection}
              onRemoveSection={removeSection}
              onDeleteContent={(path) => updateResumeData(path, '')}
              editingPath={editingPath}
              setEditingPath={setEditingPath}
            />
          </div>

          <div className={styles.exportButtons}>
            <button onClick={exportPDF} className={styles.btn}>PDF Export</button>
            <button onClick={exportLatex} className={styles.btn}>LaTeX Export</button>
          </div>
        </div>
      </div>
    </div>
  );
}
