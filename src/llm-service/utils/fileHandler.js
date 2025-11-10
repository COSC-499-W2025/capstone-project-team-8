import multer from 'multer';

// File upload configuration
const storage = multer.memoryStorage();

// Allowed file types and extensions
const allowedTypes = [
  'text/plain',
  'text/csv',
  'application/json',
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/markdown',
  'text/x-python',
  'text/javascript',
  'application/javascript',
  'text/html',
  'text/css',
  'text/x-php',
  'application/x-php',
  'application/php'
];

const allowedExtensions = [
  '.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.csv',
  '.php', '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.rb', 
  '.go', '.rs', '.swift', '.kt', '.tsx', '.jsx', '.ts', '.vue',
  '.xml', '.yaml', '.yml', '.ini', '.conf', '.cfg', '.log',
  '.sql', '.sh', '.bat', '.ps1', '.r', '.scala', '.pl', '.lua'
];

// File filter function
const fileFilter = (req, file, cb) => {
  const fileExtension = '.' + file.originalname.split('.').pop().toLowerCase();
  
  if (allowedTypes.includes(file.mimetype) || allowedExtensions.includes(fileExtension)) {
    cb(null, true);
  } else {
    cb(new Error(`Unsupported file type: ${file.originalname}. Supported types: text files, code files (.php, .py, .js, .java, .cpp, etc.), JSON, CSV, PDF, Word documents`));
  }
};

// Multer upload configuration
export const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024,
    files: 1
  },
  fileFilter: fileFilter
});

// File content extraction utility
export const extractFileContent = (file) => {
  if (!file) return null;
  
  try {
    const content = file.buffer.toString('utf-8');
    return {
      filename: file.originalname,
      mimetype: file.mimetype,
      size: file.size,
      content: content
    };
  } catch (error) {
    throw new Error('Failed to extract file content: ' + error.message);
  }
};