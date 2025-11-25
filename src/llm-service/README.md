# llm-service (Ollama + Express proxy)

This microservice provides a small Express API that will act as a layer that is part of our analysis process. 

**Why separate this from our Django app you might be thinking?** Because we can deploy this microservice completely independently, scale it separately. If we need to rotate cloud providers, it is extremely easy to do so with this architecture. We can simply use our cloud computing trials and clone this microservice to the new environment without touching our main application.

**Why use an express.js layer and not the API that comes with Ollama?**
The Express.js API forwards requests to a locally running Ollama instance, which hosts the LLM models. This allows us to handle authentication, logging, rate limiting, and much more when we need to in the future.

## Security Features

This service includes several security measures:
- **API Key Authentication**: All requests to `/api/query` require a valid API key
- **Rate Limiting**: Each IP is limited to 10 requests per minute to prevent abuse
- **Input Validation**: Prompts are validated and limited to 20,000 characters
- **CORS Protection**: Cross-origin requests are handled securely

### API Key Usage

⚠️ **IMPORTANT**: The API key can be found in the Discord channel. **DO NOT commit the API key to git or share it publicly**. Always use environment variables or `.env` files (which are gitignored).

The API key must be included in requests using either:
- Header: `x-api-key: YOUR_API_KEY`
- Query parameter: `?apikey=YOUR_API_KEY`

For development and testing purposes, it is advised that you run a small model on Olamma locally (e.g., `mistral` or `llama3`), which can be pulled from Ollama's model repository. **NOTE:** we will use much powerful models in production.

Quick Rundown:
- Ollama handles model hosting and the model API at port 11434 by default.
- The Express server exposes a simple HTTP API (JSON) which forwards requests to Ollama (so your frontend/backend can call a single service).

## Prerequisites

- Node.js (v16+ recommended)
- npm (or yarn)
- Ollama installed on the host machine. See https://ollama.com/ for installation instructions.

## Installation Options

### Option 1: Docker Deployment (Recommended for Production)

The easiest way to deploy this microservice is using Docker.

**Quick Docker Setup:**
```bash
# Copy environment template
cp .env.example .env
# Edit .env to set your API key
nano .env

# Deploy with Docker Compose
docker-compose up -d

# Check health
curl http://localhost:3001/health
```

**Windows PowerShell:**
```powershell
# Copy environment template  
Copy-Item .env.example .env
# Edit .env to set your API key
notepad .env

# Deploy using the script
.\deploy.ps1 deploy

# Check health
Invoke-WebRequest http://localhost:3001/health
```

### Option 2: Local Development Install

From the `src/llm-service` folder:

```powershell
npm install
```

## Run an Ollama instance (local model server)

1. Install Ollama following the official instructions: https://ollama.com/
2. Pull or install the model you want to use using cmd. Example using the `mistral` model (replace with the model you prefer):

```bash
ollama pull mistral
```

3. Start the Ollama server (it will listen on 127.0.0.1:11434 by default):

```bash
ollama serve
```

Notes
- By default Ollama listens on port 11434 and exposes a REST-like endpoint `/api/generate`.
- The reason we use an Express proxy is to add flexibility (authentication, logging, rate limiting, payload normalization) and to avoid CORS issues when calling from a browser.

## Start the Express server (this microservice)

This Express app is a thin API that forwards requests to the Ollama server. By default it listens on port 3001.

### Docker Deployment (Production)
```bash
# Quick deployment with Docker Compose
docker-compose up -d
```

### Local Development
From `src/llm-service`:

```powershell
npm start
# or for development with auto-restart
npm run dev
```

On bash / macOS / Linux:

```bash
PORT=3001 npm start
```

## Cloud Based API Usage

### Authentication Required

All requests to the protected endpoints require authentication. Include the API key in your request headers (you can find the key in our group Discord channel):

```bash
curl -X POST http://129.146.9.215:3001/api/query \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY_HERE" \
  -d '{
    "model": "llama3.1:8b",
    "prompt": "Your prompt here"
  }'
```

### Rate Limiting

- **Limit**: 10 requests per minute per IP address (can increase after testing)
- **Response**: HTTP 429 (Too Many Requests) when limit exceeded
- **Reset**: Automatic reset after 1 minute

### Endpoints

**POST** `/api/query` (Protected - requires API key)
- Forwards requests to Ollama with authentication and rate limiting
- Expected JSON payload:

```json
{
	"model": "llama3.1:8b",
	"prompt": "Answer ONLY in English: Summarize the following text: 'Artificial intelligence is transforming the world.'"
}
```

**GET** `/health` (Public - no API key required)
- Returns service health status and uptime
