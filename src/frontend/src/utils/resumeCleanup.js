/**
 * Export Cleanup Utilities
 * Transforms working resume data into clean export format
 */

/**
 * Clean a single item by removing null/empty fields and edit controls
 */
export const cleanItem = (item) => {
  if (!item) return null;
  
  const cleaned = {};
  for (const [key, value] of Object.entries(item)) {
    // Skip edit/UI fields
    if (key === 'editMode' || key === 'showDelete' || key === 'hover') {
      continue;
    }
    
    // Skip null, undefined, or empty strings
    if (value === null || value === undefined || value === '') {
      continue;
    }
    
    cleaned[key] = value;
  }
  
  return Object.keys(cleaned).length > 0 ? cleaned : null;
};

/**
 * Clean an array of items
 */
export const cleanArray = (arr) => {
  if (!Array.isArray(arr)) return [];
  
  return arr
    .map(cleanItem)
    .filter(item => item !== null && item !== undefined);
};

/**
 * Clean summary text (trim, remove extra whitespace)
 */
export const cleanText = (text) => {
  if (typeof text !== 'string') return '';
  return text.trim().replace(/\s+/g, ' ');
};

/**
 * Transform full resume data into export-ready format
 * Removes: null fields, empty strings, edit controls, unnecessary sections
 */
export const cleanResumeForExport = (resumeData) => {
  if (!resumeData) return null;
  
  const cleaned = {
    name: cleanText(resumeData.name || ''),
    sections: {
      summary: cleanText(resumeData.sections?.summary || ''),
      experience: cleanArray(resumeData.sections?.experience || []),
      education: cleanArray(resumeData.sections?.education || []),
      skills: cleanArray(resumeData.sections?.skills || []),
      certifications: cleanArray(resumeData.sections?.certifications || []),
      projects: cleanArray(resumeData.sections?.projects || [])
    }
  };
  
  // Remove empty sections
  const finalSections = {};
  for (const [key, value] of Object.entries(cleaned.sections)) {
    if (key === 'summary') {
      if (value && value.length > 0) {
        finalSections[key] = value;
      }
    } else if (Array.isArray(value)) {
      if (value.length > 0) {
        finalSections[key] = value;
      }
    } else if (value) {
      finalSections[key] = value;
    }
  }
  
  return {
    name: cleaned.name,
    sections: finalSections
  };
};

/**
 * Extract draggable items from a resume data structure
 * Used to populate the ProjectsPanel with available items
 */
export const extractDraggableItems = (projects) => {
  if (!Array.isArray(projects)) return [];
  
  return projects.map(project => ({
    projectId: project.id,
    projectName: project.name,
    projectType: project.classification_type || 'project',
    skills: (project.languages || [])
      .map(lang => ({
        id: `skill-${lang.id}`,
        title: lang.name,
        source: 'language',
        projectId: project.id
      }))
      .concat((project.frameworks || [])
        .map(fw => ({
          id: `framework-${fw.id}`,
          title: fw.name,
          source: 'framework',
          projectId: project.id
        })))
      .concat((project.resume_bullet_points || [])
        .map((bullet, idx) => ({
          id: `skill-text-${project.id}-${idx}`,
          title: bullet,
          source: 'custom',
          projectId: project.id
        }))),
    bullets: (project.resume_bullet_points || []).map((bullet, idx) => ({
      id: `bullet-${project.id}-${idx}`,
      content: bullet,
      projectId: project.id,
      projectName: project.name
    }))
  }));
};

/**
 * Format resume data for LaTeX/PDF export
 * Creates a version with proper formatting but clean structure
 */
export const formatResumeForLatex = (cleanedData) => {
  // LaTeX expects specific structure
  return {
    name: cleanedData.name || 'Resume',
    sections: cleanedData.sections || {}
  };
};

export const formatResumeForPdf = (cleanedData) => {
  // PDF expects the same clean structure
  return cleanedData;
};
/**
 * Format Unix timestamp to "Month Year" (e.g., "Jan 2023")
 * @param {number} timestamp - Unix timestamp in seconds
 * @returns {string} Formatted date string
 */
export const formatTimestampToDate = (timestamp) => {
  if (!timestamp) return 'Present';
  
  const date = new Date(timestamp * 1000); // Convert seconds to milliseconds
  const options = { year: 'numeric', month: 'short' };
  return date.toLocaleDateString('en-US', options);
};

/**
 * Get readable date range from project dates
 * @param {number} startTimestamp - When work started (optional)
 * @param {number} endTimestamp - When work ended (optional)
 * @returns {string} Date range like "Jan 2023 - Present" or just "Started Jan 2023"
 */
export const getProjectDateRange = (startTimestamp, endTimestamp) => {
  const startDate = formatTimestampToDate(startTimestamp);
  const endDate = formatTimestampToDate(endTimestamp);
  
  if (startDate && endDate && startDate !== endDate) {
    return `${startDate} - ${endDate}`;
  } else if (startDate) {
    return startDate;
  } else if (endDate) {
    return endDate;
  }
  return 'Present';
};