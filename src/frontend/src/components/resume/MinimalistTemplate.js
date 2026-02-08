import { useState } from 'react';
import styles from './MinimalistTemplate.module.css';

/**
 * MinimalistTemplate Component
 * 
 * Sparse, elegant resume template focused on content.
 * Minimal design with essential information only.
 * Users can click text to edit, delete sections, and add new sections.
 */
export default function MinimalistTemplate({
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
      {/* Minimal header */}
      <div className={styles.header}>
        <EditableField
          path="name"
          value={data.name}
          placeholder="Name"
          className={styles.nameField}
        />
      </div>

      {/* Summary - optional, minimal */}
      {data.sections.summary && (
        <section className={styles.section}>
          <EditableField
            path="sections.summary"
            value={data.sections.summary}
            placeholder="Summary..."
            multiline
            className={styles.summaryField}
          />
        </section>
      )}

      {/* Experience */}
      {data.sections.experience && data.sections.experience.length > 0 && (
        <section className={styles.section}>
          <div className={styles.sectionLabel}>EXPERIENCE</div>
          {data.sections.experience.map((item, idx) => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemTop}>
                <EditableField
                  path={`sections.experience.${idx}.title`}
                  value={item.title}
                  placeholder="Position"
                  className={styles.boldField}
                />
                <EditableField
                  path={`sections.experience.${idx}.duration`}
                  value={item.duration}
                  placeholder="Dates"
                  className={styles.dateField}
                />
              </div>
              <EditableField
                path={`sections.experience.${idx}.company`}
                value={item.company}
                placeholder="Company"
                className={styles.companyField}
              />
              {item.content && (
                <EditableField
                  path={`sections.experience.${idx}.content`}
                  value={item.content}
                  placeholder="Details..."
                  className={styles.descriptionField}
                />
              )}
              <button 
                onClick={() => onRemoveSection('experience', item.id)}
                className={styles.deleteBtn}
              >
                remove
              </button>
            </div>
          ))}
          <button 
            onClick={() => onAddSection('experience')}
            className={styles.addBtn}
          >
            + add
          </button>
        </section>
      )}

      {/* Education */}
      {data.sections.education && data.sections.education.length > 0 && (
        <section className={styles.section}>
          <div className={styles.sectionLabel}>EDUCATION</div>
          {data.sections.education.map((item, idx) => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemTop}>
                <EditableField
                  path={`sections.education.${idx}.title`}
                  value={item.title}
                  placeholder="Degree"
                  className={styles.boldField}
                />
                <EditableField
                  path={`sections.education.${idx}.duration`}
                  value={item.duration}
                  placeholder="Year"
                  className={styles.dateField}
                />
              </div>
              <EditableField
                path={`sections.education.${idx}.company`}
                value={item.company}
                placeholder="School"
                className={styles.companyField}
              />
              {item.content && (
                <EditableField
                  path={`sections.education.${idx}.content`}
                  value={item.content}
                  placeholder="Details..."
                  className={styles.descriptionField}
                />
              )}
              <button 
                onClick={() => onRemoveSection('education', item.id)}
                className={styles.deleteBtn}
              >
                remove
              </button>
            </div>
          ))}
          <button 
            onClick={() => onAddSection('education')}
            className={styles.addBtn}
          >
            + add
          </button>
        </section>
      )}

      {/* Skills - inline */}
      {data.sections.skills && data.sections.skills.length > 0 && (
        <section className={styles.section}>
          <div className={styles.sectionLabel}>SKILLS</div>
          <div className={styles.skillsList}>
            {data.sections.skills.map((skill, idx) => (
              <span key={skill.id} className={styles.skill}>
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
              </span>
            ))}
          </div>
          <button 
            onClick={() => onAddSection('skills')}
            className={styles.addBtn}
          >
            + add
          </button>
        </section>
      )}

      {/* Certifications */}
      {data.sections.certifications && data.sections.certifications.length > 0 && (
        <section className={styles.section}>
          <div className={styles.sectionLabel}>CERTIFICATIONS</div>
          {data.sections.certifications.map((item, idx) => (
            <div key={item.id} className={styles.item}>
              <div className={styles.itemTop}>
                <EditableField
                  path={`sections.certifications.${idx}.title`}
                  value={item.title}
                  placeholder="Cert"
                  className={styles.boldField}
                />
                <EditableField
                  path={`sections.certifications.${idx}.duration`}
                  value={item.duration}
                  placeholder="Year"
                  className={styles.dateField}
                />
              </div>
              <EditableField
                path={`sections.certifications.${idx}.company`}
                value={item.company}
                placeholder="Issuer"
                className={styles.companyField}
              />
              {item.content && (
                <EditableField
                  path={`sections.certifications.${idx}.content`}
                  value={item.content}
                  placeholder="ID..."
                  className={styles.descriptionField}
                />
              )}
              <button 
                onClick={() => onRemoveSection('certifications', item.id)}
                className={styles.deleteBtn}
              >
                remove
              </button>
            </div>
          ))}
          <button 
            onClick={() => onAddSection('certifications')}
            className={styles.addBtn}
          >
            + add
          </button>
        </section>
      )}
    </div>
  );
}
