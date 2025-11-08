import express from "express";
import axios from "axios";
import cors from "cors";
import multer from "multer";
import dotenv from "dotenv";
import { rateLimiter } from "./middleware/rateLimiter.js";

// Load environment variables
dotenv.config();

const app = express();

// File upload configuration
const storage = multer.memoryStorage();
const upload = multer({
  storage: storage,
  limits: {
    fileSize: 10 * 1024 * 1024,
    files: 1
  },
  fileFilter: (req, file, cb) => {
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
    const fileExtension = '.' + file.originalname.split('.').pop().toLowerCase();
    
    if (allowedTypes.includes(file.mimetype) || allowedExtensions.includes(fileExtension)) {
      cb(null, true);
    } else {
      cb(new Error(`Unsupported file type: ${file.originalname}. Supported types: text files, code files (.php, .py, .js, .java, .cpp, etc.), JSON, CSV, PDF, Word documents`));
    }
  }
});

// File content extraction utility
const extractFileContent = (file) => {
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

// Make sure to add API key in your .env file
const LLM_API_KEY = process.env.LLM_API_KEY;

// Debug: Check if API key is loaded
console.log('Loaded API Key:', LLM_API_KEY ? 'Present' : 'Missing');
if (!LLM_API_KEY) {
  console.error('WARNING: LLM_API_KEY not found in environment variables');
}

const requireApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'] || 
                 req.headers['X-API-KEY'] ||
                 req.headers['X-Api-Key'] ||
                 req.query.apikey;
  
  if (!apiKey || apiKey !== LLM_API_KEY) {
    return res.status(401).json({ 
      error: "Invalid or missing API key. Include 'x-api-key' header or 'apikey' query parameter.",
      receivedKey: apiKey ? "Key received but doesn't match" : "No key received",
      expectedFormat: "x-api-key header"
    });
  }
  
  next();
};

// Apply middleware
app.set('trust proxy', true);
app.use(express.json({ limit: '1mb' }));
app.use(cors());
app.use(rateLimiter);

const OLLAMA_API = "http://127.0.0.1:11434/api/generate";

// START THE API ENDPOINTS
app.get("/health", (req, res) => {
  res.json({ 
    status: "ok", 
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// File upload endpoint with prompt
app.post("/api/query-with-file", requireApiKey, upload.single('file'), async (req, res) => {
  const { prompt, model = "mistral:latest" } = req.body;
  const file = req.file;
  
  if (!prompt || typeof prompt !== 'string' || prompt.length > 20000) {
    return res.status(400).json({ 
      error: "Invalid prompt. String under 20000 characters required." 
    });
  }
  
  let finalPrompt = prompt;

  if (file) {
    try {
      const fileData = extractFileContent(file);
      finalPrompt = `${prompt}\n\nAnalyze this file:\nFilename: ${fileData.filename}\nFile Content:\n${fileData.content}`;
    } catch (error) {
      return res.status(400).json({ 
        error: "Failed to process uploaded file: " + error.message 
      });
    }
  }

  try {
    console.log(`Sending request to: ${OLLAMA_API}`);
    console.log(`Model: ${model}`);
    console.log(`Prompt length: ${finalPrompt.length}`);
    console.log(`File uploaded: ${file ? 'Yes (' + file.originalname + ')' : 'No'}`);
    
    const response = await axios.post(OLLAMA_API, {
      model,
      prompt: finalPrompt,
      stream: false,
    });

    res.json({ 
      success: true, 
      response: response.data.response,
      fileProcessed: !!file,
      filename: file ? file.originalname : null,
      model: model
    });
  } catch (err) {
    console.error('Ollama API Error:', err.response?.status, err.response?.statusText);
    console.error('Error details:', err.response?.data || err.message);
    res.status(500).json({ 
      success: false, 
      error: err.message,
      ollamaError: err.response?.data || 'Unknown Ollama error'
    });
  }
});

app.post("/api/query", requireApiKey, async (req, res) => {
  const { prompt, model = "mistral:latest" } = req.body;
  
  if (!prompt || typeof prompt !== 'string' || prompt.length > 20000) {
    return res.status(400).json({ 
      error: "Invalid prompt. String under 20000 characters required." 
    });
  }

  try {
    console.log(`Sending request to: ${OLLAMA_API}`);
    console.log(`Model: ${model}`);
    console.log(`Prompt length: ${prompt.length}`);
    
    const response = await axios.post(OLLAMA_API, {
      model,
      prompt,
      stream: false,
    });

    res.json({ success: true, response: response.data.response });
  } catch (err) {
    console.error('Ollama API Error:', err.response?.status, err.response?.statusText);
    console.error('Error details:', err.response?.data || err.message);
    res.status(500).json({ 
      success: false, 
      error: err.message,
      ollamaError: err.response?.data || 'Unknown Ollama error'
    });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`API running on http://localhost:${PORT}`));
