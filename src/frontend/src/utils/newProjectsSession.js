/**
 * Utility for managing newly uploaded projects in sessionStorage
 * sessionStorage clears when the browser tab closes, which matches the desired behavior
 */

const NEW_PROJECTS_KEY = 'newProjects';

export function addNewProject(projectId) {
  try {
    if (!projectId) return;
    const newProjects = getNewProjects();
    const id = parseInt(projectId, 10);
    if (!newProjects.includes(id)) {
      newProjects.push(id);
      sessionStorage.setItem(NEW_PROJECTS_KEY, JSON.stringify(newProjects));
    }
  } catch (error) {
    console.error('Failed to add new project to sessionStorage:', error);
  }
}

export function addNewProjects(projectIds) {
  try {
    if (!Array.isArray(projectIds)) return;
    const newProjects = getNewProjects();
    projectIds.forEach(id => {
      const parsedId = parseInt(id, 10);
      if (!newProjects.includes(parsedId)) {
        newProjects.push(parsedId);
      }
    });
    sessionStorage.setItem(NEW_PROJECTS_KEY, JSON.stringify(newProjects));
  } catch (error) {
    console.error('Failed to add new projects to sessionStorage:', error);
  }
}

export function getNewProjects() {
  try {
    const stored = sessionStorage.getItem(NEW_PROJECTS_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch (error) {
    console.error('Failed to get new projects from sessionStorage:', error);
    return [];
  }
}

export function isNewProject(projectId) {
  return getNewProjects().includes(parseInt(projectId, 10));
}

export function clearNewProjects() {
  try {
    sessionStorage.removeItem(NEW_PROJECTS_KEY);
  } catch (error) {
    console.error('Failed to clear new projects from sessionStorage:', error);
  }
}
