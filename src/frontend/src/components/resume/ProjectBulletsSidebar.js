import { useState } from 'react';
import styles from './ProjectBulletsSidebar.module.css';

export default function ProjectBulletsSidebar({ projects, onAddBullet }) {
  const [expandedProject, setExpandedProject] = useState(null);

  const toggleProject = (projectId) => {
    setExpandedProject(expandedProject === projectId ? null : projectId);
  };

  // Ensure projects is an array
  const projectsList = Array.isArray(projects) ? projects : [];

  if (!projectsList || projectsList.length === 0) {
    return (
      <div className={styles.empty}>
        <p>No projects found. Upload projects to get started!</p>
      </div>
    );
  }

  return (
    <div className={styles.sidebar}>
      {projectsList.map((project) => (
        <div key={project.id} className={styles.projectItem}>
          <div 
            className={styles.projectHeader}
            onClick={() => toggleProject(project.id)}
          >
            <span className={styles.chevron}>
              {expandedProject === project.id ? '▼' : '▶'}
            </span>
            <div className={styles.projectTitle}>
              <h3>{project.name}</h3>
              {project.thumbnail && (
                <img src={project.thumbnail} alt={project.name} className={styles.thumbnail} />
              )}
            </div>
          </div>

          {expandedProject === project.id && (
            <div className={styles.bulletsList}>
              {project.resume_bullet_points && project.resume_bullet_points.length > 0 ? (
                project.resume_bullet_points.map((bullet, index) => (
                  <div key={index} className={styles.bulletItem}>
                    <div className={styles.bulletText}>{bullet}</div>
                    <button
                      className={styles.addBtn}
                      onClick={() => onAddBullet(bullet, project.id)}
                      title="Add to resume"
                    >
                      +
                    </button>
                  </div>
                ))
              ) : (
                <p className={styles.noBullets}>No bullet points generated for this project yet.</p>
              )}
            </div>
          )}

          {project.description && (
            <div className={styles.projectDescription}>
              <p>{project.description}</p>
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
