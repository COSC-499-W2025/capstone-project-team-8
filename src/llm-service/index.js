import express from "express";
import axios from "axios";
import cors from "cors";
import dotenv from "dotenv";

// Load environment variables
dotenv.config();

const app = express();

// Rate limiting parameters
const rateLimit = {};
const RATE_LIMIT = 10;
const TIME_WINDOW = 60 * 1000;

// Custom rate liminiting middleware
const rateLimiter = (req, res, next) => {
  const clientIP = req.ip || req.connection.remoteAddress;
  const now = Date.now();
  
  if (!rateLimit[clientIP]) {
    rateLimit[clientIP] = { count: 1, resetTime: now + TIME_WINDOW };
    return next();
  }
  
  if (now > rateLimit[clientIP].resetTime) {
    rateLimit[clientIP] = { count: 1, resetTime: now + TIME_WINDOW };
    return next();
  }
  
  if (rateLimit[clientIP].count >= RATE_LIMIT) {
    return res.status(429).json({ 
      error: "Too many requests. Try again later.",
      retryAfter: Math.ceil((rateLimit[clientIP].resetTime - now) / 1000)
    });
  }
  
  rateLimit[clientIP].count++;
  next();
};

// Make sure to add API key in your .env file
const LLM_API_KEY = process.env.LLM_API_KEY;

const requireApiKey = (req, res, next) => {
  const apiKey = req.headers['x-api-key'] || req.query.apikey;
  
  if (!apiKey || apiKey !== LLM_API_KEY) {
    return res.status(401).json({ 
      error: "Invalid or missing API key. Include 'x-api-key' header or 'apikey' query parameter." 
    });
  }
  
  next();
};

// Apply middleware
app.set('trust proxy', true);
app.use(express.json({ limit: '1mb' }));
app.use(cors());
app.use(rateLimiter);

const OLLAMA_API = process.env.OLLAMA_API || "http://localhost:11434/api/generate";

// START THE API ENDPOINTS
app.get("/health", (req, res) => {
  res.json({ 
    status: "ok", 
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

app.post("/api/query", requireApiKey, async (req, res) => {
  const { prompt, model = "llama3.1:8b" } = req.body;
  
  if (!prompt || typeof prompt !== 'string' || prompt.length > 20000) {
    return res.status(400).json({ 
      error: "Invalid prompt. String under 20000 characters required." 
    });
  }

  try {
    const response = await axios.post(OLLAMA_API, {
      model,
      prompt,
      stream: false,
    });

    res.json({ success: true, response: response.data.response });
  } catch (err) {
    console.error(err.message);
    res.status(500).json({ success: false, error: err.message });
  }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => console.log(`API running on http://localhost:${PORT}`));
