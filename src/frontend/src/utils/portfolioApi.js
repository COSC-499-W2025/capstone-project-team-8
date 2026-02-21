import config from '@/config';

/**
 * Make an authenticated API call
 */
async function authenticatedFetch(endpoint, options = {}, token) {
  const headers = {
    ...options.headers,
  };

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const url = `${config.API_URL}${endpoint}`;

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.detail || errorData.message || `API error: ${response.statusText}`);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return { ok: true };
  }

  return response.json();
}

/**
 * Get list of user's portfolios
 */
export async function getPortfolios(token) {
  const data = await authenticatedFetch('/api/portfolio/', {
    method: 'GET',
  }, token);
  return data;
}

/**
 * Get a single portfolio by ID
 */
export async function getPortfolio(portfolioId, token = null) {
  const data = await authenticatedFetch(`/api/portfolio/${portfolioId}/`, {
    method: 'GET',
  }, token);
  return data;
}

/**
 * Create a new portfolio
 * @param {Object} portfolioData - Portfolio creation data
 * @param {string} portfolioData.title - Portfolio title (required)
 * @param {string} portfolioData.description - Portfolio description
 * @param {string} portfolioData.slug - Custom slug (auto-generated if not provided)
 * @param {boolean} portfolioData.is_public - Whether portfolio is public
 * @param {string} portfolioData.target_audience - Target audience description
 * @param {string} portfolioData.tone - Tone: 'professional', 'casual', 'technical', 'creative'
 * @param {number[]} portfolioData.project_ids - IDs of projects to include
 * @param {boolean} portfolioData.generate_summary - Whether to generate AI summary
 * @param {string} token - Auth token
 */
export async function createPortfolio(portfolioData, token) {
  const data = await authenticatedFetch('/api/portfolio/generate/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(portfolioData),
  }, token);
  return data;
}

/**
 * Update an existing portfolio
 * @param {number} portfolioId - Portfolio ID
 * @param {Object} updateData - Fields to update
 * @param {string} updateData.title - New title
 * @param {string} updateData.description - New description
 * @param {boolean} updateData.is_public - New visibility
 * @param {string} updateData.target_audience - New target audience
 * @param {string} updateData.tone - New tone
 * @param {boolean} updateData.regenerate_summary - Whether to regenerate AI summary
 * @param {string} token - Auth token
 */
export async function updatePortfolio(portfolioId, updateData, token) {
  const data = await authenticatedFetch(`/api/portfolio/${portfolioId}/edit/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updateData),
  }, token);
  return data;
}

/**
 * Delete a portfolio
 */
export async function deletePortfolio(portfolioId, token) {
  const data = await authenticatedFetch(`/api/portfolio/${portfolioId}/`, {
    method: 'DELETE',
  }, token);
  return data;
}

/**
 * Add a project to a portfolio
 * @param {number} portfolioId - Portfolio ID
 * @param {Object} projectData - Project data
 * @param {number} projectData.project_id - Project ID to add
 * @param {string} projectData.notes - Optional notes about the project
 * @param {boolean} projectData.featured - Whether to feature this project
 * @param {number} projectData.order - Optional order position
 * @param {string} token - Auth token
 */
export async function addProjectToPortfolio(portfolioId, projectData, token) {
  const data = await authenticatedFetch(`/api/portfolio/${portfolioId}/projects/add/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(projectData),
  }, token);
  return data;
}

/**
 * Remove a project from a portfolio
 */
export async function removeProjectFromPortfolio(portfolioId, projectId, token) {
  const data = await authenticatedFetch(`/api/portfolio/${portfolioId}/projects/${projectId}/`, {
    method: 'DELETE',
  }, token);
  return data;
}

/**
 * Reorder projects in a portfolio
 * @param {number} portfolioId - Portfolio ID
 * @param {number[]} projectIds - Ordered list of project IDs
 * @param {string} token - Auth token
 */
export async function reorderPortfolioProjects(portfolioId, projectIds, token) {
  const data = await authenticatedFetch(`/api/portfolio/${portfolioId}/projects/reorder/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ project_ids: projectIds }),
  }, token);
  return data;
}
