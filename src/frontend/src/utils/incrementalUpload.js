import config from '@/config';

/**
 * Fetch user's existing projects
 */
export const fetchUserProjects = async (token) => {
  const response = await fetch(`${config.API_URL}/api/projects/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch projects');
  }

  const data = await response.json();
  return data.projects || []; // Extract projects from nested response
};

/**
 * Fetch user's existing portfolios
 */
export const fetchUserPortfolios = async (token) => {
  const response = await fetch(`${config.API_URL}/api/portfolio/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch portfolios');
  }

  const data = await response.json();
  return data.portfolios || []; // Extract portfolios from nested response
};

/**
 * Fetch project history/versions for a specific project
 */
export const fetchProjectHistory = async (projectId, token) => {
  const response = await fetch(`${config.API_URL}/api/projects/${projectId}/history/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch project history');
  }

  return response.json();
};

/**
 * Fetch portfolio statistics
 */
export const fetchPortfolioStats = async (portfolioId, token) => {
  const response = await fetch(`${config.API_URL}/api/portfolio/${portfolioId}/incremental-stats/`, {
    method: 'GET',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error('Failed to fetch portfolio stats');
  }

  return response.json();
};

/**
 * Perform incremental upload
 */
export const performIncrementalUpload = async (
  file,
  targetType,
  targetId,
  mergeStrategy,
  token,
  progressCallback = null
) => {
  const formData = new FormData();
  formData.append('file', file);
  
  // Send correct parameter names based on target type
  if (targetType === 'project') {
    formData.append('target_project_id', targetId.toString());
  } else if (targetType === 'portfolio') {
    formData.append('target_portfolio_id', targetId.toString());
  }
  
  formData.append('merge_strategy', mergeStrategy);

  // Create XMLHttpRequest to track upload progress
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    // Track upload progress
    if (progressCallback) {
      xhr.upload.addEventListener('progress', (e) => {
        if (e.lengthComputable) {
          const progress = Math.round((e.loaded / e.total) * 100);
          progressCallback(progress, 'Uploading file...');
        }
      });
    }

    // Handle response
    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const result = JSON.parse(xhr.responseText);
          if (progressCallback) {
            progressCallback(100, 'Upload completed!');
          }
          resolve(result);
        } catch (error) {
          reject(new Error('Failed to parse response'));
        }
      } else {
        try {
          const errorData = JSON.parse(xhr.responseText);
          reject(new Error(errorData.error || `Upload failed with status ${xhr.status}`));
        } catch {
          reject(new Error(`Upload failed with status ${xhr.status}`));
        }
      }
    });

    // Handle errors
    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'));
    });

    // Handle abort
    xhr.addEventListener('abort', () => {
      reject(new Error('Upload was cancelled'));
    });

    // Start the request
    xhr.open('POST', `${config.API_URL}/api/incremental-upload/`);
    xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    
    if (progressCallback) {
      progressCallback(0, 'Preparing upload...');
    }
    
    xhr.send(formData);
  });
};

/**
 * Validate file for incremental upload
 */
export const validateIncrementalFile = (file) => {
  const errors = [];
  
  // Check if file exists
  if (!file) {
    errors.push('No file selected');
    return errors;
  }
  
  // Check file type
  if (file.type !== 'application/zip' && !file.name.toLowerCase().endsWith('.zip')) {
    errors.push('File must be a ZIP archive');
  }
  
  // Check minimum size (at least 1KB)
  if (file.size < 1024) {
    errors.push('File appears to be empty or too small');
  }
  
  return errors;
};

/**
 * Get merge strategy description
 */
export const getMergeStrategyDescription = (strategy) => {
  const descriptions = {
    'merge_similar': {
      title: 'Merge with Similar Projects',
      description: 'Files will be analyzed and merged with existing projects that have similar content or structure. This is ideal for adding related files to existing work.',
      icon: '🔗'
    },
    'add_to_portfolio': {
      title: 'Add to Portfolio',
      description: 'Files will be processed as a new project and added to the selected portfolio. Good for adding distinct new work.',
      icon: '📁'
    },
    'create_new': {
      title: 'Create New Version',
      description: 'Files will create a completely new project version. Best for major updates or revisions to existing work.',
      icon: '🆕'
    }
  };
  
  return descriptions[strategy] || descriptions['merge_similar'];
};

/**
 * Format upload progress status
 */
export const formatUploadStatus = (progress, phase) => {
  const phases = {
    'uploading': 'Uploading files...',
    'extracting': 'Extracting archive...',
    'analyzing': 'Analyzing content...',
    'processing': 'Processing files...',
    'merging': 'Merging with existing content...',
    'saving': 'Saving changes...',
    'complete': 'Upload complete!'
  };
  
  return phases[phase] || phase;
};