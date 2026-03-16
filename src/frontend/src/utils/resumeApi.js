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
 * Fetch all saved resumes for the authenticated user.
 */
export const listResumes = async (token) => {
  const response = await fetch(`${config.API_URL}/api/resume/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch resumes: ${response.status}`);
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
export const generateResume = async (token, name, content, theme = 'classic') => {
  const response = await fetch(`${config.API_URL}/api/resume/generate/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      content,
      theme,
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
 * Delete a saved resume.
 */
export const deleteResume = async (token, resumeId) => {
  const response = await fetch(`${config.API_URL}/api/resume/${resumeId}/`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to delete resume: ${response.status}`);
  }

  if (response.status === 204) {
    return { ok: true };
  }

  return response.json();
};

/**
 * Update an existing resume
 */
export const updateResume = async (token, resumeId, name, content, theme = 'classic') => {
  const response = await fetch(`${config.API_URL}/api/resume/${resumeId}/edit/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name,
      content,
      theme,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to update resume: ${response.status}`);
  }

  return response.json();
};

/**
 * Generate a PDF via RenderCV and trigger a browser download.
 * @param {string} token  - JWT access token
 * @param {object} resumeData - frontend resumeData state object
 * @param {string} theme  - "classic" | "moderncv" | "engineeringclassic" | "sb2nov"
 */
export const generateRenderCVPdf = async (token, resumeData, theme = 'classic') => {
  const response = await fetch(`${config.API_URL}/api/resume/render-pdf/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ resumeData, theme }),
  });

  if (!response.ok) {
    let message = `Failed to generate PDF: ${response.status}`;
    try {
      const body = await response.json();
      if (body?.error) message = body.error;
    } catch (_) { /* ignore parse errors */ }
    throw new Error(message);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'resume.pdf';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};

/**
 * Fetch all aggregated skills (languages + frameworks) for the authenticated user.
 * Returns { languages:[{name, project_count}], frameworks:[{name, project_count}], total_projects }
 */
export const getSkills = async (token) => {
  const response = await fetch(`${config.API_URL}/api/skills/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch skills: ${response.status}`);
  }

  return response.json();
};

/**
 * Download the raw RenderCV YAML for the current resume (for debugging).
 */
export const downloadRenderCVYaml = async (token, resumeData, theme = 'classic') => {
  const response = await fetch(`${config.API_URL}/api/resume/render-yaml/`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ resumeData, theme }),
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch YAML: ${response.status}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = 'resume.yaml';
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
};
