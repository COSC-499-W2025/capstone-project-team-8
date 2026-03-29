export function isValidLinkedInUrl(value) {
  if (!value) return true;

  const normalized = value.trim().toLowerCase();

  return (
    normalized.startsWith('https://www.linkedin.com/in/') ||
    normalized.startsWith('www.linkedin.com/in/') ||
    normalized.startsWith('linkedin.com/in/')
  );
}
