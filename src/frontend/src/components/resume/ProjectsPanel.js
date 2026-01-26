/**
 * ProjectsPanel Component
 * 
 * Displays all user projects with their skills and bullet points
 * Items are draggable and can be added to the resume
 */

import { useState, useEffect } from 'react';
import styles from './ProjectsPanel.module.css';

export default function ProjectsPanel({ projects, onAddItem }) {
  const [expandedProjects, setExpandedProjects] = useState(new Set());
  const [draggedItem, setDraggedItem] = useState(null);

  // Debug: Log projects when they arrive
  useEffect(() => {
    if (projects && projects.length > 0) {
      console.log('ProjectsPanel received projects:', projects);
    }
  }, [projects]);

  const toggleProject = (projectId) => {
    const newExpanded = new Set(expandedProjects);
    if (newExpanded.has(projectId)) {
      newExpanded.delete(projectId);
    } else {
      newExpanded.add(projectId);
    }
    setExpandedProjects(newExpanded);
  };

  const handleDragStart = (e, item, type, project) => {
    setDraggedItem({ item, type });
    e.dataTransfer.effectAllowed = 'copy';
    // Include full project info with the drag data
    const dragData = {
      item,
      type,
      projectId: project.id,
      projectName: project.name,
      projectCreatedAt: project.created_at,
      projectFirstCommitDate: project.first_commit_date
    };
    e.dataTransfer.setData('application/json', JSON.stringify(dragData));
  };

  const handleDragEnd = () => {
    setDraggedItem(null);
  };

  const handleQuickAdd = (item, type) => {
    if (onAddItem) {
      onAddItem(item, type);
    }
  };

  if (!projects || projects.length === 0) {
    return (
      <div className={styles.panel}>
        <h3 className={styles.panelTitle}>Projects</h3>
        <p className={styles.empty}>No projects yet. Upload some to get started!</p>
      </div>
    );
  }

  return (
    <div className={styles.panel}>
      <h3 className={styles.panelTitle}>Projects</h3>
      <p className={styles.hint}>Drag items into resume or click to add</p>

      <div className={styles.projectsList}>
        {projects.map(project => (
          <div key={project.id} className={styles.projectItem}>
            <div
              className={styles.projectHeader}
              onClick={() => toggleProject(project.id)}
            >
              <span className={styles.arrow}>
                {expandedProjects.has(project.id) ? '▼' : '▶'}
              </span>
              <div className={styles.projectInfo}>
                <h4 className={styles.projectName}>{project.name}</h4>
                <p className={styles.projectType}>{project.classification_type || 'Project'}</p>
              </div>
            </div>

            {expandedProjects.has(project.id) && (
              <div className={styles.projectContent}>
                {/* Skills Section */}
                {project.languages && project.languages.length > 0 && (
                  <div className={styles.section}>
                    <h5 className={styles.sectionTitle}>Languages</h5>
                    <div className={styles.skillsList}>
                      {project.languages.map(lang => (
                        <div
                          key={`lang-${lang.id}`}
                          className={`${styles.skill} ${draggedItem?.item?.id === `lang-${lang.id}` ? styles.dragging : ''}`}
                          draggable
                          onDragStart={(e) =>
                            handleDragStart(e, { id: `lang-${lang.id}`, title: lang.name, type: 'language' }, 'skill', project)
                          }
                          onDragEnd={handleDragEnd}
                        >
                          <span className={styles.skillText}>{lang.name}</span>
                          <button
                            className={styles.quickAddBtn}
                            onClick={() => handleQuickAdd({ title: lang.name, projectName: project.name, projectId: project.id }, 'skill')}
                            title="Add to Skills"
                          >
                            +
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Frameworks Section */}
                {project.frameworks && project.frameworks.length > 0 && (
                  <div className={styles.section}>
                    <h5 className={styles.sectionTitle}>Frameworks</h5>
                    <div className={styles.skillsList}>
                      {project.frameworks.map(fw => (
                        <div
                          key={`fw-${fw.id}`}
                          className={`${styles.skill} ${draggedItem?.item?.id === `fw-${fw.id}` ? styles.dragging : ''}`}
                          draggable
                          onDragStart={(e) =>
                            handleDragStart(e, { id: `fw-${fw.id}`, title: fw.name, type: 'framework' }, 'skill', project)
                          }
                          onDragEnd={handleDragEnd}
                        >
                          <span className={styles.skillText}>{fw.name}</span>
                          <button
                            className={styles.quickAddBtn}
                            onClick={() => handleQuickAdd({ title: fw.name, projectName: project.name, projectId: project.id }, 'skill')}
                            title="Add to Skills"
                          >
                            +
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Bullet Points Section */}
                {project.resume_bullet_points && project.resume_bullet_points.length > 0 && (
                  <div className={styles.section}>
                    <h5 className={styles.sectionTitle}>Bullet Points</h5>
                    <div className={styles.bulletsList}>
                      {project.resume_bullet_points.map((bullet, idx) => (
                        <div
                          key={`bullet-${project.id}-${idx}`}
                          className={`${styles.bullet} ${draggedItem?.item?.id === `bullet-${project.id}-${idx}` ? styles.dragging : ''}`}
                          draggable
                          onDragStart={(e) =>
                            handleDragStart(
                              e,
                              {
                                id: `bullet-${project.id}-${idx}`,
                                content: bullet,
                                projectName: project.name,
                                projectId: project.id
                              },
                              'bullet',
                              project
                            )
                          }
                          onDragEnd={handleDragEnd}
                          title="Drag to add to experience or click +"
                        >
                          <span className={styles.bulletDot}>•</span>
                          <span className={styles.bulletText}>{bullet}</span>
                          <button
                            className={styles.quickAddBtn}
                            onClick={() => handleQuickAdd({ content: bullet, projectName: project.name, projectId: project.id }, 'bullet')}
                            title="Add to Experience"
                          >
                            +
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
