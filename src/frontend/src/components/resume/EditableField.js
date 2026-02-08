import { useState } from 'react';
import styles from './ResumeTemplate.module.css';

/**
 * EditableField Component
 * 
 * Reusable editable field that switches between view and edit modes.
 * Used across all resume templates to maintain consistency.
 */
export default function EditableField({
  path,
  value,
  placeholder,
  multiline = false,
  className = '',
  editingPath,
  setEditingPath,
  onEdit
}) {
  const [editValue, setEditValue] = useState('');
  const isEditing = editingPath === path;

  const startEdit = (currentValue) => {
    setEditingPath(path);
    setEditValue(currentValue || '');
  };

  const finishEdit = () => {
    onEdit(path, editValue);
    setEditingPath(null);
    setEditValue('');
  };

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
            onBlur={() => finishEdit()}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && e.ctrlKey) {
                finishEdit();
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
            onBlur={() => finishEdit()}
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                finishEdit();
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
      onClick={() => startEdit(value)}
      title="Click to edit"
    >
      {value || <span className={styles.placeholder}>{placeholder}</span>}
    </div>
  );
}
