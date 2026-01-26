'use client';

import { useState } from 'react';
import styles from './ResumeEditor.module.css';

export default function ResumeEditor({ 
  content, 
  onUpdateSection, 
  onRemoveBullet, 
  onReorderBullets 
}) {
  const [draggedIndex, setDraggedIndex] = useState(null);
  const [editingBulletId, setEditingBulletId] = useState(null);
  const [editingText, setEditingText] = useState('');

  // Handle drag start
  const handleDragStart = (index) => {
    setDraggedIndex(index);
  };

  // Handle drag over
  const handleDragOver = (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  // Handle drop to reorder
  const handleDrop = (e, targetIndex) => {
    e.preventDefault();
    if (draggedIndex === null || draggedIndex === targetIndex) return;

    const newOrder = [...content.sections.projects];
    const draggedItem = newOrder[draggedIndex];
    newOrder.splice(draggedIndex, 1);
    newOrder.splice(targetIndex, 0, draggedItem);

    onReorderBullets(newOrder);
    setDraggedIndex(null);
  };

  // Handle edit bullet
  const handleEditBullet = (bulletId, currentText) => {
    setEditingBulletId(bulletId);
    setEditingText(currentText);
  };

  // Handle save edit
  const handleSaveEdit = (bulletId) => {
    const updatedBullets = content.sections.projects.map(b =>
      b.id === bulletId ? { ...b, text: editingText } : b
    );
    onReorderBullets(updatedBullets);
    setEditingBulletId(null);
    setEditingText('');
  };

  // Handle cancel edit
  const handleCancelEdit = () => {
    setEditingBulletId(null);
    setEditingText('');
  };

  // Handle add section
  const handleAddSection = (sectionName) => {
    const newSection = {
      id: Date.now(),
      title: '',
      content: '',
    };
    const updated = [...(content.sections[sectionName] || []), newSection];
    onUpdateSection(sectionName, updated);
  };

  // Handle update section item
  const handleUpdateSectionItem = (sectionName, itemId, field, value) => {
    const updated = content.sections[sectionName].map(item =>
      item.id === itemId ? { ...item, [field]: value } : item
    );
    onUpdateSection(sectionName, updated);
  };

  // Handle remove section item
  const handleRemoveSectionItem = (sectionName, itemId) => {
    const updated = content.sections[sectionName].filter(item => item.id !== itemId);
    onUpdateSection(sectionName, updated);
  };

  return (
    <div className={styles.editor}>
      {/* Projects Section (from bullet points) */}
      <section className={styles.section}>
        <h3>Selected Project Bullets</h3>
        <div className={styles.bulletPoints}>
          {content.sections.projects && content.sections.projects.length > 0 ? (
            content.sections.projects.map((bullet, index) => (
              <div
                key={bullet.id}
                className={styles.bulletPoint}
                draggable
                onDragStart={() => handleDragStart(index)}
                onDragOver={handleDragOver}
                onDrop={(e) => handleDrop(e, index)}
              >
                <span className={styles.dragHandle}>⋮⋮</span>
                
                {editingBulletId === bullet.id ? (
                  <div className={styles.editingBullet}>
                    <textarea
                      className={styles.editInput}
                      value={editingText}
                      onChange={(e) => setEditingText(e.target.value)}
                      autoFocus
                    />
                    <div className={styles.editActions}>
                      <button
                        className={styles.btnSave}
                        onClick={() => handleSaveEdit(bullet.id)}
                      >
                        Save
                      </button>
                      <button
                        className={styles.btnCancel}
                        onClick={handleCancelEdit}
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    <div className={styles.bulletContent}>
                      <p>{bullet.text}</p>
                    </div>
                    <div className={styles.bulletActions}>
                      <button
                        className={styles.btnEdit}
                        onClick={() => handleEditBullet(bullet.id, bullet.text)}
                        title="Edit bullet"
                      >
                        ✏️
                      </button>
                      <button
                        className={styles.btnRemove}
                        onClick={() => onRemoveBullet(bullet.id)}
                        title="Remove bullet"
                      >
                        ✕
                      </button>
                    </div>
                  </>
                )}
              </div>
            ))
          ) : (
            <p className={styles.emptySection}>
              Add bullet points from the left sidebar to get started
            </p>
          )}
        </div>
      </section>

      {/* Experience Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3>Experience</h3>
          <button
            className={styles.btnAddSection}
            onClick={() => handleAddSection('experience')}
          >
            + Add
          </button>
        </div>
        <div className={styles.formItems}>
          {content.sections.experience && content.sections.experience.map(item => (
            <div key={item.id} className={styles.formItem}>
              <input
                type="text"
                placeholder="Job Title"
                className={styles.input}
                value={item.title || ''}
                onChange={(e) => handleUpdateSectionItem('experience', item.id, 'title', e.target.value)}
              />
              <input
                type="text"
                placeholder="Company"
                className={styles.input}
                value={item.company || ''}
                onChange={(e) => handleUpdateSectionItem('experience', item.id, 'company', e.target.value)}
              />
              <textarea
                placeholder="Description"
                className={styles.textarea}
                value={item.content || ''}
                onChange={(e) => handleUpdateSectionItem('experience', item.id, 'content', e.target.value)}
              />
              <button
                className={styles.btnRemoveItem}
                onClick={() => handleRemoveSectionItem('experience', item.id)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Education Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3>Education</h3>
          <button
            className={styles.btnAddSection}
            onClick={() => handleAddSection('education')}
          >
            + Add
          </button>
        </div>
        <div className={styles.formItems}>
          {content.sections.education && content.sections.education.map(item => (
            <div key={item.id} className={styles.formItem}>
              <input
                type="text"
                placeholder="School/University"
                className={styles.input}
                value={item.school || ''}
                onChange={(e) => handleUpdateSectionItem('education', item.id, 'school', e.target.value)}
              />
              <input
                type="text"
                placeholder="Degree"
                className={styles.input}
                value={item.degree || ''}
                onChange={(e) => handleUpdateSectionItem('education', item.id, 'degree', e.target.value)}
              />
              <input
                type="text"
                placeholder="Field of Study"
                className={styles.input}
                value={item.field || ''}
                onChange={(e) => handleUpdateSectionItem('education', item.id, 'field', e.target.value)}
              />
              <button
                className={styles.btnRemoveItem}
                onClick={() => handleRemoveSectionItem('education', item.id)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      </section>

      {/* Skills Section */}
      <section className={styles.section}>
        <div className={styles.sectionHeader}>
          <h3>Skills</h3>
          <button
            className={styles.btnAddSection}
            onClick={() => handleAddSection('skills')}
          >
            + Add
          </button>
        </div>
        <div className={styles.formItems}>
          {content.sections.skills && content.sections.skills.map(item => (
            <div key={item.id} className={styles.formItem}>
              <input
                type="text"
                placeholder="Skill Category (e.g., Languages)"
                className={styles.input}
                value={item.category || ''}
                onChange={(e) => handleUpdateSectionItem('skills', item.id, 'category', e.target.value)}
              />
              <textarea
                placeholder="Skills (comma-separated)"
                className={styles.textarea}
                value={item.content || ''}
                onChange={(e) => handleUpdateSectionItem('skills', item.id, 'content', e.target.value)}
              />
              <button
                className={styles.btnRemoveItem}
                onClick={() => handleRemoveSectionItem('skills', item.id)}
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
