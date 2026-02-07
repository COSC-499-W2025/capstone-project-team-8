'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/AuthContext';
import Header from '@/components/Header';
import Toast from '@/components/Toast';
import { getCurrentUser } from '@/utils/api';
import { 
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
import { cleanResumeForExport, getProjectDateRange, formatTimestampToDate } from '@/utils/resumeCleanup';
import { 
  getTemplateComponent, 
  getTemplateMetadata,
  getNextTemplateIndex,
  getPreviousTemplateIndex,
  getTemplateCount
} from '@/utils/TemplateRegistry';
import ProjectsPanel from '@/components/resume/ProjectsPanel';
import styles from './resume.module.css';

export default function ResumePage() {
  const router = useRouter();
  const { isAuthenticated, token } = useAuth();
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState({ type: '', text: '' });

  // Undo/Redo history
  const [history, setHistory] = useState([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const historyRef = useRef(null);

  // Main state
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

  const currentTemplate = getTemplateMetadata(templateIndex);
  const TemplateComponent = getTemplateComponent(templateIndex);

  // Initialize page
  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }

    // Don't proceed if token hasn't been loaded yet
    if (!token) {
      return;
    }

    const initializeResumePage = async () => {
      try {
        const [userData, projectsData, previewData] = await Promise.all([
          getCurrentUser(token),
          getProjects(token),
          getResumePreview(token),
        ]);

        // Build name from user data
        const userFullName = (() => {
          const firstName = userData.user?.first_name || '';
          const lastName = userData.user?.last_name || '';
          if (firstName && lastName) return `${firstName} ${lastName}`;
          if (firstName) return firstName;
          if (lastName) return lastName;
          return 'Your Name';
        })();

        // Handle projects - ensure it's an array with all details
        const projectsList = Array.isArray(projectsData) 
          ? projectsData 
          : (projectsData.projects || projectsData.results || []);
        console.log('Projects loaded:', projectsList);
        setProjects(projectsList);

        // Build initial education entry from user data
        const userEducation = [];
        if (userData.user?.university || userData.user?.degree_major) {
          const degreeTitle = userData.user?.degree_major ? 
            `${userData.user.degree_major}` : 'Degree';
          const university = userData.user?.university || '';
          
          let duration = '';
          if (userData.user?.expected_graduation) {
            const gradDate = new Date(userData.user.expected_graduation);
            duration = `Expected ${gradDate.getFullYear()}`;
          }
          
          userEducation.push({
            id: 1,
            title: degreeTitle,
            company: university,
            duration: duration,
            content: userData.user?.education_city || ''
          });
        }

        // Load resume from backend context (has user's actual data)
        if (previewData && previewData.context) {
          const context = previewData.context;
          setResumeData(prev => ({
            ...prev,
            name: context.summary?.user_name || userFullName,
            sections: {
              summary: context.summary?.summary || prev.sections.summary,
              experience: context.experience || prev.sections.experience,
              education: context.education && context.education.length > 0 
                ? context.education 
                : userEducation.length > 0 ? userEducation : prev.sections.education,
              skills: context.skills || prev.sections.skills,
              certifications: context.certifications || prev.sections.certifications,
              projects: []
            }
          }));
        } else {
          // Fallback: Load saved draft or use user data
          const savedDraft = getCurrentDraft();
          if (savedDraft && savedDraft.resumeData) {
            setResumeData(savedDraft.resumeData);
          } else {
            // Use user data to populate resume
            setResumeData(prev => ({
              ...prev,
              name: userFullName,
              sections: {
                ...prev.sections,
                education: userEducation.length > 0 ? userEducation : prev.sections.education
              }
            }));
          }
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

  // Undo/Redo functions
  const pushToHistory = (data) => {
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(JSON.parse(JSON.stringify(data)));
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const undo = () => {
    if (historyIndex > 0) {
      const newIndex = historyIndex - 1;
      setResumeData(JSON.parse(JSON.stringify(history[newIndex])));
      setHistoryIndex(newIndex);
      setMessage({ type: 'info', text: 'Undo completed' });
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      const newIndex = historyIndex + 1;
      setResumeData(JSON.parse(JSON.stringify(history[newIndex])));
      setHistoryIndex(newIndex);
      setMessage({ type: 'info', text: 'Redo completed' });
    }
  };

  // Navigation
  const nextTemplate = useCallback(() => {
    setTemplateIndex(getNextTemplateIndex(templateIndex));
  }, [templateIndex]);

  const prevTemplate = useCallback(() => {
    setTemplateIndex(getPreviousTemplateIndex(templateIndex));
  }, [templateIndex]);

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
      
      // Track history
      if (historyRef.current) {
        clearTimeout(historyRef.current);
      }
      historyRef.current = setTimeout(() => {
        pushToHistory(newData);
      }, 500); // Debounce history tracking
      
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

  const saveResume = async () => {
    try {
      await generateResume(token, resumeData.name || 'My Resume', resumeData.sections);
      setMessage({ type: 'success', text: 'Resume saved successfully' });
    } catch (err) {
      console.error('Save error:', err);
      setMessage({ type: 'error', text: 'Failed to save resume' });
    }
  };

  const addProjectBullet = (projectId) => {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    // Create a project item with resume bullet points from backend
    const projectItem = {
      id: Date.now(),
      title: project.name,
      company: project.classification_type || 'Project',
      duration: '',
      content: (project.resume_bullet_points || []).join('\n')
    };

    setResumeData(prev => ({
      ...prev,
      sections: {
        ...prev.sections,
        projects: [...(prev.sections.projects || []), projectItem]
      }
    }));

    setSelectedProjects(prev => new Set(prev).add(projectId));
  };

  // Drag and Drop handlers
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  };

  const handleDropSkill = (e) => {
    e.preventDefault();
    try {
      const data = JSON.parse(e.dataTransfer.getData('application/json'));
      if (data.type === 'skill') {
        const timestamp = Date.now();
        
        // Determine if we should add skill or create experience entry with project context
        if (data.projectName) {
          // Check if experience entry for this project already exists
          const existingIndex = (resumeData.sections.experience || []).findIndex(
            exp => exp.company === data.projectName
          );
          
          const dateRange = getProjectDateRange(data.projectFirstCommitDate, data.projectCreatedAt);
          const skillText = `Worked with ${data.item.title} on ${data.projectName}`;
          
          let updatedExperience;
          
          if (existingIndex >= 0) {
            // Append to existing entry
            updatedExperience = [...(resumeData.sections.experience || [])];
            const existingEntry = updatedExperience[existingIndex];
            updatedExperience[existingIndex] = {
              ...existingEntry,
              content: `${existingEntry.content}\n• ${data.item.title}`
            };
            setMessage({ type: 'success', text: `Added "${data.item.title}" to ${data.projectName}` });
          } else {
            // Create new entry with bullet point
            const newExperience = {
              id: timestamp,
              title: data.item.title,
              company: data.projectName,
              duration: dateRange,
              content: `• ${data.item.title}`
            };
            updatedExperience = [...(resumeData.sections.experience || []), newExperience];
            setMessage({ type: 'success', text: `Added "${data.item.title}" from ${data.projectName}` });
          }
          
          setResumeData(prev => ({
            ...prev,
            sections: {
              ...prev.sections,
              experience: updatedExperience
            }
          }));
          
          pushToHistory({
            ...resumeData,
            sections: {
              ...resumeData.sections,
              experience: updatedExperience
            }
          });
        } else {
          // Simple skill addition without project context
          const newSkill = {
            id: timestamp,
            title: data.item.title
          };
          
          setResumeData(prev => ({
            ...prev,
            sections: {
              ...prev.sections,
              skills: [...(prev.sections.skills || []), newSkill]
            }
          }));
          
          pushToHistory({
            ...resumeData,
            sections: {
              ...resumeData.sections,
              skills: [...(resumeData.sections.skills || []), newSkill]
            }
          });
          
          setMessage({ type: 'success', text: 'Skill added!' });
        }
      }
    } catch (err) {
      console.error('Drop error:', err);
    }
  };

  const handleDropExperience = (e) => {
    e.preventDefault();
    try {
      const data = JSON.parse(e.dataTransfer.getData('application/json'));
      if (data.type === 'bullet') {
        // Extract project info from drag data
        const projectName = data.projectName || 'Project Work';
        const dateRange = getProjectDateRange(data.projectFirstCommitDate, data.projectCreatedAt);
        
        // Check if experience entry for this project already exists
        const existingIndex = (resumeData.sections.experience || []).findIndex(
          exp => exp.title === projectName
        );
        
        let updatedExperience;
        
        if (existingIndex >= 0) {
          // Append to existing entry
          updatedExperience = [...(resumeData.sections.experience || [])];
          const existingEntry = updatedExperience[existingIndex];
          updatedExperience[existingIndex] = {
            ...existingEntry,
            content: `${existingEntry.content}\n• ${data.item.content}`
          };
          setMessage({ type: 'success', text: `Added to ${projectName}` });
        } else {
          // Create new entry with bullet
          const newExperience = {
            id: Date.now(),
            title: projectName,
            company: '',
            duration: dateRange,
            content: `• ${data.item.content}`
          };
          updatedExperience = [...(resumeData.sections.experience || []), newExperience];
          setMessage({ type: 'success', text: `Added achievement from ${projectName}` });
        }
        
        setResumeData(prev => ({
          ...prev,
          sections: {
            ...prev.sections,
            experience: updatedExperience
          }
        }));
        
        pushToHistory({
          ...resumeData,
          sections: {
            ...resumeData.sections,
            experience: updatedExperience
          }
        });
      }
    } catch (err) {
      console.error('Drop error:', err);
    }
  };

  const handleQuickAdd = (item, type) => {
    if (type === 'skill') {
      const timestamp = Date.now();
      
      // Determine if we should add skill or create experience entry with project context
      if (item.projectName) {
        // Need to find the project to get dates - look through projects array
        const project = projects.find(p => p.id === item.projectId);
        const dateRange = project 
          ? getProjectDateRange(project.first_commit_date, project.created_at)
          : 'Present';
        
        // Check if experience entry for this project already exists
        const existingIndex = (resumeData.sections.experience || []).findIndex(
          exp => exp.company === item.projectName
        );
        
        let updatedExperience;
        
        if (existingIndex >= 0) {
          // Append to existing entry
          updatedExperience = [...(resumeData.sections.experience || [])];
          const existingEntry = updatedExperience[existingIndex];
          updatedExperience[existingIndex] = {
            ...existingEntry,
            content: `${existingEntry.content}\n• ${item.title}`
          };
          setMessage({ type: 'success', text: `Added "${item.title}" to ${item.projectName}` });
        } else {
          // Create new entry with bullet
          const newExperience = {
            id: timestamp,
            title: item.title,
            company: item.projectName,
            duration: dateRange,
            content: `• ${item.title}`
          };
          updatedExperience = [...(resumeData.sections.experience || []), newExperience];
          setMessage({ type: 'success', text: `Added "${item.title}" from ${item.projectName}` });
        }
        
        setResumeData(prev => ({
          ...prev,
          sections: {
            ...prev.sections,
            experience: updatedExperience
          }
        }));
        
        pushToHistory({
          ...resumeData,
          sections: {
            ...resumeData.sections,
            experience: updatedExperience
          }
        });
      } else {
        // Simple skill addition
        const newSkill = {
          id: timestamp,
          title: item.title
        };
        
        setResumeData(prev => ({
          ...prev,
          sections: {
            ...prev.sections,
            skills: [...(prev.sections.skills || []), newSkill]
          }
        }));
        
        pushToHistory({
          ...resumeData,
          sections: {
            ...resumeData.sections,
            skills: [...(resumeData.sections.skills || []), newSkill]
          }
        });
        
        setMessage({ type: 'success', text: 'Skill added!' });
      }
    } else if (type === 'bullet') {
      // Find project to get dates
      const project = projects.find(p => p.id === item.projectId);
      const projectName = item.projectName || 'Project Work';
      const dateRange = project 
        ? getProjectDateRange(project.first_commit_date, project.created_at)
        : 'Present';
      
      // Check if experience entry for this project already exists
      const existingIndex = (resumeData.sections.experience || []).findIndex(
        exp => exp.title === projectName
      );
      
      let updatedExperience;
      
      if (existingIndex >= 0) {
        // Append to existing entry
        updatedExperience = [...(resumeData.sections.experience || [])];
        const existingEntry = updatedExperience[existingIndex];
        updatedExperience[existingIndex] = {
          ...existingEntry,
          content: `${existingEntry.content}\n• ${item.content}`
        };
        setMessage({ type: 'success', text: `Added to ${projectName}` });
      } else {
        // Create new entry with bullet
        const newExperience = {
          id: Date.now(),
          title: projectName,
          company: '',
          duration: dateRange,
          content: `• ${item.content}`
        };
        updatedExperience = [...(resumeData.sections.experience || []), newExperience];
        setMessage({ type: 'success', text: `Added achievement from ${projectName}` });
      }
      
      setResumeData(prev => ({
        ...prev,
        sections: {
          ...prev.sections,
          experience: updatedExperience
        }
      }));
      
      pushToHistory({
        ...resumeData,
        sections: {
          ...resumeData.sections,
          experience: updatedExperience
        }
      });
    }
  };

  const reorderItems = (sectionType, fromIndex, toIndex) => {
    setResumeData(prev => {
      const newData = JSON.parse(JSON.stringify(prev));
      const items = newData.sections[sectionType];
      const [movedItem] = items.splice(fromIndex, 1);
      items.splice(toIndex, 0, movedItem);
      
      pushToHistory(newData);
      return newData;
    });
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
      
      // Remove all edit controls from clone
      const editButtons = clone.querySelectorAll('button');
      editButtons.forEach(btn => btn.remove());
      
      // Remove max-height constraint from the clone
      const wrapper = clone.querySelector('[style*="max-height"]');
      if (wrapper) {
        wrapper.style.maxHeight = 'none';
        wrapper.style.overflow = 'visible';
      }
      
      // Use cleaned resume data
      const cleanedResume = cleanResumeForExport(resumeData);
      
      const options = {
        margin: [8, 8, 8, 8],
        filename: `${cleanedResume.name || 'resume'}.pdf`,
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
      // Clean the resume data before sending
      const cleanedResume = cleanResumeForExport(resumeData);
      
      // First save the cleaned resume to ensure backend has latest edits
      await generateResume(token, cleanedResume.name || 'My Resume', cleanedResume.sections);
      
      // Then generate LaTeX from backend (will use saved data)
      await generateLatexResume(token);
      
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
        {/* Left Sidebar - Projects Panel */}
        <div className={styles.leftSidebar}>
          <div className={styles.sidebarSection}>
            <div className={styles.sidePanelHeader}>
              <h3>Templates</h3>
            </div>
            <div className={styles.templateNav}>
              <button onClick={prevTemplate} className={styles.navButton}>← Prev</button>
              <div className={styles.templateName}>{currentTemplate?.name || 'Select'}</div>
              <button onClick={nextTemplate} className={styles.navButton}>Next →</button>
            </div>
          </div>

          <div className={styles.sidebarDivider} />

          <div className={styles.sidebarSection}>
            <div className={styles.sidePanelHeader}>
              <h3>Edit Controls</h3>
            </div>
            <div className={styles.controlsGroup}>
              <button 
                onClick={undo} 
                disabled={historyIndex <= 0}
                className={styles.controlBtn}
                title="Undo (Ctrl+Z)"
              >
                ↶ Undo
              </button>
              <button 
                onClick={redo} 
                disabled={historyIndex >= history.length - 1}
                className={styles.controlBtn}
                title="Redo (Ctrl+Y)"
              >
                ↷ Redo
              </button>
            </div>
          </div>

          <div className={styles.sidebarDivider} />

          <ProjectsPanel 
            projects={projects}
            onAddItem={handleQuickAdd}
          />
        </div>

        {/* Main Resume Editor - Center */}
        <div className={styles.mainResume}>
          <div 
            className={styles.resumeEditorWrapper} 
            id="resume-preview"
            onDragOver={handleDragOver}
          >
            <TemplateComponent
              data={resumeData}
              onEdit={updateResumeData}
              onAddSection={addSection}
              onRemoveSection={removeSection}
              onDeleteContent={(path) => updateResumeData(path, '')}
              editingPath={editingPath}
              setEditingPath={setEditingPath}
              onDropSkill={handleDropSkill}
              onDropExperience={handleDropExperience}
              onReorder={reorderItems}
            />
          </div>

          <div className={styles.exportButtons}>
            <button onClick={saveResume} className={styles.btn}>💾 Save</button>
            <button onClick={exportPDF} className={styles.btn}>📄 PDF</button>
            <button onClick={exportLatex} className={styles.btn}>📝 LaTeX</button>
          </div>
        </div>
      </div>
    </div>
  );
}
