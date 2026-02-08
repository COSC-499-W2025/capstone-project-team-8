/**
 * Template Registry
 * Central registry for managing all available resume templates
 * Allows dynamic template loading and switching
 */

import ClassicTemplate from '@/components/resume/ResumeTemplate';
import ModernTemplate from '@/components/resume/ModernTemplate';
import MinimalistTemplate from '@/components/resume/MinimalistTemplate';

// Template metadata and component mapping
export const templates = [
  {
    id: 0,
    name: 'Classic',
    component: ClassicTemplate,
    description: 'Professional and traditional design',
    icon: '📋',
  },
  {
    id: 1,
    name: 'Modern',
    component: ModernTemplate,
    description: 'Contemporary with blue accents',
    icon: '✨',
  },
  {
    id: 2,
    name: 'Minimalist',
    component: MinimalistTemplate,
    description: 'Sparse and elegant design',
    icon: '✓',
  },
];

/**
 * Get template component by index
 * @param {number} index - Template index (0, 1, 2, etc.)
 * @returns {React.Component} The template component
 */
export const getTemplateComponent = (index) => {
  const template = templates[index];
  return template ? template.component : templates[0].component; // Default to Classic
};

/**
 * Get template metadata by index
 * @param {number} index - Template index
 * @returns {object} Template metadata {name, description, icon}
 */
export const getTemplateMetadata = (index) => {
  const template = templates[index];
  if (!template) return templates[0]; // Default to Classic metadata
  
  return {
    name: template.name,
    description: template.description,
    icon: template.icon,
  };
};

/**
 * Get total number of templates
 * @returns {number} Number of available templates
 */
export const getTemplateCount = () => {
  return templates.length;
};

/**
 * Get all template names
 * @returns {string[]} Array of template names
 */
export const getTemplateNames = () => {
  return templates.map(t => t.name);
};

/**
 * Validate template index
 * @param {number} index - Template index to validate
 * @returns {boolean} True if index is valid
 */
export const isValidTemplateIndex = (index) => {
  return index >= 0 && index < templates.length;
};

/**
 * Get next template index with wrapping
 * @param {number} currentIndex - Current template index
 * @returns {number} Next template index
 */
export const getNextTemplateIndex = (currentIndex) => {
  const nextIndex = currentIndex + 1;
  return nextIndex >= templates.length ? 0 : nextIndex;
};

/**
 * Get previous template index with wrapping
 * @param {number} currentIndex - Current template index
 * @returns {number} Previous template index
 */
export const getPreviousTemplateIndex = (currentIndex) => {
  const prevIndex = currentIndex - 1;
  return prevIndex < 0 ? templates.length - 1 : prevIndex;
};

export default templates;
