import { useState } from 'react';
import styles from './ModernTemplate.module.css';

/**
 * ModernTemplate Component
 * 
 * Clean, contemporary resume template with modern design principles.
 * Features: accent colors, better spacing, modern typography
 * Users can click text to edit, delete sections, and add new sections.
 */
export default function ModernTemplate({
  data,
  onEdit,
  onAddSection,
  onRemoveSection,
  onDeleteContent,
  editingPath,
  setEditingPath
}) {
  const [editValue, setEditValue] = useState('');

  const startEdit = (path, currentValue) => {
    setEditingPath(path);
    setEditValue(currentValue || '');
  };

  const finishEdit = (path) => {
    onEdit(path, editValue);
    setEditingPath(null);
    setEditValue('');
  };

  const EditableField = ({ path, value, placeholder, multiline = false, className = '' }) => {
    const isEditing = editingPath === path;

    if (isEditing) {
      return (
        <div className={styles.editingContainer}>
          {multiline ? (
            <textarea
              autoFocus
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              placeholder={placeholder}
              className={styles.textarea}
              onBlur={() => finishEdit(path)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && e.ctrlKey) {
                  finishEdit(path);
                }
              }}
            />
          ) : (
            <input
              autoFocus
              value={editValue}
              onChange={(e) => setEditValue(e.target.value)}
              placeholder={placeholder}
              className={styles.input}
              onBlur={() => finishEdit(path)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  finishEdit(path);
                }
              }}
            />
          )}
        </div>
      );
    }

    return (
      <div 
        className={`${styles.editableField} ${className}`}
        onClick={() => startEdit(path, value)}
        title="Click to edit"
      >
        {value || <span className={styles.placeholder}>{placeholder}</span>}
      </div>
    );
  };

  return (
    <div className={styles.resumeTemplate}>
      {/* Header with accent */}
      <div className={styles.header}>
        <EditableField
          path="name"
          value={data.name}
          placeholder="Your Name"
          className={styles.nameField}
        />
      </div>

      {/* Summary Section */}
      <section className={styles.section}>
        <h3 className={styles.sectionTitle}>Summary</h3>
        <div className={styles.sectionContent}>
          <EditableField
            path="sections.summary"
            value={data.sections.summary}
            placeholder="Professional summary..."
            multiline
            className={styles.summaryField}
          />
        </div>
      </section>

      {/* Experience Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3 className={styles.sectionTitle}>Experience</h3>
          <button 
            onClick={() => onAddSection('experience')}
            className={styles.addBtn}
            title="Add experience"
          >
            +
          </button>
        </div>
        <div className={styles.sectionContent}>
          {data.sections.experience && data.sections.experience.length > 0 ? (
            data.sections.experience.map((item, idx) => (
              <div key={item.id} className={styles.experienceItem}>
                <div className={styles.itemHeader}>
                  <div>
                    <EditableField
                      path={`sections.experience.${idx}.title`}
                      value={item.title}
                      placeholder="Position"
                      className={styles.boldField}
                    />
                    <EditableField
                      path={`sections.experience.${idx}.company`}
                      value={item.company}
                      placeholder="Company"
                      className={styles.companyField}
                    />
                  </div>
                  <button 
                    onClick={() => onRemoveSection('experience', item.id)}
                    className={styles.deleteBtn}
                  >
                    ✕
                  </button>
                </div>
                <EditableField
                  path={`sections.experience.${idx}.duration`}
                  value={item.duration}
                  placeholder="Jan 2020 - Present"
                  className={styles.durationField}
                />
                <EditableField
                  path={`sections.experience.${idx}.content`}
                  value={item.content}
                  placeholder="Describe achievements..."
                  className={styles.descriptionField}
                />
              </div>
            ))
          ) : (
            <p className={styles.emptyState}>No experience added</p>
          )}
        </div>
      </section>

      {/* Education Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3 className={styles.sectionTitle}>Education</h3>
          <button 
            onClick={() => onAddSection('education')}
            className={styles.addBtn}
          >
            +
          </button>
        </div>
        <div className={styles.sectionContent}>
          {data.sections.education && data.sections.education.length > 0 ? (
            data.sections.education.map((item, idx) => (
              <div key={item.id} className={styles.educationItem}>
                <div className={styles.itemHeader}>
                  <div>
                    <EditableField
                      path={`sections.education.${idx}.title`}
                      value={item.title}
                      placeholder="Degree"
                      className={styles.boldField}
                    />
                    <EditableField
                      path={`sections.education.${idx}.company`}
                      value={item.company}
                      placeholder="School"
                      className={styles.companyField}
                    />
                  </div>
                  <button 
                    onClick={() => onRemoveSection('education', item.id)}
                    className={styles.deleteBtn}
                  >
                    ✕
                  </button>
                </div>
                <EditableField
                  path={`sections.education.${idx}.duration`}
                  value={item.duration}
                  placeholder="2015 - 2019"
                  className={styles.durationField}
                />
                <EditableField
                  path={`sections.education.${idx}.content`}
                  value={item.content}
                  placeholder="GPA, honors..."
                  className={styles.descriptionField}
                />
              </div>
            ))
          ) : (
            <p className={styles.emptyState}>No education added</p>
          )}
        </div>
      </section>

      {/* Skills Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3 className={styles.sectionTitle}>Skills</h3>
          <button 
            onClick={() => onAddSection('skills')}
            className={styles.addBtn}
          >
            +
          </button>
        </div>
        <div className={styles.sectionContent}>
          {data.sections.skills && data.sections.skills.length > 0 ? (
            <div className={styles.skillsList}>
              {data.sections.skills.map((skill, idx) => (
                <div key={skill.id} className={styles.skillTag}>
                  <EditableField
                    path={`sections.skills.${idx}.title`}
                    value={skill.title}
                    placeholder="Skill"
                    className={styles.skillField}
                  />
                  <button 
                    onClick={() => onRemoveSection('skills', skill.id)}
                    className={styles.deleteBtn}
                  >
                    ✕
                  </button>
                </div>
              ))}
            </div>
          ) : (
            <p className={styles.emptyState}>No skills added</p>
          )}
        </div>
      </section>

      {/* Certifications Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3 className={styles.sectionTitle}>Certifications</h3>
          <button 
            onClick={() => onAddSection('certifications')}
            className={styles.addBtn}
          >
            +
          </button>
        </div>
        <div className={styles.sectionContent}>
          {data.sections.certifications && data.sections.certifications.length > 0 ? (
            data.sections.certifications.map((item, idx) => (
              <div key={item.id} className={styles.certificationItem}>
                <div className={styles.itemHeader}>
                  <div>
                    <EditableField
                      path={`sections.certifications.${idx}.title`}
                      value={item.title}
                      placeholder="Certification"
                      className={styles.boldField}
                    />
                    <EditableField
                      path={`sections.certifications.${idx}.company`}
                      value={item.company}
                      placeholder="Organization"
                      className={styles.companyField}
                    />
                  </div>
                  <button 
                    onClick={() => onRemoveSection('certifications', item.id)}
                    className={styles.deleteBtn}
                  >
                    ✕
                  </button>
                </div>
                <EditableField
                  path={`sections.certifications.${idx}.duration`}
                  value={item.duration}
                  placeholder="Year"
                  className={styles.durationField}
                />
                <EditableField
                  path={`sections.certifications.${idx}.content`}
                  value={item.content}
                  placeholder="Details..."
                  className={styles.descriptionField}
                />
              </div>
            ))
          ) : (
            <p className={styles.emptyState}>No certifications added</p>
          )}
        </div>
      </section>
    </div>
  );
}
