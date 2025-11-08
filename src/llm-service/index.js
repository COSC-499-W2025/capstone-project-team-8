import express from "express";
import axios from "axios";
import cors from "cors";
import dotenv from "dotenv";
import { rateLimiter } from "./middleware/rateLimiter.js";
import { requireApiKey } from "./middleware/auth.js";
import { upload, extractFileContent } from "./utils/fileHandler.js";

dotenv.config();
const app = express();
const LLM_API_KEY = process.env.LLM_API_KEY;
const OLLAMA_API = "http://127.0.0.1:11434/api/generate";

// Console log check to verify if api key was added
console.log('Loaded API Key:', LLM_API_KEY ? 'Present' : 'Missing');
if (!LLM_API_KEY) {
  console.error('WARNING: LLM_API_KEY not found in environment variables');
}

// Apply middleware
app.set('trust proxy', true);
app.use(express.json({ limit: '1mb' }));
app.use(cors());
app.use(rateLimiter);

// START THE API ENDPOINTS
app.get("/health", (req, res) => {
  res.json({ 
    status: "ok", 
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// MAIN ENDPOINT 
app.post("/api/query", requireApiKey, upload.single('file'), async (req, res) => {
  const { prompt, model = "mistral:latest" } = req.body;
  const file = req.file;
  
  if (!prompt || typeof prompt !== 'string' || prompt.length > 20000) {
    return res.status(400).json({ 
      error: "Invalid prompt. String under 20000 characters required." 
    });
  }
  
  let finalPrompt = prompt;

  // If there is a file uploaded, then process it and include in the prompt
  if (file) {
    try {
      const fileData = extractFileContent(file);
      finalPrompt = `${prompt}\n\nAnalyze this file:\nFilename: ${fileData.filename}\nFile Content:\n${fileData.content}`;
      console.log(`File processed: ${file.originalname} (${fileData.size} bytes)`);
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
    console.log(`File: ${file ? file.originalname : 'None'}`);
    
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

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`API running on http://localhost:${PORT}`));
