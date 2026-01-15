import config from '@/config';

/**
 * Make an API call with optional bearer token
 */
export async function apiCall(endpoint, options = {}, token = null) {
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
    throw new Error(errorData.detail || errorData.message || `API error: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Login user
 */
export async function login(username, password) {
  const data = await apiCall('/api/token/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  return data;
}

/**
 * Signup user
 */
export async function signup(username, password, email, confirmPassword) {
  const data = await apiCall('/api/signup/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password, email, confirm_password: confirmPassword }),
  });
  return data;
}

/**
 * Logout user
 */
export async function logout(token) {
  const data = await apiCall('/api/token/logout/', {
    method: 'POST',
  }, token);
  return data;
}

/**
 * Get current user profile
 */
export async function getCurrentUser(token) {
  const data = await apiCall('/api/users/me/', {
    method: 'GET',
  }, token);
  return data;
}

/**
 * Upload folder with token
 */
export async function uploadFolder(file, scanConsent, llmConsent, token) {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('consent_scan', scanConsent ? 'true' : 'false');
  formData.append('consent_send_llm', llmConsent ? 'true' : 'false');

  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${config.API_URL}/api/upload-folder/`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || errorData.message || `Upload failed: ${response.statusText}`);
  }

  return response.json();
}
