import config from '@/config';

/**
 * Fetch all projects for the authenticated user
 */
export const getProjects = async (token) => {
  const response = await fetch(`${config.API_URL}/api/projects/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch projects: ${response.status}`);
  }

  return response.json();
};

/**
 * Fetch resume templates
 */
export const getResumeTemplates = async (token) => {
  const response = await fetch(`${config.API_URL}/api/resume/templates/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch templates: ${response.status}`);
  }

  return response.json();
};

/**
 * Get resume preview with template and context data
 */
export const getResumePreview = async (token, templateId = null) => {
  const url = new URL(`${config.API_URL}/api/resume/preview/`);
  if (templateId) {
    url.searchParams.append('template_id', templateId);
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch preview: ${response.status}`);
  }

  return response.json();
};

/**
 * Generate LaTeX resume and download it
 */
export const generateLatexResume = async (token) => {
  const response = await fetch(`${config.API_URL}/api/resume/generate/latex/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to generate LaTeX: ${response.status}`);
  }

  // Get the filename from Content-Disposition header
  const contentDisposition = response.headers.get('Content-Disposition');
  let filename = 'resume.tex';
  if (contentDisposition) {
    const matches = contentDisposition.match(/filename="(.+?)"/);
    if (matches) filename = matches[1];
  }

  // Download the file
  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Generate a new resume
 */
export const generateResume = async (token, name, content) => {
  const response = await fetch(`${config.API_URL}/api/resume/generate/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      content,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to generate resume: ${response.status}`);
  }

  return response.json();
};

/**
 * Get a specific resume by ID
 */
export const getResume = async (token, resumeId) => {
  const response = await fetch(`${config.API_URL}/api/resume/${resumeId}/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch resume: ${response.status}`);
  }

  return response.json();
};

/**
 * Update an existing resume
 */
export const updateResume = async (token, resumeId, name, content) => {
  const response = await fetch(`${config.API_URL}/api/resume/${resumeId}/edit/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      content,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update resume: ${response.status}`);
  }

  return response.json();
};
