/**
 * Local Storage utilities for resume drafts
 * Provides functionality to save/restore resume drafts locally
 */

const STORAGE_KEY = 'resumeBuilderDrafts';
const CURRENT_DRAFT_KEY = 'resumeBuilderCurrentDraft';

/**
 * Save a resume draft to localStorage
 */
export const saveDraft = (resumeName, content) => {
  try {
    const drafts = getDrafts();
    const draft = {
      id: Date.now(),
      name: resumeName,
      content,
      savedAt: new Date().toISOString(),
    };

    drafts[draft.id] = draft;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
    localStorage.setItem(CURRENT_DRAFT_KEY, draft.id.toString());
    return draft;
  } catch (err) {
    console.error('Error saving draft:', err);
    return null;
  }
};

/**
 * Get all saved drafts
 */
export const getDrafts = () => {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : {};
  } catch (err) {
    console.error('Error loading drafts:', err);
    return {};
  }
};

/**
 * Get a specific draft by ID
 */
export const getDraft = (draftId) => {
  const drafts = getDrafts();
  return drafts[draftId] || null;
};

/**
 * Get the current/last draft
 */
export const getCurrentDraft = () => {
  try {
    const draftId = localStorage.getItem(CURRENT_DRAFT_KEY);
    if (draftId) {
      return getDraft(parseInt(draftId));
    }
    return null;
  } catch (err) {
    console.error('Error loading current draft:', err);
    return null;
  }
};

/**
 * Delete a draft
 */
export const deleteDraft = (draftId) => {
  try {
    const drafts = getDrafts();
    delete drafts[draftId];
    localStorage.setItem(STORAGE_KEY, JSON.stringify(drafts));
    
    // If deleted draft was current, clear current
    const currentId = localStorage.getItem(CURRENT_DRAFT_KEY);
    if (currentId === draftId.toString()) {
      localStorage.removeItem(CURRENT_DRAFT_KEY);
    }
    return true;
  } catch (err) {
    console.error('Error deleting draft:', err);
    return false;
  }
};

/**
 * Clear all drafts
 */
export const clearAllDrafts = () => {
  try {
    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(CURRENT_DRAFT_KEY);
    return true;
  } catch (err) {
    console.error('Error clearing drafts:', err);
    return false;
  }
};

/**
 * Export draft as JSON
 */
export const exportDraftAsJSON = (draftId) => {
  const draft = getDraft(draftId);
  if (!draft) return null;

  const dataStr = JSON.stringify(draft, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${draft.name.replace(/\s+/g, '_')}_draft.json`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
};

/**
 * Import draft from JSON file
 */
export const importDraftFromJSON = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const draft = JSON.parse(e.target.result);
        const saved = saveDraft(draft.name, draft.content);
        resolve(saved);
      } catch (err) {
        reject(new Error('Invalid draft file format'));
      }
    };
    reader.onerror = () => reject(new Error('Error reading file'));
    reader.readAsText(file);
  });
};

/**
 * Get draft statistics
 */
export const getDraftStats = () => {
  const drafts = getDrafts();
  const draftIds = Object.keys(drafts);
  
  return {
    totalDrafts: draftIds.length,
    drafts: draftIds.map(id => ({
      id: parseInt(id),
      name: drafts[id].name,
      savedAt: drafts[id].savedAt,
    })),
  };
};
