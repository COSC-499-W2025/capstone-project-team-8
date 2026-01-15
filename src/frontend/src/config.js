// Global configuration for the frontend
// Update these values or set environment variables for different environments

const config = {
  // API Base URL - configure for your deployment environment
  API_URL: process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000',
};

export default config;
